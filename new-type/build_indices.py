#!/usr/bin/env python3
"""
build_indices.py  –  Create 1–5‑scaled items, reverse‑code negatives,
                     and generate Connectivity & Productivity composite indices.

Python ≥3.8, pandas, openpyxl required.
"""

import pandas as pd
from pathlib import Path

# ------------------------------------------------------------------
# 1.  CONFIGURATION  ------------------------------------------------
# ------------------------------------------------------------------

# 1.a  Choose the input CSV  (or .xlsx – pandas can read both)
INPUT_FILE = "./comprehensive_anova_data.csv"

# 1.b  Columns that are already numeric / continuous
NUMERIC_COLS = [
    "WiFi_Speed_Score",
    "Reliability_Score",
    "Peak_Performance_Score",
    "Outage_Frequency_Score",
    "Programming_Impact_Score",    # Likert 1–5
    "Collaboration_Score",
    "Task_Abandonment_Score",      # will reverse later
    "Time_Lost_Score",             # will reverse later
    "Productivity_Influence_Score",
    "Future_Performance_Score",
]

# 1.c  Ordinal / text columns → numeric mapping (all columns are already numeric)
ORDINAL_MAP = {
    # Since all columns are already numeric with _Score suffix, 
    # we don't need any text-to-numeric mapping
}

# 1.d  Items where HIGH raw value means WORSE outcome
Productivity_loss = [
    "Outage_Frequency_Score",   # Higher frequency = more outages = worse
    "Task_Abandonment_Score",   # Higher score = more abandonment = worse
    "Time_Lost_Score",          # Higher score = more time lost = worse
]

# 1.e  Composite‑index ingredients
Internet_connectivity = [
    "WiFi_Speed_Score", "Reliability_Score", "Peak_Performance_Score", "Outage_Frequency_Score_R"
]

Productivity = [
    "Programming_Impact_Score", "Collaboration_Score",
    "Task_Abandonment_Score_R", "Time_Lost_Score_R",
    "Productivity_Influence_Score", "Future_Performance_Score"
]

# Output
OUTPUT_FILE = "composite_indices.xlsx"

# ------------------------------------------------------------------
# 2.  HELPER FUNCTIONS  --------------------------------------------
# ------------------------------------------------------------------

def rescale_1to5(series: pd.Series) -> pd.Series:
    """Min–max rescale a numeric pandas Series to 1‑5."""
    s_min, s_max = series.min(), series.max()
    if pd.isna(s_min) or s_min == s_max:
        # constant column → centre value 3
        return pd.Series([3.0] * len(series), index=series.index)
    return (series - s_min) / (s_max - s_min) * 4 + 1


def reverse_code(series: pd.Series) -> pd.Series:
    """Assumes incoming series already on a 1‑5 scale."""
    return 6 - series


# ------------------------------------------------------------------
# 3.  LOAD DATA  ----------------------------------------------------
# ------------------------------------------------------------------

print(f"Reading {INPUT_FILE} …")
df = pd.read_csv(INPUT_FILE) if INPUT_FILE.endswith(".csv") else pd.read_excel(INPUT_FILE)

# ------------------------------------------------------------------
# 4.  MAP ORDINAL TEXT → NUMERIC -----------------------------------
# ------------------------------------------------------------------

for col, mapping in ORDINAL_MAP.items():
    if col in df.columns:
        df[col] = df[col].map(mapping)
    else:
        print(f"⚠️  Column '{col}' listed in ORDINAL_MAP but not found in file.")

# ------------------------------------------------------------------
# 5.  RESCALE EVERYTHING TO 1‑5  -----------------------------------
# ------------------------------------------------------------------

# A. numeric columns
for col in NUMERIC_COLS:
    if col in df.columns:
        df[col] = rescale_1to5(df[col])
    else:
        print(f"⚠️  Column '{col}' listed in NUMERIC_COLS but not found in file.")

# B. any ordinal‑mapped columns now numeric but maybe not 1‑5 (depends on map)
for col in ORDINAL_MAP:
    if col in df.columns and (df[col].min() < 1 or df[col].max() > 5):
        df[col] = rescale_1to5(df[col])

# ------------------------------------------------------------------
# 6.  REVERSE‑CODE “higher = worse” ITEMS --------------------------
# ------------------------------------------------------------------

for col in Productivity_loss:
    if col in df.columns:
        df[f"{col}_R"] = reverse_code(df[col])
    else:
        print(f"⚠️  Column '{col}' listed in REVERSE_ITEMS but not found in file.")

# ------------------------------------------------------------------
# 7.  BUILD COMPOSITE INDICES  -------------------------------------
# ------------------------------------------------------------------

def safe_mean(row, cols):
    vals = row[cols].dropna()
    return vals.mean() if len(vals) else pd.NA

df["Connectivity_Index"] = df.apply(lambda row: safe_mean(row, Internet_connectivity), axis=1)
df["Productivity_Index"] = df.apply(lambda row: safe_mean(row, Productivity), axis=1)

# ------------------------------------------------------------------
# 8.  SAVE  ---------------------------------------------------------
# ------------------------------------------------------------------

df.to_excel(OUTPUT_FILE, index=False)
print(f"✅  Done.  Composite indices saved to {OUTPUT_FILE}")
