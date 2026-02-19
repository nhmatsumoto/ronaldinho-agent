import os
import sys
import json
import time
from datetime import datetime

WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CONFIG_DIR = os.path.join(WORKSPACE_DIR, "ronaldinho", "config")
SCHEDULE_FILE = os.path.join(CONFIG_DIR, "schedule.json")

def load_schedule():
    if not os.path.exists(SCHEDULE_FILE):
        return []
    try:
        with open(SCHEDULE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save_schedule(tasks):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(SCHEDULE_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=4)

def add_task(time_expr, skill, action, args=None):
    """
    Adds a task to the schedule. 
    time_expr: 'HH:MM' for daily or raw timestamp for one-shot.
    """
    tasks = load_schedule()
    tasks.append({
        "time": time_expr,
        "skill": skill,
        "action": action,
        "args": args or [],
        "last_run": None
    })
    save_schedule(tasks)
    print(f"✅ Agendado: {skill}:{action} em {time_expr}")

def list_tasks():
    tasks = load_schedule()
    if not tasks:
        print("Nenhuma tarefa agendada.")
        return
    for i, t in enumerate(tasks):
        print(f"[{i}] {t['time']} -> {t['skill']}:{t['action']} (Args: {t['args']})")

def check_and_trigger():
    """Checks if any task is due and returns it for execution."""
    tasks = load_schedule()
    now = datetime.now()
    now_hm = now.strftime("%H:%M")
    triggered = []

    changed = False
    for t in tasks:
        # Simple daily trigger
        if t["time"] == now_hm and t["last_run"] != now.strftime("%Y-%m-%d"):
            triggered.append(t)
            t["last_run"] = now.strftime("%Y-%m-%d")
            changed = True
    
    if changed:
        save_schedule(tasks)
    
    return triggered

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: scheduler_skill [add|list|check] ...")
        sys.exit(1)
    
    cmd = sys.argv[1]
    if cmd == "add" and len(sys.argv) >= 5:
        add_task(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5:])
    elif cmd == "list":
        list_tasks()
    elif cmd == "check":
        found = check_and_trigger()
        if found:
            print(json.dumps(found))
        else:
            print("[]")
