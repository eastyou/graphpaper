"""把纸张规格渲染成可打印的 A4 HTML。"""

from __future__ import annotations

import html
from typing import List

from .paper import (
    LABEL_STEP_MM,
    PAGE_HEIGHT_MM,
    PAGE_WIDTH_MM,
    PaperError,
    PaperSpec,
    calc_axes,
    calc_geometry,
    horizontal_lines,
    vertical_lines,
)


def _num(value: float) -> str:
    """去掉多余的小数零，减小 HTML 体积。"""
    text = "%.3f" % value
    return text.rstrip("0").rstrip(".") if "." in text else text


def _grid_lines(spec: PaperSpec) -> List[str]:
    geometry = calc_geometry(spec)
    parts: List[str] = []

    major = LABEL_STEP_MM
    for index, x in enumerate(vertical_lines(geometry)):
        is_major = (index * geometry.spacing) % major == 0
        color = "#c3cedd" if is_major else "#e1e8f1"
        width = "0.24" if is_major else "0.14"
        parts.append(
            '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="%s"/>'
            % (
                _num(x),
                _num(geometry.y0),
                _num(x),
                _num(geometry.y1),
                color,
                width,
            )
        )
    for index, y in enumerate(horizontal_lines(geometry)):
        is_major = (index * geometry.spacing) % major == 0
        color = "#c3cedd" if is_major else "#e1e8f1"
        width = "0.24" if is_major else "0.14"
        parts.append(
            '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="%s"/>'
            % (
                _num(geometry.x0),
                _num(y),
                _num(geometry.x1),
                _num(y),
                color,
                width,
            )
        )
    return parts


def _dot_grid(spec: PaperSpec) -> List[str]:
    geometry = calc_geometry(spec)
    parts: List[str] = []
    for y in horizontal_lines(geometry):
        for x in vertical_lines(geometry):
            parts.append(
                '<circle cx="%s" cy="%s" r="0.3" fill="#7c8798"/>'
                % (_num(x), _num(y))
            )
    return parts


def _coordinate_layers(spec: PaperSpec) -> List[str]:
    geometry = calc_geometry(spec)
    axes = calc_axes(geometry)
    parts: List[str] = []

    # 每秒一格的浅网格，整厘米略深。
    for index, x in enumerate(vertical_lines(geometry)):
        is_major = (index * geometry.spacing) % LABEL_STEP_MM == 0
        parts.append(
            '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="%s"/>'
            % (
                _num(x),
                _num(geometry.y0),
                _num(x),
                _num(geometry.y1),
                "#c3cedd" if is_major else "#e6ecf4",
                "0.2" if is_major else "0.12",
            )
        )
    for index, y in enumerate(horizontal_lines(geometry)):
        is_major = (index * geometry.spacing) % LABEL_STEP_MM == 0
        parts.append(
            '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="%s"/>'
            % (
                _num(geometry.x0),
                _num(y),
                _num(geometry.x1),
                _num(y),
                "#c3cedd" if is_major else "#e6ecf4",
                "0.2" if is_major else "0.12",
            )
        )

    # 两条坐标轴。
    parts.append(
        '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="#0f172a" stroke-width="0.4"/>'
        % (
            _num(geometry.x0),
            _num(axes.y),
            _num(geometry.x1),
            _num(axes.y),
        )
    )
    parts.append(
        '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="#0f172a" stroke-width="0.4"/>'
        % (
            _num(axes.x),
            _num(geometry.y0),
            _num(axes.x),
            _num(geometry.y1),
        )
    )

    # 轴末端的箭头。
    parts.append(
        '<polygon points="%s,%s %s,%s %s,%s" fill="#0f172a"/>'
        % (
            _num(geometry.x1 - 2.4),
            _num(axes.y - 1.1),
            _num(geometry.x1),
            _num(axes.y),
            _num(geometry.x1 - 2.4),
            _num(axes.y + 1.1),
        )
    )
    parts.append(
        '<polygon points="%s,%s %s,%s %s,%s" fill="#0f172a"/>'
        % (
            _num(axes.x - 1.1),
            _num(geometry.y0 + 2.4),
            _num(axes.x),
            _num(geometry.y0),
            _num(axes.x + 1.1),
            _num(geometry.y0 + 2.4),
        )
    )

    # 每格一个短刻度。
    for index in range(geometry.columns + 1):
        x = geometry.x0 + index * geometry.spacing
        parts.append(
            '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="#0f172a" stroke-width="0.18"/>'
            % (_num(x), _num(axes.y - 0.8), _num(x), _num(axes.y + 0.8))
        )
    for index in range(geometry.rows + 1):
        y = geometry.y0 + index * geometry.spacing
        parts.append(
            '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="#0f172a" stroke-width="0.18"/>'
            % (_num(axes.x - 0.8), _num(y), _num(axes.x + 0.8), _num(y))
        )

    # 整厘米标签，单位为 cm。
    for x, text in axes.x_labels:
        parts.append(
            '<text x="%s" y="%s" font-size="2.9" text-anchor="middle" fill="#334155">%s</text>'
            % (_num(x), _num(axes.y + 4.3), html.escape(text))
        )
    for y, text in axes.y_labels:
        parts.append(
            '<text x="%s" y="%s" font-size="2.9" text-anchor="end" fill="#334155">%s</text>'
            % (_num(axes.x - 2.3), _num(y + 1), html.escape(text))
        )
    parts.append(
        '<text x="%s" y="%s" font-size="3.2" text-anchor="end" fill="#0f172a">O</text>'
        % (_num(axes.x - 2.3), _num(axes.y + 4.3))
    )
    parts.append(
        '<text x="%s" y="%s" font-size="3.4" font-style="italic" fill="#0f172a">x</text>'
        % (_num(geometry.x1 - 1.2), _num(axes.y - 2.6))
    )
    parts.append(
        '<text x="%s" y="%s" font-size="3.4" font-style="italic" fill="#0f172a">y</text>'
        % (_num(axes.x + 2.2), _num(geometry.y0 + 3.4))
    )
    return parts


