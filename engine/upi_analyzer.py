import re
from engine.rules import find_organisations


def extract_upi_ids(text):
    # UPI handles have no dot in the provider part, which filters out plain email addresses.
    found = re.findall(r'\b[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\b', text)
    return list(dict.fromkeys(f for f in found if "." not in f.split("@")[1]))


def extract_amounts(text):
    patterns = [r'\u20b9\s?[\d,]+(?:\.\d+)?', r'Rs\.?\s?[\d,]+(?:\.\d+)?', r'INR\s?[\d,]+(?:\.\d+)?']
    amounts = []
    for pattern in patterns:
        amounts.extend(re.findall(pattern, text))
    return list(dict.fromkeys(amounts))


def analyze_upi(text):
    upis, amounts, claimed = extract_upi_ids(text), extract_amounts(text), find_organisations(text)
    analysis = []
    if claimed and upis:
        analysis.append({"code": "org_upi", "orgs": ", ".join(claimed), "ids": ", ".join(upis)})
    elif upis:
        analysis.append({"code": "upi_only"})
    if claimed and any(float(re.sub(r"[^\d.]", "", a) or 0) <= 10 for a in amounts):
        analysis.append({"code": "small"})
    return {"upi_ids": upis, "amounts": amounts, "claimed_entities": claimed, "analysis": analysis}
