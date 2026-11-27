from pathlib import Path
import re
from typing import Iterable, List, Sequence, Set, Tuple, Union

import gdstk


class NetlistCell:
    """用于生成 netlist 的 cell 接口信息"""

    def __init__(self, name: str, ports: List[str]):
        self._name = name
        self._ports = ports

    @property
    def name(self) -> str:
        return self._name

    @property
    def pins(self) -> List[str]:
        return self._ports


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

