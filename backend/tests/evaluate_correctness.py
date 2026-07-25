"""
Correctness evaluation harness for DRS adjudication pipeline.

Usage:
    python tests/evaluate_correctness.py              # full run (hits LLMs)
    python tests/evaluate_correctness.py --dry-run     # scoring rules only, no LLM
    python tests/evaluate_correctness.py --fast        # deterministic fallback only
"""

import argparse
import asyncio
import json
import logging
import sys
import time
from collections import Counter
from pathlib import Path
from unittest.mock import patch

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_factory
from app.models.dispute_models import (
    AuditTrail,
    AutoFetchedLogs,
    Dispute,
    DisputeReasonCode,
    DisputeStatus,
    Evidence,
    EvidenceSource,
    Merchant,
    User,
    VerdictType,
)
from app.services.adjudication import _build_data_dict, _build_evidence_summary, calculate_scores, run_adjudication
from app.services.reasoning import _deterministic_fallback, generate_verdict

logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")
logger = logging.getLogger("eval")

GOLDEN_PATH = Path(__file__).parent / "golden_dataset.json"


def load_dataset() -> list[dict]:
    with open(GOLDEN_PATH) as f:
        return json.load(f)


async def ensure_user(db: AsyncSession, email: str = "eval@drs.local") -> User:
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user:
        user = User(full_name="Eval User", email=email)
        db.add(user)
        await db.flush()
    return user


async def ensure_merchant(db: AsyncSession, name: str = "Eval Merchant") -> Merchant:
    result = await db.execute(select(Merchant).where(Merchant.business_name == name))
    merchant = result.scalar_one_or_none()
    if not merchant:
        merchant = Merchant(business_name=name, return_policy_url="https://example.com/returns")
        db.add(merchant)
        await db.flush()
    return merchant


async def evaluate_single(
    db: AsyncSession,
    tc: dict,
    user: User,
    merchant: Merchant,
    use_llm: bool,
) -> dict:
    reason_code = DisputeReasonCode(tc["reason_code"])
    amount = tc["mock_responses"]["razorpay"]["amount"]

    dispute = Dispute(
        transaction_id=f"EVAL-{tc['id']}",
        user_id=user.id,
        merchant_id=merchant.id,
        amount=amount,
        currency="INR",
        reason_code=reason_code,
        user_narrative=tc.get("user_narrative"),
        status=DisputeStatus.INITIATED,
    )
    db.add(dispute)
    await db.flush()

    auto_logs = AutoFetchedLogs(
        dispute_id=dispute.id,
        razorpay_payload=tc["mock_responses"]["razorpay"],
        shopify_payload=tc["mock_responses"]["shopify"],
        shiprocket_payload=tc["mock_responses"]["shiprocket"],
    )
    db.add(auto_logs)

    audit = AuditTrail(
        dispute_id=dispute.id,
        action_taken="EVAL_CREATED",
        performed_by="EVAL_HARNESS",
    )
    db.add(audit)
    await db.flush()

    data = _build_data_dict(auto_logs, [])
    score = calculate_scores(data)
    evidence_summary = _build_evidence_summary([])

    if use_llm:
        verdict_result = await generate_verdict(
            evidence_summary=evidence_summary,
            merchant_score=score.merchant_score,
            user_score=score.user_score,
            rules_triggered=score.rules_triggered,
            user_narrative=tc.get("user_narrative"),
            merchant_policy=tc.get("merchant_return_policy"),
            reason_code=reason_code.value,
            amount=amount,
            currency="INR",
        )
    else:
        verdict_result = _deterministic_fallback(score.merchant_score, score.user_score)

    actual_verdict = verdict_result.get("verdict", "NEEDS_HUMAN_INTERVENTION")
    confidence = verdict_result.get("confidence_score", 0.0)
    expected = tc["expected_verdict"]

    await db.rollback()

    return {
        "id": tc["id"],
        "reason_code": tc["reason_code"],
        "expected_verdict": expected,
        "actual_verdict": actual_verdict,
        "confidence": confidence,
        "merchant_score": score.merchant_score,
        "user_score": score.user_score,
        "rules_triggered": [r["rule"] for r in score.rules_triggered],
        "correct": actual_verdict == expected,
    }


async def run_evaluation(use_llm: bool) -> dict:
    dataset = load_dataset()

    async with async_session_factory() as seed_db:
        user = await ensure_user(seed_db)
        merchant = await ensure_merchant(seed_db)
        await seed_db.commit()

    results = []
    start = time.time()

    for tc in dataset:
        async with async_session_factory() as db:
            result = await evaluate_single(db, tc, user, merchant, use_llm)
        results.append(result)
        elapsed = time.time() - start
        done = len(results)
        remaining = len(dataset) - done
        avg = elapsed / done
        eta = avg * remaining
        symbol = "✓" if result["correct"] else "✗"
        print(f"  [{done}/{len(dataset)}] {symbol} {tc['id']}: expected={result['expected_verdict']} actual={result['actual_verdict']} (c={result['confidence']:.2f}) [ETA {eta:.0f}s]")

    total_time = time.time() - start

    return build_report(results, total_time)


