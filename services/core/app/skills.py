import os

def load_soul_and_knowledge(root_path: str) -> str:
    """Loads the core soul and knowledge files into a single prompt string."""
    soul_path = os.path.join(root_path, "ronaldinho/soul/SOUL.md")
    knowledge_path = os.path.join(root_path, "ronaldinho/soul/KNOWLEDGE.md")
    
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
    skills_dir = os.path.join(root_path, "ronaldinho/skills")
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

def get_integrated_system_prompt(root_path: str) -> str:
    """Combines Soul, Knowledge and Skills into the final system prompt."""
    soul_info = load_soul_and_knowledge(root_path)
    skills_info = load_skills(root_path)
    
    return f"{soul_info}\n\n{skills_info}"
