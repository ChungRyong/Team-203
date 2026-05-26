import unittest
import sys
import os
import sqlite3
import json
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

# Append absolute path to current workspace root to run tests properly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app import database
from orchestrator import VirtualStudioOrchestrator

class TestSystemAudits(unittest.TestCase):
    
    def setUp(self):
        self.client = TestClient(app)
        # Clean system_audit_logs table to ensure isolated test calculations
        conn = database.get_db_connection()
        try:
            conn.execute("DELETE FROM system_audit_logs;")
            # Also clear penalties for clean discipline score
            conn.execute("DELETE FROM agent_penalties;")
            # Seed default agent penalties
            conn.execute("INSERT OR REPLACE INTO agent_penalties (agent_name, warning_count, is_penalized) VALUES ('Concept-Agent', 0, 0);")
            conn.execute("INSERT OR REPLACE INTO agent_penalties (agent_name, warning_count, is_penalized) VALUES ('Art-Agent', 0, 0);")
            conn.execute("INSERT OR REPLACE INTO agent_penalties (agent_name, warning_count, is_penalized) VALUES ('Dev-Agent', 0, 0);")
            conn.commit()
        except Exception as e:
            print(f"Failed setup clean: {e}")
        finally:
            conn.close()
            
    def tearDown(self):
        # Clean up after test
        conn = database.get_db_connection()
        try:
            conn.execute("DELETE FROM system_audit_logs;")
            conn.commit()
        finally:
            conn.close()

    def test_post_audit_log_success(self):
        payload = {
            "event_type": "VRAM_UNLOAD",
            "status": "SUCCESS",
            "details": {"model": "qwen3.6:35b-mlx"},
            "elapsed_ms": 150
        }
        res = self.client.post("/api/audit/log", json=payload)
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.json()["status"], "success")
        
        # Verify database entry
        conn = database.get_db_connection()
        row = conn.execute("SELECT * FROM system_audit_logs ORDER BY log_id DESC LIMIT 1").fetchone()
        conn.close()
        
        self.assertIsNotNone(row)
        self.assertEqual(row["event_type"], "VRAM_UNLOAD")
        self.assertEqual(row["status"], "SUCCESS")
        self.assertEqual(row["elapsed_ms"], 150)
        details = json.loads(row["details"])
        self.assertEqual(details["model"], "qwen3.6:35b-mlx")

    def test_audit_summary_calculation(self):
        # 1. Seed different logs to compute metrics
        conn = database.get_db_connection()
        # VRAM Logs: 2 successes, 1 failure
        conn.execute("INSERT INTO system_audit_logs (event_type, status, elapsed_ms) VALUES ('VRAM_UNLOAD', 'SUCCESS', 100);")
        conn.execute("INSERT INTO system_audit_logs (event_type, status, elapsed_ms) VALUES ('VRAM_UNLOAD', 'SUCCESS', 120);")
        conn.execute("INSERT INTO system_audit_logs (event_type, status, elapsed_ms) VALUES ('VRAM_UNLOAD', 'FAILED', 0);")
        
        # CTO Logs: 3 successes, 1 failure
        conn.execute("INSERT INTO system_audit_logs (event_type, status, elapsed_ms) VALUES ('CTO_REVIEW', 'SUCCESS', 5000);")
        conn.execute("INSERT INTO system_audit_logs (event_type, status, elapsed_ms) VALUES ('CTO_REVIEW', 'SUCCESS', 4500);")
        conn.execute("INSERT INTO system_audit_logs (event_type, status, elapsed_ms) VALUES ('CTO_REVIEW', 'SUCCESS', 4800);")
        conn.execute("INSERT INTO system_audit_logs (event_type, status, elapsed_ms) VALUES ('CTO_REVIEW', 'FAILED', 200);")
        
        # Git logs: 1 success, 1 failure
        conn.execute("INSERT INTO system_audit_logs (event_type, status, elapsed_ms) VALUES ('GIT_SNAPSHOT', 'SUCCESS', 150);")
        conn.execute("INSERT INTO system_audit_logs (event_type, status, elapsed_ms) VALUES ('GIT_SNAPSHOT', 'FAILED', 50);")
        
        # Discipline: 1 warning for Dev-Agent, 0 penalties
        conn.execute("UPDATE agent_penalties SET warning_count = 1, is_penalized = 0 WHERE agent_name = 'Dev-Agent';")
        conn.commit()
        conn.close()
        
        # 2. Query Summary API
        res = self.client.get("/api/audit/summary")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        
        # 3. Assert precise calculation logic
        # VRAM Health: 2 / 3 = 66.67%
        self.assertAlmostEqual(data["vram_health"], 66.67, places=1)
        # CTO Compliance: 3 / 4 = 75.0%
        self.assertAlmostEqual(data["cto_compliance"], 75.0, places=1)
        # Backup Reliability: 1 / 2 = 50.0%
        self.assertAlmostEqual(data["backup_reliability"], 50.0, places=1)
        # Discipline Level: 100 - (1 warning * 10) = 90.0%
        self.assertAlmostEqual(data["discipline_score"], 90.0, places=1)
        
        self.assertEqual(data["warning_agents_count"], 1)
        self.assertEqual(data["penalized_agents_count"], 0)
        self.assertEqual(data["total_warnings"], 1)
        
        # Aggregated Health Index: (66.67 + 75.0 + 50.0 + 90.0) / 4 = 70.42%
        self.assertAlmostEqual(data["office_health_index"], 70.42, places=1)

    @patch("orchestrator.send_discord_log")
    def test_orchestrator_finalize_alert_embeds(self, mock_send_discord):
        """
        Verify that orchestrator finalize studio issues professional blue embeds
        when office health index is >= 80%, and emergency red embeds when health index < 80%.
        """
        orchestrator = VirtualStudioOrchestrator(
            task_id="TASK-AUDIT-TEST",
            room_id="tf_audit_test",
            room_name="Audit Integration Test TF Room",
            allowed_agents=["Concept-Agent", "Dev-Agent"]
        )
        
        # Case A: Good Health Score (e.g. 95%) -> Blue Embed
        with patch.object(orchestrator, "call_api") as mock_api:
            # Mock Close Room
            mock_close = MagicMock()
            mock_close.status_code = 200
            
            # Mock Update Task
            mock_update = MagicMock()
            mock_update.status_code = 200
            
            # Mock Summary (95% high health)
            mock_summary = MagicMock()
            mock_summary.status_code = 200
            mock_summary.json.return_value = {
                "office_health_index": 95.0,
                "vram_health": 100.0,
                "cto_compliance": 100.0,
                "backup_reliability": 100.0,
                "discipline_score": 80.0,
                "total_warnings": 2,
                "penalized_agents_count": 0
            }
            
            mock_api.side_effect = [mock_close, mock_update, mock_summary]
            
            # Finalize
            orchestrator.finalize_studio("Sample milestone overview")
            
            # Assertions for Blue Embed
            mock_send_discord.assert_called_once()
            args, kwargs = mock_send_discord.call_args
            self.assertEqual(kwargs["color"], 3447003) # Blue
            self.assertIn("🏆 [마일스톤 완료]", kwargs["title"])
            self.assertIn("사내 건강성 지수: **95.0%**", kwargs["content"])
            
        # Clear mock calls
        mock_send_discord.reset_mock()
        
        # Case B: Poor Health Score (e.g. 70%) -> Red Embed (color: 16711680)
        with patch.object(orchestrator, "call_api") as mock_api:
            # Mock Close Room
            mock_close = MagicMock()
            mock_close.status_code = 200
            
            # Mock Update Task
            mock_update = MagicMock()
            mock_update.status_code = 200
            
            # Mock Summary (70% poor health)
            mock_summary = MagicMock()
            mock_summary.status_code = 200
            mock_summary.json.return_value = {
                "office_health_index": 70.0,
                "vram_health": 50.0,
                "cto_compliance": 80.0,
                "backup_reliability": 50.0,
                "discipline_score": 100.0,
                "total_warnings": 0,
                "penalized_agents_count": 0
            }
            
            mock_api.side_effect = [mock_close, mock_update, mock_summary]
            
            # Finalize
            orchestrator.finalize_studio("Sample poor milestone overview")
            
            # Assertions for Red Embed
            mock_send_discord.assert_called_once()
            args, kwargs = mock_send_discord.call_args
            self.assertEqual(kwargs["color"], 16711680) # Red
            self.assertIn("🚨 [비상 경보]", kwargs["title"])
            self.assertIn("사내 건강성 지수: **70.0%**", kwargs["content"])
            
            # Verify file creation for diary
            import glob
            import datetime
            today_str = datetime.datetime.now().strftime("%Y%m%d")
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            expected_diary = os.path.join(base_dir, "workspace", "audit", f"audit_diary_{today_str}.md")
            
            self.assertTrue(os.path.exists(expected_diary))
            with open(expected_diary, "r", encoding="utf-8") as f:
                diary_text = f.read()
            self.assertIn(f"사내 건강성 지수 (Office Health Index): **[70.0%]**", diary_text)
            self.assertIn("비상 관리 위원회 권고 사항", diary_text)
            
            # Clean up the created diary to avoid littering
            if os.path.exists(expected_diary):
                os.remove(expected_diary)

if __name__ == "__main__":
    unittest.main()
