import csv
import random

NUM_READINGS = 250

def stat(temp, press, vib, rpm, current):
    if temp > 85 or press > 8.5 or vib > 4.0 or rpm > 3200 or current > 22.0:
        return "Failure"
    elif temp > 70 or press > 6.5 or vib > 3.5 or rpm > 2800 or current > 18.0:
        return "Warning"
    else:
        return "Normal"

data = []
for i in range(1, NUM_READINGS + 1):
    temp = round(random.uniform(50,95), 1)  
    p = round(random.uniform(1.0,10.0), 1)     
    v = round(random.uniform(0.0,5.0), 2)     
    rpm = random.randint(1000, 3500)                    
    cur = round(random.uniform(0.5,25.0), 1)       
    
    status = stat(temp, p, v, rpm, cur)
    
    data.append([temp, p, v, rpm, cur, status])

header = ['Temperature', 'Pressure', 'Vibration', 'RPM', 'Current', 'Output']

with open('sensor_readings.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(header)
    writer.writerows(data)

