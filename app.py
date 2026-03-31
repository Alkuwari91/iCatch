import streamlit as st
import requests
import json
import pandas as pd
from datetime import date
from curriculum import CURRICULUM, STANDARDS, get_lessons_by_module, get_all_lessons
from rag import build_corpus, embed_corpus, retrieve, build_context

st.set_page_config(
    page_title="iCatch | لحق",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;700;900&family=DM+Serif+Display&family=Inter:wght@300;400;600;700&display=swap');

:root {
    --bg:        #F2EDE6;
    --bg-card:   #FBF7F2;
    --bg-deep:   #EDE6DC;
    --border:    #D8CDBC;
    --text:      #2C1F14;
    --muted:     #7A6858;
    --maroon:    #8D1B3D;
    --maroon-dk: #6B1530;
    --terra:     #C8703C;
    --success:   #5C7A4A;
    --success-bg:#EDF5E8;
    --warn-bg:   #FEF6EC;
    --warn-br:   #E8C080;
}

html, body, [class*="css"] {
    font-family: 'Inter', 'Tajawal', sans-serif;
    color: var(--text);
}

/* Force background */
.stApp, [data-testid="stAppViewContainer"] { background: var(--bg) !important; }
[data-testid="stHeader"] { background: transparent !important; }
[data-testid="collapsedControl"], section[data-testid="stSidebar"] { display: none !important; }

/* Hero */
.hero {
    background: linear-gradient(135deg, #8D1B3D 0%, #6B1530 55%, #4A0F22 100%);
    color: white;
    padding: 26px 40px;
    border-radius: 14px;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    gap: 20px;
    box-shadow: 0 6px 28px rgba(141,27,61,0.28);
}
.hero h1 { margin:0; font-family:'DM Serif Display',serif; font-size:2rem; font-weight:400; letter-spacing:-0.3px; }
.hero .tagline { font-family:'Tajawal',sans-serif; font-size:0.95rem; font-weight:700; opacity:0.85; margin:4px 0 0 0; }

/* View toggle */
.view-toggle { display:flex; gap:10px; margin-bottom:20px; }

/* Cards */
.card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px 24px;
    margin: 10px 0;
    line-height: 1.75;
    font-size: 0.94rem;
    color: var(--text);
}
.card-accent { border-left: 5px solid var(--maroon); }
.card-title { font-size:1rem; font-weight:700; color:var(--maroon); margin-bottom:10px; }

/* NSIS panel */
.nsis-panel {
    background: var(--bg-deep);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 18px 24px;
    margin: 14px 0;
}

/* Badges */
.badge-advanced     { background:#3D6B2C; color:#fff; padding:3px 12px; border-radius:20px; font-size:0.8rem; font-weight:700; }
.badge-intermediate { background:#B85C1A; color:#fff; padding:3px 12px; border-radius:20px; font-size:0.8rem; font-weight:700; }
.badge-beginner     { background:#8D1B3D; color:#fff; padding:3px 12px; border-radius:20px; font-size:0.8rem; font-weight:700; }

/* Alert */
.alert-absent {
    background: var(--warn-bg);
    border: 1px solid var(--warn-br);
    border-left: 5px solid var(--terra);
    border-radius: 8px;
    padding: 14px 18px;
    color: #7C3A00;
    margin: 12px 0;
}

/* Content boxes */
.lesson-box {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-top: 4px solid #C8A060;
    border-radius: 10px;
    padding: 26px 30px;
    margin: 14px 0;
    white-space: pre-wrap;
    font-size: 0.97rem;
    line-height: 1.85;
    color: var(--text);
}
.worksheet-box {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-top: 4px solid #7A9A6A;
    border-radius: 10px;
    padding: 26px 30px;
    margin: 14px 0;
    white-space: pre-wrap;
    font-size: 0.97rem;
    line-height: 1.85;
    color: var(--text);
}

/* Quiz */
.quiz-q {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 14px 18px;
    margin: 10px 0;
    font-weight: 600;
    color: var(--text);
}
.result-correct { background:#EDF5E8; border:1px solid #A8CCA0; border-radius:8px; padding:12px 16px; margin:6px 0; color:#2C5A20; }
.result-wrong   { background:#FBF0EC; border:1px solid #DDB898; border-radius:8px; padding:12px 16px; margin:6px 0; color:#7C3010; }

/* Score */
.score-card {
    text-align:center;
    background: linear-gradient(135deg, #8D1B3D, #B83060);
    color:white; border-radius:14px;
    padding:30px; margin:20px 0;
    box-shadow:0 6px 20px rgba(141,27,61,0.28);
}
.score-card h1 { font-size:3rem; margin:0; font-family:'DM Serif Display',serif; }
.score-card p  { opacity:0.88; font-size:1rem; margin:8px 0 0 0; }

/* Video card */
.video-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-top: 4px solid var(--terra);
    border-radius: 10px;
    padding: 20px 24px;
    margin: 14px 0;
}
.video-sent-badge {
    display:inline-block;
    background:#EDF5E8; color:#2C5A20;
    border:1px solid #A8CCA0;
    padding:4px 14px; border-radius:20px;
    font-size:0.82rem; font-weight:700;
    margin-bottom:12px;
}

/* Sent summary */
.sent-item {
    background: var(--bg-card);
    border:1px solid var(--border);
    border-radius:8px;
    padding:10px 16px;
    margin:6px 0;
    font-size:0.9rem;
    color: var(--text);
}

/* Buttons */
.stButton > button[kind="primary"] {
    background: var(--maroon) !important; border:none !important;
    border-radius:8px !important; font-weight:600 !important;
    padding:0.5rem 2rem !important; color:white !important;
}
.stButton > button[kind="primary"]:hover { background: var(--maroon-dk) !important; }
.stButton > button[kind="secondary"] {
    background: var(--bg-deep) !important;
    border:1px solid var(--border) !important;
    border-radius:8px !important; font-weight:600 !important;
    color: var(--text) !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] { gap:6px; background:transparent !important; }
.stTabs [data-baseweb="tab"] {
    border-radius:8px 8px 0 0 !important;
    font-weight:600 !important;
    font-size:0.88rem !important;
    background: var(--bg-deep) !important;
    color: var(--text) !important;
}
.stTabs [aria-selected="true"] { background: var(--maroon) !important; color:white !important; }

/* Metrics */
[data-testid="stMetric"] {
    background: var(--bg-card) !important;
    border-radius:10px !important; padding:14px 18px !important;
    border:1px solid var(--border) !important;
}
[data-testid="stMetricLabel"], [data-testid="stMetricValue"] { color: var(--text) !important; }

/* Selectbox and inputs */
[data-testid="stSelectbox"] > div, .stTextInput > div > div {
    background: var(--bg-card) !important;
    border-color: var(--border) !important;
    color: var(--text) !important;
}

/* Divider */
hr { border-color: var(--border) !important; }

/* Section header */
.section-header {
    font-size:1.3rem; font-weight:700;
    color: var(--text);
    margin: 20px 0 12px 0;
    padding-bottom:8px;
    border-bottom:2px solid var(--border);
}

/* Info override */
.stAlert { background: var(--bg-deep) !important; border-color: var(--border) !important; color: var(--text) !important; }
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
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={api_key}"
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


def gen_video_lesson(lesson_name, lesson_info, level, api_key):
    """RAG-powered: generate structured JSON for HTML5 interactive lesson."""
    corpus  = st.session_state.get("rag_corpus") or []
    query   = f"{lesson_name} {level} interactive explanation examples"
    chunks  = retrieve(query, corpus, api_key, top_k=3) if corpus else [lesson_info]
    context = build_context(chunks)

    prompt = f"""You are creating a 4-slide interactive lesson for a Grade 5 student in Qatar.
Use ONLY the curriculum content below as your source.

RETRIEVED CURRICULUM CONTEXT:
{context}

TARGET LESSON: {lesson_name}
STUDENT LEVEL: {level}

Return ONLY a valid JSON object, no markdown, no explanation:
{{
  "title": "short lesson title",
  "slides": [
    {{"id":1,"title":"Learning Goal","body":"one clear sentence stating what we learn today","example":""}},
    {{"id":2,"title":"The Rule","body":"clear explanation of the grammar or phonics rule","example":"one example sentence from the curriculum"}},
    {{"id":3,"title":"Examples","body":"3 example sentences from the curriculum content, numbered 1 2 3","example":""}},
    {{"id":4,"title":"Remember!","body":"one memorable tip from the curriculum","example":"a short practice sentence for the student to complete"}}
  ]
}}"""

    raw = call_gemini(prompt, api_key).strip()
    if "```" in raw:
        for p in raw.split("```"):
            p = p.strip().lstrip("json").strip()
            if p.startswith("{"):
                raw = p; break
    s, e = raw.find("{"), raw.rfind("}")+1
    if s != -1 and e > s:
        raw = raw[s:e]
    try:
        data = json.loads(raw)
    except Exception:
        return None

    colors = ["#8D1B3D","#B85C1A","#3D6B2C","#1A5C7A"]
    icons  = ["🎯","📖","✏️","💡"]

    slides_html = ""
    for i, sl in enumerate(data.get("slides",[])):
        c = colors[i % len(colors)]
        icon = icons[i % len(icons)]
        ex = f'<div style="margin-top:14px;background:rgba(255,255,255,0.15);border-radius:8px;padding:10px 14px;font-size:0.9rem;font-style:italic">{sl.get("example","")}</div>' if sl.get("example") else ""
        slides_html += f'''
        <div class="slide" id="slide{sl["id"]}" style="display:none">
            <div style="background:{c};color:white;border-radius:14px;padding:30px 36px;min-height:280px;box-shadow:0 6px 24px rgba(0,0,0,0.15)">
                <div style="font-size:1.8rem;margin-bottom:10px">{icon}</div>
                <div style="font-size:1.15rem;font-weight:700;margin-bottom:14px;opacity:0.85">{sl["title"]}</div>
                <div style="font-size:1rem;line-height:1.75">{sl["body"]}</div>
                {ex}
            </div>
        </div>'''

    html = f'''<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
  body{{margin:0;padding:16px;font-family:Inter,Tajawal,sans-serif;background:#F2EDE6}}
  .header{{text-align:center;margin-bottom:18px}}
  .header h2{{margin:0;font-size:1.1rem;color:#2C1F14}}
  .header p{{margin:4px 0 0;font-size:0.82rem;color:#7A6858}}{lesson_name} · {level} Level
  .dots{{display:flex;justify-content:center;gap:8px;margin:16px 0}}
  .dot{{width:10px;height:10px;border-radius:50%;background:#D8CDBC;transition:background .3s;cursor:pointer}}
  .dot.active{{background:#8D1B3D}}
  .nav{{display:flex;justify-content:space-between;align-items:center;margin-top:16px}}
  .btn{{background:#8D1B3D;color:white;border:none;border-radius:8px;padding:10px 28px;font-size:0.9rem;font-weight:600;cursor:pointer;transition:background .2s}}
  .btn:hover{{background:#6B1530}}
  .btn:disabled{{background:#D8CDBC;cursor:default}}
  .counter{{font-size:0.82rem;color:#7A6858}}
</style>
</head>
<body>
<div class="header">
  <h2>{data.get("title","Interactive Lesson")}</h2>
  <p>{lesson_name} · {level} Level</p>
</div>
{slides_html}
<div class="dots" id="dots"></div>
<div class="nav">
  <button class="btn" id="prevBtn" onclick="move(-1)" disabled>Back</button>
  <span class="counter" id="counter">1 / {len(data.get("slides",[]))}</span>
  <button class="btn" id="nextBtn" onclick="move(1)">Next</button>
</div>
<script>
var cur=0, total={len(data.get("slides",[]))};
var dots=document.getElementById("dots");
for(var i=0;i<total;i++){{var d=document.createElement("span");d.className="dot"+(i==0?" active":"");d.setAttribute("data-i",i);d.onclick=function(){{goTo(+this.getAttribute("data-i"))}};dots.appendChild(d);}}
function show(){{
  for(var i=1;i<=total;i++)document.getElementById("slide"+i).style.display="none";
  document.getElementById("slide"+(cur+1)).style.display="block";
  document.querySelectorAll(".dot").forEach(function(d,i){{d.className="dot"+(i==cur?" active":"")}});
  document.getElementById("counter").textContent=(cur+1)+" / "+total;
  document.getElementById("prevBtn").disabled=cur==0;
  document.getElementById("nextBtn").disabled=cur==total-1;
}}
function move(d){{cur=Math.max(0,Math.min(total-1,cur+d));show();}}
function goTo(i){{cur=i;show();}}
show();
</script>
</body>
</html>'''
    return html

# ─── SESSION STATE ───────────────────────────────────────────
# ─── RAG corpus (built once per session) ────────────────────
import numpy as np

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
    <div style="font-size:2.6rem;line-height:1">🎓</div>
    <div>
        <h1>iCatch &nbsp;<span style="font-weight:300;opacity:0.5">|</span>&nbsp; لحق</h1>
        <p class="tagline">No Student Left Behind</p>
    </div>
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
    if st.button("Teacher Dashboard", type="primary" if st.session_state.view=="teacher" else "secondary", use_container_width=True):
        st.session_state.view = "teacher"
        st.rerun()
with col_s:
    if st.button("Student View", type="primary" if st.session_state.view=="student" else "secondary", use_container_width=True):
        st.session_state.view = "student"
        st.rerun()

st.markdown("---")

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

        # NSIS — immediate display
        level_color = {"Advanced":"#3D6B2C","Intermediate":"#B85C1A","Beginner":"#8D1B3D"}
        lvl = student["level"]
        st.markdown(f"""
        <div class="nsis-panel">
            <div style="font-size:0.78rem;font-weight:700;color:var(--muted);letter-spacing:1px;text-transform:uppercase;margin-bottom:10px">NSIS — Academic Record</div>
            <div style="font-size:1.05rem;font-weight:700;margin-bottom:4px">{selected_student} &nbsp;|&nbsp; {student['arabic_name']}</div>
            <div style="margin-bottom:10px">
                English Average: <b>{student['english_avg']}%</b> &nbsp;
                <span style="background:{level_color[lvl]};color:white;padding:2px 10px;border-radius:12px;font-size:0.8rem;font-weight:700">{lvl} | {student['level_ar']}</span>
            </div>
            <div style="font-size:0.82rem;color:var(--muted)">Recent scores: {' → '.join(map(str,student['recent_grades']))}</div>
        </div>
        """, unsafe_allow_html=True)

        df = pd.DataFrame({"Quiz":[f"Q{i+1}" for i in range(5)],"Score":student['recent_grades']}).set_index("Quiz")
        st.bar_chart(df, color="#8D1B3D", height=160)

    with col_b:
        st.markdown("**Today's Lesson (Qatar Platform)**")
        selected_lesson = st.selectbox("", LESSON_DISPLAY_NAMES, label_visibility="collapsed", key="t_lesson")
        lesson = LESSON_MAP[selected_lesson]

        st.markdown(f"""
        <div class="card card-accent" style="margin-top:12px">
            <div class="card-title">Lesson Posted by Teacher</div>
            <b>Unit:</b> {lesson.get('module','')}<br>
            <b>Type:</b> {lesson['type']}<br>
            <b>Objective:</b> {lesson['objective']}<br>
            <b>Key Rule:</b> <code style="background:#F0E8D8;padding:2px 6px;border-radius:4px;font-size:0.85rem">{lesson['key_rules']}</code>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="alert-absent">
            <b>Absence Detected</b> — {selected_student} ({student['arabic_name']}) was marked absent today.<br>
            Level from NSIS: <b>{student['level']}</b> — Recovery pack will be tailored accordingly.
        </div>
        """, unsafe_allow_html=True)

        if not st.session_state.pack_sent:
            if st.button("Generate and Send Recovery Pack", type="primary", use_container_width=True):
                if not api_key:
                    st.error("Please add your API Key in Settings above.")
                else:
                    with st.spinner("Building knowledge base..."):
                        if not st.session_state.rag_ready:
                            corpus = build_corpus()
                            st.session_state.rag_corpus = embed_corpus(corpus, api_key)
                            st.session_state.rag_ready  = True
                    with st.spinner("Preparing personalised recovery pack..."):
                        st.session_state.lesson_content    = gen_lesson(selected_lesson, lesson, student['level'], api_key)
                        st.session_state.worksheet_content = gen_worksheet(selected_lesson, lesson, student['level'], api_key)
                        st.session_state.quiz_questions    = gen_quiz(selected_lesson, lesson, student['level'], api_key)
                        st.session_state.video_html        = gen_video_lesson(selected_lesson, lesson, student['level'], api_key)
                        st.session_state.pack_sent = True
                    st.rerun()
        else:
            st.markdown("""
            <div style="background:#EDF5E8;border:1px solid #A8CCA0;border-radius:8px;padding:14px 18px;color:#2C5A20;margin-top:8px">
                <b>Recovery pack sent</b> — Student has been notified.<br>
                <small>Includes: Lesson · Worksheet · Quiz · Video Resource</small>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("**Pack Summary**")
            items = ["Personalised micro-lesson (adapted to level)", "Practice worksheet — 3 exercises", "5-question knowledge check quiz", "Video resource sent to student device"]
            for item in items:
                st.markdown(f'<div class="sent-item">&#10003; &nbsp; {item}</div>', unsafe_allow_html=True)

            if st.button("Switch to Student View", type="secondary"):
                st.session_state.view = "student"
                st.rerun()

# ══════════════════════════════════════════════════════════════
#  STUDENT VIEW
# ══════════════════════════════════════════════════════════════
else:
    # Resolve student and lesson from teacher selections
    selected_student = st.session_state.get("t_student", list(STUDENTS.keys())[0])
    selected_lesson  = st.session_state.get("t_lesson",  LESSON_DISPLAY_NAMES[0])
    student = STUDENTS[selected_student]
    lesson  = LESSON_MAP.get(selected_lesson, ALL_LESSONS[0])

    st.markdown(f"""
    <div class="card" style="display:flex;align-items:center;gap:16px;margin-bottom:4px">
        <div>
            <div style="font-size:1.05rem;font-weight:700">{selected_student} &nbsp;|&nbsp; {student['arabic_name']}</div>
            <div style="color:var(--muted);font-size:0.88rem">Grade {student['grade']} · Section {student['section']} · {selected_lesson}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.pack_sent:
        st.info("Your recovery pack will appear here once the teacher sends it.")
    else:
        tab1, tab2, tab3, tab4 = st.tabs(["Lesson", "Worksheet", "Quiz", "Video"])

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
                    st.markdown(f'<div class="quiz-q">Question {i+1}: {q["question"]}</div>', unsafe_allow_html=True)
                    answers[i] = st.radio("", q["options"], key=f"qr_{i}", label_visibility="collapsed")
                st.markdown("---")
                if st.button("Submit", type="primary", key="submit_q"):
                    st.session_state.quiz_answers   = answers
                    st.session_state.quiz_submitted = True
                    st.rerun()

            elif st.session_state.quiz_questions and st.session_state.quiz_submitted:
                questions = st.session_state.quiz_questions
                user_ans  = st.session_state.quiz_answers
                score = 0
                for i, q in enumerate(questions):
                    chosen = user_ans.get(i,"")
                    correct = q["answer"]
                    ok = (chosen == correct)
                    if ok: score += 1
                    if ok:
                        st.markdown(f'<div class="result-correct"><b>Q{i+1}:</b> {q["question"]}<br><small>Your answer: {chosen} — Correct</small></div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="result-wrong"><b>Q{i+1}:</b> {q["question"]}<br><small>Your answer: {chosen}</small><br><small>Correct answer: {correct}</small></div>', unsafe_allow_html=True)

                pct = int(score/len(questions)*100)
                msgs = {5:"Perfect Score!", 4:"Excellent work!", 3:"Good effort — keep practising."}
                msg = msgs.get(score,"Review the lesson and try again.")
                st.markdown(f"""<div class="score-card">
                    <h1>{score} / 5 ({pct}%)</h1>
                    <p>{msg}</p>
                </div>""", unsafe_allow_html=True)
                if st.button("Try Again", key="retry"):
                    st.session_state.quiz_submitted = False
                    st.rerun()

        # ── Video (RAG-powered HTML5 interactive lesson) ──────
        with tab4:
            st.markdown('<div class="section-header">Interactive Lesson</div>', unsafe_allow_html=True)
            if "video_html" not in st.session_state:
                st.session_state.video_html = None
            if st.session_state.video_html:
                import streamlit.components.v1 as components
                components.html(st.session_state.video_html, height=500, scrolling=False)
            else:
                st.caption("Interactive lesson will appear here once the teacher sends the recovery pack.")
