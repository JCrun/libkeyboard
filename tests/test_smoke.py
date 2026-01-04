import sys
import os
import unittest
import time

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from libkeyboard import KeyBoard, keyboard_write, keyboard_group

class TestSmoke(unittest.TestCase):
    def test_import(self):
        """Test if the module can be imported"""
        self.assertIsNotNone(KeyBoard)
        self.assertIsNotNone(keyboard_write)
        self.assertIsNotNone(keyboard_group)

    def test_instantiate(self):
        """Test if KeyBoard can be instantiated and closed"""
        try:
            with KeyBoard() as kb:
                pass
        except Exception as e:
            # Depending on the environment (e.g. headless Linux without Xvfb), this might fail.
            # But we want to know if it fails due to code errors or env errors.
            # In GitHub Actions with Xvfb (Linux) or Windows, it should pass.
            self.fail(f"Failed to instantiate KeyBoard: {e}")

    def test_write_api(self):
        """Test high-level write API (mock run)"""
        # We don't want to actually type into the console during test if possible,
        # but keyboard_write sends events globally.
        # Just calling it to ensure no exceptions are raised.
        try:
            # Type something short
            keyboard_write("test", delay=0.01)
        except Exception as e:
            self.fail(f"keyboard_write failed: {e}")

if __name__ == '__main__':
    unittest.main()
