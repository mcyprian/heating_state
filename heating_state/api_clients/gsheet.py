import gspread_asyncio
from google.oauth2.service_account import Credentials

from typing import Generator
from heating_state.config import compose_gspread_credentials, GSHEET_NAME


def get_creds():
    creds = Credentials.from_service_account_info(compose_gspread_credentials())
    scoped = creds.with_scopes(
        [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
    )
    return scoped


async def get_gsheet() -> Generator:
    """Get spreadsheet client."""
    gspread_client_manager = gspread_asyncio.AsyncioGspreadClientManager(get_creds)
    gspread_client = await gspread_client_manager.authorize()
    sheet = await gspread_client.open(GSHEET_NAME)
    yield sheet
