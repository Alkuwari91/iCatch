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
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Design tokens (Agenta-style shadcn/ui vocabulary) ── */
:root {
    --background:   #ffffff;
    --foreground:   #09090b;
    --card:         #ffffff;
    --card-border:  #e4e4e7;
    --muted:        #f4f4f5;
    --muted-fg:     #71717a;
    --border:       #e4e4e7;
    --input-bg:     #ffffff;
    --ring:         rgba(141,27,61,0.20);
    --radius:       0.5rem;

    /* Brand */
    --primary:      #8D1B3D;
    --primary-dk:   #6B1530;
    --primary-ring: rgba(141,27,61,0.15);

    /* Semantic */
    --success:      #16a34a;
    --success-bg:   #f0fdf4;
    --success-bd:   #bbf7d0;
    --warn-bg:      #fefce8;
    --warn-bd:      #fde047;
    --warn-fg:      #854d0e;
    --error-bg:     #fff1f2;
    --error-bd:     #fecdd3;
    --error-fg:     #881337;

    /* Shadows — neutral, not warm-tinted */
    --shadow-xs:    0 1px 2px rgba(0,0,0,0.05);
    --shadow-sm:    0 1px 3px rgba(0,0,0,0.07), 0 1px 2px rgba(0,0,0,0.04);
    --shadow-md:    0 4px 8px rgba(0,0,0,0.06), 0 2px 4px rgba(0,0,0,0.04);
    --shadow-lg:    0 10px 24px rgba(0,0,0,0.09), 0 4px 8px rgba(0,0,0,0.05);
}

/* ── Reset & base ── */
html, body, [class*="css"] {
    font-family: 'Inter', 'Tajawal', ui-sans-serif, system-ui, sans-serif;
    color: var(--foreground);
    -webkit-font-smoothing: antialiased;
    font-feature-settings: "cv02","cv03","cv04","cv11";
}
.stApp, [data-testid="stAppViewContainer"] {
    background: #fafafa !important;
}
[data-testid="stHeader"]          { background: transparent !important; }
[data-testid="collapsedControl"],
section[data-testid="stSidebar"]  { display: none !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar              { width:5px; height:5px; }
::-webkit-scrollbar-track        { background: var(--muted); }
::-webkit-scrollbar-thumb        { background: #d4d4d8; border-radius:3px; }
::-webkit-scrollbar-thumb:hover  { background: #a1a1aa; }

/* ══════════════════════════════════════════
   HERO — dark ground, maroon accent stripe
══════════════════════════════════════════ */
.hero {
    background: #0c0c0e;
    color: #fafafa;
    padding: 28px 40px;
    border-radius: calc(var(--radius) * 2);
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    gap: 20px;
    box-shadow: var(--shadow-lg);
    border: 1px solid #1f1f23;
    position: relative;
    overflow: hidden;
}
/* Maroon accent line along top */
.hero::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--primary) 0%, #c94070 50%, transparent 100%);
}
/* Subtle grid texture */
.hero::after {
    content: '';
    position: absolute;
    inset: 0;
    background-image:
        linear-gradient(rgba(255,255,255,0.015) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.015) 1px, transparent 1px);
    background-size: 32px 32px;
    pointer-events: none;
}
.hero-icon {
    font-size: 2.4rem;
    line-height: 1;
    background: rgba(141,27,61,0.18);
    border: 1px solid rgba(141,27,61,0.30);
    border-radius: var(--radius);
    padding: 12px 14px;
    flex-shrink: 0;
    position: relative; z-index: 1;
}
.hero-text { position: relative; z-index: 1; }
.hero h1 {
    margin: 0;
    font-size: 1.8rem;
    font-weight: 700;
    letter-spacing: -0.6px;
    line-height: 1.15;
    color: #fafafa;
}
.hero h1 span.ar {
    font-family: 'Tajawal', sans-serif;
    font-weight: 400;
    color: #a1a1aa;
    font-size: 1.4rem;
}
.hero .tagline {
    font-size: 0.82rem;
    color: #71717a;
    margin: 5px 0 0 0;
    font-weight: 400;
    letter-spacing: 0.2px;
}
.hero-badge {
    margin-left: auto;
    background: rgba(141,27,61,0.12);
    border: 1px solid rgba(141,27,61,0.25);
    border-radius: calc(var(--radius) * 0.75);
    padding: 6px 14px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.4px;
    color: #fda4af;
    flex-shrink: 0;
    position: relative; z-index: 1;
}

