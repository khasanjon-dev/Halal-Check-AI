from pydantic import BaseModel
from typing import List, Dict


class Evidence(BaseModel):
    title: str
    snippet: str
    link: str


class GoogleAnalysis(BaseModel):
    decision: str
    summary: str
    links: List[Evidence]


class IngredientAnalysis(BaseModel):
    ingredient: str
    ai_analysis: Dict
    google_analysis: GoogleAnalysis