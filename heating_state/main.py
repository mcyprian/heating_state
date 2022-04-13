from __future__ import annotations

import enum
import json
import os
import secrets
from pprint import pprint
from typing import Any


from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from .models import Snapshot, DeviceSnapshotWriter
from .api_clients import salus
from .gsheet import open_gsheet


AUTH_TOKEN = None

EMAIL = "skala.lukas@gmail.com"
PASSWORD = os.environ["SALUS_PASSWORD"]

BASIC_AUTH_USERS = json.loads(os.environ["BASIC_AUTH_USERS"])


class Devices(enum.Enum):
    prizemie_chodba = "0.03 Prízemie chodba"
    suteren = "T. Suterén"


ACTIVE_DEVICES = (Devices.suteren.value, Devices.prizemie_chodba.value)


async def add_snapshot_to_worksheet(
    device_writers: dict[str, DeviceSnapshotWriter],
    auth_token: str,
):
    """Create new snapshot and append rows to worksheet."""
    device_properties = await salus.get_mapped_properties(auth_token)

    for device in device_properties:
        device_name = device["name"]
        device_writer = device_writers.get(device_name)

        if device_writer is None:
            continue

        for device_property in device["properties"]["property"]:
            value = device_property["value"]

            if device_property["name"].endswith("x100") and value is not None:
                value = value / 100

            device_writer.add_property(device_property["name"], value)

        pprint(list(device_writer.parsed_properties.values()))

        device_writer.write_snapshot()


app = FastAPI()
security = HTTPBasic()


def validate_credentials(credentials: HTTPBasicCredentials) -> str:
    password = BASIC_AUTH_USERS.get(credentials.username)

    if password is None:
        correct_password = False
    else:
        correct_password = secrets.compare_digest(credentials.password, password)

    if not correct_password:
        raise HTTPException(
            status_code=401,
            detail="Incorrect name or password",
            headers={"WWW-Authenticate": "Basic"},
        )

    return credentials.username


@app.post("/snapshots")
async def create_snapshot(
    snapshot: Snapshot, credentials: HTTPBasicCredentials = Depends(security)
) -> dict[str, Any]:
    validate_credentials(credentials)

    sheet = open_gsheet(snapshot.sheet_name)

    devices = {
        device_name: DeviceSnapshotWriter(device_name, sheet.worksheet(device_name))
        for device_name in ACTIVE_DEVICES
    }

    global AUTH_TOKEN
    if AUTH_TOKEN is None:
        AUTH_TOKEN = await salus.get_auth_token(EMAIL, PASSWORD)

    try:
        await add_snapshot_to_worksheet(devices, AUTH_TOKEN)
        return {
            "status": "ok",
            "message": f"snapshot added to sheet {snapshot.sheet_name}",
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"ERROR: {type(exc)} {exc}")
