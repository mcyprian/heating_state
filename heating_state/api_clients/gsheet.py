import gspread

from typing import Generator
from heating_state.config import compose_gspread_credentials, GSHEET_NAME


def get_gsheet() -> Generator:
    """Get spreadsheet client."""
    service_account = gspread.service_account_from_dict(compose_gspread_credentials())
    sheet = service_account.open(GSHEET_NAME)
    try:
        yield sheet
    finally:
        sheet.client.session.close()
