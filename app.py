import html
import re
from datetime import datetime
from pathlib import Path

import requests
import streamlit as st

from engine.risk_engine import analyze_text
from engine.upi_analyzer import analyze_upi
from engine.ocr import extract_text_from_image
import engine.ocr as ocr_module
from engine.llm import analyze_with_llm
from engine.conversation import analyze_conversation
from engine.i18n import tr, DEMOS, LANG_NAMES

st.set_page_config(page_title="RakshaNet AI", page_icon="\U0001F6E1\uFE0F", layout="wide",
                   initial_sidebar_state="collapsed")

LOGO = (Path(__file__).parent / "assets" / "logo.svg").read_text(encoding="utf-8")
COLORS = {"CRITICAL": "#FB4B6B", "HIGH": "#FB923C", "MEDIUM": "#FBBF24", "LOW": "#34D399"}
LANGS = {"en": "English", "kn": "\u0c95\u0ca8\u0ccd\u0ca8\u0ca1", "hi": "\u0939\u093f\u0928\u094d\u0926\u0940"}
lang = "en"  # set from the language switch below, before anything renders


def t(key, **kw):
    return tr(lang, key, **kw)


def lvl(level):
    return t("lvl_" + level) if level in COLORS else t("lvl_UNKNOWN")


CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@500;600;700;800&family=Manrope:wght@400;500;600;700&family=JetBrains+Mono:wght@500&family=Noto+Sans+Devanagari:wght@400;600;700&family=Noto+Sans+Kannada:wght@400;600;700&display=swap');
:root{--bg:#070B1C;--panel:rgba(255,255,255,.045);--line:rgba(148,163,255,.17);--text:#E8ECFF;--mut:#97A0C4;--teal:#5EEAD4;--ind:#818CF8;--vio:#C084FC}
html,body,.stApp,[class*="css"]{font-family:'Manrope','Noto Sans Devanagari','Noto Sans Kannada',system-ui,sans-serif}
.stApp{color:var(--text);background:radial-gradient(1100px 560px at 10% -8%,rgba(94,234,212,.14),transparent 60%),radial-gradient(900px 600px at 98% 2%,rgba(192,132,252,.16),transparent 60%),linear-gradient(rgba(129,140,248,.045) 1px,transparent 1px) 0 0/44px 44px,linear-gradient(90deg,rgba(129,140,248,.045) 1px,transparent 1px) 0 0/44px 44px,var(--bg)}
[data-testid="stHeader"]{background:transparent}#MainMenu,footer,[data-testid="stToolbar"]{visibility:hidden}
.block-container{max-width:1120px;padding-top:1.6rem;padding-bottom:3rem}
h1,h2,h3,h4{font-family:'Sora','Noto Sans Devanagari','Noto Sans Kannada',sans-serif!important;color:var(--text)!important;letter-spacing:-.01em}
p,label,span,li{color:inherit}
.hero{display:flex;align-items:center;gap:22px;padding:26px 30px;border:1px solid var(--line);border-radius:26px;background:linear-gradient(135deg,rgba(94,234,212,.08),rgba(129,140,248,.07) 45%,rgba(192,132,252,.10));backdrop-filter:blur(14px);position:relative;overflow:hidden;margin-bottom:22px}
.hero:after{content:"";position:absolute;inset:0;background:linear-gradient(105deg,transparent 40%,rgba(94,234,212,.16) 50%,transparent 60%);transform:translateX(-120%);animation:scan 5.5s ease-in-out .6s 1 forwards;pointer-events:none}
@keyframes scan{to{transform:translateX(120%)}}
.hero .logo{width:92px;height:92px;flex:none;filter:drop-shadow(0 0 22px rgba(129,140,248,.55))}
.hero h1{font-size:44px;font-weight:800;margin:0;line-height:1.05;background:linear-gradient(90deg,#fff,#C7D2FE 60%,#5EEAD4);-webkit-background-clip:text;background-clip:text;color:transparent!important}
.hero h1 small{font-size:.5em;font-weight:700;margin-left:8px;color:var(--teal);-webkit-text-fill-color:var(--teal)}
.hero p{margin:8px 0 14px;color:var(--mut);font-size:17px;max-width:640px}
.chips{display:flex;gap:8px;flex-wrap:wrap}
.pill{display:inline-flex;align-items:center;gap:8px;padding:6px 13px;border-radius:999px;border:1px solid var(--line);background:rgba(8,12,34,.55);font-size:13px;color:var(--mut)}
.dot{width:8px;height:8px;border-radius:50%;background:#34D399;box-shadow:0 0 10px #34D399;animation:pulse 2s infinite}.dot.off{background:#FBBF24;box-shadow:0 0 10px #FBBF24;animation:none}
@keyframes pulse{50%{opacity:.35}}
.stTabs [data-baseweb="tab-list"]{gap:6px;background:var(--panel);padding:6px;border-radius:16px;border:1px solid var(--line);width:fit-content;max-width:100%;overflow-x:auto}
.stTabs [data-baseweb="tab"]{height:42px;padding:0 20px;border-radius:11px;color:var(--mut);font-weight:600;background:transparent}
.stTabs [aria-selected="true"]{background:linear-gradient(135deg,rgba(94,234,212,.20),rgba(129,140,248,.28));color:#fff!important;box-shadow:inset 0 0 0 1px rgba(129,140,248,.45)}
.stTabs [data-baseweb="tab-highlight"],.stTabs [data-baseweb="tab-border"]{display:none}
.stTextArea textarea{background:rgba(9,14,40,.75)!important;border:1px solid var(--line)!important;color:var(--text)!important;border-radius:16px!important;font-size:15.5px;line-height:1.6}
.stTextArea textarea:focus{border-color:var(--teal)!important;box-shadow:0 0 0 3px rgba(94,234,212,.15)!important}
.stTextArea label p,.stSelectbox label p,.stFileUploader label p{color:var(--mut)!important;font-weight:600}
[data-baseweb="select"]>div{background:rgba(9,14,40,.75)!important;border:1px solid var(--line)!important;border-radius:12px!important;color:var(--text)!important}
[data-testid="stFileUploaderDropzone"]{background:rgba(9,14,40,.6);border:1.5px dashed rgba(94,234,212,.4);border-radius:18px}
.stButton>button[kind="primary"],[data-testid="stBaseButton-primary"]{background:linear-gradient(135deg,#2DD4BF,#6366F1 60%,#A855F7)!important;color:#fff!important;border:0!important;border-radius:14px!important;height:52px;font-family:'Sora','Noto Sans Devanagari','Noto Sans Kannada',sans-serif;font-weight:700;font-size:16px;box-shadow:0 10px 30px -8px rgba(99,102,241,.7);transition:transform .15s,box-shadow .15s}
.stButton>button[kind="primary"]:hover,[data-testid="stBaseButton-primary"]:hover{transform:translateY(-2px);box-shadow:0 16px 36px -8px rgba(99,102,241,.9)}
.stDownloadButton button,[data-testid="stBaseButton-secondary"]{background:var(--panel)!important;border:1px solid var(--line)!important;color:var(--text)!important;border-radius:12px!important}
[data-testid="stExpander"]{border:1px solid var(--line)!important;border-radius:16px!important;background:var(--panel)}
[data-testid="stExpander"] summary{color:var(--text)}
.card{border:1px solid var(--line);border-radius:22px;padding:22px 24px;background:var(--panel);backdrop-filter:blur(10px);margin-bottom:16px;height:calc(100% - 16px)}
.card h4{margin:0 0 14px;font-size:17px;font-weight:700}
.muted{color:var(--mut)}
.gauge{position:relative;width:210px;height:210px;margin:0 auto}
.gauge svg{width:100%;height:100%;overflow:visible}
.g-track{fill:none;stroke:rgba(148,163,255,.14);stroke-width:11}
.g-arc{fill:none;stroke-width:11;stroke-linecap:round;stroke-dasharray:var(--circ);stroke-dashoffset:var(--off);transform:rotate(-90deg);transform-origin:70px 70px;filter:drop-shadow(0 0 7px var(--c));animation:sweep 1.5s cubic-bezier(.2,.8,.2,1)}
@keyframes sweep{from{stroke-dashoffset:var(--circ)}}
.g-num{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center}
.g-num b{font-family:'Sora','Noto Sans Devanagari','Noto Sans Kannada',sans-serif;font-size:58px;line-height:1;font-weight:800}.g-num span{font-size:13px;color:var(--mut);margin-top:4px}
.verdict{font-family:'Sora','Noto Sans Devanagari','Noto Sans Kannada',sans-serif;font-size:30px;font-weight:800;margin:2px 0 6px}
.tiles{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-top:16px}
.tile{padding:13px 15px;border-radius:14px;background:rgba(9,14,40,.6);border:1px solid var(--line)}
.tile span{display:block;font-size:12.5px;color:var(--mut);margin-bottom:4px}.tile b{font-family:'Sora','Noto Sans Devanagari','Noto Sans Kannada',sans-serif;font-size:16px}
.sig{margin-bottom:14px}.sig-top{display:flex;align-items:center;gap:10px;font-weight:600;font-size:14.5px;margin-bottom:6px}.sig-top i{margin-left:auto;font-style:normal;color:var(--mut);font-family:'JetBrains Mono',monospace;font-size:13px}
.chip{font-style:normal;font-size:11.5px;padding:2px 9px;border-radius:999px;font-weight:700}
.chip.HIGH{background:rgba(251,146,60,.16);color:#FDBA74}.chip.CRITICAL{background:rgba(251,75,107,.18);color:#FDA4AF}
.bar{height:7px;border-radius:9px;background:rgba(148,163,255,.12);overflow:hidden}.bar span{display:block;height:100%;border-radius:9px}
.tag{display:inline-block;padding:7px 14px;margin:0 8px 8px 0;border-radius:999px;background:rgba(129,140,248,.14);border:1px solid rgba(129,140,248,.35);font-size:14px}
.ev{display:flex;gap:12px;padding:12px 14px;border-radius:12px;background:rgba(9,14,40,.55);border:1px solid var(--line);margin-bottom:9px;font-size:14.5px}
.ev:before{content:"";flex:none;width:3px;border-radius:3px;background:linear-gradient(var(--teal),var(--vio))}
.upi{font-family:'JetBrains Mono',monospace;background:rgba(94,234,212,.09);border:1px solid rgba(94,234,212,.3);color:var(--teal);padding:5px 11px;border-radius:9px;display:inline-block;margin:3px 6px 3px 0;font-size:14px}
.kv{margin-bottom:14px}.kv>span{display:block;font-size:12.5px;color:var(--mut);margin-bottom:5px}
.note{padding:12px 15px;border-radius:12px;background:rgba(251,191,36,.09);border:1px solid rgba(251,191,36,.3);color:#FDE68A;font-size:14px;margin-top:8px}
.note.info{background:rgba(129,140,248,.10);border-color:rgba(129,140,248,.35);color:#C7D2FE}
.action{padding:20px 24px;border-radius:20px;background:linear-gradient(135deg,rgba(52,211,153,.13),rgba(94,234,212,.06));border:1px solid rgba(52,211,153,.4);font-size:16px;line-height:1.6}
.action b{font-family:'Sora','Noto Sans Devanagari','Noto Sans Kannada',sans-serif;display:block;margin-bottom:6px;color:#6EE7B7}
.msgtext{line-height:1.75;font-size:15px}.msgtext mark{background:rgba(251,75,107,.22);color:#FFD1DA;border-bottom:2px solid #FB4B6B;padding:1px 4px;border-radius:4px}
.bubble{max-width:82%;padding:11px 15px;border-radius:16px 16px 16px 4px;background:rgba(129,140,248,.16);border:1px solid var(--line);margin-bottom:8px;font-size:14.5px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:14px;margin-bottom:16px}
.grid .card{margin:0;height:auto}.grid .card b{display:block;font-family:'Sora','Noto Sans Devanagari','Noto Sans Kannada',sans-serif;margin-bottom:6px}.grid .card p{margin:0;color:var(--mut);font-size:14.5px;line-height:1.55}
.help{display:flex;align-items:center;gap:16px;padding:16px 20px;border-radius:18px;border:1px solid rgba(251,75,107,.4);background:rgba(251,75,107,.08);margin-bottom:12px}
.help .n{font-family:'Sora','Noto Sans Devanagari','Noto Sans Kannada',sans-serif;font-size:38px;font-weight:800;color:#FDA4AF}
.hist{display:flex;align-items:center;gap:12px;padding:10px 14px;border-bottom:1px solid var(--line);font-size:14px}.hist:last-child{border:0}.hist i{margin-left:auto;font-style:normal;color:var(--mut);font-size:12.5px}
.footer{text-align:center;color:var(--mut);opacity:.75;font-size:13px;margin-top:36px}
@media (max-width:760px){.hero{flex-direction:column;align-items:flex-start;padding:22px}.hero h1{font-size:34px}.tiles{grid-template-columns:1fr}}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
.st-key-lang{display:flex;justify-content:flex-end}[data-testid="stRadio"] label p{color:var(--text)}
</style>
"""


def show(markup):
    """Render HTML (newlines collapsed so Markdown never treats indented tags as code)."""
    st.markdown(re.sub(r"\n\s*", "", markup), unsafe_allow_html=True)


def esc(value):
    return html.escape(str(value)).replace("\n", "<br>")


@st.cache_data(ttl=20)
def ollama_online():
    try:
        return requests.get("http://localhost:11434/api/tags", timeout=1).ok
    except Exception:
        return False


@st.cache_data(ttl=60)
def ocr_ready():
    try:
        ocr_module.pytesseract.get_tesseract_version()
        return True
    except Exception:
        return False


def status_pill(label, ok):
    return f'<span class="pill"><i class="dot {"" if ok else "off"}"></i>{label}</span>'


def hero():
    ai, ocr = ollama_online(), ocr_ready()
    show(f"""<div class="hero"><div class="logo">{LOGO}</div><div><h1>RakshaNet<small>AI</small></h1>
    <p>{t("tagline")}</p>
    <div class="chips">{status_pill(t("rules_ready"), True)}{status_pill(t("ai_on") if ai else t("ai_off"), ai)}
    {status_pill(t("ocr_on") if ocr else t("ocr_off"), ocr)}<span class="pill">{t("private")}</span></div></div></div>""")


def gauge(score, level):
    color, circ = COLORS.get(level, "#94A3B8"), 339.3
    off = circ * (1 - min(max(score, 0), 100) / 100)
    return (f'<div class="gauge"><svg viewBox="0 0 140 140"><circle class="g-track" cx="70" cy="70" r="54"/>'
            f'<circle class="g-arc" cx="70" cy="70" r="54" style="stroke:{color};--c:{color};--circ:{circ};--off:{off:.1f}"/></svg>'
            f'<div class="g-num"><b style="color:{color}">{score}</b><span>{t("risk_score")}</span></div></div>')


def verdict_panel(score, level, tiles, blurb=None):
    title, text = t("v_" + level if level in COLORS else "v_UNKNOWN")
    color = COLORS.get(level, "#94A3B8")
    tiles_html = "".join(f'<div class="tile"><span>{esc(k)}</span><b>{esc(v)}</b></div>' for k, v in tiles)
    extra = f'<p style="margin-top:16px">{esc(blurb)}</p>' if blurb else ""
    left, right = st.columns([1, 1.7])
    with left:
        show(f'<div class="card" style="text-align:center">{gauge(score, level)}<div class="verdict" style="color:{color};margin-top:10px">{lvl(level)}</div></div>')
    with right:
        show(f'<div class="card"><div class="verdict">{title}</div><div class="muted" style="font-size:16px">{text}</div>'
             f'<div class="tiles">{tiles_html}</div>{extra}</div>')


def tags_html(items):
    return "".join(f'<span class="tag">{esc(i)}</span>' for i in items) or f'<span class="muted">{t("no_tactics")}</span>'


def evidence_html(items):
    return "".join(f'<div class="ev">{esc(i)}</div>' for i in items) or f'<span class="muted">{t("no_evidence")}</span>'


def highlight(text, terms):
    safe = html.escape(text)
    if terms:
        pattern = re.compile("|".join(re.escape(html.escape(x)) for x in terms), re.I)
        safe = pattern.sub(lambda m: f"<mark>{m.group(0)}</mark>", safe)
    return safe.replace("\n", "<br>")


def record(kind, score, level, snippet):
    st.session_state.setdefault("history", []).insert(
        0, {"kind": kind, "score": score, "level": level, "text": snippet[:70], "time": datetime.now().strftime("%H:%M")})


def report(kind, score, level, ai, text):
    lines = [t("rep_title", k=kind), f"{t('rep_gen')}: {datetime.now():%d %b %Y, %H:%M}", "",
             f"{t('rep_risk')}: {score}/100 ({lvl(level)})", f"{t('rep_cat')}: {ai.get('scam_category', '-')}", "",
             f"{t('rep_tactics')}: " + (", ".join(ai.get("tactics", [])) or t("rep_none")), "", f"{t('rep_ev')}:"]
    lines += [f"- {e}" for e in ai.get("evidence", [])] + ["", f"{t('rep_reco')}: {ai.get('recommendation', '')}", "",
                                                            f"{t('rep_text')}:", text]
    return "\n".join(lines)


def show_result(text):
    if not text or not text.strip():
        show(f'<div class="note">{t("empty_msg")}</div>')
        return
    payment = analyze_upi(text)
    result = analyze_text(text, payment)
    ai = analyze_with_llm(text, result, payment, LANG_NAMES[lang])
    score, level = result["score"], result["level"]
    record("msg", score, level, text)
    if ai.get("error"):
        ai.update(summary=t("ai_offline_summary"), recommendation=t("fallback_reco"), scam_category=t("ai_unavailable"))
        show(f'<div class="note">{t("ai_offline_note")}</div>')
    verdict_panel(score, level, [(t("rule_engine"), lvl(level)), (t("ai_verdict"), lvl(str(ai.get("classification", level)).upper())),
                                 (t("scam_type"), ai.get("scam_category", "-"))], ai.get("summary"))
    c1, c2 = st.columns(2)
    with c1:
        rows = "".join(
            f'<div class="sig"><div class="sig-top">{esc(t("sig:" + s["name"]))}<em class="chip {s["severity"]}">{lvl(s["severity"])}</em><i>+{s["points"]}</i></div>'
            f'<div class="bar"><span style="width:{s["points"] / 25 * 100:.0f}%;background:{COLORS.get(s["severity"], "#FB923C")}"></span></div></div>'
            for s in result["signals"]) or f'<span class="muted">{t("no_signals")}</span>'
        show(f'<div class="card"><h4>{t("h_signals")}</h4>{rows}</div>')
    with c2:
        none = f'<span class="muted">{t("none")}</span>'
        org = ", ".join(payment["claimed_entities"]) or t("none")
        upis = "".join(f'<span class="upi">{esc(u)}</span>' for u in payment["upi_ids"]) or none
        amts = "".join(f'<span class="upi">{esc(a)}</span>' for a in payment["amounts"]) or none
        notes = "".join(f'<div class="note info">{esc(t("pay_" + a["code"] if a["code"] != "small" else "pay_small", **{k: v for k, v in a.items() if k != "code"}))}</div>'
                        for a in payment["analysis"])
        show(f'<div class="card"><h4>{t("h_payment")}</h4><div class="kv"><span>{t("claimed_org")}</span>{esc(org)}</div>'
             f'<div class="kv"><span>{t("upi_id")}</span>{upis}</div><div class="kv"><span>{t("amount_req")}</span>{amts}</div>{notes}</div>')
    c3, c4 = st.columns(2)
    with c3:
        show(f'<div class="card"><h4>{t("h_tactics")}</h4>{tags_html(ai.get("tactics", []))}</div>')
    with c4:
        show(f'<div class="card"><h4>{t("h_flagged")}</h4>{evidence_html(ai.get("evidence", []))}</div>')
    if ai.get("recommendation"):
        show(f'<div class="action"><b>{t("what_now")}</b>{esc(ai["recommendation"])}</div>')
    with st.expander(t("exp_highlight")):
        show(f'<div class="msgtext">{highlight(text, result["matches"])}</div>')
    st.download_button(t("download"), report(t("tab_msg"), score, level, ai, text), "rakshanet_report.txt")


def show_conversation(messages):
    cr = analyze_conversation(messages, LANG_NAMES[lang])
    score, cls = int(cr.get("risk_score", 0) or 0), str(cr.get("classification", "UNKNOWN")).upper()
    record("chat", score, cls, messages[0])
    if cr.get("error"):
        cr.update(conversation_pattern=None, recommendation=t("chat_fallback_reco"), scam_category=t("ai_unavailable"))
        show(f'<div class="note">{t("ai_offline_chat")}</div>')
    verdict_panel(score, cls, [(t("risk_score_t"), f"{score}/100"), (t("class_t"), lvl(cls)), (t("scam_type"), cr.get("scam_category", "-"))],
                  cr.get("conversation_pattern"))
    c1, c2 = st.columns(2)
    with c1:
        show(f'<div class="card"><h4>{t("h_tactics")}</h4>{tags_html(cr.get("tactics", []))}</div>')
    with c2:
        show(f'<div class="card"><h4>{t("h_evidence")}</h4>{evidence_html(cr.get("evidence", []))}</div>')
    if cr.get("recommendation"):
        show(f'<div class="action"><b>{t("what_now")}</b>{esc(cr["recommendation"])}</div>')
    with st.expander(t("exp_chat")):
        show("".join(f'<div class="bubble">{esc(m)}</div>' for m in messages))
    st.download_button(t("download"), report(t("tab_chat"), score, cls, cr, "\n\n".join(messages)), "rakshanet_conversation_report.txt")


def load_demo():
    samples = DEMOS.get(st.session_state.get("lang", "en"), DEMOS["en"])
    pick = st.session_state.get("sample_id")
    if pick in samples:  # ignore stale or placeholder values
        st.session_state.msg_text = samples[pick][1]


def safety_hub():
    rules = "".join(f'<div class="card"><b>{esc(a)}</b><p>{esc(b)}</p></div>' for a, b in t("rules"))
    scams = "".join(f'<div class="card"><b>{esc(a)}</b><p>{esc(b)}</p></div>' for a, b in t("scams"))
    show(f"""<div class="help"><div class="n">1930</div><div><b>{t("hub_help_title")}</b><br>
    <span class="muted">{t("hub_help_text")}</span></div></div>
    <h3 style="margin:22px 0 12px">{t("hub_rules_title")}</h3><div class="grid">{rules}</div>
    <h3 style="margin:22px 0 12px">{t("hub_scams_title")}</h3><div class="grid">{scams}</div>""")
    rows = "".join(f'<div class="hist"><span class="chip" style="background:{COLORS.get(h["level"], "#64748B")}33;color:{COLORS.get(h["level"], "#CBD5E1")}">{esc(lvl(h["level"]))} {h["score"]}</span>'
                   f'{esc(t("tab_msg") if h["kind"] == "msg" else t("tab_chat"))}: {esc(h["text"])}<i>{h["time"]}</i></div>'
                   for h in st.session_state.get("history", [])[:8])
    empty = f'<span class="muted">{t("hub_none")}</span>'
    show(f'<h3 style="margin:22px 0 12px">{t("hub_hist_title")}</h3><div class="card">{rows or empty}</div>')


show(CSS)
_, lang_col = st.columns([3, 1.6])
with lang_col:
    st.radio("Language", list(LANGS), format_func=LANGS.get, horizontal=True, key="lang", label_visibility="collapsed")
lang = st.session_state.lang
hero()
tab_msg, tab_img, tab_chat, tab_hub = st.tabs([t("tab_msg"), t("tab_img"), t("tab_chat"), t("tab_hub")])

with tab_msg:
    st.selectbox(t("try_sample"), [""] + list(DEMOS[lang]), key="sample_id", on_change=load_demo,
                 format_func=lambda k: t("sample_ph") if not k else DEMOS[lang][k][0])
    text = st.text_area(t("msg_label"), height=210, key="msg_text", placeholder=t("msg_ph"))
    if st.button(t("btn_msg"), type="primary", use_container_width=True, key="go_msg"):
        with st.spinner(t("spin_msg")):
            show_result(text)

with tab_img:
    uploaded = st.file_uploader(t("up_shot"), type=["png", "jpg", "jpeg", "webp"])
    if uploaded:
        st.image(uploaded, use_container_width=True)
        if st.button(t("btn_shot"), type="primary", use_container_width=True, key="go_img"):
            with st.spinner(t("spin_ocr")):
                extracted = extract_text_from_image(uploaded)
            if extracted.startswith("OCR_ERROR"):
                show(f'<div class="note">{esc(t("ocr_fail", d=extracted))}</div>')
            elif not extracted:
                show(f'<div class="note">{t("ocr_none")}</div>')
            else:
                show_result(extracted)

with tab_chat:
    mode = st.radio(t("chat_mode_q"), ["up", "paste"], format_func=lambda m: t("mode_" + m), horizontal=True, key="chat_input_mode")
    msgs = []
    if mode == "up":
        st.caption(t("cap_up"))
        shots = (st.file_uploader(t("chat_shots"), type=["png", "jpg", "jpeg", "webp"],
                                  accept_multiple_files=True, key="chat_shots") or [])[:6]
        if shots:
            for i, (col, f) in enumerate(zip(st.columns(len(shots)), shots), 1):
                with col:
                    st.image(f, caption=t("shot_n", n=i), use_container_width=True)
        if st.button(t("btn_chat"), type="primary", use_container_width=True, key="go_chat_img"):
            if not shots:
                show(f'<div class="note">{t("need_shot")}</div>')
            else:
                with st.spinner(t("spin_ocr")):
                    texts = [extract_text_from_image(f) for f in shots]
                failed = [i for i, x in enumerate(texts, 1) if not x or x.startswith("OCR_ERROR")]
                msgs = [x for x in texts if x and not x.startswith("OCR_ERROR")]
                for n in failed:
                    show(f'<div class="note">{t("shot_unread", n=n)}</div>')
                if msgs:
                    with st.spinner(t("spin_chat")):
                        show_conversation(msgs)
    else:
        st.caption(t("cap_paste"))
        cols = st.columns(2)
        for i in range(6):
            with cols[i % 2]:
                m = st.text_area(t("message_n", n=i + 1), height=110, key=f"conversation_message_{i}", placeholder=t("msg_paste_ph"))
            if m.strip():
                msgs.append(m.strip())
        if st.button(t("btn_chat"), type="primary", use_container_width=True, key="go_chat"):
            if len(msgs) < 2:
                show(f'<div class="note">{t("need_two")}</div>')
            else:
                with st.spinner(t("spin_chat")):
                    show_conversation(msgs)

with tab_hub:
    safety_hub()

show(f'<div class="footer">{t("footer")}</div>')
