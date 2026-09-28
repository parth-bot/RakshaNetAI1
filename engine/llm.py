import os
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
    """Check whether the Groq AI service is configured and reachable."""
    if not GROQ_API_KEY or client is None:
        return False

    try:
        client.models.list()
        return True
    except Exception:
        return False


def analyze_with_llm(text):
    """Analyze suspicious text using Groq."""

    if not client:
        return None

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are RakshaNet AI, a cybersecurity assistant. "
                        "Analyze messages for scams, phishing, fraud, "
                        "social engineering, suspicious payment requests, "
                        "malicious links, and other online threats. "
                        "Give a concise explanation and practical safety advice."
                    )
                },
                {
                    "role": "user",
                    "content": text
                }
            ],
            temperature=0.2,
            max_tokens=500
        )

        return response.choices[0].message.content

    except Exception as exc:
        return f"LLM_ERROR: {exc}"
