from pathlib import Path
import re
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple, Union

import gdstk


class NetlistCell:
    """用于生成 netlist 的 cell 接口信息"""

    def __init__(self, name: str, ports: List[str]):
        self._name = name
        self._ports = ports
        self._instances: List[str] = []

    @property
    def name(self) -> str:
        return self._name

    @property
    def ports(self) -> List[str]:
        return self._ports

    @property
    def instances(self) -> List[str]:
        return self._instances

    def update_ports(self, new_ports: List[str]) -> None:
        self._ports = new_ports

    def add_instance(self, instance_name: str) -> None:
        self._instances.append(instance_name)


class DeviceInstance:
    """Holds data parsed from one instance line inside a subckt."""

    def __init__(self, name: str) -> None:
        self._name: str = name
        self.connections: List[str] = []
        self.device_name: Optional[str] = None
        self.parameters: Dict[str, str] = {}

    @property
    def code(self) -> str:
        return self._name[0].lower()

    def __str__(self) -> str:
        return self._name


class NetlistLibrary:
    def __init__(self):
        self.cells: Dict[str, NetlistCell] = {}
        self.includes: Set[str] = set()
        self.top_cell: Optional[NetlistCell] = None

    @property
    def top_cell_name(self) -> Optional[str]:
        return self.top_cell.name if self.top_cell else None

    def add_cell(self, cell: NetlistCell) -> None:
        self.cells[cell.name] = cell

    def delete_cell(self, cell_name: str) -> None:
        if cell_name in self.cells:
            del self.cells[cell_name]
            if self.top_cell and self.top_cell.name == cell_name:
                self.top_cell = None

    def get_cell(self, name: str) -> Optional[NetlistCell]:
        return self.cells.get(name)

    def set_top_cell(self, cell_name: str) -> None:
        cell = self.get_cell(cell_name)
        if cell:
            self.top_cell = cell

    def add_include(self, include_path: str) -> None:
        self.includes.add(include_path)

    def delete_include(self, include_path: str) -> None:
        self.includes.discard(include_path)

    def export_cdl(self, out_file: str) -> None:
        """Export the netlist library to a CDL file."""
        if not self.top_cell:
            raise ValueError("Top cell is not set. Cannot export CDL.")

        cdl_lines = []
        for include in sorted(self.includes):
            cdl_lines.append(f".INCLUDE {include}")

        for cell in self.cells.values():
            cdl_lines.append(f".SUBCKT {cell.name} {' '.join(cell.ports)}")
            for instance_name in cell.instances:
                connections = " ".join(cell.ports)  # Placeholder for actual connections
                parameters = " ".join(f"{k}={v}" for k, v in cell.parameters.items())
                cdl_lines.append(f"{instance_name} {connections} {cell.name} {parameters}")
            cdl_lines.append(".ENDS")

        # Write to a CDL file (this is just a placeholder, actual file writing code would go here)
        with open(out_file, "w") as f:
            f.write("\n".join(cdl_lines))
    