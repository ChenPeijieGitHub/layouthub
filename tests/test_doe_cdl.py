import csv
import json
import tempfile
import unittest
from pathlib import Path

import gdstk

from generator.cdl_generator import CdlGenerator
from parser.doe_parser import DoeParseError, LayoutDoeFlow, register_parameter_extractor
from parser.doe_parser.config import DeviceRule, DoeCdlConfig
from parser.doe_parser.parser import DoeParser


class DoeCdlFlowTests(unittest.TestCase):
    def _make_layout(self, path: Path) -> None:
        library = gdstk.Library()
        dut = gdstk.Cell("DUT_2_0.07_20_0.04")
        dut.add(gdstk.rectangle((0, 0), (0.07, 20), layer=1, datatype=0))
        dut.add(gdstk.Label("MINUS", (0.07, 20), layer=10, texttype=0))
        dut.add(gdstk.Label("PLUS", (0, 0), layer=10, texttype=0))
        dut.add(gdstk.Label("not_a_pin", (0, 0), layer=5, texttype=0))

        testkey = gdstk.Cell("TL_mismatch_001")
        testkey.add(gdstk.Reference(dut))
        testkey.add(gdstk.Reference(dut, origin=(1, 0)))
        testkey.add(gdstk.Label("IN", (0, 0), layer=10, texttype=0))

        no_pins = gdstk.Cell("NO_PIN_CELL")
        testkey.add(gdstk.Reference(no_pins, origin=(2, 0)))
        library.add(dut, testkey, no_pins)
        library.write_gds(str(path))

    def _write_config(self, path: Path) -> None:
        path.write_text(
            json.dumps(
                {
                    "testkey_pattern": "^TL_",
                    "coordinate_unit": "um",
                    "pin_layers": [{"layer": 10, "texttype": 0}],
                    "pin_order_rules": [
                        {"cell_pattern": "^DUT_", "pins": ["PLUS", "MINUS"]}
                    ],
                    "device_rules": [
                        {
                            "cell_pattern": "^DUT_",
                            "device_type": "mos",
                            "extractor": "bbox",
                            "options": {"layer": 1, "datatype": 0},
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )

    def test_flow_writes_geometry_doe_and_only_pin_label_interfaces(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            gds_path = root / "layout.gds"
            config_path = root / "config.json"
            self._make_layout(gds_path)
            self._write_config(config_path)

            doe_path, cdl_path = LayoutDoeFlow(gds_path, config_path).run(root / "out")

            with doe_path.open(encoding="utf-8-sig", newline="") as doe_file:
                rows = list(csv.DictReader(doe_file))
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["testkey"], "TL_mismatch_001")
            self.assertEqual(rows[0]["dut_cell"], "DUT_2_0.07_20_0.04")
            self.assertEqual(rows[0]["width"], "0.07")
            self.assertEqual(rows[0]["height"], "20.0")
            self.assertEqual(rows[0]["coordinate_unit"], "um")

            cdl = cdl_path.read_text(encoding="utf-8")
            self.assertIn(".SUBCKT DUT_2_0.07_20_0.04 PLUS MINUS", cdl)
            self.assertIn(".SUBCKT TL_mismatch_001", cdl)
            self.assertNotIn(".SUBCKT NO_PIN_CELL", cdl)
            self.assertNotIn("not_a_pin", cdl)

    def test_unknown_extractor_fails_instead_of_emitting_incomplete_doe(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            gds_path = root / "layout.gds"
            config_path = root / "config.json"
            self._make_layout(gds_path)
            self._write_config(config_path)
            config_data = json.loads(config_path.read_text(encoding="utf-8"))
            config_data["device_rules"][0]["extractor"] = "missing"
            config_path.write_text(json.dumps(config_data), encoding="utf-8")

            with self.assertRaisesRegex(DoeParseError, "Unknown parameter extractor"):
                LayoutDoeFlow(gds_path, config_path).run(root / "out")

    def test_cdl_generator_emits_no_subcircuit_without_pin_labels(self) -> None:
        cell = gdstk.Cell("unlabeled")
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = CdlGenerator(
                [(10, 0)],
                [("^unlabeled$", ["PIN"])],
            ).write(
                [cell], Path(temp_dir) / "empty.cdl"
            )
            self.assertNotIn(".SUBCKT", output_path.read_text(encoding="utf-8"))

    def test_overlapping_device_rules_are_rejected(self) -> None:
        config = DoeCdlConfig(
            testkey_pattern="^TL_",
            coordinate_unit="um",
            pin_layers=(),
            pin_order_rules=(),
            device_rules=(
                DeviceRule("^DUT_", "mos", "bbox", {"layer": 1}),
                DeviceRule("DUT_", "other", "bbox", {"layer": 1}),
            ),
        )
        parser = DoeParser(config)
        with self.assertRaisesRegex(DoeParseError, "Multiple device rules"):
            parser.parse([gdstk.Cell("DUT_1")])

    def test_device_specific_extractor_can_be_registered(self) -> None:
        extractor_name = "test_device_specific"
        register_parameter_extractor(
            extractor_name,
            lambda cell, options: {"finger_count": options["finger_count"]},
        )
        dut = gdstk.Cell("CUSTOM_DEVICE")
        testkey = gdstk.Cell("TL_custom")
        testkey.add(gdstk.Reference(dut))
        config = DoeCdlConfig(
            testkey_pattern="^TL_",
            coordinate_unit="um",
            pin_layers=(),
            pin_order_rules=(),
            device_rules=(
                DeviceRule(
                    "^CUSTOM_",
                    "custom",
                    extractor_name,
                    {"finger_count": 4},
                ),
            ),
        )

        rows = DoeParser(config).parse([testkey])

        self.assertEqual(rows[0]["finger_count"], 4)


if __name__ == "__main__":
    unittest.main()
