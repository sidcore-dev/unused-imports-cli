import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory

from unused_imports_cli.cli import main


class TestCli(unittest.TestCase):
    def test_exit_code_0_when_clean(self) -> None:
        with TemporaryDirectory() as tmp:
            f = Path(tmp) / "a.py"
            f.write_text("import os\nprint(os.getcwd())\n")
            code = main([str(f)])
            self.assertEqual(code, 0)

    def test_exit_code_1_when_unused_found(self) -> None:
        with TemporaryDirectory() as tmp:
            f = Path(tmp) / "a.py"
            f.write_text("import os\n")
            code = main([str(f)])
            self.assertEqual(code, 1)

    def test_exit_code_2_on_parse_error(self) -> None:
        with TemporaryDirectory() as tmp:
            f = Path(tmp) / "a.py"
            f.write_text("def f(:\n")
            code = main([str(f)])
            self.assertEqual(code, 2)

    def test_exit_code_2_on_missing_file(self) -> None:
        code = main(["/nonexistent/path/does_not_exist.py"])
        self.assertEqual(code, 2)

    def test_output_format(self) -> None:
        with TemporaryDirectory() as tmp:
            f = Path(tmp) / "a.py"
            f.write_text("import os\n")
            out = io.StringIO()
            with redirect_stdout(out):
                main([str(f)])
            self.assertIn(f"{f}:1: unused import 'os'", out.getvalue())

    def test_scans_directory_recursively(self) -> None:
        with TemporaryDirectory() as tmp:
            sub = Path(tmp) / "pkg"
            sub.mkdir()
            (sub / "a.py").write_text("import os\n")
            (sub / "b.py").write_text("import sys\nprint(sys.argv)\n")
            out = io.StringIO()
            with redirect_stdout(out):
                code = main([tmp])
            self.assertEqual(code, 1)
            self.assertIn("unused import 'os'", out.getvalue())
            self.assertNotIn("unused import 'sys'", out.getvalue())

    def test_skips_pycache_directory(self) -> None:
        with TemporaryDirectory() as tmp:
            cache = Path(tmp) / "__pycache__"
            cache.mkdir()
            (cache / "bad.py").write_text("def f(:\n")
            (Path(tmp) / "good.py").write_text("x = 1\n")
            code = main([tmp])
            self.assertEqual(code, 0)


if __name__ == "__main__":
    unittest.main()
