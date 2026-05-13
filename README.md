# FHIR-Powered ETL Pipeline for Healthcare Data Interoperability

An end-to-end ETL pipeline that extracts patient and clinical data 
from a FHIR API, applies domain-aware transformations using SNOMED CT 
and ICD-10 mapping, loads validated resources into a secondary FHIR 
endpoint, and generates HL7 v2 messages for legacy system compatibility.

## Project Overview

Built as part of M.S. Health Informatics coursework at Indiana University 
Indianapolis. This pipeline demonstrates real-world healthcare 
interoperability standards used across modern EHR systems.

---

## Pipeline Architecture
OpenEMR FHIR API → Extract → Transform → Load → Primary Care FHIR API
↓
HL7 v2 ADT Message (Legacy Support)
---

## What It Does

| Task | Description |
|---|---|
| Task 1 | Extract patient data + SNOMED CT child term mapping |
| Task 2 | Retrieve all patient Condition resources |
| Task 3 | Create blood pressure Observation (LOINC coded) |
| Task 4 | Create EEG Procedure resource (SNOMED coded) |
| Task 5 | Map SNOMED → ICD-10 and generate HL7 v2 ADT message |
| Visualization | Gender distribution chart from FHIR patient data |

---

## Tech Stack

- **Language:** Python 3.8+
- **FHIR APIs:** OpenEMR (source) · Primary Care EHR (target)
- **Terminology:** SNOMED CT · ICD-10 · LOINC
- **Mapping:** Hermes Terminology Server
- **Legacy Interop:** HL7 v2 via hl7apy
- **Auth:** OAuth 2.0 (Authorization Code Flow)
- **Visualization:** matplotlib

---

## Key Features

**FHIR Resource Handling**
Extracts, transforms, and loads Patient, Condition, 
Observation, and Procedure resources using FHIR-compliant 
JSON payloads.

**Terminology Mapping**
Uses Hermes API to resolve SNOMED CT parent/child 
relationships and map to ICD-10 codes - ensuring semantic 
accuracy across systems.

**HL7 v2 Interoperability**
Converts FHIR JSON to HL7 v2 ADT^A01 messages including 
MSH, PID, PV1, and DG1 segments - supporting legacy EHR 
systems that haven't transitioned to FHIR.

**OAuth 2.0 Security**
Implements full Authorization Code Flow with access token 
retrieval, secure storage, and automated refresh token 
handling for uninterrupted pipeline execution.

---

## Project Structure

fhir-etl-pipeline/
├── auth/
│   └── get_token.py          # OAuth 2.0 token management
├── tasks/
│   ├── task1_extract_patient.py
│   ├── task2_get_conditions.py
│   ├── task3_create_observation.py
│   ├── task4_create_procedure.py
│   └── task5_hl7_generation.py
├── visualization/
│   └── gender_distribution.py
├── requirements.txt
└── README.md

---

## Setup

```bash
git clone https://github.com/pgarlap/fhir-etl-pipeline
cd fhir-etl-pipeline
pip install -r requirements.txt
```

---

## Requirements
requests
hl7apy
matplotlib

---

## Key Learnings

- FHIR's resource-based schema enforces data integrity across 
  Patient, Condition, Observation, and Procedure records
- SNOMED CT to ICD-10 mapping requires resolving parent/child 
  terminology relationships for clinical accuracy
- Converting FHIR to HL7 v2 ensures backward compatibility with 
  legacy hospital systems (LIS, RIS, billing engines)
- OAuth 2.0 token refresh automation is critical for long-running 
  ETL pipelines

---

## Author

**Poojitha Garlapati** - API Integration Specialist & Data Extractor  
PharmD + M.S. Health Informatics, Indiana University Indianapolis

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0A66C2?style=flat-square&logo=linkedin&logoColor=white)](https://linkedin.com/in/garlapati-poojitha)
[![Email](https://img.shields.io/badge/Email-D14836?style=flat-square&logo=gmail&logoColor=white)](mailto:poojithagarlapati55@gmail.com)
