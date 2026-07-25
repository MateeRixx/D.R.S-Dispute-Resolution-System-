import json
import os

from google import genai
from google.genai import types as genai_types

from app.core.config import settings

OCR_PROMPT = """Extract all key-value fields from this receipt or tax invoice.
Return ONLY valid JSON with no markdown formatting, using this exact structure:
{
  "invoice_number": "string or null",
  "invoice_date": "YYYY-MM-DD or null",
  "vendor_name": "string or null",
  "line_items": [{"description": "string", "quantity": number, "unit_price": number, "total": number}],
  "total_amount": number or null,
  "currency": "string or null",
  "tax_amount": number or null
}
Fill null for any field you cannot determine confidently."""

VISION_PROMPT = """Analyse this product image for physical defects or damage.
Return ONLY valid JSON with no markdown formatting, using this exact structure:
{
  "defects_detected": true or false,
  "defect_regions": [
    {
      "label": "cracked_screen | broken_seal | dent | scratch | discolouration | wrong_colour | other",
      "confidence": 0.0 to 1.0,
      "bbox": [x, y, width, height]
    }
  ],
  "overall_condition": "description of the item's physical state"
}
If no defects found, return defects_detected: false and an empty defect_regions array."""


class OCRVisionService:

    def __init__(self):
        self.client = None
        self.model = "gemini-2.0-flash"
        self._init_client()

    def _init_client(self):
        api_key = settings.gemini_api_key or os.getenv("GEMINI_API_KEY")
        if api_key:
            self.client = genai.Client(api_key=api_key)

    def is_available(self) -> bool:
        return self.client is not None

    def _encode_image(self, image_bytes: bytes) -> genai_types.Part:
        return genai_types.Part.from_bytes(
            data=image_bytes,
            mime_type="image/jpeg",
        )

    def run_ocr(self, image_bytes: bytes) -> dict:
        if not self.is_available():
            return {"error": "Gemini API not configured", "invoice_number": None}

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=[OCR_PROMPT, self._encode_image(image_bytes)],
                config=genai_types.GenerateContentConfig(
                    temperature=0.1,
                    max_output_tokens=1024,
                ),
            )
            return self._parse_response(response.text)
        except Exception as e:
            return {"error": str(e), "invoice_number": None}

    def run_vision_analysis(self, image_bytes: bytes) -> dict:
        if not self.is_available():
            return {"error": "Gemini API not configured", "defects_detected": False}

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=[VISION_PROMPT, self._encode_image(image_bytes)],
                config=genai_types.GenerateContentConfig(
                    temperature=0.2,
                    max_output_tokens=1024,
                ),
            )
            return self._parse_response(response.text)
        except Exception as e:
            return {"error": str(e), "defects_detected": False}

    def _parse_response(self, text: str) -> dict:
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {"error": "Failed to parse Gemini response", "raw": text}


ocr_service = OCRVisionService()
