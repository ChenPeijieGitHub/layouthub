from typing import Optional


class Layer:
     """Layer类用于表示一个图层，包含层号、数据类型和名称等属性。"""

     def __init__(self, layer_number: int, data_type: int, name: Optional[str] = None, 
                  purpose: Optional[str] = None, mask: Optional[str] = None):
         self.layer_number = layer_number
         self.data_type = data_type
         self.name = name
         self.purpose = purpose
         self.mask = mask

     def __repr__(self) -> str:
         return f"Layer(layer_number={self.layer_number}, data_type={self.data_type}, name={self.name}, \
            purpose={self.purpose}, mask={self.mask})"