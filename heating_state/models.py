from typing import Any

from dataclasses import dataclass
import gspread


@dataclass
class DeviceStateWriter:
    name: str
    worksheet: gspread.worksheet.Worksheet
    parsed_properties: dict[str, Any] | None = None

    def add_property(self, name, value):
        if self.parsed_properties is None:
            self.parsed_properties = {name: value}
        else:
            self.parsed_properties[name] = value

    def create_sample(self):
        self.worksheet.append_row(list(self.parsed_properties.values()))
