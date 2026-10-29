End-to-End Clinical Data Pipeline: Phase II Oncology Trial (ONCO-2026-TKI)

👋 Welcome to the Project

Hello! I built this portfolio project to demonstrate the complete, real-world lifecycle of clinical trial data.

In the industry, data doesn't just appear clean and ready for analysis. It has to be collected accurately, audited for medical and logical errors, transformed into strict regulatory formats, and finally visualized to see if a drug actually works.

This project simulates a Phase II Oncology Trial (ONCO-2026-TKI) testing a targeted therapy in 30 patients with Non-Small Cell Lung Cancer (NSCLC). I acted as the Clinical Data Manager, Statistical Programmer, and Data Scientist to take this data from a blank form all the way to final FDA-style efficacy charts.

🎯 Overall Project Scope & The Step-by-Step Journey

The goal was to build a fully functional, audit-ready clinical data pipeline. Here is exactly how I executed it, step-by-step:

Phase 1: Clinical Data Operations & Database Lock

Building the Database (eCRF Design): I didn't start with a spreadsheet. I designed a CDASH-compliant clinical database in REDCap, creating forms for Demographics, Vitals, Dosing, Tumor Restaging, and Adverse Events.

Generating Realistic Data: I wrote a Python script to generate 30 synthetic patients. I intentionally planted 5 specific clinical errors (like a patient being too old for the protocol, or a tumor response contradiction) to simulate real-world messy data.

Auditing the Data (Data Validation): I wrote a custom Python validation engine (discrepancy_validation.py) to act as a digital auditor. It scanned the messy data and flagged the 5 deliberate errors, generating a formal Query Log.

Fixing the Data (Database Lock): Acting as a Data Manager, I went back into REDCap, resolved the queries with proper 21 CFR Part 11 audit trails, and achieved a "Database Lock" (zero errors).

Phase 2: The SDTM Transformation Engine

Formatting for Submission (SDTM): Regulatory agencies don't accept raw REDCap data. I wrote a Python pipeline to transform the clean data into strict CDISC SDTM formats (DM, AE, EX, RS).

Phase 3: Oncology Efficacy & Safety Analytics

Analyzing the Results (Data Science): Finally, I used the standardized data to generate the exact visual charts used by Medical Monitors to see if the drug was safe and effective.

📊 Phase 3 Results: Did the treatment work?

(These are the automated outputs from the final step of the project, visualizing the locked data).

1. Best Overall Response (RECIST 1.1 Efficacy)

How to read this result:
This waterfall plot shows how much each patient's tumor shrank or grew.

The green dotted line (-30%) is the threshold for a Partial Response (meaning the drug is significantly shrinking the tumor).

The red dotted line (+20%) is the threshold for Progressive Disease (meaning the cancer is growing and the drug isn't working for them).

Conclusion: Our simulated cohort shows a strong response to the ONC-702 drug, with the vast majority of patients crossing the green threshold and achieving tumor shrinkage. Only a few patients experienced tumor growth.

2. Treatment-Emergent Adverse Events (Safety)

How to read this result:
This chart tracks the side effects (Adverse Events) patients experienced, categorized by severity (Grade 1 is mild, Grade 4 is severe/life-threatening).

Conclusion: The most common side effects were Nausea, Acneiform Rash, and Diarrhea, mostly kept at a mild/manageable Grade 1 or 2. There were very few severe events (like Grade 3/4 Febrile Neutropenia), indicating that the drug has an acceptable safety profile for this stage of research.

📂 Repository Structure

Here is how the project files and directories are organized based on my workspace:

Onco 2026/
├── assets/
│   ├── ctcae_toxicity_profile.png
│   └── recist_waterfall_plot.png
├── data/
│   ├── sdtm/
│   └── clean_clinical_data_export.csv
├── reports/
│   └── data_quality_discrepancy_log.csv
├── scripts/
│   ├── cdash_to_sdtm_pipeline.py
│   ├── plot_oncology_readouts.py
│   ├── discrepancy_validation.py
│   └── generate_synthetic_data.py
├── raw_clinical_data_export.csv
├── synthetic_study_data_30_records.csv
└── README.md


🚀 How to Run This Project Locally

If you want to run the scripts yourself and see the pipeline in action, follow these steps:

1. Set up your environment

Make sure you have Python installed, then install the necessary data science libraries by running this command in your terminal:

pip install pandas numpy matplotlib seaborn


2. Verify the Database Lock (Phase 1)

Run the discrepancy engine against the clean dataset. This proves the data cleaning phase was successful and there are zero outstanding queries:

python scripts/discrepancy_validation.py


3. Run the SDTM Transformation (Phase 2)

Watch the script reshape the raw data into regulatory-ready SDTM domains. The output files will be saved directly into the data/sdtm/ folder:

python scripts/cdash_to_sdtm_pipeline.py


4. Generate the Analytics (Phase 3)

Run the visualization script to generate the publication-ready efficacy and safety charts. The .png files will be saved in the assets/ folder:

python scripts/plot_oncology_readouts.py
