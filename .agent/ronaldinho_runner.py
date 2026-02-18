import os
import time
import json
import subprocess

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MISSION_STORE = os.path.join(WORKSPACE_ROOT, ".agent", "MISSION_STORE.toon")
LOG_DIR = os.path.join(WORKSPACE_ROOT, "logs", "runs")

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
    print("--- Ronaldinho LITE Runner Started ---")
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

        time.sleep(10)

if __name__ == "__main__":
    run_loop()
