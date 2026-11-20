"""纸张规格与网格几何计算。"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Optional, Tuple

PAGE_WIDTH_MM = 210.0
PAGE_HEIGHT_MM = 297.0
MARGIN_MM = 12.0
MIN_SPACING_MM = 2
MAX_SPACING_MM = 20
MIN_PAGES = 1
MAX_PAGES = 50
LABEL_STEP_MM = 10

PAPER_TYPES = {
    "grid": "方格纸",
    "dot": "点阵纸",
    "coordinate": "坐标纸",
}


class PaperError(ValueError):
    """纸张参数不合法。"""


@dataclass(frozen=True)
class PaperSpec:
    """一张纸的规格：类型、间距、页数与标题。"""

    kind: str = "grid"
    spacing_mm: int = 5
    pages: int = 1
    title: Optional[str] = None

    def __post_init__(self) -> None:
        if not isinstance(self.kind, str) or self.kind not in PAPER_TYPES:
            raise PaperError(
                "纸张类型必须是 %s 之一，收到 %r"
                % ("、".join(sorted(PAPER_TYPES)), self.kind)
            )
        if isinstance(self.spacing_mm, bool) or not isinstance(self.spacing_mm, int):
            raise PaperError("间距必须是整数毫米，收到 %r" % (self.spacing_mm,))
        if not MIN_SPACING_MM <= self.spacing_mm <= MAX_SPACING_MM:
            raise PaperError(
                "间距必须在 %d~%d 毫米之间，收到 %d"
                % (MIN_SPACING_MM, MAX_SPACING_MM, self.spacing_mm)
            )
        if isinstance(self.pages, bool) or not isinstance(self.pages, int):
            raise PaperError("页数必须是整数，收到 %r" % (self.pages,))
        if not MIN_PAGES <= self.pages <= MAX_PAGES:
            raise PaperError(
                "页数必须在 %d~%d 之间，收到 %d"
                % (MIN_PAGES, MAX_PAGES, self.pages)
            )

        title = self.title
        if title is None:
            title = PAPER_TYPES[self.kind]
        if not isinstance(title, str):
            raise PaperError("标题必须是文本")
        title = title.strip()
        if not title:
            raise PaperError("标题不能为空")
        object.__setattr__(self, "title", title)

    @property
    def display_name(self) -> str:
        """返回中文类型名，例如「方格纸」。"""
        return PAPER_TYPES[self.kind]


@dataclass(frozen=True)
class Geometry:
    """网格在页面上的几何信息，单位均为毫米。"""

    x0: float
    y0: float
    columns: int
    rows: int
    spacing: int

    @property
    def x1(self) -> float:
        return self.x0 + self.columns * self.spacing

    @property
    def y1(self) -> float:
        return self.y0 + self.rows * self.spacing

    @property
    def points(self) -> int:
        return (self.columns + 1) * (self.rows + 1)


@dataclass(frozen=True)
class Axes:
    """坐标纸的坐标轴位置与刻度标签。"""

    x: float
    y: float
    x_labels: Tuple[Tuple[float, str], ...]
    y_labels: Tuple[Tuple[float, str], ...]


def calc_geometry(spec: PaperSpec) -> Geometry:
    """按页面尺寸和间距算出网格行列数。"""
    usable_width = PAGE_WIDTH_MM - 2 * MARGIN_MM
    usable_height = PAGE_HEIGHT_MM - 2 * MARGIN_MM
    columns = int(math.floor(usable_width / spec.spacing_mm))
    rows = int(math.floor(usable_height / spec.spacing_mm))
    if columns < 1 or rows < 1:
        raise PaperError("当前间距过大，页面上放不下网格")
    return Geometry(MARGIN_MM, MARGIN_MM, columns, rows, spec.spacing_mm)


def vertical_lines(geometry: Geometry) -> List[float]:
    """所有竖线的 x 坐标，从左边距开始。"""
    return [
        geometry.x0 + index * geometry.spacing
        for index in range(geometry.columns + 1)
    ]


def horizontal_lines(geometry: Geometry) -> List[float]:
    """所有横线的 y 坐标，从上边距开始。"""
    return [
        geometry.y0 + index * geometry.spacing for index in range(geometry.rows + 1)
    ]


def calc_axes(geometry: Geometry) -> Axes:
    """把坐标原点放在页面中心附近，并生成整厘米的刻度标签。"""
    center_column = int(round((PAGE_WIDTH_MM / 2 - geometry.x0) / geometry.spacing))
    center_row = int(round((PAGE_HEIGHT_MM / 2 - geometry.y0) / geometry.spacing))
    origin_column = min(max(center_column, 1), geometry.columns - 1)
    origin_row = min(max(center_row, 1), geometry.rows - 1)

    origin_x = geometry.x0 + origin_column * geometry.spacing
    origin_y = geometry.y0 + origin_row * geometry.spacing

    x_labels: List[Tuple[float, str]] = []
    for column in range(geometry.columns + 1):
        offset = (column - origin_column) * geometry.spacing
        if offset == 0 or offset % LABEL_STEP_MM != 0:
            continue
        x_labels.append((geometry.x0 + column * geometry.spacing, str(offset // 10)))

    y_labels: List[Tuple[float, str]] = []
    for row in range(geometry.rows + 1):
        offset = (origin_row - row) * geometry.spacing
        if offset == 0 or offset % LABEL_STEP_MM != 0:
            continue
        y_labels.append((geometry.y0 + row * geometry.spacing, str(offset // 10)))

    return Axes(origin_x, origin_y, tuple(x_labels), tuple(y_labels))
