from engine.risk_engine import analyze_text
from engine.upi_analyzer import analyze_upi


def test_high_risk_message():
    text = "URGENT! Your SBI account will be blocked today. Pay ₹2 immediately and share your OTP."
    result = analyze_text(text)
    assert result["score"] >= 60
    assert result["level"] in ["HIGH", "CRITICAL"]


def test_upi_extraction():
    result = analyze_upi("Please pay ₹2 to support123@xyz")
    assert "support123@xyz" in result["upi_ids"]
    assert "₹2" in result["amounts"]


def test_email_is_not_upi():
    assert analyze_upi("mail me at ravi@gmail.com")["upi_ids"] == []


def test_org_plus_upi_is_flagged():
    text = "Your SBI account is blocked. Send ₹2 to support123@xyz"
    pay = analyze_upi(text)
    assert pay["claimed_entities"] == ["SBI"] and pay["analysis"]
    names = [s["name"] for s in analyze_text(text, pay)["signals"]]
    assert "Organisation asks for UPI payment" in names


def test_whole_word_matching():
    # 'pin' inside 'shopping' and 'fine' inside 'define' must not trigger rules
    assert analyze_text("Let's go shopping and define the plan")["score"] == 0


def test_legitimate_bill_is_low():
    text = ("Your electricity bill of ₹1,240 is due on 30 September. Please use the official "
            "electricity provider application or website to make your payment.")
    assert analyze_text(text, analyze_upi(text))["level"] == "LOW"
