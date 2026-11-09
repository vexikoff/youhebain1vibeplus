import tempfile
import unittest
from pathlib import Path

from build_preflight import check_project


MAIN_SOURCE = """
import pygame

def asset_path(name):
    return name

pygame.mixer.music.load(asset_path('theme.wav'))
pygame.mixer.Sound(asset_path('effect.wav'))
"""

SPEC_SOURCE = """
a = Analysis(['main.py'], datas=[('theme.wav', '.'), ('effect.wav', '.')])
exe = EXE(a, name='test-game', icon='icon.ico', console=True)
coll = COLLECT(exe, name='test-game')
"""


class BuildPreflightTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        (self.root / "main.py").write_text(MAIN_SOURCE, encoding="utf-8")
        (self.root / "game.spec").write_text(SPEC_SOURCE, encoding="utf-8")
        (self.root / "theme.wav").write_bytes(b"theme")
        (self.root / "effect.wav").write_bytes(b"effect")
        (self.root / "icon.ico").write_bytes(b"icon")

    def tearDown(self):
        self.temporary.cleanup()

    def test_valid_build_configuration_passes(self):
        self.assertEqual(check_project(self.root), [])

    def test_reports_runtime_asset_missing_from_spec(self):
        (self.root / "game.spec").write_text(
            "a = Analysis(['main.py'], datas=[('theme.wav', '.')])\n"
            "exe = EXE(a, name='test-game', icon='icon.ico', console=True)\n"
            "coll = COLLECT(exe, name='test-game')\n",
            encoding="utf-8",
        )
        errors = check_project(self.root)
        self.assertTrue(any("effect.wav" in error and "Analysis.datas" in error for error in errors))

    def test_reports_missing_icon_and_disabled_console(self):
        (self.root / "game.spec").write_text(
            "a = Analysis(['main.py'], datas=[('theme.wav', '.'), ('effect.wav', '.')])\n"
            "exe = EXE(a, name='test-game', icon='missing.ico', console=False)\n"
            "coll = COLLECT(exe, name='test-game')\n",
            encoding="utf-8",
        )
        errors = check_project(self.root)
        self.assertTrue(any("icon file not found" in error for error in errors))
        self.assertTrue(any("console must be True" in error for error in errors))

    def test_reports_mismatched_executable_and_distribution_names(self):
        (self.root / "game.spec").write_text(
            "a = Analysis(['main.py'], datas=[('theme.wav', '.'), ('effect.wav', '.')])\n"
            "exe = EXE(a, name='test-game', icon='icon.ico', console=True)\n"
            "coll = COLLECT(exe, name='other-name')\n",
            encoding="utf-8",
        )
        errors = check_project(self.root)
        self.assertTrue(any("names must both be set and match" in error for error in errors))

    def test_reports_missing_or_empty_runtime_files(self):
        (self.root / "theme.wav").unlink()
        (self.root / "effect.wav").write_bytes(b"")
        errors = check_project(self.root)
        self.assertTrue(any("runtime asset not found: theme.wav" in error for error in errors))
        self.assertTrue(any("runtime asset is empty: effect.wav" in error for error in errors))

    def test_reports_malformed_spec(self):
        (self.root / "game.spec").write_text("a = Analysis(", encoding="utf-8")
        errors = check_project(self.root)
        self.assertTrue(any("game.spec" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
