# Sensor Data Analysis on Azure

Azure Functions project for generating synthetic sensor readings, storing them in Azure SQL, and computing descriptive statistics for each sensor.

The project demonstrates a small serverless data pipeline using Python, Azure Functions, SQL triggers, timer triggers, HTTP endpoints, and an Azure SQL backend.

## Overview

The system is organised into three Azure Function apps:

| Module | Purpose |
|---|---|
| `sensor-data-creation` | HTTP-triggered function that generates synthetic readings and inserts them into Azure SQL |
| `sensor-statistics` | HTTP-triggered function that calculates min, max, and average values per sensor |
| `realistic-scenario` | Timer-triggered data generation combined with SQL-triggered statistics logging |

Each generated record contains:

- Sensor ID
- Temperature
- Wind speed
- Relative humidity
- CO2 level
- Timestamp

## Repository Structure

```text
.
├── assets/                         # Figures and screenshots
├── docs/                           # Architecture and setup notes
├── functions/
│   ├── realistic-scenario/          # Timer + SQL trigger implementation
│   ├── sensor-data-creation/        # HTTP data generation function
│   └── sensor-statistics/           # HTTP statistics function
├── .gitignore
├── requirements.txt
└── README.md
```

## Requirements

- Python 3.10+
- Azure Functions Core Tools
- Azure SQL Database
- ODBC Driver 18 for SQL Server
- Python packages listed in `requirements.txt`

Install Python dependencies:

```bash
pip install -r requirements.txt
```

## Local Configuration

Each function folder contains a `local.settings.example.json` file.

Copy it to `local.settings.json` inside the function app you want to run:

```bash
cp local.settings.example.json local.settings.json
```

Then fill in:

```json
{
  "DatabaseName": "<azure-sql-database-name>",
  "TableName": "SensorReadings",
  "SqlConnectionString": "Server=tcp:<server>.database.windows.net,1433;Database=<database>;Uid=<user>;Pwd=<password>;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
}
```

`local.settings.json` is ignored by Git to avoid committing credentials.

## Running Locally

From one of the function folders, start the Azure Functions host:

```bash
cd functions/sensor-data-creation
func start
```

Then call the HTTP endpoint locally, for example:

```bash
curl http://localhost:7071/api/generate
```

For the statistics endpoint:

```bash
cd functions/sensor-statistics
func start
curl http://localhost:7071/api/data_statistics_sensor
```

## Example Workflow

1. Run `sensor-data-creation` to generate synthetic sensor records.
2. Store records in Azure SQL.
3. Run `sensor-statistics` to calculate per-sensor summary statistics.
4. Use `realistic-scenario` for a more automated setup with scheduled data generation.

## Notes

This is an educational cloud-computing project focused on serverless data ingestion and basic sensor analytics. It is designed to demonstrate Azure Functions, database-backed event processing, and simple statistical aggregation rather than production-grade IoT monitoring.

## Author

Murat Kurmaz

## License

This project is licensed under the MIT License.
