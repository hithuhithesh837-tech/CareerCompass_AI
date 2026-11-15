# CareerCompass AI — upgraded starter project

A Streamlit career-exploration app with a consolidated premium theme, skill-based recommendations, category-interest weighting, a searchable career library, and PDF/CSV exports.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate  # macOS / Linux
pip install -r requirements.txt
streamlit run app.py
```

## Project structure

```text
CareerCompass_AI_Upgrade/
├── app.py
├── requirements.txt
├── README.md
├── data/
│   └── career_data.csv
└── utils/
    └── recommender.py
```

## How the fit score works

The displayed fit score is a heuristic, not an employment probability. It combines skill coverage (80% of the skill score) and Jaccard skill overlap (20%). When category interests are selected, the skill score contributes 90% and a matching category contributes the remaining 10%.

## Dataset

The included `data/career_data.csv` contains the 15 career paths supplied for the original project.
