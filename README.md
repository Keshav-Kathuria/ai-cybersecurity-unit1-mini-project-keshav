# Cyber Security Threat Detection with Machine Learning and Deep Learning (CICIDS2017)
| Name | Roll No | 
|---|---|
| Keshav Kathuria | 2301730348

Detecting malicious network traffic from flow-level features. This project classifies network flows from the **CICIDS2017** dataset as **normal** or **suspicious**, using machine learning baselines and a small neural network (MLP). It then compares the approaches on detection quality, training time and practical feasibility.

---

## Table of contents

1. [Project overview](#1-project-overview)
2. [Repository structure](#2-repository-structure)
3. [Dataset](#3-dataset)
4. [Setup and installation](#4-setup-and-installation)
5. [How to run](#5-how-to-run)
6. [Methodology](#6-methodology)
7. [Results](#7-results)
8. [Key findings and discussion](#8-key-findings-and-discussion)
9. [Limitations and future work](#9-limitations-and-future-work)
10. [Reproducibility notes](#10-reproducibility-notes)
11. [Tech stack](#11-tech-stack)
12. [Acknowledgements and citation](#12-acknowledgements-and-citation)

---

## 1. Project overview

| Task | Description | Where |
|---|---|---|
| 1. Environment setup | Project structure, virtual environment, `requirements.txt`, setup validation | `requirements.txt`, notebook Part 1 |
| 2. Threat landscape analysis | Exploratory data analysis of the traffic: suspicious activity, feature distributions, normal vs attack behavior | `notebooks/EDA.py` |
| 3. ML-based threat classification | Preprocessing, Logistic Regression and Decision Tree, evaluation with accuracy, precision, recall, F1, ROC and PR curves | notebook Parts 2 and 3 |
| 4. Introduction to deep learning | MLP neural network compared with the ML models on training time, detection accuracy and feasibility | notebook Part 4 |

**Problem framing:** binary classification. The original `Label` column is converted to `0 = normal (BENIGN)` and `1 = suspicious (any attack type)`. Per-attack-type detection rates are reported separately so that weak spots on rare attacks are not hidden by the overall score.

---

## 2. Repository structure

```
.
├── data/
│   └── cicids2017_cleaned.csv          # CICIDS2017 flow data (see Dataset section)
├── notebooks/
│   ├── cyber_threat_classification.ipynb   # main notebook: setup, preprocessing, ML, DL comparison
│   └── EDA.py                              # exploratory data analysis
├── README.md
└── requirements.txt
```

---

## 3. Dataset

**CICIDS2017** (Canadian Institute for Cybersecurity, University of New Brunswick) contains realistic benign traffic and common attacks, captured as network flows with 78 numeric features extracted by CICFlowMeter, plus a `Label` column.

**Feature groups (examples):**

- Flow basics: `Destination Port`, `Flow Duration`, `Flow Bytes/s`, `Flow Packets/s`
- Packet counts and lengths: `Total Fwd Packets`, `Total Backward Packets`, `Fwd Packet Length Mean`, `Packet Length Std`, ...
- Inter-arrival times: `Flow IAT Mean`, `Fwd IAT Total`, `Bwd IAT Max`, ...
- TCP flags: `SYN Flag Count`, `ACK Flag Count`, `RST Flag Count`, `PSH Flag Count`, ...
- Window, segment and subflow statistics: `Init_Win_bytes_forward`, `Subflow Fwd Bytes`, `min_seg_size_forward`, ...
- Activity and idle times: `Active Mean`, `Idle Mean`, `Idle Max`, ...

**Traffic classes:** `BENIGN`, `DoS Hulk`, `DDoS`, `PortScan`, `DoS GoldenEye`, `FTP-Patator`, `SSH-Patator`, `DoS slowloris`, `DoS Slowhttptest`, `Bot`, `Web Attack - Brute Force`, `Web Attack - XSS`, `Web Attack - Sql Injection`, `Infiltration`, `Heartbleed`.

**Data notes**

- The raw CICIDS2017 files have stray spaces in column names and contain `inf` and `NaN` values (for example in `Flow Bytes/s`). The notebook cleans these on load.
- The dataset is **heavily imbalanced**: benign flows dominate, and some attack types (Infiltration, Heartbleed, SQL injection) have only a handful of samples.
- If the CSV is larger than 100 MB, GitHub will reject it. In that case add it to `.gitignore` or use Git LFS, and tell users to download it and place it in `data/`.
- Download and documentation: https://www.unb.ca/cic/datasets/ids-2017.html

---

## 4. Setup and installation

**Requirements:** Python 3.9 or newer.

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd <your-repo-folder>

# 2. Create a virtual environment
python -m venv venv

# 3. Activate it
#    Windows (PowerShell / cmd):
venv\Scripts\activate
#    macOS / Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Start Jupyter
jupyter notebook
```

`requirements.txt` contains: `numpy`, `pandas`, `scikit-learn`, `matplotlib`, `seaborn`, `jupyter`.

---

## 5. How to run

1. Make sure the dataset CSV is inside `data/`.
2. Open `notebooks/cyber_threat_classification.ipynb`.
3. In the **Part 2** cell, check the settings:
   - `DATA_DIR = "../data"`: folder containing the CSV files (all CSVs in it are concatenated).
   - `MAX_ROWS = 200_000`: random sample size for speed. Set to `None` to use the full dataset (needs more RAM and time).
4. Run all cells from top to bottom (**Kernel > Restart & Run All**).
5. Re-running an individual model cell is safe: results are replaced, not duplicated.

The notebook is organized as follows:

| Part | Content |
|---|---|
| 1 | Environment setup validation (package versions, tiny sanity model) |
| 2 | Data loading, cleaning, preprocessing, stratified train/test split, plotting helpers |
| 3 | ML classification: Logistic Regression and Decision Tree with detailed evaluation |
| 4 | Neural network (MLP) vs ML: performance, training time, inference time, analysis |

`notebooks/EDA.py` contains the exploratory data analysis (threat indicators, distribution of attack-related features, normal vs suspicious behavior).

---

## 6. Methodology

### 6.1 Preprocessing

| Step | Method |
|---|---|
| Cleaning | Strip spaces from column names, replace `inf` / `-inf` with `NaN` |
| Target | `is_attack = 0` if `Label == BENIGN`, else `1` |
| Missing values | Median imputation (`SimpleImputer`) |
| Categorical encoding | `Destination Port` is bucketed into `well_known` (0-1023), `registered` (1024-49151) and `dynamic` (49152-65535), then one-hot encoded. Raw port numbers are kept as a numeric feature as well |
| Normalization | `StandardScaler` on numeric features |
| Split | Stratified 75% train / 25% test, `random_state=42` |
| Leakage control | The preprocessing is **fit on the training split only**, then applied to the test split |

### 6.2 Models

| Model | Configuration |
|---|---|
| Logistic Regression | `max_iter=1000`, `class_weight="balanced"` |
| Decision Tree | `max_depth=12`, `class_weight="balanced"`, `random_state=42` |
| Neural Network (MLP) | `MLPClassifier`, hidden layers (64, 32), `early_stopping=True`, `max_iter=200`, `random_state=42` (about 6.8k trainable parameters) |

The MLP trains for up to 200 epochs but stops early once the validation score stops improving for 10 consecutive epochs. The actual number of epochs used is printed in the notebook (`Stopped after N epochs`).

### 6.3 Evaluation

- **Metrics:** accuracy, precision, recall, F1-score, ROC AUC, precision-recall AUC (average precision)
- **Plots:** metrics comparison, confusion matrices (counts and normalized), ROC and precision-recall curves, predicted-score distributions per class, **recall per attack type**, Logistic Regression coefficients, Decision Tree feature importance, a depth-3 tree visualization, F1 vs tree depth (under/over-fitting), model learning curve for the MLP
- **Feasibility comparison:** training time and inference time (ms per 1,000 flows) for each model
- **Feature correlation analysis:** Spearman correlation of features with the attack label, heatmap of the most label-correlated features, and a list of near-duplicate feature pairs (|corr| >= 0.95)

---

## 7. Results

The numbers below come from a run on the cleaned CICIDS2017 data with the default settings. They will change slightly with the sample size, random seed and split.

### 7.1 Model comparison

| Metric | Result |
|---|---|
| Best model by F1 | **Decision Tree**, F1 = 0.9889 |
| MLP F1 | about 0.9833 (0.0056 below the Decision Tree) |
| MLP training time | 8.3x the Decision Tree and 14.2x Logistic Regression |
| MLP size | 6,849 trainable parameters |

The full table (accuracy, precision, recall, F1, ROC AUC, PR AUC, training time, inference time) is produced by the notebook and saved in the executed cell outputs.

### 7.2 Detection rate (recall) per attack type

Share of each attack type that was correctly flagged as suspicious on the test split. `n` is the number of test flows of that type.

| Attack type | n | Logistic Regression | Decision Tree |
|---|---:|---:|---:|
| Web Attack - Sql Injection | 2 | 0.000 | 0.000 |
| SSH-Patator | 57 | 0.018 | 1.000 |
| Web Attack - Brute Force | 23 | 0.043 | 0.870 |
| Web Attack - XSS | 14 | 0.143 | 1.000 |
| Bot | 49 | 0.245 | 0.531 |
| FTP-Patator | 115 | 0.722 | 0.974 |
| DoS slowloris | 108 | 0.778 | 0.935 |
| DoS Slowhttptest | 99 | 0.798 | 0.889 |
| DoS GoldenEye | 227 | 0.881 | 0.938 |
| PortScan | 1782 | 0.990 | 0.998 |
| DoS Hulk | 3502 | 0.996 | 0.998 |
| DDoS | 2455 | 0.999 | 0.999 |

Averaged equally across the 12 attack types, recall is about **84% for the Decision Tree** and about **55% for Logistic Regression**, much lower than the headline accuracy of around 99%.

---

## 8. Key findings and discussion

1. **The Decision Tree is the best overall model here.** It has the highest F1, trains fastest of the non-linear models, and is interpretable through feature importances and readable rules.
2. **The neural network does not beat the tree on this data.** The 0.56-point F1 gap is small and within what a different seed or split could change, but the MLP also costs 8 to 14 times more training time. Network-flow features are tabular, with threshold-like decision rules and heavily skewed values, which suits tree models well. A small untuned MLP has to approximate those rules.
3. **High accuracy hides weak spots.** About 99% accuracy is driven by three high-volume attack types (DDoS, DoS Hulk, PortScan) that are almost trivially detected. Rare attacks are much harder, with Bot at about 53% recall for the tree and web attacks and SSH-Patator near zero for Logistic Regression.
4. **Linear models are not enough for rare attacks.** Logistic Regression misses most low-volume attacks because they are not linearly separable from normal traffic.
5. **Redundant features exist.** CICIDS2017 contains many highly correlated or duplicated features (for example `Fwd Header Length` appears twice and `Subflow Fwd Packets` equals `Total Fwd Packets`). This makes Logistic Regression coefficients less reliable, because correlated features share credit.
6. **Practical feasibility.** For a deployed intrusion detection system on tabular flow features, tree-based models offer the best trade-off of accuracy, speed, simplicity of retraining and explainability to a security analyst. Neural networks become attractive with very large datasets, raw packet or sequential inputs, or when many weak signals must be combined.

### Caveats on the high scores

- Random train/test splits on CICIDS2017 can place near-identical flows (the same attack tool run repeatedly) on both sides, which inflates scores.
- Features such as `Destination Port` and `Init_Win_bytes_*` act as shortcuts for some attacks (for example a perfect SSH-Patator score likely reflects port 22).
- Very small classes (SQL injection n=2, XSS n=14) give unstable recall values. One flow changes the result by several percentage points.

---

## 9. Limitations and future work

- Run sanity checks on the high scores: remove duplicate rows before splitting, retrain without `Destination Port`, compare against a majority-class baseline.
- Use a **time-based or group-based split** instead of a random split to better estimate real-world performance.
- Apply `log1p` transforms to skewed features and tune the MLP (width, depth, regularization, learning rate); average results over several seeds.
- Add stronger models such as Random Forest and gradient boosting, and report cross-validated scores.
- Address class imbalance explicitly (resampling, cost-sensitive learning) and report macro-averaged metrics.
- Move from binary detection to **multi-class** attack classification.
- Try a Keras/PyTorch network, and sequence models on raw flows or packets.

---

## 10. Reproducibility notes

- All models and the train/test split use `random_state=42`.
- The split is stratified on the binary label.
- `MAX_ROWS = 200_000` takes a random sample of the data; changing it changes the results.
- Training and inference times depend on your hardware and are best read as relative comparisons between models.

---

## 11. Tech stack

Python, NumPy, pandas, scikit-learn, Matplotlib, seaborn, Jupyter.

---
