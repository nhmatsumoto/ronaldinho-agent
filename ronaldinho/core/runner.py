import os
import time
import json
import subprocess

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MISSION_STORE = os.path.join(WORKSPACE_ROOT, "ronaldinho", "config", "mission_store.toon")
LOG_DIR = os.path.join(WORKSPACE_ROOT, "ronaldinho", "audit")
SKILLS_DIR = os.path.join(WORKSPACE_ROOT, "ronaldinho", "skills")

def log_event(agent, event, status, mission_id=None):
    os.makedirs(LOG_DIR, exist_ok=True)
    log_file = os.path.join(LOG_DIR, f"run_{time.strftime('%Y%m%d')}.jsonl")
    entry = {
        "ts": time.time(),
        "agent": agent,
        "event": event,
        "status": status,
        "mission_id": mission_id
    }
    with open(log_file, "a") as f:
        f.write(json.dumps(entry) + "\n")

def parse_missions():
    if not os.path.exists(MISSION_STORE):
        return []
    
    missions = []
    with open(MISSION_STORE, "r", encoding="utf-8") as f:
        for line in f:
            if "| M-" in line:
                parts = [p.strip() for p in line.split("|")]
                if len(parts) >= 5:
                    missions.append({
                        "id": parts[1],
                        "name": parts[2],
                        "status": parts[3],
                        "owner": parts[4]
                    })
    return missions

def update_mission_status(mission_id, new_status):
    if not os.path.exists(MISSION_STORE):
        return
    
    lines = []
    with open(MISSION_STORE, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    with open(MISSION_STORE, "w", encoding="utf-8") as f:
        for line in lines:
            if f"| {mission_id} |" in line:
                parts = [p.strip() for p in line.split("|")]
                parts[3] = new_status
                f.write(f"| {' | '.join(parts[1:-1])} |\n")
            else:
                f.write(line)

def run_loop():
    print("=== Ronaldinho LITE Runner Started ===")
    while True:
        missions = parse_missions()
        active = [m for m in missions if m["status"] in ["EM_EXECUCAO", "EM_PROGRESSO", "EM_PLANEJAMENTO"]]
        
        for m in active:
            print(f"> Executing Mission [{m['id']}]: {m['name']}")
            log_event("Orquestrador", f"Iniciando missão {m['name']}", "PROCESSANDO", m['id'])
            
            # Update to In Progress
            update_mission_status(m['id'], "EM_PROGRESSO")
            
            # Simple execution simulation for the LITE version
            time.sleep(2) 
            
            # Success
            update_mission_status(m['id'], "CONCLUIDO")
            log_event("Orquestrador", f"Missão {m['name']} finalizada", "SUCESSO", m['id'])
            print(f"> Mission {m['id']} DONE.")

        # Self-Audit Loop (Rule #11 - Evolution)
        try:
            audit_script = os.path.join(WORKSPACE_ROOT, "ronaldinho", "skills", "audit_tool.py")
            memory_dir = os.path.join(WORKSPACE_ROOT, "ronaldinho", "memory")
            subprocess.run(["python", audit_script, LOG_DIR, memory_dir], capture_output=True)
            
            # Memory Sync to GitHub
            memory_script = os.path.join(WORKSPACE_ROOT, "ronaldinho", "skills", "memory_tool.py")
            subprocess.run(["python", memory_script, "sync", "--summary", "Automatic context sync"], capture_output=True)
        except Exception as e:
            print(f"! Self-Audit or Memory Sync Failed: {e}")

        # Telegram Bridge Polling (Rule #4 Compliance)
        try:
            bridge_script = os.path.join(SKILLS_DIR, "bridge_tool.py")
            reasoning_script = os.path.join(SKILLS_DIR, "reasoning_tool.py")
            
            result = subprocess.run(["python", bridge_script, "--check"], capture_output=True, text=True)
            if result.stdout.strip() != "[]":
                messages = json.loads(result.stdout)
                for msg in messages:
                    user_id = msg['user_id']
                    text = msg['text']
                    print(f"[+] Telegram Message Received: {text}")
                    
                    # 0. Show Typing Status
                    subprocess.run(["python", bridge_script, "--typing", str(user_id)])
                    
                    # 1. Reasoning
                    reason_res = subprocess.run(["python", reasoning_script, text, str(user_id)], capture_output=True, text=True)
                    try:
                        # Clean the output in case there's extra text
                        output = reason_res.stdout.strip()
                        if not output:
                             raise ValueError("Empty reasoning output")
                             
                        plan = json.loads(output)
                        if plan and "skill" in plan:
                            skill_script = os.path.join(SKILLS_DIR, f"{plan['skill']}.py")
                            action = plan["action"]
                            args = plan["args"]
                            
                            print(f"[!] Executing Action: {plan['skill']} -> {action}")
                            exec_res = subprocess.run(["python", skill_script, action] + args, capture_output=True, text=True)
                            response_text = f"Acao concluida:\n{exec_res.stdout.strip()}"
                        else:
                            response_text = f"🤔 Ronaldinho ainda não sabe como fazer isso diretamente: '{text}'. Vou tentar evoluir para aprender!"
                    except Exception as e:
                        print(f"! Error parsing reasoning: {e}")
                        response_text = f"🤖 Recebi: '{text}'. Processando com o nucleo de evolução..."

                    # 2. Respond
                    subprocess.run(["python", bridge_script, "--respond", str(user_id), response_text])
                    log_event("Orquestrador", f"Telegram msg from {user_id}", "PROCESSADO")
        except Exception as e:
            print(f"! Telegram Polling Failed: {e}")

        time.sleep(2)

if __name__ == "__main__":
    try:
        run_loop()
    except KeyboardInterrupt:
        print("\n[!] Ronaldinho Runner interruped by user. Shutting down...")
    except Exception as e:
        print(f"\n[!] Critical Runner Error: {e}")
        log_event("SISTEMA", f"Erro crítico: {e}", "CRASH")
