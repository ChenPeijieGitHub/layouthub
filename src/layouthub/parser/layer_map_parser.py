from pathlib import Path
from typing import Union

from .base_parser import BaseParser
from layouthub.common import Layer, get_logger


logger = get_logger(__name__)

class LayerMapParser(BaseParser):
    def __init__(self, file_path: Union[str, Path]):
        super().__init__(file_path)
        self.layer_map: dict = self.parse()
        
    def parse(self) -> dict:
        """
        解析层映射文件，返回一个字典，键为层名，值为对应的层号
        """
        layer_map = {}
        with open(self.file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                parts = line.split()
                name, purpose, layer_number, data_type = parts[0], parts[1], parts[2], parts[3]
                if len(parts) == 4:
                    layer_map[(layer_number, data_type)] = layer_map[(name, purpose)] = Layer(
                        layer_number=int(layer_number),
                        data_type=int(data_type),
                        name=name,
                        purpose=purpose
                    )
                elif len(parts) == 6 and parts[4].lower().find('mask') != -1:
                    mask = parts[4]
                    layer_map[(layer_number, data_type)] = layer_map[(name, purpose, mask)] = Layer(
                        layer_number=int(layer_number),
                        data_type=int(data_type),
                        name=name,
                        purpose=purpose,
                        mask=mask
                    )
                else:
                    logger.warning(f"Invalid line in layer map file: {line}")
        return layer_map

    def close(self) -> None:
        """释放资源"""
        pass