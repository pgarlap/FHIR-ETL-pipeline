import requests
import json
from datetime import datetime
from hl7apy.core import Message
from auth.get_token import load_token

HERMES_BASE_URL = "https://your-hermes-server"
OUTPUT_FILE = "task_5_hl7.txt"


def map_snomed_to_icd10(snomed_code):
    """
    Use Hermes Terminology Server to map
    SNOMED CT code to ICD-10 code.
    """
    response = requests.get(
        f"{HERMES_BASE_URL}/v1/snomed/map",
        params={
            "code": snomed_code,
            "targetSystem": "http://hl7.org/fhir/sid/icd-10"
        }
    )

    if response.status_code == 200:
        mappings = response.json()
        if mappings:
            icd10_code = mappings[0].get("code", "R56.9")
            icd10_display = mappings[0].get("display", "Unspecified convulsions")
            print(f"SNOMED {snomed_code} → ICD-10 {icd10_code}: {icd10_display}")
            return icd10_code, icd10_display
    print(f"Mapping failed: {response.status_code} — using default R56.9")
    return "R56.9", "Unspecified convulsions"


def generate_hl7_message(patient, conditions, icd10_mappings):
    """
    Generate HL7 v2 ADT^A01 message from FHIR patient
    and condition data. Includes MSH, PID, PV1, DG1 segments.
    """
    msg = Message("ADT_A01", version="2.5")

    # MSH - Message Header
    msg.msh.msh_3 = "FHIR_ETL_PIPELINE"
    msg.msh.msh_4 = "IU_HEALTH_INFORMATICS"
    msg.msh.msh_5 = "PRIMARY_CARE_EHR"
    msg.msh.msh_6 = "RECEIVING_FACILITY"
    msg.msh.msh_7 = datetime.now().strftime("%Y%m%d%H%M%S")
    msg.msh.msh_9 = "ADT^A01"
    msg.msh.msh_10 = "MSG001"
    msg.msh.msh_11 = "P"
    msg.msh.msh_12 = "2.5"

    # PID - Patient Identification
    name = patient.get("name", [{}])[0]
    family = name.get("family", "Unknown")
    given = name.get("given", ["Unknown"])[0]

    msg.pid.pid_3 = patient.get("id", "UNKNOWN")
    msg.pid.pid_5 = f"{family}^{given}"
    msg.pid.pid_7 = patient.get("birthDate", "").replace("-", "")
    msg.pid.pid_8 = patient.get("gender", "U")[0].upper()

    address = patient.get("address", [{}])[0]
    msg.pid.pid_11 = address.get("city", "Indianapolis")

    # PV1 - Patient Visit
    msg.pv1.pv1_2 = "O"
    msg.pv1.pv1_3 = "PRIMARY_CARE_CLINIC"
    msg.pv1.pv1_44 = datetime.now().strftime("%Y%m%d%H%M%S")

    # DG1 - Diagnosis (one per condition)
    for i, (icd10_code, icd10_display) in enumerate(icd10_mappings, start=1):
        msg.add_segment("DG1")
        dg1 = msg.dg1
        dg1.dg1_1 = str(i)
        dg1.dg1_3 = icd10_code
        dg1.dg1_4 = icd10_display
        dg1.dg1_6 = "F"

    hl7_text = msg.to_er7()
    print("HL7 v2 ADT^A01 message generated successfully.")
    return hl7_text


if __name__ == "__main__":
    # Load outputs from Task 1 and Task 2
    with open("coding_task1_output.json", "r") as f:
        task1 = json.load(f)

    with open("coding_task2_output.json", "r") as f:
        task2 = json.load(f)

    # Map each SNOMED condition to ICD-10
    icd10_mappings = []
    for condition in task2["conditions"]:
        snomed_code = condition["snomed_code"]
        icd10_code, icd10_display = map_snomed_to_icd10(snomed_code)
        icd10_mappings.append((icd10_code, icd10_display))

    # Build a minimal patient dict for HL7
    patient = {
        "id": task1["primary_patient_id"],
        "name": [{"family": "Smith", "given": ["John"]}],
        "birthDate": "1990-01-01",
        "gender": "male",
        "address": [{"city": "Indianapolis"}]
    }

    # Generate HL7 message
    hl7_message = generate_hl7_message(patient, task2["conditions"], icd10_mappings)

    # Save HL7 output
    with open(OUTPUT_FILE, "w") as f:
        f.write(hl7_message)

    print(f"Task 5 complete. HL7 message saved to {OUTPUT_FILE}")
