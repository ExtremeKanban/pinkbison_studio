"""
Stateless agent factory for creating fresh agent instances per task.
Agents don't hold model references or state between tasks.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agents.plot_architect import PlotArchitect
    from agents.worldbuilder import WorldbuilderAgent
    from agents.character_agent import CharacterAgent
    from agents.scene_generator import SceneGeneratorAgent
    from agents.continuity_agent import ContinuityAgent
    from agents.editor_agent import EditorAgent

from core.event_bus import EventBus
from core.audit_log import AuditLog
from memory_store import MemoryStore


class AgentFactory:
    """
    Creates fresh, stateless agent instances on-demand.
    
    Design:
    - Agents are task-scoped, not process-scoped
    - No retained state between tasks
    - Model references injected via ModelPool
    """
    
    def __init__(self, project_name: str, event_bus: EventBus, 
                 audit_log: AuditLog, fast_model_url: str, model_mode: str):
        self.project_name = project_name
        self.event_bus = event_bus
        self.audit_log = audit_log
        self.fast_model_url = fast_model_url
        self.model_mode = model_mode
        self.memory = MemoryStore(project_name)
    
    def create_plot_architect(self) -> "PlotArchitect":
        """Create fresh PlotArchitect instance"""
        from agents.plot_architect import PlotArchitect
        
        return PlotArchitect(
            name="plot_architect",
            project_name=self.project_name,
            event_bus=self.event_bus,
            audit_log=self.audit_log,
            fast_model_url=self.fast_model_url,
            model_mode=self.model_mode
        )
    
    def create_worldbuilder(self) -> "WorldbuilderAgent":
        """Create fresh WorldbuilderAgent instance"""
        from agents.worldbuilder import WorldbuilderAgent
        
        return WorldbuilderAgent(
            name="worldbuilder",
            project_name=self.project_name,
            event_bus=self.event_bus,
            audit_log=self.audit_log,
            fast_model_url=self.fast_model_url,
            model_mode=self.model_mode
        )
    
    def create_character_agent(self) -> "CharacterAgent":
        """Create fresh CharacterAgent instance"""
        from agents.character_agent import CharacterAgent
        
        return CharacterAgent(
            name="character_agent",
            project_name=self.project_name,
            event_bus=self.event_bus,
            audit_log=self.audit_log,
            fast_model_url=self.fast_model_url,
            model_mode=self.model_mode
        )
    
    def create_scene_generator(self) -> "SceneGeneratorAgent":
        """Create fresh SceneGeneratorAgent instance"""
        from agents.scene_generator import SceneGeneratorAgent
        
        return SceneGeneratorAgent(
            name="scene_generator",
            project_name=self.project_name,
            event_bus=self.event_bus,
            audit_log=self.audit_log,
            fast_model_url=self.fast_model_url,
            model_mode=self.model_mode
        )
    
    def create_continuity_agent(self) -> "ContinuityAgent":
        """Create fresh ContinuityAgent instance"""
        from agents.continuity_agent import ContinuityAgent
        
        return ContinuityAgent(
            name="continuity_agent",
            project_name=self.project_name,
            event_bus=self.event_bus,
            audit_log=self.audit_log,
            fast_model_url=self.fast_model_url,
            model_mode=self.model_mode
        )
    
    def create_editor_agent(self) -> "EditorAgent":
        """Create fresh EditorAgent instance"""
        from agents.editor_agent import EditorAgent
        
        return EditorAgent(
            name="editor_agent",
            project_name=self.project_name,
            event_bus=self.event_bus,
            audit_log=self.audit_log,
            fast_model_url=self.fast_model_url,
            model_mode=self.model_mode
        )