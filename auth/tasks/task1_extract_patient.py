import requests
import json
from auth.get_token import load_token

# FHIR Server Configuration
OPENEMR_BASE_URL = "https://your-openemr-server/apis/default/fhir"
PRIMARY_CARE_BASE_URL = "https://your-primarycare-server/fhir"
HERMES_BASE_URL = "https://your-hermes-server"

OUTPUT_FILE = "coding_task1_output.json"


def get_headers():
    token = load_token()
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/fhir+json",
        "Accept": "application/fhir+json"
    }


def search_patient(name, birthdate):
    """
    Search for a patient on OpenEMR FHIR server
    using name and birthdate filters.
    """
    params = {
        "name": name,
        "birthdate": birthdate
    }
    response = requests.get(
        f"{OPENEMR_BASE_URL}/Patient",
        headers=get_headers(),
        params=params
    )
    if response.status_code == 200:
        bundle = response.json()
        entries = bundle.get("entry", [])
        if entries:
            patient = entries[0]["resource"]
            print(f"Patient found: {patient['id']}")
            return patient
    print(f"Patient search failed: {response.status_code}")
    return None


def get_patient_condition(patient_id):
    """
    Retrieve SNOMED condition code from patient's
    Condition resource on OpenEMR FHIR server.
    """
    response = requests.get(
        f"{OPENEMR_BASE_URL}/Condition",
        headers=get_headers(),
        params={"patient": patient_id}
    )
    if response.status_code == 200:
        bundle = response.json()
        entries = bundle.get("entry", [])
        if entries:
            condition = entries[0]["resource"]
            snomed_code = condition["code"]["coding"][0]["code"]
            print(f"SNOMED condition code: {snomed_code}")
            return snomed_code
    print(f"Condition retrieval failed: {response.status_code}")
    return None


def get_child_snomed_concept(parent_code):
    """
    Use Hermes Terminology Server to find a child
    SNOMED CT concept using < constraint.
    """
    response = requests.get(
        f"{HERMES_BASE_URL}/v1/snomed/search",
        params={
            "constraint": f"< {parent_code}",
            "maxResults": 1
        }
    )
    if response.status_code == 200:
        results = response.json()
        if results:
            child_code = results[0]["conceptId"]
            child_display = results[0]["preferredTerm"]
            print(f"Child SNOMED concept: {child_code} - {child_display}")
            return child_code, child_display
    print(f"Hermes lookup failed: {response.status_code}")
    return None, None


def create_patient_on_primary_care(patient):
    """
    Create a new Patient resource on the
    Primary Care FHIR server.
    """
    payload = {
        "resourceType": "Patient",
        "name": patient.get("name", []),
        "gender": patient.get("gender", "unknown"),
        "birthDate": patient.get("birthDate", ""),
        "address": patient.get("address", [])
    }
    response = requests.post(
        f"{PRIMARY_CARE_BASE_URL}/Patient",
        headers=get_headers(),
        json=payload
    )
    if response.status_code in [200, 201]:
        new_patient = response.json()
        print(f"New patient created: {new_patient['id']}")
        return new_patient["id"]
    print(f"Patient creation failed: {response.status_code}")
    return None


def create_condition_on_primary_care(patient_id, snomed_code, snomed_display):
    """
    Create a new Condition resource using child
    SNOMED concept on Primary Care FHIR server.
    """
    payload = {
        "resourceType": "Condition",
        "subject": {"reference": f"Patient/{patient_id}"},
        "code": {
            "coding": [{
                "system": "http://snomed.info/sct",
                "code": snomed_code,
                "display": snomed_display
            }]
        },
        "clinicalStatus": {
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                "code": "active"
            }]
        }
    }
    response = requests.post(
        f"{PRIMARY_CARE_BASE_URL}/Condition",
        headers=get_headers(),
        json=payload
    )
    if response.status_code in [200, 201]:
        condition = response.json()
        print(f"Condition created: {condition['id']}")
        return condition["id"]
    print(f"Condition creation failed: {response.status_code}")
    return None


if __name__ == "__main__":
    # Step 1: Search for patient
    patient = search_patient(name="Smith", birthdate="1990-01-01")
    if not patient:
        exit()

    patient_id = patient["id"]

    # Step 2: Get SNOMED condition code
    snomed_code = get_patient_condition(patient_id)
    if not snomed_code:
        exit()

    # Step 3: Get child SNOMED concept via Hermes
    child_code, child_display = get_child_snomed_concept(snomed_code)
    if not child_code:
        exit()

    # Step 4: Create patient on Primary Care server
    primary_patient_id = create_patient_on_primary_care(patient)
    if not primary_patient_id:
        exit()

    # Step 5: Create condition with child SNOMED code
    condition_id = create_condition_on_primary_care(
        primary_patient_id, child_code, child_display
    )

    # Step 6: Save output for use in later tasks
    output = {
        "primary_patient_id": primary_patient_id,
        "condition_id": condition_id,
        "snomed_code": child_code,
        "snomed_display": child_display
    }
    with open(OUTPUT_FILE, "w") as f:
        json.dump(output, f, indent=2)

    print(f"Task 1 complete. Output saved to {OUTPUT_FILE}")
