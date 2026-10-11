import random
import time
import json
import pandas as pd

from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score

DATA_FILE = r"C:\Users\pl\Documents\GitHub\system-automation-psg-24i361\Day 2\data\day2_sample.csv"
LOG_FILE = "final_combined_log.txt"

FEATURES = ["temperature", "pressure", "vibration", "current", "rpm"]

data = pd.read_csv(DATA_FILE)

X = data[FEATURES]
y = data["state"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

model = DecisionTreeClassifier(
    random_state=42,
    class_weight="balanced"
)

model.fit(X_train, y_train)

print(
    "Decision Tree Accuracy:",
    round(accuracy_score(y_test, model.predict(X_test)) * 100, 2),
    "%"
)

model.fit(X, y)


def generate_sensor_data():
    return {
        "temperature": round(random.uniform(50, 95), 2),
        "pressure": round(random.uniform(1.0, 10.0), 2),
        "vibration": round(random.uniform(0.0, 5.0), 2),
        "current": round(random.uniform(0.5, 25.0), 2),
        "rpm": random.randint(1000, 3500)
    }


RULES = [
    {
        "name": "HIGH_TEMP",
        "priority": 1,
        "condition": lambda r: r["temperature"] > 85,
        "state": "OVERHEATING",
        "action": "STOP_MACHINE"
    },
    {
        "name": "HIGH_VIBRATION",
        "priority": 2,
        "condition": lambda r: r["vibration"] > 4.0,
        "state": "HIGH_VIBRATION",
        "action": "STOP_MACHINE"
    },
    {
        "name": "MOTOR_OVERLOAD",
        "priority": 3,
        "condition": lambda r: r["current"] > 22.0 or r["rpm"] > 3200,
        "state": "MOTOR_OVERLOAD",
        "action": "STOP_MACHINE"
    },
    {
        "name": "LOW_PRESSURE",
        "priority": 4,
        "condition": lambda r: r["pressure"] < 2.0,
        "state": "LOW_PRESSURE",
        "action": "REPAIR_MACHINE"
    }
]


def evaluate_rules(reading):
    for rule in sorted(RULES, key=lambda r: r["priority"]):
        if rule["condition"](reading):
            return rule["name"], rule["state"], rule["action"]

    return None, None, None


def take_action(action):
    actions = {
        "STOP_MACHINE": "ALERT! Stop machine and inspect.",
        "REPAIR_MACHINE": "Maintenance inspection required.",
        "WARNING": "Warning! Check machine condition.",
        "CONTINUE": "Continue operation; monitor readings."
    }

    return actions.get(action, "No action defined.")


def log_decision(reading, prediction, rule_name, state, action):
    entry = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "reading": reading,
        "model_prediction": prediction,
        "triggered_rule": rule_name,
        "final_state": state,
        "action": action
    }

    with open(LOG_FILE, "a", encoding="utf-8") as file:
        file.write(json.dumps(entry) + "\n")


def append_to_dataset(reading, state):
    new_row = {
        "temperature": reading["temperature"],
        "pressure": reading["pressure"],
        "vibration": reading["vibration"],
        "current": reading["current"],
        "rpm": reading["rpm"],
        "state": state
    }

    try:
        pd.DataFrame([new_row], columns=FEATURES + ["state"]).to_csv(
            DATA_FILE,
            mode="a",
            header=False,
            index=False
        )
        print(f"DATA APPENDED TO: {DATA_FILE}")

    except Exception as e:
        print(f"DATA APPEND FAILED: {e}")


def main():
    action_map = {
        "NORMAL": "CONTINUE",
        "OVERHEATING": "STOP_MACHINE",
        "HIGH_VIBRATION": "STOP_MACHINE",
        "MOTOR_OVERLOAD": "STOP_MACHINE",
        "LOW_PRESSURE": "REPAIR_MACHINE"
    }

    for tick in range(1, 11):
        reading = generate_sensor_data()

        input_data = pd.DataFrame([reading], columns=FEATURES)
        prediction = model.predict(input_data)[0]

        rule_name, rule_state, rule_action = evaluate_rules(reading)

        final_state = prediction
        action = action_map.get(final_state, "WARNING")
        source = "DECISION TREE"

        if rule_name is not None:
            source = "DECISION TREE (RULE CHECKED)"

        outcome = take_action(action)

        print(f"\n[TICK {tick:02d}] SENSE -> {reading}")
        print(f"MODEL PREDICTION -> {prediction}")
        print(f"TRIGGERED RULE -> {rule_name or 'NONE'}")
        print(f"RULE STATE -> {rule_state or 'NONE'}")
        print(f"FINAL STATE -> {final_state}")
        print(f"DECISION SOURCE -> {source}")
        print(f"ACT -> {outcome}")

        log_decision(reading, prediction, rule_name, final_state, action)
        append_to_dataset(reading, final_state)

        time.sleep(0.2)


if __name__ == "__main__":
    main()