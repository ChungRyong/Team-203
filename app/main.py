from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional
import sys
import os

# Ensure the app package is in the import path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import database
from app.database import run_git_snapshot
from app.blinky_middleware import check_and_compress_context
from app.penalties import enforce_penalty_check, get_agent_system_prompt

app = FastAPI(
    title="Team-203 Virtual Office Meeting Room Engine",
    description="FastAPI + SQLite Lightweight Dialogue Server with Blinky Context Compression Middleware",
    version="1.0.0"
)

# --- PYDANTIC SCHEMAS ---

class TaskCreate(BaseModel):
    task_id: str = Field(..., example="TASK-20260525-01")
    title: str = Field(..., example="테트리스 게임 기본 개발")
    description: Optional[str] = Field(None, example="Godot 4.2+ 엔진을 이용한 테트리스 웹 게임 프로토타입 작성")
    status: Optional[str] = Field("PENDING", example="PENDING")

class RoomCreate(BaseModel):
    room_id: str = Field(..., example="tf_concept_dev_01")
    room_name: str = Field(..., example="기획-개발 협업 TF룸")
    task_id: str = Field(..., example="TASK-20260525-01")
    allowed_agents: List[str] = Field(..., example=["Concept-Agent", "Dev-Agent"])

class MessageCreate(BaseModel):
    sender_role: str = Field(..., example="Dev-Agent")
    content: str = Field(..., example="테트리스 블록 강하 로직 구현 완료했습니다.")
    payload_type: Optional[str] = Field("TEXT", example="TEXT")

class PenalizeRequest(BaseModel):
    reason: str = Field(..., example="가상 함수 날조 및 린트 검증 실패")
    
class PromptRequest(BaseModel):
    base_prompt: str = Field(..., example="당신은 수석 엔지니어입니다. 코드를 구현해 주세요.")

class VramUnloadRequest(BaseModel):
    model: str = Field(..., example="qwen3.6:35b-mlx")

class TaskResponse(BaseModel):
    task_id: str
    title: str
    description: Optional[str]
    status: str
    created_at: str
    updated_at: str

class RoomResponse(BaseModel):
    room_id: str
    room_name: str
    task_id: Optional[str]
    allowed_agents: List[str]
    turn_count: int
    is_active: int
    created_at: str

class MessageResponse(BaseModel):
    message_id: int
    room_id: str
    sender_role: str
    content: str
    payload_type: str
    is_archived: int
    created_at: str

# --- API ENDPOINTS ---

@app.on_event("startup")
def startup_event():
    # Double check tables are initialized
    database.create_tables()

