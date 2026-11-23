from typing import Any, Callable, Dict, Mapping

import gdstk

from .exceptions import DoeParseError

ParameterExtractor = Callable[[gdstk.Cell, Mapping[str, Any]], Mapping[str, Any]]
_EXTRACTORS: Dict[str, ParameterExtractor] = {}


def register_parameter_extractor(name: str, extractor: ParameterExtractor) -> None:
    """注册器件专用的 GDS 参数提取策略。"""
    if not name or not callable(extractor):
        raise ValueError("An extractor name and callable are required")
    if name in _EXTRACTORS:
        raise ValueError(f"Parameter extractor '{name}' is already registered")
    _EXTRACTORS[name] = extractor


def extract_parameters(
    extractor_name: str,
    cell: gdstk.Cell,
    options: Mapping[str, Any],
) -> Mapping[str, Any]:
    try:
        extractor = _EXTRACTORS[extractor_name]
    except KeyError as exc:
        raise DoeParseError(
            f"Unknown parameter extractor '{extractor_name}' for cell '{cell.name}'"
        ) from exc
    parameters = extractor(cell, options)
    if not isinstance(parameters, Mapping):
        raise DoeParseError(
            f"Extractor '{extractor_name}' returned invalid parameters for cell '{cell.name}'"
        )
    return parameters


def _bounding_box(cell: gdstk.Cell, options: Mapping[str, Any]) -> Mapping[str, Any]:
    layer = options.get("layer")
    datatype = options.get("datatype", 0)
    if not isinstance(layer, int) or isinstance(layer, bool):
        raise DoeParseError(f"bbox extractor for '{cell.name}' requires integer option 'layer'")
    if not isinstance(datatype, int) or isinstance(datatype, bool):
        raise DoeParseError(f"bbox extractor for '{cell.name}' requires integer option 'datatype'")

    # 仅测量当前 cell 自身的几何；依赖层级的参数应使用自定义提取器。
    polygons = cell.get_polygons(layer=layer, datatype=datatype, depth=0)
    if not polygons:
        raise DoeParseError(
            f"No polygon or path on layer {layer}/{datatype} in cell '{cell.name}'"
        )

    points = [point for polygon in polygons for point in polygon.points]
    x_values = [point[0] for point in points]
    y_values = [point[1] for point in points]
    # GDS 坐标保持用户单位；DOE 行会记录配置中的单位标记。
    return {
        "width": max(x_values) - min(x_values),
        "height": max(y_values) - min(y_values),
    }


register_parameter_extractor("bbox", _bounding_box)
