import requests
import json
from auth.get_token import load_token

PRIMARY_CARE_BASE_URL = "https://your-primarycare-server/fhir"
OUTPUT_FILE = "coding_task4_output.json"


def get_headers():
    token = load_token()
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/fhir+json",
        "Accept": "application/fhir+json"
    }


def create_eeg_procedure(patient_id):
    """
    Create an EEG Procedure resource coded with
    SNOMED CT and linked to patient and practitioner.
    Posts to the Primary Care FHIR server.
    """
    payload = {
        "resourceType": "Procedure",
        "status": "completed",
        "subject": {
            "reference": f"Patient/{patient_id}"
        },
        "code": {
            "coding": [{
                "system": "http://snomed.info/sct",
                "code": "54550000",
                "display": "Electroencephalography (EEG)"
            }]
        },
        "performedDateTime": "2025-01-15T11:00:00Z",
        "performer": [{
            "actor": {
                "reference": "Practitioner/example-practitioner",
                "display": "Dr. Jane Smith, Neurologist"
            }
        }],
        "note": [{
            "text": "EEG performed to evaluate seizure activity. "
                    "No abnormal electrical activity detected during "
                    "the 30-minute recording session."
        }]
    }

    response = requests.post(
        f"{PRIMARY_CARE_BASE_URL}/Procedure",
        headers=get_headers(),
        json=payload
    )

    if response.status_code in [200, 201]:
        procedure = response.json()
        print(f"Procedure created: {procedure['id']}")
        return procedure["id"]
    else:
        print(f"Procedure creation failed: {response.status_code}")
        print(response.text)
        return None


if __name__ == "__main__":
    # Load patient ID from Task 1 output
    with open("coding_task1_output.json", "r") as f:
        task1_output = json.load(f)

    patient_id = task1_output["primary_patient_id"]

    # Create EEG procedure
    procedure_id = create_eeg_procedure(patient_id)

    # Save output
    output = {
        "primary_patient_id": patient_id,
        "procedure_id": procedure_id,
        "procedure_type": "Electroencephalography (EEG)",
        "snomed_code": "54550000",
        "performer": "Dr. Jane Smith, Neurologist"
    }
    with open(OUTPUT_FILE, "w") as f:
        json.dump(output, f, indent=2)

    print(f"Task 4 complete. Output saved to {OUTPUT_FILE}")
