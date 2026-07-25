import logging
from typing import Optional

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

TEMPLATES = {
    "DISPUTE_CREATED": "Your dispute #{transaction_id} has been filed and is being processed.",
    "EVIDENCE_UPLOADED": "New evidence has been uploaded for dispute #{transaction_id}.",
    "AUTO_FETCH_COMPLETED": "Transaction data has been automatically fetched for dispute #{transaction_id}.",
    "DECISION_RENDERED": "A decision has been made on dispute #{transaction_id}: {verdict}.",
    "CLOSED": "Dispute #{transaction_id} has been closed.",
}


def _build_html_body(body_text: str) -> str:
    return f"""<html><body style="font-family:sans-serif;padding:24px;background:#F8F6F3">
<div style="max-width:480px;margin:0 auto;background:white;border-radius:12px;padding:24px;border:1px solid #E3DFD8">
<div style="width:32px;height:32px;background:#1A3C5E;border-radius:8px;display:flex;align-items:center;justify-content:center;margin-bottom:16px">
<span style="color:white;font-weight:bold;font-size:14px">D</span></div>
{body_text}
</div></body></html>"""


def send_email_resend(to_email: str, subject: str, html_body: str) -> bool:
    api_key = settings.resend_api_key
    from_email = settings.resend_from_email or "noreply@drs.local"

    if not api_key:
        logger.warning("Resend API key not configured — email not sent to %s", to_email)
        return False

    try:
        resp = httpx.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "from": from_email,
                "to": [to_email],
                "subject": subject,
                "html": html_body,
            },
            timeout=15,
        )
        if resp.is_success:
            logger.info("Email sent via Resend to %s: %s", to_email, subject)
            return True
        else:
            logger.error("Resend API error: %s %s", resp.status_code, resp.text)
            return False
    except Exception as e:
        logger.error("Resend send failed: %s", e)
        return False


def send_dispute_notification(
    to_email: str,
    action: str,
    transaction_id: str,
    extra: Optional[dict] = None,
) -> bool:
    template = TEMPLATES.get(action)
    if not template:
        return False

    body = template.format(transaction_id=transaction_id, **(extra or {}))
    title_map = {
        "DISPUTE_CREATED": "Dispute Filed",
        "EVIDENCE_UPLOADED": "Evidence Uploaded",
        "AUTO_FETCH_COMPLETED": "Data Fetched",
        "DECISION_RENDERED": "Decision Made",
        "CLOSED": "Dispute Closed",
    }
    subject = f"[DRS] {title_map.get(action, action)} — #{transaction_id}"

    body_html = _build_html_body(f"""
<p style="font-size:14px;color:#1C1917;line-height:1.6">{body}</p>
<p style="font-size:12px;color:#6B6560;margin-top:16px">
  <a href="{settings.frontend_url}/portal" style="color:#2E5C8A">View in dashboard</a>
</p>
""")

    return send_email_resend(to_email, subject, body_html)
