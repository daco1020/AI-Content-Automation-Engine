from flows.image_content_generator.pipeline.prompt_base.models import BaseIdea, CategoryHandler
from flows.image_content_generator.pipeline.prompt_shorts.terror import (
    constants as terror_constants,
)

class ParanormalTerrorIdea(BaseIdea):
    """
    Idea model for paranormal terror stories.
    """
    IDEA_PROMPT = terror_constants.IDEA_PROMPT_PARANORMAL
    entity_type: str
    setting_description: str
    climactic_scare: str

class PsychologicalTerrorIdea(BaseIdea):
    """
    Idea model for psychological terror videos.
    """
    IDEA_PROMPT = terror_constants.IDEA_PROMPT_PSYCHOLOGICAL
    protagonist_fear: str
    creepy_realization: str
    plot_twist: str

class TerrorHandler(CategoryHandler):
    """
    Specialized handler for Terror-themed short videos.
    Encapsulates Paranormal and Psychological terror variants.
    """
    SCRIPT_PROMPT = terror_constants.SCRIPT_PROMPT
    idea_variants = [
        ParanormalTerrorIdea,
        PsychologicalTerrorIdea,
    ]
