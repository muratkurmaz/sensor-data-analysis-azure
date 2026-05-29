import logging
import azure.functions as func
import os
import random
import pyodbc
from datetime import datetime

# Validate required environment variables and raise an error if any are missing
required_env_vars = ["DatabaseName", "TableName", "SqlConnectionString"]
missing_vars = [var for var in required_env_vars if var not in os.environ]
if missing_vars:
    raise EnvironmentError(f"Missing environment variables: {', '.join(missing_vars)}")

# Configure SQL driver and connection string
# DatabaseName, TableName, SqlConnectionString are currently as placeholder.
SQLDRIVER = "Driver={ODBC Driver 18 for SQL Server};"
DATABASE_NAME = os.environ["DatabaseName"]
TABLE_NAME = os.environ["TableName"]
CONNECTION_STRING = SQLDRIVER + os.environ["SqlConnectionString"]

# Initialize Azure Function App
app = func.FunctionApp()

# Placeholder function for input validation
def validate_input(req):
    # Implement specific validation logic based on your requirements
    pass

# Define Azure Function with HTTP trigger
@app.function_name(name="Sensor_Data_Creation")
@app.route(methods=["GET", "POST"], route="generate")
def Sensor_Data_Creation(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # Validate input (if necessary)
        validate_input(req)
        logging.info("HTTP trigger function processed a request.")

        # Define the number of sensors and readings per sensor
        num_sensors = 20
        readings_per_sensor = 10

        # Generate sensor readings with timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        readings = [
            {
                "Sensor_ID": i,
                "Temperature": random.randint(8, 15),  # Temperature in degrees Celsius
                "Wind": random.uniform(15, 25),  # Wind speed in km/h
                "Relative_Humidity": random.randint(40, 70),  # Relative Humidity in %
                "CO2": random.randint(500, 1500),  # CO2 levels in ppm
                "Time_stamp": timestamp,
            }
            for i in range(num_sensors) for _ in range(readings_per_sensor)
        ]

        # Connect to the database and insert readings
        with pyodbc.connect(CONNECTION_STRING) as conn:
            cur = conn.cursor()

            # Check if the table exists, create it if not
            if not cur.tables(table=TABLE_NAME, tableType="TABLE").fetchone():
                logging.info(f"Creating table {TABLE_NAME}.")
                create_table_sql = (
                    f"CREATE TABLE {TABLE_NAME}("
                    "id int IDENTITY(1,1) PRIMARY KEY, "
                    "Sensor_ID int, Temperature int, Wind float, "
                    "Relative_Humidity int, CO2 int, Time_stamp datetime)"
                )
                cur.execute(create_table_sql)
                conn.commit()
                logging.info("Table created.")
            else:
                logging.info(f"Table {TABLE_NAME} exists.")

            # Insert the generated readings into the database
            cur.executemany(
                f"INSERT INTO {TABLE_NAME} (Sensor_ID, Temperature, Wind, Relative_Humidity, CO2, Time_stamp) VALUES (?,?,?,?,?,?)",
                [(r["Sensor_ID"], r["Temperature"], r["Wind"], r["Relative_Humidity"], r["CO2"], r["Time_stamp"]) for r in readings]
            )
            conn.commit()

        return func.HttpResponse(
            f"This HTTP triggered function executed successfully. Data Is Generated {len(readings)} readings. Synthetic Data for Sensor has been sent to the database",
            status_code=200
        )
    except pyodbc.Error as e:
        # Log database errors and return a server error response
        logging.error(f"Database error: {e}")
        return func.HttpResponse(
            "An error occurred while processing the request.",
            status_code=500
        )
    except Exception as e:
        # Log unexpected errors and return a server error response
        logging.error(f"Unexpected error: {e}")
        return func.HttpResponse(
            "An error occurred while processing the request.",
            status_code=500
        )

