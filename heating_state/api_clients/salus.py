from __future__ import annotations
from typing import Any
import asyncio
import enum

import aiohttp

BASE_API_URL = "https://eu.salusconnect.io"

BASE_HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Heating state history script (Lukas Skala)",
}


class DeviceProperties(enum.Enum):
    temperature = "ep_9:sIT600TH:LocalTemperature_x100"
    running_state = "ep_9:sIT600TH:RunningState"

    cloudy_setpoint = "ep_9:sIT600TH:CloudySetpoint_x100"
    sunny_setpoint = "ep_9:sIT600TH:SunnySetpoint_x100"
    cooling_control = "ep_9:sIT600TH:CoolingControl"
    heating_control = "ep_9:sIT600TH:HeatingControl"
    hold_type = "ep_9:sIT600TH:HoldType"
    sensor_probe = "ep_9:sIT600TH:OUTSensorProbe"
    schedule_type = "ep_9:sIT600TH:ScheduleType"
    running_mode = "ep_9:sIT600TH:RunningMode"
    system_mode = "ep_9:sIT600TH:SystemMode"
    leave_network = "ep_9:sZDO:LeaveNetwork"
    online_status = "ep_9:sZDOInfo:OnlineStatus_i"


def get_auth_header(auth_token: str) -> str:
    return {"Authorization": f"auth_token {auth_token}"}


async def get_auth_token(
    email: str,
    password: str,
) -> str:
    """Obtain fresh auth token."""
    async with aiohttp.ClientSession(headers=BASE_HEADERS) as session:
        auth_payload = {"user": {"email": email, "password": password}}

        async with session.post(
            f"{BASE_API_URL}/users/sign_in.json", json=auth_payload, ssl=False
        ) as response:
            return (await response.json())["access_token"]


async def get_device_map(session: aiohttp.ClientSession) -> dict[str, Any]:
    """Get map of device IDs to names."""
    async with session.get(
        f"{BASE_API_URL}/apiv1/devices.json",
        ssl=False,
    ) as response:
        devices = await response.json()

    return {
        device["device"]["key"]: device["device"]["product_name"] for device in devices
    }


async def get_device_properties(session: aiohttp.ClientSession) -> dict[str, Any]:
    """Get map of properties for each device ID."""
    async with session.get(
        f"{BASE_API_URL}/apiv1/groups/62774/datapoints.json",
        params=[
            ("property_names[]", DeviceProperties.temperature.value),
            ("property_names[]", DeviceProperties.running_state.value),
            ("property_names[]", DeviceProperties.cloudy_setpoint.value),
            ("property_names[]", DeviceProperties.sunny_setpoint.value),
            ("property_names[]", DeviceProperties.cooling_control.value),
            ("property_names[]", DeviceProperties.heating_control.value),
            ("property_names[]", DeviceProperties.hold_type.value),
            ("property_names[]", DeviceProperties.sensor_probe.value),
            ("property_names[]", DeviceProperties.schedule_type.value),
            ("property_names[]", DeviceProperties.running_mode.value),
            ("property_names[]", DeviceProperties.system_mode.value),
            ("property_names[]", DeviceProperties.leave_network.value),
            ("property_names[]", DeviceProperties.online_status.value),
        ],
        ssl=False,
    ) as response:
        return (await response.json())["datapoints"]["devices"]["device"]


async def get_mapped_properties(auth_token: str) -> dict[str, Any]:
    """Get properties mapped to device names."""
    async with aiohttp.ClientSession(
        headers={**BASE_HEADERS, **get_auth_header(auth_token)}
    ) as session:
        device_map, device_properties = await asyncio.gather(
            *[
                get_device_map(session),
                get_device_properties(session),
            ]
        )

    for device in device_properties:
        device["name"] = device_map[device["id"]]

    return device_properties
