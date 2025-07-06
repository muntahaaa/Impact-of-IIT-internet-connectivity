#!/usr/bin/env python3
"""
build_composite_from_scaled.py
--------------------------------
Create Connectivity_Index and Productivity_Index
from the already scaled / reverse‑coded columns
stored in composite_indices.xlsx.
"""

import pandas as pd
from pathlib import Path

# ------------------------------------------------------------------
# 1. CONFIG – ADJUST TO YOUR FILE ----------------------------------
# ------------------------------------------------------------------
INPUT_FILE  = Path("scaled_data.xlsx")
OUTPUT_FILE = Path("composite_indices_with_scores.xlsx")

# Columns that belong in each composite  (✏️  customise these)
INTERNET_CONNECTIVITY_METRICS = [
    "WiFi_Speed_Score", "Reliability_Score", "Peak_Performance_Score", "Outage_Frequency_Score_R"
]

STUDENT_PRODUCTIVITY_METRICS = [
    "Programming_Impact_Score", "Collaboration_Score",
    "Task_Abandonment_Score_R", "Time_Lost_Score_R",
    "Productivity_Influence_Score", "Future_Performance_Score"
]

# ------------------------------------------------------------------
# 2. LOAD THE WORKBOOK ---------------------------------------------
# ------------------------------------------------------------------
print(f"📂  Reading {INPUT_FILE} …")
df = pd.read_excel(INPUT_FILE)

# Sanity check – warn if any expected column is missing
missing_connect = [c for c in INTERNET_CONNECTIVITY_METRICS  if c not in df.columns]
missing_prod    = [c for c in STUDENT_PRODUCTIVITY_METRICS if c not in df.columns]
if missing_connect or missing_prod:
    raise ValueError(
        f"Missing columns:\n"
        f"  Connectivity: {missing_connect}\n"
        f"  Productivity: {missing_prod}"
    )

# ------------------------------------------------------------------
# 3. COMPUTE THE COMPOSITE INDICES ---------------------------------
# ------------------------------------------------------------------
df["Connectivity_Index"] = df[INTERNET_CONNECTIVITY_METRICS].mean(axis=1, skipna=True)
df["Productivity_Index"] = df[STUDENT_PRODUCTIVITY_METRICS].mean(axis=1, skipna=True)

# Optional: categorise connectivity into Low / Medium / High terciles
df["Connectivity_Group"] = pd.qcut(
    df["Connectivity_Index"],
    q=[0, 1/3, 2/3, 1],
    labels=["Low", "Medium", "High"]
)

# ------------------------------------------------------------------
# 4. SAVE THE RESULT -----------------------------------------------
# ------------------------------------------------------------------
# Create a new dataframe with only the composite indices
composite_df = df[["Connectivity_Index", "Productivity_Index", "Connectivity_Group"]].copy()

composite_df.to_excel(OUTPUT_FILE, index=False)
print(f"✅  Done!  Composite indices written to {OUTPUT_FILE}")
