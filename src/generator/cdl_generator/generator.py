from pathlib import Path
import re
from typing import Iterable, List, Sequence, Set, Tuple

import gdstk


class CdlGenerationError(Exception):
    """生成 CDL 接口时遇到无效 pin label。"""


class CdlGenerator:
    """仅为含有配置 pin label 的 cell 生成 CDL 子电路接口骨架。"""

    def __init__(
        self,
        pin_layers: Sequence[Tuple[int, int]],
        pin_order_rules: Sequence[Tuple[str, Sequence[str]]] = (),
    ):
        self.pin_layers = set(pin_layers)
        self.pin_order_rules = [
            (
                re.compile(pattern),
                tuple(pins),
            )
            for pattern, pins in pin_order_rules
        ]

    def write(self, roots: Iterable[gdstk.Cell], output_path: str | Path) -> Path:
        output_path = Path(output_path)
        cells = self._hierarchy_cells(roots)
        interfaces = [
            (cell.name, self._pins(cell))
            for cell in cells
        ]
        interfaces = [(name, pins) for name, pins in interfaces if pins]
        for cell_name, _ in interfaces:
            if any(character.isspace() for character in cell_name):
                raise CdlGenerationError(
                    f"Cell name '{cell_name}' contains whitespace and cannot be emitted as CDL"
                )
        lines = [
            "* 仅生成 CDL 接口骨架；未提取内部连接关系。"
        ]
        for cell_name, pins in sorted(interfaces, key=lambda item: item[0]):
            lines.extend(
                [
                    f".SUBCKT {cell_name} {' '.join(pins)}",
                    f".ENDS {cell_name}",
                    "",
                ]
            )

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text("\n".join(lines), encoding="utf-8")
        return output_path

    def _pins(self, cell: gdstk.Cell) -> List[str]:
        pins: List[str] = []
        seen: Set[str] = set()
        for label in cell.labels:
            if (label.layer, label.texttype) not in self.pin_layers:
                continue
            pin = label.text.strip()
            if not pin:
                raise CdlGenerationError(f"Empty pin label on cell '{cell.name}'")
            if any(character.isspace() for character in pin):
                raise CdlGenerationError(
                    f"Pin label '{label.text}' in cell '{cell.name}' contains whitespace"
                )
            if pin not in seen:
                pins.append(pin)
                seen.add(pin)
        if not pins:
            return pins
        matching_orders = [
            order
            for pattern, order in self.pin_order_rules
            if pattern.search(cell.name)
        ]
        if len(matching_orders) > 1:
            raise CdlGenerationError(
                f"Multiple pin order rules match cell '{cell.name}'"
            )
        if matching_orders:
            configured_order = matching_orders[0]
            if set(configured_order) != seen:
                raise CdlGenerationError(
                    f"Configured pin order for cell '{cell.name}' does not match "
                    "the pin labels on configured layers"
                )
            pins = list(configured_order)
        # GDS 未定义 CDL 端口顺序，因此未配置顺序时沿用 label 顺序。
        return pins

    @staticmethod
    def _hierarchy_cells(roots: Iterable[gdstk.Cell]) -> List[gdstk.Cell]:
        cells: List[gdstk.Cell] = []
        seen: Set[gdstk.Cell] = set()
        stack = list(roots)
        while stack:
            cell = stack.pop()
            if cell in seen:
                continue
            seen.add(cell)
            cells.append(cell)
            stack.extend(reference.cell for reference in reversed(cell.references))
        return cells
