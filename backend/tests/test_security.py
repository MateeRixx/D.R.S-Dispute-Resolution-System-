from datetime import timedelta

import pytest

from app.core.security import create_access_token, decode_token, scrub_pii


def test_scrub_pii_removes_card_numbers():
    text = "My card is 4111 1111 1111 1111 and it was charged."
    result = scrub_pii(text)
    assert "[REDACTED_CARD]" in result
    assert "4111" not in result


def test_scrub_pii_removes_phone():
    text = "Call me at +91 9876543210 or 9876543210"
    result = scrub_pii(text)
    assert "[REDACTED_PHONE]" in result
    assert "9876543210" not in result


def test_scrub_pii_removes_email():
    text = "Contact support@example.com for help"
    result = scrub_pii(text)
    assert "[REDACTED_EMAIL]" in result
    assert "support@example.com" not in result


def test_scrub_pii_skips_clean_text():
    text = "This is a normal dispute with no sensitive data."
    result = scrub_pii(text)
    assert result == text


def test_create_and_decode_token():
    token = create_access_token(sub="user-123", role="ROLE_CARDHOLDER")
    payload = decode_token(token)
    assert payload["sub"] == "user-123"
    assert payload["role"] == "ROLE_CARDHOLDER"
    assert "exp" in payload
    assert "iat" in payload


def test_token_with_custom_expiry():
    token = create_access_token(sub="merchant-456", role="ROLE_MERCHANT", expires_delta=timedelta(minutes=5))
    payload = decode_token(token)
    assert payload["sub"] == "merchant-456"
    assert payload["role"] == "ROLE_MERCHANT"


def test_decode_invalid_token():
    with pytest.raises(Exception):
        decode_token("invalid-token-string")
