from __future__ import annotations

import asyncio
from typing import Any
from pprint import pprint

from fastapi import FastAPI, Depends, HTTPException, responses
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import gspread_asyncio

from .devices import GROUND_FLOOR_DEVICES, FIRST_FLOOR_DEVIDES
from .config import GSHEET_NAME
from .models import Snapshot, DeviceSnapshotWriter, FloorName
from .api_clients import salus, gsheet
from .auth import validate_credentials


async def add_snapshot_to_worksheet(
    device_writers: dict[str, DeviceSnapshotWriter],
):
    """Create new snapshot and append rows to worksheet."""
    device_properties = await salus.get_mapped_properties()

    tasks = []

    for device in device_properties:
        device_name = device["name"]
        device_writer = device_writers.get(device_name)

        if device_writer is None:
            continue

        for device_property in device["properties"]["property"]:
            value = device_property["value"]

            if device_property["name"].endswith("x100") and value is not None:
                value = int(value) / 100

            device_writer.add_property(device_property["name"], value)

        pprint(device_writer.parsed_properties)

        tasks.append(device_writer.write_snapshot())

    asyncio.gather(*tasks, return_exceptions=True)


app = FastAPI()
security = HTTPBasic()


@app.get("/")
async def root() -> responses.RedirectResponse:
    return responses.RedirectResponse("/docs", status_code=302)


@app.post("/snapshots")
async def create_snapshot(
    snapshot: Snapshot,
    credentials: HTTPBasicCredentials = Depends(security),
    sheet: gspread_asyncio.AsyncioGspreadSpreadsheet = Depends(gsheet.get_gsheet),
) -> dict[str, Any]:
    validate_credentials(credentials)

    devices_to_check = (
        GROUND_FLOOR_DEVICES
        if snapshot.floor_name == FloorName.ground.value
        else FIRST_FLOOR_DEVIDES
    )

    devices = {
        device_name: DeviceSnapshotWriter(
            device_name, await sheet.worksheet(device_name)
        )
        for device_name in (device.value for device in devices_to_check)
    }

    try:
        await add_snapshot_to_worksheet(devices)
        return {
            "status": "ok",
            "message": f"snapshot added to sheet {GSHEET_NAME}",
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"ERROR: {type(exc)} {exc}")
