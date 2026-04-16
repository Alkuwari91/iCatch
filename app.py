import streamlit as st
import requests
import json
import pandas as pd
from curriculum import get_lessons_by_module, get_all_lessons
from rag import build_corpus, embed_corpus, retrieve, build_context

st.set_page_config(
    page_title="iCatch | لحق",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;700;900&family=DM+Serif+Display&family=Inter:wght@300;400;500;600;700&display=swap');

:root {
    --bg:           #F5F2EE;
    --bg-card:      #FFFFFF;
    --bg-deep:      #EDE8E1;
    --bg-subtle:    #FAF8F5;
    --border:       #E0D9CF;
    --border-light: #EDE8E1;
    --text:         #1C1410;
    --text-secondary: #6B5D52;
    --maroon:       #8D1B3D;
    --maroon-dk:    #6B1530;
    --maroon-light: #F9EEF2;
    --terra:        #C4623A;
    --terra-light:  #FEF4EF;
    --success:      #1A7A4A;
    --success-bg:   #EDFBF3;
    --success-border:#A3D9BC;
    --warn-bg:      #FFFBEB;
    --warn-border:  #FCD34D;
    --warn-text:    #92400E;
    --shadow-sm:    0 1px 3px rgba(28,20,16,0.08), 0 1px 2px rgba(28,20,16,0.04);
    --shadow-md:    0 4px 12px rgba(28,20,16,0.10), 0 2px 6px rgba(28,20,16,0.06);
    --shadow-lg:    0 10px 30px rgba(28,20,16,0.12), 0 4px 12px rgba(28,20,16,0.08);
    --radius-sm:    8px;
    --radius-md:    12px;
    --radius-lg:    16px;
    --radius-xl:    20px;
}

html, body, [class*="css"] {
    font-family: 'Inter', 'Tajawal', sans-serif;
    color: var(--text);
}

/* ── Base ── */
.stApp, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
}
[data-testid="stHeader"] { background: transparent !important; }
[data-testid="collapsedControl"], section[data-testid="stSidebar"] { display: none !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg-deep); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--text-secondary); }

