import sqlite3
import os
import json

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "hermes_soul.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    # WAL Mode for high concurrency
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA busy_timeout=5000;")
    return conn

def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. tasks Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        task_id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT,
        status TEXT DEFAULT 'PENDING' CHECK(status IN ('PENDING', 'IN_PROGRESS', 'COMPLETED', 'PASSED_WITHOUT_CLAUDE')),
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)
    
    # 2. rooms Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS rooms (
        room_id TEXT PRIMARY KEY,
        room_name TEXT NOT NULL,
        task_id TEXT,
        allowed_agents TEXT NOT NULL, -- JSON string array, e.g. '["Concept-Agent", "Dev-Agent"]'
        turn_count INTEGER DEFAULT 0,
        is_active INTEGER DEFAULT 1, -- 1: active, 0: closed/destructed
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (task_id) REFERENCES tasks (task_id)
    );
    """)
    
    # 3. messages Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        message_id INTEGER PRIMARY KEY AUTOINCREMENT,
        room_id TEXT NOT NULL,
        sender_role TEXT NOT NULL,
        content TEXT NOT NULL,
        payload_type TEXT DEFAULT 'TEXT' CHECK(payload_type IN ('TEXT', 'CODE', 'JSON_SPEC', 'IMAGE_PATH', 'JSON_VALIDATED', 'SYSTEM_SUMMARY')),
        is_archived INTEGER DEFAULT 0, -- 1: archived by Blinky context compression, 0: active
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (room_id) REFERENCES rooms (room_id)
    );
    """)
    
    # 4. agent_penalties Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS agent_penalties (
        agent_name TEXT PRIMARY KEY,
        warning_count INTEGER DEFAULT 0,
        is_penalized INTEGER DEFAULT 0, -- 1: penalized (Temp 0.0), 0: normal
        last_penalty_reason TEXT,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)
    
    # 5. system_settings Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS system_settings (
        setting_key TEXT PRIMARY KEY,
        setting_value TEXT NOT NULL
    );
    """)
    
    conn.commit()
    conn.close()

# --- CRUD HELPER FUNCTIONS ---

def add_task(task_id, title, description="", status="PENDING"):
    conn = get_db_connection()
    try:
        conn.execute(
            "INSERT INTO tasks (task_id, title, description, status) VALUES (?, ?, ?, ?)",
            (task_id, title, description, status)
        )
        conn.commit()
    finally:
        conn.close()

def get_task(task_id):
    conn = get_db_connection()
    try:
        row = conn.execute("SELECT * FROM tasks WHERE task_id = ?", (task_id,)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()

def update_task_status(task_id, status):
    conn = get_db_connection()
    try:
        conn.execute(
            "UPDATE tasks SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE task_id = ?",
            (status, task_id)
        )
        conn.commit()
    finally:
        conn.close()

def add_room(room_id, room_name, task_id, allowed_agents):
    conn = get_db_connection()
    try:
        agents_str = json.dumps(allowed_agents)
        conn.execute(
            "INSERT OR REPLACE INTO rooms (room_id, room_name, task_id, allowed_agents, turn_count, is_active) VALUES (?, ?, ?, ?, 0, 1)",
            (room_id, room_name, task_id, agents_str)
        )
        conn.commit()
    finally:
        conn.close()

def get_room(room_id):
    conn = get_db_connection()
    try:
        row = conn.execute("SELECT * FROM rooms WHERE room_id = ?", (room_id,)).fetchone()
        if row:
            res = dict(row)
            res['allowed_agents'] = json.loads(res['allowed_agents'])
            return res
        return None
    finally:
        conn.close()

def update_room_turn_count(room_id, turn_count):
    conn = get_db_connection()
    try:
        conn.execute("UPDATE rooms SET turn_count = ? WHERE room_id = ?", (turn_count, room_id))
        conn.commit()
    finally:
        conn.close()

def close_room(room_id):
    conn = get_db_connection()
    try:
        conn.execute("UPDATE rooms SET is_active = 0 WHERE room_id = ?", (room_id,))
        conn.commit()
    finally:
        conn.close()

def add_message(room_id, sender_role, content, payload_type="TEXT"):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO messages (room_id, sender_role, content, payload_type, is_archived) VALUES (?, ?, ?, ?, 0)",
            (room_id, sender_role, content, payload_type)
        )
        
        # Automatically increment room turn count for non-system messages
        if sender_role != "System" and sender_role != "Blinky_Observer":
            cursor.execute("UPDATE rooms SET turn_count = turn_count + 1 WHERE room_id = ?", (room_id,))
            
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()

def get_room_messages(room_id, include_archived=False):
    conn = get_db_connection()
    try:
        if include_archived:
            rows = conn.execute(
                "SELECT * FROM messages WHERE room_id = ? ORDER BY created_at ASC",
                (room_id,)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM messages WHERE room_id = ? AND is_archived = 0 ORDER BY created_at ASC",
                (room_id,)
            ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()

def archive_room_messages(room_id):
    conn = get_db_connection()
    try:
        conn.execute("UPDATE messages SET is_archived = 1 WHERE room_id = ?", (room_id,))
        conn.commit()
    finally:
        conn.close()

def seed_agent_penalties(agents):
    conn = get_db_connection()
    try:
        for agent in agents:
            conn.execute(
                "INSERT OR IGNORE INTO agent_penalties (agent_name, warning_count, is_penalized) VALUES (?, 0, 0)",
                (agent,)
            )
        conn.commit()
    finally:
        conn.close()

def get_agent_penalty(agent_name):
    conn = get_db_connection()
    try:
        row = conn.execute("SELECT * FROM agent_penalties WHERE agent_name = ?", (agent_name,)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()

def increment_agent_warning(agent_name, reason):
    conn = get_db_connection()
    try:
        row = conn.execute("SELECT warning_count FROM agent_penalties WHERE agent_name = ?", (agent_name,)).fetchone()
        if row:
            new_warnings = row['warning_count'] + 1
            is_penalized = 1 if new_warnings >= 3 else 0
            conn.execute(
                "UPDATE agent_penalties SET warning_count = ?, is_penalized = ?, last_penalty_reason = ?, updated_at = CURRENT_TIMESTAMP WHERE agent_name = ?",
                (new_warnings, is_penalized, reason, agent_name)
            )
            conn.commit()
            return {"warning_count": new_warnings, "is_penalized": is_penalized}
        return None
    finally:
        conn.close()

def run_git_snapshot(room_id: str, action_type: str):
    """
    Executes an automated background Git snapshot.
    Runs 'git add .' and 'git commit -m' to capture intermediate or final state.
    Gracefully bypasses any Git error (e.g. nothing to commit or lock issues) without blocking.
    """
    try:
        import subprocess
        # Determine working directory to be the workspace root
        cwd = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # 1. git add .
        subprocess.run(["git", "add", "."], cwd=cwd, check=True, capture_output=True)
        
        # 2. git commit -m
        commit_msg = f"Auto-backup TF-Room [{room_id}] checkpoint ({action_type})"
        res = subprocess.run(["git", "commit", "-m", commit_msg], cwd=cwd, check=True, capture_output=True)
        
        print(f"📦 [Git Snapshot] Backup successful: {commit_msg}")
        return True
    except subprocess.CalledProcessError as e:
        stderr_msg = e.stderr.decode().strip() if e.stderr else "No stderr"
        # Often occurs when there is nothing to commit, which is a success from our pipeline perspective.
        print(f"📡 [Git Snapshot Info] Bypassed: {stderr_msg}")
        return False
    except Exception as e:
        print(f"🚨 [Git Snapshot Error] Unexpected git error bypassed: {str(e)}")
        return False

def get_system_setting(key: str, default_value: str = "0") -> str:
    """
    Retrieves a configuration value from the SQLite system_settings table.
    """
    conn = get_db_connection()
    try:
        row = conn.execute("SELECT setting_value FROM system_settings WHERE setting_key = ?", (key,)).fetchone()
        return row['setting_value'] if row else default_value
    except Exception as e:
        print(f"⚠️ [DB Warning] Failed to read system setting '{key}': {e}")
        return default_value
    finally:
        conn.close()

def update_system_setting(key: str, value: str):
    """
    Inserts or updates a configuration value in the SQLite system_settings table.
    """
    conn = get_db_connection()
    try:
        conn.execute(
            "INSERT OR REPLACE INTO system_settings (setting_key, setting_value) VALUES (?, ?)",
            (key, str(value))
        )
        conn.commit()
        print(f"⚙️ [DB Config] System setting '{key}' updated to '{value}'.")
    except Exception as e:
        print(f"🚨 [DB Error] Failed to update system setting '{key}': {e}")
    finally:
        conn.close()

def pardon_agent_penalty(agent_name: str) -> bool:
    """
    Resets an agent's warning stack and removes penalty status.
    """
    conn = get_db_connection()
    try:
        conn.execute(
            "UPDATE agent_penalties SET warning_count = 0, is_penalized = 0, last_penalty_reason = NULL, updated_at = CURRENT_TIMESTAMP WHERE agent_name = ?",
            (agent_name,)
        )
        conn.commit()
        print(f"🕊️ [DB Penalty Reset] Agent '{agent_name}' has been pardoned and warning stack reset to 0.")
        return True
    except Exception as e:
        print(f"🚨 [DB Error] Failed to pardon agent '{agent_name}': {e}")
        return False
    finally:
        conn.close()

