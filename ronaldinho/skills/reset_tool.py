import os
import shutil
import sys

def reset_workspace(root_path):
    workspace_path = os.path.join(root_path, "workspace")
    config_path = os.path.join(root_path, "ronaldinho", "config")
    audit_path = os.path.join(root_path, "ronaldinho", "audit")
    
    print(f"--- INIT WORKSPACE RESET ---")
    
    # 1. Clear workspace/
    if os.path.exists(workspace_path):
        print(f"> Cleaning {workspace_path}...")
        for item in os.listdir(workspace_path):
            item_path = os.path.join(workspace_path, item)
            try:
                if os.path.isfile(item_path) or os.path.islink(item_path):
                    os.unlink(item_path)
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
            except Exception as e:
                print(f"  ! Could not delete {item_path}: {e}")
    
    # 2. Reset MISSION_STORE.toon
    mission_store = os.path.join(config_path, "MISSION_STORE.toon")
    if os.path.exists(mission_store):
        print(f"> Resetting {mission_store}...")
        header = "| ID | Nome | Status | Responsável |\n| :--- | :--- | :--- | :--- |\n"
        with open(mission_store, "w", encoding="utf-8") as f:
            f.write(header)

    # 3. Purge audit logs
    if os.path.exists(audit_path):
        print(f"> Purging logs in {audit_path}...")
        for f in os.listdir(audit_path):
            if f.endswith(".jsonl"):
                try:
                    os.remove(os.path.join(audit_path, f))
                except:
                    pass

    print("--- RESET COMPLETE. READY FOR NEW PROJECT ---")

if __name__ == "__main__":
    # Assuming the script runs from within ronaldinho/skills/ or root
    # Find root by looking for 'ronaldinho' folder
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up until we find 'workspace' and 'ronaldinho'
    root = current_dir
    while root != os.path.dirname(root):
        if os.path.exists(os.path.join(root, "ronaldinho")) and os.path.exists(os.path.join(root, "workspace")):
            break
        root = os.path.dirname(root)
    
    reset_workspace(root)
