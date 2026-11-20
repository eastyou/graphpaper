"""graphpaper：方格纸、点阵纸与坐标纸生成器。"""

from __future__ import annotations

from .paper import (
    PAPER_TYPES,
    Axes,
    Geometry,
    PaperError,
    PaperSpec,
    calc_axes,
    calc_geometry,
    horizontal_lines,
    vertical_lines,
)
from .render import render_html, render_svg

__version__ = "0.1.0"

__all__ = [
    "PAPER_TYPES",
    "Axes",
    "Geometry",
    "PaperError",
    "PaperSpec",
    "calc_axes",
    "calc_geometry",
    "horizontal_lines",
    "render_html",
    "render_svg",
    "vertical_lines",
    "__version__",
]
