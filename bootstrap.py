import sys
import os
import subprocess

# Append the current directory so Python can import the 'app' module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import create_tables, seed_agent_penalties, DB_PATH, update_system_setting

def get_keychain_secret(service):
    try:
        # Run macOS security CLI to retrieve credentials safely from Keychain
        cmd = f'security find-generic-password -a "Team203" -s "{service}" -w'
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
        if res.returncode == 0:
            return res.stdout.strip()
    except Exception:
        pass
    return None

def resolve_keychain_secrets():
    print("🔑 [Keychain Resolver] Syncing credentials from macOS Keychain...")
    discord_url = get_keychain_secret("Discord_Webhook_URL")
    hf_token = get_keychain_secret("HF_TOKEN")
    
    if not discord_url and not hf_token:
        print("⚠️ [Keychain Resolver] No Generic Password found in Keychain for account 'Team203'. Bypassing or using existing .env.")
        return
        
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    env_example_path = env_path + ".example"
    
    lines = []
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    elif os.path.exists(env_example_path):
        with open(env_example_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    else:
        lines = [
            "PORT=8000\n",
            "OLLAMA_CHAT_URL=http://localhost:11434/api/chat\n",
            "DISCORD_WEBHOOK_URL=\n",
            "HF_TOKEN=\n"
        ]
        
    updated_lines = []
    for line in lines:
        if line.startswith("DISCORD_WEBHOOK_URL=") and discord_url:
            updated_lines.append(f"DISCORD_WEBHOOK_URL={discord_url}\n")
            print("  🔒 Loaded Discord Webhook URL from Keychain.")
        elif line.startswith("HF_TOKEN=") and hf_token:
            updated_lines.append(f"HF_TOKEN={hf_token}\n")
            print("  🔒 Loaded HuggingFace Token from Keychain.")
        else:
            updated_lines.append(line)
            
    with open(env_path, "w", encoding="utf-8") as f:
        f.writelines(updated_lines)
    print("✅ [Keychain Resolver] .env file successfully created/updated with Keychain credentials.")

def bootstrap():
    print("🚀 [Team-203 Bootstrap] Initializing Virtual Office Infrastructure...")
    
    # 0. Resolve keychain credentials and dynamically generate/merge .env file
    resolve_keychain_secrets()
    
    # 1. Create tables
    print(f"🔌 Creating database tables in SQLite db path: {DB_PATH}")
    try:
        create_tables()
        print("✅ Database tables created successfully.")
    except Exception as e:
        print(f"❌ Failed to create database tables: {e}")
        sys.exit(1)
        
    # 2. Seed initial agent penalty records
    core_agents = ["Hermes", "Concept-Agent", "Art-Agent", "Dev-Agent", "Blinky"]
    print(f"👥 Seeding core agents penalty metadata: {core_agents}")
    try:
        seed_agent_penalties(core_agents)
        print("✅ Core agents seeded successfully with 0 warning stack.")
    except Exception as e:
        print(f"❌ Failed to seed core agents: {e}")
        sys.exit(1)
        
    # 3. Seed initial system settings
    print("⚙️ Seeding initial system configuration settings (cto_review_enabled = '0')...")
    try:
        update_system_setting("cto_review_enabled", "0") # Default is OFF (disabled)
        print("✅ System configuration seeded successfully (CTO Review is OFF by default).")
    except Exception as e:
        print(f"❌ Failed to seed system configuration: {e}")
        sys.exit(1)
        
    # 4. Create local Monorepo project folders physically
    print("📁 Initializing physical Monorepo workspace projects directory tree...")
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        projects_dir = os.path.join(base_dir, "workspace", "projects")
        
        # Create game_01_tetris sandbox directories
        tetris_dir = os.path.join(projects_dir, "game_01_tetris")
        for sub in ["concept", "art", "dev"]:
            path = os.path.join(tetris_dir, sub)
            os.makedirs(path, exist_ok=True)
            
        print(f"✅ Created physical directories: {tetris_dir}/(concept, art, dev)")
    except Exception as e:
        print(f"❌ Failed to build physical directory tree: {e}")
        sys.exit(1)
        
    print("\n🎉 [Team-203 Bootstrap] Setup finished successfully! DB is ready to serve.")

if __name__ == "__main__":
    bootstrap()
