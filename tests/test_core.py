import unittest

from unused_imports_cli.core import find_unused_imports


class TestFindUnusedImports(unittest.TestCase):
    def test_simple_unused_import(self) -> None:
        result = find_unused_imports("import os\n")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, "os")
        self.assertEqual(result[0].line, 1)

    def test_used_import_not_flagged(self) -> None:
        result = find_unused_imports("import os\nprint(os.getcwd())\n")
        self.assertEqual(result, [])

    def test_import_as_alias(self) -> None:
        result = find_unused_imports("import numpy as np\n")
        self.assertEqual(result[0].name, "numpy as np")

    def test_used_alias_not_flagged(self) -> None:
        result = find_unused_imports("import numpy as np\nnp.array([1])\n")
        self.assertEqual(result, [])

    def test_from_import(self) -> None:
        result = find_unused_imports("from collections import OrderedDict\n")
        self.assertEqual(result[0].name, "collections.OrderedDict")

    def test_from_import_as(self) -> None:
        result = find_unused_imports("from collections import OrderedDict as OD\n")
        self.assertEqual(result[0].name, "collections.OrderedDict as OD")

    def test_dotted_import_binds_root(self) -> None:
        result = find_unused_imports("import os.path\nprint(os.getcwd())\n")
        self.assertEqual(result, [])

    def test_multiple_unused(self) -> None:
        result = find_unused_imports("import os\nimport sys\nimport json\n")
        self.assertEqual([u.name for u in result], ["os", "sys", "json"])

    def test_star_import_skipped(self) -> None:
        result = find_unused_imports("from os import *\n")
        self.assertEqual(result, [])

    def test_all_export_counts_as_used(self) -> None:
        result = find_unused_imports("from mod import helper\n\n__all__ = ['helper']\n")
        self.assertEqual(result, [])

    def test_used_in_function_body(self) -> None:
        source = "import json\n\ndef load(s):\n    return json.loads(s)\n"
        result = find_unused_imports(source)
        self.assertEqual(result, [])

    def test_used_in_type_annotation(self) -> None:
        source = "from typing import Optional\n\ndef f(x: Optional[int]) -> None:\n    pass\n"
        result = find_unused_imports(source)
        self.assertEqual(result, [])

    def test_relative_import(self) -> None:
        result = find_unused_imports("from . import helper\n")
        self.assertEqual(result[0].name, ".helper")


if __name__ == "__main__":
    unittest.main()
