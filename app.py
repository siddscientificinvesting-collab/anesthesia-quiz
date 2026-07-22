import streamlit as st
import json
import time
from datetime import datetime, timezone
import os

try:
    from supabase import create_client
    SUPABASE_AVAILABLE = True
except Exception:
    SUPABASE_AVAILABLE = False

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Anesthesia MCQ Quiz",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Available Quizzes ────────────────────────────────────────────────────────
QUIZ_CATALOG = {
    "section2": {
        "file": "questions.json",
        "label": "Section 2 – Equipment in Anesthesia (Ch 2–3)",
        "short": "Equipment (Ch 2–3)",
        "icon": "🔧",
    },
    "section2_v2": {
        "file": "questions_v2.json",
        "label": "Section 2 – Equipment in Anesthesia (Ch 2–3) – Version 2",
        "short": "Equipment V2 (Ch 2–3)",
        "icon": "🔧",
    },
    "ch18": {
        "file": "questions_ch18.json",
        "label": "Chapter 18 – Anesthesia for Cardiovascular Diseases",
        "short": "Cardiovascular (Ch 18)",
        "icon": "❤️",
    },
    "ch19": {
        "file": "questions_ch19.json",
        "label": "Chapter 19 – Anesthesia for Respiratory Diseases",
        "short": "Respiratory (Ch 19)",
        "icon": "🫁",
    },
    "ch40": {
        "file": "questions_ch40.json",
        "label": "Chapter 40 – Intensive Care Management",
        "short": "ICU Management (Ch 40)",
        "icon": "🏥",
    },
    "ch41": {
        "file": "questions_ch41.json",
        "label": "Chapter 41 – Cardiopulmonary & Cerebral Resuscitation",
        "short": "CPR/CPCR (Ch 41)",
        "icon": "🫀",
    },
    "ch20": {
        "file": "questions_ch20.json",
        "label": "Chapter 20 – Anesthesia for CNS Diseases",
        "short": "CNS Diseases (Ch 20)",
        "icon": "🧠",
    },
    "ch21": {
        "file": "questions_ch21.json",
        "label": "Chapter 21 – Anesthesia for Hepatic Diseases",
        "short": "Hepatic Diseases (Ch 21)",
        "icon": "🫁",
    },
    "ch20_v2": {
        "file": "questions_ch20_v2.json",
        "label": "Chapter 20 – CNS Diseases – Version 2",
        "short": "CNS Diseases V2 (Ch 20)",
        "icon": "🧠",
    },
    "ch21_v2": {
        "file": "questions_ch21_v2.json",
        "label": "Chapter 21 – Hepatic Diseases – Version 2",
        "short": "Hepatic Diseases V2 (Ch 21)",
        "icon": "🫁",
    },
    "ch22": {
        "file": "questions_ch22.json",
        "label": "Chapter 22 – Anesthesia for Renal Diseases & Electrolyte Imbalances",
        "short": "Renal & Electrolytes (Ch 22)",
        "icon": "🫘",
    },
    "ch23": {
        "file": "questions_ch23.json",
        "label": "Chapter 23 – Anesthesia for Endocrinal Disorders",
        "short": "Endocrinal Disorders (Ch 23)",
        "icon": "🦋",
    },
    "ch25": {
        "file": "questions_ch25.json",
        "label": "Chapter 25 – Anesthesia for Immune Mediated & Infectious Diseases",
        "short": "Immune & Infectious (Ch 25)",
        "icon": "🛡️",
    },
    "ch4": {
        "file": "questions_ch4.json",
        "label": "Chapter 4 – Preoperative Assessment and Premedication",
        "short": "Preop Assessment (Ch 4)",
        "icon": "📋",
    },
    "ch5": {
        "file": "questions_ch5.json",
        "label": "Chapter 5 – Difficult Airway Management",
        "short": "Difficult Airway (Ch 5)",
        "icon": "🫁",
    },
    "ch6": {
        "file": "questions_ch6.json",
        "label": "Chapter 6 – Monitoring in Anesthesia",
        "short": "Monitoring (Ch 6)",
        "icon": "📊",
    },
    "ch7": {
        "file": "questions_ch7.json",
        "label": "Chapter 7 – Fluids and Blood Transfusion",
        "short": "Fluids & Blood (Ch 7)",
        "icon": "🩸",
    },
    "ch26": {
        "file": "questions_ch26.json",
        "label": "Chapter 26 – Anesthesia for Disorders of Blood",
        "short": "Blood Disorders (Ch 26)",
        "icon": "🩸",
    },
    "ch27": {
        "file": "questions_ch27.json",
        "label": "Chapter 27 – Neurosurgical Anesthesia",
        "short": "Neurosurgical (Ch 27)",
        "icon": "🧠",
    },
    "ch36": {
        "file": "questions_ch36.json",
        "label": "Chapter 36 – Anesthesia for Orthopedics",
        "short": "Orthopedics (Ch 36)",
        "icon": "🦴",
    },
    "ch37": {
        "file": "questions_ch37.json",
        "label": "Chapter 37 – Anesthesia at Remote Locations",
        "short": "Remote Locations (Ch 37)",
        "icon": "🏔️",
    },
    "ch38": {
        "file": "questions_ch38.json",
        "label": "Chapter 38 – Anesthesia for Day-care Surgery",
        "short": "Day-care Surgery (Ch 38)",
        "icon": "🏃",
    },
    "ch35": {
        "file": "questions_ch35.json",
        "label": "Chapter 35 – Anesthesia for Trauma and Burns",
        "short": "Trauma & Burns (Ch 35)",
        "icon": "🔥",
    },
    "ch34": {
        "file": "questions_ch34.json",
        "label": "Chapter 34 – Anesthesia for ENT Surgery",
        "short": "ENT Surgery (Ch 34)",
        "icon": "👂",
    },
    "ch31": {
        "file": "questions_ch31.json",
        "label": "Chapter 31 – Anesthesia for Obese Patients (Bariatric)",
        "short": "Bariatric (Ch 31)",
        "icon": "⚖️",
    },
    "ch32": {
        "file": "questions_ch32.json",
        "label": "Chapter 32 – Anesthesia for Laparoscopy",
        "short": "Laparoscopy (Ch 32)",
        "icon": "🔬",
    },
    "ch30": {
        "file": "questions_ch30.json",
        "label": "Chapter 30 – Geriatric Anesthesia",
        "short": "Geriatric (Ch 30)",
        "icon": "👴",
    },
    "ch29": {
        "file": "questions_ch29.json",
        "label": "Chapter 29 – Pediatric Anesthesia",
        "short": "Pediatric (Ch 29)",
        "icon": "👶",
    },
    "ch1": {
        "file": "questions_ch1.json",
        "label": "new Chapter 1 – Applied Anatomy, Physiology and Physics",
        "short": "new Anatomy/Physiology (Ch 1)",
        "icon": "🫁",
    },
    "ch8": {
        "file": "questions_ch8.json",
        "label": "new Chapter 8 – History of Anesthesia",
        "short": "new History (Ch 8)",
        "icon": "📜",
    },
    "ch9": {
        "file": "questions_ch9.json",
        "label": "new Chapter 9 – Introduction to General Anesthesia",
        "short": "new Intro to GA (Ch 9)",
        "icon": "💉",
    },
    "ch10": {
        "file": "questions_ch10.json",
        "label": "new Chapter 10 – Inhalational Agents",
        "short": "new Inhalational Agents (Ch 10)",
        "icon": "🌬️",
    },
    "ch11": {
        "file": "questions_ch11.json",
        "label": "new Chapter 11 – Gases Used in Anesthesia",
        "short": "new Gases (Ch 11)",
        "icon": "🧪",
    },
    "ch12": {
        "file": "questions_ch12.json",
        "label": "new Chapter 12 – Intravenous Anesthetics",
        "short": "new IV Anesthetics (Ch 12)",
        "icon": "💊",
    },
    "ch13": {
        "file": "questions_ch13.json",
        "label": "new Chapter 13 – Muscle Relaxants",
        "short": "new Muscle Relaxants (Ch 13)",
        "icon": "💪",
    },
    "ch14": {
        "file": "questions_ch14.json",
        "label": "new Chapter 14 – Perioperative Complications of GA",
        "short": "new Perioperative Complications (Ch 14)",
        "icon": "⚠️",
    },
    "ch15": {
        "file": "questions_ch15.json",
        "label": "new Chapter 15 – Local Anesthetics",
        "short": "new Local Anesthetics (Ch 15)",
        "icon": "🧴",
    },
    "ch16": {
        "file": "questions_ch16.json",
        "label": "new Chapter 16 – Peripheral Nerve Blocks",
        "short": "new Peripheral Nerve Blocks (Ch 16)",
        "icon": "🎯",
    },
    "ch17": {
        "file": "questions_ch17.json",
        "label": "new Chapter 17 – Central Neuraxial Blocks (Spinal & Epidural)",
        "short": "new Spinal & Epidural (Ch 17)",
        "icon": "🦴",
    },
    "ch24": {
        "file": "questions_ch24.json",
        "label": "new Chapter 24 – Anesthesia for Neuromuscular Diseases",
        "short": "new Neuromuscular Diseases (Ch 24)",
        "icon": "🧬",
    },
    "ch28": {
        "file": "questions_ch28.json",
        "label": "new Chapter 28 – Anesthesia for Obstetrics",
        "short": "new Obstetrics (Ch 28)",
        "icon": "🤰",
    },
    "ch33": {
        "file": "questions_ch33.json",
        "label": "new Chapter 33 – Anesthesia for Ophthalmic Surgery",
        "short": "new Ophthalmic Surgery (Ch 33)",
        "icon": "👁️",
    },
    "ch39": {
        "file": "questions_ch39.json",
        "label": "new Chapter 39 – Pain Management",
        "short": "new Pain Management (Ch 39)",
        "icon": "🩹",
    },
    "ch1_to_5": {
        "file": "questions_ch1_to_5.json",
        "label": "Chapters 1–5 – Anatomy, Equipment & Airway (Combined)",
        "short": "Combined (Ch 1–5)",
        "icon": "📚",
    },
    "cleaning_sterilization": {
        "file": "questions_cleaning_sterilization.json",
        "label": "Chapter 34 – Cleaning and Sterilization (Dorsch & Dorsch)",
        "short": "Cleaning & Sterilization",
        "icon": "🧹",
    },
    "methods_of_sterilization": {
        "file": "questions_methods_of_sterilization.json",
        "label": "Methods of Sterilization – ORT Textbook (Pages 363–368)",
        "short": "Methods of Sterilization",
        "icon": "🔬",
    },
    "chemical_sterilization": {
        "file": "questions_chemical_sterilization.json",
        "label": "Chemical & New Methods of Sterilization – ORT Textbook (Ch 78–79, Pages 369–374)",
        "short": "Chemical & New Sterilization (Ch 78–79)",
        "icon": "🧪",
    },
    "tables_ch40": {
        "file": "Tables/questions_tables_ch40.json",
        "label": "Chapter 40 – Acid-Base Balance (Tables & Flowcharts)",
        "short": "Acid-Base Tables (Ch 40)",
        "icon": "⚗️",
    },
    "section9_combined": {
        "file": "questions_section9_combined.json",
        "label": "Section 9 – Cardiorespiratory Care (Ch 40–41 + Mixed) [150 Qs]",
        "short": "Cardiorespiratory + Mixed (150Q)",
        "icon": "🫀",
    },
    "keypoints_ch1_to_17": {
        "file": "questions_keypoints_ch1_to_17.json",
        "label": "Key Points – Chapters 1 to 17 (Ajay Yadav) [150 Qs / 90 min]",
        "short": "Key Points Ch 1–17 (150Q)",
        "icon": "🔑",
    },
    "keypoints_all_200": {
        "file": "questions_keypoints_all_chapters_200.json",
        "label": "Key Points – All Chapters Mixed (200 Qs / 90 min)",
        "short": "Key Points All Ch (200Q)",
        "icon": "🔑",
    },
    "ch6_to_12_200": {
        "file": "questions_ch6_to_12_200.json",
        "label": "Chapters 6–12 Mixed (Monitoring, Fluids, History, GA, Inhalational, Gases, IV Anesthetics) [200 Qs / 90 min]",
        "short": "Ch 6–12 Mixed (200Q)",
        "icon": "📖",
    },
    "ch1_to_12_200": {
        "file": "questions_ch1_to_12_200.json",
        "label": "Chapters 1–12 Full Mixed (Anatomy to IV Anesthetics) [200 Qs / 90 min]",
        "short": "Ch 1–12 Full (200Q)",
        "icon": "📘",
    },
    "ch13_to_17_200": {
        "file": "questions_ch13_to_17_200.json",
        "label": "Chapters 13–17 Mixed (Muscle Relaxants, Complications, LA, Nerve Blocks, CNB) [200 Qs / 90 min]",
        "short": "Ch 13–17 (200Q)",
        "icon": "💉",
    },
    "ch18_to_26_200": {
        "file": "questions_ch18_to_26_200.json",
        "label": "Chapters 18–26 Mixed (Anesthesia for Coexisting Diseases) [200 Qs / 90 min]",
        "short": "Ch 18–26 Coexisting (200Q)",
        "icon": "🫀",
    },
    "ch18_to_26_deep_50": {
        "file": "questions_ch18_to_26_deep_50.json",
        "label": "Chapters 18–26 DEEP & TWISTED (Coexisting Diseases – Advanced) [50 Qs / 45 min]",
        "short": "Ch 18–26 Deep (50Q)",
        "icon": "🧠",
    },
    "ch27_to_39_200": {
        "file": "questions_ch27_to_39_200.json",
        "label": "Chapters 27–39 Mixed (Subspecialty Anesthetic Management) [200 Qs / 90 min]",
        "short": "Ch 27–39 Subspecialty (200Q)",
        "icon": "🏥",
    },
    "ch16_ch39_deep_200": {
        "file": "questions_ch16_ch39_deep_200.json",
        "label": "Ch 16 + Ch 39 DEEP (Nerve Blocks & Pain Management) [200 Qs / 90 min]",
        "short": "Nerve Blocks + Pain Deep (200Q)",
        "icon": "🎯",
    },
    "ch15_to_41_part1": {
        "file": "questions_ch15_to_41_part1.json",
        "label": "Chapters 15–41 Part 1 (Regional, Coexisting, Subspecialty, ICU & CPR) [100 Qs / 90 min]",
        "short": "Ch 15–41 Part 1 (100Q)",
        "icon": "📗",
    },
    "ch15_to_41_part2": {
        "file": "questions_ch15_to_41_part2.json",
        "label": "Chapters 15–41 Part 2 (Regional, Coexisting, Subspecialty, ICU & CPR) [100 Qs / 90 min]",
        "short": "Ch 15–41 Part 2 (100Q)",
        "icon": "📕",
    },
    "ch15_to_41_part3": {
        "file": "questions_ch15_to_41_part3.json",
        "label": "Chapters 15–41 Part 3 – TOUGH (Regional, Coexisting, Subspecialty, ICU & CPR) [100 Qs / 90 min]",
        "short": "Ch 15–41 Part 3 TOUGH (100Q)",
        "icon": "🔥",
    },
    "ch15_to_41_part4": {
        "file": "questions_ch15_to_41_part4.json",
        "label": "Chapters 15–41 Part 4 – TOUGH (Regional, Coexisting, Subspecialty, ICU & CPR) [100 Qs / 90 min]",
        "short": "Ch 15–41 Part 4 TOUGH (100Q)",
        "icon": "🔥",
    },
}

