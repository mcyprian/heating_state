from __future__ import annotations
from typing import Any

import arrow
from dataclasses import dataclass
import gspread


@dataclass
class DeviceStateWriter:
    name: str
    worksheet: gspread.worksheet.Worksheet
    parsed_properties: dict[str, Any] | None = None

    @staticmethod
    def _get_current_time():
        current_utc = arrow.utcnow()
        return current_utc.to("Europe/Prague").format("YYYY-MM-DD HH:mm:ss ZZ")

    def add_property(self, name, value):
        if self.parsed_properties is None:
            self.parsed_properties = {
                "local_time": self._get_current_time(),
                name: value,
            }
        else:
            self.parsed_properties[name] = value

    def create_sample(self):
        self.worksheet.append_row(list(self.parsed_properties.values()))
