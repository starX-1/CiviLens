from fastapi import APIRouter, HTTPException, Depends
from models.query_models import QueryRequest, QueryResponse, ErrorResponse, FaqList
from services.llm_service import deepseek_service
from services.openAi_service import openai_service
from services.cache_service import cache_service
from typing import List, Dict, Any
from fastapi.responses import JSONResponse
from fastapi import status

router = APIRouter()

@router.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    try:
        # Check cache
        cached_response = await cache_service.get_cached_response(
            request.query, request.detail_level
        )
        if cached_response:
            return cached_response

        # Context building
        context = {}
        if request.topic_category == "constitution":
            context["constitution_sections"] = "Sample constitution sections"
        elif request.topic_category == "policy":
            context["policy_data"] = "Sample policy data"

        # Call DeepSeek (LLM)
        # response = await deepseek_service.generate_response(
        #     request.query, request.detail_level, context
        # )
        # call openAi service
        response = await openai_service.generate_response(
            request.query, request.detail_level, context
        )

        # If DeepSeek returns an error, return custom response directly
        if isinstance(response, dict) and response.get("error"):
            return JSONResponse(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                content={
                    "error": True,
                    "message": response.get("message", "LLM request failed"),
                    "details": response.get("details", {})
                }
            )

        # Cache and return valid response
        await cache_service.cache_response(
            request.query, request.detail_level, response
        )
        return response

    except Exception as e:
        # Logging the error could be useful here
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": True,
                "message": "Internal server error occurred.",
                "details": str(e)
            }
        )

@router.get("/faqs", response_model=FaqList)
async def get_faqs():
    """
    Return a list of frequently asked questions
    """
    # In production, these would come from a database
    faqs = [
        {"question": "What does the Finance Bill 2024 mean for ordinary Kenyans?", "category": "policy"},
        {"question": "How does devolution affect my county's budget?", "category": "governance"},
        {"question": "What were the main promises in the 2022 elections?", "category": "politics"},
        {"question": "How is the judiciary structured in Kenya?", "category": "constitution"},
        {"question": "What are my rights as a Kenyan citizen?", "category": "rights"}
    ]
    
    return {"faqs": faqs}
