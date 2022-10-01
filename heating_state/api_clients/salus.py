from __future__ import annotations
from typing import Any
import asyncio
from dataclasses import dataclass

import aiohttp
import arrow

from ..config import SALUS_EMAIL, SALUS_PASSWORD, SALUS_BASE_API_URL, SALUS_BASE_HEADERS
from ..models import DeviceProperties


@dataclass
class SalusAuth:
    _access_token: str | None = None
    expiration_time: arrow.Arrow | None = None

    async def _renew_auth_token(
        self,
        email: str,
        password: str,
    ) -> str:
        """Obtain fresh access token."""
        async with aiohttp.ClientSession(headers=SALUS_BASE_HEADERS) as session:
            auth_payload = {"user": {"email": email, "password": password}}

            async with session.post(
                f"{SALUS_BASE_API_URL}/users/sign_in.json", json=auth_payload, ssl=False
            ) as response:
                response.raise_for_status()
                response_json = await response.json()
                self._access_token = response_json["access_token"]
                self.expiration_time = arrow.utcnow().shift(
                    seconds=response_json["expires_in"]
                )

    @property
    def token_expired(self) -> bool:
        return self.expiration_time.shift(minutes=-10) < arrow.utcnow()

    @property
    async def access_token(self) -> str:
        if self._access_token is None or self.token_expired:
            await self._renew_auth_token(SALUS_EMAIL, SALUS_PASSWORD)
        return self._access_token

    @property
    async def auth_header(self) -> str:
        return {"Authorization": f"auth_token {await self.access_token}"}


SALUS_AUTH = SalusAuth()


async def get_device_map(session: aiohttp.ClientSession) -> dict[str, Any]:
    """Get map of device IDs to names."""
    async with session.get(
        f"{SALUS_BASE_API_URL}/apiv1/devices.json",
        ssl=False,
    ) as response:
        response.raise_for_status()
        devices = await response.json()

    return {
        device["device"]["key"]: device["device"]["product_name"] for device in devices
    }


async def get_device_properties(session: aiohttp.ClientSession) -> dict[str, Any]:
    """Get map of properties for each device ID."""
    async with session.get(
        f"{SALUS_BASE_API_URL}/apiv1/groups/62774/datapoints.json",
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


async def get_mapped_properties() -> dict[str, Any]:
    """Get properties mapped to device names."""

    async with aiohttp.ClientSession(
        headers={**SALUS_BASE_HEADERS, **(await SALUS_AUTH.auth_header)}
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