def build_report(results: list[dict], total_time: float) -> dict:
    total = len(results)
    correct = sum(1 for r in results if r["correct"])
    accuracy = correct / total if total else 0

    conf_matrix = Counter()
    for r in results:
        conf_matrix[(r["expected_verdict"], r["actual_verdict"])] += 1

    by_reason = {}
    for r in results:
        key = r["reason_code"]
        by_reason.setdefault(key, {"total": 0, "correct": 0})
        by_reason[key]["total"] += 1
        if r["correct"]:
            by_reason[key]["correct"] += 1

    by_verdict = {}
    for r in results:
        key = r["expected_verdict"]
        by_verdict.setdefault(key, {"total": 0, "correct": 0, "confidences": []})
        by_verdict[key]["total"] += 1
        by_verdict[key]["confidences"].append(r["confidence"])
        if r["correct"]:
            by_verdict[key]["correct"] += 1

    correct_conf = [r["confidence"] for r in results if r["correct"]]
    incorrect_conf = [r["confidence"] for r in results if not r["correct"]]

    return {
        "total": total,
        "correct": correct,
        "accuracy": round(accuracy, 4),
        "total_time_seconds": round(total_time, 2),
        "avg_time_per_case": round(total_time / total, 2) if total else 0,
        "confusion_matrix": {str(k): v for k, v in conf_matrix.most_common()},
        "per_reason_code": {
            k: {
                "total": v["total"],
                "correct": v["correct"],
                "accuracy": round(v["correct"] / v["total"], 2) if v["total"] else 0,
            }
            for k, v in sorted(by_reason.items())
        },
        "per_verdict": {
            k: {
                "total": v["total"],
                "correct": v["correct"],
                "precision": round(v["correct"] / v["total"], 2) if v["total"] else 0,
                "avg_confidence": round(sum(v["confidences"]) / len(v["confidences"]), 2) if v["confidences"] else 0,
            }
            for k, v in sorted(by_verdict.items())
        },
        "avg_confidence_correct": round(sum(correct_conf) / len(correct_conf), 2) if correct_conf else 0,
        "avg_confidence_incorrect": round(sum(incorrect_conf) / len(incorrect_conf), 2) if incorrect_conf else 0,
    }


def print_report(report: dict):
    sep = "=" * 55
    print(f"\n{sep}")
    print("  DRS CORRECTNESS REPORT")
    print(sep)
    print(f"  Accuracy:         {report['correct']}/{report['total']} = {report['accuracy']*100:.1f}%")
    print(f"  Total time:       {report['total_time_seconds']:.1f}s ({report['avg_time_per_case']:.2f}s/case)")
    print()

    print("  Per reason code:")
    for rc, stats in report["per_reason_code"].items():
        bar = "█" * int(stats["accuracy"] * 20) + "░" * (20 - int(stats["accuracy"] * 20))
        print(f"    {rc:<30s} {stats['correct']:>2d}/{stats['total']:<2d} {stats['accuracy']*100:>5.1f}%  {bar}")
    print()

    print("  Per verdict:")
    for v, stats in report["per_verdict"].items():
        print(f"    {v:<30s} precision={stats['precision']*100:.0f}%  avg_conf={stats['avg_confidence']:.2f}")
    print()

    print("  Confidence:")
    print(f"    Average (correct):   {report['avg_confidence_correct']:.2f}")
    print(f"    Average (incorrect): {report['avg_confidence_incorrect']:.2f}")
    print(f"    Delta:               {report['avg_confidence_correct'] - report['avg_confidence_incorrect']:+.2f}")
    print()

    print("  Confusion matrix (expected -> actual):")
    for key, count in report["confusion_matrix"].items():
        exp, act = eval(key)
        if exp != act:
            print(f"    {exp:<30s} → {act:<30s} ({count}x)")
    print(sep)


def main():
    parser = argparse.ArgumentParser(description="Evaluate DRS adjudication correctness")
    parser.add_argument("--dry-run", action="store_true", help="Scoring rules only, no LLM or deterministic fallback")
    parser.add_argument("--fast", action="store_true", help="Use deterministic fallback instead of LLM")
    args = parser.parse_args()

    if args.dry_run:
        print("\n  DRY RUN — scoring rules evaluation only\n")
        dataset = load_dataset()
        for tc in dataset:
            data = tc["mock_responses"]
            score = calculate_scores(data)
            tag = "✓" if score.merchant_score or score.user_score else " "
            print(f"  [{tag}] {tc['id']}: M={score.merchant_score:>2d} U={score.user_score:>2d} rules={[r['rule'] for r in score.rules_triggered]}")
        print(f"\n  Evaluated {len(dataset)} cases (scoring only).")
        return

    use_llm = not args.fast
    mode = "FULL (LLM)" if use_llm else "FAST (deterministic)"
    print(f"\n  Mode: {mode}")
    print(f"  Dataset: {GOLDEN_PATH}")
    print()

    report = asyncio.run(run_evaluation(use_llm))
    print_report(report)


if __name__ == "__main__":
    main()
