import azure.functions as func
import logging
import random
import pyodbc
import os
import json
from datetime import datetime

def get_db_connection():
    # Establish a database connection using environment variables
    SQLDRIVER = "Driver={ODBC Driver 18 for SQL Server};"
    DATABASE_NAME = os.environ["DatabaseName"]
    CONNECTION_STRING = SQLDRIVER + os.environ.get("SqlConnectionString")
    if not CONNECTION_STRING:
        raise ValueError("Database connection string is not set properly.")
    return pyodbc.connect(CONNECTION_STRING)

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.function_name(name="Sensor_Data_Creation")
@app.timer_trigger(schedule="*/5 * * * * *", arg_name="timer", run_on_startup=True, use_monitor=False)
def Sensor_Data_Creation(timer: func.TimerRequest) -> None:
    # Check if the timer is past due
    if timer.past_due:
        logging.info("The timer is past due!")

    # Generate sensor readings for a predefined number of sensors
    num_sensors = 20
    readings = [{
        "Sensor_ID": i,
        "Temperature": random.randint(8, 15),
        "Wind": random.uniform(15, 25),
        "Relative_Humidity": random.randint(40, 70),
        "CO2": random.randint(500, 1500),
        "Time_stamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    } for i in range(num_sensors)]

    # Connect to the database and prepare for data insertion
    conn = get_db_connection()
    cur = conn.cursor()

    # Validate table name environment variable
    TABLE_NAME = os.environ.get("TableName")
    if not TABLE_NAME:
        raise ValueError("Table name is not set properly.")

    # Create the table if it does not exist
    if not cur.tables(table=TABLE_NAME, tableType="TABLE").fetchone():
        create_table_sql = f"CREATE TABLE {TABLE_NAME}(id int IDENTITY(1,1) PRIMARY KEY, Sensor_ID int, Temperature int, Wind float, Relative_Humidity int, CO2 int, Time_stamp datetime)"
        cur.execute(create_table_sql)
        conn.commit()
        logging.info("Table created.")

    # Insert generated readings into the database
    insert_sql = f"INSERT INTO {TABLE_NAME} (Sensor_ID, Temperature, Wind, Relative_Humidity, CO2, Time_stamp) VALUES (?, ?, ?, ?, ?, ?)"
    cur.executemany(insert_sql, [(r["Sensor_ID"], r["Temperature"], r["Wind"], r["Relative_Humidity"], r["CO2"], r["Time_stamp"]) for r in readings])
    conn.commit()
    conn.close()

@app.function_name(name="data_statistics_sensor")
@app.generic_trigger(arg_name="data", type="sqlTrigger", TableName=os.environ.get("TableName"), ConnectionStringSetting="SqlConnectionString", data_type=func.DataType.STRING)
def data_statistics_sensor(data: str) -> None:
    # Connect to the database
    conn = get_db_connection()
    cur = conn.cursor()

    # Validate table name environment variable
    TABLE_NAME = os.environ.get("TableName")
    if not TABLE_NAME:
        raise ValueError("Table has not been set properly.")

    # Check if the table exists and exit early if not
    if not cur.tables(table=TABLE_NAME, tableType="TABLE").fetchone():
        conn.close()
        logging.info("Sensor readings are not available.")
        return

    # Fetch distinct sensor IDs from the table
    sensors_in_use = [row[0] for row in cur.execute(f"SELECT DISTINCT Sensor_ID FROM {TABLE_NAME} ORDER BY Sensor_ID ASC")]

    # Calculate statistics for each sensor
    stats = {}
    data_points = ["Temperature", "Wind", "CO2", "Relative_Humidity"]
    for sensor in sensors_in_use:
        stats[sensor] = {dat: cur.execute(f"SELECT MIN({dat}), MAX({dat}), AVG({dat}) FROM {TABLE_NAME} WHERE Sensor_ID = ?", sensor).fetchone() for dat in data_points}

    # Log and return the calculated statistics
    conn.commit()
    conn.close()
    logging.info("Data is analysed and Statistics are created.")
    logging.info(json.dumps(stats))