@app.post("/api/tasks", status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate):
    existing = database.get_task(task.task_id)
    if existing:
        raise HTTPException(status_code=400, detail="Task with this ID already exists.")
    try:
        database.add_task(task.task_id, task.title, task.description, task.status)
        return {"status": "success", "message": f"Task {task.task_id} registered successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: str):
    res = database.get_task(task_id)
    if not res:
        raise HTTPException(status_code=404, detail="Task not found.")
    return res

@app.post("/api/rooms", status_code=status.HTTP_201_CREATED)
def create_room(room: RoomCreate):
    task = database.get_task(room.task_id)
    if not task:
        raise HTTPException(status_code=400, detail=f"Task {room.task_id} does not exist. Please register the task first.")
        
    try:
        database.add_room(room.room_id, room.room_name, room.task_id, room.allowed_agents)
        return {"status": "success", "message": f"Room {room.room_id} opened successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/rooms/{room_id}", response_model=RoomResponse)
def get_room(room_id: str):
    res = database.get_room(room_id)
    if not res:
        raise HTTPException(status_code=404, detail="Room not found.")
    return res

@app.post("/api/rooms/{room_id}/messages", status_code=status.HTTP_201_CREATED)
def post_message(room_id: str, msg: MessageCreate):
    room = database.get_room(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found.")
    if not room["is_active"]:
        raise HTTPException(status_code=400, detail="This meeting room has been closed/destructed.")
        
    # Security Check: Ensure sender is allowed in this room
    if msg.sender_role not in room["allowed_agents"] and msg.sender_role not in ["System", "Blinky_Observer", "Hermes"]:
        raise HTTPException(
            status_code=403, 
            detail=f"Access Denied: Agent '{msg.sender_role}' is not authorized in this room."
        )
        
    try:
        msg_id = database.add_message(room_id, msg.sender_role, msg.content, msg.payload_type)
        
        # Intercept with Blinky Observer Context Compression Middleware
        check_and_compress_context(room_id)
        
        return {
            "status": "success", 
            "message_id": msg_id, 
            "message": "Message posted successfully."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/rooms/{room_id}/messages", response_model=List[MessageResponse])
def get_messages(room_id: str, include_archived: bool = False):
    room = database.get_room(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found.")
    return database.get_room_messages(room_id, include_archived=include_archived)

@app.get("/api/rooms/{room_id}/context")
def get_room_context(room_id: str):
    """
    Returns compiled messages formatted for LLM conversation history.
    If a SYSTEM_SUMMARY is present, it is served as the foundational baseline context,
    followed by subsequent active messages.
    """
    room = database.get_room(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found.")
        
    messages = database.get_room_messages(room_id, include_archived=False)
    
    formatted_messages = []
    
    # 1. Parse baseline system summary if any
    system_summary = None
    active_msgs = []
    
    for msg in messages:
        if msg["payload_type"] == "SYSTEM_SUMMARY":
            system_summary = msg
        else:
            active_msgs.append(msg)
            
    # Inject baseline system context if summary exists
    if system_summary:
        formatted_messages.append({
            "role": "system",
            "content": (
                f"### [Blinky Baseline Context Summary]\n"
                f"다음은 이전 회의실 세션의 압축 요약입니다. 본 맥락을 이정표로 삼아 대화를 재개해 주세요.\n\n"
                f"{system_summary['content']}"
            )
        })
    else:
        formatted_messages.append({
            "role": "system",
            "content": f"회의실 '{room['room_name']}'에 입장하셨습니다. 프로젝트 태스크를 위해 토론을 시작해 주세요."
        })
        
    # 2. Append subsequent active dialogue
    for msg in active_msgs:
        role = "assistant"
        # Optional: You can map roles if needed, e.g. mapping sender_role to user/assistant.
        # But for LLM multi-agent systems, putting the sender name inside the content is highly standard.
        formatted_messages.append({
            "role": role,
            "content": f"[{msg['sender_role']}]: {msg['content']}"
        })
        
    return {
        "room_id": room_id,
        "room_name": room["room_name"],
        "turn_count": room["turn_count"],
        "is_active": room["is_active"],
        "allowed_agents": room["allowed_agents"],
        "llm_history": formatted_messages
    }

@app.post("/api/rooms/{room_id}/close")
def close_meeting_room(room_id: str):
    room = database.get_room(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found.")
        
    database.close_room(room_id)
    
    # Trigger background Git snapshot backup
    run_git_snapshot(room_id, "closed")
    
    # Post system shutdown announcement
    database.add_message(
        room_id, 
        "System", 
        "🚪 [시스템 안내] 수석PM(Hermes)의 지시로 회의가 성공적으로 승인 종료되었으며 회의실 세션이 영구 폐쇄되었습니다.", 
        "TEXT"
    )
    return {"status": "success", "message": f"Room {room_id} closed/destructed successfully."}

@app.post("/api/vram/unload")
def unload_vram(req: VramUnloadRequest):
    """
    Instructs the local Ollama instance to unload a model from memory (VRAM).
    Sends a POST request to Ollama's API with keep_alive set to 0.
    """
    import requests
    ollama_chat_url = "http://localhost:11434/api/chat"
    payload = {
        "model": req.model,
        "messages": [],
        "keep_alive": 0
    }
    
    try:
        # Send keep_alive = 0 to Ollama API to force release
        # Short timeout to avoid blocking if Ollama is unresponsive
        res = requests.post(ollama_chat_url, json=payload, timeout=5)
        return {
            "status": "success",
            "model": req.model,
            "message": f"Successfully requested Ollama to unload model '{req.model}'.",
            "ollama_status_code": res.status_code
        }
    except Exception as e:
        # Return success with fallback/warning message so it remains robust (Fail-Safe)
        return {
            "status": "warning",
            "model": req.model,
            "message": f"Ollama connection bypassed or offline. Model '{req.model}' unload requested.",
            "error_detail": str(e)
        }

@app.post("/api/agents/{agent_name}/penalize")
def penalize_agent(agent_name: str, req: PenalizeRequest):
    existing = database.get_agent_penalty(agent_name)
    if not existing:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not registered in penalty profiles.")
        
    try:
        res = enforce_penalty_check(agent_name, req.reason)
        return {"status": "success", "penalty_status": res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/agents/{agent_name}/prompt")
def get_agent_prompt(agent_name: str, req: PromptRequest):
    existing = database.get_agent_penalty(agent_name)
    if not existing:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not registered in penalty profiles.")
        
    try:
        res = get_agent_system_prompt(agent_name, req.base_prompt)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class CtoReviewConfigRequest(BaseModel):
    enabled: bool = Field(..., example=False)

@app.get("/api/config/cto-review")
def get_cto_review_config():
    """
    Returns the current ON/OFF state of the dynamic Claude CTO code review system.
    """
    val = database.get_system_setting("cto_review_enabled", "0")
    return {
        "cto_review_enabled": True if val == "1" else False
    }

@app.post("/api/config/cto-review")
def update_cto_review_config(req: CtoReviewConfigRequest):
    """
    Allows Hermes (or the CEO) to dynamically toggle the Claude CTO code review system.
    1: ON (Enabled), 0: OFF (Disabled)
    """
    val_str = "1" if req.enabled else "0"
    database.update_system_setting("cto_review_enabled", val_str)
    return {
        "status": "success",
        "cto_review_enabled": req.enabled,
        "message": f"CTO dynamic code review has been successfully turned {'ON' if req.enabled else 'OFF'}."
    }
