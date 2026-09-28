import json
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.2:3b"

def analyze_conversation(messages, lang="English"):
    conversation_text = "\n".join(f"Message {i + 1}: {message}" for i, message in enumerate(messages))
    prompt = f'''You are RakshaNet AI, an Indian cybersecurity assistant.

Analyze this conversation for possible social-engineering fraud.

CONVERSATION:
{conversation_text}

Look for:
- Building trust before asking for something
- Urgency or time pressure
- Impersonation
- Requests for money or UPI payments
- Requests for OTP, PIN, CVV or passwords
- Threats or intimidation
- Fake rewards or offers
- Suspicious links
- Attempts to move the victim to another platform
- Repeated pressure
- Requests to keep the interaction secret

Important:
- Do not invent facts.
- Do not assume someone is fraudulent without evidence.
- Clearly express uncertainty.
- Never ask the user to provide an OTP, PIN, CVV, password or other secret.
- Focus on observable behaviour.
- Write conversation_pattern, scam_category, tactics, evidence and recommendation in {lang}. Keep classification in English (LOW/MEDIUM/HIGH/CRITICAL).

Return ONLY valid JSON:
{{
    "classification": "LOW/MEDIUM/HIGH/CRITICAL",
    "scam_category": "category or Unknown",
    "risk_score": 0,
    "conversation_pattern": "short explanation",
    "tactics": ["tactic 1", "tactic 2"],
    "evidence": ["evidence 1", "evidence 2"],
    "recommendation": "safe practical advice"
}}'''
    try:
        response = requests.post(OLLAMA_URL, json={"model": MODEL, "prompt": prompt, "stream": False, "format": "json"}, timeout=120)
        response.raise_for_status()
        return json.loads(response.json()["response"])
    except Exception as exc:
        return {
            "classification": "UNKNOWN",
            "scam_category": "AI reasoning unavailable",
            "risk_score": 0,
            "conversation_pattern": "The local AI model could not analyze the conversation.",
            "tactics": [],
            "evidence": [],
            "recommendation": "Do not send money or sensitive information until the request has been independently verified.",
            "error": str(exc),
        }
