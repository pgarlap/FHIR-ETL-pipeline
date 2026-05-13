import requests
import json
from auth.get_token import load_token

PRIMARY_CARE_BASE_URL = "https://your-primarycare-server/fhir"
OUTPUT_FILE = "coding_task3_output.json"


def get_headers():
    token = load_token()
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/fhir+json",
        "Accept": "application/fhir+json"
    }


def create_blood_pressure_observation(patient_id):
    """
    Create a blood pressure Observation resource
    coded with LOINC for systolic and diastolic values.
    Posts to the Primary Care FHIR server.
    """
    payload = {
        "resourceType": "Observation",
        "status": "final",
        "category": [{
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                "code": "vital-signs",
                "display": "Vital Signs"
            }]
        }],
        "code": {
            "coding": [{
                "system": "http://loinc.org",
                "code": "55284-4",
                "display": "Blood pressure systolic and diastolic"
            }]
        },
        "subject": {
            "reference": f"Patient/{patient_id}"
        },
        "effectiveDateTime": "2025-01-15T10:30:00Z",
        "component": [
            {
                "code": {
                    "coding": [{
                        "system": "http://loinc.org",
                        "code": "8480-6",
                        "display": "Systolic blood pressure"
                    }]
                },
                "valueQuantity": {
                    "value": 120,
                    "unit": "mmHg",
                    "system": "http://unitsofmeasure.org",
                    "code": "mm[Hg]"
                }
            },
            {
                "code": {
                    "coding": [{
                        "system": "http://loinc.org",
                        "code": "8462-4",
                        "display": "Diastolic blood pressure"
                    }]
                },
                "valueQuantity": {
                    "value": 80,
                    "unit": "mmHg",
                    "system": "http://unitsofmeasure.org",
                    "code": "mm[Hg]"
                }
            }
        ]
    }

    response = requests.post(
        f"{PRIMARY_CARE_BASE_URL}/Observation",
        headers=get_headers(),
        json=payload
    )

    if response.status_code in [200, 201]:
        observation = response.json()
        print(f"Observation created: {observation['id']}")
        return observation["id"]
    else:
        print(f"Observation creation failed: {response.status_code}")
        print(response.text)
        return None


if __name__ == "__main__":
    # Load patient ID from Task 1 output
    with open("coding_task1_output.json", "r") as f:
        task1_output = json.load(f)

    patient_id = task1_output["primary_patient_id"]

    # Create blood pressure observation
    observation_id = create_blood_pressure_observation(patient_id)

    # Save output
    output = {
        "primary_patient_id": patient_id,
        "observation_id": observation_id,
        "observation_type": "Blood Pressure",
        "loinc_code": "55284-4",
        "systolic": 120,
        "diastolic": 80
    }
    with open(OUTPUT_FILE, "w") as f:
        json.dump(output, f, indent=2)

    print(f"Task 3 complete. Output saved to {OUTPUT_FILE}")
