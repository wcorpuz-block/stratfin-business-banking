# Block Business Banking Financial Models

Strategic finance analysis toolkit for Block's Business Banking products — Instant Transfer, Credit Card, and Debit Card.

## Overview

This project automates financial modeling by pulling live data from Snowflake and outputting results directly to Google Sheets, replacing manual SmartView refreshes and CSV copy/paste workflows.

## Project Structure

```
Projects/
├── models/                        # Financial model scripts
│   └── banking_financial_model.py # Core model: revenue, costs, profitability
├── queries/                       # SQL queries for Snowflake
│   └── snowflake_queries.sql
├── shared/                        # Reusable connectors
│   ├── snowflake_connector.py     # Snowflake SSO connection
│   └── sheets_connector.py        # Google Sheets writer
├── docs/                          # Research, templates, and planning docs
├── scripts/                       # Setup and utility scripts
├── outputs/                       # Local Excel outputs (gitignored)
├── credentials/                   # Google service account JSON (gitignored)
├── .env                           # Environment variables (gitignored)
└── .gitignore
```

## Setup

### 1. Install dependencies
```bash
pip install snowflake-connector-python pandas openpyxl gspread google-auth python-dotenv
```

### 2. Configure environment variables
Copy `.env` and fill in your values:
```
SNOWFLAKE_USER=your-email@block.xyz
SNOWFLAKE_ACCOUNT=block.snowflakecomputing.com
SNOWFLAKE_DATABASE=your-database
SNOWFLAKE_SCHEMA=your-schema
SNOWFLAKE_WAREHOUSE=your-warehouse

GOOGLE_CREDENTIALS_PATH=C:\Users\WilliamSpencerCorpuz\Projects\credentials\google_service_account.json
GOOGLE_SHEET_URL=https://docs.google.com/spreadsheets/d/your-sheet-id
```

### 3. Add Google credentials
Place your Google service account JSON file at:
```
credentials/google_service_account.json
```
See [Google Sheets setup instructions](docs/google_sheets_setup.md) for details.

## Running the Model

```bash
python models/banking_financial_model.py
```

This will:
1. Authenticate to Snowflake via SSO (opens browser on first run)
2. Pull live transaction data to update model assumptions
3. Run scenario analysis across customer counts: 1K, 5K, 10K, 25K, 50K
4. Write results to 4 tabs in your Google Sheet

## Data Sources

| Source | What it provides |
|---|---|
| Snowflake | Live transaction volumes and averages |
| EPM Cloud (planned) | Actuals and budget data via REST API |
| Hardcoded assumptions | Fallback when Snowflake is unavailable |
