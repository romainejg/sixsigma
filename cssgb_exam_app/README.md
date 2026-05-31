# CSSGB Exam App (Streamlit)

A daily scenario-based learning app for **ASQ Six Sigma Green Belt (CSSGB)** preparation.

## Features

- DMAIC-aligned curriculum coverage
- Scenario generation with beginner/intermediate/advanced difficulty
- Free-text answer evaluation across consistent score dimensions
- Tutor feedback with model answers and practical rules of thumb
- Adaptive concept mastery updates in local SQLite
- Local dashboard + review history + curriculum progress view
- Works in deterministic **Mock/Demo mode** when no OpenAI API key is present

## Tech Stack

- Python 3.10+
- Streamlit
- SQLite
- OpenAI Python SDK v1+
- pandas
- python-dotenv

## Project Structure

```text
cssgb_exam_app/
├── app.py
├── config.py
├── requirements.txt
├── .env.example
├── README.md
├── core/
│   ├── __init__.py
│   ├── database.py
│   ├── models.py
│   ├── curriculum.py
│   ├── openai_service.py
│   ├── scenario_generator.py
│   ├── evaluator.py
│   ├── tutor.py
│   ├── adaptive_engine.py
│   └── session_manager.py
├── data/
│   └── app.db
└── prompts/
    ├── __init__.py
    ├── scenario_prompts.py
    ├── evaluation_prompts.py
    └── tutor_prompts.py
```

## Setup

```bash
cd cssgb_exam_app
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
cp .env.example .env
```

Set your API key in `.env`:

```bash
OPENAI_API_KEY=your_key_here
```

## Run

```bash
streamlit run app.py
```

## API Key Resolution

The app checks keys in this order:

1. `os.getenv("OPENAI_API_KEY")`
2. `st.secrets["OPENAI_API_KEY"]`

If no key is found, deterministic Mock mode is used automatically.

## Mock/Demo Mode Behavior

When Mock mode is active, app still runs full flow with deterministic JSON outputs:

- Scenario: Intermediate Measure Phase assembly-line case
- Includes Gage R&R total variance = 32%, Cp = 1.4, Cpk = 0.82
- Evaluation and tutor outputs remain schema-accurate and reproducible

## Curriculum Framework

The curriculum follows five DMAIC pillars with modules and concepts based on CSSGB BoK:

- Define
- Measure
- Analyze
- Improve
- Control

## Adaptive MVP Rules

- If overall score >= 85 twice recently on a concept, mastery increases faster
- If overall score < 70, mastery decreases
- Repeated missed concepts are downgraded and prioritized
- Daily recommendation favors weak concepts and spaced repetition

## Database Notes

- SQLite file auto-created at `data/app.db`
- JSON list/dict fields are serialized with `json.dumps` and loaded with `json.loads`
- Reset is only available in **Settings** and guarded by explicit confirmation checkbox

## Future Extensions

- Better spaced repetition scheduling by concept decay and elapsed days
- Real streak tracking on activity dates
- Structured-output strict JSON schemas for richer validation
- Explainable recommendation traces and scenario deduplication logic
