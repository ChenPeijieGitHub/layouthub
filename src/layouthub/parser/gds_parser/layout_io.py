# lib/parser/gds_parser/layout_io.py
from pathlib import Path
import re
from typing import List, Optional, Generator, Literal, Set, Tuple, Union
import gdstk

from layouthub.parser.base_parser import BaseParser
from .exceptions import LayoutIoError
from layouthub.common.logger import get_logger

logger = get_logger(__name__)
DMY_MATCH_LIST = ["FDY_", "BDY_", "FEOL_", "BEOL_"]


class LayoutIo(BaseParser):
    """
    版图文件读写一体化封装,基于gdstk
    支持:GDSII(.gds) / OASIS(.oas)
    能力:读取、查找cell、遍历、修改图形、新增cell、写出gds/oas
    上层拿到的cell对象统一
    """
    def __init__(self, file_path: Union[str, Path]):
        super().__init__(file_path)
        self.lib: Optional[gdstk.Library] = None
        self._format: Optional[Literal["gds", "oas"]] = None

    @property
    def format(self) -> Optional[Literal["gds", "oas"]]:
        """获取输入文件格式：'gds' / 'oas',不支持则返回None"""
        if self._format is None:
            suffix = self.file_path.suffix.lower()
            if suffix in (".gds", ".gdsii"):
                self._format = "gds"
            elif suffix in (".oas", ".oasis"):
                self._format = "oas"
        return self._format

    def parse(self) -> "LayoutIo":
        if self.lib is not None:
            logger.warning("Library already loaded, skip re-read")
            return self

        try:
            logger.info(f"Start reading layout file: {self.file_path}")
            if self.format == "gds":
                self.lib = gdstk.read_gds(str(self.file_path))
            elif self.format == "oas":
                self.lib = gdstk.read_oas(str(self.file_path))
            else:
                raise LayoutIoError(f"Unsupported file format: {self.format}, only .gds/.oas")

            top_cells = self.lib.top_level()
            logger.info(f"Loaded success. Top cells: [{', '.join(c.name for c in top_cells)}]")
            return self
        except Exception as e:
            raise LayoutIoError(f"Failed to read {self.file_path}: {str(e)}") from e

    def get_top_cells(self) -> List[gdstk.Cell]:
        if self.lib is None:
            raise LayoutIoError("Library not parsed, call parse() first")
        return self.lib.top_level()

    def get_cell_by_name(self, cell_name: str) -> gdstk.Cell:
        if self.lib is None:
            raise LayoutIoError("Library not parsed, call parse() first")
        for cell in self.lib.cells:
            if cell.name == cell_name:
                return cell
        raise LayoutIoError(f"Cell '{cell_name}' not found")

    def find_cells_by_pattern(self, pattern: str) -> List[gdstk.Cell]:
        import re
        pat = re.compile(pattern)
        return [cell for cell in self.lib.cells if pat.search(cell.name)]

    def iterate_all_cells(self) -> Generator[gdstk.Cell, None, None]:
        if self.lib is None:
            raise LayoutIoError("Library not parsed, call parse() first")
        for cell in self.lib.cells:
            yield cell

    def add_cell(self, cell: gdstk.Cell):
        if self.lib is None:
            raise LayoutIoError("Library not parsed")
        self.lib.add(cell)
        logger.debug(f"Add cell: {cell.name}")

    def remove_dummy_cells(
        self,
        match_list: Optional[List[str]] = None,
        dry_run: bool = False,
    ) -> None:
        """
        根据 cell 名称子串删除匹配的 cell、其所有子 cell 及指向它们的引用。
        :param match_list: cell 名称匹配子串列表，默认使用 DMY_MATCH_LIST
        :param dry_run: 是否仅统计、不执行删除
        """
        if self.lib is None:
            raise LayoutIoError("Call parse() first")
        if match_list is None:
            match_list = DMY_MATCH_LIST
        if not match_list:
            logger.info("Empty cell match list, skip delete")
            return
        if any(not isinstance(item, str) or not item for item in match_list):
            raise LayoutIoError("Cell match patterns must be non-empty strings")

        # 将子串转义后合并成正则，按字面内容匹配 cell 名称。
        pattern = "|".join(re.escape(item) for item in match_list)
        targets = {cell for cell in self.lib.cells if re.search(pattern, cell.name)}
        if not targets:
            logger.info(f"No cell matched by {match_list}")
            return
        logger.info(f"Matched {len(targets)} target cells")

        # 沿 cell 引用遍历所有后代；集合可避免重复访问和循环引用。
        delete_cells = set()
        stack = list(targets)
        while stack:
            cell = stack.pop()
            if cell in delete_cells:
                continue
            delete_cells.add(cell)
            delete_cells.update(cell.dependencies(True))
        logger.info(f"Subtree total {len(delete_cells)} cells")

        if dry_run:
            logger.info("Dry run, skip delete")
            return

        # 清理引用
        left_cells = set(self.lib.cells) - delete_cells
        for cell in left_cells:
            refs_to_remove = [ref for ref in cell.references if ref.cell in delete_cells]
            cell.remove(*refs_to_remove)
        # 引用清理后，再从 library 中移除匹配 cell 及其所有子 cell
        self.lib.remove(*delete_cells)
        logger.info(f"Removed {len(delete_cells)} cells")

    def get_cell_pins(self, cell: gdstk.Cell, pin_layers: Set[Tuple[int, int]]) -> List[str]:
        return [label.text for label in cell.labels if (label.layer, label.texttype) in pin_layers]

    def save(self) -> None:
        """原地保存,按原文件后缀自动选择gds/oas格式"""
        if self.lib is None:
            raise LayoutIoError("Library not parsed")
        logger.info(f"Overwrite save to {self.file_path}")
        if self.format == "gds":
            self.lib.write_gds(str(self.file_path))
        elif self.format == "oas":
            self.lib.write_oas(str(self.file_path))

    def save_as(self, out_path: Union[str, Path]) -> None:
        """另存为,自动根据输出文件名后缀选格式"""
        out_path = Path(out_path)
        if self.lib is None:
            raise LayoutIoError("Library not parsed")
        out_suffix = out_path.suffix.lower()
        logger.info(f"Save layout to {out_path}")
        if out_suffix == ".gds":
            self.lib.write_gds(str(out_path))
        elif out_suffix == ".oas":
            self.lib.write_oas(str(out_path))
        else:
            raise LayoutIoError(f"Unsupported output suffix {out_suffix}")

    def close(self):
        if self.lib is not None:
            logger.debug("Release layout library resource")
            self.lib = None

    def __repr__(self):
        return f"<LayoutIo file={self.file_path} format={self.format} loaded={self.lib is not None}>"