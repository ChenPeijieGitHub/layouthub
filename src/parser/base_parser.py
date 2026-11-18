from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Union


class BaseParser(ABC):
    """
    所有文件解析器的抽象基类
    支持 with 上下文管理；统一接口：parse / close
    子类：GdsParser、OasParser、CdlParser、SpiceParser 等
    """

    def __init__(self, file_path: Union[str, Path]):
        self.file_path = Path(file_path)

    @abstractmethod
    def parse(self) -> Any:
        """
        主解析入口
        返回解析后的对象（由子类自己定义返回类型）
        """
        ...

    @abstractmethod
    def close(self) -> None:
        """释放底层资源、清空句柄"""
        ...

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()