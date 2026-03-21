# Anesthesia MCQ Quiz Hub

**Live App:** _(paste your Streamlit Cloud URL here after deployment)_

## About
- 250 MCQs (50 per chapter) from **Short Textbook of Anesthesia – Ajay Yadav**
- CRE-style Single Best Answer format
- 30-minute countdown timer per test
- **Separate link for each chapter test**
- Enhanced Review Dashboard with book references (Chapter, Section, Page)
- Results saved to Supabase with leaderboard

## Available Tests & Links

| Link | Chapter | Topics |
|------|---------|--------|
| `?quiz=section2` | Section 2 – Equipment (Ch 2–3) | Anesthesia Machine, Circuits, Airway Equipment |
| `?quiz=ch18` | Chapter 18 – Cardiovascular | IHD, Valvular, CHD, Heart Failure, Hypertension |
| `?quiz=ch19` | Chapter 19 – Respiratory | Asthma, COPD, URTI, Tuberculosis, Ventilation |
| `?quiz=ch40` | Chapter 40 – ICU Management | Respiratory Failure, Ventilators, Shock, ARDS |
| `?quiz=ch41` | Chapter 41 – CPR/CPCR | BLS, ACLS, Defibrillation, Drugs, Neonatal CPR |

## Quick Start (Local)

```bash
pip install -r requirements.txt
streamlit run app.py
```

Then visit:
- **Quiz Hub:** http://localhost:8501
- **Chapter 18 Test:** http://localhost:8501/?quiz=ch18
- **Chapter 19 Test:** http://localhost:8501/?quiz=ch19
- **Chapter 40 Test:** http://localhost:8501/?quiz=ch40
- **Chapter 41 Test:** http://localhost:8501/?quiz=ch41

## Features
- ⏱ 30-minute timer per 50 questions
- 📊 Score card with PASS/BORDERLINE/FAIL grading
- 📖 **Review Dashboard** — filter by Correct/Incorrect/Unanswered, by Chapter, by Topic
- 📚 **Book References** — each answer links to Chapter, Section & Page number
- 🏆 Leaderboard via Supabase
- 🔀 Separate test links per chapter

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
