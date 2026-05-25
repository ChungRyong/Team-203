import unittest
import sys
import os
import shutil
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
        
    @patch("requests.post")
    @patch("requests.get")
    @patch("subprocess.run")
    def test_main_cli_failsafe_flow(self, mock_sub, mock_get, mock_post):
        # 1. Setup mock responses representing a safe file but Claude CLI missing (Fail-Safe trigger)
        filepath = os.path.join(self.test_dir, "safe_sample.py")
        code = "def fine():\n    return 42\n"
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(code)
            
        # Simulate local 'claude' CLI command not found (FileNotFoundError)
        mock_sub.side_effect = FileNotFoundError()
        
        # Mock task APIs
        mock_get_res = MagicMock()
        mock_get_res.status_code = 200
        mock_get_res.json.return_value = {"task_id": "TASK-123", "title": "Tetris", "status": "PENDING"}
        mock_get.return_value = mock_get_res
        
        mock_post_res = MagicMock()
        mock_post_res.status_code = 200
        mock_post.return_value = mock_post_res
        
        # Run main and ensure it handles the FileNotFoundError gracefully and exits with code 0 (success due to fail-safe)
        with patch("sys.argv", ["run_cto_review.py", filepath, "TASK-123"]):
            with self.assertRaises(SystemExit) as cm:
                main()
            self.assertEqual(cm.exception.code, 0)
            
        # Verify that it updated the task status to PASSED_WITHOUT_CLAUDE
        mock_post.assert_called_with(
            "http://localhost:8000/api/tasks", # or port env
            json={"task_id": "TASK-123", "title": "Tetris", "status": "PASSED_WITHOUT_CLAUDE"},
            timeout=5
        )

if __name__ == "__main__":
    unittest.main()
