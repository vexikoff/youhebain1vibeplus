import ast
import unittest
from pathlib import Path

from cpuinfo import get_cpu_info


ROOT = Path(__file__).parent


class CpuInfoSupportTests(unittest.TestCase):
    def test_main_imports_cpu_info_function_used_by_support(self):
        tree = ast.parse((ROOT / "main.py").read_text(encoding="utf-8"))
        imports_cpu_info = any(
            isinstance(node, ast.ImportFrom)
            and node.module == "cpuinfo"
            and any(alias.name == "get_cpu_info" for alias in node.names)
            for node in ast.walk(tree)
        )
        self.assertTrue(imports_cpu_info)

    def test_runtime_dependency_is_declared(self):
        requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8")
        dependencies = set(requirements.splitlines())
        self.assertIn("py-cpuinfo==9.0.0", dependencies)
        self.assertIn("requests==2.34.2", dependencies)
        self.assertIn("textual==8.2.8", dependencies)

    def test_cpu_info_api_returns_payload_fields(self):
        info = get_cpu_info()

        self.assertIsInstance(info, dict)
        self.assertIn("brand_raw", info)
        self.assertIn("arch", info)


if __name__ == "__main__":
    unittest.main()
