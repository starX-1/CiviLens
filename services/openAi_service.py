from openai import AsyncOpenAI
from typing import Dict, Any, Optional
from core.config import settings

class OpenAIService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def generate_response(
        self, 
        query: str, 
        detail_level: str = "balanced", 
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        max_tokens = settings.SIMPLIFIED_RESPONSE_TOKENS
        if detail_level == "detailed":
            max_tokens = settings.DETAILED_RESPONSE_TOKENS
        elif detail_level == "balanced":
            max_tokens = (settings.SIMPLIFIED_RESPONSE_TOKENS + settings.DETAILED_RESPONSE_TOKENS) // 2

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

        context_text = ""
        if context:
            if "constitution_sections" in context:
                context_text += f"\nRelevant constitutional sections: {context['constitution_sections']}\n"
            if "policy_data" in context:
                context_text += f"\nRelevant policy information: {context['policy_data']}\n"

        level_instructions = {
            "simplified": "Explain this like I'm 12 years old, using very simple language and basic concepts.",
            "balanced": "Provide a balanced explanation suitable for an average adult citizen.",
            "detailed": "Provide a comprehensive explanation with nuanced details and specific references."
        }

        user_message = f"{query}\n\n{context_text}\n\n{level_instructions[detail_level]}"

        try:
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=max_tokens,
                temperature=0.3
            )

            ai_response = response.choices[0].message.content
            return self._structure_response(ai_response)

        except Exception as e:
            return {"error": True, "message": "Error from OpenAI", "details": str(e)}

    def _structure_response(self, raw_response: str) -> Dict[str, Any]:
        sections = {
            "summary": "",
            "impact": "",
            "historical_context": "",
            "constitutional_references": "",
            "full_response": raw_response
        }

        lines = raw_response.split('\n')
        current_section = "summary"

        for line in lines:
            line = line.strip()
            if not line:
                continue

            lower_line = line.lower()
            if "impact" in lower_line or "effect" in lower_line:
                current_section = "impact"
            elif "history" in lower_line or "background" in lower_line or "context" in lower_line:
                current_section = "historical_context"
            elif "constitution" in lower_line or "article" in lower_line:
                current_section = "constitutional_references"

            sections[current_section] += f"\n{line}"

        if not sections["summary"]:
            sections["summary"] = sections["full_response"].split("\n\n")[0]

        return sections

openai_service = OpenAIService()
