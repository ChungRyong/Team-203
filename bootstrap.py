import sys
import os

# Append the current directory so Python can import the 'app' module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import create_tables, seed_agent_penalties, DB_PATH, update_system_setting

def bootstrap():
    print("🚀 [Team-203 Bootstrap] Initializing Virtual Office Infrastructure...")
    
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
        
    print("\n🎉 [Team-203 Bootstrap] Setup finished successfully! DB is ready to serve.")

if __name__ == "__main__":
    bootstrap()
