import os
import logging

logger = logging.getLogger("neural-core")

def load_soul_and_knowledge(root_path: str) -> str:
    """Loads the core soul and knowledge files into a single prompt string."""
    soul_path = os.path.join(root_path, ".agent/soul/SOUL.md")
    knowledge_path = os.path.join(root_path, ".agent/soul/KNOWLEDGE.md")
    
    prompt_parts = []
    
    if os.path.exists(soul_path):
        with open(soul_path, 'r') as f:
            prompt_parts.append(f"### SOUL (Identity)\n{f.read()}")
            
    if os.path.exists(knowledge_path):
        with open(knowledge_path, 'r') as f:
            prompt_parts.append(f"### KNOWLEDGE (Context)\n{f.read()}")
            
    return "\n\n".join(prompt_parts)

def load_skills(root_path: str) -> str:
    """Discovers and loads all SKILL.md files from the skills directory."""
    skills_dir = os.path.join(root_path, ".agent/skills")
    if not os.path.exists(skills_dir):
        return ""
        
    skills_prompt = ["### SKILLS (Extended Capabilities)"]
    
    for skill_name in os.listdir(skills_dir):
        skill_path = os.path.join(skills_dir, skill_name)
        if os.path.isdir(skill_path):
            skill_file = os.path.join(skill_path, "SKILL.md")
            if os.path.exists(skill_file):
                with open(skill_file, 'r') as f:
                    skills_prompt.append(f"#### Skill: {skill_name}\n{f.read()}")
                    
    return "\n\n".join(skills_prompt) if len(skills_prompt) > 1 else ""

def load_persona(root_path: str, persona_name: str) -> str:
    """Loads a specific specialist persona from the team directory."""
    persona_file = os.path.join(root_path, f".agent/team/{persona_name}.toon")
    if os.path.exists(persona_file):
        with open(persona_file, 'r') as f:
            return f"### ACTIVE SPECIALIST PERSONA: {persona_name.upper()}\n{f.read()}"
    return ""

def get_integrated_system_prompt(root_path: str, active_persona: str = None) -> str:
    """Combines Soul, Knowledge, Skills and optional Persona into the final system prompt."""
    soul_info = load_soul_and_knowledge(root_path)
    skills_info = load_skills(root_path)
    
    full_prompt = [soul_info, skills_info]
    
    if active_persona:
        persona_info = load_persona(root_path, active_persona)
        if persona_info:
            full_prompt.append(persona_info)
            
    return "\n\n".join(full_prompt)

def detect_best_persona(message: str) -> str:
    """Heuristically determines the best specialist for a message."""
    msg = message.lower()
    if any(kw in msg for kw in ["arquitetura", "estrutura", "padrao", "desenho"]):
        return "architect"
    if any(kw in msg for kw in ["frontend", "ui", "ux", "tela", "css", "react"]):
        return "frontend"
    if any(kw in msg for kw in ["banco", "database", "sql", "postgres", "schema"]):
        return "database"
    if any(kw in msg for kw in ["bug", "fix", "erro", "consertar", "debug"]):
        return "reviewer"
    if any(kw in msg for kw in ["codigo", "implemente", "crie", "desenvolva"]):
        return "developer"
    if any(kw in msg for kw in ["saas", "negocio", "plano", "mercado"]):
        return "business"
    return None
