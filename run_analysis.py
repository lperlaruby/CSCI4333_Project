import sqlite3
import pandas as pd
import numpy as np

# =========================================================================================================================
# Task 2:Build a database (named as robot.db) via Python and SQLite and import the data in the CSV file into the database.
# =========================================================================================================================

# To make the database connection
conn = sqlite3.connect("robot.db")
cur = conn.cursor()

# Creates the three tables: Robot, Trajectory (positions), TargetInterval (event windows)
cur.executescript("""
DROP TABLE IF EXISTS Robot;
DROP TABLE IF EXISTS Trajectory;
DROP TABLE IF EXISTS TargetInterval;

CREATE TABLE Robot (
  robot_id INTEGER PRIMARY KEY,
  name TEXT
);

CREATE TABLE Trajectory (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  robot_id INTEGER,
  timestamp INTEGER,
  x REAL,
  y REAL
);

CREATE TABLE TargetInterval (
  interval_id INTEGER PRIMARY KEY AUTOINCREMENT,
  start_time INTEGER,
  end_time INTEGER,
  event_type TEXT
);
""")

# Loads the robots information and event intervals
robot = pd.read_csv("robot.csv", names=['robot_id', 'name'])
interval = pd.read_csv("interval.csv", names=['start_time', 'end_time', 'event_type'])

robot.to_sql("Robot", conn, if_exists="append", index=False)
interval.to_sql("TargetInterval", conn, if_exists="append", index=False)

# Loads the position data for each robot (t1 to t5)
for i in range(1, 6):
    df = pd.read_csv(f"t{i}.csv")
    df["robot_id"] = i
    df["timestamp"] = df.index + 1
    df.columns = ["x", "y", "robot_id", "timestamp"]
    df.to_sql("Trajectory", conn, if_exists="append", index=False)

# =================================================================================================================================
# Task 3:Using SQL, return the following information related to meta-info of the data (print out the query result is sufficient).
#1. A table consists of the names of robots and the maximal x-axis, minimum x-axis reached by this robot.
#2. A table consists of the names of robots and the maximal y-axis, minimum y-axis reached by this robot.
# ==================================================================================================================================

# Task 3.1: Max and min x values for each robot
print("\n Max & Min X per Robot ")
print(pd.read_sql("""
SELECT name, MAX(x) as max_x, MIN(x) as min_x
FROM Robot JOIN Trajectory USING(robot_id)
GROUP BY name;
""", conn))

# Task 3.2:he max and min y values for each robot
print("\n Max & Min Y per Robot ")
print(pd.read_sql("""
SELECT name, MAX(y) as max_y, MIN(y) as min_y
FROM Robot JOIN Trajectory USING(robot_id)
GROUP BY name;
""", conn))

# =================================================================================================================================
# Task 4: Using SQL, write code to analyze the following info related to robot trajectory:
#1. Suppose we define two robots are close with each other if 'both x-axis and y-axis' difference is smaller than 1 cm. 
# Return all the regions (measured by x min, x max, y min, y max) that robot "Astro" and "IamHuman" are closed with each other.
#2. For the same robots, measured how many secs that they are close with each other.
# =================================================================================================================================

# This gets the robot IDs from name
ids = pd.read_sql("SELECT * FROM Robot", conn).set_index("name")["robot_id"]
astro = ids["Astro"]
iamhuman = ids["IamHuman"]

# Task 4.1: Finds the region where Astro and IamHuman were less than 1 cm apart
print("\nRegion Where Astro & IamHuman Are Close ")
print(pd.read_sql(f"""
SELECT MIN(a.x) as x_min, MAX(a.x) as x_max,
       MIN(a.y) as y_min, MAX(a.y) as y_max
FROM Trajectory a JOIN Trajectory b ON a.timestamp = b.timestamp
WHERE a.robot_id = {astro} AND b.robot_id = {iamhuman}
AND ABS(a.x - b.x) < 1 AND ABS(a.y - b.y) < 1;
""", conn))

# Task 4.2: Counts how many seconds they were close
print("\n Seconds They Are Close ")
print(pd.read_sql(f"""
SELECT COUNT(*) as seconds_close
FROM Trajectory a JOIN Trajectory b ON a.timestamp = b.timestamp
WHERE a.robot_id = {astro} AND b.robot_id = {iamhuman}
AND ABS(a.x - b.x) < 1 AND ABS(a.y - b.y) < 1;
""", conn))
# =========================================================================================
# This is for the bonus which checks if speed during intervals is under 0.2 cm/s
print("\n Speed Check Under 0.2 cm/s ")
results = []
for idx, row in interval.iterrows():
    start, end = row["start_time"], row["end_time"]
    t = pd.read_sql(f"""
        SELECT * FROM Trajectory
        WHERE timestamp BETWEEN {start} AND {end}
        ORDER BY robot_id, timestamp
    """, conn)

    speeds = []
    for rid in t["robot_id"].unique():
        r = t[t["robot_id"] == rid].sort_values("timestamp")
        dx = r["x"].diff()
        dy = r["y"].diff()
        dt = r["timestamp"].diff()
        s = ((dx**2 + dy**2)**0.5 / dt).dropna()
        speeds.extend(s)

    avg = np.mean(speeds) if speeds else 0
    results.append((idx + 1, "Yes" if avg < 0.2 else "No"))

print(pd.DataFrame(results, columns=["Interval_ID", "AvgSpeed<0.2cm/s"]))
conn.close()
