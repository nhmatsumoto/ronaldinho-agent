import argparse
import os
import subprocess
import sys
from pathlib import Path

# Paths
WORKSPACE_ROOT = Path(__file__).parent
RONALDINHO_CORE = WORKSPACE_ROOT / "ronaldinho" / "core" / "runner.py"
SKILLS_DIR = WORKSPACE_ROOT / "ronaldinho" / "skills"

def run_agent():
    """Start the Ronaldinho Agent Runner and the Telegram Bridge."""
    print("[*] Starting Ronaldinho System...")
    
    bridge_path = WORKSPACE_ROOT / "services" / "Ronaldinho.Bridge" / "Ronaldinho.Bridge.csproj"
    bridge_proc = None
    
    try:
        if bridge_path.exists():
            print("[+] Starting Telegram Bridge (.NET)...")
            bridge_proc = subprocess.Popen(
                ["dotnet", "run", "--project", str(bridge_path)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.STDOUT
            )
        
        print("[+] Starting Ronaldinho Agent Brain...")
        subprocess.run([sys.executable, str(RONALDINHO_CORE)], check=True)
        
    except KeyboardInterrupt:
        print("\n[!] Stopping Ronaldinho...")
    except Exception as e:
        print(f"[-] Error starting system: {e}")
    finally:
        if bridge_proc:
            print("[*] Shutting down Telegram Bridge...")
            bridge_proc.terminate()
            try:
                bridge_proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                bridge_proc.kill()

def sync_memory(summary):
    """Sync agent memory with GitHub."""
    print(f"🧠 Syncing memory: {summary}")
    memory_tool = SKILLS_DIR / "memory_tool.py"
    try:
        subprocess.run([sys.executable, str(memory_tool), "sync", "--summary", summary], check=True)
    except Exception as e:
        print(f"❌ Sync failed: {e}")

def main():
    parser = argparse.ArgumentParser(description="Gemini CLI - Ronaldinho-Agent Control Center")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Start command
    subparsers.add_parser("start", help="Start the Ronaldinho Agent runner")

    # Sync command
    sync_parser = subparsers.add_parser("sync", help="Sync project context/memory")
    sync_parser.add_argument("--summary", required=True, help="Description of the changes")

    # Help command
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()

    if args.command == "start":
        run_agent()
    elif args.command == "sync":
        sync_memory(args.summary)

if __name__ == "__main__":
    main()
