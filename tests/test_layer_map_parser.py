import os

from layouthub.src.parser import LayerMapParser
import unittest

class TestLayerMapParser(unittest.TestCase):
    def setUp(self):
        # 创建一个临时的层映射文件
        layer_map_file = os.path.join(os.environ.get("LAYOUT_HUB_ROOT", "."), "tests", "mock_files", "tsmcN7.layermap")

    def test_parse_layer_map(self):
        parser = LayerMapParser(self.layer_map_file)
        layer_map = parser.layer_map

        # 检查解析结果是否正确
        self.assertIn(("31", "250"), layer_map)
        self.assertEqual(layer_map[("31", "250")].name, "M1")
        self.assertEqual(layer_map[("31", "250")].purpose, "drawing")
        self.assertEqual(layer_map[("31", "250")].layer_number, 31)
        self.assertEqual(layer_map[("31", "250")].data_type, 250)
