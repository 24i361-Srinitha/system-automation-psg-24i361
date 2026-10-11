
import random
import time
import json
from datetime import datetime

LOG_FILE = "day1_log.txt"

def generate_sensor_data():
    return {
        "temperature": random.uniform(50,95),   
        "pressure": random.uniform(1.0,10.0),     
        "vibration": random.uniform(0.0,5.0),  
        "current": random.uniform(0.5,25.0)   
    }

RULES = [
    {"name": "HIGH_TEMP","priority": 1,"condition": lambda r: r["temperature"] is not None and r["temperature"] > 80, "action": "STOP_MACHINE"},
    {"name": "MED_TEMP","priority": 5,"condition": lambda r: r["temperature"] is not None and r["temperature"] > 50,"action": "REPAIR_MACHINE"},
    {"name": "LOW_TEMP","priority": 6,"condition": lambda r: r["temperature"] is not None and r["temperature"] > 15,"action": "CONTINUE"},
    {"name": "HIGH_VIBRATION","priority": 2,"condition": lambda r: r["vibration"] is not None and r["vibration"] > 8.5, "action": "STOP_MACHINE"},
    {"name": "HIGH_PRESSURE","priority": 3,"condition": lambda r: r["pressure"] is not None and r["pressure"] > 3.5,"action": "STOP"},
    {"name": "LOW_PRESSURE","priority": 7,"condition": lambda r: r["pressure"] is not None and r["pressure"] < 1.0,"action": "REPAIR_MACHINE"},
    {"name": "HIGH_CURRENT","priority": 4,"condition": lambda r: r["current"] is not None and r["current"] >20.0,"action": "WARNING"}
]


def evaluate_rules(reading, rules):
    rules=sorted(rules,key=lambda x:x['priority'])
    for i in rules:
        if i["condition"](reading):
            return i['name'],i['action']

    return "NO_RULE_FIRED", "CONTINUE_NORMAL"

def take_action(action):
    actions = {"STOP_MACHINE": "EMERGENCY! Stop machine.",
        "REPAIR_MACHINE": "Maintenance required.",
        "CONTINUE": "Continue normal Operation",
        "STOP": "HIGH PRESSURE ALERT!, Reduce the pressure immediately.",
        "WARNING": "Current exceeding, action required!"}

    return actions.get(action, f"(no handler yet for action: {action})")

def log_decision(reading, rule_name, action):
    log_entry = {"timestamp": datetime.now().isoformat(timespec="seconds"),"reading": reading,"rule": rule_name,"action": action}

    with open(LOG_FILE, "a", encoding="utf-8") as file:
        file.write(json.dumps(log_entry) + "\n")

def main():
    for tick in range(1, 11):
        reading = generate_sensor_data()
        rule_name, action = evaluate_rules(reading, RULES)
        outcome = take_action(action)

        print(f"[Tick {tick:02d}] SENSE -> {reading}")
        print(f"           THINK -> {rule_name}")
        print(f"           ACT   -> {outcome}\n")

        log_decision(reading, rule_name, action)
        time.sleep(0.2)


if __name__ == "__main__":
    main()