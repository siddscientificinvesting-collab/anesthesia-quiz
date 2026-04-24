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
    "cns": {
        "file": "questions_cns.json",
        "label": "Anesthesia for Central Nervous System Diseases",
        "short": "CNS Diseases",
        "icon": "🧠",
    },
    "hepatic": {
        "file": "questions_hepatic.json",
        "label": "Anesthesia for Hepatic Disease",
        "short": "Hepatic Disease",
        "icon": "🫁",
    },
}

# ─── Load Questions ──────────────────────────────────────────────────────────
@st.cache_data
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
    try:
        sb = get_supabase()
        if sb is not None:
            sb.table("quiz_results").insert(payload).execute()
    except Exception:
        pass
    # Always save locally
    results = _load_local_results()
    results.append(payload)
    _save_local_results(results)
    return True

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
                .limit(20)
                .execute()
            )
            if resp.data:
                return resp.data
    except Exception:
        pass
    # Fallback to local results
    results = _load_local_results()
    results.sort(key=lambda r: (-r.get("percentage", 0), r.get("time_taken_s", 9999)))
    return results[:20]

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
    st.divider()

    for key, info in QUIZ_CATALOG.items():
        c1, c2 = st.columns([4, 1])
        with c1:
            st.markdown(f"### {info['icon']} {info['label']}")
            qdata = load_questions(info['file'])
            topics = sorted(set(q.get('topic', 'General') for q in qdata['questions']))
            st.caption(f"**50 MCQs** | **{qdata['time_limit_minutes']} min** | Topics: {', '.join(topics[:5])}{'...' if len(topics) > 5 else ''}")
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
    save_result(
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
    if not st.session_state.submitted:
        st.warning("No quiz to review. Take the test first!")
        if st.button("◀ Back to Home"):
            st.session_state.page = "home"
            st.rerun()
        return

    st.title("📖 Review Dashboard")

    # ── Summary Stats ─────────────────────────────────────────────────────────
    correct_ids, incorrect_ids, unanswered_ids = [], [], []
    for q in QUESTIONS:
        qid = str(q["id"])
        user_ans = st.session_state.answers.get(qid)
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
        user_ans = st.session_state.answers.get(qid)
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
        user_ans = st.session_state.answers.get(qid)
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
        st.info(f"**Explanation:** {q['explanation']}")

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

            # Expandable answer review for each attempt
            raw_answers = row.get("answers")
            if raw_answers:
                attempt_answers = json.loads(raw_answers) if isinstance(raw_answers, str) else raw_answers

                # Determine which question set this attempt used
                attempt_quiz_id = row.get("quiz_id", "")
                attempt_questions = _resolve_questions_for_attempt(attempt_quiz_id)

                if attempt_questions:
                    with st.expander(f"📖 Review {row['name']}'s answers", expanded=False):
                        correct_count = 0
                        incorrect_count = 0
                        unanswered_count = 0

                        for q in attempt_questions:
                            qid = str(q["id"])
                            user_ans = attempt_answers.get(qid)
                            correct = q["answer"]

                            if user_ans is None:
                                unanswered_count += 1
                                icon = "⬜"
                            elif user_ans == correct:
                                correct_count += 1
                                icon = "✅"
                            else:
                                incorrect_count += 1
                                icon = "❌"

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

                            st.info(f"**Explanation:** {q['explanation']}")

                            ref = q.get("reference", "")
                            if ref:
                                st.markdown(
                                    f'<div class="ref-box">📖 <strong>Reference:</strong> {ref}<br>'
                                    f'<em>Source: Short Textbook of Anesthesia – Ajay Yadav</em></div>',
                                    unsafe_allow_html=True,
                                )
                            st.divider()

                        # Summary at bottom
                        st.markdown(
                            f"**Summary:** ✅ {correct_count} Correct &nbsp;|&nbsp; "
                            f"❌ {incorrect_count} Incorrect &nbsp;|&nbsp; "
                            f"⬜ {unanswered_count} Unanswered"
                        )

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
