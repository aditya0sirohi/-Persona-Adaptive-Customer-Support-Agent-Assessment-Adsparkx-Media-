import os
import requests

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

TONE_TEMPLATES = {
    "Technical Expert": (
        "You are a technical support assistant. "
        "Provide a structured explanation using bullet points or numbered steps. "
        "Include technical terminology and reference retrieved context. "
        "Format your response for clarity and precision."
    ),
    "Frustrated User": (
        "You are a calm and empathetic support agent. "
        "Begin with an empathetic sentence acknowledging the user's frustration. "
        "Provide clear, short steps to resolve the issue. "
        "End with a reassuring statement that support is available."
    ),
    "Business Executive": (
        "You are a strategic support advisor. "
        "Start with a concise summary (1–2 lines) of the solution or insight. "
        "Provide 2–3 bullet points highlighting business impact or outcomes. "
        "Avoid technical jargon and keep the response focused on strategic value."
    )
}

def generate_response(query: str, persona: str, context: list[str]) -> str:
    api_key = os.getenv("OPENROUTER_API_KEY")
    system_prompt = TONE_TEMPLATES.get(persona, TONE_TEMPLATES["Business Executive"])
    context_str = "\n".join(context)
    full_prompt = f"""
SYSTEM INSTRUCTIONS:
{system_prompt}

RETRIEVED KNOWLEDGE:
{context_str}

USER QUESTION:
{query}

INSTRUCTIONS:
- Use only the retrieved knowledge when possible.
- If knowledge is insufficient, clearly state limitation.
- Follow the persona response structure strictly.
"""
    if api_key:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "openrouter/auto",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": full_prompt}
            ],
            "max_tokens": 256,
            "temperature": 0.2
        }
        try:
            resp = requests.post(OPENROUTER_API_URL, headers=headers, json=payload, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            answer = data["choices"][0]["message"]["content"].strip()
            return answer
        except Exception:
            pass  # Fallback below
    # Fallback offline response
    fallback = f"""
[Offline Mode Response]

Based on our documentation:
{context[0] if context else 'No relevant documentation found.'}

Please contact support if you need more assistance.
"""
    return fallback