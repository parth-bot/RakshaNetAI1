from engine.rules import (
    detect_urgency, detect_payment_request, detect_otp_request,
    detect_impersonation, detect_threat, detect_suspicious_link, matched_terms,
)


def analyze_text(text, payment=None):
    payment = payment or {}
    signals, score = [], 0
    checks = [
        (detect_urgency(text), "Urgency", "HIGH", 15),
        (detect_payment_request(text), "Payment request", "HIGH", 20),
        (detect_otp_request(text), "OTP/PIN request", "CRITICAL", 25),
        (detect_impersonation(text), "Possible impersonation", "HIGH", 20),
        (detect_threat(text), "Threat/intimidation", "HIGH", 15),
        (detect_suspicious_link(text), "Suspicious link", "HIGH", 15),
        (bool(payment.get("claimed_entities") and payment.get("upi_ids")),
         "Organisation asks for UPI payment", "HIGH", 15),
    ]
    for hit, name, severity, points in checks:
        if hit:
            signals.append({"name": name, "severity": severity, "points": points})
            score += points
    score = min(score, 100)
    level = "CRITICAL" if score >= 80 else "HIGH" if score >= 60 else "MEDIUM" if score >= 30 else "LOW"
    return {"score": score, "level": level, "signals": signals, "matches": matched_terms(text)}
