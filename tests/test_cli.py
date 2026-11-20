"""命令行入口的单元测试。"""

from __future__ import annotations

import io
import os
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from graphpaper.cli import main


class CliTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def run_cli(self, argv: list) -> tuple:
        out = io.StringIO()
        err = io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = main(argv)
        return code, out.getvalue(), err.getvalue()

    def test_generate_default_grid(self) -> None:
        output = self.tmp / "grid.html"
        code, out, err = self.run_cli(["-o", str(output)])
        self.assertEqual(code, 0, err)
        self.assertTrue(output.exists())
        self.assertIn("方格纸", out)
        self.assertIn("37×54", out)

    def test_html_is_utf8(self) -> None:
        output = self.tmp / "grid.html"
        self.assertEqual(self.run_cli(["-o", str(output)])[0], 0)
        content = output.read_text(encoding="utf-8")
        self.assertIn('lang="zh-CN"', content)

    def test_default_filename_uses_type(self) -> None:
        cwd = os.getcwd()
        os.chdir(self.tmp)
        try:
            code, _, _ = self.run_cli(["--type", "dot"])
            self.assertEqual(code, 0)
            self.assertTrue((self.tmp / "点阵纸.html").exists())
        finally:
            os.chdir(cwd)

    def test_coordinate_type(self) -> None:
        output = self.tmp / "coord.html"
        code, out, err = self.run_cli(
            ["--type", "coordinate", "--spacing", "10", "-o", str(output)]
        )
        self.assertEqual(code, 0, err)
        self.assertIn("坐标纸", out)
        self.assertIn(">O</text>", output.read_text(encoding="utf-8"))

    def test_custom_title(self) -> None:
        output = self.tmp / "t.html"
        self.assertEqual(
            self.run_cli(["--title", "数学练习纸", "-o", str(output)])[0], 0
        )
        self.assertIn("数学练习纸", output.read_text(encoding="utf-8"))

    def test_multiple_pages(self) -> None:
        output = self.tmp / "p.html"
        self.assertEqual(self.run_cli(["--pages", "2", "-o", str(output)])[0], 0)
        content = output.read_text(encoding="utf-8")
        self.assertEqual(content.count('<section class="sheet">'), 2)

    def test_invalid_type(self) -> None:
        code, _, err = self.run_cli(["--type", "hex"])
        self.assertEqual(code, 2)
        self.assertIn("纸张类型", err)

    def test_invalid_spacing(self) -> None:
        code, _, err = self.run_cli(["--spacing", "1"])
        self.assertEqual(code, 2)
        self.assertIn("间距", err)

    def test_invalid_pages(self) -> None:
        code, _, err = self.run_cli(["--pages", "0"])
        self.assertEqual(code, 2)
        self.assertIn("页数", err)

    def test_write_failure_returns_one(self) -> None:
        code, _, err = self.run_cli(["-o", str(self.tmp)])
        self.assertEqual(code, 1)
        self.assertIn("写入文件失败", err)

    def test_help_exits_zero(self) -> None:
        with self.assertRaises(SystemExit) as ctx:
            with redirect_stdout(io.StringIO()):
                main(["--help"])
        self.assertEqual(ctx.exception.code, 0)


if __name__ == "__main__":
    unittest.main()
