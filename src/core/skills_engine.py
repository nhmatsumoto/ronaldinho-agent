import os
import logging
import importlib.util
from typing import List, Callable, Any
from pydantic_ai import RunContext

logger = logging.getLogger("skills-engine")

class SkillsEngine:
    """
    Dynamic skill discovery and registration system.
    Inspired by OpenClaw's modular tool loading.
    """
    def __init__(self, skills_dir: str):
        self.skills_dir = skills_dir
        self.loaded_skills = {}
        self.cached_tools = None

    def discover_tools(self) -> List[Callable]:
        """
        Scans the skills directory for Python-based skills and returns 
        the callables ready for PydanticAI. (Cached for speed)
        """
        if self.cached_tools is not None:
            return self.cached_tools

        tools = []
        if not os.path.exists(self.skills_dir):
            self.cached_tools = []
            return tools

        for skill_folder in os.listdir(self.skills_dir):
            folder_path = os.path.join(self.skills_dir, skill_folder)
            if not os.path.isdir(folder_path):
                continue
            
            skill_script = os.path.join(folder_path, "main.py")
            if os.path.exists(skill_script):
                try:
                    spec = importlib.util.spec_from_file_location(skill_folder, skill_script)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    for name in dir(module):
                        obj = getattr(module, name)
                        if callable(obj) and (hasattr(obj, "is_ai_tool") or name.endswith("_tool")):
                            tools.append(obj)
                            logger.info(f"[*] Skill Registry: {skill_folder}.{name}")
                except Exception as e:
                    logger.error(f"[!] Failed to load skill {skill_folder}: {e}")
        
        self.cached_tools = tools
        return tools

    def refresh_cache(self):
        """Clears cache to allow discovery of new skills."""
        self.cached_tools = None

    def get_skills_instructions(self) -> str:
        """Loads all SKILL.md descriptions for the system prompt."""
        instructions = ["### AGENT SKILLS REGISTRY"]
        if not os.path.exists(self.skills_dir):
            return ""

        for skill_folder in os.listdir(self.skills_dir):
            folder_path = os.path.join(self.skills_dir, skill_folder)
            skill_md = os.path.join(folder_path, "SKILL.md")
            if os.path.exists(skill_md):
                with open(skill_md, 'r') as f:
                    instructions.append(f"#### Skill: {skill_folder}\n{f.read()}")
        
        return "\n\n".join(instructions) if len(instructions) > 1 else ""

# Global Instance
skills_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.agent/skills"))
skills_engine = SkillsEngine(skills_path)
