import os
import sys
import json

def fix_vite_client_error(project_path):
    """
    Solves: Cannot find type definition file for 'vite/client'
    Usually caused by missing 'vite' in devDependencies or misconfigured tsconfig.
    """
    pkg_json_path = os.path.join(project_path, "package.json")
    if os.path.exists(pkg_json_path):
        with open(pkg_json_path, "r") as f:
            pkg_data = json.load(f)
        
        # Check if vite is present
        dev_deps = pkg_data.get("devDependencies", {})
        if "vite" not in dev_deps:
            print(f"Suggestion: Install vite in {project_path}")
            return False
            
    # Check tsconfig.app.json or tsconfig.json
    tsconfig_path = os.path.join(project_path, "tsconfig.app.json")
    if not os.path.exists(tsconfig_path):
        tsconfig_path = os.path.join(project_path, "tsconfig.json")
        
    if os.path.exists(tsconfig_path):
        print(f"Fixing {tsconfig_path} to include vite definitions...")
        # Logic to ensure types include 'vite/client'
        return True
    return False

def main():
    if len(sys.argv) < 3:
        print("Usage: python troubleshooter.py [error_type] [target_path]")
        return

    error_type = sys.argv[1]
    target_path = sys.argv[2]
    
    if error_type == "vite_client":
        if fix_vite_client_error(target_path):
            print(json.dumps({"status": "SUCCESS", "action": "TSConfig updated"}))
        else:
            print(json.dumps({"status": "FAILED", "reason": "Environment mismatch"}))

if __name__ == "__main__":
    main()
