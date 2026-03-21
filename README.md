# 🩺 Anesthesia MCQ Quiz Hub

**Live App:** _(paste your Streamlit Cloud URL here after deployment)_

## About
- **250 MCQs** (50 per chapter) from **Short Textbook of Anesthesia – Ajay Yadav**
- CRE-style Single Best Answer (SBA) format
- 30-minute countdown timer per test
- **Separate link for each chapter test** — share individual chapter URLs
- Enhanced Review Dashboard with book references (Chapter, Section, Page number)
- Leaderboard with expandable answer review for every attempt
- Results saved to Supabase

## Available Tests & Links

| Link | Chapter | Pages | Topics |
|------|---------|-------|--------|
| `?quiz=section2` | Section 2 – Equipment (Ch 2–3) | 32 pages | Anesthesia Machine, Circuits, Airway Equipment |
| `?quiz=ch18` | Chapter 18 – Cardiovascular | 11 pages | IHD, Valvular Diseases, CHD, Heart Failure, Hypertension, Shock |
| `?quiz=ch19` | Chapter 19 – Respiratory | 4 pages | Asthma, COPD, URTI, Tuberculosis, Ventilation Principles |
| `?quiz=ch40` | Chapter 40 – ICU Management | 22 pages | Respiratory Failure, Ventilators, Shock, ARDS, Sepsis |
| `?quiz=ch41` | Chapter 41 – CPR/CPCR | 35 pages | BLS, ACLS, Defibrillation, Drugs, Neonatal/Pediatric CPR |

## Features
- 🏠 **Quiz Hub** — landing page listing all 5 chapter tests
- ⏱ **30-minute timer** per 50 questions
- 📊 **Score Card** — PASS (≥75%) / BORDERLINE (50–74%) / FAIL (<50%) grading
- 📖 **Review Dashboard** — filter by ✅ Correct / ❌ Incorrect / ⬜ Unanswered, by Chapter, by Topic
- 📚 **Book References** — every question links to Chapter, Section & Page number from the textbook
- 🏆 **Leaderboard** — top 20 attempts with expandable answer review per attempt
- 🔀 **Separate URLs** — each chapter has its own link for easy sharing

## Quick Start (Local)

```bash
pip install -r requirements.txt
streamlit run app.py
```

Then visit:
- **Quiz Hub:** http://localhost:8501
- **Equipment (Ch 2–3):** http://localhost:8501/?quiz=section2
- **Cardiovascular (Ch 18):** http://localhost:8501/?quiz=ch18
- **Respiratory (Ch 19):** http://localhost:8501/?quiz=ch19
- **ICU Management (Ch 40):** http://localhost:8501/?quiz=ch40
- **CPR/CPCR (Ch 41):** http://localhost:8501/?quiz=ch41

## Deploy to Streamlit Cloud

1. Push this repo to GitHub
2. Go to [streamlit.io/cloud](https://streamlit.io/cloud) → New App
3. Select this repo → `app.py`
4. Add Secrets (Settings → Secrets):
```toml
SUPABASE_URL = "https://YOUR_PROJECT_ID.supabase.co"
SUPABASE_KEY = "YOUR_SUPABASE_ANON_KEY"
```

## Supabase Setup

Run this SQL in your Supabase SQL Editor:

```sql
CREATE TABLE quiz_results (
  id            bigserial PRIMARY KEY,
  name          text NOT NULL,
  score         int  NOT NULL,
  max_score     int  NOT NULL,
  percentage    float NOT NULL,
  time_taken_s  int  NOT NULL,
  time_limit_s  int  NOT NULL,
  answers       jsonb,
  quiz_id       text,
  attempted_at  timestamptz DEFAULT now()
);

-- Allow anonymous inserts (for Streamlit app)
ALTER TABLE quiz_results ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Allow insert" ON quiz_results FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow select" ON quiz_results FOR SELECT USING (true);
```

## Project Structure

```
anesthesia_quiz/
├── app.py                  # Main Streamlit app (multi-chapter quiz hub)
├── questions.json          # Section 2 – Equipment (Ch 2–3) — 50 MCQs
├── questions_ch18.json     # Chapter 18 – Cardiovascular — 50 MCQs
├── questions_ch19.json     # Chapter 19 – Respiratory — 50 MCQs
├── questions_ch40.json     # Chapter 40 – ICU Management — 50 MCQs
├── questions_ch41.json     # Chapter 41 – CPR/CPCR — 50 MCQs
├── requirements.txt        # Python dependencies
└── README.md
```
