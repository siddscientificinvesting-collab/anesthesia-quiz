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
    page_title="Anesthesia Equipment MCQ",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Load Questions ──────────────────────────────────────────────────────────
@st.cache_data
def load_questions():
    path = os.path.join(os.path.dirname(__file__), "questions.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

quiz_data = load_questions()
QUESTIONS    = quiz_data["questions"]
TIME_LIMIT   = quiz_data["time_limit_minutes"] * 60  # seconds
TOTAL_Q      = quiz_data["total_questions"]

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
        "page":        "home",       # home | quiz | result | leaderboard
        "name":        "",
        "answers":     {},
        "start_time":  None,
        "submitted":   False,
        "score":       0,
        "time_taken":  0,
        "current_q":   0,
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

def save_result_to_supabase(name: str, score: int, time_taken: int, answers: dict):
    try:
        sb = get_supabase()
        if sb is None:
            return False
        payload = {
            "name":         name,
            "score":        score,
            "max_score":    TOTAL_Q,
            "percentage":   round(score / TOTAL_Q * 100, 1),
            "time_taken_s": time_taken,
            "time_limit_s": TIME_LIMIT,
            "answers":      json.dumps(answers),
            "quiz_id":      quiz_data.get("title", "anesthesia_section2"),
            "attempted_at": datetime.now(timezone.utc).isoformat(),
        }
        sb.table("quiz_results").insert(payload).execute()
        return True
    except Exception as e:
        st.warning(f"Result saved locally only (DB error: {e})")
        return False

def get_leaderboard():
    try:
        sb = get_supabase()
        if sb is None:
            return []
        resp = (
            sb.table("quiz_results")
            .select("name, score, max_score, percentage, time_taken_s, attempted_at")
            .order("percentage", desc=True)
            .order("time_taken_s", desc=False)
            .limit(20)
            .execute()
        )
        return resp.data
    except Exception as e:
        st.error(f"Could not load leaderboard: {e}")
        return []

# ════════════════════════════════════════════════════════════════════════════
#  PAGES
# ════════════════════════════════════════════════════════════════════════════

# ─── HOME ────────────────────────────────────────────────────────────────────
def page_home():
    st.title("🩺 Anesthesia Equipment MCQ")
    st.markdown(f"""
**Source:** Short Textbook of Anesthesia – Ajay Yadav  
**Section:** Section 2 – Equipment in Anesthesia (Chapters 2–3)  
**Questions:** {TOTAL_Q}  &nbsp;|&nbsp; **Time Limit:** {quiz_data['time_limit_minutes']} minutes  
**Pattern:** CRE-style Single Best Answer (SBA)
    """)
    st.divider()

    name = st.text_input("Enter your name to begin:", placeholder="e.g. Dr. Ramesh")
    col1, col2 = st.columns([1, 2])
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

    st.divider()
    st.markdown("""
**Instructions:**  
1. Answer all 50 questions before the timer runs out.  
2. You can navigate freely using the sidebar question map.  
3. Click **Submit Test** when done (or it auto-submits when time is up).  
4. Review correct answers after submission.
    """)


# ─── QUIZ ─────────────────────────────────────────────────────────────────────
def page_quiz():
    rem = remaining()

    # Auto-submit when time expires
    if rem == 0 and not st.session_state.submitted:
        st.session_state.submitted = True
        st.session_state.score      = compute_score()
        st.session_state.time_taken = TIME_LIMIT
        save_result_to_supabase(
            st.session_state.name,
            st.session_state.score,
            st.session_state.time_taken,
            st.session_state.answers,
        )
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
        cols = st.columns(5)
        for i, q in enumerate(QUESTIONS):
            answered = str(q["id"]) in st.session_state.answers
            label    = f"{'✅' if answered else '⬜'} {i+1}"
            if cols[i % 5].button(label, key=f"nav_{i}", use_container_width=True):
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

    # Find index of current answer
    default_idx = None
    if current_answer and current_answer in option_keys:
        default_idx = option_keys.index(current_answer)

    choice = st.radio(
        "Select one:",
        options,
        index=default_idx,
        key=f"q_{idx}_{qid}",
    )

    if choice:
        selected_key = choice.split(".")[0]
        st.session_state.answers[qid] = selected_key

    st.divider()

    # ── Navigation Buttons ────────────────────────────────────────────────────
    c1, c2, c3 = st.columns([1, 1, 2])
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
        answered_count = len(st.session_state.answers)
        btn_label = f"✅ Submit ({answered_count}/{TOTAL_Q} answered)"
        if st.button(btn_label, type="primary", use_container_width=True):
            if answered_count < TOTAL_Q:
                st.warning(f"You have {TOTAL_Q - answered_count} unanswered questions. Submit anyway?")
                if st.button("Confirm Submit", type="primary"):
                    _do_submit()
            else:
                _do_submit()

    # Timer auto-refresh — runs AFTER full page renders
    time.sleep(1)
    st.rerun()


def _do_submit():
    st.session_state.submitted  = True
    st.session_state.score      = compute_score()
    st.session_state.time_taken = elapsed()
    save_result_to_supabase(
        st.session_state.name,
        st.session_state.score,
        st.session_state.time_taken,
        st.session_state.answers,
    )
    st.session_state.page = "result"
    st.rerun()


# ─── RESULT ────────────────────────────────────────────────────────────────────
def page_result():
    score      = st.session_state.score
    time_taken = st.session_state.time_taken
    pct        = round(score / TOTAL_Q * 100, 1)

    if pct >= 75:
        grade, color = "PASS ✅", "#a6e3a1"
    elif pct >= 50:
        grade, color = "BORDERLINE ⚠️", "#f9e2af"
    else:
        grade, color = "FAIL ❌", "#f38ba8"

    st.title("📊 Your Results")
    st.markdown(f"""
<div class="score-card">
<h2 style="color:{color};">{grade}</h2>
<h1 style="font-size:3rem; color:white;">{score} / {TOTAL_Q}</h1>
<h3 style="color:#cdd6f4;">{pct}%</h3>
<p style="color:#888;">Time taken: {fmt_time(time_taken)}</p>
</div>
    """, unsafe_allow_html=True)

    st.divider()

    # ── Detailed Review ───────────────────────────────────────────────────────
    with st.expander("📖 Review All Answers", expanded=False):
        for q in QUESTIONS:
            qid      = str(q["id"])
            user_ans = st.session_state.answers.get(qid, "Not answered")
            correct  = q["answer"]
            is_ok    = user_ans == correct
            icon     = "✅" if is_ok else "❌"

            st.markdown(f"**{icon} Q{q['id']}. {q['question']}**")
            for k, v in q["options"].items():
                if k == correct and k == user_ans:
                    st.markdown(f"&nbsp;&nbsp;&nbsp;**✅ {k}. {v}** ← Your answer (Correct)")
                elif k == correct:
                    st.markdown(f"&nbsp;&nbsp;&nbsp;**✅ {k}. {v}** ← Correct answer")
                elif k == user_ans:
                    st.markdown(f"&nbsp;&nbsp;&nbsp;❌ ~~{k}. {v}~~ ← Your answer")
                else:
                    st.markdown(f"&nbsp;&nbsp;&nbsp;{k}. {v}")
            st.info(f"**Explanation:** {q['explanation']}")
            st.divider()

    c1, c2 = st.columns(2)
    with c1:
        if st.button("🔁 Retake Test", use_container_width=True, type="primary"):
            for key in ["answers", "start_time", "submitted", "score", "time_taken", "current_q"]:
                st.session_state[key] = {} if key == "answers" else (None if key == "start_time" else 0 if key in ["score","time_taken","current_q"] else False)
            st.session_state.page = "home"
            st.rerun()
    with c2:
        if st.button("🏆 View Leaderboard", use_container_width=True):
            st.session_state.page = "leaderboard"
            st.rerun()


# ─── LEADERBOARD ──────────────────────────────────────────────────────────────
def page_leaderboard():
    st.title("🏆 Leaderboard")
    st.markdown("Top 20 attempts sorted by score (then fastest time)")

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
elif page == "leaderboard":
    page_leaderboard()