/* ── Hero ── */
.hero {
    background: linear-gradient(135deg, #8D1B3D 0%, #6B1530 50%, #4A0F22 100%);
    color: white;
    padding: 32px 44px;
    border-radius: var(--radius-xl);
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    gap: 24px;
    box-shadow: var(--shadow-lg), inset 0 1px 0 rgba(255,255,255,0.1);
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute;
    top: -40px; right: -40px;
    width: 200px; height: 200px;
    background: rgba(255,255,255,0.04);
    border-radius: 50%;
}
.hero::after {
    content: '';
    position: absolute;
    bottom: -60px; right: 120px;
    width: 160px; height: 160px;
    background: rgba(255,255,255,0.03);
    border-radius: 50%;
}
.hero-icon {
    font-size: 3rem;
    line-height: 1;
    background: rgba(255,255,255,0.12);
    border-radius: var(--radius-lg);
    padding: 14px;
    backdrop-filter: blur(4px);
    flex-shrink: 0;
}
.hero h1 {
    margin: 0;
    font-family: 'DM Serif Display', serif;
    font-size: 2.1rem;
    font-weight: 400;
    letter-spacing: -0.5px;
    line-height: 1.1;
}
.hero .tagline {
    font-family: 'Tajawal', sans-serif;
    font-size: 1rem;
    font-weight: 700;
    opacity: 0.75;
    margin: 6px 0 0 0;
    letter-spacing: 0.3px;
}
.hero-badge {
    margin-left: auto;
    background: rgba(255,255,255,0.12);
    border: 1px solid rgba(255,255,255,0.18);
    border-radius: var(--radius-md);
    padding: 8px 18px;
    font-size: 0.8rem;
    font-weight: 600;
    letter-spacing: 0.5px;
    backdrop-filter: blur(4px);
    flex-shrink: 0;
}

/* ── Nav Toggle ── */
.nav-wrap {
    display: flex;
    gap: 0;
    margin-bottom: 28px;
    background: var(--bg-deep);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 4px;
    width: fit-content;
}

/* ── Cards ── */
.card {
    background: var(--bg-card);
    border: 1px solid var(--border-light);
    border-radius: var(--radius-md);
    padding: 22px 26px;
    margin: 10px 0;
    line-height: 1.7;
    font-size: 0.94rem;
    color: var(--text);
    box-shadow: var(--shadow-sm);
}
.card-accent {
    border-left: 4px solid var(--maroon);
}
.card-title {
    font-size: 0.85rem;
    font-weight: 700;
    color: var(--maroon);
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 6px;
}

/* ── NSIS Panel ── */
.nsis-panel {
    background: var(--bg-card);
    border: 1px solid var(--border-light);
    border-radius: var(--radius-md);
    padding: 20px 24px;
    margin: 14px 0;
    box-shadow: var(--shadow-sm);
}
.nsis-label {
    font-size: 0.72rem;
    font-weight: 700;
    color: var(--text-secondary);
    letter-spacing: 1.2px;
    text-transform: uppercase;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 6px;
}
.nsis-label::before {
    content: '';
    width: 3px; height: 12px;
    background: var(--maroon);
    border-radius: 2px;
    display: inline-block;
}
.nsis-name {
    font-size: 1.1rem;
    font-weight: 700;
    margin-bottom: 10px;
    color: var(--text);
}
.nsis-avg {
    font-size: 0.88rem;
    color: var(--text-secondary);
    margin-bottom: 6px;
}
.scores-row {
    display: flex;
    gap: 6px;
    margin-top: 8px;
}
.score-pill {
    background: var(--bg-deep);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 3px 10px;
    font-size: 0.78rem;
    font-weight: 600;
    color: var(--text-secondary);
}

/* ── Level Badges ── */
.badge {
    display: inline-flex;
    align-items: center;
    padding: 3px 12px;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.3px;
}
.badge-advanced     { background: #DCFCE7; color: #166534; border: 1px solid #BBF7D0; }
.badge-intermediate { background: #FEF3C7; color: #92400E; border: 1px solid #FDE68A; }
.badge-beginner     { background: #FCE7F3; color: #9D174D; border: 1px solid #FBCFE8; }

/* ── Alert ── */
.alert-absent {
    background: var(--warn-bg);
    border: 1px solid var(--warn-border);
    border-left: 4px solid #F59E0B;
    border-radius: var(--radius-sm);
    padding: 14px 18px;
    color: var(--warn-text);
    margin: 14px 0;
    font-size: 0.9rem;
    line-height: 1.6;
}

/* ── Content Boxes ── */
.lesson-box {
    background: var(--bg-card);
    border: 1px solid var(--border-light);
    border-top: 3px solid #B8860B;
    border-radius: var(--radius-md);
    padding: 28px 32px;
    margin: 14px 0;
    white-space: pre-wrap;
    font-size: 0.95rem;
    line-height: 1.9;
    color: var(--text);
    box-shadow: var(--shadow-sm);
}
.worksheet-box {
    background: var(--bg-card);
    border: 1px solid var(--border-light);
    border-top: 3px solid #2D7A4F;
    border-radius: var(--radius-md);
    padding: 28px 32px;
    margin: 14px 0;
    white-space: pre-wrap;
    font-size: 0.95rem;
    line-height: 1.9;
    color: var(--text);
    box-shadow: var(--shadow-sm);
}

/* ── Quiz ── */
.quiz-q {
    background: var(--bg-card);
    border: 1px solid var(--border-light);
    border-radius: var(--radius-md);
    padding: 16px 20px;
    margin: 12px 0 4px 0;
    font-weight: 600;
    font-size: 0.95rem;
    color: var(--text);
    box-shadow: var(--shadow-sm);
    display: flex;
    align-items: flex-start;
    gap: 10px;
}
.quiz-num {
    background: var(--maroon);
    color: white;
    border-radius: 50%;
    width: 26px; height: 26px;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.78rem; font-weight: 700;
    flex-shrink: 0;
    margin-top: 1px;
}
.result-correct {
    background: var(--success-bg);
    border: 1px solid var(--success-border);
    border-radius: var(--radius-sm);
    padding: 14px 18px;
    margin: 8px 0;
    color: #0F5132;
    font-size: 0.9rem;
    line-height: 1.6;
}
.result-wrong {
    background: #FFF5F5;
    border: 1px solid #FEB2B2;
    border-radius: var(--radius-sm);
    padding: 14px 18px;
    margin: 8px 0;
    color: #7F1D1D;
    font-size: 0.9rem;
    line-height: 1.6;
}
.result-icon { font-size: 1rem; margin-right: 4px; }

/* ── Score Card ── */
.score-card {
    text-align: center;
    background: linear-gradient(135deg, #8D1B3D 0%, #B83060 100%);
    color: white;
    border-radius: var(--radius-xl);
    padding: 40px 30px;
    margin: 24px 0;
    box-shadow: var(--shadow-lg);
    position: relative;
    overflow: hidden;
}
.score-card::before {
    content: '';
    position: absolute;
    top: -30px; left: -30px;
    width: 120px; height: 120px;
    background: rgba(255,255,255,0.05);
    border-radius: 50%;
}
.score-card h1 {
    font-size: 3.5rem;
    margin: 0;
    font-family: 'DM Serif Display', serif;
    line-height: 1;
}
.score-card .pct {
    font-size: 1.1rem;
    opacity: 0.7;
    margin: 6px 0 16px 0;
    font-weight: 300;
}
.score-card .msg {
    font-size: 1.05rem;
    opacity: 0.9;
    font-weight: 500;
    background: rgba(255,255,255,0.12);
    border-radius: var(--radius-md);
    padding: 10px 20px;
    display: inline-block;
}

/* ── Video Card ── */
.video-card {
    background: var(--bg-card);
    border: 1px solid var(--border-light);
    border-top: 3px solid var(--terra);
    border-radius: var(--radius-md);
    padding: 22px 26px;
    margin: 14px 0;
    box-shadow: var(--shadow-sm);
}

/* ── Sent Summary ── */
.sent-success {
    background: var(--success-bg);
    border: 1px solid var(--success-border);
    border-radius: var(--radius-md);
    padding: 18px 22px;
    color: #0F5132;
    margin-top: 10px;
    box-shadow: var(--shadow-sm);
}
.sent-item {
    background: var(--bg-card);
    border: 1px solid var(--border-light);
    border-radius: var(--radius-sm);
    padding: 11px 16px;
    margin: 6px 0;
    font-size: 0.9rem;
    color: var(--text);
    display: flex;
    align-items: center;
    gap: 10px;
    box-shadow: var(--shadow-sm);
}
.sent-item-dot {
    width: 8px; height: 8px;
    background: var(--success);
    border-radius: 50%;
    flex-shrink: 0;
}

/* ── Divider ── */
.divider {
    height: 1px;
    background: var(--border);
    margin: 22px 0;
}

/* ── Section Header ── */
.section-header {
    font-size: 1.2rem;
    font-weight: 700;
    color: var(--text);
    margin: 18px 0 14px 0;
    display: flex;
    align-items: center;
    gap: 8px;
}
.section-header::after {
    content: '';
    flex: 1;
    height: 1px;
    background: var(--border);
    margin-left: 4px;
}

/* ── Student Header Card ── */
.student-header {
    background: var(--bg-card);
    border: 1px solid var(--border-light);
    border-radius: var(--radius-md);
    padding: 18px 24px;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 16px;
    box-shadow: var(--shadow-sm);
}
.student-avatar {
    width: 46px; height: 46px;
    background: linear-gradient(135deg, var(--maroon), #B83060);
    color: white;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.1rem; font-weight: 700;
    flex-shrink: 0;
}

/* ── Buttons ── */
.stButton > button {
    border-radius: var(--radius-sm) !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    transition: all 0.15s ease !important;
    letter-spacing: 0.2px !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, var(--maroon) 0%, var(--maroon-dk) 100%) !important;
    border: none !important;
    padding: 0.55rem 2rem !important;
    color: white !important;
    box-shadow: 0 2px 8px rgba(141,27,61,0.30) !important;
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #A02248 0%, var(--maroon) 100%) !important;
    box-shadow: 0 4px 14px rgba(141,27,61,0.38) !important;
    transform: translateY(-1px) !important;
}
.stButton > button[kind="secondary"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    box-shadow: var(--shadow-sm) !important;
}
.stButton > button[kind="secondary"]:hover {
    background: var(--bg-deep) !important;
    border-color: var(--text-secondary) !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 2px;
    background: var(--bg-deep) !important;
    border-radius: var(--radius-md) !important;
    padding: 4px !important;
    border: 1px solid var(--border) !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: var(--radius-sm) !important;
    font-weight: 600 !important;
    font-size: 0.86rem !important;
    background: transparent !important;
    color: var(--text-secondary) !important;
    padding: 8px 20px !important;
    transition: all 0.15s !important;
}
.stTabs [aria-selected="true"] {
    background: var(--bg-card) !important;
    color: var(--maroon) !important;
    box-shadow: var(--shadow-sm) !important;
}
.stTabs [data-testid="stTabContent"] {
    padding-top: 16px !important;
}

/* ── Metrics ── */
[data-testid="stMetric"] {
    background: var(--bg-card) !important;
    border-radius: var(--radius-md) !important;
    padding: 18px 22px !important;
    border: 1px solid var(--border-light) !important;
    box-shadow: var(--shadow-sm) !important;
}
[data-testid="stMetricLabel"] { color: var(--text-secondary) !important; font-size: 0.82rem !important; }
[data-testid="stMetricValue"] { color: var(--text) !important; font-weight: 700 !important; }

/* ── Inputs ── */
[data-testid="stSelectbox"] > div,
.stTextInput > div > div {
    background: var(--bg-card) !important;
    border-color: var(--border) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text) !important;
    box-shadow: var(--shadow-sm) !important;
}
[data-testid="stSelectbox"] > div:focus-within,
.stTextInput > div > div:focus-within {
    border-color: var(--maroon) !important;
    box-shadow: 0 0 0 3px rgba(141,27,61,0.12) !important;
}

/* ── Spinner ── */
.stSpinner > div { border-top-color: var(--maroon) !important; }

/* ── Radio ── */
[data-testid="stRadio"] > div { gap: 6px !important; }
[data-testid="stRadio"] label {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    padding: 8px 14px !important;
    cursor: pointer !important;
    transition: border-color 0.15s !important;
    font-size: 0.9rem !important;
}
[data-testid="stRadio"] label:hover { border-color: var(--maroon) !important; }

/* ── Alert / Info ── */
.stAlert {
    background: var(--bg-deep) !important;
    border-color: var(--border) !important;
    color: var(--text) !important;
    border-radius: var(--radius-sm) !important;
}

/* ── Bar chart ── */
[data-testid="stVegaLiteChart"] {
    background: transparent !important;
}

/* ── Empty state ── */
.empty-state {
    text-align: center;
    padding: 48px 24px;
    color: var(--text-secondary);
}
.empty-state .icon { font-size: 3rem; margin-bottom: 12px; opacity: 0.5; }
.empty-state h3 { font-size: 1rem; font-weight: 600; margin: 0 0 6px 0; color: var(--text); }
.empty-state p  { font-size: 0.88rem; margin: 0; }

/* ── Code inline ── */
code {
    background: var(--bg-deep) !important;
    color: var(--maroon) !important;
    padding: 2px 7px !important;
    border-radius: 4px !important;
    font-size: 0.85em !important;
    border: 1px solid var(--border) !important;
}

/* ── Label overrides ── */
.stMarkdown p { line-height: 1.7; }
label[data-testid="stWidgetLabel"] { font-weight: 600 !important; font-size: 0.88rem !important; color: var(--text-secondary) !important; }
</style>
""", unsafe_allow_html=True)

# ─── DATA ────────────────────────────────────────────────────
STUDENTS = {
    "Nour Al-Rashid": {
        "arabic_name":"نور الراشد","grade":5,"section":"A",
        "english_avg":88,"recent_grades":[85,90,87,88,91],
        "level":"Intermediate","level_ar":"متوسط","level_badge":"badge-intermediate"
    },
    "Lina Al-Mansouri": {
        "arabic_name":"لينا المنصوري","grade":5,"section":"A",
        "english_avg":62,"recent_grades":[58,65,60,62,64],
        "level":"Beginner","level_ar":"مبتدئ","level_badge":"badge-beginner"
    },
    "Reem Al-Hajri": {
        "arabic_name":"ريم الهاجري","grade":5,"section":"A",
        "english_avg":96,"recent_grades":[95,98,94,97,96],
        "level":"Advanced","level_ar":"متقدم","level_badge":"badge-advanced"
    },
    "Sara Al-Kuwari": {
        "arabic_name":"سارة الكواري","grade":5,"section":"B",
        "english_avg":75,"recent_grades":[72,76,74,78,75],
        "level":"Intermediate","level_ar":"متوسط","level_badge":"badge-intermediate"
    },
}

# Build LESSONS dict from curriculum for backward compat
LESSONS_BY_MODULE = get_lessons_by_module()
ALL_LESSONS = get_all_lessons()
LESSON_DISPLAY_NAMES = [l["display"] for l in ALL_LESSONS]
LESSON_MAP = {l["display"]: l for l in ALL_LESSONS}

# ─── AI FUNCTIONS ────────────────────────────────────────────
def call_gemini(prompt, api_key):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    try:
        r = requests.post(url, json={"contents":[{"parts":[{"text":prompt}]}],"generationConfig":{"temperature":0.7,"maxOutputTokens":2000}}, timeout=40)
        data = r.json()
        if "candidates" in data:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        return "Error: " + data.get("error",{}).get("message","Unknown")
    except Exception as e:
        return "Connection error: " + str(e)

def gen_lesson(lesson_name, lesson_info, level, api_key):
    vocab_str = ", ".join(lesson_info.get("vocabulary", [])[:8])
    standards_str = ", ".join(lesson_info.get("standards", []))
    prompt = f"""You are a friendly English teacher for Grade 5 in Qatar.
A student missed today's lesson and needs a personalised catch-up.

TOPIC: {lesson_name}
TYPE: {lesson_info["type"]}
OBJECTIVE: {lesson_info["objective"]}
CURRICULUM CONTENT (from the textbook):
{lesson_info["key_rules"]}
KEY VOCABULARY: {vocab_str}
STUDENT LEVEL: {level}
CURRICULUM STANDARDS: {standards_str}

Write a micro-lesson (200-260 words) adapted for a {level} student (age 10-11).
Base it STRICTLY on the curriculum content above.
Format (plain text only, no asterisks or hash symbols):

Learning Goal
[one sentence matching the objective]

The Rule
[explain the key rules simply — shorter/simpler for Beginner, richer for Advanced]

Examples
[4 clear examples using vocabulary from the lesson]

Remember This!
[one memorable tip related to the curriculum content]"""
    return call_gemini(prompt, api_key)

def gen_worksheet(lesson_name, lesson_info, level, api_key):
    corpus = st.session_state.get("rag_corpus") or []
    query  = f"{lesson_name} {level} Grade 5 English worksheet exercises"
    chunks = retrieve(query, corpus, api_key, top_k=3) if corpus else [lesson_info]
    context = build_context(chunks)
    prompt = f"""You are a Grade 5 English teacher in Qatar.
Generate a practice worksheet using ONLY the curriculum content below.

RETRIEVED CURRICULUM CONTEXT:
{context}

TARGET LESSON: {lesson_name}
STUDENT LEVEL: {level}

Write a worksheet (plain text, no asterisks or hash symbols):

EXERCISE 1 - Fill in the Blanks
Word bank: [5 words from the retrieved vocabulary]
5 sentences with one blank each. Based strictly on the curriculum rules above.

EXERCISE 2 - Circle the Correct Answer
4 questions testing the grammar or phonics from the context above. Options: a / b / c

EXERCISE 3 - Write Your Own Sentences
3 prompts asking the student to write sentences using today's rule.

Adapt difficulty to {level} level. No answers given."""
    return call_gemini(prompt, api_key)

def gen_quiz(lesson_name, lesson_info, level, api_key):
    prompt = f"""Create 5 multiple-choice questions for Grade 5 English in Qatar.
Base questions STRICTLY on this textbook content:

TOPIC: {lesson_name}
CURRICULUM RULES:
{lesson_info["key_rules"]}
STUDENT LEVEL: {level}

Return ONLY a valid JSON array, no markdown, no explanation:
[{{"question":"...","options":["option A text","option B text","option C text","option D text"],"answer":"option A text"}}]
Rules: exactly 5 questions, 4 options each, answer must match one option exactly, difficulty suits {level} level."""
    raw = call_gemini(prompt, api_key).strip()
    if "```" in raw:
        for p in raw.split("```"):
            p = p.strip().lstrip("json").strip()
            if p.startswith("["):
                raw = p; break
    s, e = raw.find("["), raw.rfind("]")+1
    if s != -1 and e > s:
        raw = raw[s:e]
    try:
        return json.loads(raw)
    except:
        return None


def gen_video_lesson(lesson_name, lesson_info, level):
    """Build HTML5 interactive lesson directly from curriculum — no API needed."""
    rules_text = lesson_info.get("key_rules", "").strip()
    vocab_list = lesson_info.get("vocabulary", [])[:8]
    obj_text   = lesson_info.get("objective", "")
    module_name = lesson_info.get("module", "")
    lesson_type = lesson_info.get("type", "Grammar")

    rule_lines = [l.strip() for l in rules_text.split("\n") if l.strip()]
    rule_body  = "<br>".join(rule_lines[:4]) if rule_lines else rules_text[:300]
    examples   = [l for l in rule_lines if l.startswith("-") or "->" in l or l.startswith("e.g")]
    if not examples:
        examples = rule_lines[4:7]
    ex_body    = "<br>".join(examples[:5]) if examples else "See examples in your worksheet."
    tip_body   = rule_lines[-1] if len(rule_lines) > 2 else f"Practice these words: {', '.join(vocab_list[:5])}"
    vocab_html = " &nbsp; ".join(f'<span style="background:rgba(255,255,255,0.18);padding:3px 12px;border-radius:14px;font-size:0.84rem;font-weight:500">{w}</span>' for w in vocab_list)

    level_colors = {"Beginner":"#8D1B3D","Intermediate":"#B85C1A","Advanced":"#1A6B3C"}
    slide_colors = [level_colors.get(level,"#8D1B3D"), "#1A4F7A", "#1A6B3C", "#5A3D8D"]
    icons = ["🎯","📖","✏️","💡"]
    titles = ["Learning Goal","The Rule","Examples","Remember!"]
    bodies = [obj_text, rule_body, ex_body, tip_body]

    slides_html = ""
    for i in range(4):
        slides_html += f'''
        <div class="slide" id="sl{i+1}" style="display:none">
          <div style="background:{slide_colors[i]};color:white;border-radius:16px;padding:30px 34px;min-height:260px;box-shadow:0 6px 24px rgba(0,0,0,0.16)">
            <div style="font-size:1.6rem;margin-bottom:10px">{icons[i]}</div>
            <div style="font-size:0.78rem;font-weight:700;opacity:0.65;letter-spacing:1px;text-transform:uppercase;margin-bottom:8px">{titles[i]}</div>
            <div style="font-size:0.96rem;line-height:1.85;opacity:0.95">{bodies[i]}</div>
          </div>
        </div>'''

    html = f'''<!DOCTYPE html><html><head><meta charset="UTF-8">
<style>
*{{box-sizing:border-box}}
body{{margin:0;padding:16px;font-family:Inter,Tajawal,sans-serif;background:#F5F2EE;color:#1C1410}}
.hdr{{text-align:center;margin-bottom:16px;padding:0 8px}}
.hdr h3{{margin:0;font-size:1rem;font-weight:700;color:#1C1410}}
.hdr p{{margin:4px 0 0;font-size:0.78rem;color:#6B5D52}}
.dots{{display:flex;justify-content:center;gap:8px;margin:16px 0}}
.dot{{width:8px;height:8px;border-radius:50%;background:#E0D9CF;cursor:pointer;transition:all .25s}}
.dot.on{{background:#8D1B3D;width:24px;border-radius:4px}}
.nav{{display:flex;justify-content:space-between;align-items:center;margin-top:14px}}
.btn{{background:#8D1B3D;color:white;border:none;border-radius:8px;padding:10px 26px;font-size:0.86rem;font-weight:600;cursor:pointer;transition:all .15s}}
.btn:hover{{background:#6B1530;transform:translateY(-1px)}}
.btn:disabled{{background:#E0D9CF;color:#A09080;cursor:default;transform:none}}
.ctr{{font-size:0.8rem;color:#6B5D52;font-weight:500}}
.vocab{{margin-top:14px;font-size:0.8rem;color:#6B5D52;text-align:center;line-height:2}}
</style></head><body>
<div class="hdr"><h3>{lesson_name}</h3><p>{module_name} &nbsp;·&nbsp; {level} Level &nbsp;·&nbsp; {lesson_type}</p></div>
{slides_html}
<div class="dots" id="dots"></div>
<div class="nav">
  <button class="btn" id="p" onclick="mv(-1)" disabled>← Back</button>
  <span class="ctr" id="ctr">1 / 4</span>
  <button class="btn" id="n" onclick="mv(1)">Next →</button>
</div>
<div class="vocab">{vocab_html}</div>
<script>
var c=0;
var dots=document.getElementById("dots");
for(var i=0;i<4;i++){{var d=document.createElement("span");d.className="dot"+(i==0?" on":"");(function(x){{d.onclick=function(){{go(x)}}}})(i);dots.appendChild(d);}}
function show(){{for(var i=1;i<=4;i++)document.getElementById("sl"+i).style.display="none";document.getElementById("sl"+(c+1)).style.display="block";document.querySelectorAll(".dot").forEach(function(d,i){{d.className="dot"+(i==c?" on":"")}});document.getElementById("ctr").textContent=(c+1)+" / 4";document.getElementById("p").disabled=c==0;document.getElementById("n").disabled=c==3;}}
function mv(d){{c=Math.max(0,Math.min(3,c+d));show();}}
function go(i){{c=i;show();}}
show();
</script></body></html>'''
    return html


# ─── SESSION STATE ───────────────────────────────────────────
defaults = {
    "view":"teacher","api_key":"",
    "lesson_content":None,"worksheet_content":None,
    "quiz_questions":None,"quiz_submitted":False,"quiz_answers":{},
    "pack_sent":False,"selected_student_cache":None,
    "rag_corpus":None,"rag_ready":False
}
for k,v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─── HERO ────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-icon">🎓</div>
    <div>
        <h1>iCatch &nbsp;<span style="font-weight:300;opacity:0.4">|</span>&nbsp; لحق</h1>
        <p class="tagline">AI-Powered Recovery · No Student Left Behind · Qatar MoEHE</p>
    </div>
    <div class="hero-badge">Grade 5 · English</div>
</div>
""", unsafe_allow_html=True)

# ─── API KEY from Streamlit Secrets ─────────────────────────
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    api_key = ""

# ─── VIEW TOGGLE ─────────────────────────────────────────────
col_t, col_s, col_empty = st.columns([1.2, 1.2, 6])
with col_t:
    if st.button("🏫  Teacher Dashboard", type="primary" if st.session_state.view=="teacher" else "secondary", use_container_width=True):
        st.session_state.view = "teacher"
        st.rerun()
with col_s:
    if st.button("🎒  Student View", type="primary" if st.session_state.view=="student" else "secondary", use_container_width=True):
        st.session_state.view = "student"
        st.rerun()

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  TEACHER DASHBOARD
# ══════════════════════════════════════════════════════════════
if st.session_state.view == "teacher":

    st.markdown('<div class="section-header">Teacher Dashboard</div>', unsafe_allow_html=True)

    col_a, col_b = st.columns([1.4, 1.6])

    with col_a:
        st.markdown("**Absent Student**")
        selected_student = st.selectbox("", list(STUDENTS.keys()), label_visibility="collapsed", key="t_student")
        student = STUDENTS[selected_student]

        # Reset pack if student changed
        if st.session_state.selected_student_cache != selected_student:
            st.session_state.pack_sent = False
            st.session_state.lesson_content = None
            st.session_state.worksheet_content = None
            st.session_state.quiz_questions = None
            st.session_state.selected_student_cache = selected_student

        # NSIS Panel
        level_color = {"Advanced":"#166534","Intermediate":"#92400E","Beginner":"#9D174D"}
        level_bg    = {"Advanced":"#DCFCE7","Intermediate":"#FEF3C7","Beginner":"#FCE7F3"}
        level_border= {"Advanced":"#BBF7D0","Intermediate":"#FDE68A","Beginner":"#FBCFE8"}
        lvl = student["level"]
        initials = "".join(w[0] for w in selected_student.split()[:2]).upper()
        scores_pills = "".join(f'<span class="score-pill">{s}</span>' for s in student['recent_grades'])

        st.markdown(f"""
        <div class="nsis-panel">
            <div class="nsis-label">NSIS — Academic Record</div>
            <div style="display:flex;align-items:center;gap:14px;margin-bottom:12px">
                <div style="width:42px;height:42px;background:linear-gradient(135deg,#8D1B3D,#B83060);
                            color:white;border-radius:50%;display:flex;align-items:center;
                            justify-content:center;font-size:0.95rem;font-weight:700;flex-shrink:0">{initials}</div>
                <div>
                    <div class="nsis-name">{selected_student} &nbsp;|&nbsp; {student['arabic_name']}</div>
                    <div class="nsis-avg">Grade {student['grade']} · Section {student['section']}</div>
                </div>
            </div>
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px">
                <span style="font-size:0.88rem;color:var(--text-secondary)">English Average:</span>
                <span style="font-size:1rem;font-weight:700;color:var(--text)">{student['english_avg']}%</span>
                <span style="background:{level_bg[lvl]};color:{level_color[lvl]};border:1px solid {level_border[lvl]};
                             padding:3px 12px;border-radius:20px;font-size:0.78rem;font-weight:700">{lvl} | {student['level_ar']}</span>
            </div>
            <div style="font-size:0.78rem;color:var(--text-secondary);margin-bottom:6px;font-weight:500">Recent quiz scores:</div>
            <div class="scores-row">{scores_pills}</div>
        </div>
        """, unsafe_allow_html=True)

        df = pd.DataFrame({"Quiz":[f"Q{i+1}" for i in range(5)],"Score":student['recent_grades']}).set_index("Quiz")
        st.bar_chart(df, color="#8D1B3D", height=150)

    with col_b:
        st.markdown("**Today's Lesson (Qatar Platform)**")
        selected_lesson = st.selectbox("", LESSON_DISPLAY_NAMES, label_visibility="collapsed", key="t_lesson")
        lesson = LESSON_MAP[selected_lesson]

        st.markdown(f"""
        <div class="card card-accent" style="margin-top:12px">
            <div class="card-title">📋 Lesson Posted by Teacher</div>
            <div style="display:grid;grid-template-columns:80px 1fr;gap:6px 12px;font-size:0.9rem">
                <span style="color:var(--text-secondary);font-weight:600">Unit</span>
                <span>{lesson.get('module','')}</span>
                <span style="color:var(--text-secondary);font-weight:600">Type</span>
                <span>{lesson['type']}</span>
                <span style="color:var(--text-secondary);font-weight:600">Objective</span>
                <span>{lesson['objective']}</span>
                <span style="color:var(--text-secondary);font-weight:600">Key Rule</span>
                <span><code>{lesson['key_rules'][:120]}{'...' if len(lesson['key_rules'])>120 else ''}</code></span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="alert-absent">
            <b>⚠️ Absence Detected</b> — {selected_student} ({student['arabic_name']}) was marked absent today.<br>
            <span style="opacity:0.85">Level from NSIS: <b>{student['level']}</b> — Recovery pack will be tailored accordingly.</span>
        </div>
        """, unsafe_allow_html=True)

        if not st.session_state.pack_sent:
            if st.button("✨  Generate and Send Recovery Pack", type="primary", use_container_width=True):
                if not api_key:
                    st.error("Please add your Gemini API Key in Streamlit Secrets.")
                else:
                    with st.spinner("Building knowledge base from curriculum..."):
                        if not st.session_state.rag_ready:
                            corpus = build_corpus()
                            st.session_state.rag_corpus = embed_corpus(corpus, api_key)
                            st.session_state.rag_ready  = True
                    with st.spinner("Preparing personalised recovery pack..."):
                        st.session_state.lesson_content    = gen_lesson(selected_lesson, lesson, student['level'], api_key)
                        st.session_state.worksheet_content = gen_worksheet(selected_lesson, lesson, student['level'], api_key)
                        st.session_state.quiz_questions    = gen_quiz(selected_lesson, lesson, student['level'], api_key)
                        st.session_state.video_html        = gen_video_lesson(selected_lesson, lesson, student['level'])
                        st.session_state.pack_sent = True
                    st.rerun()
        else:
            st.markdown("""
            <div class="sent-success">
                <div style="font-size:1rem;font-weight:700;margin-bottom:4px">✅ Recovery pack sent successfully</div>
                <div style="font-size:0.85rem;opacity:0.85">Student has been notified · Includes lesson, worksheet, quiz &amp; interactive slides</div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("**Pack Summary**", unsafe_allow_html=False)
            items = [
                ("📖", "Personalised micro-lesson (adapted to student level)"),
                ("📝", "Practice worksheet — 3 exercises"),
                ("✅", "5-question knowledge check quiz"),
                ("🎞️", "Interactive slide lesson (4 slides)"),
            ]
            for icon, text in items:
                st.markdown(f'<div class="sent-item"><div class="sent-item-dot"></div><span style="margin-right:6px">{icon}</span>{text}</div>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Switch to Student View →", type="secondary"):
                st.session_state.view = "student"
                st.rerun()

# ══════════════════════════════════════════════════════════════
#  STUDENT VIEW
# ══════════════════════════════════════════════════════════════
else:
    selected_student = st.session_state.get("t_student", list(STUDENTS.keys())[0])
    selected_lesson  = st.session_state.get("t_lesson",  LESSON_DISPLAY_NAMES[0])
    student = STUDENTS[selected_student]
    lesson  = LESSON_MAP.get(selected_lesson, ALL_LESSONS[0])

    initials = "".join(w[0] for w in selected_student.split()[:2]).upper()
    lvl = student["level"]
    level_color = {"Advanced":"#166534","Intermediate":"#92400E","Beginner":"#9D174D"}
    level_bg    = {"Advanced":"#DCFCE7","Intermediate":"#FEF3C7","Beginner":"#FCE7F3"}
    level_border= {"Advanced":"#BBF7D0","Intermediate":"#FDE68A","Beginner":"#FBCFE8"}

    st.markdown(f"""
    <div class="student-header">
        <div class="student-avatar">{initials}</div>
        <div>
            <div style="font-size:1.05rem;font-weight:700;color:var(--text)">{selected_student} &nbsp;<span style="opacity:0.4">|</span>&nbsp; {student['arabic_name']}</div>
            <div style="color:var(--text-secondary);font-size:0.85rem;margin-top:2px">
                Grade {student['grade']} · Section {student['section']} &nbsp;·&nbsp;
                <span style="background:{level_bg[lvl]};color:{level_color[lvl]};border:1px solid {level_border[lvl]};
                             padding:1px 10px;border-radius:12px;font-size:0.78rem;font-weight:700">{lvl}</span>
            </div>
        </div>
        <div style="margin-left:auto;text-align:right">
            <div style="font-size:0.75rem;color:var(--text-secondary);font-weight:500">Today's Lesson</div>
            <div style="font-size:0.85rem;font-weight:600;color:var(--text);max-width:200px;text-align:right">{selected_lesson}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.pack_sent:
        st.markdown("""
        <div class="empty-state">
            <div class="icon">📬</div>
            <h3>Your recovery pack isn't ready yet</h3>
            <p>Your teacher will send it shortly. Check back soon!</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        tab1, tab2, tab3, tab4 = st.tabs(["📖  Lesson", "📝  Worksheet", "✅  Quiz", "🎞️  Interactive"])

        # ── Lesson ──────────────────────────────────────────
        with tab1:
            st.markdown('<div class="section-header">Today\'s Lesson</div>', unsafe_allow_html=True)
            if st.session_state.lesson_content:
                st.markdown(f'<div class="lesson-box">{st.session_state.lesson_content}</div>', unsafe_allow_html=True)

        # ── Worksheet ───────────────────────────────────────
        with tab2:
            st.markdown('<div class="section-header">Practice Worksheet</div>', unsafe_allow_html=True)
            if st.session_state.worksheet_content:
                st.markdown(f'<div class="worksheet-box">{st.session_state.worksheet_content}</div>', unsafe_allow_html=True)

        # ── Quiz ────────────────────────────────────────────
        with tab3:
            st.markdown('<div class="section-header">Knowledge Check</div>', unsafe_allow_html=True)

            if st.session_state.quiz_questions and not st.session_state.quiz_submitted:
                questions = st.session_state.quiz_questions
                answers = {}
                for i, q in enumerate(questions):
                    st.markdown(f'''<div class="quiz-q">
                        <div class="quiz-num">{i+1}</div>
                        <span>{q["question"]}</span>
                    </div>''', unsafe_allow_html=True)
                    answers[i] = st.radio("", q["options"], key=f"qr_{i}", label_visibility="collapsed")
                    st.markdown("<div style='margin-bottom:8px'></div>", unsafe_allow_html=True)

                st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
                if st.button("Submit Answers", type="primary", key="submit_q"):
                    st.session_state.quiz_answers   = answers
                    st.session_state.quiz_submitted = True
                    st.rerun()

            elif st.session_state.quiz_questions and st.session_state.quiz_submitted:
                questions = st.session_state.quiz_questions
                user_ans  = st.session_state.quiz_answers
                score = 0
                for i, q in enumerate(questions):
                    chosen  = user_ans.get(i,"")
                    correct = q["answer"]
                    ok      = (chosen == correct)
                    if ok: score += 1
                    if ok:
                        st.markdown(f'''<div class="result-correct">
                            <span class="result-icon">✅</span>
                            <b>Q{i+1}:</b> {q["question"]}<br>
                            <small style="opacity:0.8">Your answer: {chosen}</small>
                        </div>''', unsafe_allow_html=True)
                    else:
                        st.markdown(f'''<div class="result-wrong">
                            <span class="result-icon">❌</span>
                            <b>Q{i+1}:</b> {q["question"]}<br>
                            <small style="opacity:0.8">Your answer: {chosen} &nbsp;·&nbsp; Correct: <b>{correct}</b></small>
                        </div>''', unsafe_allow_html=True)

                pct  = int(score / len(questions) * 100)
                msgs = {5:"🎉 Perfect Score!", 4:"🌟 Excellent work!", 3:"👍 Good effort — keep practising."}
                msg  = msgs.get(score, "📚 Review the lesson and try again.")
                st.markdown(f"""
                <div class="score-card">
                    <h1>{score} / 5</h1>
                    <p class="pct">{pct}%</p>
                    <span class="msg">{msg}</span>
                </div>""", unsafe_allow_html=True)

                if st.button("Try Again", key="retry", type="secondary"):
                    st.session_state.quiz_submitted = False
                    st.rerun()

        # ── Interactive Lesson (HTML5 slides) ────────────────
        with tab4:
            st.markdown('<div class="section-header">Interactive Lesson</div>', unsafe_allow_html=True)
            if "video_html" not in st.session_state:
                st.session_state.video_html = None
            if st.session_state.video_html:
                import streamlit.components.v1 as components
                components.html(st.session_state.video_html, height=500, scrolling=False)
            else:
                st.markdown("""
                <div class="empty-state">
                    <div class="icon">🎞️</div>
                    <h3>Interactive lesson not loaded</h3>
                    <p>Ask your teacher to resend the recovery pack.</p>
                </div>
                """, unsafe_allow_html=True)
