import pandas as pd
import numpy as np
from datetime import datetime, timedelta

np.random.seed(42)  # so you get the same "random" data every time you run this

# ---- Basic setup ----
machines = ["PNEU-M1", "PNEU-M2", "PNEU-M3"]   # 3 pneumatic assembly machines
shifts = ["Morning", "Afternoon", "Night"]
shift_length_minutes = 480  # 8-hour shift = planned production time

start_date = datetime(2026, 1, 1)
num_days = 60

# Each machine has a slightly different "personality" (this is realistic --
# in real factories, some machines are just older/worse than others)
machine_profile = {
    "PNEU-M1": {"downtime_tendency": 1.0, "defect_tendency": 1.0, "target_rate": 60},  # units/hour
    "PNEU-M2": {"downtime_tendency": 1.4, "defect_tendency": 1.2, "target_rate": 55},  # older machine
    "PNEU-M3": {"downtime_tendency": 0.8, "defect_tendency": 0.9, "target_rate": 65},  # newer machine
}

downtime_reasons = [
    "Air pressure drop", "Valve leakage", "Scheduled maintenance",
    "Sensor fault", "Operator break overrun", "Material shortage", "No downtime"
]

rows = []

for day in range(num_days):
    current_date = start_date + timedelta(days=day)
    for machine in machines:
        profile = machine_profile[machine]
        for shift in shifts:

            # --- Downtime simulation ---
            # Most shifts have a little downtime, occasionally a lot
            base_downtime = np.random.gamma(shape=2.0, scale=10) * profile["downtime_tendency"]
            downtime_minutes = min(base_downtime, shift_length_minutes * 0.6)  # cap so it's realistic

            if downtime_minutes < 5:
                reason = "No downtime"
                downtime_minutes = 0
            else:
                reason = np.random.choice(downtime_reasons[:-1])  # exclude "No downtime"

            run_time = shift_length_minutes - downtime_minutes

            # --- Performance simulation ---
            # target units if machine ran at ideal speed for the actual run_time
            target_rate_per_min = profile["target_rate"] / 60
            ideal_units = run_time * target_rate_per_min

            # real machines rarely hit 100% speed -- add realistic slowdowns
            speed_factor = np.clip(np.random.normal(0.85, 0.08), 0.5, 1.0)
            units_produced = int(ideal_units * speed_factor)

            # --- Quality simulation ---
            defect_rate = np.clip(np.random.normal(0.04, 0.015) * profile["defect_tendency"], 0.005, 0.15)
            defective_units = int(units_produced * defect_rate)

            rows.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "machine_id": machine,
                "shift": shift,
                "planned_production_time_min": shift_length_minutes,
                "downtime_min": round(downtime_minutes, 1),
                "downtime_reason": reason,
                "units_produced": units_produced,
                "target_rate_per_hour": profile["target_rate"],
                "defective_units": defective_units,
            })

df = pd.DataFrame(rows)
df.to_csv("D:\OEE_INTERNSHIP\production_logs.csv", index=False)

print(f"Generated {len(df)} rows of data")
print(df.head(10))