/* ══════════════════════════════════════════
   CARDS
══════════════════════════════════════════ */
.card {
    background: var(--card);
    border: 1px solid var(--card-border);
    border-radius: var(--radius);
    padding: 20px 24px;
    margin: 10px 0;
    line-height: 1.65;
    font-size: 0.9rem;
    color: var(--foreground);
    box-shadow: var(--shadow-xs);
}
.card-accent { border-left: 3px solid var(--primary); }
.card-title {
    font-size: 0.72rem;
    font-weight: 600;
    color: var(--muted-fg);
    text-transform: uppercase;
    letter-spacing: 0.9px;
    margin-bottom: 14px;
}

/* ══════════════════════════════════════════
   NSIS PANEL
══════════════════════════════════════════ */
.nsis-panel {
    background: var(--card);
    border: 1px solid var(--card-border);
    border-radius: var(--radius);
    padding: 18px 22px;
    margin: 12px 0;
    box-shadow: var(--shadow-xs);
}
.nsis-label {
    font-size: 0.68rem;
    font-weight: 600;
    color: var(--muted-fg);
    letter-spacing: 1.1px;
    text-transform: uppercase;
    margin-bottom: 14px;
    display: flex;
    align-items: center;
    gap: 7px;
}
.nsis-label::before {
    content: '';
    width: 2px; height: 11px;
    background: var(--primary);
    border-radius: 1px;
    display: inline-block;
}
.nsis-name {
    font-size: 1rem;
    font-weight: 600;
    margin-bottom: 2px;
    color: var(--foreground);
    letter-spacing: -0.2px;
}
.nsis-avg  { font-size: 0.82rem; color: var(--muted-fg); }
.scores-row { display: flex; gap: 5px; margin-top: 10px; flex-wrap: wrap; }
.score-pill {
    background: var(--muted);
    border: 1px solid var(--border);
    border-radius: 999px;
    padding: 2px 10px;
    font-size: 0.75rem;
    font-weight: 500;
    color: var(--muted-fg);
}

