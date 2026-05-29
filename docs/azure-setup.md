# Azure Setup Notes

## 1. Create Azure SQL Database

Create an Azure SQL Server and database, then ensure your local IP address or Function App has access through the SQL firewall rules.

## 2. Install ODBC Driver

The functions use `pyodbc` and ODBC Driver 18 for SQL Server.

On Windows, install the Microsoft ODBC Driver 18 for SQL Server before running locally.

## 3. Configure Function Settings

Set the following application settings either in Azure Portal or in `local.settings.json` for local development:

```text
DatabaseName
TableName
SqlConnectionString
```

## 4. Run with Azure Functions Core Tools

From a function folder:

```bash
func start
```

## 5. Deploy

A typical deployment command is:

```bash
func azure functionapp publish <function-app-name>
```

Use separate Function Apps if you want to deploy each module independently.
