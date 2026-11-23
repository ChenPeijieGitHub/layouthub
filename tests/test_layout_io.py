import tempfile
import unittest
from pathlib import Path

import gdstk

from parser.gds_parser import LayoutIo


class RemoveDummyCellsTests(unittest.TestCase):
    def _make_layout(self, path: Path) -> None:
        library = gdstk.Library()
        top = gdstk.Cell("Top")
        child_01 = gdstk.Cell("child_001")
        child_02 = gdstk.Cell("child_002")
        child_03 = gdstk.Cell("child_003")

        sub_cell_001 = gdstk.Cell("sub_cell_001")
        dummy_cell = gdstk.Cell("BEOL_Top")
        sub_dummy_cell = gdstk.Cell("BEOL_001")
        dummy_cell.add(gdstk.Reference(sub_dummy_cell))

        child_01.add(gdstk.Reference(dummy_cell))
        child_01.add(gdstk.Reference(sub_cell_001))
        
        top.add(gdstk.Reference(child_01))
        top.add(gdstk.Reference(child_02))
        top.add(gdstk.Reference(child_03))

        library.add(top, child_01, child_02, child_03, dummy_cell, sub_dummy_cell)
        library.write_gds(str(path))

    def test_remove_dummy_cells(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "layout.gds"
            self._make_layout(path)

            with LayoutIo(path) as layout:
                layout.parse()
                layout.remove_dummy_cells()
                layout.save()

            with LayoutIo(path) as layout:
                layout.parse()
                cells = {cell.name: cell for cell in layout.iterate_all_cells()}

            self.assertEqual(
                set(cells),
                {"Top", "child_001", "child_002", "child_003"},
            )
            self.assertEqual([cell.cell_name for cell in cells["Top"].references], ["child_001", "child_002", "child_003"])
            self.assertEqual([cell.cell_name for cell in cells["child_001"].references], ["sub_cell_001"])


if __name__ == "__main__":
    unittest.main()
