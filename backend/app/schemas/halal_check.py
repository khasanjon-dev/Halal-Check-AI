from pydantic import BaseModel
from typing import List


class IngredientEvidence(BaseModel):
    title: str
    snippet: str
    link: str


class IngredientAnalysis(BaseModel):
    ingredient: str
    is_halal: str  # "true" | "false" | "doubtful"
    reason: str
    evidence: List[IngredientEvidence]
    confidence: int


class HalalCheckResult(BaseModel):
    product_name: str
    is_halal: str
    is_edible: bool
    ingredients_analysis: List[IngredientAnalysis]
    overall_summary: str


class HalalCheckRequest(BaseModel):
    text: str
    device_id: str


class HalalCheckResponse(BaseModel):
    id: int
    device_id: str
    product_name: str
    is_halal: str
    is_edible: bool
    result: HalalCheckResult
    created_at: str


class ProductCheckHistory(BaseModel):
    id: int
    product_name: str
    is_halal: str
    is_edible: bool
    created_at: str