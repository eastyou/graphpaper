"""HTML / SVG 渲染的单元测试。"""

from __future__ import annotations

import unittest

from graphpaper.paper import PaperError, PaperSpec, calc_geometry
from graphpaper.render import render_html, render_svg


class GridRenderTest(unittest.TestCase):
    def test_svg_has_a4_viewbox(self) -> None:
        svg = render_svg(PaperSpec())
        self.assertIn('width="210mm"', svg)
        self.assertIn('height="297mm"', svg)
        self.assertIn('viewBox="0 0 210 297"', svg)
        self.assertTrue(svg.endswith("</svg>"))

    def test_grid_line_count(self) -> None:
        spec = PaperSpec(spacing_mm=10)
        svg = render_svg(spec)
        geometry = calc_geometry(spec)
        expected = (geometry.columns + 1) + (geometry.rows + 1)
        self.assertEqual(svg.count("<line"), expected)

    def test_html_contains_one_sheet_per_page(self) -> None:
        html = render_html(PaperSpec(pages=3))
        self.assertEqual(html.count('<section class="sheet">'), 3)
        self.assertEqual(html.count("<svg"), 3)

    def test_print_styles(self) -> None:
        html = render_html(PaperSpec())
        self.assertIn("@page { size: A4 portrait; margin: 0; }", html)
        self.assertIn("print-color-adjust", html)

    def test_no_script(self) -> None:
        html = render_html(PaperSpec())
        self.assertNotIn("<script", html)

    def test_title_is_escaped(self) -> None:
        html = render_html(PaperSpec(title="<实验>"))
        self.assertIn("&lt;实验&gt;", html)
        self.assertNotIn("<实验>", html)

    def test_footer_has_page_number(self) -> None:
        svg = render_svg(PaperSpec(pages=2), index=1)
        self.assertIn("第 2 / 2 页", svg)
        self.assertIn("graphpaper", svg)

    def test_reject_out_of_range_index(self) -> None:
        with self.assertRaises(PaperError):
            render_svg(PaperSpec(), index=1)
        with self.assertRaises(PaperError):
            render_svg(PaperSpec(), index=-1)

    def test_reject_non_integer_index(self) -> None:
        with self.assertRaises(PaperError):
            render_svg(PaperSpec(), index=0.5)  # type: ignore[arg-type]


class DotRenderTest(unittest.TestCase):
    def test_dot_count(self) -> None:
        spec = PaperSpec(kind="dot", spacing_mm=10)
        svg = render_svg(spec)
        geometry = calc_geometry(spec)
        self.assertEqual(svg.count("<circle"), geometry.points)

    def test_dot_paper_has_no_grid_lines(self) -> None:
        svg = render_svg(PaperSpec(kind="dot"))
        self.assertNotIn("<line", svg)

    def test_dots_use_uniform_radius(self) -> None:
        svg = render_svg(PaperSpec(kind="dot", spacing_mm=20))
        self.assertIn('r="0.3"', svg)


class CoordinateRenderTest(unittest.TestCase):
    def setUp(self) -> None:
        self.spec = PaperSpec(kind="coordinate", spacing_mm=10)
        self.svg = render_svg(self.spec)

    def test_axes_are_present(self) -> None:
        self.assertGreaterEqual(self.svg.count('stroke="#0f172a"'), 2)

    def test_axis_arrows(self) -> None:
        self.assertEqual(self.svg.count("<polygon"), 2)

    def test_origin_marker(self) -> None:
        self.assertIn(">O</text>", self.svg)
        self.assertIn(">x</text>", self.svg)
        self.assertIn(">y</text>", self.svg)

    def test_centimeter_labels(self) -> None:
        self.assertIn(">10</text>", self.svg)
        self.assertIn(">-10</text>", self.svg)

    def test_labels_have_no_zero(self) -> None:
        self.assertNotIn(">0</text>", self.svg)

    def test_grid_plus_axis_lines(self) -> None:
        geometry = calc_geometry(self.spec)
        grid_lines = (geometry.columns + 1) + (geometry.rows + 1)
        self.assertGreater(self.svg.count("<line"), grid_lines)

    def test_ticks_for_every_intersection(self) -> None:
        geometry = calc_geometry(self.spec)
        ticks = (geometry.columns + 1) + (geometry.rows + 1)
        self.assertGreaterEqual(self.svg.count('stroke-width="0.18"'), ticks)


if __name__ == "__main__":
    unittest.main()
