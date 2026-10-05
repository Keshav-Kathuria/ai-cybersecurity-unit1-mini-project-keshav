"""
CICIDS2017 — STEP 1: Study + Clean the raw data (no training yet)
-------------------------------------------------------------------
Goal: understand what's actually in the 8 files, fix known issues,
and produce ONE clean CSV we can confidently train on later.
"""

import pandas as pd
import numpy as np
import glob
import os
import warnings

warnings.filterwarnings("ignore", category=RuntimeWarning)

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 200)

# ----------------------------------------------------------------------
# 0. SET YOUR FOLDER PATH HERE
# ----------------------------------------------------------------------
FOLDER_PATH = "."

# ----------------------------------------------------------------------
# 1. LOAD + INSPECT EACH FILE INDIVIDUALLY
# ----------------------------------------------------------------------
csv_files = sorted(glob.glob(os.path.join(FOLDER_PATH, "*.csv")))
print(f"Found {len(csv_files)} CSV files\n")

df_list = []
all_col_sets = []

for f in csv_files:
    temp = pd.read_csv(f, encoding="latin1", low_memory=False)
    temp.columns = temp.columns.str.strip()

    print(f"--- {os.path.basename(f)} ---")
    print(f"  Shape: {temp.shape}")
    if "Label" in temp.columns:
        print(f"  Label counts: {dict(temp['Label'].value_counts())}")
    else:
        print(f"  WARNING: no 'Label' column! Columns found: {list(temp.columns)}")
    print()

    all_col_sets.append(set(temp.columns))
    df_list.append(temp)

# Column consistency check across files
common_cols = set.intersection(*all_col_sets)
union_cols = set.union(*all_col_sets)
if common_cols != union_cols:
    print(f"WARNING: mismatched columns across files: {union_cols - common_cols}")
    print("Using only columns common to all files.\n")
    df_list = [d[list(common_cols)] for d in df_list]
else:
    print("All 8 files have matching columns.\n")

# ----------------------------------------------------------------------
# 2. MERGE
# ----------------------------------------------------------------------
df = pd.concat(df_list, ignore_index=True)
print(f"Merged shape (before cleaning): {df.shape}\n")

# Handle the known duplicate 'Fwd Header Length' column name issue
dupe_cols = df.columns[df.columns.duplicated()].tolist()
if dupe_cols:
    print(f"Duplicate column names found (pandas auto-renamed): {dupe_cols}\n")

# ----------------------------------------------------------------------
# 3. OVERALL LABEL DISTRIBUTION (before cleaning)
# ----------------------------------------------------------------------
print("=" * 60)
print("FULL LABEL DISTRIBUTION (all 8 days combined)")
print("=" * 60)
label_counts = df["Label"].value_counts()
print(label_counts)
print(f"\nTotal rows: {len(df)}")
print(f"Benign %: {(label_counts.get('BENIGN', 0) / len(df)) * 100:.2f}%")
print(f"Attack %: {(1 - label_counts.get('BENIGN', 0) / len(df)) * 100:.2f}%\n")

# ----------------------------------------------------------------------
# 4. MISSING VALUES CHECK
# ----------------------------------------------------------------------
print("=" * 60)
print("MISSING VALUES (NaN) PER COLUMN — top offenders")
print("=" * 60)
missing = df.isnull().sum()
missing = missing[missing > 0].sort_values(ascending=False)
if len(missing) > 0:
    print(missing)
    print(f"\nTotal rows with at least one NaN: {df.isnull().any(axis=1).sum()}")
else:
    print("No NaN values found (yet — infinities are checked separately below).")
print()

# ----------------------------------------------------------------------
# 5. INFINITE VALUES CHECK (known issue: Flow Bytes/s, Flow Packets/s divide by ~0 duration)
# ----------------------------------------------------------------------
print("=" * 60)
print("INFINITE VALUES PER COLUMN")
print("=" * 60)
numeric_df = df.select_dtypes(include=[np.number])
inf_counts = np.isinf(numeric_df).sum()
inf_counts = inf_counts[inf_counts > 0].sort_values(ascending=False)
if len(inf_counts) > 0:
    print(inf_counts)
    print(f"\nTotal rows with at least one infinite value: {np.isinf(numeric_df).any(axis=1).sum()}")
else:
    print("No infinite values found.")
print()

# ----------------------------------------------------------------------
# 6. DUPLICATE ROWS CHECK
# ----------------------------------------------------------------------
n_dupes = df.duplicated().sum()
print("=" * 60)
print(f"DUPLICATE ROWS: {n_dupes} ({n_dupes/len(df)*100:.2f}% of data)")
print("=" * 60 + "\n")

# ----------------------------------------------------------------------
# 7. CONSTANT / NEAR-USELESS COLUMNS CHECK
# ----------------------------------------------------------------------
print("=" * 60)
print("CONSTANT COLUMNS (same value in every row — no signal, safe to drop)")
print("=" * 60)
constant_cols = [c for c in numeric_df.columns if numeric_df[c].nunique(dropna=True) <= 1]
print(constant_cols if constant_cols else "None found.")
print()

# ----------------------------------------------------------------------
# 8. BASIC STATS ON NUMERIC FEATURES (sanity check for weirdness)
# ----------------------------------------------------------------------
print("=" * 60)
print("BASIC STATS (first 10 numeric columns shown)")
print("=" * 60)
print(numeric_df.iloc[:, :10].describe().T)
print()

# ----------------------------------------------------------------------
# 9. NOW ACTUALLY CLEAN (based on what we found above)
# ----------------------------------------------------------------------
print("=" * 60)
print("CLEANING")
print("=" * 60)
before = len(df)

df.replace([np.inf, -np.inf], np.nan, inplace=True)
df.dropna(inplace=True)
print(f"After dropping NaN/inf rows: {len(df)} (removed {before - len(df)})")

before = len(df)
df.drop_duplicates(inplace=True)
print(f"After dropping duplicate rows: {len(df)} (removed {before - len(df)})")

if constant_cols:
    df.drop(columns=constant_cols, inplace=True)
    print(f"Dropped {len(constant_cols)} constant column(s): {constant_cols}")

print(f"\nFinal cleaned shape: {df.shape}")
print("\nFinal label distribution after cleaning:")
print(df["Label"].value_counts())

# ----------------------------------------------------------------------
# 10. SAVE CLEANED DATA
# ----------------------------------------------------------------------
OUTPUT_PATH = os.path.join(FOLDER_PATH, "cicids2017_cleaned.csv")
df.to_csv(OUTPUT_PATH, index=False)
print(f"\nSaved cleaned dataset to: {OUTPUT_PATH}")