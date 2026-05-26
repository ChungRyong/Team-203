import unittest
import sys
import os
import shutil
import json
from unittest.mock import patch, MagicMock

# Append absolute path to current workspace root to run tests properly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from run_cto_review import analyze_file, get_function_line_count, main

class TestCtoReview(unittest.TestCase):
    
    def setUp(self):
        # Create a temp directory for source code test assets inside workspace
        self.test_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp_cto_review")
        os.makedirs(self.test_dir, exist_ok=True)
        
    def tearDown(self):
        # Cleanup temp directory
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
            
    def test_line_count_calculation(self):
        # 1. Write a mock python file with precise comments, docstrings and function lengths
        filepath = os.path.join(self.test_dir, "calc_sample.py")
        code = (
            "def small_function():\n"
            "    '''\n"
            "    This is a multi-line docstring.\n"
            "    It should be completely ignored.\n"
            "    '''\n"
            "    a = 1\n"
            "    # This is a comment to ignore\n"
            "    \n"
            "    b = 2\n"
            "    return a + b\n"
        )
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(code)
            
        violations = analyze_file(filepath)
        self.assertEqual(len(violations), 0) # No violations, only 3 clean active lines inside function
        
    def test_fifty_line_violation_triggers_penalty(self):
        # 1. Write an excessively long function (> 50 active clean lines)
        filepath = os.path.join(self.test_dir, "long_sample.py")
        
        long_body = "\n".join([f"    x_{i} = {i}" for i in range(55)]) # 55 clean lines of code
        code = f"def giant_function():\n{long_body}\n"
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(code)
            
        violations = analyze_file(filepath)
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0]["function"], "giant_function")
        self.assertEqual(violations[0]["lines"], 56) # 56 lines (1 signature line + 55 body lines)
        
    @patch("requests.patch")
    @patch("requests.get")
    @patch("subprocess.run")
    def test_main_cli_failsafe_flow(self, mock_sub, mock_get, mock_patch):
        # 1. Setup mock responses representing a safe file but Claude CLI missing (Fail-Safe trigger)
        filepath = os.path.join(self.test_dir, "safe_sample.py")
        code = "def fine():\n    return 42\n"
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(code)
            
        # Simulate local 'claude' CLI command not found (FileNotFoundError)
        mock_sub.side_effect = FileNotFoundError()
        
        # Route mock_get side effects to handle CONFIG endpoint
        def mock_get_side_effect(url, **kwargs):
            res = MagicMock()
            res.status_code = 200
            if "config/cto-review" in url:
                res.json.return_value = {"cto_review_enabled": True}
            return res
            
        mock_get.side_effect = mock_get_side_effect
        
        mock_patch_res = MagicMock()
        mock_patch_res.status_code = 200
        mock_patch.return_value = mock_patch_res
        
        # Run main and ensure it handles the FileNotFoundError gracefully and exits with code 0 (success due to fail-safe)
        with patch("sys.argv", ["run_cto_review.py", filepath, "TASK-123"]):
            with self.assertRaises(SystemExit) as cm:
                main()
            self.assertEqual(cm.exception.code, 0)
            
        # Verify that it updated the task status to PASSED_WITHOUT_CLAUDE
        mock_patch.assert_called_with(
            "http://localhost:8000/api/tasks/TASK-123", # or port env
            json={"status": "PASSED_WITHOUT_CLAUDE"},
            timeout=5
        )

    @patch("requests.get")
    def test_cto_review_disabled_bypasses_all(self, mock_get):
        # 1. Setup mock that return cto_review_enabled = False (OFF)
        mock_get_res = MagicMock()
        mock_get_res.status_code = 200
        mock_get_res.json.return_value = {"cto_review_enabled": False}
        mock_get.return_value = mock_get_res
        
        # 2. Write a highly illegal (> 50 lines) function that would normally fail AST and report penalty
        filepath = os.path.join(self.test_dir, "illegal_but_disabled.py")
        long_body = "\n".join([f"    x_{i} = {i}" for i in range(100)]) # 100 clean lines of code
        code = f"def giant_illegal_function():\n{long_body}\n"
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(code)
            
        # 3. Running main should bypass everything and exit with 0 (success)
        with patch("sys.argv", ["run_cto_review.py", filepath, "TASK-123"]):
            with self.assertRaises(SystemExit) as cm:
                main()
            self.assertEqual(cm.exception.code, 0) # Bypassed and succeeded!

    def test_asset_audit_success(self):
        # 1. Setup mock art directory and metadata.json inside test sandbox
        art_dir = os.path.join(self.test_dir, "art")
        os.makedirs(art_dir, exist_ok=True)
        
        metadata_path = os.path.join(art_dir, "metadata.json")
        mock_meta = {
            "assets": [
                {"filename": "ui_wireframe_01.png", "asset_type": "UI_WIREFRAME"},
                {"filename": "sprite_block_01.png", "asset_type": "SPRITE"}
            ]
        }
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(mock_meta, f)
            
        # 2. Write a clean source code that references only registered assets
        dev_dir = os.path.join(self.test_dir, "dev")
        os.makedirs(dev_dir, exist_ok=True)
        filepath = os.path.join(dev_dir, "tetris_clean.py")
        code = (
            "def load_game_assets():\n"
            "    logo = 'art/ui_wireframe_01.png'\n"
            "    block = 'res://art/sprite_block_01.png'\n"
            "    return logo, block\n"
        )
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(code)
            
        from run_cto_review import get_registered_assets, check_asset_violations
        
        # 3. Check registered list
        registered = get_registered_assets(filepath)
        self.assertEqual(len(registered), 2)
        self.assertIn("ui_wireframe_01.png", registered)
        self.assertIn("sprite_block_01.png", registered)
        
        # 4. Check violations (Should be zero!)
        violations = check_asset_violations(filepath, registered)
        self.assertEqual(len(violations), 0)

    def test_asset_audit_failure_unregistered_asset(self):
        # 1. Setup metadata.json
        art_dir = os.path.join(self.test_dir, "art")
        os.makedirs(art_dir, exist_ok=True)
        
        metadata_path = os.path.join(art_dir, "metadata.json")
        mock_meta = {
            "assets": [
                {"filename": "ui_wireframe_01.png", "asset_type": "UI_WIREFRAME"}
            ]
        }
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(mock_meta, f)
            
        # 2. Write code with unregistered asset 'sprite_fake_block.png'
        dev_dir = os.path.join(self.test_dir, "dev")
        os.makedirs(dev_dir, exist_ok=True)
        filepath = os.path.join(dev_dir, "tetris_dirty.py")
        code = (
            "def load_assets():\n"
            "    # Registered!\n"
            "    ok_ui = 'art/ui_wireframe_01.png'\n"
            "    # Unregistered design asset (Hallucination!)\n"
            "    fake_block = 'res://art/sprite_fake_block.png'\n"
            "    return ok_ui, fake_block\n"
        )
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(code)
            
        from run_cto_review import get_registered_assets, check_asset_violations
        
        registered = get_registered_assets(filepath)
        violations = check_asset_violations(filepath, registered)
        
        # Should detect 1 violation
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0]["filename"], "sprite_fake_block.png")
        self.assertEqual(violations[0]["reference"], "res://art/sprite_fake_block.png")

if __name__ == "__main__":
    unittest.main()
