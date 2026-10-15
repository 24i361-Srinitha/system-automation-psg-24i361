import argparse
import json
from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split


BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "historical_readings.csv"
MAINTENANCE_FILE = BASE_DIR / "maintenance_log.txt"
RESULT_FILE = BASE_DIR / "decision_log.jsonl"

SENSOR_COLUMNS = [
    "torque_nm",
    "temperature_c",
    "vibration_mm_s"
]

MAX_SAFE_VALUES = {
    "torque_nm": 70.0,
    "temperature_c": 90.0,
    "vibration_mm_s": 7.5
}

WEAR_KEYWORDS = [
    "vibration", "bearing", "noise",
    "looseness", "fluctuate", "warmer"
]

SENSOR_KEYWORDS = [
    "calibration", "sensor cable",
    "connector", "reading integrity"
]


def build_model():
    readings = pd.read_csv(DATA_FILE)

    features = readings[SENSOR_COLUMNS]
    labels = readings["wear_label"]

    train_x, test_x, train_y, test_y = train_test_split(
        features,
        labels,
        test_size=0.2,
        random_state=42,
        stratify=labels
    )

    forest = RandomForestClassifier(
        n_estimators=150,
        random_state=42,
        class_weight="balanced"
    )

    forest.fit(train_x, train_y)

    test_predictions = forest.predict(test_x)

    print(
        "Random Forest accuracy on the test data:",
        f"{accuracy_score(test_y, test_predictions):.1%}"
    )

    print(
        classification_report(
            test_y,
            test_predictions,
            zero_division=0
        )
    )

    forest.fit(features, labels)

    return forest


def check_safety_limits(reading):
    exceeded_limits = []

    for sensor, limit in MAX_SAFE_VALUES.items():
        if float(reading[sensor]) >= limit:
            exceeded_limits.append(sensor)

    return exceeded_limits


def read_maintenance_notes(arm_id, joint_name):
    wear_records = []
    sensor_records = []

    if not MAINTENANCE_FILE.exists():
        return wear_records, sensor_records

    with MAINTENANCE_FILE.open(
        "r", encoding="utf-8"
    ) as file:
        for note in file:
            cleaned_note = note.strip()
            note_text = cleaned_note.lower()

            if (
                arm_id.lower() not in note_text
                or joint_name.lower() not in note_text
            ):
                continue

            if any(word in note_text for word in SENSOR_KEYWORDS):
                sensor_records.append(cleaned_note)

            elif any(word in note_text for word in WEAR_KEYWORDS):
                wear_records.append(cleaned_note)

    return wear_records, sensor_records


def check_reading_validity(reading, previous_reading=None):
    warnings = []

    valid_ranges = {
        "torque_nm": (0, 80),
        "temperature_c": (0, 110),
        "vibration_mm_s": (0, 10)
    }

    for sensor, (minimum, maximum) in valid_ranges.items():
        value = float(reading[sensor])

        if value < minimum or value > maximum:
            warnings.append(
                f"{sensor} is outside its expected range"
            )

    if previous_reading is not None:
        current_torque = float(reading["torque_nm"])
        previous_torque = float(previous_reading["torque_nm"])

        if abs(current_torque - previous_torque) > 35:
            warnings.append(
                "Unexpected change in torque compared with "
                "the previous trusted reading"
            )

    return warnings


