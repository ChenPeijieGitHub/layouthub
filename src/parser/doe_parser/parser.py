import re
from typing import Any, Dict, Iterable, List, Sequence

import gdstk

from .config import DoeCdlConfig, DeviceRule
from .exceptions import DoeParseError
from .extractors import extract_parameters

_RESERVED_COLUMNS = {
    "testkey",
    "dut_cell",
    "device_type",
    "coordinate_unit",
}


class DoeParser:
    """从 testkey 层级中匹配的 DUT cell 提取 DOE 数据。"""

    def __init__(self, config: DoeCdlConfig):
        self.config = config
        self._testkey_regex = re.compile(config.testkey_pattern)
        self._rule_regexes = [
            (rule, re.compile(rule.cell_pattern)) for rule in config.device_rules
        ]

    def find_testkeys(self, top_cells: Iterable[gdstk.Cell]) -> List[gdstk.Cell]:
        return sorted(
            (cell for cell in top_cells if self._testkey_regex.search(cell.name)),
            key=lambda cell: cell.name,
        )

    def parse(self, testkeys: Sequence[gdstk.Cell]) -> List[Dict[str, Any]]:
        rows: List[Dict[str, Any]] = []
        for testkey in testkeys:
            for cell in self._hierarchy_cells(testkey):
                rule = self._rule_for_cell(cell)
                if rule is None:
                    continue
                parameters = extract_parameters(rule.extractor, cell, rule.options)
                invalid_columns = [
                    key
                    for key in parameters
                    if not isinstance(key, str)
                    or not key
                    or key in _RESERVED_COLUMNS
                ]
                if invalid_columns:
                    raise DoeParseError(
                        f"Extractor '{rule.extractor}' returned invalid or reserved "
                        f"column names for cell '{cell.name}': {invalid_columns}"
                    )
                rows.append(
                    {
                        "testkey": testkey.name,
                        "dut_cell": cell.name,
                        "device_type": rule.device_type,
                        "coordinate_unit": self.config.coordinate_unit,
                        **parameters,
                    }
                )
        return rows

    def _hierarchy_cells(self, root: gdstk.Cell) -> List[gdstk.Cell]:
        cells: List[gdstk.Cell] = []
        seen = set()
        stack = [root]
        while stack:
            cell = stack.pop()
            if cell in seen:
                continue
            # 重复引用仍指向同一 cell 定义，每个 testkey 仅解析一次。
            seen.add(cell)
            cells.append(cell)
            stack.extend(reference.cell for reference in reversed(cell.references))
        return cells

    def _rule_for_cell(self, cell: gdstk.Cell) -> DeviceRule | None:
        matches = [
            rule
            for rule, pattern in self._rule_regexes
            if pattern.search(cell.name)
        ]
        if len(matches) > 1:
            raise DoeParseError(
                f"Multiple device rules match cell '{cell.name}': "
                f"{', '.join(rule.cell_pattern for rule in matches)}"
            )
        return matches[0] if matches else None
