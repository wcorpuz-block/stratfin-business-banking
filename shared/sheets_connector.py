"""
Google Sheets connector used by all models.
Requires a service account credentials JSON file.
Set GOOGLE_CREDENTIALS_PATH in your .env file.
"""

import os
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

load_dotenv()

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]


def get_client():
    """Return an authenticated gspread client."""
    creds_path = os.getenv("GOOGLE_CREDENTIALS_PATH")
    if not creds_path:
        raise EnvironmentError("GOOGLE_CREDENTIALS_PATH is not set in your .env file.")
    creds = Credentials.from_service_account_file(creds_path, scopes=SCOPES)
    return gspread.authorize(creds)


def write_dataframe(spreadsheet_url: str, sheet_name: str, df: pd.DataFrame, clear: bool = True):
    """
    Write a DataFrame to a named tab in a Google Sheet.

    Args:
        spreadsheet_url: Full URL of the Google Sheet
        sheet_name:      Name of the tab to write to (creates it if it doesn't exist)
        df:              DataFrame to write
        clear:           If True, clears existing content before writing
    """
    client = get_client()
    spreadsheet = client.open_by_url(spreadsheet_url)

    # Get or create the worksheet tab
    try:
        worksheet = spreadsheet.worksheet(sheet_name)
    except gspread.exceptions.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=50)

    if clear:
        worksheet.clear()

    # Write header + data
    data = [df.columns.tolist()] + df.astype(str).values.tolist()
    worksheet.update(data)
    print(f"Written to Google Sheet tab '{sheet_name}'.")
