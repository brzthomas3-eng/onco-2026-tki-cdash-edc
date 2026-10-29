"""
================================================================================
ONCOLOGY CLINICAL DATA SCIENCE VISUALIZER
Protocol: ONCO-2026-TKI
Description: Generates RECIST 1.1 Waterfall & CTCAE Toxicity Plots
================================================================================
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.patches as mpatches

# ==============================================================================
# 1. CONFIGURATION & DATA INGESTION
# ==============================================================================
INPUT_FILE = os.path.join("data", "clean_clinical_data_export.csv")
OUTPUT_DIR = "assets"

os.makedirs(OUTPUT_DIR, exist_ok=True)
print(f"[INIT] Ingesting locked database for visual analytics: {INPUT_FILE}")

# Read CSV and strip any hidden trailing spaces from REDCap column headers
df = pd.read_csv(INPUT_FILE, dtype=str).fillna("")
df.columns = df.columns.str.strip()

# Ensure styling is crisp for publication
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_context("talk")

# ------------------------------------------------------------------------------
# Robust Tumor Measurement Extractor
# ------------------------------------------------------------------------------
def get_tumor_measure(df_subset):
    """Safely extracts tumor burden whether REDCap calculated the sum or not."""
    # Check if tu_sum_diam exists AND has at least one non-blank value
    if 'tu_sum_diam' in df_subset.columns and df_subset['tu_sum_diam'].str.strip().astype(bool).any():
        return pd.to_numeric(df_subset['tu_sum_diam'], errors='coerce')
    else:
        # Fallback: Just use tu_diam_1 (add tu_diam_2 if it exists)
        d1 = pd.to_numeric(df_subset.get('tu_diam_1', pd.Series(0, index=df_subset.index)), errors='coerce').fillna(0)
        d2 = pd.to_numeric(df_subset.get('tu_diam_2', pd.Series(0, index=df_subset.index)), errors='coerce').fillna(0)
        return d1 + d2

# ==============================================================================
# 2. RECIST 1.1 WATERFALL PLOT (EFFICACY)
# ==============================================================================
print("[PROCESS] Generating RECIST 1.1 Best Overall Response Waterfall Plot...")

# Extract Baseline Tumor Diameters
base_mask = df['redcap_event_name'].str.contains("baseline|screening", case=False, na=False)
base_df = df[base_mask].copy()
base_df['base_diam'] = get_tumor_measure(base_df)
base_df = base_df[['subjid', 'base_diam']].dropna(subset=['base_diam'])

# Extract Restaging Tumor Diameters & Response
rest_mask = df['redcap_event_name'].str.contains("restaging", case=False, na=False)
rest_df = df[rest_mask].copy()
rest_df['rest_diam'] = get_tumor_measure(rest_df)
rest_df = rest_df[['subjid', 'rest_diam', 'recist_eval']].dropna(subset=['rest_diam'])

# Merge and calculate Percentage Change
wf_df = pd.merge(base_df, rest_df, on='subjid', how='inner')

# Calculate percentage change safely (avoid division by zero)
wf_df['pct_change'] = np.where(
    wf_df['base_diam'] > 0, 
    ((wf_df['rest_diam'] - wf_df['base_diam']) / wf_df['base_diam']) * 100, 
    0
)

# Sort for the waterfall effect (largest growth to largest shrinkage)
wf_df = wf_df.sort_values(by='pct_change', ascending=False).reset_index(drop=True)

# Color mapping based on RECIST 1.1 standard oncology palettes
color_map = {'CR': '#28a745', 'PR': '#17a2b8', 'SD': '#ffc107', 'PD': '#dc3545'}
wf_df['color'] = wf_df['recist_eval'].str.strip().map(color_map).fillna('#6c757d')

plt.figure(figsize=(12, 7))
bars = plt.bar(wf_df.index, wf_df['pct_change'], color=wf_df['color'], edgecolor='black', linewidth=0.5)

# Reference Threshold Lines (RECIST 1.1 Criteria)
plt.axhline(y=20, color='#dc3545', linestyle='--', linewidth=1.5, label='Progressive Disease (PD) Threshold (+20%)')
plt.axhline(y=-30, color='#28a745', linestyle='--', linewidth=1.5, label='Partial Response (PR) Threshold (-30%)')
plt.axhline(y=0, color='black', linewidth=1)

# Formatting
plt.title('Best Overall Response Waterfall Plot (ONC-702)\nPhase II NSCLC Cohort', fontsize=16, fontweight='bold', pad=15)
plt.xlabel('Individual Patients (N=30)', fontsize=12)
plt.ylabel('Maximum % Change in Target Lesion Sum from Baseline', fontsize=12)
plt.xticks([])  # Hide x-axis labels to anonymize patients visually

# Dynamic Y-Axis Limits
if not wf_df.empty:
    y_max = max(40, wf_df['pct_change'].max() + 10)
    plt.ylim(-100, y_max)
else:
    plt.ylim(-100, 100)

# Custom Legend
legend_patches = [
    mpatches.Patch(color='#28a745', label='Complete Response (CR)'),
    mpatches.Patch(color='#17a2b8', label='Partial Response (PR)'),
    mpatches.Patch(color='#ffc107', label='Stable Disease (SD)'),
]
if 'PD' in wf_df['recist_eval'].values:
    legend_patches.append(mpatches.Patch(color='#dc3545', label='Progressive Disease (PD)'))

plt.legend(handles=legend_patches, loc='lower left', fontsize=10, frameon=True, shadow=True)

plt.tight_layout()
waterfall_path = os.path.join(OUTPUT_DIR, "recist_waterfall_plot.png")
plt.savefig(waterfall_path, dpi=300)
plt.close()

# ==============================================================================
# 3. CTCAE TOXICITY PROFILE (SAFETY)
# ==============================================================================
print("[PROCESS] Generating CTCAE Adverse Event Toxicity Profile...")

ae_df = df[(df.get('redcap_repeat_instrument', '') == 'ae_log') & (df.get('aeterm', '') != "")].copy()
ae_df['aetoxgr'] = pd.to_numeric(ae_df.get('aetoxgr', 1), errors='coerce').fillna(1).astype(int)

# Count AEs by Term and Grade
tox_summary = ae_df.groupby(['aeterm', 'aetoxgr']).size().unstack(fill_value=0)

# Ensure all 4 grade columns exist for plotting consistency
for i in range(1, 5):
    if i not in tox_summary.columns:
        tox_summary[i] = 0

# Sort by total incidence
if not tox_summary.empty:
    tox_summary['Total'] = tox_summary.sum(axis=1)
    tox_summary = tox_summary.sort_values(by='Total', ascending=True).drop(columns=['Total'])

# Plot
plt.figure(figsize=(10, 6))
colors = {1: '#28a745', 2: '#ffc107', 3: '#fd7e14', 4: '#dc3545'}
if not tox_summary.empty:
    tox_summary.plot(kind='barh', stacked=True, color=[colors[i] for i in tox_summary.columns], edgecolor='black', ax=plt.gca())

plt.title('Treatment-Emergent Adverse Events (TEAEs) by CTCAE v5.0 Grade', fontsize=14, fontweight='bold', pad=15)
plt.xlabel('Number of Events', fontsize=12)
plt.ylabel('MedDRA Preferred Term', fontsize=12)

# Format Legend
plt.legend(title='CTCAE Severity Grade', labels=[f'Grade {c}' for c in range(1,5)], loc='lower right', frameon=True, shadow=True)
plt.tight_layout()

ae_path = os.path.join(OUTPUT_DIR, "ctcae_toxicity_profile.png")
plt.savefig(ae_path, dpi=300)
plt.close()

print("\n[SUCCESS] Oncology Visualizations Generated Successfully.")
print(f"  --> Saved: {waterfall_path}")
print(f"  --> Saved: {ae_path}")