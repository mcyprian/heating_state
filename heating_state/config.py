from __future__ import annotations
from typing import Any
import json
import os
from functools import lru_cache

BASIC_AUTH_USERS = json.loads(os.environ["BASIC_AUTH_USERS"])

SALUS_BASE_API_URL = "https://eu.salusconnect.io"

SALUS_BASE_HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Heating state history script (Lukas Skala)",
}

SALUS_EMAIL = "skala.lukas@gmail.com"
SALUS_PASSWORD = os.environ["SALUS_PASSWORD"]

GSPREAD_CREADENTIALS = json.loads(os.environ["GSPREAD_SA"])
GSPREAD_PRIVATE_KEY = os.environ["GSPREAD_SA_KEY"]
GSHEET_NAME = "HistoriaKureniaLukas"


@lru_cache(maxsize=1)
def compose_gspread_credentials() -> dict[str, Any]:
    return {
        **GSPREAD_CREADENTIALS,
        **{"private_key": GSPREAD_PRIVATE_KEY.replace("\\n", "\n")},
    }
