import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, List, Mapping, Tuple

from .exceptions import DoeParseError


@dataclass(frozen=True)
class DeviceRule:
    cell_pattern: str
    device_type: str
    extractor: str
    options: Mapping[str, Any]


@dataclass(frozen=True)
class PinOrderRule:
    cell_pattern: str
    pins: Tuple[str, ...]


@dataclass(frozen=True)
class DoeCdlConfig:
    testkey_pattern: str
    coordinate_unit: str
    pin_layers: Tuple[Tuple[int, int], ...]
    pin_order_rules: Tuple[PinOrderRule, ...]
    device_rules: Tuple[DeviceRule, ...]

    @classmethod
    def from_file(cls, path: str | Path) -> "DoeCdlConfig":
        config_path = Path(path)
        try:
            with config_path.open(encoding="utf-8") as config_file:
                data = json.load(config_file)
        except OSError as exc:
            raise DoeParseError(f"Cannot read config {config_path}: {exc}") from exc
        except json.JSONDecodeError as exc:
            raise DoeParseError(f"Invalid JSON in config {config_path}: {exc}") from exc

        if not isinstance(data, dict):
            raise DoeParseError("DOE/CDL config must be a JSON object")

        testkey_pattern = data.get("testkey_pattern", "^TL_")
        coordinate_unit = data.get("coordinate_unit", "user_unit")
        if not isinstance(testkey_pattern, str) or not isinstance(coordinate_unit, str):
            raise DoeParseError("'testkey_pattern' and 'coordinate_unit' must be strings")
        _compile_pattern(testkey_pattern, "testkey_pattern")

        raw_pin_layers = data.get("pin_layers", [])
        if not isinstance(raw_pin_layers, list):
            raise DoeParseError("'pin_layers' must be a list")
        pin_layers: List[Tuple[int, int]] = []
        for item in raw_pin_layers:
            if not isinstance(item, dict):
                raise DoeParseError("Each pin layer must be an object")
            layer = item.get("layer")
            texttype = item.get("texttype", 0)
            if not _is_int(layer) or not _is_int(texttype):
                raise DoeParseError("Pin layer and texttype must be integers")
            pin_layers.append((layer, texttype))

        raw_pin_order_rules = data.get("pin_order_rules", [])
        if not isinstance(raw_pin_order_rules, list):
            raise DoeParseError("'pin_order_rules' must be a list")
        pin_order_rules: List[PinOrderRule] = []
        for item in raw_pin_order_rules:
            if not isinstance(item, dict):
                raise DoeParseError("Each pin order rule must be an object")
            cell_pattern = item.get("cell_pattern")
            pins = item.get("pins")
            if not isinstance(cell_pattern, str) or not cell_pattern:
                raise DoeParseError("Each pin order rule requires a non-empty cell_pattern")
            if (
                not isinstance(pins, list)
                or not all(isinstance(pin, str) and pin for pin in pins)
                or len(pins) != len(set(pins))
            ):
                raise DoeParseError("Pin order rule 'pins' must be a list of unique non-empty strings")
            _compile_pattern(cell_pattern, "pin order rule cell_pattern")
            pin_order_rules.append(PinOrderRule(cell_pattern, tuple(pins)))

        raw_rules = data.get("device_rules", [])
        if not isinstance(raw_rules, list):
            raise DoeParseError("'device_rules' must be a list")
        rules: List[DeviceRule] = []
        for item in raw_rules:
            if not isinstance(item, dict):
                raise DoeParseError("Each device rule must be an object")
            cell_pattern = item.get("cell_pattern")
            device_type = item.get("device_type")
            extractor = item.get("extractor")
            options = item.get("options", {})
            if not all(isinstance(value, str) and value for value in (cell_pattern, device_type, extractor)):
                raise DoeParseError(
                    "Each device rule requires non-empty string cell_pattern, device_type, and extractor"
                )
            if not isinstance(options, dict):
                raise DoeParseError("Device rule 'options' must be an object")
            _compile_pattern(cell_pattern, "device rule cell_pattern")
            rules.append(DeviceRule(cell_pattern, device_type, extractor, options))

        return cls(
            testkey_pattern=testkey_pattern,
            coordinate_unit=coordinate_unit,
            pin_layers=tuple(pin_layers),
            pin_order_rules=tuple(pin_order_rules),
            device_rules=tuple(rules),
        )


def _compile_pattern(pattern: str, field: str) -> re.Pattern[str]:
    try:
        return re.compile(pattern)
    except re.error as exc:
        raise DoeParseError(f"Invalid regular expression for {field}: {exc}") from exc


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)
