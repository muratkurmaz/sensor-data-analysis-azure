# Sample Responses

## Data Generation

A successful data generation request returns a message similar to:

```text
This HTTP triggered function executed successfully. Data Is Generated 200 readings. Synthetic Data for Sensor has been sent to the database
```

## Statistics

A successful statistics request returns JSON containing per-sensor values. The output is structured like:

```json
{
  "0": {
    "Temperature": [8, 15, 11.6],
    "Wind": [15.2, 24.8, 20.1],
    "CO2": [520, 1480, 955.4],
    "Relative_Humidity": [42, 69, 55.3]
  }
}
```
