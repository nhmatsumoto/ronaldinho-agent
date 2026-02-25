import os
import logging

logger = logging.getLogger("neural-core")

# Simple In-Memory Cache for speed
_prompt_cache = {
    "base": None,
    "skills": None,
    "personas": {}
}

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
    """Combines Soul, Knowledge, Skills and optional Persona into the final system prompt with caching."""
    global _prompt_cache
    
    if _prompt_cache["base"] is None:
        _prompt_cache["base"] = load_soul_and_knowledge(root_path)
    
    if _prompt_cache["skills"] is None:
        _prompt_cache["skills"] = load_skills(root_path)
    
    full_prompt = [_prompt_cache["base"], _prompt_cache["skills"]]
    
    if active_persona:
        if active_persona not in _prompt_cache["personas"]:
            _prompt_cache["personas"][active_persona] = load_persona(root_path, active_persona)
        
        persona_info = _prompt_cache["personas"][active_persona]
        if persona_info:
            full_prompt.append(persona_info)
            
    return "\n\n".join(full_prompt)

def clear_brain_cache():
    """Call this when .env or files are updated."""
    global _prompt_cache
    _prompt_cache = {"base": None, "skills": None, "personas": {}}
    logger.info("[🧠] Brain cache cleared.")

def detect_best_persona(message: str) -> str:
    """Heuristically determines the best specialist for a message."""
    msg = message.lower()
    
    # 0. High priority: Antigravity Signal
    if "[antigravity_sig]" in msg:
        return "antigravity_envoy"
    
    # 1. Hardcoded high-priority mappings
    mappings = {
        "architect": ["arquitetura", "projeto", "estrutura", "padrao", "desenho"],
        "frontend": ["frontend", "ui", "ux", "tela", "css", "react", "html", "browser"],
        "database": ["banco", "database", "sql", "postgres", "schema", "query", "mongo"],
        "reviewer": ["bug", "fix", "erro", "consertar", "debug", "audit"],
        "developer": ["codigo", "implemente", "crie", "desenvolva", "funcao", "script"],
        "devops": ["docker", "deploy", "kubernetes", "k8s", "pipeline", "ci/cd", "infra"],
        "security": ["seguranca", "security", "pentest", "vulnerabilidade", "auth"],
        "business": ["saas", "negocio", "plano", "mercado", "roi", "produto"],
        "prompt_engineer": ["prompt", "instrucao", "system prompt", "melhore o prompt"],
        "rag_architect": ["rag", "retrieval", "vetorial", "embeddings"],
    }
    
    for persona, keywords in mappings.items():
        if any(kw in msg for kw in keywords):
            return persona

    # 2. Dynamic slug matching
    # Check if the message contains any of the 100+ roles by their simplified name
    team_dir = ".agent/team"
    if os.path.exists(team_dir):
        files = [f.replace(".toon", "") for f in os.listdir(team_dir) if f.endswith(".toon")]
        for role_slug in files:
            # Check if slug or humanized name is in message
            humanized = role_slug.replace("_", " ")
            if role_slug in msg or humanized in msg:
                return role_slug

    return None