# ─── Load Questions ──────────────────────────────────────────────────────────
@st.cache_data(ttl=60)
def load_questions(filename):
    path = os.path.join(os.path.dirname(__file__), filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# Determine active quiz from query parameter
query_params = st.query_params
active_quiz_key = query_params.get("quiz", None)

if active_quiz_key and active_quiz_key in QUIZ_CATALOG:
    quiz_file = QUIZ_CATALOG[active_quiz_key]["file"]
    quiz_data = load_questions(quiz_file)
    QUESTIONS  = quiz_data["questions"]
    TIME_LIMIT = quiz_data["time_limit_minutes"] * 60
    TOTAL_Q    = quiz_data["total_questions"]
    QUIZ_LABEL = QUIZ_CATALOG[active_quiz_key]["label"]
else:
    quiz_data  = None
    QUESTIONS  = []
    TIME_LIMIT = 0
    TOTAL_Q    = 0
    QUIZ_LABEL = ""

# ─── Supabase Client ─────────────────────────────────────────────────────────
@st.cache_resource
def get_supabase():
    try:
        if not SUPABASE_AVAILABLE:
            return None
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except Exception:
        return None

# ─── Session State Init ──────────────────────────────────────────────────────
def init_state():
    defaults = {
        "page":           "home",       # home | quiz | result | review | leaderboard
        "name":           "",
        "answers":        {},
        "start_time":     None,
        "submitted":      False,
        "score":          0,
        "time_taken":     0,
        "current_q":      0,
        "confirm_submit": False,
        "last_result":    None,  # Persists result data across refreshes
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ─── CSS ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.timer-box {
    background: #1e1e2e;
    color: #cba6f7;
    font-size: 2rem;
    font-weight: 700;
    padding: 0.4rem 1.2rem;
    border-radius: 12px;
    display: inline-block;
    margin-bottom: 1rem;
}
.timer-warn { color: #f38ba8 !important; }
.score-card {
    background: linear-gradient(135deg, #1e1e2e, #313244);
    border-radius: 16px;
    padding: 2rem;
    text-align: center;
    margin: 1rem 0;
}
.q-progress { font-size: 0.85rem; color: #888; margin-bottom: 0.5rem; }
div[data-baseweb="radio"] label { font-size: 1rem; }
.ref-box {
    background: #1e1e2e;
    border-left: 4px solid #89b4fa;
    padding: 0.6rem 1rem;
    border-radius: 8px;
    margin: 0.5rem 0 1rem 0;
    font-size: 0.9rem;
    color: #cdd6f4;
}
.review-stat {
    background: linear-gradient(135deg, #1e1e2e, #313244);
    border-radius: 12px;
    padding: 1.2rem;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# ─── Helpers ──────────────────────────────────────────────────────────────────
def elapsed():
    if st.session_state.start_time is None:
        return 0
    return int(time.time() - st.session_state.start_time)

def remaining():
    return max(0, TIME_LIMIT - elapsed())

def fmt_time(secs: int) -> str:
    m, s = divmod(secs, 60)
    return f"{m:02d}:{s:02d}"

def compute_score():
    score = 0
    for q in QUESTIONS:
        user_ans = st.session_state.answers.get(str(q["id"]))
        if user_ans == q["answer"]:
            score += 1
    return score

LOCAL_RESULTS_FILE = os.path.join(os.path.dirname(__file__), "quiz_results.json")

def _load_local_results():
    if os.path.exists(LOCAL_RESULTS_FILE):
        try:
            with open(LOCAL_RESULTS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def _save_local_results(results):
    with open(LOCAL_RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

def save_result(name: str, score: int, time_taken: int, answers: dict):
    payload = {
        "name":         name,
        "score":        score,
        "max_score":    TOTAL_Q,
        "percentage":   round(score / TOTAL_Q * 100, 1),
        "time_taken_s": time_taken,
        "time_limit_s": TIME_LIMIT,
        "answers":      json.dumps(answers),
        "quiz_id":      quiz_data.get("title", active_quiz_key or "unknown") if quiz_data else "unknown",
        "attempted_at": datetime.now(timezone.utc).isoformat(),
    }
    # Save to Supabase if available
    sb_error = None
    try:
        sb = get_supabase()
        if sb is not None:
            sb.table("quiz_results").insert(payload).execute()
        else:
            sb_error = "Supabase client is None (secrets missing or package unavailable)"
    except Exception as e:
        sb_error = str(e)
    # Always save locally
    results = _load_local_results()
    results.append(payload)
    _save_local_results(results)
    return sb_error  # None means success, string means Supabase failed

def get_leaderboard():
    # Try Supabase first
    try:
        sb = get_supabase()
        if sb is not None:
            resp = (
                sb.table("quiz_results")
                .select("name, score, max_score, percentage, time_taken_s, attempted_at, answers, quiz_id")
                .order("percentage", desc=True)
                .order("time_taken_s", desc=False)
                .execute()
            )
            if resp.data:
                return resp.data
    except Exception:
        pass
    # Fallback to local results
    results = _load_local_results()
    results.sort(key=lambda r: (-r.get("percentage", 0), r.get("time_taken_s", 9999)))
    return results

# ════════════════════════════════════════════════════════════════════════════
#  PAGES
# ════════════════════════════════════════════════════════════════════════════

# ─── HOME ────────────────────────────────────────────────────────────────────
def page_home():
    # Landing page: show quiz catalog if no quiz selected
    if not active_quiz_key:
        page_catalog()
        return

    st.title(f"🩺 {QUIZ_LABEL}")
    time_min = quiz_data['time_limit_minutes']
    st.markdown(f"""
**Source:** Short Textbook of Anesthesia – Ajay Yadav  
**Questions:** {TOTAL_Q}  &nbsp;|&nbsp; **Time Limit:** {time_min} minutes  
**Pattern:** CRE-style Single Best Answer (SBA)
    """)
    st.divider()

    name = st.text_input("Enter your name to begin:", placeholder="e.g. Dr. Ramesh")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("▶  Start Test", type="primary", use_container_width=True):
            if not name.strip():
                st.error("Please enter your name.")
            else:
                st.session_state.name       = name.strip()
                st.session_state.start_time = time.time()
                st.session_state.answers    = {}
                st.session_state.submitted  = False
                st.session_state.current_q  = 0
                st.session_state.page       = "quiz"
                st.rerun()
    with col2:
        if st.button("🏆  View Leaderboard", use_container_width=True):
            st.session_state.page = "leaderboard"
            st.rerun()
    with col3:
        if st.button("📚 All Quizzes", use_container_width=True):
            st.query_params.clear()
            st.session_state.page = "home"
            st.rerun()
    # Extra row for All Results
    if st.button("📋 All Results (Admin)", use_container_width=False):
        st.session_state.page = "all_results"
        st.rerun()

    st.divider()
    st.markdown(f"""
**Instructions:**  
1. Answer all {TOTAL_Q} questions before the timer runs out.  
2. You can navigate freely using the sidebar question map.  
3. Click **Submit Test** when done (or it auto-submits when time is up).  
4. Review correct answers with book references after submission.
    """)


# ─── QUIZ CATALOG ─────────────────────────────────────────────────────────────
def page_catalog():
    st.title("🩺 Anesthesia MCQ Quiz Hub")
    st.markdown("""
**Source:** Short Textbook of Anesthesia – Ajay Yadav  
**Pattern:** CRE-style Single Best Answer (SBA)  
**Each test:** 50 Questions | 30 Minutes  

Select a chapter to start your test:
    """)

    col_a, col_b = st.columns([1, 1])
    with col_a:
        if st.button("📋 View All Results", use_container_width=True):
            st.session_state.page = "all_results"
            st.rerun()
    with col_b:
        if st.button("🏆 Leaderboard", use_container_width=True):
            st.session_state.page = "leaderboard"
            st.rerun()

    st.divider()

    for key, info in QUIZ_CATALOG.items():
        c1, c2 = st.columns([4, 1])
        with c1:
            st.markdown(f"### {info['icon']} {info['label']}")
            try:
                qdata = load_questions(info['file'])
                if isinstance(qdata, list):
                    qs = qdata
                    total_qs = len(qs)
                    time_min = 30
                else:
                    qs = qdata.get('questions', qdata) if isinstance(qdata, dict) else qdata
                    total_qs = qdata.get('total_questions', len(qs)) if isinstance(qdata, dict) else len(qs)
                    time_min = qdata.get('time_limit_minutes', 30) if isinstance(qdata, dict) else 30
                chapters = sorted(set(str(q.get('chapter', '')) for q in qs if isinstance(q, dict) and q.get('chapter')))
                st.caption(f"**{total_qs} MCQs** | **{time_min} min** | Chapters: {', '.join(chapters[:8])}{'...' if len(chapters) > 8 else ''}")
            except Exception:
                st.caption("Quiz available")
        with c2:
            link = f"?quiz={key}"
            if st.button(f"▶ Start", key=f"cat_{key}", type="primary", use_container_width=True):
                st.query_params["quiz"] = key
                st.session_state.page = "home"
                # Reset quiz state
                for k in ["answers", "start_time", "submitted", "score", "time_taken", "current_q"]:
                    if k in st.session_state:
                        del st.session_state[k]
                st.rerun()
            st.caption(f"Link: `{link}`")
        st.divider()


# ─── QUIZ ─────────────────────────────────────────────────────────────────────
def page_quiz():
    rem = remaining()

    # Auto-submit when time expires
    if rem == 0 and not st.session_state.submitted:
        st.session_state.submitted = True
        st.session_state.score      = compute_score()
        st.session_state.time_taken = TIME_LIMIT
        save_result(
            st.session_state.name,
            st.session_state.score,
            st.session_state.time_taken,
            st.session_state.answers,
        )
        st.session_state["last_result"] = {
            "name": st.session_state.name,
            "score": st.session_state.score,
            "time_taken": st.session_state.time_taken,
            "answers": dict(st.session_state.answers),
            "quiz_label": QUIZ_LABEL,
            "total_q": TOTAL_Q,
        }
        st.session_state.page = "result"
        st.rerun()

    # ── Top Bar ──────────────────────────────────────────────────────────────
    top_left, top_right = st.columns([3, 1])
    with top_left:
        answered = len(st.session_state.answers)
        st.markdown(f"**{st.session_state.name}** &nbsp;|&nbsp; "
                    f"Answered: **{answered}/{TOTAL_Q}**")
    with top_right:
        warn = "timer-warn" if rem < 300 else ""
        st.markdown(
            f'<div class="timer-box {warn}">⏱ {fmt_time(rem)}</div>',
            unsafe_allow_html=True,
        )

    st.divider()

    # ── Question Navigation Sidebar ──────────────────────────────────────────
    with st.sidebar:
        st.markdown("### Question Map")

        # Filter options for navigation
        filter_nav = st.radio("Show:", ["All", "Unanswered Only", "Answered Only"], horizontal=True, key="nav_filter")

        filtered_indices = []
        for i, q in enumerate(QUESTIONS):
            is_answered = str(q["id"]) in st.session_state.answers
            if filter_nav == "Unanswered Only" and is_answered:
                continue
            if filter_nav == "Answered Only" and not is_answered:
                continue
            filtered_indices.append(i)

        if not filtered_indices:
            st.info("No questions match this filter.")
        else:
            cols = st.columns(5)
            for col_idx, i in enumerate(filtered_indices):
                q_item = QUESTIONS[i]
                is_answered = str(q_item["id"]) in st.session_state.answers
                label = f"{'✅' if is_answered else '⬜'} {i+1}"
                if cols[col_idx % 5].button(label, key=f"nav_{i}", use_container_width=True):
                    st.session_state.current_q = i
                    st.rerun()

    # ── Current Question ──────────────────────────────────────────────────────
    idx = st.session_state.current_q
    q   = QUESTIONS[idx]
    qid = str(q["id"])

    st.markdown(f'<div class="q-progress">Question {idx+1} of {TOTAL_Q}</div>',
                unsafe_allow_html=True)
    st.progress((idx + 1) / TOTAL_Q)
    st.markdown(f"### Q{idx+1}. {q['question']}")

    current_answer = st.session_state.answers.get(qid)
    options        = [f"{k}. {v}" for k, v in q["options"].items()]
    option_keys    = list(q["options"].keys())

    # Find index of current answer - use None for no selection
    default_idx = None
    if current_answer and current_answer in option_keys:
        default_idx = option_keys.index(current_answer)

    choice = st.radio(
        "Select one:",
        options,
        index=default_idx,
        key=f"q_{idx}_{qid}",
    )

    # Save answer on selection
    if choice:
        selected_key = choice.split(".")[0]
        if st.session_state.answers.get(qid) != selected_key:
            st.session_state.answers[qid] = selected_key
            st.rerun()

    st.divider()

    # ── Navigation Buttons ────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns([1, 1, 1, 2])
    with c1:
        if idx > 0:
            if st.button("◀ Previous", use_container_width=True):
                st.session_state.current_q -= 1
                st.rerun()
    with c2:
        if idx < TOTAL_Q - 1:
            if st.button("Next ▶", type="primary", use_container_width=True):
                st.session_state.current_q += 1
                st.rerun()
    with c3:
        # Jump to next unanswered
        next_unanswered = None
        for i in range(idx + 1, TOTAL_Q):
            if str(QUESTIONS[i]["id"]) not in st.session_state.answers:
                next_unanswered = i
                break
        if next_unanswered is None:
            for i in range(0, idx):
                if str(QUESTIONS[i]["id"]) not in st.session_state.answers:
                    next_unanswered = i
                    break
        if next_unanswered is not None:
            if st.button("⏭ Next Unanswered", use_container_width=True):
                st.session_state.current_q = next_unanswered
                st.rerun()
    with c4:
        answered_count = len(st.session_state.answers)
        btn_label = f"✅ Submit ({answered_count}/{TOTAL_Q} answered)"
        if st.button(btn_label, type="primary", use_container_width=True):
            if answered_count < TOTAL_Q:
                st.session_state.confirm_submit = True
            else:
                _do_submit()

        if st.session_state.confirm_submit:
            st.warning(f"You have {TOTAL_Q - answered_count} unanswered questions. Submit anyway?")
            cc1, cc2 = st.columns(2)
            with cc1:
                if st.button("Yes, Submit", type="primary", use_container_width=True):
                    st.session_state.confirm_submit = False
                    _do_submit()
            with cc2:
                if st.button("Cancel", use_container_width=True):
                    st.session_state.confirm_submit = False
                    st.rerun()

    # Timer auto-refresh — runs AFTER full page renders
    time.sleep(1)
    st.rerun()


def _do_submit():
    st.session_state.submitted  = True
    st.session_state.score      = compute_score()
    st.session_state.time_taken = elapsed()
    sb_err = save_result(
        st.session_state.name,
        st.session_state.score,
        st.session_state.time_taken,
        st.session_state.answers,
    )
    if sb_err:
        st.session_state["sb_save_error"] = sb_err
    # Persist result so it survives page refresh
    st.session_state["last_result"] = {
        "name": st.session_state.name,
        "score": st.session_state.score,
        "time_taken": st.session_state.time_taken,
        "answers": dict(st.session_state.answers),
        "quiz_label": QUIZ_LABEL,
        "total_q": TOTAL_Q,
    }
    st.session_state.page = "result"
    st.rerun()


# ─── RESULT ────────────────────────────────────────────────────────────────────
def page_result():
    # Use last_result if session was refreshed
    last = st.session_state.get("last_result")
    if not st.session_state.submitted and last:
        score = last["score"]
        time_taken = last["time_taken"]
        total = last.get("total_q", TOTAL_Q) or TOTAL_Q
    elif st.session_state.submitted:
        score = st.session_state.score
        time_taken = st.session_state.time_taken
        total = TOTAL_Q
    else:
        st.warning("No result to display. Take a test first!")
        if st.button("◀ Back to Home"):
            st.session_state.page = "home"
            st.rerun()
        return

    pct = round(score / total * 100, 1) if total > 0 else 0

    if pct >= 75:
        grade, color = "PASS ✅", "#a6e3a1"
    elif pct >= 50:
        grade, color = "BORDERLINE ⚠️", "#f9e2af"
    else:
        grade, color = "FAIL ❌", "#f38ba8"

    st.title("📊 Your Results")

    # Show Supabase save status
    sb_err = st.session_state.get("sb_save_error")
    if sb_err:
        st.warning(f"⚠️ Result saved locally but Supabase sync failed: {sb_err}")
    else:
        st.success("✅ Result saved successfully.")

    st.markdown(f"""
<div class="score-card">
<h2 style="color:{color};">{grade}</h2>
<h1 style="font-size:3rem; color:white;">{score} / {total}</h1>
<h3 style="color:#cdd6f4;">{pct}%</h3>
<p style="color:#888;">Time taken: {fmt_time(time_taken)}</p>
</div>
    """, unsafe_allow_html=True)

    st.divider()

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("📖 Review Dashboard", use_container_width=True, type="primary"):
            st.session_state.page = "review"
            st.rerun()
    with c2:
        if st.button("🔁 Retake Test", use_container_width=True):
            for key in ["answers", "start_time", "submitted", "score", "time_taken", "current_q"]:
                st.session_state[key] = {} if key == "answers" else (None if key == "start_time" else 0 if key in ["score","time_taken","current_q"] else False)
            st.session_state.page = "home"
            st.rerun()
    with c3:
        if st.button("🏆 View Leaderboard", use_container_width=True):
            st.session_state.page = "leaderboard"
            st.rerun()


# ─── REVIEW DASHBOARD ─────────────────────────────────────────────────────────
def page_review():
    # Allow review if submitted OR if last_result exists (survives refresh)
    last = st.session_state.get("last_result")
    if not st.session_state.submitted and not last:
        st.warning("No quiz to review. Take the test first!")
        if st.button("◀ Back to Home"):
            st.session_state.page = "home"
            st.rerun()
        return

    # Use persisted answers if session refreshed
    review_answers = st.session_state.answers if st.session_state.answers else (last.get("answers", {}) if last else {})

    st.title("📖 Review Dashboard")

    # ── Summary Stats ─────────────────────────────────────────────────────────
    correct_ids, incorrect_ids, unanswered_ids = [], [], []
    for q in QUESTIONS:
        qid = str(q["id"])
        user_ans = review_answers.get(qid)
        if user_ans is None:
            unanswered_ids.append(q["id"])
        elif user_ans == q["answer"]:
            correct_ids.append(q["id"])
        else:
            incorrect_ids.append(q["id"])

    s1, s2, s3, s4 = st.columns(4)
    with s1:
        st.markdown(f'<div class="review-stat"><h2 style="color:#a6e3a1;">✅ {len(correct_ids)}</h2><p>Correct</p></div>', unsafe_allow_html=True)
    with s2:
        st.markdown(f'<div class="review-stat"><h2 style="color:#f38ba8;">❌ {len(incorrect_ids)}</h2><p>Incorrect</p></div>', unsafe_allow_html=True)
    with s3:
        st.markdown(f'<div class="review-stat"><h2 style="color:#f9e2af;">⬜ {len(unanswered_ids)}</h2><p>Unanswered</p></div>', unsafe_allow_html=True)
    with s4:
        pct = round(len(correct_ids) / TOTAL_Q * 100, 1)
        st.markdown(f'<div class="review-stat"><h2 style="color:#89b4fa;">{pct}%</h2><p>Score</p></div>', unsafe_allow_html=True)

    st.divider()

    # ── Filters ───────────────────────────────────────────────────────────────
    fc1, fc2, fc3 = st.columns([1, 1, 1])
    with fc1:
        filter_mode = st.selectbox("Filter by:", ["All Questions", "✅ Correct Only", "❌ Incorrect Only", "⬜ Unanswered Only"])
    with fc2:
        chapters = sorted(set(q.get("chapter", "Unknown") for q in QUESTIONS))
        chapter_filter = st.selectbox("Chapter:", ["All Chapters"] + chapters)
    with fc3:
        topics = sorted(set(q.get("topic", "Unknown") for q in QUESTIONS))
        topic_filter = st.selectbox("Topic:", ["All Topics"] + topics)

    # ── Filter Questions ──────────────────────────────────────────────────────
    filtered = []
    for q in QUESTIONS:
        qid = str(q["id"])
        user_ans = review_answers.get(qid)
        is_correct = user_ans == q["answer"]
        is_unanswered = user_ans is None

        # Filter by answer status
        if filter_mode == "✅ Correct Only" and not is_correct:
            continue
        if filter_mode == "❌ Incorrect Only" and (is_correct or is_unanswered):
            continue
        if filter_mode == "⬜ Unanswered Only" and not is_unanswered:
            continue

        # Filter by chapter
        if chapter_filter != "All Chapters" and q.get("chapter") != chapter_filter:
            continue

        # Filter by topic
        if topic_filter != "All Topics" and q.get("topic") != topic_filter:
            continue

        filtered.append(q)

    st.markdown(f"**Showing {len(filtered)} of {TOTAL_Q} questions**")
    st.divider()

    # ── Render Questions ──────────────────────────────────────────────────────
    for q in filtered:
        qid      = str(q["id"])
        user_ans = review_answers.get(qid)
        correct  = q["answer"]

        if user_ans is None:
            icon, status_color = "⬜", "#f9e2af"
        elif user_ans == correct:
            icon, status_color = "✅", "#a6e3a1"
        else:
            icon, status_color = "❌", "#f38ba8"

        # Question header with chapter/topic badge
        chapter_label = q.get("chapter", "")
        topic_label   = q.get("topic", "")
        st.markdown(
            f"**{icon} Q{q['id']}. {q['question']}**  \n"
            f"<small style='color:#89b4fa;'>📚 {chapter_label} › {topic_label}</small>",
            unsafe_allow_html=True,
        )

        # Options with visual feedback
        for k, v in q["options"].items():
            if k == correct and k == user_ans:
                st.markdown(f"&nbsp;&nbsp;&nbsp;**✅ {k}. {v}** ← Your answer (Correct)")
            elif k == correct:
                st.markdown(f"&nbsp;&nbsp;&nbsp;**✅ {k}. {v}** ← Correct answer")
            elif k == user_ans:
                st.markdown(f"&nbsp;&nbsp;&nbsp;❌ ~~{k}. {v}~~ ← Your answer")
            else:
                st.markdown(f"&nbsp;&nbsp;&nbsp;{k}. {v}")

        # Explanation
        explanation = q.get('explanation', '')
        if explanation:
            st.info(f"**Explanation:** {explanation}")

        # Book Reference
        ref = q.get("reference", "")
        if ref:
            st.markdown(
                f'<div class="ref-box">📖 <strong>Reference:</strong> {ref}<br>'
                f'<em>Source: Short Textbook of Anesthesia – Ajay Yadav</em></div>',
                unsafe_allow_html=True,
            )

        st.divider()

    # ── Navigation ────────────────────────────────────────────────────────────
    bc1, bc2, bc3 = st.columns(3)
    with bc1:
        if st.button("◀ Back to Results", use_container_width=True):
            st.session_state.page = "result"
            st.rerun()
    with bc2:
        if st.button("🔁 Retake Test", use_container_width=True):
            for key in ["answers", "start_time", "submitted", "score", "time_taken", "current_q"]:
                st.session_state[key] = {} if key == "answers" else (None if key == "start_time" else 0 if key in ["score","time_taken","current_q"] else False)
            st.session_state.page = "home"
            st.rerun()
    with bc3:
        if st.button("🏠 Home", use_container_width=True):
            st.session_state.page = "home"
            st.rerun()


# ─── LEADERBOARD ──────────────────────────────────────────────────────────────
def page_leaderboard():
    st.title("🏆 Leaderboard")
    st.markdown("All attempts sorted by score (then fastest time)")

    data = get_leaderboard()
    if not data:
        st.info("No results yet. Be the first to take the test!")
    else:
        for i, row in enumerate(data):
            medal = ["🥇", "🥈", "🥉"][i] if i < 3 else f"#{i+1}"
            attempted = row.get("attempted_at", "")[:10] if row.get("attempted_at") else ""
            st.markdown(
                f"{medal} &nbsp; **{row['name']}** — "
                f"**{row['score']}/{row['max_score']}** ({row['percentage']}%) — "
                f"⏱ {fmt_time(row['time_taken_s'])} — 📅 {attempted}"
            )

            # Expandable answer review for each attempt
            raw_answers = row.get("answers")
            if raw_answers:
                attempt_answers = json.loads(raw_answers) if isinstance(raw_answers, str) else raw_answers

                # Determine which question set this attempt used
                attempt_quiz_id = row.get("quiz_id", "")
                attempt_questions = _resolve_questions_for_attempt(attempt_quiz_id)

                if attempt_questions:
                    with st.expander(f"📖 Review {row['name']}'s answers", expanded=False):
                        # Pre-calculate counts
                        correct_count = 0
                        incorrect_count = 0
                        unanswered_count = 0
                        for q in attempt_questions:
                            qid = str(q["id"])
                            user_ans = attempt_answers.get(qid)
                            if user_ans is None:
                                unanswered_count += 1
                            elif user_ans == q["answer"]:
                                correct_count += 1
                            else:
                                incorrect_count += 1

                        # Summary at top
                        st.markdown(
                            f"**Summary:** ✅ {correct_count} Correct &nbsp;|&nbsp; "
                            f"❌ {incorrect_count} Incorrect &nbsp;|&nbsp; "
                            f"⬜ {unanswered_count} Unanswered"
                        )

                        # Filter inside expander
                        lb_filter = st.radio(
                            "Filter:",
                            ["All", "✅ Correct", "❌ Incorrect", "⬜ Unanswered"],
                            horizontal=True,
                            key=f"lb_filter_{i}",
                        )

                        for q in attempt_questions:
                            qid = str(q["id"])
                            user_ans = attempt_answers.get(qid)
                            correct = q["answer"]

                            if user_ans is None:
                                icon = "⬜"
                                status = "unanswered"
                            elif user_ans == correct:
                                icon = "✅"
                                status = "correct"
                            else:
                                icon = "❌"
                                status = "incorrect"

                            # Apply filter
                            if lb_filter == "✅ Correct" and status != "correct":
                                continue
                            if lb_filter == "❌ Incorrect" and status != "incorrect":
                                continue
                            if lb_filter == "⬜ Unanswered" and status != "unanswered":
                                continue

                            # Question header
                            chapter_label = q.get("chapter", "")
                            topic_label = q.get("topic", "")
                            st.markdown(
                                f"**{icon} Q{q['id']}. {q['question']}**  \n"
                                f"<small style='color:#89b4fa;'>📚 {chapter_label} › {topic_label}</small>",
                                unsafe_allow_html=True,
                            )

                            for k, v in q["options"].items():
                                if k == correct and k == user_ans:
                                    st.markdown(f"&nbsp;&nbsp;&nbsp;**✅ {k}. {v}** ← Your answer (Correct)")
                                elif k == correct:
                                    st.markdown(f"&nbsp;&nbsp;&nbsp;**✅ {k}. {v}** ← Correct answer")
                                elif k == user_ans:
                                    st.markdown(f"&nbsp;&nbsp;&nbsp;❌ ~~{k}. {v}~~ ← Your answer")
                                else:
                                    st.markdown(f"&nbsp;&nbsp;&nbsp;{k}. {v}")

                            explanation = q.get('explanation', '')
                            if explanation:
                                st.info(f"**Explanation:** {explanation}")

                            ref = q.get("reference", "")
                            if ref:
                                st.markdown(
                                    f'<div class="ref-box">📖 <strong>Reference:</strong> {ref}<br>'
                                    f'<em>Source: Short Textbook of Anesthesia – Ajay Yadav</em></div>',
                                    unsafe_allow_html=True,
                                )
                            st.divider()

    st.divider()
    if st.button("◀ Back to Home"):
        st.session_state.page = "home"
        st.rerun()


def _resolve_questions_for_attempt(quiz_id: str):
    """Match a stored quiz_id to the correct question set."""
    for key, info in QUIZ_CATALOG.items():
        try:
            qdata = load_questions(info["file"])
            if qdata.get("title", "") == quiz_id:
                return qdata["questions"]
        except Exception:
            continue
    # Fallback: if active quiz is loaded, use that
    if QUESTIONS:
        return QUESTIONS
    return []


def get_all_results():
    """Fetch ALL results from Supabase (no limit), fallback to local."""
    errors = []
    try:
        sb = get_supabase()
        if sb is not None:
            resp = (
                sb.table("quiz_results")
                .select("name, score, max_score, percentage, time_taken_s, attempted_at, quiz_id")
                .order("attempted_at", desc=True)
                .execute()
            )
            if resp.data:
                return resp.data, None
            else:
                errors.append("Supabase connected but table returned 0 rows.")
        else:
            errors.append("Supabase client is None (secrets missing or supabase package unavailable).")
    except Exception as e:
        errors.append(f"Supabase error: {e}")
    # Fallback to local results
    results = _load_local_results()
    results.sort(key=lambda r: r.get("attempted_at", ""), reverse=True)
    if results:
        return results, None
    return [], "; ".join(errors) if errors else "No data in local file either."


def page_all_results():
    st.title("📋 All Results")
    st.markdown("Complete history of all quiz attempts from day one.")
    st.divider()

    data, error = get_all_results()
    if error:
        st.warning(f"⚠️ Debug info: {error}")
    if not data:
        st.info("No results found yet.")
    else:
        # Summary stats
        total_attempts = len(data)
        unique_users = len(set(r.get("name", "") for r in data))
        avg_pct = sum(r.get("percentage", 0) for r in data) / total_attempts

        c1, c2, c3 = st.columns(3)
        c1.metric("Total Attempts", total_attempts)
        c2.metric("Unique Users", unique_users)
        c3.metric("Avg Score", f"{avg_pct:.1f}%")
        st.divider()

        # Filter by name
        all_names = sorted(set(r.get("name", "Unknown") for r in data))
        selected_name = st.selectbox("Filter by student:", ["All"] + all_names)

        # Filter by quiz
        all_quizzes = sorted(set(r.get("quiz_id", "Unknown") for r in data))
        selected_quiz = st.selectbox("Filter by quiz:", ["All"] + all_quizzes)

        filtered = data
        if selected_name != "All":
            filtered = [r for r in filtered if r.get("name") == selected_name]
        if selected_quiz != "All":
            filtered = [r for r in filtered if r.get("quiz_id") == selected_quiz]

        st.markdown(f"**Showing {len(filtered)} of {total_attempts} records**")
        st.divider()

        # Table view
        for i, row in enumerate(filtered):
            pct = row.get("percentage", 0)
            if pct >= 75:
                grade = "🟢 PASS"
            elif pct >= 50:
                grade = "🟡 BORDERLINE"
            else:
                grade = "🔴 FAIL"

            attempted = row.get("attempted_at", "")[:16].replace("T", " ") if row.get("attempted_at") else "N/A"
            quiz_name = row.get("quiz_id", "Unknown")
            time_str = fmt_time(row.get("time_taken_s", 0))

            st.markdown(
                f"**{i+1}.** {grade} &nbsp; **{row.get('name', 'Unknown')}** — "
                f"**{row.get('score', 0)}/{row.get('max_score', 50)}** ({pct}%) — "
                f"⏱ {time_str} — 📅 {attempted}  \n"
                f"<small style='color:#89b4fa;'>📝 {quiz_name}</small>",
                unsafe_allow_html=True,
            )
            st.divider()

    if st.button("◀ Back to Home"):
        st.session_state.page = "home"
        st.rerun()


# ─── Router ───────────────────────────────────────────────────────────────────
page = st.session_state.page
if page == "home":
    page_home()
elif page == "quiz":
    page_quiz()
elif page == "result":
    page_result()
elif page == "review":
    page_review()
elif page == "leaderboard":
    page_leaderboard()
elif page == "all_results":
    page_all_results()
