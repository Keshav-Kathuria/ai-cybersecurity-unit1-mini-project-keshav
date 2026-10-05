# Cyber Security Threat Detection (CICIDS2017)

```
cyber_threat_project/
├── requirements.txt
├── data/        # put CICIDS2017 CSVs here
└── notebooks/
    ├── 01_setup_validation.ipynb         # Task 1
    ├── 02_ml_threat_classification.ipynb # Task 3 (EDA / Task 2 already done)
    └── 03_ml_vs_dl_comparison.ipynb      # Task 4
```

## Setup
```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
jupyter notebook
```

## Data
Place the CICIDS2017 CSVs in `data/`. If you keep them elsewhere, change `DATA_DIR` in the first code cell of notebooks 02 and 03.
`data/sample_cicids_like.csv` is a synthetic placeholder used only if no real CSVs are found; ignore its (unrealistically perfect) scores.

## Notes
- Label is binarised: BENIGN = normal (0), all attacks = suspicious (1).
- `MAX_ROWS = 200_000` samples the data for speed; set to `None` for the full dataset.
- Notebooks 02 and 03 are self-contained and use the same train/test split settings, so results are comparable.
