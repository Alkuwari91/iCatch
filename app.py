import streamlit as st
import requests
import json
import pandas as pd
from datetime import date

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

LESSONS = {
    "Grammar: Present Simple vs Present Continuous": {
        "type":"Grammar",
        "objective":"Distinguish between present simple (habits) and present continuous (now)",
        "key_rule":"I play football every day. (Simple) vs I am playing football now. (Continuous)",
        "unit":"Unit 4 — Daily Routines",
        "video_id":"WlM20KkHFKs"
    },
    "Grammar: Past Simple (Regular Verbs)": {
        "type":"Grammar",
        "objective":"Form and use past simple tense with regular verbs",
        "key_rule":"Add -ed to the base verb: play to played, walk to walked, study to studied",
        "unit":"Unit 5 — Yesterday's Events",
        "video_id":"vFDnJhMGOsU"
    },
    "Phonics: Long Vowel Sounds (a_e, i_e, o_e)": {
        "type":"Phonics",
        "objective":"Recognize and read words with magic-e long vowel pattern",
        "key_rule":"When e comes at the end, the vowel says its name: cake, bike, home",
        "unit":"Unit 3 — Sounds Around Us",
        "video_id":"UBiZuG6AACU"
    },
    "Grammar: Adjectives and Comparatives": {
        "type":"Grammar",
        "objective":"Use adjectives to describe and compare people and things",
        "key_rule":"Short adj: add -er (tall to taller). Long adj: more + adj (beautiful to more beautiful)",
        "unit":"Unit 6 — Describing the World",
        "video_id":"IHAYqJsoeOw"
    },
    "Vocabulary: School Subjects and Timetable": {
        "type":"Vocabulary",
        "objective":"Learn vocabulary for school subjects and use it in context",
        "key_rule":"Maths, Science, Arabic, Physical Education, Art, Music — used in sentences",
        "unit":"Unit 2 — School Life",
        "video_id":"eS4SJL1CleM"
    },
}

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
    prompt = f"""You are a friendly English teacher for Grade 5 in Qatar.
TOPIC: {lesson_name} | TYPE: {lesson_info['type']} | LEVEL: {level}
OBJECTIVE: {lesson_info['objective']}
KEY RULE: {lesson_info['key_rule']}

Write a micro-lesson (200-250 words) for a {level} student age 10-11.
Format (plain text only, no asterisks or hash symbols):

Learning Goal
[one sentence]

The Rule
[explanation adapted to level]

Examples
[3 sentences, simple to complex]

Remember This!
[one memorable tip]"""
    return call_gemini(prompt, api_key)

def gen_worksheet(lesson_name, lesson_info, level, api_key):
    prompt = f"""English teacher, Grade 5 Qatar. TOPIC: {lesson_name} LEVEL: {level}
Create a worksheet (plain text, no asterisks or hash symbols):

EXERCISE 1 - Fill in the Blanks
Word bank: [5 words]
5 sentences with one blank each.

EXERCISE 2 - Circle the Correct Answer
4 questions with options a / b / c

EXERCISE 3 - Write Your Own
3 writing prompts

Adapt to {level} level. No answers given."""
    return call_gemini(prompt, api_key)

def gen_quiz(lesson_name, lesson_info, level, api_key):
    prompt = f"""5 MCQ questions for Grade 5 English Qatar.
TOPIC: {lesson_name} LEVEL: {level}
Return ONLY valid JSON array:
[{{"question":"...","options":["A","B","C","D"],"answer":"A"}}]
5 questions, 4 options, answer must match one option exactly."""
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

# ─── SESSION STATE ───────────────────────────────────────────
defaults = {
    "view":"teacher","api_key":"",
    "lesson_content":None,"worksheet_content":None,
    "quiz_questions":None,"quiz_submitted":False,"quiz_answers":{},
    "pack_sent":False,"selected_student_cache":None
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
        selected_lesson = st.selectbox("", list(LESSONS.keys()), label_visibility="collapsed", key="t_lesson")
        lesson = LESSONS[selected_lesson]

        st.markdown(f"""
        <div class="card card-accent" style="margin-top:12px">
            <div class="card-title">Lesson Posted by Teacher</div>
            <b>Unit:</b> {lesson['unit']}<br>
            <b>Type:</b> {lesson['type']}<br>
            <b>Objective:</b> {lesson['objective']}<br>
            <b>Key Rule:</b> <code style="background:#F0E8D8;padding:2px 6px;border-radius:4px;font-size:0.85rem">{lesson['key_rule']}</code>
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
                    with st.spinner("Preparing personalised recovery pack..."):
                        st.session_state.lesson_content    = gen_lesson(selected_lesson, lesson, student['level'], api_key)
                        st.session_state.worksheet_content = gen_worksheet(selected_lesson, lesson, student['level'], api_key)
                        st.session_state.quiz_questions    = gen_quiz(selected_lesson, lesson, student['level'], api_key)
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
    selected_lesson  = st.session_state.get("t_lesson",  list(LESSONS.keys())[0])
    student = STUDENTS[selected_student]
    lesson  = LESSONS[selected_lesson]

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

        # ── Video ────────────────────────────────────────────
        with tab4:
            st.markdown('<div class="section-header">Video Resource</div>', unsafe_allow_html=True)
            vid_id = lesson.get("video_id","")
            st.markdown(f"""
            <div class="video-card">
                <div class="video-sent-badge">Sent to your device</div>
                <div style="font-weight:700;margin-bottom:6px;color:var(--text)">{selected_lesson}</div>
                <div style="color:var(--muted);font-size:0.88rem;margin-bottom:14px">
                    A short review video covering the key skills from today's lesson.
                </div>
            </div>
            """, unsafe_allow_html=True)
            if vid_id:
                st.components.v1.iframe(f"https://www.youtube.com/embed/{vid_id}", height=340)
