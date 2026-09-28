import os
import json
import re
from openai import OpenAI

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

MODEL = os.getenv(
    "GROQ_MODEL",
    "openai/gpt-oss-20b"
)

client = None

if GROQ_API_KEY:
    client = OpenAI(
        api_key=GROQ_API_KEY,
        base_url="https://api.groq.com/openai/v1"
    )


def llm_available():
    """Check whether Groq AI is configured and reachable."""
    if not GROQ_API_KEY or client is None:
        return False

    try:
        client.models.list()
        return True
    except Exception:
        return False


def _extract_json(text):
    """Extract JSON even if the model wraps it in markdown."""
    if not text:
        return None

    text = text.strip()

    # Remove ```json ... ``` if present
    match = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL)

    if match:
        text = match.group(1).strip()

    try:
        return json.loads(text)
    except Exception:
        return None


def analyze_with_llm(text, result=None, payment=None, language="English"):
    """Analyze suspicious text using Groq and return RakshaNet's expected structure."""

    fallback = {
        "classification": result.get("level", "UNKNOWN") if result else "UNKNOWN",
        "scam_category": "AI unavailable",
        "tactics": [],
        "evidence": [],
        "recommendation": "Do not click suspicious links or send money until the message is verified.",
        "summary": "The AI analysis service is currently unavailable.",
    }

    if not client:
        fallback["error"] = "Groq API key not configured"
        return fallback

    result = result or {}
    payment = payment or {}

    prompt = f"""
Analyze the following message for RakshaNet AI.

Return ONLY valid JSON. Do not use markdown.

The JSON must contain exactly these fields:
{{
  "classification": "CRITICAL/HIGH/MEDIUM/LOW",
  "scam_category": "string",
  "tactics": ["string"],
  "evidence": ["string"],
  "recommendation": "string",
  "summary": "string"
}}

Rules:
- Be conservative and evidence-based.
- Do not claim something is a scam unless the message contains supporting indicators.
- Explain suspicious indicators clearly.
- Give practical safety advice.
- Respond in {language}.

Rule-engine result:
{json.dumps(result, ensure_ascii=False)}

Payment analysis:
{json.dumps(payment, ensure_ascii=False)}

Message:
{text}
"""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are RakshaNet AI, a cybersecurity and "
                        "online-scam detection assistant."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0.2,
            max_tokens=700,
        )

        content = response.choices[0].message.content
        parsed = _extract_json(content)

        if not parsed:
            fallback["error"] = "AI returned invalid JSON"
            return fallback

        # Ensure expected fields always exist
        parsed.setdefault("classification", result.get("level", "UNKNOWN"))
        parsed.setdefault("scam_category", "Unknown")
        parsed.setdefault("tactics", [])
        parsed.setdefault("evidence", [])
        parsed.setdefault(
            "recommendation",
            "Verify the message before clicking links or sending money."
        )
        parsed.setdefault("summary", "AI analysis completed.")

        return parsed

    except Exception as exc:
        fallback["error"] = str(exc)
        return fallback
