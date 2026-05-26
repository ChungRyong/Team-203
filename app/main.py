from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional
import sys
import os
import json
import time
import random
import shutil
import requests

# Ensure the app package is in the import path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import database
from app.database import run_git_snapshot
from app.blinky_middleware import check_and_compress_context
from app.penalties import enforce_penalty_check, get_agent_system_prompt, enforce_pardon_agent
from config.settings import OLLAMA_CHAT_URL

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

class ArtGenerateRequest(BaseModel):
    project_id: str = Field(..., example="game_01_tetris")
    asset_type: str = Field(..., example="UI_WIREFRAME")
    prompt: str = Field(..., example="neon tetris grid board game UI layout")
    seed: Optional[int] = Field(-1, example=-1)

class AuditLogCreate(BaseModel):
    event_type: str = Field(..., example="VRAM_UNLOAD")
    status: str = Field(..., example="SUCCESS")
    details: Optional[dict] = Field(None, example={"model": "qwen3.6:35b-mlx"})
    elapsed_ms: Optional[int] = Field(None, example=120)

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, example="테트리스 게임 기본 개발 수정")
    description: Optional[str] = Field(None, example="Godot 4.2+ 엔진을 이용한 정교한 물리 연동")
    status: Optional[str] = Field(None, example="PASSED_WITHOUT_CLAUDE")

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

