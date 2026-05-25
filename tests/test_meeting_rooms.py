import unittest
import sys
import os
import sqlite3
from fastapi.testclient import TestClient

# Append absolute path to current workspace root to run tests properly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import database
from app.main import app

class TestMeetingRooms(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        # Initialize SQLite tables
        database.create_tables()
        
    def setUp(self):
        # Clean database tables before each test to guarantee test isolation
        conn = database.get_db_connection()
        try:
            conn.execute("DELETE FROM messages")
            conn.execute("DELETE FROM rooms")
            conn.execute("DELETE FROM tasks")
            conn.execute("DELETE FROM agent_penalties")
            conn.commit()
        finally:
            conn.close()
            
        # Seed core agent warning structures
        database.seed_agent_penalties(["Hermes", "Concept-Agent", "Art-Agent", "Dev-Agent", "Blinky"])
        
        # Test FastAPI client
        self.client = TestClient(app)
        
    def test_complete_meeting_room_lifecycle(self):
        # 1. Create a Task
        task_data = {
            "task_id": "TASK-TEST-001",
            "title": "테트리스 게임 기본 개발",
            "description": "Godot 4.2+ 엔진을 이용한 테트리스 웹 게임 프로토타입 작성",
            "status": "PENDING"
        }
        res = self.client.post("/api/tasks", json=task_data)
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.json()["status"], "success")
        
        # 2. Create a Room
        room_data = {
            "room_id": "tf_test_room",
            "room_name": "기획-개발 협업 TF룸",
            "task_id": "TASK-TEST-001",
            "allowed_agents": ["Concept-Agent", "Dev-Agent"]
        }
        res = self.client.post("/api/rooms", json=room_data)
        self.assertEqual(res.status_code, 201)
        
        # Verify room state
        res = self.client.get("/api/rooms/tf_test_room")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["turn_count"], 0)
        self.assertEqual(res.json()["is_active"], 1)
        
        # 3. Security Check: Post message from non-allowed agent should be rejected
        bad_msg = {
            "sender_role": "Art-Agent", # Art-Agent is not in allowed_agents!
            "content": "비개발 에셋입니다.",
            "payload_type": "TEXT"
        }
        res = self.client.post("/api/rooms/tf_test_room/messages", json=bad_msg)
        self.assertEqual(res.status_code, 403)
        self.assertIn("Access Denied", res.json()["detail"])
        
        # 4. Post 17 messages sequentially (alternating Concept-Agent and Dev-Agent)
        for i in range(1, 18):
            sender = "Concept-Agent" if i % 2 != 0 else "Dev-Agent"
            msg_data = {
                "sender_role": sender,
                "content": f"대화 턴 {i}입니다. 소스코드 및 논리 전개중...",
                "payload_type": "TEXT"
            }
            res = self.client.post("/api/rooms/tf_test_room/messages", json=msg_data)
            self.assertEqual(res.status_code, 201)
            
        # Verify turn count is 17
        res = self.client.get("/api/rooms/tf_test_room")
        self.assertEqual(res.json()["turn_count"], 17)
        
        # 5. Post 18th message (triggers warning)
        msg_18 = {
            "sender_role": "Concept-Agent",
            "content": "대화 턴 18입니다. 이제 한계가 머지않았습니다.",
            "payload_type": "TEXT"
        }
        res = self.client.post("/api/rooms/tf_test_room/messages", json=msg_18)
        self.assertEqual(res.status_code, 201)
        
        # Verify 18th warning triggers a System message in DB
        res = self.client.get("/api/rooms/tf_test_room/messages")
        messages = res.json()
        
        # We expect 19 messages in total: 18 user messages + 1 System warning message
        self.assertEqual(len(messages), 19)
        self.assertEqual(messages[-1]["sender_role"], "System")
        self.assertIn("18턴에 도달했습니다", messages[-1]["content"])
        
        # Verify room turn count is 18 (since System messages don't increment turn count)
        res = self.client.get("/api/rooms/tf_test_room")
        self.assertEqual(res.json()["turn_count"], 18)
        
        # 6. Post 19th message
        msg_19 = {
            "sender_role": "Dev-Agent",
            "content": "대화 턴 19입니다. 마지막 정적 린팅 패스 대기.",
            "payload_type": "TEXT"
        }
        res = self.client.post("/api/rooms/tf_test_room/messages", json=msg_19)
        self.assertEqual(res.status_code, 201)
        
        # 7. Post 20th message (Triggers Blinky Observer Context Compression Middleware!)
        # Because Ollama is not running in the testing runner environment, this will trigger our robust fallback!
        msg_20 = {
            "sender_role": "Concept-Agent",
            "content": "대화 턴 20입니다! 테트리스 스펙 최종 결정. 코드 블록도 아래에 보관합니다. ```python\ndef tetris():\n    pass\n```",
            "payload_type": "TEXT"
        }
        res = self.client.post("/api/rooms/tf_test_room/messages", json=msg_20)
        self.assertEqual(res.status_code, 201)
        
        # Verify Blinky Observer Intercept Output:
        # A. All previous raw messages are archived (is_archived = 1)
        res = self.client.get("/api/rooms/tf_test_room/messages?include_archived=true")
        all_messages = res.json()
        self.assertTrue(len(all_messages) > 20) # should include user messages + System warning + Blinky summary + System announcement
        
        # B. Active messages (is_archived = 0) should only be Blinky_Observer summary + System refresh announcement
        res = self.client.get("/api/rooms/tf_test_room/messages?include_archived=false")
        active_messages = res.json()
        self.assertEqual(len(active_messages), 2)
        
        self.assertEqual(active_messages[0]["sender_role"], "Blinky_Observer")
        self.assertEqual(active_messages[0]["payload_type"], "SYSTEM_SUMMARY")
        
        # Verify code block was successfully preserved in the fallback summarizer!
        self.assertIn("def tetris():", active_messages[0]["content"])
        
        self.assertEqual(active_messages[1]["sender_role"], "System")
        self.assertIn("성공적으로 요약 압축", active_messages[1]["content"])
        
        # C. Room turn_count resets to 0
        res = self.client.get("/api/rooms/tf_test_room")
        self.assertEqual(res.json()["turn_count"], 0)
        
        # 8. Check Context Compiler Endpoint `/api/rooms/{room_id}/context`
        res = self.client.get("/api/rooms/tf_test_room/context")
        self.assertEqual(res.status_code, 200)
        
        llm_history = res.json()["llm_history"]
        self.assertEqual(len(llm_history), 2) # 1 System baseline summary + 1 assistant message (System refresh notice)
        
        self.assertEqual(llm_history[0]["role"], "system")
        self.assertIn("[Blinky Baseline Context Summary]", llm_history[0]["content"])
        
        # 9. Close Room
        res = self.client.post("/api/rooms/tf_test_room/close")
        self.assertEqual(res.status_code, 200)
        
        # Verify room is closed
        res = self.client.get("/api/rooms/tf_test_room")
        self.assertEqual(res.json()["is_active"], 0)

if __name__ == "__main__":
    unittest.main()
