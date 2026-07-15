import sqlite3
import pandas as pd

conn = sqlite3.connect("D:\OEE_INTERNSHIP\oee_data.db")
cursor = conn.cursor()

# ---- Create machines table ----
cursor.execute("DROP TABLE IF EXISTS machines")
cursor.execute("""
CREATE TABLE machines (
    machine_id TEXT PRIMARY KEY,
    target_rate_per_hour INTEGER,
    machine_type TEXT
)
""")

machines_data = [
    ("PNEU-M1", 60, "Standard pneumatic actuator line"),
    ("PNEU-M2", 55, "Older pneumatic actuator line"),
    ("PNEU-M3", 65, "Newer pneumatic actuator line"),
]
cursor.executemany("INSERT INTO machines VALUES (?, ?, ?)", machines_data)

# ---- Create production_logs table ----
cursor.execute("DROP TABLE IF EXISTS production_logs")
cursor.execute("""
CREATE TABLE production_logs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    machine_id TEXT,
    shift TEXT,
    planned_production_time_min REAL,
    downtime_min REAL,
    downtime_reason TEXT,
    units_produced INTEGER,
    defective_units INTEGER,
    FOREIGN KEY (machine_id) REFERENCES machines(machine_id)
)
""")

# ---- Load CSV data into production_logs ----
df = pd.read_csv("D:\OEE_INTERNSHIP\production_logs.csv")

# only keep columns that match the table (we don't need target_rate_per_hour here
# since it's already stored in the machines table -- avoids duplicate data)
df_to_load = df[[
    "date", "machine_id", "shift", "planned_production_time_min",
    "downtime_min", "downtime_reason", "units_produced", "defective_units"
]]

df_to_load.to_sql("production_logs", conn, if_exists="append", index=False)

conn.commit()

# ---- Quick sanity check ----
check = pd.read_sql("SELECT COUNT(*) as total_rows FROM production_logs", conn)
print("Rows loaded into production_logs:", check["total_rows"][0])

check2 = pd.read_sql("SELECT * FROM production_logs LIMIT 5", conn)
print(check2)

conn.close()
print("\nDatabase created at: D:\OEE_INTERNSHIP\oee_data.db")
