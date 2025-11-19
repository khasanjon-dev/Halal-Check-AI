from typing import List
from pydantic import BaseModel, Field


class HalalCheckRequest(BaseModel):
    """Request schema for halal check"""
    text: str = Field(..., description="Product description or ingredient list to analyze")
    device_id: str = Field(..., description="Unique device identifier")


class HalalCheckResult(BaseModel):
    """Result schema for halal check - matches Gemini response"""
    product_name: str
    is_halal: str  # "true", "false", or "doubtful"
    halal_reason: str
    is_edible: bool
    edible_reason: str
    detected_ingredients: List[str]
    harmful_or_suspicious: List[str]
    allergens: List[str]
    overall_summary: str


class HalalCheckResponse(BaseModel):
    """Response schema for halal check endpoint"""
    id: int
    device_id: str
    product_name: str
    is_halal: str
    is_edible: bool
    result: HalalCheckResult
    created_at: str

    class Config:
        from_attributes = True


class ProductCheckHistory(BaseModel):
    """Schema for product check history"""
    id: int
    product_name: str
    is_halal: str
    is_edible: bool
    created_at: str

    class Config:
        from_attributes = True

