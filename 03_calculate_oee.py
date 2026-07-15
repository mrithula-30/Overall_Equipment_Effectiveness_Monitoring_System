import sqlite3
import pandas as pd

conn = sqlite3.connect("D:\OEE_INTERNSHIP\oee_data.db")

# We join production_logs with machines to get each machine's target rate
# (this is why we split into 2 tables -- SQL joins are the whole point!)

oee_query = """
SELECT
    p.date,
    p.machine_id,
    p.shift,
    p.planned_production_time_min,
    p.downtime_min,
    (p.planned_production_time_min - p.downtime_min) AS run_time_min,
    p.units_produced,
    p.defective_units,
    (p.units_produced - p.defective_units) AS good_units,
    m.target_rate_per_hour,

    -- Availability: run time as a fraction of planned time
    ROUND(
        (p.planned_production_time_min - p.downtime_min) * 1.0
        / p.planned_production_time_min, 4
    ) AS availability,

    -- Performance: actual output rate vs ideal output rate
    ROUND(
        (p.units_produced * 1.0 / NULLIF((p.planned_production_time_min - p.downtime_min), 0))
        / (m.target_rate_per_hour / 60.0), 4
    ) AS performance,

    -- Quality: good units as a fraction of total units
    ROUND(
        (p.units_produced - p.defective_units) * 1.0
        / NULLIF(p.units_produced, 0), 4
    ) AS quality

FROM production_logs p
JOIN machines m ON p.machine_id = m.machine_id
"""

oee_df = pd.read_sql(oee_query, conn)

# OEE = Availability x Performance x Quality (calculated in Python for clarity,
# though you could also do this in the SQL query itself)
oee_df["oee"] = (oee_df["availability"] * oee_df["performance"] * oee_df["quality"]).round(4)

print("Sample OEE calculation per shift:")
print(oee_df[["date", "machine_id", "shift", "availability", "performance", "quality", "oee"]].head(10))

# ---- Save shift-level detail (this becomes your Power BI raw data source) ----
oee_df.to_csv("D:\OEE_INTERNSHIP\oee_shift_level.csv", index=False)

# ---- Also build a summary: average OEE per machine ----
summary_query = """
SELECT machine_id,
       ROUND(AVG(downtime_min), 1) as avg_downtime_min,
       COUNT(*) as total_shifts
FROM production_logs
GROUP BY machine_id
"""
summary = pd.read_sql(summary_query, conn)

# Merge in average OEE components computed in Python (simpler than nested SQL)
machine_summary = oee_df.groupby("machine_id").agg(
    avg_availability=("availability", "mean"),
    avg_performance=("performance", "mean"),
    avg_quality=("quality", "mean"),
    avg_oee=("oee", "mean"),
).reset_index()

machine_summary = machine_summary.round(4)
machine_summary.to_csv("D:\OEE_INTERNSHIP\oee_machine_summary.csv", index=False)

print("\nMachine-level OEE summary:")
print(machine_summary)

conn.close()

print("\nFiles created:")
print("- oee_shift_level.csv     (detailed, one row per shift -- use this in Power BI)")
print("- oee_machine_summary.csv (one row per machine -- good for a quick KPI card)")
