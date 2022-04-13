from __future__ import annotations
from typing import Any
from dataclasses import dataclass

import arrow
import gspread
from pydantic import BaseModel


class Snapshot(BaseModel):
    sheet_name: str


@dataclass
class DeviceSnapshotWriter:
    name: str
    worksheet: gspread.worksheet.Worksheet
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

    def write_snapshot(self):
        self.worksheet.append_row(list(self.parsed_properties.values()))
