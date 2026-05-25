import requests
import os

DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL", "")

def send_discord_log(content, title="🚨 [Blinky System Log]", color=16711680):
    """
    Sends a beautifully structured system log directly to the Discord channel using a direct webhook.
    Completely bypasses n8n, eliminating third-party local dependencies.
    """
    if not DISCORD_WEBHOOK_URL:
        # Fallback gracefully if webhook URL is not configured
        print(f"📡 [Discord Relay - Fallback Log] {title}: {content}")
        return False
        
    payload = {
        "embeds": [
            {
                "title": title,
                "description": content,
                "color": color, # default is Red
                "footer": {
                    "text": "Team-203 로컬 가상 사옥 관제망"
                }
            }
        ]
    }
    
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
        if response.status_code == 204:
            print("✅ [Discord Relay] Log successfully relayed to Discord.")
            return True
        else:
            print(f"⚠️ [Discord Relay] Discord API returned status: {response.status_code}")
            return False
    except Exception as e:
        print(f"⚠️ [Discord Relay] Direct HTTP webhook connection failed: {e}")
        return False