@app.patch("/api/tasks/{task_id}", response_model=TaskResponse)
def update_task_endpoint(task_id: str, task_up: TaskUpdate):
    existing = database.get_task(task_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Task not found.")
        
    try:
        # If status is updated, use the standard update helper
        if task_up.status is not None:
            database.update_task_status(task_id, task_up.status)
            
        # Update other fields using SQLite connection directly to keep it extremely simple and isolated
        conn = database.get_db_connection()
        try:
            if task_up.title is not None:
                conn.execute("UPDATE tasks SET title = ?, updated_at = CURRENT_TIMESTAMP WHERE task_id = ?", (task_up.title, task_id))
            if task_up.description is not None:
                conn.execute("UPDATE tasks SET description = ?, updated_at = CURRENT_TIMESTAMP WHERE task_id = ?", (task_up.description, task_id))
            conn.commit()
        finally:
            conn.close()
            
        updated = database.get_task(task_id)
        return updated
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
        # Hermes represents 'user' (initiating commands/planning), while other specialists act as 'assistant'
        role = "user" if msg["sender_role"] == "Hermes" else "assistant"
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
        
    import time
    start_time = time.perf_counter()
    
    database.close_room(room_id)
    
    # Archive all active messages from the closed room
    database.archive_room_messages(room_id)
    
    # Trigger background Git snapshot backup
    git_start = time.perf_counter()
    git_success = run_git_snapshot(room_id, "closed")
    git_elapsed = int((time.perf_counter() - git_start) * 1000)
    
    # Record Git snapshot to audit logs
    database.add_audit_log(
        event_type="GIT_SNAPSHOT",
        status="SUCCESS" if git_success else "FAILED",
        details={"room_id": room_id, "action": "close_meeting_room"},
        elapsed_ms=git_elapsed
    )
    
    # Post system shutdown announcement
    database.add_message(
        room_id, 
        "System", 
        "🚪 [시스템 안내] 수석PM(Hermes)의 지시로 회의가 성공적으로 승인 종료되었으며 회의실 세션이 영구 폐쇄되었습니다.", 
        "TEXT"
    )
    
    total_elapsed = int((time.perf_counter() - start_time) * 1000)
    # Record Session close to audit logs
    database.add_audit_log(
        event_type="SESSION_COMPRESS",
        status="SUCCESS",
        details={"room_id": room_id, "action": "close_and_archive"},
        elapsed_ms=total_elapsed
    )
    return {
        "status": "success", 
        "message": f"Room {room_id} closed/destructed successfully.",
        "git_snapshot_status": "SUCCESS" if git_success else "FAILED"
    }

@app.post("/api/vram/unload")
def unload_vram(req: VramUnloadRequest):
    """
    Instructs the local Ollama instance to unload a model from memory (VRAM).
    Sends a POST request to Ollama's API with keep_alive set to 0.
    """
    import requests
    ollama_chat_url = OLLAMA_CHAT_URL
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

@app.post("/api/agents/{agent_name}/pardon")
def pardon_agent(agent_name: str):
    existing = database.get_agent_penalty(agent_name)
    if not existing:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not registered in penalty profiles.")
        
    try:
        res = enforce_pardon_agent(agent_name)
        return {"status": "success", "penalty_status": res}
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

@app.post("/api/art/generate")
def generate_art(req: ArtGenerateRequest):
    # 1. Base directory and target path
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    target_dir = os.path.join(base_dir, "workspace", "projects", req.project_id, "art")
    os.makedirs(target_dir, exist_ok=True)
    
    # 2. Determine target filename based on index
    index = 1
    import glob
    existing = glob.glob(os.path.join(target_dir, f"{req.asset_type.lower()}_*.png"))
    if existing:
        index = len(existing) + 1
    target_filename = f"{req.asset_type.lower()}_{index:02d}.png"
    target_filepath = os.path.join(target_dir, target_filename)
    
    # 3. Resolve seed
    seed_val = req.seed
    if seed_val == -1:
        seed_val = random.randint(1, 2147483647)
        
    # 4. Load ComfyUI workflow template
    workflow_path = os.path.join(base_dir, "config", "comfyui_workflow_flux.json")
    workflow_data = {}
    if os.path.exists(workflow_path):
        try:
            with open(workflow_path, "r", encoding="utf-8") as f:
                workflow_str = f.read()
                workflow_str = workflow_str.replace("{{POSITIVE_PROMPT}}", req.prompt)
                workflow_data = json.loads(workflow_str)
                if "3" in workflow_data and "inputs" in workflow_data["3"]:
                    workflow_data["3"]["inputs"]["seed"] = seed_val
        except Exception:
            pass
            
    is_fallback = False
    fallback_reason = ""
    
    # 5. Attempt ComfyUI API communication (Fail-Safe wrapper)
    comfyui_url = "http://localhost:8188"
    try:
        prompt_res = requests.post(f"{comfyui_url}/prompt", json={"prompt": workflow_data}, timeout=5)
        if prompt_res.status_code == 200:
            prompt_id = prompt_res.json().get("prompt_id")
            
            completed = False
            for _ in range(5):
                time.sleep(2)
                history_res = requests.get(f"{comfyui_url}/history/{prompt_id}", timeout=5)
                if history_res.status_code == 200 and history_res.json():
                    history_data = history_res.json().get(prompt_id, {})
                    outputs = history_data.get("outputs", {})
                    for node_id, node_out in outputs.items():
                        if "images" in node_out:
                            for img in node_out["images"]:
                                filename = img.get("filename")
                                comfy_output_dir = os.path.join(os.path.dirname(base_dir), "ComfyUI", "output")
                                if not os.path.exists(comfy_output_dir):
                                    comfy_output_dir = os.path.join(base_dir, "ComfyUI", "output")
                                if not os.path.exists(comfy_output_dir):
                                    comfy_output_dir = "output"
                                src_path = os.path.join(comfy_output_dir, filename)
                                if os.path.exists(src_path):
                                    shutil.copy(src_path, target_filepath)
                                    completed = True
                                    break
                    if completed:
                        break
            if not completed:
                is_fallback = True
                fallback_reason = "ComfyUI prompt completed but output image could not be resolved from output folder."
        else:
            is_fallback = True
            fallback_reason = f"ComfyUI prompt API returned error status: {prompt_res.status_code}"
    except Exception as e:
        is_fallback = True
        fallback_reason = f"ComfyUI offline or connection failed: {e}"
        
    # 6. Apply Fail-Safe Placeholder copy if fallback is active
    if is_fallback:
        tiny_png_bin = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\rIDATx\x9cc`\x00\x01\x00\x00\x0c\x00\x01\x07\xcd\xf3\xb0\x00\x00\x00\x00IEND\xaeB`\x82'
        try:
            with open(target_filepath, "wb") as f:
                f.write(tiny_png_bin)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to write mock image: {e}")
            
    # 7. Write/Update metadata.json
    metadata_path = os.path.join(target_dir, "metadata.json")
    metadata = {"assets": []}
    if os.path.exists(metadata_path):
        try:
            with open(metadata_path, "r", encoding="utf-8") as f:
                metadata = json.load(f)
        except Exception:
            pass
            
    asset_entry = {
        "filename": target_filename,
        "asset_type": req.asset_type,
        "prompt": req.prompt,
        "seed": seed_val,
        "sampler": "euler",
        "scheduler": "normal",
        "steps": 20,
        "is_fallback": is_fallback,
        "fallback_reason": fallback_reason if is_fallback else None,
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }
    metadata["assets"].append(asset_entry)
    
    try:
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update metadata.json: {e}")
        
    if is_fallback:
        return {
            "status": "warning",
            "filename": target_filename,
            "filepath": target_filepath,
            "message": f"ComfyUI offline ({fallback_reason}). Bypassed with tiny PNG mockup.",
            "metadata": asset_entry
        }
    else:
        return {
            "status": "success",
            "filename": target_filename,
            "filepath": target_filepath,
            "message": "Art asset generated and saved successfully via ComfyUI.",
            "metadata": asset_entry
        }

@app.post("/api/audit/log", status_code=status.HTTP_201_CREATED)
def post_audit_log(log: AuditLogCreate):
    try:
        database.add_audit_log(log.event_type, log.status, log.details, log.elapsed_ms)
        return {"status": "success", "message": "Audit log added successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/audit/summary")
def get_audit_summary():
    try:
        res = database.get_audit_summary()
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
