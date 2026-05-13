import requests
import json
from auth.get_token import load_token

PRIMARY_CARE_BASE_URL = "https://your-primarycare-server/fhir"
OUTPUT_FILE = "coding_task2_output.json"


def get_headers():
    token = load_token()
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/fhir+json",
        "Accept": "application/fhir+json"
    }


def get_all_conditions(patient_id):
    """
    Retrieve all Condition resources for a patient
    from the Primary Care FHIR server.
    """
    response = requests.get(
        f"{PRIMARY_CARE_BASE_URL}/Condition",
        headers=get_headers(),
        params={"patient": patient_id}
    )

    if response.status_code == 200:
        bundle = response.json()
        entries = bundle.get("entry", [])
        conditions = []

        for entry in entries:
            condition = entry["resource"]
            coding = condition.get("code", {}).get("coding", [{}])[0]
            clinical_status = condition.get("clinicalStatus", {}) \
                .get("coding", [{}])[0].get("code", "unknown")

            conditions.append({
                "condition_id": condition.get("id"),
                "snomed_code": coding.get("code", ""),
                "display": coding.get("display", ""),
                "clinical_status": clinical_status,
                "onset": condition.get("onsetDateTime", "unknown")
            })

        print(f"Found {len(conditions)} condition(s) for patient {patient_id}")
        return conditions
    else:
        print(f"Failed to retrieve conditions: {response.status_code}")
        return []


if __name__ == "__main__":
    # Load patient ID from Task 1 output
    with open("coding_task1_output.json", "r") as f:
        task1_output = json.load(f)

    patient_id = task1_output["primary_patient_id"]

    # Get all conditions
    conditions = get_all_conditions(patient_id)

    # Save output
    output = {
        "primary_patient_id": patient_id,
        "conditions": conditions
    }
    with open(OUTPUT_FILE, "w") as f:
        json.dump(output, f, indent=2)

    print(f"Task 2 complete. Output saved to {OUTPUT_FILE}")
