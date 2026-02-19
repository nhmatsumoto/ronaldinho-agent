import os
import time
import json
import subprocess
import sys

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if WORKSPACE_ROOT not in sys.path:
    sys.path.append(WORKSPACE_ROOT)

LOG_DIR = os.path.join(WORKSPACE_ROOT, "ronaldinho", "audit")
SKILLS_DIR = os.path.join(WORKSPACE_ROOT, "ronaldinho", "skills")
MISSION_STORE = os.path.join(WORKSPACE_ROOT, "ronaldinho", "config", "mission_store.toon")

def log_event(agent, event, status, mission_id=None):
    os.makedirs(LOG_DIR, exist_ok=True)
    log_file = os.path.join(LOG_DIR, f"run_{time.strftime('%Y%m%d')}.jsonl")
    entry = {"ts": time.time(), "agent": agent, "event": event, "status": status, "mission_id": mission_id}
    with open(log_file, "a") as f:
        f.write(json.dumps(entry) + "\n")

def parse_missions():
    if not os.path.exists(MISSION_STORE): return []
    missions = []
    with open(MISSION_STORE, "r", encoding="utf-8") as f:
        for line in f:
            if "| M-" in line:
                parts = [p.strip() for p in line.split("|")]
                if len(parts) >= 5:
                    missions.append({"id": parts[1], "name": parts[2], "status": parts[3]})
    return missions

def update_mission_status(mission_id, new_status):
    if not os.path.exists(MISSION_STORE): return
    with open(MISSION_STORE, "r", encoding="utf-8") as f: lines = f.readlines()
    with open(MISSION_STORE, "w", encoding="utf-8") as f:
        for line in lines:
            if f"| {mission_id} |" in line:
                parts = [p.strip() for p in line.split("|")]
                parts[3] = new_status
                f.write(f"| {' | '.join(parts[1:-1])} |\n")
            else: f.write(line)

def run_once(silent=False):
    """Processes all pending missions and Telegram messages once."""
    if not silent: print("[!] Reactive Execution Triggered")
    try:
        # 1. Mission Processing
        missions = parse_missions()
        active = [m for m in missions if m["status"] in ["EM_EXECUCAO", "EM_PROGRESSO"]]
        for m in active:
            print(f"> Processing Mission: {m['name']}")
            update_mission_status(m['id'], "CONCLUIDO")

        # 2. Telegram Bridge Polling
        bridge_script = os.path.join(SKILLS_DIR, "bridge_tool.py")
        result = subprocess.run(["python", bridge_script, "--check"], capture_output=True, text=True)
        
        if result.stdout.strip() != "[]":
            messages = json.loads(result.stdout)
            for msg in messages:
                user_id = msg['user_id']
                text = msg['text']
                print(f"[+] Reactive Processing: {text}")
                subprocess.run(["python", bridge_script, "--typing", str(user_id)])
                
                try:
                    from ronaldinho.skills.reasoning_tool import parse_instruction
                    raw_plan = parse_instruction(text, str(user_id))
                    
                    # Zero-Limbo Logic
                    if not raw_plan or (isinstance(raw_plan, dict) and "chat" in raw_plan.get("action", "") and "não sabe" in str(raw_plan.get("args", [""])[0]).lower()):
                        os.environ["REASONING_MODE"] = "PLANNING"
                        raw_plan = parse_instruction(text, str(user_id))
                    
                    plans = raw_plan if isinstance(raw_plan, list) else [raw_plan]
                    response_text = ""
                    
                    for plan in plans:
                        if plan and "skill" in plan:
                            if plan["skill"] == "gemini" and plan["action"] == "chat":
                                response_text += f"\n{plan['args'][0]}"
                                continue

                            skill_name = plan["skill"]
                            toolbox_dir = os.path.join(os.path.dirname(SKILLS_DIR), ".toolbox")
                            
                            if skill_name.startswith("toolbox:"):
                                skill_script = os.path.join(toolbox_dir, f"{skill_name.split(':')[1]}.py")
                            elif os.path.exists(os.path.join(SKILLS_DIR, f"{skill_name}.py")):
                                skill_script = os.path.join(SKILLS_DIR, f"{skill_name}.py")
                            elif os.path.exists(os.path.join(SKILLS_DIR, f"{skill_name}_skill.py")):
                                skill_script = os.path.join(SKILLS_DIR, f"{skill_name}_skill.py")
                            else:
                                skill_script = os.path.join(toolbox_dir, f"{skill_name}.py")

                            if not os.path.exists(skill_script):
                                response_text += f"\n❌ Ferramenta '{skill_name}' não encontrada."
                                continue

                            exec_res = subprocess.run(["python", skill_script, plan["action"]] + [str(a) for a in plan["args"]], capture_output=True, text=True)
                            response_text += f"\n{exec_res.stdout.strip()}"
                        else:
                            response_text += "\n🤖 Evoluindo..."
                except Exception as e:
                    response_text = f"🤖 Erro: {e}"

                if not response_text.strip(): response_text = "Processado."
                subprocess.run(["python", bridge_script, "--respond", str(user_id), response_text.strip()])
                log_event("Orquestrador", f"Processed {text}", "SUCESSO")
                
    except Exception as e:
        print(f"! Reactive Error: {e}")

def run_loop():
    print("=== Ronaldinho Runner Loop started (Heartbeat) ===")
    while True:
        run_once(silent=True)
        time.sleep(0.5) 

if __name__ == "__main__":
    if "--once" in sys.argv:
        run_once(silent=False)
    else:
        try:
            run_loop()
        except KeyboardInterrupt:
            print("\n[!] Shutdown.")
