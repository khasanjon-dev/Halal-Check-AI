import asyncio
import json
import logging
import re
from typing import List, Dict, Any

import google.generativeai as genai

from app.config.core import settings
from app.utils.search import FreeSearchService

logger = logging.getLogger(__name__)


class GeminiService:
    def __init__(self, api_key: str, gemini_model: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(gemini_model)
        self.search_service = FreeSearchService()

    # ---------- JSON parsing ----------
    def _safe_json(self, text: str, fallback: Any) -> Any:
        """Extract JSON from Gemini response, handling markdown and malformed output."""
        try:
            # Remove markdown code fences
            text = re.sub(r"```json|```", "", text).strip()
            # Find first JSON structure
            start = text.find('{')
            if start == -1:
                start = text.find('[')
            end = text.rfind('}') if start >= 0 and text[start] == '{' else text.rfind(']')
            if start == -1 or end == -1:
                raise ValueError("No JSON found")
            json_str = text[start:end + 1]
            return json.loads(json_str)
        except Exception as e:
            logger.warning(f"JSON parse failed: {e}")
            return fallback

    # ---------- Classification ----------
    def classify_product_type(self, text: str) -> dict:
        prompt = f"""
        Classify this product:

        "{text}"

        Return JSON:
        {{
          "is_food": true/false,
          "category": "food|cosmetic|book|electronics|other",
          "reason": "short explanation"
        }}
        """
        res = self.model.generate_content(prompt)
        return self._safe_json(res.text, {"is_food": False, "category": "unknown", "reason": "Could not classify"})

    # ---------- Ingredient extraction ----------
    def extract_ingredients(self, text: str) -> List[str]:
        prompt = f"""
        Extract ingredients from:

        "{text}"

        Return JSON list:
        ["ingredient1", "ingredient2"]
        """
        res = self.model.generate_content(prompt)
        ingredients = self._safe_json(res.text, [])
        if isinstance(ingredients, list):
            return [i.strip().lower() for i in ingredients if isinstance(i, str)]
        return []

    # ---------- Batch AI analysis ----------
    async def analyze_ingredients_batch(self, ingredients: List[str]) -> List[Dict[str, Any]]:
        """One Gemini call for all ingredients."""
        if not ingredients:
            return []
        prompt = f"""
        For each of the following ingredients, tell whether it is halal or haram.
        Return a JSON array of objects, each with:
          - "ingredient": the ingredient name (exactly as given)
          - "is_halal": "true"|"false"|"doubtful"
          - "reason": short explanation
          - "confidence": 0-100

        Ingredients:
        {", ".join(ingredients)}
        """
        loop = asyncio.get_event_loop()
        res = await loop.run_in_executor(None, self.model.generate_content, prompt)
        data = self._safe_json(res.text, [])

        # Convert dict to list if needed (e.g., {"0": {...}, "1": {...}})
        if isinstance(data, dict):
            try:
                sorted_keys = sorted(data.keys(), key=lambda x: int(x) if x.isdigit() else float('inf'))
                data = [data[k] for k in sorted_keys]
            except Exception:
                data = list(data.values())

        if not isinstance(data, list):
            data = []

        # Build result list matching input order
        result = []
        for i, ing in enumerate(ingredients):
            item = data[i] if i < len(data) else {}
            if not isinstance(item, dict):
                item = {}
            result.append({
                "ingredient": ing,
                "is_halal": item.get("is_halal", "doubtful"),
                "reason": item.get("reason", "unknown"),
                "confidence": item.get("confidence", 50)
            })
        return result

    # ---------- Google analysis for a single ingredient ----------
    def analyze_google(self, ingredient: str, evidence: List[dict]) -> dict:
        if not evidence:
            return {"decision": "unclear", "summary": "No search results", "links": []}
        text = "\n".join(f"{e.get('title', '')} - {e.get('snippet', '')}" for e in evidence)
        prompt = f"""
        Ingredient: {ingredient}

        Based ONLY on this:

        {text}

        Return JSON:
        {{
          "decision": "halal|haram|mixed|unclear",
          "summary": "short explanation"
        }}
        """
        res = self.model.generate_content(prompt)
        google_result = self._safe_json(res.text, {"decision": "unclear", "summary": "Could not determine"})
        google_result["links"] = evidence
        return google_result

    # ---------- Process a single ingredient with search ----------
    async def process_ingredient(self, ingredient: str, ai_result: dict, is_food: bool = True) -> dict:
        loop = asyncio.get_event_loop()
        # Build search query with context to disambiguate
        if is_food:
            query = f"{ingredient} halal or haram food ingredient"
        else:
            query = f"{ingredient} halal or haram"
        try:
            evidence = await asyncio.wait_for(
                loop.run_in_executor(None, self.search_service.search, query),
                timeout=5
            )
        except Exception:
            evidence = []
        google_result = await loop.run_in_executor(None, self.analyze_google, ingredient, evidence)
        return {
            "ingredient": ingredient,
            "ai_analysis": ai_result,
            "google_analysis": google_result
        }

    # ---------- Main product analysis ----------
    async def analyze_product(self, text: str) -> dict:
        # Step 1: classify
        product_type = self.classify_product_type(text)
        is_food = product_type.get("is_food", False)
        if not is_food:
            return {
                "product_name": text[:50],
                "is_edible": False,
                "category": product_type.get("category"),
                "ingredients_analysis": [],
                "overall_summary": f"Not a food product. {product_type.get('reason')}"
            }

        # Step 2: extract ingredients
        ingredients = self.extract_ingredients(text)
        if not ingredients:
            return {
                "product_name": text[:50],
                "is_edible": True,
                "is_halal": "doubtful",
                "ingredients_analysis": [],
                "overall_summary": "No ingredients detected"
            }

        # Step 3: batch AI analysis
        ai_results = await self.analyze_ingredients_batch(ingredients)

        # Step 4: parallel Google searches + combine
        tasks = [self.process_ingredient(ing, ai, is_food) for ing, ai in zip(ingredients, ai_results)]
        combined_results = await asyncio.gather(*tasks)

        # Step 5: flatten per-ingredient results for the schema
        flattened_ingredients = []
        for combined in combined_results:
            ai = combined["ai_analysis"]
            google = combined["google_analysis"]

            final_is_halal = ai["is_halal"]
            if google.get("decision") == "haram":
                final_is_halal = "false"
            elif google.get("decision") == "halal" and final_is_halal == "doubtful":
                final_is_halal = "true"

            reason = f"{ai['reason']} (Google: {google.get('summary', 'no info')})"

            evidence = []
            for link in google.get("links", []):
                evidence.append({
                    "title": link.get("title", ""),
                    "snippet": link.get("snippet", ""),
                    "link": link.get("link", "")
                })

            flattened_ingredients.append({
                "ingredient": combined["ingredient"],
                "is_halal": final_is_halal,
                "reason": reason,
                "evidence": evidence,
                "confidence": ai.get("confidence", 50)
            })

        # Step 6: final product decision
        final_product_halal = "true"
        for ing in flattened_ingredients:
            if ing["is_halal"] == "false":
                final_product_halal = "false"
                break
            elif ing["is_halal"] == "doubtful":
                final_product_halal = "doubtful"

        return {
            "product_name": text[:50],
            "is_edible": True,
            "is_halal": final_product_halal,
            "ingredients_analysis": flattened_ingredients,
            "overall_summary": "Analysis completed"
        }

    # ---------- Image analysis (placeholder) ----------
    async def analyze_image(self, image_bytes: bytes, content_type: str) -> dict:
        # For a real implementation, use Gemini Vision to extract text from the image
        # and then call analyze_product with that text.
        # This example returns a placeholder.
        return {
            "product_name": "Image product",
            "is_edible": True,
            "is_halal": "doubtful",
            "ingredients_analysis": [],
            "overall_summary": "Image OCR not implemented in this example."
        }


# ---------- Singleton ----------
_gemini_service = None


def get_gemini_service() -> GeminiService:
    global _gemini_service
    if _gemini_service is None:
        _gemini_service = GeminiService(
            api_key=settings.GEMINI_API_KEY,
            gemini_model=settings.GEMINI_MODEL
        )
    return _gemini_service
