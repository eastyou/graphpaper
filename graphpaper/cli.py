"""命令行入口：生成可打印的方格纸、点阵纸或坐标纸。"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional, Sequence

import argparse

from .paper import PaperError, PaperSpec, calc_geometry
from .render import render_html


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="graphpaper",
        description="方格纸 / 点阵纸 / 坐标纸生成器：输出可直接打印的 A4 页面",
    )
    parser.add_argument("--version", action="version", version="graphpaper 0.1.0")
    parser.add_argument(
        "--type",
        dest="kind",
        default="grid",
        help="纸张类型：grid 方格纸（默认）、dot 点阵纸、coordinate 坐标纸",
    )
    parser.add_argument(
        "--spacing", type=int, default=5, help="网格间距，单位毫米，2~20，默认 5"
    )
    parser.add_argument("--pages", type=int, default=1, help="页数，1~50，默认 1")
    parser.add_argument("--title", default=None, help="页眉标题，默认使用纸张类型名")
    parser.add_argument(
        "-o", "--output", default=None, help="输出 HTML 路径，默认使用纸张类型名"
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        spec = PaperSpec(
            kind=args.kind,
            spacing_mm=args.spacing,
            pages=args.pages,
            title=args.title,
        )
    except PaperError as exc:
        print("错误: %s" % exc, file=sys.stderr)
        return 2

    output = args.output or "%s.html" % spec.display_name
    try:
        page = render_html(spec)
    except PaperError as exc:
        print("错误: %s" % exc, file=sys.stderr)
        return 2

    try:
        Path(output).write_text(page, encoding="utf-8")
    except OSError as exc:
        print("错误: 写入文件失败: %s" % exc, file=sys.stderr)
        return 1

    geometry = calc_geometry(spec)
    print(
        "已生成 %s：%s，%d mm 间距，%d×%d 格，共 %d 页"
        % (
            output,
            spec.display_name,
            spec.spacing_mm,
            geometry.columns,
            geometry.rows,
            spec.pages,
        )
    )
    print("用浏览器打开后按 Ctrl/Cmd + P，纸张选 A4 纵向、边距选「无」即可打印")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
