CSCI 4333 Project - Swarm Robot Trajectory

How it works:

This Python file creates a database called robot.db that uses the CSV files given for the project. It puts robot names, their locations over time, and event intervals into 3 tables.

Then it runs SQL queries to answer:
- The max/min X and Y positions each robot reached
- Where and when "Astro" and "IamHuman" got close to each other
- If robots moved slower than 0.2 cm/s during any interval

To make it run:
1. You need to have Python installed and up to date and have the CSV files in the same folder.
2. Then you run the python run_analysis.py file.
3. Lastly everything prints out in the terminal.
