import azure.functions as func
import logging
import pyodbc
import os
import json

def get_db_connection():
    # Establish a database connection using environment variables
    SQLDRIVER = "Driver={ODBC Driver 18 for SQL Server};"
    DATABASE_NAME = os.environ.get("DatabaseName")
    TABLE_NAME = os.environ.get("TableName")
    CONNECTION_STRING = SQLDRIVER + os.environ.get("SqlConnectionString")

    if not DATABASE_NAME or not TABLE_NAME or not CONNECTION_STRING:
        raise ValueError("Database configuration is not set properly.")

    return pyodbc.connect(CONNECTION_STRING), TABLE_NAME

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.function_name(name="data_statistics_sensor")
@app.route(route="data_statistics_sensor")
def data_statistics_sensor(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # Get database connection and table name
        conn, TABLE_NAME = get_db_connection()
        cur = conn.cursor()

        # Check if the table exists in the database
        if not cur.tables(table=TABLE_NAME, tableType="TABLE").fetchone():
            return func.HttpResponse("Sensor data has not found!!", status_code=404)

        # Fetch distinct sensor IDs from the table
        sensors_in_use = [row[0] for row in cur.execute(f"SELECT DISTINCT Sensor_ID FROM {TABLE_NAME} ORDER BY Sensor_ID ASC")]

        # Initialize a dictionary to store statistics
        stats = {}
        data_points = ["Temperature", "Wind", "CO2", "Relative_Humidity"]
        for sensor in sensors_in_use:
            # Calculate and store min, max, and average for each data point
            stats[sensor] = {dat: cur.execute(f"SELECT MIN({dat}), MAX({dat}), AVG({dat}) FROM {TABLE_NAME} WHERE Sensor_ID = ?", sensor).fetchone() for dat in data_points}

        # Return the calculated statistics as a JSON response
        logging.info("Data has analysed and Statistics has created.")
        return func.HttpResponse(json.dumps(stats), status_code=200)

    except pyodbc.Error as e:
        # Log database errors and return an error response
        logging.error(f"Database error: {e}")
        return func.HttpResponse("Database error occurred.", status_code=500)
    except Exception as e:
        # Log unexpected errors and return an error response
        logging.error(f"Unexpected error: {e}")
        return func.HttpResponse("An unexpected error occurred.", status_code=500)
    finally:
        # Ensure the database connection is closed
        conn.close()
