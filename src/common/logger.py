# lib/common/logger.py
import logging
import os
from pathlib import Path
from typing import Optional


def get_logger(
    name: str,
    log_dir: Optional[str | Path] = None,
    log_level: str = "INFO",
    console: bool = True,
    file: bool = True
) -> logging.Logger:
    """
    获取统一格式的logger
    :param name: logger名称
    :param log_dir: 日志存放目录，默认 ./output/logs
    :param log_level: DEBUG / INFO / WARNING / ERROR
    :param console: 是否打印到终端
    :param file: 是否输出日志文件
    :return: logger实例
    """
    logger = logging.getLogger(name)
    if logger.handlers:
        # 避免重复添加handler
        return logger

    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR
    }
    level = level_map.get(log_level.upper(), logging.INFO)
    logger.setLevel(level)
    logger.propagate = False

    # 日志格式
    fmt_str = "%(asctime)s [%(levelname)-5s] %(name)s - %(message)s"
    datefmt_str = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(fmt_str, datefmt=datefmt_str)

    if console:
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        logger.addHandler(ch)

    if file:
        if log_dir is None:
            log_dir = Path("./output/logs")
        log_dir = Path(log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / f"{name}.log"
        fh = logging.FileHandler(log_file, encoding="utf-8")
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    return logger


# 全局默认logger，方便直接导入使用
default_logger = get_logger("layout-hub")