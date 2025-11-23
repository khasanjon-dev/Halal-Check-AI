import json
import logging
from typing import Optional, Dict, Any

import google.generativeai as genai

from app.config.core import settings

logger = logging.getLogger(__name__)


class GeminiService:
    """Service for interacting with Google Gemini API"""

    SYSTEM_PROMPT = """You are a strict and reliable Halal Compliance and Food Safety checker. Your job is to analyze ANY product description, ingredient list, or textual product data and return a detailed halal/haram evaluation with clear explanations.

Follow these rules:
1. Be accurate and strict about halal requirements.
2. If an ingredient is unclear, treat it as "doubtful" and explain why.
3. Do NOT guess. Use reasoning based on general halal principles.
4. Provide results ONLY in JSON format.
5. Include human-edible safety checks (allergens, harmful substances, dietary concerns).
6. Never include unnecessary text outside the JSON.
7. is_halal MUST be one of: "true", "false", or "doubtful" (lowercase string)
8. is_edible MUST be a boolean: true or false

Return response in this EXACT JSON structure:

{
  "product_name": "string",
  "is_halal": "true"/"false"/"doubtful",
  "halal_reason": "string",
  "is_edible": true/false,
  "edible_reason": "string",
  "detected_ingredients": ["string"],
  "harmful_or_suspicious": ["string"],
  "allergens": ["string"],
  "overall_summary": "string"
}

Provide detailed reasoning in each field."""

    def __init__(self):
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not set in environment variables")

        genai.configure(api_key=settings.GEMINI_API_KEY)
        # Using the latest Gemini Flash model for fast, efficient responses
        self.model = genai.GenerativeModel("gemini-2.5-flash")

    def _parse_gemini_response(self, response_text: str) -> Dict[str, Any]:
        """Parse and validate Gemini API response"""
        # Remove markdown code blocks if present
        cleaned_text = response_text.strip()

        if cleaned_text.startswith("```json"):
            cleaned_text = cleaned_text[7:]
        elif cleaned_text.startswith("```"):
            cleaned_text = cleaned_text[3:]

        if cleaned_text.endswith("```"):
            cleaned_text = cleaned_text[:-3]

        cleaned_text = cleaned_text.strip()

        # Parse JSON
        try:
            result = json.loads(cleaned_text)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Response text: {cleaned_text}")
            raise ValueError(f"Invalid JSON response from Gemini API: {str(e)}")

        # Validate required fields
        required_fields = [
            "product_name",
            "is_halal",
            "halal_reason",
            "is_edible",
            "edible_reason",
            "detected_ingredients",
            "harmful_or_suspicious",
            "allergens",
            "overall_summary",
        ]

        missing_fields = [field for field in required_fields if field not in result]
        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

        # Normalize is_halal to string
        if isinstance(result["is_halal"], bool):
            result["is_halal"] = "true" if result["is_halal"] else "false"
        elif isinstance(result["is_halal"], str):
            result["is_halal"] = result["is_halal"].lower()
            # Validate it's one of the acceptable values
            if result["is_halal"] not in ["true", "false", "doubtful"]:
                logger.warning(
                    f"Invalid is_halal value: {result['is_halal']}, defaulting to 'doubtful'"
                )
                result["is_halal"] = "doubtful"

        # Normalize is_edible to boolean
        if isinstance(result["is_edible"], str):
            result["is_edible"] = result["is_edible"].lower() in ["true", "yes", "1"]
        elif not isinstance(result["is_edible"], bool):
            result["is_edible"] = False

        # Ensure arrays are actually arrays
        for array_field in [
            "detected_ingredients",
            "harmful_or_suspicious",
            "allergens",
        ]:
            if not isinstance(result[array_field], list):
                result[array_field] = []

        # Ensure strings are actually strings
        for string_field in [
            "product_name",
            "halal_reason",
            "edible_reason",
            "overall_summary",
        ]:
            if not isinstance(result[string_field], str):
                result[string_field] = str(result[string_field])

        return result

    async def analyze_product(self, product_text: str) -> Dict[str, Any]:
        """
        Analyze product text for halal compliance and food safety

        Args:
            product_text: The product description or ingredient list

        Returns:
            Dictionary containing the analysis results

        Raises:
            ValueError: If the response is invalid or cannot be parsed
            Exception: For other API errors
        """
        if not product_text or not product_text.strip():
            raise ValueError("Product text cannot be empty")

        try:
            user_prompt = f"""Analyze the following product description for halal compliance and food safety:

"{product_text.strip()}"

Return ONLY the JSON as described in the system prompt. No additional text or explanation."""

            full_prompt = f"{self.SYSTEM_PROMPT}\n\n{user_prompt}"

            logger.info("Sending request to Gemini API for product analysis")
            response = self.model.generate_content(full_prompt)

            if not response or not response.text:
                raise ValueError("Empty response from Gemini API")

            result = self._parse_gemini_response(response.text)

            logger.info(
                f"Successfully analyzed product: {result.get('product_name', 'Unknown')}, "
                f"Halal: {result.get('is_halal')}, Edible: {result.get('is_edible')}"
            )
            return result

        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error calling Gemini API: {e}", exc_info=True)
            raise Exception(f"Failed to analyze product: {str(e)}")

    async def analyze_image(
        self, image_bytes: bytes, mime_type: str = "image/jpeg"
    ) -> Dict[str, Any]:
        """
        Analyze product image for halal compliance using OCR

        Args:
            image_bytes: The image binary data
            mime_type: MIME type of the image

        Returns:
            Dictionary containing the analysis results

        Raises:
            ValueError: If the response is invalid or cannot be parsed
            Exception: For other API errors
        """
        if not image_bytes or len(image_bytes) == 0:
            raise ValueError("Image data cannot be empty")

        try:
            user_prompt = """Analyze this product label image using OCR. Extract all visible text including:
- Product name
- Ingredients list
- Nutritional information
- Any certifications or labels
- Any relevant food safety information

Then analyze the extracted information for halal compliance and food safety.

Return ONLY the JSON as described in the system prompt. No additional text or explanation."""

            full_prompt = f"{self.SYSTEM_PROMPT}\n\n{user_prompt}"

            logger.info(
                f"Sending image analysis request to Gemini API (mime_type: {mime_type})"
            )

            # Create image part for Gemini
            image_part = {"mime_type": mime_type, "data": image_bytes}

            response = self.model.generate_content([full_prompt, image_part])

            if not response or not response.text:
                raise ValueError("Empty response from Gemini API")

            result = self._parse_gemini_response(response.text)

            logger.info(
                f"Successfully analyzed image: {result.get('product_name', 'Unknown')}, "
                f"Halal: {result.get('is_halal')}, Edible: {result.get('is_edible')}"
            )
            return result

        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error calling Gemini API for image: {e}", exc_info=True)
            raise Exception(f"Failed to analyze image: {str(e)}")


# Singleton instance
_gemini_service: Optional[GeminiService] = None


def get_gemini_service() -> GeminiService:
    """Get or create Gemini service instance"""
    global _gemini_service
    if _gemini_service is None:
        _gemini_service = GeminiService()
    return _gemini_service
