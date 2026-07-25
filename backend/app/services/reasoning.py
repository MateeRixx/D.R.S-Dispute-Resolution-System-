import json
import logging
import os
from decimal import Decimal
from typing import Optional

from app.core.config import settings
from app.core.security import scrub_pii

logger = logging.getLogger(__name__)

REASONING_PROMPT_TEMPLATE = """You are a neutral financial dispute arbitrator for an Indian e-commerce chargeback resolution platform called DRS. Your task is to analyse the evidence summary, fairness scores, user narrative, and merchant policy details below, then return a structured JSON verdict.

**Rules:**
- REFUND_USER — evidence strongly favours the card member (e.g. item not delivered, confirmed defects, policy violation)
- REJECT_CLAIM — evidence strongly favours the merchant (e.g. delivery confirmed with signature, no defects, valid transaction)
- PARTIAL_REFUND — mixed evidence; partial compensation is fair
- NEEDS_HUMAN_INTERVENTION — cannot decide confidently (confidence < 0.60 or contradictory strong evidence)

Return ONLY valid JSON with no markdown formatting:
{{"verdict": "REFUND_USER" | "REJECT_CLAIM" | "PARTIAL_REFUND" | "NEEDS_HUMAN_INTERVENTION", "confidence_score": 0.00 to 1.00, "reasoning_summary": "2-3 sentence explanation of the decision in plain English", "merchant_risk_flags": ["flag1", "flag2"], "user_risk_flags": ["flag1"]}}

**Evidence Summary:**
{evidence_summary}

**Fairness Scores:**
- Merchant Score: {merchant_score}/25
- User Score: {user_score}/45
- Rules Triggered: {rules_triggered}

**User Narrative:** {user_narrative}

**Merchant Policy:** {merchant_policy}

**Dispute Details:**
- Reason Code: {reason_code}
- Amount: {amount} {currency}
"""


def build_prompt(
    evidence_summary: str,
    merchant_score: int,
    user_score: int,
    rules_triggered: list[dict],
    user_narrative: Optional[str],
    merchant_policy: Optional[str],
    reason_code: str,
    amount: Decimal,
    currency: str,
) -> str:
    narrative = scrub_pii(user_narrative or "Not provided")
    policy = merchant_policy or "Not available"

    triggered_str = "; ".join(
        f"{r['rule']} (+{r['points']} {r['awarded_to']})" for r in rules_triggered
    ) or "None"

    return REASONING_PROMPT_TEMPLATE.format(
        evidence_summary=evidence_summary,
        merchant_score=merchant_score,
        user_score=user_score,
        rules_triggered=triggered_str,
        user_narrative=narrative,
        merchant_policy=policy,
        reason_code=reason_code,
        amount=amount,
        currency=currency,
    )


def _try_groq(prompt: str) -> Optional[dict]:
    api_key = settings.groq_api_key or os.getenv("GROQ_API_KEY")
    if not api_key:
        logger.warning("No Groq API key configured")
        return None

    try:
        from groq import Groq
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=1024,
        )
        return _parse_json(response.choices[0].message.content)
    except ImportError:
        logger.warning("groq package not installed, skipping")
        return None
    except Exception as e:
        logger.error("Groq API call failed: %s", e)
        return None


def _try_gemini(prompt: str) -> Optional[dict]:
    api_key = settings.gemini_api_key or os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.warning("No Gemini API key configured")
        return None

    try:
        from google import genai
        from google.genai import types as genai_types
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[prompt],
            config=genai_types.GenerateContentConfig(
                temperature=0.3,
                max_output_tokens=1024,
            ),
        )
        return _parse_json(response.text)
    except Exception as e:
        logger.error("Gemini API call failed: %s", e)
        return None


def _deterministic_fallback(
    merchant_score: int,
    user_score: int,
) -> dict:
    diff = user_score - merchant_score
    if diff >= 15:
        return {"verdict": "REFUND_USER", "confidence_score": 0.75, "reasoning_summary": "User evidence outweighs merchant evidence by a significant margin."}
    elif diff <= -15:
        return {"verdict": "REJECT_CLAIM", "confidence_score": 0.75, "reasoning_summary": "Merchant evidence outweighs user evidence by a significant margin."}
    elif diff > 0:
        return {"verdict": "PARTIAL_REFUND", "confidence_score": 0.60, "reasoning_summary": "Mixed evidence; partial compensation is appropriate."}
    else:
        return {"verdict": "NEEDS_HUMAN_INTERVENTION", "confidence_score": 0.50, "reasoning_summary": "Evidence is inconclusive or evenly balanced. Human review required."}


def _parse_json(text: str) -> Optional[dict]:
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        logger.error("Failed to parse LLM response as JSON: %s", text[:200])
        return None


async def generate_verdict(
    evidence_summary: str = "",
    merchant_score: int = 0,
    user_score: int = 0,
    rules_triggered: Optional[list[dict]] = None,
    user_narrative: Optional[str] = None,
    merchant_policy: Optional[str] = None,
    reason_code: str = "",
    amount: Optional[Decimal] = None,
    currency: str = "INR",
) -> dict:
    prompt = build_prompt(
        evidence_summary=evidence_summary,
        merchant_score=merchant_score,
        user_score=user_score,
        rules_triggered=rules_triggered or [],
        user_narrative=user_narrative,
        merchant_policy=merchant_policy,
        reason_code=reason_code,
        amount=amount or Decimal("0"),
        currency=currency,
    )

    result = _try_groq(prompt)
    if result is not None:
        return result

    logger.warning("All LLM providers unavailable, using deterministic fallback")
    return _deterministic_fallback(merchant_score, user_score)
