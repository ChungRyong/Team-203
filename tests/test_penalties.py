import unittest
import sys
import os
from fastapi.testclient import TestClient

# Append absolute path to current workspace root to run tests properly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import database
from app.main import app

class TestPenalties(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        # Initialize SQLite tables
        database.create_tables()
        
    def setUp(self):
        # Clean agent penalties table to guarantee test isolation
        conn = database.get_db_connection()
        try:
            conn.execute("DELETE FROM agent_penalties")
            conn.commit()
        finally:
            conn.close()
            
        # Seed core agent penalty structures
        database.seed_agent_penalties(["Hermes", "Concept-Agent", "Art-Agent", "Dev-Agent", "Blinky"])
        
        # Test FastAPI client
        self.client = TestClient(app)
        
    def test_agent_penalty_lifecycle(self):
        base_prompt = "당신은 수석 엔지니어입니다. 코드를 구현해 주세요."
        
        # 1. Verify initial state (unpenalized, recommended temperature is 0.2)
        prompt_data = {
            "base_prompt": base_prompt
        }
        res = self.client.post("/api/agents/Dev-Agent/prompt", json=prompt_data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["is_penalized"], False)
        self.assertEqual(res.json()["warning_count"], 0)
        self.assertEqual(res.json()["system_prompt"], base_prompt)
        self.assertEqual(res.json()["recommended_temperature"], 0.2)
        
        # 2. Strike One Warning
        penalize_data = {
            "reason": "1회 린트 검증 실패"
        }
        res = self.client.post("/api/agents/Dev-Agent/penalize", json=penalize_data)
        self.assertEqual(res.status_code, 200)
        status = res.json()["penalty_status"]
        self.assertEqual(status["warning_count"], 1)
        self.assertEqual(status["is_penalized"], False)
        
        # 3. Strike Two Warning
        penalize_data = {
            "reason": "2회 함수 날조 적발"
        }
        res = self.client.post("/api/agents/Dev-Agent/penalize", json=penalize_data)
        self.assertEqual(res.status_code, 200)
        status = res.json()["penalty_status"]
        self.assertEqual(status["warning_count"], 2)
        self.assertEqual(status["is_penalized"], False)
        
        # 4. Strike Three Warning (Three Strikes Out!)
        penalize_data = {
            "reason": "3회 린트 검증 무단 무시 및 허위 보고"
        }
        res = self.client.post("/api/agents/Dev-Agent/penalize", json=penalize_data)
        self.assertEqual(res.status_code, 200)
        status = res.json()["penalty_status"]
        self.assertEqual(status["warning_count"], 3)
        self.assertEqual(status["is_penalized"], True) # Penalized!
        
        # 5. Verify penalized state (penalized, prefix injected, recommended temperature locked to 0.0)
        res = self.client.post("/api/agents/Dev-Agent/prompt", json=prompt_data)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["is_penalized"], True)
        self.assertEqual(data["warning_count"], 3)
        self.assertTrue(data["system_prompt"].startswith("⚠️ [징계 집행 상태 - 절대 팩트 모드 고정]"))
        self.assertIn(base_prompt, data["system_prompt"])
        self.assertEqual(data["recommended_temperature"], 0.0) # Absolute Fact-Mode!

if __name__ == "__main__":
    unittest.main()