def evaluate_joint(
    reading,
    model,
    arm_id="ARM-01",
    joint_name="shoulder",
    previous_reading=None
):
    exceeded_limits = check_safety_limits(reading)

    if exceeded_limits:
        return {
            "decision": "EMERGENCY_STOP",
            "reason": (
                "Safety limits exceeded: "
                + ", ".join(exceeded_limits)
            ),
            "model_prediction": None,
            "wear_notes": [],
            "integrity_notes": [],
            "spoof_alerts": []
        }

    validity_warnings = check_reading_validity(
        reading, previous_reading
    )

    wear_notes, sensor_notes = read_maintenance_notes(
        arm_id, joint_name
    )

    input_data = pd.DataFrame(
        [reading],
        columns=SENSOR_COLUMNS
    )

    prediction = model.predict(input_data)[0]

    if validity_warnings or sensor_notes:
        decision = "SCHEDULE_MAINTENANCE"
        reason = (
            "A possible sensor integrity issue was found. "
            "Inspect the sensor and joint."
        )

    elif prediction == "WEAR" and wear_notes:
        decision = "SCHEDULE_MAINTENANCE"
        reason = (
            "The model detected possible wear, and the "
            "maintenance notes support this finding."
        )

    elif prediction == "WEAR" or wear_notes:
        decision = "MONITOR"
        reason = (
            "A possible wear issue was detected. "
            "Monitor the joint and collect more readings."
        )

    else:
        decision = "SAFE"
        reason = (
            "No safety limit violations or wear indicators "
            "were found."
        )

    return {
        "decision": decision,
        "reason": reason,
        "model_prediction": str(prediction),
        "wear_notes": wear_notes,
        "integrity_notes": sensor_notes,
        "spoof_alerts": validity_warnings
    }


def save_result(result, reading, arm_id, joint_name):
    entry = {
        "arm_id": arm_id,
        "joint": joint_name,
        "reading": reading,
        **result
    }

    with RESULT_FILE.open("a", encoding="utf-8") as file:
        file.write(json.dumps(entry) + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Check robotic arm sensor readings"
    )

    parser.add_argument(
        "--examples",
        action="store_true",
        help="Run the program with sample readings"
    )

    parser.add_argument("--arm", default="ARM-01")

    parser.add_argument(
        "--joint",
        default="shoulder",
        choices=["shoulder", "elbow", "wrist"]
    )

    parser.add_argument("--torque", type=float, default=42)
    parser.add_argument("--temperature", type=float, default=55)
    parser.add_argument("--vibration", type=float, default=2)

    args = parser.parse_args()

    model = build_model()

    if args.examples:
        test_cases = [
            (
                "ARM-03",
                "shoulder",
                {
                    "torque_nm": 25,
                    "temperature_c": 40,
                    "vibration_mm_s": 1.0
                }
            ),
            (
                "ARM-01",
                "shoulder",
                {
                    "torque_nm": 48,
                    "temperature_c": 65,
                    "vibration_mm_s": 4.0
                }
            ),
            (
                "ARM-02",
                "elbow",
                {
                    "torque_nm": 58,
                    "temperature_c": 75,
                    "vibration_mm_s": 5.5
                }
            ),
            (
                "ARM-04",
                "shoulder",
                {
                    "torque_nm": 75,
                    "temperature_c": 60,
                    "vibration_mm_s": 2.0
                }
            )
        ]

    else:
        sensor_reading = {
            "torque_nm": args.torque,
            "temperature_c": args.temperature,
            "vibration_mm_s": args.vibration
        }

        test_cases = [
            (args.arm, args.joint, sensor_reading)
        ]

    for arm_id, joint_name, reading in test_cases:
        result = evaluate_joint(
            reading,
            model,
            arm_id,
            joint_name
        )

        print("\n" + "=" * 50)
        print("Arm:", arm_id)
        print("Joint:", joint_name)
        print("Sensor readings:", reading)
        print("Decision:", result["decision"])
        print("Reason:", result["reason"])
        print("Model prediction:", result["model_prediction"])

        if result["wear_notes"]:
            print("Wear notes:", result["wear_notes"])

        if result["integrity_notes"]:
            print("Sensor integrity notes:", result["integrity_notes"])

        if result["spoof_alerts"]:
            print("Reading warnings:", result["spoof_alerts"])

        save_result(
            result,
            reading,
            arm_id,
            joint_name
        )

    print("\nResults saved to:", RESULT_FILE)


if __name__ == "__main__":
    main()

