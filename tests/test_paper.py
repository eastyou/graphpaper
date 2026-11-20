"""纸张规格与几何计算的单元测试。"""

from __future__ import annotations

import unittest

from graphpaper.paper import (
    MARGIN_MM,
    PAGE_HEIGHT_MM,
    PAGE_WIDTH_MM,
    PaperError,
    PaperSpec,
    calc_axes,
    calc_geometry,
    horizontal_lines,
    vertical_lines,
)


class PaperSpecTest(unittest.TestCase):
    def test_defaults(self) -> None:
        spec = PaperSpec()
        self.assertEqual(spec.kind, "grid")
        self.assertEqual(spec.spacing_mm, 5)
        self.assertEqual(spec.pages, 1)
        self.assertEqual(spec.title, "方格纸")
        self.assertEqual(spec.display_name, "方格纸")

    def test_default_title_follows_type(self) -> None:
        self.assertEqual(PaperSpec(kind="dot").title, "点阵纸")
        self.assertEqual(PaperSpec(kind="coordinate").title, "坐标纸")

    def test_title_is_stripped(self) -> None:
        spec = PaperSpec(title="  我的方格纸  ")
        self.assertEqual(spec.title, "我的方格纸")

    def test_reject_unknown_type(self) -> None:
        with self.assertRaises(PaperError) as ctx:
            PaperSpec(kind="hex")
        self.assertIn("纸张类型", str(ctx.exception))

    def test_reject_non_text_type(self) -> None:
        with self.assertRaises(PaperError):
            PaperSpec(kind=3)  # type: ignore[arg-type]

    def test_reject_too_small_spacing(self) -> None:
        with self.assertRaises(PaperError) as ctx:
            PaperSpec(spacing_mm=1)
        self.assertIn("2~20", str(ctx.exception))

    def test_reject_too_large_spacing(self) -> None:
        with self.assertRaises(PaperError):
            PaperSpec(spacing_mm=21)

    def test_reject_float_spacing(self) -> None:
        with self.assertRaises(PaperError):
            PaperSpec(spacing_mm=2.5)  # type: ignore[arg-type]

    def test_reject_bool_spacing(self) -> None:
        with self.assertRaises(PaperError):
            PaperSpec(spacing_mm=True)  # type: ignore[arg-type]

    def test_reject_zero_pages(self) -> None:
        with self.assertRaises(PaperError):
            PaperSpec(pages=0)

    def test_reject_too_many_pages(self) -> None:
        with self.assertRaises(PaperError):
            PaperSpec(pages=51)

    def test_reject_blank_title(self) -> None:
        with self.assertRaises(PaperError) as ctx:
            PaperSpec(title="   ")
        self.assertIn("标题", str(ctx.exception))

    def test_reject_non_text_title(self) -> None:
        with self.assertRaises(PaperError):
            PaperSpec(title=12)  # type: ignore[arg-type]


class GeometryTest(unittest.TestCase):
    def test_five_millimeter_grid(self) -> None:
        geometry = calc_geometry(PaperSpec(spacing_mm=5))
        self.assertEqual(geometry.columns, 37)
        self.assertEqual(geometry.rows, 54)
        self.assertEqual(geometry.x0, MARGIN_MM)
        self.assertEqual(geometry.y0, MARGIN_MM)

    def test_ten_millimeter_grid(self) -> None:
        geometry = calc_geometry(PaperSpec(spacing_mm=10))
        self.assertEqual(geometry.columns, 18)
        self.assertEqual(geometry.rows, 27)

    def test_two_millimeter_grid(self) -> None:
        geometry = calc_geometry(PaperSpec(spacing_mm=2))
        self.assertEqual(geometry.columns, 93)
        self.assertEqual(geometry.rows, 136)

    def test_grid_stays_inside_page(self) -> None:
        geometry = calc_geometry(PaperSpec(spacing_mm=7))
        self.assertLessEqual(geometry.x1, PAGE_WIDTH_MM - MARGIN_MM)
        self.assertLessEqual(geometry.y1, PAGE_HEIGHT_MM - MARGIN_MM)

    def test_points_count(self) -> None:
        geometry = calc_geometry(PaperSpec(spacing_mm=10))
        self.assertEqual(geometry.points, 19 * 28)

    def test_vertical_lines(self) -> None:
        geometry = calc_geometry(PaperSpec(spacing_mm=10))
        lines = vertical_lines(geometry)
        self.assertEqual(len(lines), geometry.columns + 1)
        self.assertAlmostEqual(lines[0], MARGIN_MM)
        self.assertAlmostEqual(lines[-1], geometry.x1)

    def test_horizontal_lines(self) -> None:
        geometry = calc_geometry(PaperSpec(spacing_mm=10))
        lines = horizontal_lines(geometry)
        self.assertEqual(len(lines), geometry.rows + 1)
        self.assertAlmostEqual(lines[0], MARGIN_MM)
        self.assertAlmostEqual(lines[-1], geometry.y1)

    def test_line_spacing_is_uniform(self) -> None:
        geometry = calc_geometry(PaperSpec(spacing_mm=4))
        lines = vertical_lines(geometry)
        gaps = {round(b - a, 6) for a, b in zip(lines, lines[1:])}
        self.assertEqual(gaps, {4.0})


class AxesTest(unittest.TestCase):
    def test_origin_near_page_center(self) -> None:
        geometry = calc_geometry(PaperSpec(kind="coordinate"))
        axes = calc_axes(geometry)
        self.assertAlmostEqual(axes.x, 107.0)
        self.assertAlmostEqual(axes.y, 147.0)

    def test_origin_inside_grid(self) -> None:
        geometry = calc_geometry(PaperSpec(kind="coordinate", spacing_mm=20))
        axes = calc_axes(geometry)
        self.assertGreater(axes.x, geometry.x0)
        self.assertLess(axes.x, geometry.x1)
        self.assertGreater(axes.y, geometry.y0)
        self.assertLess(axes.y, geometry.y1)

    def test_labels_are_whole_centimeters(self) -> None:
        geometry = calc_geometry(PaperSpec(kind="coordinate"))
        axes = calc_axes(geometry)
        values = [int(text) for _, text in axes.x_labels]
        self.assertTrue(values)
        self.assertNotIn(0, values)
        expected = [v for v in range(values[0], values[-1] + 1) if v != 0]
        self.assertEqual(values, expected)

    def test_y_labels_rise_upwards(self) -> None:
        geometry = calc_geometry(PaperSpec(kind="coordinate"))
        axes = calc_axes(geometry)
        pairs = list(axes.y_labels)
        self.assertEqual(pairs, sorted(pairs, key=lambda item: item[0]))
        self.assertGreater(int(pairs[0][1]), int(pairs[-1][1]))

    def test_x_labels_increase_rightwards(self) -> None:
        geometry = calc_geometry(PaperSpec(kind="coordinate"))
        axes = calc_axes(geometry)
        pairs = list(axes.x_labels)
        self.assertEqual(pairs, sorted(pairs, key=lambda item: item[0]))
        self.assertLess(int(pairs[0][1]), int(pairs[-1][1]))


if __name__ == "__main__":
    unittest.main()
