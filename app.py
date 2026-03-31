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
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;700;900&family=Inter:wght@300;400;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', 'Tajawal', sans-serif; }
[data-testid="collapsedControl"] { display: none; }
section[data-testid="stSidebar"] { display: none; }
.hero-banner {
    background: linear-gradient(135deg, #8D1B3D 0%, #6B1530 60%, #4A0F22 100%);
    color: white; padding: 28px 40px; border-radius: 16px; margin-bottom: 24px;
    display: flex; align-items: center; gap: 24px;
    box-shadow: 0 8px 32px rgba(141,27,61,0.3);
}
.hero-banner h1 { margin: 0; font-size: 2rem; font-weight: 700; letter-spacing: -0.5px; }
.hero-banner .sub { font-family: 'Tajawal', sans-serif; font-size: 1.05rem; font-weight: 700; opacity: 0.9; margin: 4px 0 2px 0; }
.hero-banner p { margin: 0; opacity: 0.75; font-size: 0.88rem; }
.control-panel { background: #F8F9FA; border: 1px solid #E2E8F0; border-radius: 12px; padding: 20px 28px; margin-bottom: 24px; }
.platform-card { background: white; border: 1px solid #E8D5B7; border-left: 5px solid #8D1B3D; padding: 20px 24px; border-radius: 10px; margin: 12px 0; font-size: 0.95rem; line-height: 1.8; }
.student-card { background: linear-gradient(135deg, #F0F4FF, #E8EEF9); border: 1px solid #C5D0E8; border-radius: 12px; padding: 22px 26px; margin: 12px 0; }
.badge-advanced { background:#1B5E20; color:white; padding:4px 14px; border-radius:20px; font-size:0.82rem; font-weight:700; }
.badge-intermediate { background:#E65100; color:white; padding:4px 14px; border-radius:20px; font-size:0.82rem; font-weight:700; }
.badge-beginner { background:#B71C1C; color:white; padding:4px 14px; border-radius:20px; font-size:0.82rem; font-weight:700; }
.lesson-box { background: #FFFEF5; border: 1px solid #F0E68C; border-top: 4px solid #F9A825; border-radius: 10px; padding: 26px 30px; margin: 14px 0; white-space: pre-wrap; font-size: 0.97rem; line-height: 1.8; }
.worksheet-box { background: #F8FFFE; border: 1px solid #B2DFDB; border-top: 4px solid #00796B; border-radius: 10px; padding: 26px 30px; margin: 14px 0; white-space: pre-wrap; font-size: 0.97rem; line-height: 1.8; }
.quiz-q { background: white; border: 1px solid #E2E8F0; border-radius: 10px; padding: 16px 20px; margin: 10px 0; box-shadow: 0 2px 6px rgba(0,0,0,0.04); font-weight: 600; color: #1E293B; }
.result-correct { background: #F0FDF4; border: 1px solid #86EFAC; border-radius: 8px; padding: 12px 16px; margin: 6px 0; color: #15803D; }
.result-wrong { background: #FFF1F2; border: 1px solid #FECDD3; border-radius: 8px; padding: 12px 16px; margin: 6px 0; color: #BE123C; }
.score-card { text-align: center; background: linear-gradient(135deg, #8D1B3D, #C2185B); color: white; border-radius: 16px; padding: 32px; margin: 20px 0; box-shadow: 0 8px 24px rgba(141,27,61,0.3); }
.score-card h1 { font-size: 3rem; margin: 0; }
.score-card p { opacity: 0.9; font-size: 1.1rem; margin: 8px 0 0 0; }
.alert-absent { background: #FFF3E0; border: 1px solid #FFB74D; border-left: 5px solid #F57C00; border-radius: 8px; padding: 14px 18px; color: #7C3A00; margin: 12px 0; }
[data-testid="stMetric"] { background: white; border-radius: 10px; padding: 14px 18px; border: 1px solid #E2E8F0; box-shadow: 0 2px 6px rgba(0,0,0,0.04); }
.stButton > button[kind="primary"] { background: #8D1B3D !important; border: none !important; border-radius: 8px !important; font-weight: 600 !important; padding: 0.5rem 2rem !important; }
.stButton > button[kind="primary"]:hover { background: #6B1530 !important; }
.stTabs [data-baseweb="tab-list"] { gap: 6px; }
.stTabs [data-baseweb="tab"] { border-radius: 8px 8px 0 0; font-weight: 600; font-size: 0.88rem; }
</style>
""", unsafe_allow_html=True)

STUDENTS = {
    "Nour Al-Rashid": {"arabic_name":"نور الراشد","grade":5,"section":"A","english_avg":88,"recent_grades":[85,90,87,88,91],"level":"Intermediate","level_ar":"متوسط","level_badge":"badge-intermediate"},
    "Lina Al-Mansouri": {"arabic_name":"لينا المنصوري","grade":5,"section":"A","english_avg":62,"recent_grades":[58,65,60,62,64],"level":"Beginner","level_ar":"مبتدئ","level_badge":"badge-beginner"},
    "Reem Al-Hajri": {"arabic_name":"ريم الهاجري","grade":5,"section":"A","english_avg":96,"recent_grades":[95,98,94,97,96],"level":"Advanced","level_ar":"متقدم","level_badge":"badge-advanced"},
    "Sara Al-Kuwari": {"arabic_name":"سارة الكواري","grade":5,"section":"B","english_avg":75,"recent_grades":[72,76,74,78,75],"level":"Intermediate","level_ar":"متوسط","level_badge":"badge-intermediate"},
}

LESSONS = {
    "Grammar: Present Simple vs Present Continuous": {"type":"Grammar","objective":"Distinguish between present simple (habits) and present continuous (now)","key_rule":"I play football every day. (Simple) | I am playing football now. (Continuous)","unit":"Unit 4 — Daily Routines"},
    "Grammar: Past Simple (Regular Verbs)": {"type":"Grammar","objective":"Form and use past simple tense with regular verbs","key_rule":"Add -ed to the base verb: play→played, walk→walked, study→studied","unit":"Unit 5 — Yesterday's Events"},
    "Phonics: Long Vowel Sounds (a_e, i_e, o_e)": {"type":"Phonics","objective":"Recognize and read words with magic-e long vowel pattern","key_rule":"When e comes at the end, the vowel says its name: cake, bike, home","unit":"Unit 3 — Sounds Around Us"},
    "Grammar: Adjectives and Comparatives": {"type":"Grammar","objective":"Use adjectives to describe and compare people and things","key_rule":"Short adj: add -er (tall to taller) | Long adj: more + adj (beautiful to more beautiful)","unit":"Unit 6 — Describing the World"},
    "Vocabulary: School Subjects and Timetable": {"type":"Vocabulary","objective":"Learn vocabulary for school subjects and use it in context","key_rule":"Maths, Science, Arabic, Physical Education, Art, Music — used in sentences","unit":"Unit 2 — School Life"},
}

def call_gemini(prompt, api_key):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={api_key}"
    payload = {"contents":[{"parts":[{"text":prompt}]}],"generationConfig":{"temperature":0.7,"maxOutputTokens":2000}}
    try:
        r = requests.post(url, json=payload, timeout=40)
        data = r.json()
        if "candidates" in data:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        return "Error: " + data.get("error", {}).get("message", "Unknown error")
    except Exception as e:
        return "Connection error: " + str(e)

def generate_mini_lesson(lesson_name, lesson_info, level, api_key):
    prompt = f"""You are a friendly English teacher for Grade 5 in Qatar.
A student missed today's lesson and needs a short catch-up lesson.

TOPIC: {lesson_name}
TYPE: {lesson_info['type']}
OBJECTIVE: {lesson_info['objective']}
KEY RULE: {lesson_info['key_rule']}
STUDENT LEVEL: {level}

Write a micro-lesson (200-280 words) adapted for a {level} student (age 10-11).

Use EXACTLY this format (plain text, no markdown):
Learning Goal
(one clear sentence)

The Rule
(simple explanation)

Examples
(3 example sentences)

Remember This!
(one memorable tip)"""
    return call_gemini(prompt, api_key)

def generate_worksheet(lesson_name, lesson_info, level, api_key):
    prompt = f"""You are an English teacher for Grade 5 in Qatar.
Create a worksheet for a student who missed today's lesson.

TOPIC: {lesson_name}
STUDENT LEVEL: {level}

Include EXACTLY these 3 exercises (plain text, no markdown):

EXERCISE 1 - Fill in the Blanks
5 sentences with ONE blank each. Include a word bank.

EXERCISE 2 - Circle the Correct Answer
4 questions with 3 options each (a / b / c).

EXERCISE 3 - Write Your Own Sentences
3 prompts for the student.

Adapt difficulty to {level} level. No answers provided."""
    return call_gemini(prompt, api_key)

def generate_quiz(lesson_name, lesson_info, level, api_key):
    prompt = f"""Create 5 multiple-choice questions for Grade 5 English in Qatar.
TOPIC: {lesson_name}
LEVEL: {level}
Return ONLY a valid JSON array, no markdown:
[{{"question":"...","options":["A","B","C","D"],"answer":"A"}}]
Exactly 5 questions, 4 options each. answer must match one option exactly."""
    raw = call_gemini(prompt, api_key).strip()
    if "```" in raw:
        for p in raw.split("```"):
            p = p.strip().lstrip("json").strip()
            if p.startswith("["):
                raw = p
                break
    start, end = raw.find("["), raw.rfind("]") + 1
    if start != -1 and end > start:
        raw = raw[start:end]
    try:
        return json.loads(raw)
    except Exception:
        return None

# ── HERO ──
today_str = date.today().strftime("%d %B %Y")
st.markdown(f"""
<div class="hero-banner">
    <div style="font-size:2.8rem;line-height:1">🎓</div>
    <div>
        <h1>iCatch &nbsp;<span style="font-weight:300;opacity:0.6">|</span>&nbsp; لحق</h1>
        <div class="sub">نظام التعافي التعليمي بالذكاء الاصطناعي</div>
        <p>Ministry of Education and Higher Education — State of Qatar &nbsp;|&nbsp; وزارة التربية والتعليم</p>
    </div>
    <div style="margin-left:auto;text-align:right;opacity:0.7;font-size:0.82rem;line-height:1.8">
        Grade 5 — English Language<br>
        Amna Mahmoud Aljaida Primary<br>
        {today_str}
    </div>
</div>
""", unsafe_allow_html=True)

# ── CONTROL PANEL ──
st.markdown('<div class="control-panel">', unsafe_allow_html=True)
c1, c2, c3 = st.columns([1.2, 1.4, 1.4])
with c1:
    api_key = st.text_input("API Key", type="password", placeholder="Paste Gemini API key...", help="Free at: aistudio.google.com")
with c2:
    selected_student = st.selectbox("Absent Student", list(STUDENTS.keys()))
with c3:
    selected_lesson = st.selectbox("Today's Lesson (Qatar Platform)", list(LESSONS.keys()))
st.markdown('</div>', unsafe_allow_html=True)

student = STUDENTS[selected_student]
lesson  = LESSONS[selected_lesson]

# ── TABS ──
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Qatar Platform", "Student Profile", "Lesson", "Worksheet", "Quiz"])

with tab1:
    st.markdown("## Qatar Platform — منصة قطر")
    st.caption("School management system — Ministry of Education and Higher Education")
    c1, c2, c3 = st.columns(3)
    c1.metric("Date", date.today().strftime("%d/%m/%Y"))
    c2.metric("School", "Amna Mahmoud")
    c3.metric("Subject", "English — Grade 5")
    st.markdown(f"""<div class="platform-card">
        <strong style="font-size:1.05rem;color:#8D1B3D;">Lesson Posted by Teacher Today</strong><br><br>
        <b>Unit:</b> {lesson['unit']}<br>
        <b>Lesson Topic:</b> {selected_lesson}<br>
        <b>Type:</b> {lesson['type']}<br>
        <b>Objective:</b> {lesson['objective']}<br>
        <b>Key Focus:</b> <code>{lesson['key_rule']}</code>
    </div>""", unsafe_allow_html=True)
    st.markdown(f"""<div class="alert-absent">
        <b>Absence Detected</b> — {selected_student} ({student['arabic_name']}) was marked absent today.<br>
        Personalised recovery content is being prepared based on the student's recorded level: <b>{student['level']}</b>
    </div>""", unsafe_allow_html=True)

with tab2:
    st.markdown("## Student Academic Profile — NSIS")
    st.caption("National Student Information System — Ministry of Education")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("English Average", f"{student['english_avg']}%")
    c2.metric("Grade", student['grade'])
    c3.metric("Section", student['section'])
    c4.metric("Trend", "Stable")
    st.markdown(f"""<div class="student-card">
        <b style="font-size:1.05rem">{selected_student} &nbsp;|&nbsp; {student['arabic_name']}</b><br><br>
        <b>Level:</b> <span class="{student['level_badge']}">{student['level']} &nbsp;|&nbsp; {student['level_ar']}</span>
        &nbsp;&nbsp;<span style="color:#64748B;font-size:0.85rem">Classified from last 5 assessment scores</span>
    </div>""", unsafe_allow_html=True)
    df = pd.DataFrame({"Assessment":[f"Quiz {i+1}" for i in range(5)],"Score":student['recent_grades']}).set_index("Assessment")
    st.bar_chart(df, color="#8D1B3D", height=220)
    st.info("Level classification — Advanced: 90% and above | Intermediate: 70–89% | Beginner: below 70%")

with tab3:
    st.markdown("## Today's Lesson")
    st.markdown(f"""<div class="platform-card">
        Student: <b>{selected_student}</b> &nbsp;|&nbsp; Level: <b>{student['level']}</b> &nbsp;|&nbsp; Topic: <b>{selected_lesson}</b>
    </div>""", unsafe_allow_html=True)
    if "lesson_content" not in st.session_state:
        st.session_state.lesson_content = None
    if st.button("Start Lesson", type="primary", key="btn_lesson"):
        if not api_key:
            st.error("Please enter your API Key in the panel above.")
        else:
            with st.spinner("Preparing lesson..."):
                st.session_state.lesson_content = generate_mini_lesson(selected_lesson, lesson, student['level'], api_key)
    if st.session_state.lesson_content:
        st.markdown(f'<div class="lesson-box">{st.session_state.lesson_content}</div>', unsafe_allow_html=True)

with tab4:
    st.markdown("## Practice Worksheet")
    st.markdown(f"""<div class="platform-card">
        Student: <b>{selected_student}</b> &nbsp;|&nbsp; Level: <b>{student['level']}</b> &nbsp;|&nbsp; Topic: <b>{selected_lesson}</b>
    </div>""", unsafe_allow_html=True)
    if "worksheet_content" not in st.session_state:
        st.session_state.worksheet_content = None
    if st.button("Open Worksheet", type="primary", key="btn_worksheet"):
        if not api_key:
            st.error("Please enter your API Key in the panel above.")
        else:
            with st.spinner("Preparing worksheet..."):
                st.session_state.worksheet_content = generate_worksheet(selected_lesson, lesson, student['level'], api_key)
    if st.session_state.worksheet_content:
        st.markdown(f'<div class="worksheet-box">{st.session_state.worksheet_content}</div>', unsafe_allow_html=True)

with tab5:
    st.markdown("## Knowledge Check")
    st.markdown(f"""<div class="platform-card">
        Student: <b>{selected_student}</b> &nbsp;|&nbsp; Level: <b>{student['level']}</b> &nbsp;|&nbsp; 5 Questions — Topic: <b>{selected_lesson}</b>
    </div>""", unsafe_allow_html=True)
    for k in ["quiz_questions","quiz_submitted","quiz_answers"]:
        if k not in st.session_state:
            st.session_state[k] = None if k != "quiz_submitted" else False
    if st.button("Start Quiz", type="primary", key="btn_quiz"):
        if not api_key:
            st.error("Please enter your API Key in the panel above.")
        else:
            with st.spinner("Preparing quiz..."):
                questions = generate_quiz(selected_lesson, lesson, student['level'], api_key)
                if questions:
                    st.session_state.quiz_questions = questions
                    st.session_state.quiz_submitted = False
                    st.session_state.quiz_answers = {}
                else:
                    st.error("Could not load quiz. Please try again.")
    if st.session_state.quiz_questions and not st.session_state.quiz_submitted:
        questions = st.session_state.quiz_questions
        answers = {}
        st.markdown(f"**{selected_student} — {student['level']} Level**")
        st.markdown("---")
        for i, q in enumerate(questions):
            st.markdown(f'<div class="quiz-q">Question {i+1}: {q["question"]}</div>', unsafe_allow_html=True)
            answers[i] = st.radio(f"q{i}", q["options"], key=f"quiz_radio_{i}", label_visibility="collapsed")
        st.markdown("---")
        if st.button("Submit", type="primary", key="submit_quiz"):
            st.session_state.quiz_answers = answers
            st.session_state.quiz_submitted = True
            st.rerun()
    elif st.session_state.quiz_questions and st.session_state.quiz_submitted:
        questions = st.session_state.quiz_questions
        user_ans  = st.session_state.quiz_answers
        score     = 0
        st.markdown("### Results")
        for i, q in enumerate(questions):
            chosen = user_ans.get(i, "")
            correct = q["answer"]
            ok = (chosen == correct)
            if ok:
                score += 1
                st.markdown(f'<div class="result-correct"><b>Q{i+1}:</b> {q["question"]}<br><small>Your answer: {chosen} — Correct</small></div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="result-wrong"><b>Q{i+1}:</b> {q["question"]}<br><small>Your answer: {chosen}</small><br><small>Correct answer: {correct}</small></div>', unsafe_allow_html=True)
        pct = int(score / len(questions) * 100)
        msgs = {5:"Perfect Score! Outstanding work!", 4:"Excellent! Almost perfect.", 3:"Good effort! A bit more practice will help."}
        msg = msgs.get(score, "Review the lesson and try again — keep going!")
        st.markdown(f"""<div class="score-card">
            <h1>{score} / 5 &nbsp; ({pct}%)</h1>
            <p>{msg}</p>
            <p style="opacity:0.7;font-size:0.88rem;margin-top:10px">{selected_student} &nbsp;|&nbsp; {student['level']} Level</p>
        </div>""", unsafe_allow_html=True)
        if st.button("Try Again", key="retry"):
            st.session_state.quiz_submitted = False
            st.rerun()
    else:
        st.caption("Click Start Quiz to begin the 5-question check.")
