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
        # 1. Setup mock response from Ollama API
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        # 2. Call the FastAPI endpoint
        payload = {
            "model": "qwen3.6:35b-mlx"
        }
        res = self.client.post("/api/vram/unload", json=payload)
        
        # 3. Assertions
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["status"], "success")
        self.assertEqual(res.json()["model"], "qwen3.6:35b-mlx")
        self.assertIn("unload model 'qwen3.6:35b-mlx'", res.json()["message"])
        
        # Verify that requests.post was actually called with keep_alive: 0
        mock_post.assert_called_once_with(
            "http://localhost:11434/api/chat",
            json={
                "model": "qwen3.6:35b-mlx",
                "messages": [],
                "keep_alive": 0
            },
            timeout=5
        )
        
    @patch("requests.post")
    def test_vram_unload_fail_safe(self, mock_post):
        # 1. Force the requests.post call to raise a connection error (Ollama is offline)
        mock_post.side_effect = Exception("Connection refused by Ollama")
        
        # 2. Call the FastAPI endpoint
        payload = {
            "model": "flux-dev-fp8"
        }
        res = self.client.post("/api/vram/unload", json=payload)
        
        # 3. Assertions (Should return success with status = 'warning' instead of crashing)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["status"], "warning")
        self.assertEqual(res.json()["model"], "flux-dev-fp8")
        self.assertIn("Ollama connection bypassed or offline", res.json()["message"])
        self.assertEqual(res.json()["error_detail"], "Connection refused by Ollama")

if __name__ == "__main__":
    unittest.main()
