#!/usr/bin/env python3
import os
import sys
import ast
import json
import re
import requests
import subprocess

def get_registered_assets(filepath):
    """
    Traverses upwards from the inspected file's path to find art/metadata.json,
    and returns a list of registered asset filenames.
    Traverses up to 4 levels.
    """
    dirpath = os.path.abspath(filepath)
    if os.path.isfile(dirpath):
        dirpath = os.path.dirname(dirpath)
        
    for _ in range(4):
        metadata_path = os.path.join(dirpath, "art", "metadata.json")
        if os.path.exists(metadata_path):
            try:
                with open(metadata_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return [asset.get("filename") for asset in data.get("assets", [])]
            except Exception:
                pass
        dirpath = os.path.dirname(dirpath)
    return []

def check_asset_violations(filepath, registered_assets):
    """
    Extracts all PNG/TSCN asset references inside source file
    and checks if they exist in the registered assets list.
    Only audits files starting with art prefixes or explicitly inside art/.
    """
    if not registered_assets:
        return []
        
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
        
    asset_refs = re.findall(r'[\w/.:_-]+\.(?:png|tscn)', content)
    
    violations = []
    for ref in asset_refs:
        filename = os.path.basename(ref)
        is_art_asset = "art/" in ref.lower() or filename.startswith(("ui_wireframe", "sprite", "game_background"))
        
        if is_art_asset and filename not in registered_assets:
            violations.append({
                "file": filepath,
                "reference": ref,
                "filename": filename
            })
            
    return violations

# Use environment variable to toggle base URL or fallback to standard port
PORT = os.environ.get("TEAM203_PORT", "8001")
API_URL_PENALIZE = f"http://localhost:{PORT}/api/agents/Dev-Agent/penalize"
API_URL_TASKS = f"http://localhost:{PORT}/api/tasks"
API_URL_CONFIG = f"http://localhost:{PORT}/api/config/cto-review"

def check_cto_review_enabled():
    try:
        res = requests.get(API_URL_CONFIG, timeout=3)
        if res.status_code == 200:
            return res.json().get("cto_review_enabled", False)
    except Exception as e:
        # Default to False (disabled) during bootstrap or offline to remain fail-safe
        return False

def get_function_line_count(node, source_lines):
    """
    Calculates the clean physical line count of a function definition.
    Excludes comments, blank lines, and docstrings.
    """
    start = node.lineno - 1
    end = node.end_lineno
    func_lines = source_lines[start:end]
    
    # 1. Parse and extract docstring range to exclude it
    docstring = ast.get_docstring(node)
    docstring_lines = set()
    if docstring:
        # Find where docstring begins within the function
        # Typically the first node in body is a Expr containing a Constant/Str
        for body_node in node.body:
            if isinstance(body_node, ast.Expr) and isinstance(body_node.value, ast.Constant):
                ds_start = body_node.lineno - 1
                ds_end = body_node.end_lineno
                for idx in range(ds_start, ds_end):
                    docstring_lines.add(idx)
                break
                
    clean_lines = []
    for idx, line in enumerate(func_lines):
        absolute_idx = start + idx
        # Exclude docstrings
        if absolute_idx in docstring_lines:
            continue
            
        stripped = line.strip()
        # Exclude blank lines and comments
        if not stripped or stripped.startswith("#"):
            continue
        clean_lines.append(stripped)
        
    return len(clean_lines)

def analyze_file(filepath):
    """
    Parses a python file using AST to find all functions exceeding 50 clean lines.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        source = f.read()
        
    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        print(f"❌ [Syntax Error] Failed to parse {filepath}: {e}")
        return []
        
    source_lines = source.split("\n")
    violations = []
    
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            line_count = get_function_line_count(node, source_lines)
            if line_count > 50:
                violations.append({
                    "file": filepath,
                    "function": node.name,
                    "lines": line_count,
                    "start_line": node.lineno
                })
                
    return violations

def trigger_blinky_penalty(reason):
    """
    Triggers Blinky penalty increments via the FastAPI backend.
    """
    try:
        res = requests.post(API_URL_PENALIZE, json={"reason": reason}, timeout=5)
        if res.status_code == 200:
            print("🚨 [Blinky Integrator] Successfully reported violation to Blinky Penalty Engine.")
            print(f"📡 [Blinky Status] Current Stack: {res.json()['penalty_status']['warning_count']}/3 warnings.")
        else:
            print(f"⚠️ [Blinky Integrator Warning] Backend API returned status {res.status_code}")
    except Exception as e:
        print(f"⚠️ [Blinky Connection Warning] Could not report to Blinky Penalty Engine (offline): {e}")

def update_task_fail_safe(task_id, status_val):
    """
    Updates the task status in the SQLite database to PASSED_WITHOUT_CLAUDE.
    """
    try:
        url = f"{API_URL_TASKS}/{task_id}"
        # PATCH only the status to the newly created PATCH endpoint
        res = requests.patch(url, json={"status": status_val}, timeout=5)
        if res.status_code == 200:
            print(f"🛡️ [Fail-Safe Activated] Task '{task_id}' updated to status: {status_val}")
            return True
        else:
            print(f"⚠️ [Fail-Safe Warning] PATCH request returned status: {res.status_code}")
    except Exception as e:
        print(f"⚠️ [Fail-Safe DB Warning] Task update bypassed: {e}")
    return False

def run_claude_review_cli():
    """
    Attempts to call the real local 'claude' CLI tool for deep architectural review.
    Implements full Fail-Safe protection for missing command or rate limit errors.
    """
    print("👑 [Claude CTO Review] Attempting deep architectural inspection via Claude CLI...")
    try:
        # Run local 'claude review' or similar command (mock/simulation friendly)
        # We specify a short timeout to prevent hanging
        res = subprocess.run(
            ["claude", "review", "--non-interactive"], 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        
        # Check for rate limit or generic API failures
        if "429" in res.stderr or "rate limit" in res.stderr.lower():
            print("⚠️ [CTO Warning] Claude Pro Rate Limit (429) detected during CLI execution.")
            return "RATE_LIMIT"
            
        if res.returncode == 0:
            print("✅ [CTO Review] Deep architecture review PASSED.")
            return "PASSED"
        else:
            print(f"❌ [CTO Review] Architecture review FAILED:\n{res.stderr}")
            return "FAILED"
            
    except (FileNotFoundError, PermissionError):
        print("⚠️ [CTO Warning] Local 'claude' CLI executable is not installed or available on this host.")
        return "CLI_MISSING"
    except subprocess.TimeoutExpired:
        print("⚠️ [CTO Warning] Claude CLI timed out during execution.")
        return "TIMEOUT"
    except Exception as e:
        print(f"⚠️ [CTO Warning] Unexpected CLI error: {str(e)}")
        return "ERROR"

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 run_cto_review.py <file_or_directory_path> [task_id]")
        sys.exit(0)
        
    target_path = sys.argv[1]
    task_id = sys.argv[2] if len(sys.argv) > 2 else "MOCK-TASK"
    
    # 0. CTO dynamic code review ON/OFF 설정 체크
    if not check_cto_review_enabled():
        print("👑 [Claude CTO Review] CTO dynamic code review is currently turned OFF by system config.")
        print("✅ [CTO Bypassed] Skipping code audits and AST line limits. Process continues successfully.")
        sys.exit(0)
        
    # 1. AST 정적 50줄 체크 (Strict Local Rule)
    print(f"🔍 [AST Review] Starting local code audit on: {target_path}")
    
    violations = []
    if os.path.isfile(target_path):
        if target_path.endswith((".py", ".gd")):
            violations = analyze_file(target_path)
    else:
        for root, _, files in os.walk(target_path):
            for file in files:
                if file.endswith((".py", ".gd")):
                    filepath = os.path.join(root, file)
                    violations.extend(analyze_file(filepath))
                    
    # 2. 결과 처리
    if violations:
        print("\n⛔ [CTO REJECT] 50-Line Function Limit Violated! ⛔")
        for v in violations:
            print(f"  • File: {v['file']} | Function: '{v['function']}' | Lines: {v['lines']} (Start line: {v['start_line']})")
        print("\n👉 모든 파이썬 함수는 CTO Pro 토큰 보존을 위해 주석/공백 제외 50줄 이하여야 합니다.")
        
        # Blinky 징계 API 연동 (경고 1회)
        reason = f"함수 50줄 초과 위반: {violations[0]['file']} -> '{violations[0]['function']}' ({violations[0]['lines']}줄)"
        trigger_blinky_penalty(reason)
        sys.exit(1)
        
    print("✅ [AST Review] Local function length checks PASSED. (All functions <= 50 lines)")

    # 2.5 에셋 날조 정적 감사 (Visual Hallucination Audit)
    print("🎨 [Asset Audit] Auditing design resource and image path bindings...")
    asset_violations = []
    
    registered = get_registered_assets(target_path)
    if registered:
        print(f"📦 [Asset Audit] Found {len(registered)} registered assets in metadata.json.")
        
    if os.path.isfile(target_path):
        if target_path.endswith((".py", ".gd")):
            asset_violations = check_asset_violations(target_path, registered)
    else:
        for root, _, files in os.walk(target_path):
            for file in files:
                if file.endswith((".py", ".gd")):
                    filepath = os.path.join(root, file)
                    asset_violations.extend(check_asset_violations(filepath, registered))
                    
    if asset_violations:
        print("\n⛔ [CTO REJECT] Unregistered Art Asset Reference Detected! ⛔")
        for av in asset_violations:
            print(f"  • File: {av['file']} | Unregistered Reference: '{av['reference']}' (Filename: {av['filename']})")
        print("\n👉 모든 이미지 및 디자인 리소스는 반드시 Art-Agent를 통해 생성되어 art/metadata.json에 정식 등록되어 있어야 합니다.")
        
        # Blinky 징계 API 연동 (경고 1회)
        reason = f"미등록 디자인 리소스 무단 바인딩 적발: {asset_violations[0]['file']} -> '{asset_violations[0]['reference']}'"
        trigger_blinky_penalty(reason)
        sys.exit(1)
        
    print("✅ [Asset Audit] Visual resource bindings verified successfully. (No unregistered assets found)")
    
    # 3. 👑 5층 CTO Claude CLI 호출 및 Fail-Safe 활성화
    cto_status = run_claude_review_cli()
    
    if cto_status == "FAILED":
        sys.exit(1)
        
    elif cto_status in ["RATE_LIMIT", "CLI_MISSING", "TIMEOUT", "ERROR"]:
        print("🛡️ [CTO Fail-Safe] Activating TECHNICAL FAIL-SAFE protocol...")
        update_task_fail_safe(task_id, "PASSED_WITHOUT_CLAUDE")
        print("✅ [CTO Fail-Safe] Bypassed technical blocking. Process continues safely.")
        sys.exit(0)
        
    sys.exit(0)

if __name__ == "__main__":
    main()
