import httpx
import json
from typing import Dict, Any, Optional
from core.config import settings

class DeepSeekService:
    def __init__(self):
        self.api_key = settings.DEEPSEEK_API_KEY
        self.api_url = settings.DEEPSEEK_API_URL
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
    
    async def generate_response(
        self, 
        query: str, 
        detail_level: str = "balanced", 
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate a response from DeepSeek based on the political query.
        
        Args:
            query: The user's political question
            detail_level: 'simplified', 'balanced', or 'detailed'
            context: Any additional context (constitution sections, etc.)
            
        Returns:
            Dictionary containing the structured response
        """
        # Determine max tokens based on detail level
        max_tokens = settings.SIMPLIFIED_RESPONSE_TOKENS
        if detail_level == "detailed":
            max_tokens = settings.DETAILED_RESPONSE_TOKENS
        elif detail_level == "balanced":
            max_tokens = (settings.SIMPLIFIED_RESPONSE_TOKENS + settings.DETAILED_RESPONSE_TOKENS) // 2
            
        # Create system prompt based on our civic education goals
        system_prompt = """
        You are CivicLens, an educational AI designed to explain Kenyan political policies, laws, and governance 
        in a clear, factual, and unbiased manner. Your goal is to enhance political literacy.
        
        When explaining political topics:
        1. Focus on facts and avoid partisan language
        2. Provide historical context when relevant
        3. Explain potential impacts on ordinary citizens
        4. Reference constitutional articles when applicable
        5. Use simple language that is accessible to all education levels
        6. Structure your response clearly with relevant sections
        
        Your role is to EDUCATE, not persuade or take political positions.
        """
        
        # Enhanced prompt with any context
        context_text = ""
        if context:
            if "constitution_sections" in context:
                context_text += f"\nRelevant constitutional sections: {context['constitution_sections']}\n"
            if "policy_data" in context:
                context_text += f"\nRelevant policy information: {context['policy_data']}\n"
        
        # Detail level instructions
        level_instructions = {
            "simplified": "Explain this like I'm 12 years old, using very simple language and basic concepts.",
            "balanced": "Provide a balanced explanation suitable for an average adult citizen.",
            "detailed": "Provide a comprehensive explanation with nuanced details and specific references."
        }
        
        # Construct the user message with context and detail level
        user_message = f"{query}\n\n{context_text}\n\n{level_instructions[detail_level]}"
        
        payload = {
            "model": "deepseek-chat",  # Use appropriate DeepSeek model
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "max_tokens": max_tokens,
            "temperature": 0.3  # Lower temperature for more factual responses
        }
        
        # Make the API request
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.api_url,
                    headers=self.headers,
                    json=payload,
                    timeout=30.0
                )
                response.raise_for_status()  # Raises exception for 4xx/5xx errors
                result = response.json()
                ai_response = result["choices"][0]["message"]["content"]
                
                # Parse and structure the response
                structured_response = self._structure_response(ai_response)
                return structured_response
            except httpx.HTTPStatusError as e:
                return {"error": True, "message": f"HTTP error: {e.response.status_code}", "details": e.response.text}
            except httpx.RequestError as e:
                return {"error": True, "message": "Request failed", "details": str(e)}
            except Exception as e:
                return {"error": True, "message": "Unexpected error", "details": str(e)}
    
    def _structure_response(self, raw_response: str) -> Dict[str, Any]:
        """
        Parse and structure the raw LLM response into consistent sections.
        This is a simple implementation - in production, we might use more 
        sophisticated extraction with regex or a structured output format.
        """
        sections = {
            "summary": "",
            "impact": "",
            "historical_context": "",
            "constitutional_references": "",
            "full_response": raw_response
        }
        
        # Simple parsing based on keywords - in production we would
        # use a more robust approach or prompt the LLM for structured JSON
        lines = raw_response.split('\n')
        current_section = "summary"
        
        for line in lines:
            line = line.strip()
            
            if not line:
                continue
                
            # Check for section headers
            lower_line = line.lower()
            if "impact" in lower_line or "effect" in lower_line:
                current_section = "impact"
            elif "history" in lower_line or "background" in lower_line or "context" in lower_line:
                current_section = "historical_context"
            elif "constitution" in lower_line or "article" in lower_line:
                current_section = "constitutional_references"
            
            # Add content to the current section
            sections[current_section] += f"\n{line}"
        
        # If summary is empty, use the first paragraph
        if not sections["summary"]:
            sections["summary"] = sections["full_response"].split("\n\n")[0]
        
        return sections

deepseek_service = DeepSeekService()
