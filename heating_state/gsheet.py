import json
import os

import gspread

from functools import lru_cache


@lru_cache(maxsize=1)
def open_gsheet(sheet_name: str) -> gspread.Spreadsheet:
    """Initialize spreadsheet access."""
    gspread_credentials = json.loads(os.environ["GSPREAD_SA"])
    gspread_credentials_private_key = os.environ["GSPREAD_SA_KEY"]
    gspread_credentials["private_key"] = gspread_credentials_private_key.replace(
        "\\n", "\n"
    )

    service_account = gspread.service_account_from_dict(gspread_credentials)
    return service_account.open(sheet_name)
