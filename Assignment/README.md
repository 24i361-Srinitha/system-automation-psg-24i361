# Robotic Arm Joint Health Monitoring System

Educational simulation for the 23IF02 System Automation bonus challenge.

## Included
- `main.py`: Random Forest wear classifier, deterministic safety stop, maintenance-note signal, spoof checks, final decision, JSONL logging.
- `data/historical_readings.csv`: 120 synthetic labeled readings.
- `maintenance_log.txt`: 10 technician notes, including relevant and irrelevant notes.
- `explanation.md`: design and limitations.
- `requirements.txt`: dependencies.

## Run in VS Code / PowerShell
```powershell
python -m pip install -r requirements.txt
python main.py --examples
```
Or try one reading:
```powershell
python main.py --arm ARM-01 --joint shoulder --torque 42 --temperature 55 --vibration 2
```
The decisions are appended to `decision_log.jsonl`.

## Safety note
This is a classroom simulation only. Sensor thresholds and generated data are illustrative, not validated for real machinery. Do not connect it to a real robot or use it as an industrial safety system.
