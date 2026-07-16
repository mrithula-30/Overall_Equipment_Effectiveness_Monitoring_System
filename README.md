[README.md](https://github.com/user-attachments/files/30074103/README.md)
# Pneumatic  OEE Dashboard Implementation Guide

## What this project does
Simulates a pneumatic assembly line with 3 machines running 3 shifts a day
for 60 days, then calculates **OEE (Overall Equipment Effectiveness)** —
the industry-standard metric for how well automated equipment is being used.

OEE = Availability × Performance × Quality

- **Availability** — how much of the planned time the machine actually ran (vs. downtime)
- **Performance** — how fast it ran compared to its ideal target speed
- **Quality** — how many units it made were actually good (not defective)

## Files in this project
| File | What it does |
|---|---|
| `01_generate_data.py` | Creates synthetic shift-level production data → `production_logs.csv` |
| `02_load_to_sqlite.py` | Loads that CSV into a proper SQLite database (`oee_data.db`) with 2 tables |
| `03_calculate_oee.py` | Runs SQL + Python to calculate OEE → outputs 2 CSVs for your dashboard |
| `oee_data.db` | The SQLite database itself — open it directly in DB Browser for SQLite if you want to poke around |
| `oee_shift_level.csv` | One row per machine per shift per day — your main Power BI data source |
| `oee_machine_summary.csv` | One row per machine — good for KPI cards |

## How to run it yourself
```bash
python3 01_generate_data.py
python3 02_load_to_sqlite.py
python3 03_calculate_oee.py
```
Run them in that order — each step depends on the file the previous one created.

## Database design (why 2 tables, not 1 big CSV)
- `machines` — static info (machine ID, target speed). Doesn't change often.
- `production_logs` — one row per machine per shift per day. Changes constantly.

This is basic **normalization**: you don't repeat "target_rate_per_hour" 540
times in the logs table — you store it once in `machines` and JOIN when needed.
Mention this in your report/interview — it shows you understand database
design, not just spreadsheet thinking.

## Connecting to Power BI
Power BI doesn't have a native SQLite connector, so the easiest path is:

**Option A (simplest): Load the CSV directly**
1. Open Power BI Desktop → Get Data → Text/CSV
2. Select `oee_shift_level.csv`
3. Build your visuals directly from this (recommended for your first pass)

**Option B (shows more SQL skill): Connect Power BI to SQLite via ODBC**
1. Install the SQLite ODBC driver (search "sqliteodbc" — it's a small free installer)
2. In Windows, set up an ODBC Data Source pointing to `oee_data.db`
3. In Power BI: Get Data → ODBC → select your SQLite data source
4. You can now write live SQL queries inside Power BI itself

For your first working version, go with **Option A** — get the dashboard done,
then upgrade to Option B if you have time and want the extra "connected to a
real database" story for interviews.

## Suggested Power BI dashboard layout
1. **Top row (KPI cards):** Overall OEE %, Availability %, Performance %, Quality %
2. **Line chart:** OEE trend over the 60 days (date on x-axis)
3. **Bar chart:** Average OEE by machine (PNEU-M1 vs M2 vs M3) — shows M2 is the weak one
4. **Bar chart:** Downtime minutes by reason (Pareto style — biggest cause first)
5. **Matrix/table:** Shift (Morning/Afternoon/Night) vs Machine, colored by OEE — spot patterns
   like "Night shift always underperforms"

## What to say in your report/interview
- Explain OEE in plain terms first (the 3 components), then show your numbers.
- Point out **PNEU-M2 has the lowest OEE (~77.5%)** — tie it back to the "older
  machine" story: higher downtime tendency, lower quality.
- Mention that real OEE data isn't public, so this is a synthetic dataset
  built with realistic distributions (gamma-distributed downtime, normal-distributed
  defect rates) — this is a legitimate, commonly used approach when real
  industrial data isn't accessible, as long as you're transparent about it.
- If you have time, add one ML angle: a simple regression predicting OEE from
  downtime_reason + shift + machine_id — turns this from purely descriptive
  into a "predictive" story too (nice for the "full stack" tools you wanted to show).

## Possible next steps
- Add a simple `scikit-learn` model predicting next-shift OEE based on recent trend
- Add a Streamlit app as an alternative to Power BI if you want something
  Python-only and shareable via a link
