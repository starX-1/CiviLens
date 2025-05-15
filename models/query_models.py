from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List

class QueryRequest(BaseModel):
    query: str = Field(..., description="The political query from the user")
    detail_level: str = Field(
        default="balanced", 
        description="The level of detail desired in the response"
    )
    topic_category: Optional[str] = Field(
        default=None, 
        description="Category like 'policy', 'candidate', 'governance', etc."
    )

class QueryResponse(BaseModel):
    summary: str = Field(..., description="A clear summary of the policy or bill")
    impact: str = Field(..., description="The potential impact on citizens")
    historical_context: str = Field(..., description="Historical background")
    constitutional_references: str = Field(
        default="", 
        description="Related constitutional articles"
    )
    full_response: str = Field(..., description="The complete response")
    
class ErrorResponse(BaseModel):
    error: bool = True
    message: str
    details: Optional[str] = None

class FaqItem(BaseModel):
    question: str
    category: str
    
class FaqList(BaseModel):
    faqs: List[FaqItem]