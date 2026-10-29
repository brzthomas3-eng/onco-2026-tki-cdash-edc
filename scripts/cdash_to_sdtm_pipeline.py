"""
================================================================================
CDISC SDTM v3.3 TRANSFORMATION PIPELINE
Protocol: ONCO-2026-TKI
Description: Transforms locked REDCap CDASH eCRF data into SDTM submission domains
================================================================================
"""

import os
import pandas as pd

# ==============================================================================
# 1. CONFIGURATION & INGESTION
# ==============================================================================
STUDYID = "ONCO-2026-TKI"
INPUT_FILE = os.path.join("data", "clean_clinical_data_export.csv")
OUTPUT_DIR = os.path.join("data", "sdtm")

os.makedirs(OUTPUT_DIR, exist_ok=True)

print(f"[INIT] Reading Locked Clinical Database: {INPUT_FILE}")
df_raw = pd.read_csv(INPUT_FILE, dtype=str).fillna("")

# ==============================================================================
# 2. SDTM DOMAIN: DM (Demographics)
# ==============================================================================
print("[PROCESS] Generating DM (Demographics) Domain...")
# Isolate baseline visit, drop duplicates, and reset index
dm_raw = df_raw[df_raw['redcap_event_name'].str.contains("screening|baseline", case=False)].drop_duplicates(subset=["subjid"]).copy().reset_index(drop=True)

dm = pd.DataFrame()
dm['STUDYID'] = STUDYID
dm['DOMAIN'] = 'DM'
dm['USUBJID'] = STUDYID + "-" + dm_raw['siteid'] + "-" + dm_raw['subjid']
dm['SUBJID'] = dm_raw['subjid']
dm['SITEID'] = dm_raw['siteid']
dm['BRTHDTC'] = dm_raw['brthdtc']
dm['AGE'] = dm_raw['age']
dm['AGEU'] = 'YEARS'
dm['SEX'] = dm_raw['sex']
dm['RACE'] = dm_raw['race']
dm['ETHNIC'] = dm_raw['ethnic']
dm['ARMCD'] = 'ONC702'
dm['ARM'] = 'ONC-702 150mg QD'
dm['ACTARM'] = 'ONC-702 150mg QD'

dm.to_csv(os.path.join(OUTPUT_DIR, "dm.csv"), index=False)

# Create a dictionary to easily map SITEID across other domains
site_dict = dict(zip(dm_raw['subjid'], dm_raw['siteid']))

# ==============================================================================
# 3. SDTM DOMAIN: AE (Adverse Events)
# ==============================================================================
print("[PROCESS] Generating AE (Adverse Events) Domain...")
# Isolate AE Log rows, filter out blanks, and reset index
ae_raw = df_raw[(df_raw['redcap_repeat_instrument'] == 'ae_log') & (df_raw['aeterm'] != "")].copy().reset_index(drop=True)

ae = pd.DataFrame()
ae['STUDYID'] = STUDYID
ae['DOMAIN'] = 'AE'
ae['SITEID'] = ae_raw['subjid'].map(site_dict)
ae['USUBJID'] = STUDYID + "-" + ae['SITEID'] + "-" + ae_raw['subjid']

# Sequence numbers for repeating records
ae['AESEQ'] = ae_raw.groupby('subjid').cumcount() + 1
ae['AETERM'] = ae_raw['aeterm']
ae['AESTDTC'] = ae_raw['aestdat']
ae['AEENDTC'] = ae_raw['aeendat']
ae['AESEV'] = ae_raw['aetoxgr'].apply(lambda x: f"GRADE {x}" if x != "" else "")
ae['AESER'] = ae_raw['aeser'].apply(lambda x: "Y" if x == "1" else "N" if x == "0" else "")
ae['AEREL'] = ae_raw['aerel']
ae['AEOUT'] = ae_raw['aeout']

ae.to_csv(os.path.join(OUTPUT_DIR, "ae.csv"), index=False)

# ==============================================================================
# 4. SDTM DOMAIN: EX (Exposure / Dosing)
# ==============================================================================
print("[PROCESS] Generating EX (Exposure) Domain...")
ex_raw = df_raw[df_raw['exdose_act'] != ""].copy().reset_index(drop=True)

ex = pd.DataFrame()
ex['STUDYID'] = STUDYID
ex['DOMAIN'] = 'EX'
ex['SITEID'] = ex_raw['subjid'].map(site_dict)
ex['USUBJID'] = STUDYID + "-" + ex['SITEID'] + "-" + ex_raw['subjid']
ex['EXSEQ'] = ex_raw.groupby('subjid').cumcount() + 1
ex['EXTRT'] = 'ONC-702'
ex['EXDOSE'] = ex_raw['exdose_act']
ex['EXDOSU'] = 'mg'
ex['EXDOSFRM'] = 'TABLET'
ex['EXSTDTC'] = ex_raw['exstdtc']
ex['EXENDTC'] = ex_raw['exendtc']
ex['EXADJ'] = ex_raw['exadj'].apply(lambda x: "Y" if x == "1" else "N" if x == "0" else "")

ex.to_csv(os.path.join(OUTPUT_DIR, "ex.csv"), index=False)

# ==============================================================================
# 5. SDTM DOMAIN: RS (Disease Response)
# ==============================================================================
print("[PROCESS] Generating RS (Disease Response) Domain...")
rs_raw = df_raw[df_raw['recist_eval'] != ""].copy().reset_index(drop=True)

rs = pd.DataFrame()
rs['STUDYID'] = STUDYID
rs['DOMAIN'] = 'RS'
rs['SITEID'] = rs_raw['subjid'].map(site_dict)
rs['USUBJID'] = STUDYID + "-" + rs['SITEID'] + "-" + rs_raw['subjid']
rs['RSSEQ'] = rs_raw.groupby('subjid').cumcount() + 1
rs['RSTESTCD'] = 'OVRLRESP'
rs['RSTEST'] = 'Overall Response'
rs['RSCAT'] = 'RECIST 1.1'
rs['RSORRES'] = rs_raw['recist_eval']
rs['RSDTC'] = rs_raw['eval_dat']

rs.to_csv(os.path.join(OUTPUT_DIR, "rs.csv"), index=False)

# ==============================================================================
# SUMMARY
# ==============================================================================
print("\n[SUCCESS] CDASH to SDTM Transformation Complete.")
print(f"  --> DM: {len(dm)} records generated.")
print(f"  --> AE: {len(ae)} records generated.")
print(f"  --> EX: {len(ex)} records generated.")
print(f"  --> RS: {len(rs)} records generated.")
print(f"Files saved to: {OUTPUT_DIR}/")