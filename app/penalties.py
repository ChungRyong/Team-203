import sqlite3
from app.database import get_agent_penalty, increment_agent_warning
from app.discord_relay import send_discord_log

PENALTY_PROMPT_PREFIX = (
    "⚠️ [징계 집행 상태 - 절대 팩트 모드 고정]\n"
    "**[경고]** 당신은 3회 연속 린트 검증 실패 또는 기술 요구사항/함수 날조(Hallucination)로 인해 Blinky 주임에 의해 정신개조 징계 처분을 받았습니다.\n"
    "**[행동 제약 지침]**\n"
    "1. 당신의 추론 온도(Temperature)는 0.0으로 강제 절대 고정됩니다.\n"
    "2. 당신은 단 하나의 가상 함수나 명세도 임의로 유추하거나 날조해서 대답해서는 안 되며, 오직 100% 검증된 로컬 팩트와 작동 가능한 무결한 코드만을 제시해야 합니다.\n"
    "3. 모든 코딩은 Linting 에러가 '0'인 상태로만 제출하도록 철저한 검증을 통과해야 합니다.\n\n"
)

def get_agent_system_prompt(agent_name, base_prompt):
    """
    Checks the SQLite database for agent penalties.
    If the agent is penalized (warning_count >= 3), injects a strict penalty prefix,
    and returns temperature = 0.0. Otherwise, returns normal prompt and default temperature.
    """
    penalty = get_agent_penalty(agent_name)
    if penalty and penalty["is_penalized"]:
        # Prepend the penalty prompt
        penalized_prompt = f"{PENALTY_PROMPT_PREFIX}{base_prompt}"
        return {
            "agent_name": agent_name,
            "is_penalized": True,
            "warning_count": penalty["warning_count"],
            "system_prompt": penalized_prompt,
            "recommended_temperature": 0.0
        }
        
    # Return normal prompt and temperature recommendation (0.2 for precise coding, 0.5 for PM/planning)
    default_temp = 0.5 if agent_name in ["Hermes", "Concept-Agent"] else 0.2
    return {
        "agent_name": agent_name,
        "is_penalized": False,
        "warning_count": penalty["warning_count"] if penalty else 0,
        "system_prompt": base_prompt,
        "recommended_temperature": default_temp
    }

def enforce_penalty_check(agent_name, reason):
    """
    Increments agent warning in SQLite.
    If warnings reach 3, triggers 'Three Strikes Out' penalty and posts a direct Discord alert.
    """
    result = increment_agent_warning(agent_name, reason)
    if not result:
        return None
        
    warning_count = result["warning_count"]
    is_penalized = result["is_penalized"]
    
    # 1. Standard Warning Logging
    print(f"🚨 [Blinky Penalty] Agent '{agent_name}' warned. Total Warning Stack: {warning_count}/3. Reason: {reason}")
    
    # 2. Strike Three Out Penalty Enforced!
    if is_penalized:
        discord_content = (
            f"⚠️ **Blinky 주임 긴급 징계 집행 보고** ⚠️\n\n"
            f"부서원 **{agent_name}**이(가) 규정 위반(사유: {reason})으로 인해 경고가 **3회 누적**되어 **삼진 아웃(3진 아웃)**되었습니다.\n\n"
            f"해당 에이전트는 즉시 **정신 개조 징계(is_penalized=1)** 상태로 강제 전환되며, 시스템 프롬프트에 **[절대 팩트 모드 제약 조건]**이 주입되고 추론 온도가 **0.0**으로 영구 강제 고정됩니다."
        )
        send_discord_log(
            content=discord_content,
            title=f"🚨 [징계 집행] {agent_name} 삼진 아웃 징계 개시",
            color=16711680 # Pure Red
        )
        
    return {
        "agent_name": agent_name,
        "warning_count": warning_count,
        "is_penalized": is_penalized,
        "last_penalty_reason": reason
    }
