import json
import requests
OLLAMA_URL='http://localhost:11434/api/generate'
MODEL='llama3.2:3b'
def analyze_with_llm(text, rule_result, upi_result, lang="English"):
    signals=[s['name'] for s in rule_result.get('signals',[])]
    prompt=f'''You are RakshaNet AI, an Indian cybersecurity assistant. Analyze this message for possible social-engineering fraud.
MESSAGE:\n{text}\nRULE SIGNALS:\n{json.dumps(signals)}\nRULE SCORE: {rule_result.get('score',0)}/100\nUPI IDS: {json.dumps(upi_result.get('upi_ids',[]))}\nAMOUNTS: {json.dumps(upi_result.get('amounts',[]))}\nClassify as LOW, MEDIUM, HIGH, or CRITICAL. Identify a scam category only when supported by evidence. Identify social-engineering tactics, concrete evidence, and safe practical advice. Do not invent facts. Do not call an unfamiliar UPI ID fraudulent solely because it is unfamiliar. Never ask for OTP, PIN, CVV, password, or other secrets. Write scam_category, summary, tactics, evidence and recommendation in {lang}. Keep classification in English (LOW, MEDIUM, HIGH or CRITICAL). Return ONLY valid JSON with keys classification, scam_category, summary, tactics, evidence, recommendation.'''
    try:
        r=requests.post(OLLAMA_URL,json={'model':MODEL,'prompt':prompt,'stream':False,'format':'json'},timeout=120); r.raise_for_status()
        return json.loads(r.json()['response'])
    except Exception as e:
        return {'classification':rule_result.get('level','UNKNOWN'),'scam_category':'AI reasoning unavailable','summary':'The local AI model could not be reached, so the rule-based assessment is being shown.','tactics':[],'evidence':[],'recommendation':'Use caution and independently verify the request through an official channel.','error':str(e)}
