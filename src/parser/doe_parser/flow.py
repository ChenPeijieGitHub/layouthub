import csv
from pathlib import Path
from typing import Any, Dict, List, Tuple

from generator.cdl_generator import CdlGenerator
from parser.gds_parser import LayoutIo

from .config import DoeCdlConfig
from .exceptions import DoeParseError
from .parser import DoeParser

_BASE_DOE_COLUMNS = [
    "testkey",
    "dut_cell",
    "device_type",
    "coordinate_unit",
]


class LayoutDoeFlow:
    """解析 GDS 中的 testkey/DUT，并输出 DOE CSV 与 CDL 接口骨架。"""

    def __init__(self, gds_path: str | Path, config_path: str | Path):
        self.gds_path = Path(gds_path)
        self.config = DoeCdlConfig.from_file(config_path)

    def run(self, output_dir: str | Path) -> Tuple[Path, Path]:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        doe_path = output_dir / "doe.csv"
        cdl_path = output_dir / "layout.cdl"

        with LayoutIo(self.gds_path) as layout:
            layout.parse()
            top_cells = layout.get_top_cells()
            parser = DoeParser(self.config)
            testkeys = parser.find_testkeys(top_cells)
            if not testkeys:
                raise DoeParseError(
                    f"No top-level testkey matched '{self.config.testkey_pattern}' "
                    f"in {self.gds_path}"
                )
            rows = parser.parse(testkeys)
            self._write_doe(doe_path, rows)

            generator = CdlGenerator(
                self.config.pin_layers,
                [
                    (rule.cell_pattern, rule.pins)
                    for rule in self.config.pin_order_rules
                ],
            )
            generator.write(testkeys, cdl_path)

        return doe_path, cdl_path

    @staticmethod
    def _write_doe(path: Path, rows: List[Dict[str, Any]]) -> None:
        parameter_columns = sorted(
            {key for row in rows for key in row if key not in _BASE_DOE_COLUMNS}
        )
        columns = _BASE_DOE_COLUMNS + parameter_columns
        with path.open("w", encoding="utf-8-sig", newline="") as output_file:
            writer = csv.DictWriter(output_file, fieldnames=columns, extrasaction="raise")
            writer.writeheader()
            writer.writerows(rows)