def render_svg(spec: PaperSpec, index: int = 0) -> str:
    """生成一页 SVG；``index`` 从 0 开始。"""
    if isinstance(index, bool) or not isinstance(index, int):
        raise PaperError("页码必须是整数")
    if not 0 <= index < spec.pages:
        raise PaperError("页码超出范围：%d（共 %d 页）" % (index + 1, spec.pages))

    if spec.kind == "dot":
        content = _dot_grid(spec)
    elif spec.kind == "coordinate":
        content = _coordinate_layers(spec)
    else:
        content = _grid_lines(spec)

    geometry = calc_geometry(spec)
    parts: List[str] = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="%smm" height="%smm" '
        'viewBox="0 0 %s %s">'
        % (
            _num(PAGE_WIDTH_MM),
            _num(PAGE_HEIGHT_MM),
            _num(PAGE_WIDTH_MM),
            _num(PAGE_HEIGHT_MM),
        ),
        '<rect width="%s" height="%s" fill="#ffffff"/>'
        % (_num(PAGE_WIDTH_MM), _num(PAGE_HEIGHT_MM)),
        '<text x="%s" y="7.6" font-size="5.2" font-weight="600" '
        'text-anchor="middle" fill="#0f172a">%s</text>'
        % (_num(PAGE_WIDTH_MM / 2), html.escape(str(spec.title))),
    ]
    parts.extend(content)

    detail = "%s · %d mm 间距 · %d×%d 格" % (
        spec.display_name,
        spec.spacing_mm,
        geometry.columns,
        geometry.rows,
    )
    parts.append(
        '<text x="%s" y="292.6" font-size="2.7" fill="#94a3b8">%s</text>'
        % (_num(12), html.escape("graphpaper · " + detail))
    )
    parts.append(
        '<text x="%s" y="292.6" font-size="2.7" text-anchor="end" fill="#94a3b8">'
        "第 %d / %d 页</text>" % (_num(198), index + 1, spec.pages)
    )
    parts.append("</svg>")
    return "\n".join(parts)


STYLE = """
  :root { color-scheme: light; }
  * { box-sizing: border-box; }
  body {
    margin: 0;
    padding: 8mm 0;
    background: #e2e8f0;
    font-family: "PingFang SC", "Microsoft YaHei", "Noto Sans CJK SC", sans-serif;
  }
  .sheet {
    width: 210mm;
    height: 297mm;
    margin: 0 auto 8mm;
    background: #fff;
    box-shadow: 0 6px 22px rgba(15, 23, 42, 0.14);
    overflow: hidden;
    page-break-after: always;
    break-after: page;
  }
  .sheet:last-child { page-break-after: auto; break-after: auto; }
  .sheet svg { display: block; }
  @page { size: A4 portrait; margin: 0; }
  @media print {
    body { background: #fff; padding: 0; }
    .sheet { margin: 0; box-shadow: none; }
    * { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  }
"""


def render_html(spec: PaperSpec) -> str:
    """生成完整 HTML，每页一个 A4 区块。"""
    sheets = "\n".join(
        '<section class="sheet">%s</section>' % render_svg(spec, index)
        for index in range(spec.pages)
    )
    return (
        "<!doctype html>\n"
        '<html lang="zh-CN">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        "<title>%s</title>\n<style>%s</style>\n</head>\n<body>\n%s\n</body>\n</html>\n"
        % (html.escape(str(spec.title)), STYLE, sheets)
    )
