import os
import sys

# Central Configuration Loader for Team-203
# Bypasses third-party 'python-dotenv' dependency by reading .env file using pure python.

# 1. Base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 2. Pure Python .env file parser
env_data = {}
env_path = os.path.join(BASE_DIR, ".env")
if os.path.exists(env_path):
    try:
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()
                # Skip comments and blank lines
                if not stripped or stripped.startswith("#"):
                    continue
                if "=" in stripped:
                    key, val = stripped.split("=", 1)
                    env_data[key.strip()] = val.strip()
    except Exception as e:
        print(f"⚠️ [Config Alert] Could not parse .env file: {e}")

# 3. Load configurations (with env variables prioritizing over .env file, then falling back to defaults)
def get_config(key, default):
    return os.environ.get(key) or env_data.get(key) or default

# Core Config Values
PORT = int(get_config("TEAM203_PORT", "8000"))
OLLAMA_API_URL = get_config("OLLAMA_API_URL", "http://localhost:11434")
DISCORD_WEBHOOK_URL = get_config("DISCORD_WEBHOOK_URL", "")

# Derived Endpoint URLs
OLLAMA_GENERATE_URL = f"{OLLAMA_API_URL.rstrip('/')}/api/generate"
OLLAMA_CHAT_URL = f"{OLLAMA_API_URL.rstrip('/')}/api/chat"
