import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import math

# Fix seeds for reproducibility
np.random.seed(2026)
random.seed(2026)

# ==============================================================================
# 1. REDCap Longitudinal Event Configuration
# ==============================================================================
# Verify these match Project Setup -> Define My Events -> Unique event name
EV_SCR  = "baselinescreening_arm_1"
EV_C1   = "cycle_1_day_1_arm_1"
EV_C2   = "cycle_2_day_1_arm_1"
EV_REST = "tumor_restaging_arm_1"
EV_EOS  = "end_of_study_arm_1"

EVENT_ORDER = {
    EV_SCR: 1,
    EV_C1: 2,
    EV_C2: 3,
    EV_REST: 4,
    EV_EOS: 5
}

STUDY_ID = "ONCO-2026-TKI"
PLANNED_DOSE = 150

rows = []

# ==============================================================================
# 2. Subject Generation Engine (30 Patients: 25 Clean, 5 Discrepant)
# ==============================================================================
for i in range(1, 31):
    subjid = 1000 + i
    siteid = random.choice([101, 102, 103])
    
    # Chronological timeline milestones
    consent_date = datetime(2026, 3, 1) + timedelta(days=random.randint(0, 10))
    c1_date      = consent_date + timedelta(days=random.randint(4, 7))
    c2_date      = c1_date + timedelta(days=21)
    rest_date    = c1_date + timedelta(days=42)
    eos_date     = rest_date + timedelta(days=14)

    # Base Demographics
    age_years = random.randint(42, 71)
    ecog = random.choice([0, 1])
    
    # --- Discrepancy Case 5: Subject 1028 (Protocol Eligibility Breach) ---
    if subjid == 1028:
        age_years = 79       # Violates age eligibility (>75)
        ecog = 2            # Violates ECOG status (>1)
        
    dob = consent_date - timedelta(days=int(age_years * 365.25))
    sex = random.choice(["M", "F"])
    race = random.choice(["ASIAN", "WHITE", "BLACK"])
    ethnic = random.choice(["HISP", "NOTHISP"])
    egfr = random.choice(["EX19DEL", "L858R", "T790M"])
    
    height_cm = round(random.uniform(155.0, 182.0), 1)
    weight_kg = round(random.uniform(52.0, 88.0), 1)
    bsa_val = round(math.sqrt((height_cm * weight_kg) / 3600), 2)
    
    baseline_diam = round(random.uniform(28.0, 65.0), 1)

    # --------------------------------------------------------------------------
    # EVENT 1: SCREENING / BASELINE
    # --------------------------------------------------------------------------
    rows.append({
        "subjid": str(subjid),
        "redcap_event_name": EV_SCR,
        "redcap_repeat_instrument": "",
        "redcap_repeat_instance": "",
        # enroll_icf
        "studyid": STUDY_ID,
        "siteid": str(siteid),
        "dsstdat_ic": consent_date.strftime("%Y-%m-%d"),
        "ic_ver": "1.0",
        "ie_met": "1",
        "ie_cat": "",
        "ie_nr": "",
        "enroll_icf_complete": "2",
        # demog
        "brthdtc": dob.strftime("%Y-%m-%d"),
        "sex": sex,
        "race": race,
        "ethnic": ethnic,
        "ecog_bl": str(ecog),
        "egfr_mut": egfr,
        "demog_complete": "2",
        # mh_onco
        "nsclc_diag_dat": (consent_date - timedelta(days=random.randint(90, 365))).strftime("%Y-%m-%d"),
        "hist_type": "ADENO",
        "tnm_stage": "IV",
        "prev_systemic": "1",
        "prev_lines_cnt": "1",
        "prev_tki_exp": "1",
        "mh_onco_complete": "2",
        # vs (Baseline)
        "vsdat": consent_date.strftime("%Y-%m-%d"),
        "vstpt": "PRE",
        "height": str(height_cm),
        "weight": str(weight_kg),
        "bsa": str(bsa_val),
        "sysbp": str(random.randint(110, 134)),
        "diabp": str(random.randint(68, 84)),
        "pulse": str(random.randint(64, 82)),
        "vs_complete": "2",
        # lb (Baseline)
        "lbdat": consent_date.strftime("%Y-%m-%d"),
        "anc": str(round(random.uniform(2.4, 6.2), 2)),
        "plt": str(random.randint(160, 340)),
        "alt": str(random.randint(16, 38)),
        "ast": str(random.randint(15, 34)),
        "creat": str(round(random.uniform(0.65, 1.10), 2)),
        "lb_clin_sig": "0",
        "lb_complete": "2",
        # recist_tu (Baseline Scan)
        "eval_dat": consent_date.strftime("%Y-%m-%d"),
        "tu_loc_1": "Right Upper Lobe Lung",
        "tu_diam_1": str(baseline_diam),
        "tu_loc_2": "",
        "tu_diam_2": "",
        "tu_sum_diam": str(baseline_diam),
        "recist_eval": "NE",
        "recist_tu_complete": "2"
    })

    # --------------------------------------------------------------------------
    # EVENT 2: CYCLE 1 DAY 1
    # --------------------------------------------------------------------------
    c1_dose_act = PLANNED_DOSE
    c1_dose_mod = "0"
    
    # --- Discrepancy Case 4: Subject 1023 (Dose Accountability Mismatch) ---
    if subjid == 1023:
        c1_dose_act = 100
        c1_dose_mod = "0"

    rows.append({
        "subjid": str(subjid),
        "redcap_event_name": EV_C1,
        "redcap_repeat_instrument": "",
        "redcap_repeat_instance": "",
        # vs
        "vsdat": c1_date.strftime("%Y-%m-%d"),
        "vstpt": "PRE",
        "height": str(height_cm),
        "weight": str(weight_kg),
        "bsa": str(bsa_val),
        "sysbp": str(random.randint(108, 136)),
        "diabp": str(random.randint(68, 86)),
        "pulse": str(random.randint(66, 84)),
        "vs_complete": "2",
        # lb
        "lbdat": c1_date.strftime("%Y-%m-%d"),
        "anc": str(round(random.uniform(2.1, 5.8), 2)),
        "plt": str(random.randint(150, 310)),
        "alt": str(random.randint(18, 42)),
        "ast": str(random.randint(16, 38)),
        "creat": str(round(random.uniform(0.70, 1.15), 2)),
        "lb_clin_sig": "0",
        "lb_complete": "2",
        # ex
        "extrt": "ONC-702",
        "exstdtc": f"{c1_date.strftime('%Y-%m-%d')} 09:00",
        "exendtc": f"{c1_date.strftime('%Y-%m-%d')} 09:05",
        "exdose_plan": str(PLANNED_DOSE),
        "exdose_act": str(c1_dose_act),
        "exadj": c1_dose_mod,
        "exadj_rsn": "",
        "ex_complete": "2"
    })

    # Repeating ae_log Row (Instance 1)
    ae_onset = c1_date + timedelta(days=random.randint(2, 8))
    ae_term = random.choice(["Diarrhea", "Acneiform Rash", "Nausea", "Fatigue"])
    ae_grade = "1"
    ae_ser = "0"
    sae_hosp_box = ""
    sae_exp_24h = ""

    # --- Discrepancy Case 1: Subject 1004 (Chronological Order Violation) ---
    if subjid == 1004:
        ae_term = "Severe Dermatitis"
        ae_onset = consent_date - timedelta(days=8)
        ae_grade = "3"

    # --- Discrepancy Case 3: Subject 1019 (Expedited Regulatory Violation) ---
    if subjid == 1019:
        ae_term = "Febrile Neutropenia"
        ae_grade = "3"
        ae_ser = "1"
        sae_hosp_box = "1"
        sae_exp_24h = "0"

    rows.append({
        "subjid": str(subjid),
        "redcap_event_name": EV_C1,
        "redcap_repeat_instrument": "ae_log",
        "redcap_repeat_instance": "1",
        "aeterm": ae_term,
        "aestdat": ae_onset.strftime("%Y-%m-%d"),
        "aeendat": (ae_onset + timedelta(days=4)).strftime("%Y-%m-%d"),
        "ae_ongoing": "0",
        "aetoxgr": ae_grade,
        "aerel": "POSS",
        "aeacn": "NONE",
        "aeout": "RECOV",
        "aeser": ae_ser,
        "sae_crit___3": sae_hosp_box,
        "sae_exp_24h": sae_exp_24h,
        "ae_log_complete": "2"
    })

    # --------------------------------------------------------------------------
    # EVENT 3: CYCLE 2 DAY 1
    # --------------------------------------------------------------------------
    rows.append({
        "subjid": str(subjid),
        "redcap_event_name": EV_C2,
        "redcap_repeat_instrument": "",
        "redcap_repeat_instance": "",
        # vs
        "vsdat": c2_date.strftime("%Y-%m-%d"),
        "vstpt": "PRE",
        "height": str(height_cm),
        "weight": str(weight_kg),
        "bsa": str(bsa_val),
        "sysbp": str(random.randint(110, 134)),
        "diabp": str(random.randint(70, 85)),
        "pulse": str(random.randint(64, 80)),
        "vs_complete": "2",
        # lb
        "lbdat": c2_date.strftime("%Y-%m-%d"),
        "anc": str(round(random.uniform(2.0, 5.2), 2)),
        "plt": str(random.randint(145, 295)),
        "alt": str(random.randint(20, 44)),
        "ast": str(random.randint(18, 39)),
        "creat": str(round(random.uniform(0.70, 1.18), 2)),
        "lb_clin_sig": "0",
        "lb_complete": "2",
        # ex
        "extrt": "ONC-702",
        "exstdtc": f"{c2_date.strftime('%Y-%m-%d')} 09:00",
        "exendtc": f"{c2_date.strftime('%Y-%m-%d')} 09:05",
        "exdose_plan": str(PLANNED_DOSE),
        "exdose_act": str(PLANNED_DOSE),
        "exadj": "0",
        "exadj_rsn": "",
        "ex_complete": "2"
    })

    # --------------------------------------------------------------------------
    # EVENT 4: TUMOR RESTAGING (Week 6)
    # --------------------------------------------------------------------------
    restaging_diam = round(baseline_diam * random.uniform(0.55, 0.85), 1)
    overall_response = "PR" if (restaging_diam <= baseline_diam * 0.70) else "SD"

    # --- Discrepancy Case 2: Subject 1012 (RECIST Medical Contradiction) ---
    if subjid == 1012:
        restaging_diam = 14.5
        overall_response = "CR"

    rows.append({
        "subjid": str(subjid),
        "redcap_event_name": EV_REST,
        "redcap_repeat_instrument": "",
        "redcap_repeat_instance": "",
        "eval_dat": rest_date.strftime("%Y-%m-%d"),
        "tu_loc_1": "Right Upper Lobe Lung",
        "tu_diam_1": str(restaging_diam),
        "tu_loc_2": "",
        "tu_diam_2": "",
        "tu_sum_diam": str(restaging_diam),
        "recist_eval": overall_response,
        "recist_tu_complete": "2"
    })

    # --------------------------------------------------------------------------
    # EVENT 5: END OF STUDY / DISPOSITION
    # --------------------------------------------------------------------------
    rows.append({
        "subjid": str(subjid),
        "redcap_event_name": EV_EOS,
        "redcap_repeat_instrument": "",
        "redcap_repeat_instance": "",
        "dsstdat_eos": eos_date.strftime("%Y-%m-%d"),
        "dscompl": "1",
        "dsdecod": "",
        "eos_ds_complete": "2"
    })

# ==============================================================================
# 3. Clean & Export
# ==============================================================================
df_clinical = pd.DataFrame(rows)

# Fill all missing/NaN fields with clean empty strings
df_clinical = df_clinical.fillna("")

# Categorical chronological sort
df_clinical["event_seq"] = df_clinical["redcap_event_name"].map(EVENT_ORDER)
df_clinical["instance_seq"] = pd.to_numeric(df_clinical["redcap_repeat_instance"], errors="coerce").fillna(0)
df_clinical.sort_values(by=["subjid", "event_seq", "instance_seq"], inplace=True)
df_clinical.drop(columns=["event_seq", "instance_seq"], inplace=True)

output_filename = "synthetic_study_data_30_records.csv"
df_clinical.to_csv(output_filename, index=False)

print(f"Data Generation Successful: {len(df_clinical)} rows created across {df_clinical['subjid'].nunique()} clinical subjects.")
print(f"File saved to: {output_filename}")