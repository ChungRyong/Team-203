import os
import subprocess
import shutil
import sys

PRIMARY_WS = "/Users/jabiseu/Documents/obsidian-wiki-vault/projects/Team-203"
SECONDARY_WS = "/Users/jabiseu/Documents/workspace/Team-203"

def run_cmd(cmd, cwd):
    try:
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
        return res.returncode, res.stdout.strip(), res.stderr.strip()
    except Exception as e:
        return -1, "", str(e)

def get_modified_files():
    code, out, err = run_cmd("git status --porcelain", PRIMARY_WS)
    if code != 0:
        print(f"Error checking git status: {err}")
        return []
    
    files = []
    for line in out.splitlines():
        if len(line) > 3:
            filepath = line[3:].strip().strip('"')
            files.append(filepath)
    return files

def main():
    print("🔄 [Workspace Parity] Initiating workspace parity audit and synchronization...")
    
    if not os.path.exists(PRIMARY_WS):
        print(f"Error: Primary workspace path not found: {PRIMARY_WS}")
        sys.exit(1)
        
    if not os.path.exists(SECONDARY_WS):
        print(f"Error: Secondary workspace path not found: {SECONDARY_WS}")
        sys.exit(1)
        
    files = get_modified_files()
    if not files:
        print("✅ No modified or untracked files detected in Git. Both workspaces are in parity.")
        print("🚨 [POLICY REMINDER] STRICT POLICY: No 'git push' without explicit user confirmation.")
        sys.exit(0)
        
    print(f"🔍 Found {len(files)} modified/untracked files in primary workspace.")
    
    has_static_edits = False
    static_extensions = {".html", ".css", ".js", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".md"}
    
    for f in files:
        primary_path = os.path.join(PRIMARY_WS, f)
        secondary_path = os.path.join(SECONDARY_WS, f)
        
        # Check if it is a static asset
        _, ext = os.path.splitext(f.lower())
        if ext in static_extensions:
            has_static_edits = True
            
        if not os.path.exists(primary_path):
            if os.path.exists(secondary_path):
                try:
                    if os.path.isdir(secondary_path):
                        shutil.rmtree(secondary_path)
                    else:
                        os.remove(secondary_path)
                    print(f"  🗑️ Deleted in secondary: {f}")
                except Exception as e:
                    print(f"  ❌ Error deleting {f}: {e}")
            continue
            
        try:
            parent_dir = os.path.dirname(secondary_path)
            os.makedirs(parent_dir, exist_ok=True)
            
            if os.path.isdir(primary_path):
                if os.path.exists(secondary_path):
                    shutil.rmtree(secondary_path)
                shutil.copytree(primary_path, secondary_path)
            else:
                shutil.copy2(primary_path, secondary_path)
            print(f"  ➕ Synchronized: {f}")
        except Exception as e:
            print(f"  ❌ Error synchronizing {f}: {e}")
            
    print("\n✅ Synchronization completed successfully.")
    
    print("\n------------------------------------------------------------")
    print("🚨 [CRITICAL VIRTUAL-OFFICE POLICY ENFORCEMENT]")
    
    if has_static_edits:
        print("⚠️  [WARNING 1 BREACH PREVENTION]")
        print("    Static assets (HTML/CSS/JS/Markdown/Images) have been modified!")
        print("    STRICT POLICY: DO NOT run 'pytest' or backend unit tests during static edits.")
        print("    Running tests triggers autocommit/checkpoint hooks, creating system congestion.")
        
    print("⚠️  [GIT PUSH LOCK ENFORCEMENT]")
    print("    STRICT POLICY: Under NO circumstances should 'git push' be called autonomously.")
    print("    Always ask the user for explicit 'push' confirmation in the chat first.")
    print("------------------------------------------------------------\n")

if __name__ == "__main__":
    main()
