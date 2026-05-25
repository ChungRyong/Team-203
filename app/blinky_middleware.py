import requests
import json
from app.database import (
    get_room,
    get_room_messages,
    add_message,
    archive_room_messages,
    update_room_turn_count
)

OLLAMA_API_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "gemma4:4b"

def call_blinky_summarizer(transcript_str):
    """
    Call Ollama local Gemma 4B model to summarize the meeting room transcript.
    Includes a highly robust fallback in case Ollama is offline or model is missing.
    """
    system_prompt = (
        "You are Blinky, the efficient IO Operations Assistant of Team-203.\n"
        "Your task is to summarize the following multi-agent conversation transcript of a meeting room.\n"
        "Synthesize the key decisions made, final specifications, codes created, and next steps in a concise 1-page Markdown report.\n"
        "Do not lose critical technical details, code blocks, or DDL schemas!\n"
        "Provide ONLY the final concise Markdown summary without any introductory or conversational text."
    )
    
    prompt = f"{system_prompt}\n\nConversation Transcript:\n---\n{transcript_str}\n---\nMarkdown Summary:"
    
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.3
        }
    }
    
    try:
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=20)
        if response.status_code == 200:
            result = response.json()
            return result.get("response", "").strip()
        else:
            print(f"⚠️ Blinky Ollama API returned error status: {response.status_code}")
    except Exception as e:
        print(f"⚠️ Blinky summarizer connection to Ollama failed: {e}")
        
    # Robust Fallback in case of Ollama offline/failure
    print("🔄 Running automated rule-based fallback summarization...")
    return generate_fallback_summary(transcript_str)

def generate_fallback_summary(transcript_str):
    """
    Rule-based fallback summary when Ollama is unavailable.
    Parses key code blocks and DDL keywords to preserve technical details.
    """
    lines = transcript_str.split("\n")
    code_blocks = []
    in_code = False
    current_code = []
    
    for line in lines:
        if "```" in line:
            if in_code:
                in_code = False
                code_blocks.append("\n".join(current_code))
                current_code = []
            else:
                in_code = True
        elif in_code:
            current_code.append(line)
            
    summary = (
        "### 🔄 Blinky [Automated System Summary - Fallback Mode]\n\n"
        "**[System Alert]** 로컬 Ollama API가 비활성화되어 대화가 시스템 규칙에 의해 자동으로 압축 정리되었습니다.\n\n"
        "#### 📊 대화 통계 및 참여자\n"
        f"- 총 발신 대화 턴 수: 20턴\n"
        "- 요약 시각: 로컬 서버 백그라운드 스케줄러 트리거됨\n\n"
        "#### 💻 세션 보존 기술 데이터 (Code & Schema Blocks)\n"
    )
    
    if code_blocks:
        for idx, block in enumerate(code_blocks, 1):
            summary += f"##### 보존 블록 {idx}:\n```\n{block}\n```\n\n"
    else:
        summary += "- 이번 세션에서는 별도의 코드 블록이 제출되지 않았거나 감지되지 않았습니다.\n\n"
        
    summary += (
        "#### 🎯 주요 진행 맥락\n"
        "- 이전 대화 기록 20턴은 Context Rot 방어를 위해 성공적으로 아카이빙 처리되었습니다.\n"
        "- 본 회의실의 턴 카운트는 0으로 초기화되었으며 새로운 세션을 재개합니다.\n"
    )
    return summary

def check_and_compress_context(room_id):
    """
    Intercepts the turn count of a room.
    Triggers at 18 turns for warning, and 20 turns for background compression.
    """
    room = get_room(room_id)
    if not room or not room["is_active"]:
        return False
        
    turn_count = room["turn_count"]
    
    # 1. Warning trigger at 18 turns
    if turn_count == 18:
        warning_msg = (
            "⚠️ [시스템 알림 - Blinky] 현재 소회의실 대화가 18턴에 도달했습니다.\n"
            "20턴에 도달하는 즉시 Blinky 주임의 자동 백그라운드 압축 필터가 가동되어 대화록이 압축 정리되고 턴수가 0으로 리셋됩니다."
        )
        add_message(room_id, "System", warning_msg, "TEXT")
        print(f"🚨 [Blinky Observer] Room {room_id} hit 18 turns. Warning posted.")
        return True
        
    # 2. Compression trigger at 20 turns
    if turn_count >= 20:
        print(f"⚡ [Blinky Observer] Room {room_id} hit 20 turns. Triggering context compression...")
        
        # Get all current active messages
        messages = get_room_messages(room_id, include_archived=False)
        
        if not messages:
            return False
            
        # Format transcript
        transcript_lines = []
        for msg in messages:
            transcript_lines.append(f"[{msg['sender_role']}]: {msg['content']}")
        transcript_str = "\n".join(transcript_lines)
        
        # Run Blinky Gemma 4B summarizer
        summary_text = call_blinky_summarizer(transcript_str)
        
        # Archive old messages (set is_archived = 1)
        archive_room_messages(room_id)
        
        # Write summary as Blinky_Observer
        add_message(room_id, "Blinky_Observer", summary_text, "SYSTEM_SUMMARY")
        
        # Reset turn_count to 0
        update_room_turn_count(room_id, 0)
        
        # Post success system notification
        success_msg = (
            "🔄 [시스템 안내] 대화 누적량이 20턴에 임계하여 Blinky 주임이 이전 대화 로그를 "
            "성공적으로 요약 압축하고 대화 세션을 리프레시했습니다. 새로운 요약을 이정표 삼아 대화를 계속 재개합니다."
        )
        add_message(room_id, "System", success_msg, "TEXT")
        print(f"✅ [Blinky Observer] Room {room_id} context successfully compressed and reset to 0 turns.")
        return True
        
    return False
