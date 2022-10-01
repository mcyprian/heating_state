from __future__ import annotations
from typing import Any
from dataclasses import dataclass

import arrow
import enum
import gspread_asyncio
from pydantic import BaseModel


class Devices(enum.Enum):
    suteren = "T. Suterén 14°"
    prizemie_chodba = "0.03 Prízemie chodba"
    prizemie_obyv_kuchyna = "0.01, 0.02 Príz. obýv, kuchyňa"
    prizemie_hostovska = "0.04 Prízemie hosťovská"
    prizemie_kupelna = "0.06 Prízemie kúpelňa"
    poschodie_chodba = "1.05 Posch chodba nepripoj"
    poschodie_satnik = "1.03 Poschodie šatník"
    poschodie_mala_detska = "1.02 Poschodie malá detská"
    poschodie_kupelna = "1.06 Poschodie kúpeľňa"
    poschodie_spalna = "1.04 Poschodie spálňa"
    poschodie_detska = "1.01 Poschodie detská veľká"


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


class Snapshot(BaseModel):
    device_name: Devices

    class Config:
        use_enum_values = True


@dataclass
class DeviceSnapshotWriter:
    name: str
    worksheet: gspread_asyncio.AsyncioGspreadWorksheet
    parsed_properties: dict[str, Any] | None = None

    @staticmethod
    def _get_current_time() -> str:
        current_utc = arrow.utcnow()
        return current_utc.to("Europe/Prague").format("YYYY-MM-DD HH:mm:ss ZZ")

    def add_property(self, name: str, value: str):
        if self.parsed_properties is None:
            self.parsed_properties = {
                "local_time": self._get_current_time(),
                name: value,
            }
        else:
            self.parsed_properties[name] = value

    async def write_snapshot(self):
        await self.worksheet.append_row(list(self.parsed_properties.values()))
