import re

URGENCY = ["immediately", "urgent", "urgently", "urgent action", "within 10 minutes",
           "within 24 hours", "today", "expires today", "act now", "last chance",
           "account will be blocked", "account will be suspended", "limited time",
           "expires in"]
PAYMENT = ["pay", "payment", "send money", "transfer", "processing fee",
           "verification fee", "deposit", "\u20b9", "rs.", "rupees", "send"]
CREDENTIAL = ["otp", "one time password", "pin", "upi pin", "cvv", "password",
              "verification code"]
ORGS = {"sbi": "SBI", "hdfc": "HDFC Bank", "icici": "ICICI Bank", "axis bank": "Axis Bank",
        "rbi": "RBI", "income tax": "Income Tax Dept", "police": "Police",
        "government": "Government", "courier": "Courier service", "amazon": "Amazon",
        "flipkart": "Flipkart", "paytm": "Paytm", "phonepe": "PhonePe",
        "google pay": "Google Pay", "gpay": "Google Pay"}
THREAT = ["account will be blocked", "account will be suspended", "legal action",
          "police complaint", "arrest", "penalty", "fine", "disconnect",
          "service will stop", "account blocked"]
# Hindi (hi) and Kannada (kn) keywords
URGENCY += ["तुरंत", "जल्द से जल्द", "आज ही", "अंतिम मौका", "खाता बंद", "खाता ब्लॉक",
            "ತುರ್ತು", "ತುರ್ತಾಗಿ", "ತಕ್ಷಣ", "ಇಂದೇ", "ಕೊನೆಯ ಅವಕಾಶ", "ಖಾತೆ ಬ್ಲಾಕ್", "ಖಾತೆ ಸ್ಥಗಿತ"]
PAYMENT += ["भुगतान", "पैसे भेजें", "रुपये", "शुल्क", "ट्रांसफर", "जमा करें",
            "ಪಾವತಿ", "ಹಣ ಕಳುಹಿಸಿ", "ರೂಪಾಯಿ", "ಶುಲ್ಕ", "ವರ್ಗಾವಣೆ", "ಠೇವಣಿ"]
CREDENTIAL += ["ओटीपी", "यूपीआई पिन", "पिन नंबर", "सीवीवी", "पासवर्ड", "सत्यापन कोड",
               "ಒಟಿಪಿ", "ಪಿನ್", "ಸಿವಿವಿ", "ಪಾಸ್‌ವರ್ಡ್", "ಪಾಸ್ವರ್ಡ್"]
ORGS.update({"एसबीआई": "SBI", "आरबीआई": "RBI", "पुलिस": "Police", "आयकर": "Income Tax Dept",
             "ಎಸ್‌ಬಿಐ": "SBI", "ಎಸ್ಬಿಐ": "SBI", "ಆರ್‌ಬಿಐ": "RBI", "ಪೊಲೀಸ್": "Police", "ಆದಾಯ ತೆರಿಗೆ": "Income Tax Dept"})
THREAT += ["गिरफ्तार", "कानूनी कार्रवाई", "जुर्माना", "खाता बंद", "कनेक्शन कट",
           "ಬಂಧನ", "ಕಾನೂನು ಕ್ರಮ", "ದಂಡ", "ಖಾತೆ ಬ್ಲಾಕ್", "ಖಾತೆ ಸ್ಥಗಿತ"]
URL_RE = re.compile(r"https?://[^\s]+|www\.[^\s]+", re.I)


def _found(text, patterns):
    """Return patterns present as whole words/phrases (so 'pin' won't match 'shopping')."""
    text = text.lower()
    # Devanagari/Kannada words carry combining marks that break \w boundaries, so match them as substrings.
    return [p for p in patterns
            if (p in text if not p.isascii() else re.search(r"(?<!\w)" + re.escape(p) + r"(?!\w)", text))]


def detect_urgency(text): return bool(_found(text, URGENCY))
def detect_payment_request(text): return bool(_found(text, PAYMENT))
def detect_otp_request(text): return bool(_found(text, CREDENTIAL))
def detect_impersonation(text): return bool(_found(text, list(ORGS)))
def detect_threat(text): return bool(_found(text, THREAT))
def detect_suspicious_link(text): return bool(URL_RE.search(text))


def find_organisations(text):
    return list(dict.fromkeys(ORGS[o] for o in _found(text, list(ORGS))))


def matched_terms(text):
    """Every phrase that triggered a rule, longest first (used to highlight the message)."""
    terms = set()
    for group in (URGENCY, CREDENTIAL, list(ORGS), THREAT, ["\u20b9", "processing fee", "verification fee"]):
        terms.update(_found(text, group))
    terms.update(m.group(0) for m in URL_RE.finditer(text))
    return sorted(terms, key=len, reverse=True)
