import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Append absolute path to current workspace root to run tests properly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from orchestrator import VirtualStudioOrchestrator
from config.settings import PORT

API_BASE_URL = f"http://localhost:{PORT}/api"

class TestOrchestrator(unittest.TestCase):
    
    def setUp(self):
        self.task_id = "TASK-TEST-777"
        self.room_id = "tf_room_test_777"
        self.room_name = "테스트 격리방"
        self.allowed_agents = ["Concept-Agent", "Art-Agent", "Dev-Agent"]
        self.orchestrator = VirtualStudioOrchestrator(
            self.task_id, self.room_id, self.room_name, self.allowed_agents
        )
        self.orchestrator.log_audit = MagicMock()

    @patch("requests.post")
    @patch("requests.patch")
    def test_initialize_studio(self, mock_patch, mock_post):
        # Scenario A: First time registration returns 201 Created for both task and room
        mock_res_201 = MagicMock()
        mock_res_201.status_code = 201
        mock_post.return_value = mock_res_201

        self.orchestrator.initialize_studio("Tetris Title", "Tetris Desc")

        # Check API endpoints were queried (1 for tasks, 1 for rooms)
        self.assertEqual(mock_post.call_count, 2)
        mock_post.assert_any_call(
            f"{API_BASE_URL}/tasks",
            json={
                "task_id": self.task_id,
                "title": "Tetris Title",
                "description": "Tetris Desc",
                "status": "IN_PROGRESS"
            },
            timeout=10
        )
        mock_post.assert_any_call(
            f"{API_BASE_URL}/rooms",
            json={
                "room_id": self.room_id,
                "room_name": self.room_name,
                "task_id": self.task_id,
                "allowed_agents": self.allowed_agents
            },
            timeout=10
        )

        # Scenario B: Task already registered, POST tasks fails (e.g. returns 400), falls back to PATCH
        mock_post.reset_mock()
        mock_patch.reset_mock()

        def side_effect_post(url, **kwargs):
            res = MagicMock()
            if "/tasks" in url:
                res.status_code = 400
            elif "/rooms" in url:
                res.status_code = 201
            return res
        mock_post.side_effect = side_effect_post

        mock_patch_res = MagicMock()
        mock_patch_res.status_code = 200
        mock_patch.return_value = mock_patch_res

        self.orchestrator.initialize_studio("Tetris Title", "Tetris Desc")
        
        # Assert PATCH was called to update task status
        mock_patch.assert_called_once_with(
            f"{API_BASE_URL}/tasks/{self.task_id}",
            json={"status": "IN_PROGRESS"},
            timeout=10
        )

    @patch("requests.post")
    def test_unload_agent_vram(self, mock_post):
        mock_res = MagicMock()
        mock_res.status_code = 200
        mock_post.return_value = mock_res

        self.orchestrator.unload_agent_vram("qwen3.6:35b-mlx")
        
        mock_post.assert_called_once_with(
            f"{API_BASE_URL}/vram/unload",
            json={"model": "qwen3.6:35b-mlx"},
            timeout=10
        )

    @patch("requests.post")
    @patch("requests.get")
    def test_run_agent_turn_normal(self, mock_get, mock_post):
        # 1. Get dynamic prompt (normal)
        # 2. Get room context
        # 3. Post Ollama API call
        # 4. Post message to room
        
        def mock_get_side_effect(url, **kwargs):
            res = MagicMock()
            res.status_code = 200
            if "/context" in url:
                res.json.return_value = {"llm_history": [{"role": "user", "content": "hello"}]}
            return res
        mock_get.side_effect = mock_get_side_effect

        def mock_post_side_effect(url, **kwargs):
            res = MagicMock()
            res.status_code = 200
            if "/prompt" in url:
                res.json.return_value = {
                    "system_prompt": "You are Concept-Agent",
                    "recommended_temperature": 0.2,
                    "is_penalized": False
                }
            elif "/messages" in url:
                res.status_code = 201
            elif "api/chat" in url:
                res.status_code = 200
                res.json.return_value = {
                    "message": {"content": "Generated game concept"}
                }
            return res
        mock_post.side_effect = mock_post_side_effect

        response_text = self.orchestrator.run_agent_turn(
            "Concept-Agent", "base_prompt", "qwen3.6:35b-mlx"
        )
        
        self.assertEqual(response_text, "Generated game concept")
        
        # Verify /messages POST had the correct text
        mock_post.assert_any_call(
            f"{API_BASE_URL}/rooms/{self.room_id}/messages",
            json={
                "sender_role": "Concept-Agent",
                "content": "Generated game concept",
                "payload_type": "TEXT"
            },
            timeout=10
        )

    @patch("requests.post")
    @patch("requests.get")
    def test_run_agent_turn_penalized(self, mock_get, mock_post):
        # Penalized agent testing (should enforce temperature=0.0)
        def mock_get_side_effect(url, **kwargs):
            res = MagicMock()
            res.status_code = 200
            if "/context" in url:
                res.json.return_value = {"llm_history": []}
            return res
        mock_get.side_effect = mock_get_side_effect

        def mock_post_side_effect(url, **kwargs):
            res = MagicMock()
            res.status_code = 200
            if "/prompt" in url:
                res.json.return_value = {
                    "system_prompt": "[CRITICAL FACT MODE] You are penalized.",
                    "recommended_temperature": 0.0,
                    "is_penalized": True
                }
            elif "/messages" in url:
                res.status_code = 201
            elif "api/chat" in url:
                res.status_code = 200
                res.json.return_value = {
                    "message": {"content": "Penalized strictly correct response"}
                }
            return res
        mock_post.side_effect = mock_post_side_effect

        response_text = self.orchestrator.run_agent_turn(
            "Dev-Agent", "base_prompt", "gemma4:4b-mlx"
        )
        self.assertEqual(response_text, "Penalized strictly correct response")

    @patch("requests.get")
    def test_execute_cto_review_flow_bypassed(self, mock_get):
        mock_res = MagicMock()
        mock_res.status_code = 200
        mock_res.json.return_value = {"cto_review_enabled": False}
        mock_get.return_value = mock_res

        status = self.orchestrator.execute_cto_review_flow("calc_sample.py")
        self.assertEqual(status, "PASSED_BYPASSED")

    @patch("requests.get")
    @patch("subprocess.run")
    def test_execute_cto_review_flow_passed(self, mock_sub, mock_get):
        mock_get_res = MagicMock()
        mock_get_res.status_code = 200
        mock_get_res.json.return_value = {"cto_review_enabled": True}
        mock_get.return_value = mock_get_res

        mock_sub_res = MagicMock()
        mock_sub_res.returncode = 0
        mock_sub_res.stdout = "AST verification passed successfully."
        mock_sub.return_value = mock_sub_res

        status = self.orchestrator.execute_cto_review_flow("calc_sample.py")
        self.assertEqual(status, "PASSED")

    @patch("requests.post")
    @patch("requests.get")
    @patch("subprocess.run")
    def test_execute_cto_review_flow_rejected_and_pardoned(self, mock_sub, mock_get, mock_post):
        mock_get_res = MagicMock()
        mock_get_res.status_code = 200
        mock_get_res.json.return_value = {"cto_review_enabled": True}
        mock_get.return_value = mock_get_res

        # returncode = 1, and stdout has "CTO REJECT" to trigger pardon
        mock_sub_res = MagicMock()
        mock_sub_res.returncode = 1
        mock_sub_res.stdout = "CTO REJECT: Giant function violates 50-line rule"
        mock_sub.return_value = mock_sub_res

        mock_pardon_res = MagicMock()
        mock_pardon_res.status_code = 200
        mock_post.return_value = mock_pardon_res

        status = self.orchestrator.execute_cto_review_flow("calc_sample.py")
        self.assertEqual(status, "REJECTED")

        # Verify that pardon API was called
        mock_post.assert_any_call(
            f"{API_BASE_URL}/agents/Dev-Agent/pardon",
            json=None,
            timeout=10
        )

    @patch("requests.get")
    @patch("requests.post")
    @patch("requests.patch")
    @patch("orchestrator.send_discord_log")
    def test_finalize_studio(self, mock_discord, mock_patch, mock_post, mock_get):
        mock_post_res = MagicMock()
        mock_post_res.status_code = 200
        mock_post.return_value = mock_post_res

        mock_patch_res = MagicMock()
        mock_patch_res.status_code = 200
        mock_patch.return_value = mock_patch_res

        mock_get_res = MagicMock()
        mock_get_res.status_code = 200
        mock_get_res.json.return_value = {
            "office_health_index": 90.0,
            "vram_health": 100.0,
            "cto_compliance": 100.0,
            "backup_reliability": 100.0,
            "discipline_score": 100.0,
            "total_warnings": 0,
            "penalized_agents_count": 0
        }
        mock_get.return_value = mock_get_res

        self.orchestrator.finalize_studio("Game completed beautifully.")

        # Check endpoints
        mock_post.assert_called_once_with(
            f"{API_BASE_URL}/rooms/{self.room_id}/close",
            json=None,
            timeout=10
        )
        mock_patch.assert_called_once_with(
            f"{API_BASE_URL}/tasks/{self.task_id}",
            json={"status": "COMPLETED"},
            timeout=10
        )
        # Check Discord call
        mock_discord.assert_called_once()
        args, kwargs = mock_discord.call_args
        self.assertEqual(kwargs["color"], 3447003)  # Nice Blue
        self.assertIn("TASK-TEST-777", kwargs["content"])

        # Clean up any test diary files
        import glob
        import datetime
        today_str = datetime.datetime.now().strftime("%Y%m%d")
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        expected_diary = os.path.join(base_dir, "workspace", "audit", f"audit_diary_{today_str}.md")
        if os.path.exists(expected_diary):
            os.remove(expected_diary)

if __name__ == "__main__":
    unittest.main()
