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

class TestQaPipeline(unittest.TestCase):
    
    def setUp(self):
        self.client = TestClient(app)
        # Clean system_audit_logs to ensure isolated calculations
        conn = database.get_db_connection()
        try:
            conn.execute("DELETE FROM system_audit_logs;")
            conn.execute("DELETE FROM agent_penalties;")
            # Seed penalties for clean scores
            conn.execute("INSERT OR REPLACE INTO agent_penalties (agent_name, warning_count, is_penalized) VALUES ('Concept-Agent', 0, 0);")
            conn.execute("INSERT OR REPLACE INTO agent_penalties (agent_name, warning_count, is_penalized) VALUES ('Art-Agent', 0, 0);")
            conn.execute("INSERT OR REPLACE INTO agent_penalties (agent_name, warning_count, is_penalized) VALUES ('Dev-Agent', 0, 0);")
            conn.commit()
        except Exception as e:
            print(f"Failed setup clean: {e}")
        finally:
            conn.close()
            
    def tearDown(self):
        conn = database.get_db_connection()
        try:
            conn.execute("DELETE FROM system_audit_logs;")
            conn.commit()
        finally:
            conn.close()

    def test_post_qa_verify_success(self):
        payload = {
            "task_id": "TASK-QA-01",
            "test_suite_name": "Tetris_Grid_Collision",
            "total_cases": 20,
            "passed_cases": 20,
            "failed_cases": 0
        }
        res = self.client.post("/api/qa/verify", json=payload)
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.json()["status"], "success")
        self.assertEqual(res.json()["success_rate"], 100.0)
        self.assertEqual(res.json()["outcome"], "SUCCESS")
        
        # Verify Database
        conn = database.get_db_connection()
        row = conn.execute("SELECT * FROM system_audit_logs ORDER BY log_id DESC LIMIT 1").fetchone()
        conn.close()
        
        self.assertIsNotNone(row)
        self.assertEqual(row["event_type"], "GAME_QA")
        self.assertEqual(row["status"], "SUCCESS")
        
        details = json.loads(row["details"])
        self.assertEqual(details["test_suite_name"], "Tetris_Grid_Collision")
        self.assertEqual(details["success_rate"], 100.0)

    def test_post_qa_verify_failed(self):
        # 90% pass rate -> Outcome FAILED (< 95%)
        payload = {
            "task_id": "TASK-QA-02",
            "test_suite_name": "Tetromino_Edge_Cases",
            "total_cases": 20,
            "passed_cases": 18,
            "failed_cases": 2
        }
        res = self.client.post("/api/qa/verify", json=payload)
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.json()["status"], "success")
        self.assertEqual(res.json()["success_rate"], 90.0)
        self.assertEqual(res.json()["outcome"], "FAILED")
        
        # Verify Database status
        conn = database.get_db_connection()
        row = conn.execute("SELECT * FROM system_audit_logs ORDER BY log_id DESC LIMIT 1").fetchone()
        conn.close()
        
        self.assertIsNotNone(row)
        self.assertEqual(row["status"], "FAILED")

    def test_get_audit_summary_with_5_factor_including_qa_health(self):
        # Seed VRAM, CTO, Git, QA Health logs
        conn = database.get_db_connection()
        conn.execute("INSERT INTO system_audit_logs (event_type, status) VALUES ('VRAM_UNLOAD', 'SUCCESS');")
        conn.execute("INSERT INTO system_audit_logs (event_type, status) VALUES ('CTO_REVIEW', 'SUCCESS');")
        conn.execute("INSERT INTO system_audit_logs (event_type, status) VALUES ('GIT_SNAPSHOT', 'SUCCESS');")
        
        # QA logs: 1 success (100%), 1 fail (80%) -> average: 90%
        det_ok = json.dumps({"success_rate": 100.0})
        det_fail = json.dumps({"success_rate": 80.0})
        conn.execute("INSERT INTO system_audit_logs (event_type, status, details) VALUES ('GAME_QA', 'SUCCESS', ?);", (det_ok,))
        conn.execute("INSERT INTO system_audit_logs (event_type, status, details) VALUES ('GAME_QA', 'FAILED', ?);", (det_fail,))
        conn.commit()
        conn.close()
        
        res = self.client.get("/api/audit/summary")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        
        # Asserts for 5-factor scores
        self.assertEqual(data["vram_health"], 100.0)
        self.assertEqual(data["cto_compliance"], 100.0)
        self.assertEqual(data["backup_reliability"], 100.0)
        self.assertEqual(data["discipline_score"], 100.0)
        self.assertEqual(data["qa_health"], 90.0)
        
        # 5-factor aggregated index: (100+100+100+100+90)/5 = 98.0%
        self.assertEqual(data["office_health_index"], 98.0)

    @patch("orchestrator.VirtualStudioOrchestrator.call_api")
    def test_orchestrator_execute_qa_stage_passed(self, mock_api):
        orchestrator = VirtualStudioOrchestrator(
            task_id="TASK-QA-TEST",
            room_id="tf_qa_test",
            room_name="QA Unit Test Room",
            allowed_agents=["Concept-Agent", "Dev-Agent"]
        )
        
        # Mock successful QA API response
        mock_res = MagicMock()
        mock_res.status_code = 201
        mock_res.json.return_value = {
            "status": "success",
            "success_rate": 100.0,
            "outcome": "SUCCESS"
        }
        mock_api.return_value = mock_res
        
        status = orchestrator.execute_qa_audit_stage("Grid_Collision", 20, 20)
        self.assertEqual(status, "PASSED")
        
        # Verify correct payload was sent
        mock_api.assert_any_call(
            "POST",
            "/qa/verify",
            {
                "task_id": "TASK-QA-TEST",
                "test_suite_name": "Grid_Collision",
                "total_cases": 20,
                "passed_cases": 20,
                "failed_cases": 0
            }
        )

    @patch("orchestrator.VirtualStudioOrchestrator.call_api")
    def test_orchestrator_execute_qa_stage_rejected(self, mock_api):
        orchestrator = VirtualStudioOrchestrator(
            task_id="TASK-QA-TEST",
            room_id="tf_qa_test",
            room_name="QA Unit Test Room",
            allowed_agents=["Concept-Agent", "Dev-Agent"]
        )
        
        # Mock failed QA API response (90% success < 95% threshold)
        mock_res_qa = MagicMock()
        mock_res_qa.status_code = 201
        mock_res_qa.json.return_value = {
            "status": "success",
            "success_rate": 90.0,
            "outcome": "FAILED"
        }
        
        mock_res_penalize = MagicMock()
        mock_res_penalize.status_code = 200
        
        # Return mock QA result then mock penalty result
        mock_api.side_effect = [mock_res_qa, mock_res_penalize]
        
        status = orchestrator.execute_qa_audit_stage("Edge_Cases", 20, 18)
        self.assertEqual(status, "REJECTED")
        
        # Verify Dev-Agent penalize API was called
        mock_api.assert_any_call(
            "POST",
            "/agents/Dev-Agent/penalize",
            {"reason": "게임 QA 1단계(Edge_Cases) 실패 (성공율 90.0%)"}
        )

if __name__ == "__main__":
    unittest.main()
