import unittest
import sys
import os
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

# Append absolute path to current workspace root to run tests properly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app

class TestVramUnload(unittest.TestCase):
    
    def setUp(self):
        self.client = TestClient(app)
        
    @patch("requests.post")
    def test_vram_unload_success(self, mock_post):
        # 1. Call the FastAPI endpoint
        payload = {
            "model": "Qwen3.6-35B-A3B-8bit"
        }
        res = self.client.post("/api/vram/unload", json=payload)
        
        # 2. Assertions
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["status"], "success")
        self.assertEqual(res.json()["model"], "Qwen3.6-35B-A3B-8bit")
        self.assertIn("oMLX automatically manages VRAM", res.json()["message"])
        
        # Verify that requests.post was not called (bypassed)
        mock_post.assert_not_called()

if __name__ == "__main__":
    unittest.main()
