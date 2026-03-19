# Anesthesia Equipment MCQ – Section 2

**Live App:** _(paste your Streamlit Cloud URL here after deployment)_

## About
- 50 MCQs from **Short Textbook of Anesthesia – Ajay Yadav**
- Section 2: Equipment in Anesthesia (Chapters 2–3)
- CRE-style Single Best Answer format
- 60-minute countdown timer
- Results saved to Supabase with leaderboard

## Quick Start (Local)

```bash
pip install -r requirements.txt
streamlit run app.py
```

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

## Topics Covered (Section 2)
- Anesthesia Machine (High/Intermediate/Low pressure systems)
- Rotameter, Vaporizers, Safety features
- Breathing Circuits (Mapleson A–F, closed/circle system)
- CO₂ absorbents (sodalime, barylime, Amsorb)
- Airway equipment (LMA, I-gel, laryngoscopes, airways)
- Machine checking procedures
- Oxygen delivery systems, humidification
