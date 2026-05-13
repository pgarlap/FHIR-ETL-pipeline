import requests
import json
import matplotlib.pyplot as plt
import os
from auth.get_token import load_token

OPENEMR_BASE_URL = "https://your-openemr-server/apis/default/fhir"
OUTPUT_DIR = "assets"


def get_headers():
    token = load_token()
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/fhir+json"
    }


def fetch_all_patients():
    """
    Fetch all patient resources from OpenEMR
    FHIR server and return as a list.
    """
    patients = []
    url = f"{OPENEMR_BASE_URL}/Patient"

    while url:
        response = requests.get(url, headers=get_headers())
        if response.status_code != 200:
            print(f"Failed to fetch patients: {response.status_code}")
            break

        bundle = response.json()
        entries = bundle.get("entry", [])

        for entry in entries:
            patients.append(entry["resource"])

        # Handle pagination
        next_url = None
        for link in bundle.get("link", []):
            if link["relation"] == "next":
                next_url = link["url"]
                break
        url = next_url

    print(f"Total patients fetched: {len(patients)}")
    return patients


def analyze_gender_distribution(patients):
    """
    Analyze gender distribution across
    all retrieved patient resources.
    """
    gender_counts = {
        "Male": 0,
        "Female": 0,
        "Other": 0,
        "Unknown": 0
    }

    for patient in patients:
        gender = patient.get("gender", "unknown").lower()
        if gender == "male":
            gender_counts["Male"] += 1
        elif gender == "female":
            gender_counts["Female"] += 1
        elif gender == "other":
            gender_counts["Other"] += 1
        else:
            gender_counts["Unknown"] += 1

    return gender_counts


def plot_gender_distribution(gender_counts):
    """
    Plot and save gender distribution
    as a bar chart.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    labels = list(gender_counts.keys())
    values = list(gender_counts.values())
    colors = ["#4A90D9", "#E87C7C", "#7DBF7D", "#B0B0B0"]

    plt.figure(figsize=(8, 5))
    bars = plt.bar(labels, values, color=colors, edgecolor="white", linewidth=0.5)

    for bar, value in zip(bars, values):
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.3,
            str(value),
            ha="center",
            va="bottom",
            fontsize=11
        )

    plt.title("Patient Gender Distribution — FHIR Data", fontsize=14)
    plt.xlabel("Gender", fontsize=12)
    plt.ylabel("Number of Patients", fontsize=12)
    plt.tight_layout()

    output_path = os.path.join(OUTPUT_DIR, "gender_distribution.png")
    plt.savefig(output_path, dpi=150)
    plt.close()

    print(f"Chart saved to {output_path}")
    return output_path


if __name__ == "__main__":
    patients = fetch_all_patients()
    gender_counts = analyze_gender_distribution(patients)
    print(f"Gender breakdown: {json.dumps(gender_counts, indent=2)}")
    plot_gender_distribution(gender_counts)
