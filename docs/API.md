# API Documentation

## Base URL
`http://localhost:8000/api/v1`

## Endpoints

### Health
`GET /health`
Returns the status of the backend and database.

### Telemetry Ingestion
`POST /telemetry`
Accepts JSON payload of normalized network events from sensors.

### Alerts
`GET /alerts`
Returns a list of active alerts and forecasted threats.

### Assets
`GET /assets`
Returns a list of discovered network assets and their risk profiles.