/* ══════════════════════════════════════════
   BADGES
══════════════════════════════════════════ */
.badge-advanced     { display:inline-flex;align-items:center;padding:2px 10px;border-radius:999px;font-size:0.72rem;font-weight:600;
                      background:#dcfce7; color:#15803d; border:1px solid #bbf7d0; }
.badge-intermediate { display:inline-flex;align-items:center;padding:2px 10px;border-radius:999px;font-size:0.72rem;font-weight:600;
                      background:#fef9c3; color:#a16207; border:1px solid #fde047; }
.badge-beginner     { display:inline-flex;align-items:center;padding:2px 10px;border-radius:999px;font-size:0.72rem;font-weight:600;
                      background:#fce7f3; color:#9d174d; border:1px solid #fbcfe8; }

/* ══════════════════════════════════════════
   ALERTS
══════════════════════════════════════════ */
.alert-absent {
    background: var(--warn-bg);
    border: 1px solid var(--warn-bd);
    border-left: 3px solid #eab308;
    border-radius: var(--radius);
    padding: 12px 16px;
    color: var(--warn-fg);
    margin: 12px 0;
    font-size: 0.875rem;
    line-height: 1.6;
}

/* ══════════════════════════════════════════
   CONTENT BOXES
══════════════════════════════════════════ */
.lesson-box {
    background: var(--card);
    border: 1px solid var(--card-border);
    border-top: 2px solid #ca8a04;
    border-radius: var(--radius);
    padding: 26px 30px;
    margin: 12px 0;
    white-space: pre-wrap;
    font-size: 0.9rem;
    line-height: 1.85;
    color: var(--foreground);
    box-shadow: var(--shadow-xs);
}
.worksheet-box {
    background: var(--card);
    border: 1px solid var(--card-border);
    border-top: 2px solid #16a34a;
    border-radius: var(--radius);
    padding: 26px 30px;
    margin: 12px 0;
    white-space: pre-wrap;
    font-size: 0.9rem;
    line-height: 1.85;
    color: var(--foreground);
    box-shadow: var(--shadow-xs);
}

/* ══════════════════════════════════════════
   QUIZ
══════════════════════════════════════════ */
.quiz-q {
    background: var(--card);
    border: 1px solid var(--card-border);
    border-radius: var(--radius);
    padding: 14px 18px;
    margin: 10px 0 3px 0;
    font-weight: 500;
    font-size: 0.9rem;
    color: var(--foreground);
    box-shadow: var(--shadow-xs);
    display: flex;
    align-items: flex-start;
    gap: 10px;
}
.quiz-num {
    background: var(--primary);
    color: #fff;
    border-radius: 999px;
    min-width: 22px; height: 22px;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.72rem; font-weight: 700;
    flex-shrink: 0;
    margin-top: 2px;
}
.result-correct {
    background: var(--success-bg);
    border: 1px solid var(--success-bd);
    border-radius: var(--radius);
    padding: 12px 16px;
    margin: 6px 0;
    color: #14532d;
    font-size: 0.875rem;
    line-height: 1.6;
}
.result-wrong {
    background: var(--error-bg);
    border: 1px solid var(--error-bd);
    border-radius: var(--radius);
    padding: 12px 16px;
    margin: 6px 0;
    color: var(--error-fg);
    font-size: 0.875rem;
    line-height: 1.6;
}

/* ══════════════════════════════════════════
   SCORE CARD
══════════════════════════════════════════ */
.score-card {
    text-align: center;
    background: #0c0c0e;
    border: 1px solid #1f1f23;
    color: #fafafa;
    border-radius: calc(var(--radius) * 2);
    padding: 44px 32px;
    margin: 20px 0;
    box-shadow: var(--shadow-lg);
    position: relative;
    overflow: hidden;
}
.score-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--primary), #c94070, transparent);
}
.score-card h1 {
    font-size: 4rem;
    margin: 0;
    font-weight: 700;
    letter-spacing: -2px;
    line-height: 1;
    color: #fafafa;
}
.score-card .pct  { font-size: 0.95rem; color: #71717a; margin: 8px 0 20px 0; }
.score-card .msg  {
    font-size: 0.9rem; font-weight: 500;
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: var(--radius);
    padding: 8px 18px;
    display: inline-block;
    color: #e4e4e7;
}

/* ══════════════════════════════════════════
   SENT SUMMARY
══════════════════════════════════════════ */
.sent-success {
    background: var(--success-bg);
    border: 1px solid var(--success-bd);
    border-radius: var(--radius);
    padding: 16px 20px;
    color: #14532d;
    margin-top: 10px;
}
.sent-item {
    background: var(--card);
    border: 1px solid var(--card-border);
    border-radius: var(--radius);
    padding: 10px 14px;
    margin: 5px 0;
    font-size: 0.875rem;
    color: var(--foreground);
    display: flex;
    align-items: center;
    gap: 10px;
    box-shadow: var(--shadow-xs);
}
.sent-item-dot {
    width: 6px; height: 6px;
    background: var(--success);
    border-radius: 50%;
    flex-shrink: 0;
}

/* ══════════════════════════════════════════
   LAYOUT HELPERS
══════════════════════════════════════════ */
.divider { height: 1px; background: var(--border); margin: 20px 0; }

.section-header {
    font-size: 1.05rem;
    font-weight: 600;
    color: var(--foreground);
    margin: 16px 0 12px 0;
    letter-spacing: -0.2px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.section-header::after {
    content: '';
    flex: 1;
    height: 1px;
    background: var(--border);
}

.student-header {
    background: var(--card);
    border: 1px solid var(--card-border);
    border-radius: var(--radius);
    padding: 16px 22px;
    margin-bottom: 14px;
    display: flex;
    align-items: center;
    gap: 14px;
    box-shadow: var(--shadow-xs);
}
.student-avatar {
    width: 40px; height: 40px;
    background: var(--primary);
    color: #fff;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.9rem; font-weight: 700;
    flex-shrink: 0;
}

.empty-state {
    text-align: center;
    padding: 56px 24px;
    color: var(--muted-fg);
    background: var(--card);
    border: 1px dashed var(--border);
    border-radius: calc(var(--radius) * 1.5);
    margin: 8px 0;
}
.empty-state .icon  { font-size: 2.4rem; margin-bottom: 12px; display: block; opacity: 0.4; }
.empty-state h3     { font-size: 0.95rem; font-weight: 600; margin: 0 0 4px; color: var(--foreground); }
.empty-state p      { font-size: 0.82rem; margin: 0; }

/* ══════════════════════════════════════════
   STREAMLIT COMPONENT OVERRIDES
══════════════════════════════════════════ */

/* Buttons */
.stButton > button {
    border-radius: var(--radius) !important;
    font-weight: 500 !important;
    font-size: 0.875rem !important;
    transition: all 0.15s cubic-bezier(.4,0,.2,1) !important;
    letter-spacing: 0.1px !important;
    height: 2.25rem !important;
}
.stButton > button[kind="primary"] {
    background: var(--primary) !important;
    border: 1px solid var(--primary-dk) !important;
    color: #fff !important;
    box-shadow: var(--shadow-xs) !important;
}
.stButton > button[kind="primary"]:hover {
    background: #a02248 !important;
    box-shadow: var(--shadow-sm) !important;
    transform: translateY(-1px) !important;
}
.stButton > button[kind="secondary"] {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    color: var(--foreground) !important;
    box-shadow: var(--shadow-xs) !important;
}
.stButton > button[kind="secondary"]:hover {
    background: var(--muted) !important;
    border-color: #a1a1aa !important;
}

/* Tabs — pill segment control */
.stTabs [data-baseweb="tab-list"] {
    gap: 2px;
    background: var(--muted) !important;
    border-radius: calc(var(--radius) * 1.25) !important;
    padding: 3px !important;
    border: 1px solid var(--border) !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: var(--radius) !important;
    font-weight: 500 !important;
    font-size: 0.82rem !important;
    background: transparent !important;
    color: var(--muted-fg) !important;
    padding: 6px 18px !important;
    transition: all 0.15s !important;
}
.stTabs [aria-selected="true"] {
    background: var(--card) !important;
    color: var(--foreground) !important;
    box-shadow: var(--shadow-sm) !important;
    font-weight: 600 !important;
}
.stTabs [data-testid="stTabContent"] { padding-top: 14px !important; }

/* Selectbox / text input */
[data-testid="stSelectbox"] > div,
.stTextInput > div > div {
    background: var(--input-bg) !important;
    border-color: var(--border) !important;
    border-radius: var(--radius) !important;
    color: var(--foreground) !important;
    box-shadow: var(--shadow-xs) !important;
    font-size: 0.875rem !important;
}
[data-testid="stSelectbox"] > div:focus-within,
.stTextInput > div > div:focus-within {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 3px var(--ring) !important;
}

/* Radio options */
[data-testid="stRadio"] > div { gap: 5px !important; }
[data-testid="stRadio"] label {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    padding: 8px 13px !important;
    cursor: pointer !important;
    transition: border-color 0.15s, background 0.15s !important;
    font-size: 0.875rem !important;
    color: var(--foreground) !important;
}
[data-testid="stRadio"] label:hover {
    border-color: #a1a1aa !important;
    background: var(--muted) !important;
}

/* Metrics */
[data-testid="stMetric"] {
    background: var(--card) !important;
    border-radius: var(--radius) !important;
    padding: 16px 20px !important;
    border: 1px solid var(--card-border) !important;
    box-shadow: var(--shadow-xs) !important;
}
[data-testid="stMetricLabel"] { color: var(--muted-fg) !important; font-size: 0.78rem !important; }
[data-testid="stMetricValue"] { color: var(--foreground) !important; font-weight: 700 !important; }

/* Alert / info */
.stAlert {
    background: var(--muted) !important;
    border-color: var(--border) !important;
    color: var(--foreground) !important;
    border-radius: var(--radius) !important;
    font-size: 0.875rem !important;
}

/* Spinner */
.stSpinner > div { border-top-color: var(--primary) !important; }

/* Bar chart */
[data-testid="stVegaLiteChart"] { background: transparent !important; }

/* Inline code */
code {
    background: var(--muted) !important;
    color: var(--primary) !important;
    padding: 2px 6px !important;
    border-radius: calc(var(--radius) * 0.5) !important;
    font-size: 0.82em !important;
    border: 1px solid var(--border) !important;
    font-family: ui-monospace, 'Cascadia Code', monospace !important;
}

/* Widget labels */
.stMarkdown p { line-height: 1.65; font-size: 0.9rem; }
label[data-testid="stWidgetLabel"] {
    font-weight: 500 !important;
    font-size: 0.82rem !important;
    color: var(--muted-fg) !important;
    letter-spacing: 0.1px !important;
}
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
          <div style="background:{slide_colors[i]};color:#fafafa;border-radius:10px;padding:26px 30px;min-height:240px;
                      box-shadow:0 4px 16px rgba(0,0,0,0.18);border:1px solid rgba(255,255,255,0.08);position:relative;overflow:hidden">
            <div style="position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,rgba(255,255,255,0.3),transparent)"></div>
            <div style="font-size:1.4rem;margin-bottom:10px">{icons[i]}</div>
            <div style="font-size:0.65rem;font-weight:600;opacity:0.55;letter-spacing:1.1px;text-transform:uppercase;margin-bottom:8px">{titles[i]}</div>
            <div style="font-size:0.88rem;line-height:1.8;opacity:0.92">{bodies[i]}</div>
          </div>
        </div>'''

    html = f'''<!DOCTYPE html><html><head><meta charset="UTF-8">
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:Inter,ui-sans-serif,sans-serif;background:#fafafa;color:#09090b;padding:16px;-webkit-font-smoothing:antialiased}}
.hdr{{text-align:center;margin-bottom:14px}}
.hdr h3{{font-size:0.95rem;font-weight:600;color:#09090b;letter-spacing:-0.2px}}
.hdr p{{font-size:0.72rem;color:#71717a;margin-top:3px}}
.dots{{display:flex;justify-content:center;gap:6px;margin:14px 0}}
.dot{{width:6px;height:6px;border-radius:50%;background:#e4e4e7;cursor:pointer;transition:all .2s cubic-bezier(.4,0,.2,1)}}
.dot.on{{background:#8D1B3D;width:20px;border-radius:3px}}
.nav{{display:flex;justify-content:space-between;align-items:center;margin-top:12px}}
.btn{{background:#8D1B3D;color:#fff;border:none;border-radius:6px;padding:8px 22px;font-size:0.8rem;font-weight:500;cursor:pointer;transition:all .15s}}
.btn:hover{{background:#6B1530;transform:translateY(-1px)}}
.btn:disabled{{background:#f4f4f5;color:#a1a1aa;cursor:default;transform:none;border:1px solid #e4e4e7}}
.ctr{{font-size:0.75rem;color:#71717a;font-weight:500}}
.vocab{{margin-top:12px;font-size:0.75rem;color:#71717a;text-align:center;line-height:2.2}}
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
    <div class="hero-text">
        <h1>iCatch &nbsp;<span class="ar">| لحق</span></h1>
        <p class="tagline">AI-Powered Recovery &nbsp;·&nbsp; No Student Left Behind &nbsp;·&nbsp; Qatar MoEHE</p>
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
