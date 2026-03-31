import streamlit as st
import requests
import json
import pandas as pd
from datetime import date

# ─────────────────────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="iCatch | لحق",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────────────────────
#  CSS — Qatar Maroon + Clean Government Design
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;700;900&family=Inter:wght@300;400;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', 'Tajawal', sans-serif; }

/* Header Banner */
.hero-banner {
    background: linear-gradient(135deg, #8D1B3D 0%, #6B1530 60%, #4A0F22 100%);
    color: white;
    padding: 28px 36px;
    border-radius: 16px;
    margin-bottom: 28px;
    display: flex;
    align-items: center;
    gap: 20px;
    box-shadow: 0 8px 32px rgba(141,27,61,0.35);
}
.hero-banner h1 { margin: 0; font-size: 1.9rem; font-weight: 700; }
.hero-banner p  { margin: 4px 0 0 0; opacity: 0.85; font-size: 0.95rem; }
.hero-banner .arabic { font-family: 'Tajawal', sans-serif; font-size: 1.1rem; font-weight: 700; }

/* Platform Card */
.platform-card {
    background: #FFFDF8;
    border: 1px solid #E8D5B7;
    border-left: 5px solid #8D1B3D;
    padding: 20px 24px;
    border-radius: 10px;
    margin: 12px 0;
    font-size: 0.95rem;
    line-height: 1.7;
}

/* Student Card */
.student-card {
    background: linear-gradient(135deg, #F0F4FF 0%, #E8EEF9 100%);
    border: 1px solid #C5D0E8;
    border-radius: 12px;
    padding: 22px 26px;
    margin: 12px 0;
}
.student-card h3 { margin: 0 0 10px 0; color: #1A2340; }

/* Level Badges */
.badge {
    display: inline-block;
    padding: 4px 14px;
    border-radius: 20px;
    font-size: 0.82rem;
    font-weight: 700;
    letter-spacing: 0.3px;
}
.badge-advanced    { background: #1B5E20; color: white; }
.badge-intermediate{ background: #E65100; color: white; }
.badge-beginner    { background: #B71C1C; color: white; }

/* Content Boxes */
.lesson-box {
    background: #FFFEF5;
    border: 1px solid #F0E68C;
    border-top: 4px solid #F9A825;
    border-radius: 10px;
    padding: 24px 28px;
    margin: 12px 0;
    white-space: pre-wrap;
    font-size: 0.96rem;
    line-height: 1.75;
}
.worksheet-box {
    background: #F8FFFE;
    border: 1px solid #B2DFDB;
    border-top: 4px solid #00796B;
    border-radius: 10px;
    padding: 24px 28px;
    margin: 12px 0;
    white-space: pre-wrap;
    font-size: 0.96rem;
    line-height: 1.75;
}

/* Quiz Question */
.quiz-q {
    background: white;
    border: 1px solid #E2E8F0;
    border-radius: 10px;
    padding: 16px 20px;
    margin: 10px 0;
    box-shadow: 0 2px 6px rgba(0,0,0,0.05);
    font-weight: 600;
    color: #1E293B;
}
.result-correct {
    background: #F0FDF4;
    border: 1px solid #86EFAC;
    border-radius: 8px;
    padding: 12px 16px;
    margin: 6px 0;
    color: #15803D;
}
.result-wrong {
    background: #FFF1F2;
    border: 1px solid #FECDD3;
    border-radius: 8px;
    padding: 12px 16px;
    margin: 6px 0;
    color: #BE123C;
}

/* Score Card */
.score-card {
    text-align: center;
    background: linear-gradient(135deg, #8D1B3D, #C2185B);
    color: white;
    border-radius: 16px;
    padding: 30px;
    margin: 20px 0;
    box-shadow: 0 8px 24px rgba(141,27,61,0.3);
}
.score-card h1 { font-size: 3rem; margin: 0; }
.score-card p  { opacity: 0.9; font-size: 1.1rem; margin: 8px 0 0 0; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #F8F5F0;
}

/* Metrics */
[data-testid="stMetric"] {
    background: white;
    border-radius: 10px;
    padding: 14px 18px;
    border: 1px solid #E2E8F0;
    box-shadow: 0 2px 6px rgba(0,0,0,0.04);
}

/* Tab styling */
.stTabs [data-baseweb="tab-list"] { gap: 6px; }
.stTabs [data-baseweb="tab"] {
    border-radius: 8px 8px 0 0;
    font-weight: 600;
    font-size: 0.88rem;
}

/* Buttons */
.stButton > button[kind="primary"] {
    background: #8D1B3D !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    padding: 0.5rem 1.5rem !important;
}
.stButton > button[kind="primary"]:hover {
    background: #6B1530 !important;
    box-shadow: 0 4px 14px rgba(141,27,61,0.4) !important;
}

.alert-absent {
    background: #FFF3E0;
    border: 1px solid #FFB74D;
    border-left: 5px solid #F57C00;
    border-radius: 8px;
    padding: 14px 18px;
    color: #E65100;
    font-weight: 600;
    margin: 12px 0;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
#  SIMULATED NSIS — Student Data
# ─────────────────────────────────────────────────────────────
STUDENTS = {
    "Nour Al-Rashid": {
        "arabic_name": "نور الراشد",
        "grade": 5, "section": "A",
        "english_avg": 88,
        "recent_grades": [85, 90, 87, 88, 91],
        "level": "Intermediate", "level_ar": "متوسط",
        "level_badge": "badge-intermediate"
    },
    "Lina Al-Mansouri": {
        "arabic_name": "لينا المنصوري",
        "grade": 5, "section": "A",
        "english_avg": 62,
        "recent_grades": [58, 65, 60, 62, 64],
        "level": "Beginner", "level_ar": "مبتدئ",
        "level_badge": "badge-beginner"
    },
    "Reem Al-Hajri": {
        "arabic_name": "ريم الهاجري",
        "grade": 5, "section": "A",
        "english_avg": 96,
        "recent_grades": [95, 98, 94, 97, 96],
        "level": "Advanced", "level_ar": "متقدم",
        "level_badge": "badge-advanced"
    },
    "Sara Al-Kuwari": {
        "arabic_name": "سارة الكواري",
        "grade": 5, "section": "B",
        "english_avg": 75,
        "recent_grades": [72, 76, 74, 78, 75],
        "level": "Intermediate", "level_ar": "متوسط",
        "level_badge": "badge-intermediate"
    },
}

# ─────────────────────────────────────────────────────────────
#  SIMULATED QATAR PLATFORM — Lessons
# ─────────────────────────────────────────────────────────────
LESSONS = {
    "Grammar: Present Simple vs Present Continuous": {
        "type": "Grammar 📝",
        "objective": "Distinguish between present simple (habits) and present continuous (now)",
        "key_rule": "I play football every day. (Simple) | I am playing football now. (Continuous)",
        "unit": "Unit 4 — Daily Routines"
    },
    "Grammar: Past Simple (Regular Verbs)": {
        "type": "Grammar 📝",
        "objective": "Form and use past simple tense with regular verbs",
        "key_rule": "Add -ed to the base verb: play→played, walk→walked, study→studied",
        "unit": "Unit 5 — Yesterday's Events"
    },
    "Phonics: Long Vowel Sounds (a_e, i_e, o_e)": {
        "type": "Phonics 🔊",
        "objective": "Recognize and read words with magic-e long vowel pattern",
        "key_rule": "When 'e' comes at the end, the vowel says its name: c-a-ke, b-i-ke, h-o-me",
        "unit": "Unit 3 — Sounds Around Us"
    },
    "Grammar: Adjectives and Comparatives": {
        "type": "Grammar 📝",
        "objective": "Use adjectives to describe and compare people and things",
        "key_rule": "Short adj: add -er (tall→taller) | Long adj: more + adj (beautiful→more beautiful)",
        "unit": "Unit 6 — Describing the World"
    },
    "Vocabulary: School Subjects and Timetable": {
        "type": "Vocabulary 📖",
        "objective": "Learn vocabulary for school subjects and use it in context",
        "key_rule": "Maths, Science, Arabic, Physical Education, Art, Music — in sentences",
        "unit": "Unit 2 — School Life"
    },
}

# ─────────────────────────────────────────────────────────────
#  FREE AI API — Google Gemini Flash
# ─────────────────────────────────────────────────────────────
def call_gemini(prompt: str, api_key: str) -> str:
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"gemini-1.5-flash-latest:generateContent?key={api_key}"
    )
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 2000}
    }
    try:
        r = requests.post(url, json=payload, timeout=40)
        data = r.json()
        if "candidates" in data:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        err = data.get("error", {}).get("message", "Unknown error")
        return f"⚠️ API Error: {err}"
    except Exception as e:
        return f"⚠️ Connection error: {e}"


def generate_mini_lesson(lesson_name, lesson_info, level, api_key) -> str:
    prompt = f"""You are a friendly English teacher for Grade 5 in Qatar.
A student missed today's lesson and needs a short catch-up micro-lesson.

TOPIC: {lesson_name}
TYPE: {lesson_info['type']}
OBJECTIVE: {lesson_info['objective']}
KEY RULE: {lesson_info['key_rule']}
STUDENT LEVEL: {level}

Write a micro-lesson (200-280 words) adapted for a {level} student (age 10-11).

Use EXACTLY this format with these emoji headers:
🎯 Learning Goal
(one clear sentence)

📖 The Rule
(simple explanation — shorter for Beginner, richer for Advanced)

✏️ Examples
(3 example sentences, simple→complex based on level)

💡 Remember This!
(one memorable tip, fun and age-appropriate)

Use warm, encouraging language. English only. No markdown with #."""

    return call_gemini(prompt, api_key)


def generate_worksheet(lesson_name, lesson_info, level, api_key) -> str:
    prompt = f"""You are an English teacher for Grade 5 Qatar primary school.
Create a printed worksheet for a student who missed today's lesson.

TOPIC: {lesson_name}
STUDENT LEVEL: {level}

Include EXACTLY these 3 exercises:

━━━━━━━━━━━━━━━━━━━━━━━
EXERCISE 1: Fill in the Blanks
━━━━━━━━━━━━━━━━━━━━━━━
Write 5 sentences. Each has ONE blank (___) to fill.
Put the word bank at the top of this exercise.

━━━━━━━━━━━━━━━━━━━━━━━
EXERCISE 2: Circle the Correct Answer
━━━━━━━━━━━━━━━━━━━━━━━
Write 4 questions. Each has 3 options (a / b / c).

━━━━━━━━━━━━━━━━━━━━━━━
EXERCISE 3: Write Your Own Sentences
━━━━━━━━━━━━━━━━━━━━━━━
Give 3 prompts. Student writes their own sentences.

Rules:
- Beginner: very short sentences, common words, pictures described in text
- Intermediate: standard Grade 5 difficulty
- Advanced: more complex sentences, variety of contexts
- NO answers provided
- Warm encouraging tone"""

    return call_gemini(prompt, api_key)


def generate_quiz(lesson_name, lesson_info, level, api_key):
    prompt = f"""Create 5 multiple-choice quiz questions for Grade 5 English students in Qatar.

TOPIC: {lesson_name}
OBJECTIVE: {lesson_info['objective']}
STUDENT LEVEL: {level}

Return ONLY a valid JSON array. No markdown, no explanation, no code fences.
Exact format:
[
  {{
    "question": "question text",
    "options": ["option A text", "option B text", "option C text", "option D text"],
    "answer": "option A text"
  }}
]

Rules:
- Exactly 5 questions, 4 options each
- "answer" field must match one option EXACTLY (copy-paste the winning option)
- Adjust difficulty for {level} level
- Keep language appropriate for 10-11 year olds"""

    raw = call_gemini(prompt, api_key).strip()

    # Strip markdown fences if present
    if "```" in raw:
        parts = raw.split("```")
        for p in parts:
            p = p.strip()
            if p.startswith("json"):
                p = p[4:].strip()
            if p.startswith("["):
                raw = p
                break

    # Find JSON array
    start = raw.find("[")
    end   = raw.rfind("]") + 1
    if start != -1 and end > start:
        raw = raw[start:end]

    try:
        return json.loads(raw)
    except Exception:
        return None


# ─────────────────────────────────────────────────────────────
#  HEADER
# ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-banner">
    <div style="font-size:3rem;">🎓</div>
    <div>
        <h1>iCatch &nbsp;<span style="font-weight:300;opacity:0.75">|</span>&nbsp; لحق</h1>
        <span class="arabic">نظام التعافي التعليمي بالذكاء الاصطناعي</span>
        <p>Ministry of Education and Higher Education — State of Qatar &nbsp;|&nbsp; وزارة التربية والتعليم</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ System Settings")

    api_key = st.text_input(
        "🔑 Gemini API Key (Free)",
        type="password",
        help="Get your free key at: aistudio.google.com"
    )
    st.caption("👆 Free at: **aistudio.google.com** | No credit card needed")

    st.markdown("---")
    st.markdown("### 🏫 Session Details")
    st.markdown(f"📅 **{date.today().strftime('%d %B %Y')}**")
    st.markdown("🏫 Amna Mahmoud Aljaida Primary")
    st.markdown("📚 Grade 5 — English Language")

    st.markdown("---")
    st.markdown("### 👤 Absent Student (NSIS)")
    selected_student = st.selectbox("Select Student", list(STUDENTS.keys()))
    student = STUDENTS[selected_student]

    level_color = {
        "Advanced": "#1B5E20",
        "Intermediate": "#E65100",
        "Beginner": "#B71C1C"
    }
    slevel = student["level"]
    st.markdown(
        f"**Level:** <span style='background:{level_color[slevel]};"
        f"color:white;padding:2px 10px;border-radius:12px;font-size:0.82rem'>"
        f"{slevel} | {student['level_ar']}</span>",
        unsafe_allow_html=True
    )
    st.markdown(f"**Avg:** {student['english_avg']}%")

    st.markdown("---")
    st.markdown("### 📋 Today's Lesson")
    selected_lesson = st.selectbox("Lesson (Qatar Platform)", list(LESSONS.keys()))
    lesson = LESSONS[selected_lesson]


# ─────────────────────────────────────────────────────────────
#  MAIN TABS
# ─────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📚 Qatar Platform",
    "👤 Student Profile",
    "📖 Mini Lesson",
    "📝 Worksheet",
    "✅ Quiz"
])

# ══════════════════════════════════════════════════════════════
#  TAB 1 — Qatar Platform
# ══════════════════════════════════════════════════════════════
with tab1:
    st.markdown("## 🌐 Qatar Platform — منصة قطر")
    st.caption("Simulated school management system — Ministry of Education and Higher Education")

    col1, col2, col3 = st.columns(3)
    col1.metric("📅 Date", date.today().strftime("%d/%m/%Y"))
    col2.metric("🏫 School", "Amna Mahmoud")
    col3.metric("📚 Subject", "English Gr. 5")

    st.markdown(f"""
    <div class="platform-card">
        <strong style="font-size:1.05rem;color:#8D1B3D;">📌 Lesson Posted by Teacher Today</strong><br><br>
        <b>Unit:</b> {lesson['unit']}<br>
        <b>Lesson Topic:</b> {selected_lesson}<br>
        <b>Type:</b> {lesson['type']}<br>
        <b>Objective:</b> {lesson['objective']}<br>
        <b>Key Focus:</b> <code>{lesson['key_rule']}</code>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="alert-absent">
        ⚠️ ABSENCE DETECTED — <b>{selected_student}</b> ({student['arabic_name']})
        was marked absent today.<br>
        🤖 System is generating personalised recovery content based on NSIS level:
        <b>{student['level']}</b>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  TAB 2 — Student Profile
# ══════════════════════════════════════════════════════════════
with tab2:
    st.markdown("## 🗃️ NSIS — Student Academic Profile")
    st.caption("National Student Information System — Ministry of Education")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📊 English Avg", f"{student['english_avg']}%")
    col2.metric("🎓 Grade", student['grade'])
    col3.metric("🏫 Section", student['section'])
    col4.metric("📈 Trend", "↑ Stable")

    st.markdown(f"""
    <div class="student-card">
        <h3>👤 {selected_student} &nbsp;|&nbsp; {student['arabic_name']}</h3>
        <b>Assigned Level:</b>
        <span class="badge {student['level_badge']}">
            {student['level']} &nbsp;|&nbsp; {student['level_ar']}
        </span>
        &nbsp;&nbsp;
        <small style="color:#64748B">Classified from last 5 assessment scores</small>
    </div>
    """, unsafe_allow_html=True)

    df = pd.DataFrame({
        "Assessment": [f"Quiz {i+1}" for i in range(5)],
        "Score": student['recent_grades']
    }).set_index("Assessment")
    st.bar_chart(df, color="#8D1B3D", height=220)

    st.info("ℹ️ Level classification: **Advanced** ≥ 90% | **Intermediate** 70–89% | **Beginner** < 70%")

# ══════════════════════════════════════════════════════════════
#  TAB 3 — Mini Lesson
# ══════════════════════════════════════════════════════════════
with tab3:
    st.markdown("## 📖 AI-Generated Mini Lesson")

    st.markdown(f"""
    <div class="platform-card">
        Generating for: <b>{selected_student}</b> &nbsp;|&nbsp;
        Level: <b>{student['level']}</b> &nbsp;|&nbsp;
        Topic: <b>{selected_lesson}</b>
    </div>
    """, unsafe_allow_html=True)

    if "lesson_content" not in st.session_state:
        st.session_state.lesson_content = None

    if st.button("🚀 Generate Mini Lesson", type="primary", key="btn_lesson"):
        if not api_key:
            st.error("🔑 Please enter your Gemini API Key in the sidebar.")
        else:
            with st.spinner("✨ Generating personalised lesson..."):
                content = generate_mini_lesson(
                    selected_lesson, lesson, student['level'], api_key
                )
                st.session_state.lesson_content = content
                st.session_state.lesson_for = (selected_student, selected_lesson)

    if st.session_state.lesson_content:
        st.markdown(
            f'<div class="lesson-box">{st.session_state.lesson_content}</div>',
            unsafe_allow_html=True
        )

# ══════════════════════════════════════════════════════════════
#  TAB 4 — Worksheet
# ══════════════════════════════════════════════════════════════
with tab4:
    st.markdown("## 📝 Practice Worksheet")

    st.markdown(f"""
    <div class="platform-card">
        Student: <b>{selected_student}</b> &nbsp;|&nbsp;
        Level: <b>{student['level']}</b> &nbsp;|&nbsp;
        Topic: <b>{selected_lesson}</b>
    </div>
    """, unsafe_allow_html=True)

    if "worksheet_content" not in st.session_state:
        st.session_state.worksheet_content = None

    if st.button("📄 Generate Worksheet", type="primary", key="btn_worksheet"):
        if not api_key:
            st.error("🔑 Please enter your Gemini API Key in the sidebar.")
        else:
            with st.spinner("📝 Creating personalised worksheet..."):
                content = generate_worksheet(
                    selected_lesson, lesson, student['level'], api_key
                )
                st.session_state.worksheet_content = content

    if st.session_state.worksheet_content:
        st.markdown(
            f'<div class="worksheet-box">{st.session_state.worksheet_content}</div>',
            unsafe_allow_html=True
        )

# ══════════════════════════════════════════════════════════════
#  TAB 5 — Quiz
# ══════════════════════════════════════════════════════════════
with tab5:
    st.markdown("## ✅ Knowledge Check Quiz")

    st.markdown(f"""
    <div class="platform-card">
        Student: <b>{selected_student}</b> &nbsp;|&nbsp;
        Level: <b>{student['level']}</b> &nbsp;|&nbsp;
        5 Questions — Topic: <b>{selected_lesson}</b>
    </div>
    """, unsafe_allow_html=True)

    # Session state init
    for key in ["quiz_questions", "quiz_submitted", "quiz_answers"]:
        if key not in st.session_state:
            st.session_state[key] = None if key != "quiz_submitted" else False

    if st.button("🎯 Generate Quiz", type="primary", key="btn_quiz"):
        if not api_key:
            st.error("🔑 Please enter your Gemini API Key in the sidebar.")
        else:
            with st.spinner("🧠 Building quiz questions..."):
                questions = generate_quiz(
                    selected_lesson, lesson, student['level'], api_key
                )
                if questions:
                    st.session_state.quiz_questions = questions
                    st.session_state.quiz_submitted = False
                    st.session_state.quiz_answers = {}
                else:
                    st.error("Could not parse quiz. Please try again.")

    # ── QUIZ FORM ──
    if st.session_state.quiz_questions and not st.session_state.quiz_submitted:
        questions = st.session_state.quiz_questions
        answers = {}

        st.markdown(f"**📋 {selected_student} — {student['level']} Level Quiz**")
        st.markdown("---")

        for i, q in enumerate(questions):
            st.markdown(
                f'<div class="quiz-q">Q{i+1}. {q["question"]}</div>',
                unsafe_allow_html=True
            )
            answers[i] = st.radio(
                f"q{i}", q["options"],
                key=f"quiz_radio_{i}",
                label_visibility="collapsed"
            )

        st.markdown("---")
        if st.button("✅ Submit Quiz", type="primary", key="submit_quiz"):
            st.session_state.quiz_answers = answers
            st.session_state.quiz_submitted = True
            st.rerun()

    # ── RESULTS ──
    elif st.session_state.quiz_questions and st.session_state.quiz_submitted:
        questions  = st.session_state.quiz_questions
        user_ans   = st.session_state.quiz_answers
        score      = 0

        st.markdown("### 📊 Results")

        for i, q in enumerate(questions):
            chosen  = user_ans.get(i, "")
            correct = q["answer"]
            ok      = (chosen == correct)
            if ok:
                score += 1
                st.markdown(
                    f'<div class="result-correct">✅ <b>Q{i+1}:</b> {q["question"]}<br>'
                    f'<small>Your answer: {chosen}</small></div>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f'<div class="result-wrong">❌ <b>Q{i+1}:</b> {q["question"]}<br>'
                    f'<small>Your answer: {chosen}</small><br>'
                    f'<small>✅ Correct: {correct}</small></div>',
                    unsafe_allow_html=True
                )

        pct = int(score / len(questions) * 100)
        if score == 5:
            msg = "🌟 Perfect Score! Outstanding work!"
        elif score >= 4:
            msg = "🎉 Excellent! Almost there!"
        elif score >= 3:
            msg = "💪 Good effort! A bit more practice needed."
        else:
            msg = "📖 Review the mini lesson and try again — you've got this!"

        st.markdown(f"""
        <div class="score-card">
            <h1>{score}/5 &nbsp; ({pct}%)</h1>
            <p>{msg}</p>
            <p style="opacity:0.75;font-size:0.9rem;">Student: {selected_student} &nbsp;|&nbsp; Level: {student['level']}</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🔄 Try Again", key="retry"):
            st.session_state.quiz_submitted = False
            st.rerun()

    elif not st.session_state.quiz_questions:
        st.info("👆 Click **Generate Quiz** to create 5 personalised questions.")
