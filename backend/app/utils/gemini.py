import json
import logging
from typing import Optional

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

Return response in this EXACT JSON structure:

{
  "product_name": "",
  "is_halal": "true"/"false"/"doubtful",
  "halal_reason": "",
  "is_edible": true/false,
  "edible_reason": "",
  "detected_ingredients": [],
  "harmful_or_suspicious": [],
  "allergens": [],
  "overall_summary": ""
}

Provide detailed reasoning in each field."""

    def __init__(self):
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not set in environment variables")

        genai.configure(api_key=settings.GEMINI_API_KEY)
        # Using models/gemini-1.5-flash-002 which is the current stable version
        self.model = genai.GenerativeModel("gemini-2.5-flash")

    async def analyze_product(self, product_text: str) -> dict:
        """
        Analyze product text for halal compliance and food safety

        Args:
            product_text: The product description or ingredient list

        Returns:
            Dictionary containing the analysis results
        """
        response_text = ""
        try:
            user_prompt = f"""Analyze the following product description for halal compliance and food safety:

"{product_text}"

Return ONLY the JSON as described in the system prompt."""

            full_prompt = f"{self.SYSTEM_PROMPT}\n\n{user_prompt}"

            logger.info(f"Sending request to Gemini API for product analysis")
            response = self.model.generate_content(full_prompt)

            # Extract JSON from response
            response_text = response.text.strip()

            # Remove markdown code blocks if present
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]

            response_text = response_text.strip()

            # Parse JSON
            result = json.loads(response_text)

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

            for field in required_fields:
                if field not in result:
                    raise ValueError(f"Missing required field: {field}")

            # Ensure is_halal is string
            if isinstance(result["is_halal"], bool):
                result["is_halal"] = "true" if result["is_halal"] else "false"

            # Ensure is_edible is boolean
            if isinstance(result["is_edible"], str):
                result["is_edible"] = result["is_edible"].lower() == "true"

            logger.info(
                f"Successfully analyzed product: {result.get('product_name', 'Unknown')}"
            )
            return result

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Response text: {response_text}")
            raise ValueError(f"Invalid JSON response from Gemini API: {str(e)}")
        except Exception as e:
            logger.error(f"Error calling Gemini API: {e}")
            raise

    async def analyze_image(
        self, image_bytes: bytes, mime_type: str = "image/jpeg"
    ) -> dict:
        """
        Analyze product image for halal compliance using OCR

        Args:
            image_bytes: The image binary data
            mime_type: MIME type of the image

        Returns:
            Dictionary containing the analysis results
        """
        response_text = ""
        try:
            user_prompt = """Analyze this product label image using OCR. Extract all visible text including:
- Product name
- Ingredients list
- Any relevant information

Then analyze for halal compliance and food safety.

Return ONLY the JSON as described in the system prompt."""

            full_prompt = f"{self.SYSTEM_PROMPT}\n\n{user_prompt}"

            logger.info("Sending image analysis request to Gemini API")

            # Create image part for Gemini
            image_part = {"mime_type": mime_type, "data": image_bytes}

            response = self.model.generate_content([full_prompt, image_part])

            # Extract text from response
            response_text = response.text.strip()

            # Remove markdown code blocks if present
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]

            response_text = response_text.strip()

            # Parse JSON
            result = json.loads(response_text)

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

            for field in required_fields:
                if field not in result:
                    raise ValueError(f"Missing required field: {field}")

            # Ensure is_halal is string
            if isinstance(result["is_halal"], bool):
                result["is_halal"] = "true" if result["is_halal"] else "false"

            # Ensure is_edible is boolean
            if isinstance(result["is_edible"], str):
                result["is_edible"] = result["is_edible"].lower() == "true"

            logger.info(
                f"Successfully analyzed image: {result.get('product_name', 'Unknown')}"
            )
            return result

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response from image: {e}")
            logger.error(f"Response text: {response_text}")
            raise ValueError(f"Invalid JSON response from Gemini API: {str(e)}")
        except Exception as e:
            logger.error(f"Error calling Gemini API for image: {e}")
            raise


# Singleton instance
_gemini_service: Optional[GeminiService] = None


def get_gemini_service() -> GeminiService:
    """Get or create Gemini service instance"""
    global _gemini_service
    if _gemini_service is None:
        _gemini_service = GeminiService()
    return _gemini_service
