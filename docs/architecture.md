# Architecture Notes

## Components

The project contains three related Azure Function apps.

### Sensor Data Creation

`functions/sensor-data-creation` exposes an HTTP endpoint that generates synthetic sensor readings and writes them to Azure SQL.

The function checks whether the target table exists. If not, it creates a table with the following fields:

- `id`
- `Sensor_ID`
- `Temperature`
- `Wind`
- `Relative_Humidity`
- `CO2`
- `Time_stamp`

### Sensor Statistics

`functions/sensor-statistics` exposes an HTTP endpoint that reads stored sensor data and computes summary statistics for each active sensor.

For each sensor, it calculates:

- minimum
- maximum
- average

for temperature, wind, CO2, and relative humidity.

### Realistic Scenario

`functions/realistic-scenario` combines a timer trigger and SQL trigger style workflow:

1. A timer-triggered function creates new records at regular intervals.
2. A SQL-triggered function reacts to database changes and logs statistics.

## Data Flow

```text
Synthetic sensor generator
        ↓
Azure Function
        ↓
Azure SQL Database
        ↓
Statistics Function
        ↓
JSON summary / logs
```

## Security Notes

Credentials should be stored in Azure Function App settings or local `local.settings.json` during development. Do not commit database credentials to GitHub.
