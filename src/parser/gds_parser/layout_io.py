# lib/parser/gds_parser/layout_io.py
import fnmatch
from pathlib import Path
from typing import Dict, List, Optional, Generator, Literal, Set
import gdstk

from parser.base_parser import BaseParser
from parser.gds_parser.exceptions import LayoutIoError
from common.logger import get_logger

logger = get_logger(__name__)


class LayoutIo(BaseParser):
    """
    版图文件读写一体化封装,基于gdstk
    支持:GDSII(.gds) / OASIS(.oas)
    能力:读取、查找cell、遍历、修改图形、新增cell、写出gds/oas
    上层拿到的cell对象统一
    """
    def __init__(self, file_path: str | Path):
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
        
    def _match_cells_by_wildcard(self, match_list: List[str]) -> Set[gdstk.Cell]:
        """根据通配符列表匹配cell."""
        targets = set()
        for cell in self.lib.cells:
            if any(fnmatch.fnmatch(cell.name, p) for p in match_list):
                targets.add(cell)
        return targets

    def _build_ref_graph(self) -> tuple[Dict[gdstk.Cell, List[gdstk.Cell]], Dict[gdstk.Cell, List[gdstk.Cell]]]:
        """构建正向,反向引用关系图."""
        forward = {c: [] for c in self.lib.cells}
        reverse = {c: [] for c in self.lib.cells}
        for parent in self.lib.cells:
            for ref in parent.references:
                child = ref.cell
                forward[parent].append(child)
                reverse[child].append(parent)
        return forward, reverse

    def _bfs_collect_subtree(self, roots: List[gdstk.Cell], forward: Dict[gdstk.Cell, List[gdstk.Cell]]) -> Set[gdstk.Cell]:
        """通过BFS收集根节点下整棵子树的所有cell."""
        subtree, stack = set(), list(roots)
        while stack:
            cell = stack.pop()
            if cell in subtree:
                continue
            subtree.add(cell)
            stack.extend(forward[cell])
        return subtree

    def _clean_subtree_refs(self, root: gdstk.Cell, forward: Dict[gdstk.Cell, List[gdstk.Cell]], ref_cnt: Dict[gdstk.Cell, int]):
        """后序迭代遍历,清理子树内部所有引用."""
        visited, stk = set(), [(root, False)]
        while stk:
            node, done = stk.pop()
            if done:
                for ref in list(node.references):
                    ch = ref.cell
                    node.remove(ref)
                    ref_cnt[ch] -= 1
                continue
            if node in visited:
                continue
            visited.add(node)
            stk.append((node, True))
            for ch in reversed(forward[node]):
                stk.append((ch, False))

    def remove_cells_by_match_list(self, match_list: List[str], dry_run: bool = False) -> None:
        """
        删除匹配到的cell及其子cell.
        如果子cell存在外部引用,仅删除引用关系;否则直接删除cell.
        :param match_list: 通配符pattern列表,支持*,?
        :param dry_run: 是否试运行,True时只打印日志,不修改库
        """
        if self.lib is None:
            raise LayoutIoError("Call parse() first")
        targets = self._match_cells_by_wildcard(match_list)
        if not targets:
            logger.info(f"No cell matched by {match_list}")
            return
        logger.info(f"Matched {len(targets)} target cells")

        forward, reverse = self._build_ref_graph()
        ref_cnt = {c: len(v) for c, v in reverse.items()}
        subtree = self._bfs_collect_subtree(list(targets), forward)
        logger.info(f"Subtree total {len(subtree)} cells")

        if dry_run:
            logger.info("Dry run, skip delete")
            return
        for root in targets:
            self._clean_subtree_refs(root, forward, ref_cnt)
        del_cells = [c for c in self.lib.cells if ref_cnt[c] == 0]
        for c in del_cells:
            self.lib.remove(c)
        logger.info(f"Removed {len(del_cells)} cells from library")


    def save(self) -> None:
        """原地保存,按原文件后缀自动选择gds/oas格式"""
        if self.lib is None:
            raise LayoutIoError("Library not parsed")
        logger.info(f"Overwrite save to {self.file_path}")
        if self.format == "gds":
            self.lib.write_gds(str(self.file_path))
        elif self.format == "oas":
            self.lib.write_oas(str(self.file_path))

    def save_as(self, out_path: str | Path) -> None:
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