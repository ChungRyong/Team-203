import unittest
import sys
import os
import shutil
import json
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

# Append absolute path to current workspace root to run tests properly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app

class TestArtGeneration(unittest.TestCase):
    
    def setUp(self):
        self.client = TestClient(app)
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.project_dir = os.path.join(self.base_dir, "workspace", "projects", "game_test_art")
        self.art_dir = os.path.join(self.project_dir, "art")
        os.makedirs(self.art_dir, exist_ok=True)
        
    def tearDown(self):
        # Clean up game_test_art sandbox
        if os.path.exists(self.project_dir):
            shutil.rmtree(self.project_dir)
            
    def test_art_generate_success(self):
        # 1. Create fully isolated mock requests object
        mock_req = MagicMock()
        
        # Mock ComfyUI /prompt POST response
        mock_post_res = MagicMock()
        mock_post_res.status_code = 200
        mock_post_res.json.return_value = {"prompt_id": "prompt-12345"}
        mock_req.post.return_value = mock_post_res
        
        # Mock ComfyUI /history/{prompt_id} GET response showing successful completion
        mock_get_res = MagicMock()
        mock_get_res.status_code = 200
        mock_get_res.json.return_value = {
            "prompt-12345": {
                "outputs": {
                    "9": {
                        "images": [
                            {"filename": "Team203_Art_00001.png"}
                        ]
                    }
                }
            }
        }
        mock_req.get.return_value = mock_get_res
        
        # Write a mock file inside ComfyUI/output so shutil.copy finds it
        comfy_output_dir = os.path.join(self.base_dir, "ComfyUI", "output")
        os.makedirs(comfy_output_dir, exist_ok=True)
        src_image_path = os.path.join(comfy_output_dir, "Team203_Art_00001.png")
        with open(src_image_path, "wb") as f:
            f.write(b"mock_image_bytes")
            
        try:
            payload = {
                "project_id": "game_test_art",
                "asset_type": "SPRITE",
                "prompt": "pixel art hero character running",
                "seed": 123456
            }
            # Patch app.main.requests dynamically inside this context
            with patch("app.main.requests", mock_req):
                res = self.client.post("/api/art/generate", json=payload)
            
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.json()["status"], "success")
            self.assertEqual(res.json()["filename"], "sprite_01.png")
            
            # Assert file exists and has correct bytes
            target_filepath = os.path.join(self.art_dir, "sprite_01.png")
            self.assertTrue(os.path.exists(target_filepath))
            with open(target_filepath, "rb") as f:
                self.assertEqual(f.read(), b"mock_image_bytes")
                
            # Assert metadata.json was updated
            metadata_path = os.path.join(self.art_dir, "metadata.json")
            self.assertTrue(os.path.exists(metadata_path))
            with open(metadata_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
                self.assertEqual(len(meta["assets"]), 1)
                self.assertEqual(meta["assets"][0]["filename"], "sprite_01.png")
                self.assertEqual(meta["assets"][0]["is_fallback"], False)
        finally:
            # Cleanup mock comfy output image
            if os.path.exists(src_image_path):
                os.remove(src_image_path)
            # Remove comfy output dir if empty
            try:
                os.rmdir(comfy_output_dir)
            except Exception:
                pass

    def test_art_generate_fail_safe_offline(self):
        # Force a connection exception to simulate offline ComfyUI
        mock_req = MagicMock()
        mock_req.post.side_effect = Exception("ComfyUI Connection Refused")
        
        payload = {
            "project_id": "game_test_art",
            "asset_type": "UI_WIREFRAME",
            "prompt": "neon wireframe layout",
            "seed": -1
        }
        with patch("app.main.requests", mock_req):
            res = self.client.post("/api/art/generate", json=payload)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["status"], "warning")
        self.assertIn("ComfyUI offline", res.json()["message"])
        self.assertEqual(res.json()["filename"], "ui_wireframe_01.png")
        
        # Verify placeholder PNG file was generated physically and is valid 1x1 png
        target_filepath = os.path.join(self.art_dir, "ui_wireframe_01.png")
        self.assertTrue(os.path.exists(target_filepath))
        with open(target_filepath, "rb") as f:
            header = f.read(8)
            self.assertEqual(header, b'\x89PNG\r\n\x1a\n') # standard PNG header
            
        # Verify metadata sidecar
        metadata_path = os.path.join(self.art_dir, "metadata.json")
        self.assertTrue(os.path.exists(metadata_path))
        with open(metadata_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
            self.assertEqual(meta["assets"][0]["is_fallback"], True)
            self.assertIn("ComfyUI Connection Refused", meta["assets"][0]["fallback_reason"])

if __name__ == "__main__":
    unittest.main()
