"""
Shared Snowflake connection used by all models.
Credentials are loaded from the .env file in the project root.
"""

import os
import pandas as pd
import snowflake.connector
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    """Return a Snowflake connection using SSO authentication.
    A browser window will open on first run to complete SSO login.
    """
    return snowflake.connector.connect(
        user=os.getenv("SNOWFLAKE_USER"),
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        authenticator="externalbrowser"
    )


def query(sql: str) -> pd.DataFrame:
    """Run a SQL query and return results as a DataFrame."""
    conn = get_connection()
    try:
        return pd.read_sql(sql, conn)
    finally:
        conn.close()
