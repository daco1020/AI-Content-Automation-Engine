from typing import ClassVar, Sequence

from flows.image_content_generator.pipeline.prompt_base.models import BaseIdea, CategoryHandler
from flows.image_content_generator.pipeline.prompt_shorts.horror_stories import (
    constants as horror_constants,
)


class HorrorUrbanLegendIdea(BaseIdea):
    """
    Idea model for horror urban legends.
    """

    IDEA_PROMPT: ClassVar[str] = horror_constants.IDEA_PROMPT_URBAN_LEGEND
    entity_description: str
    setting: str
    horror_hook: str


class HorrorStoriesHandler(CategoryHandler):
    """
    Specialized handler for Horror-themed short videos.
    """

    SCRIPT_PROMPT: ClassVar[str] = horror_constants.SCRIPT_PROMPT
    AUDIO_PROMPT: ClassVar[str] = horror_constants.AUDIO_PROMPT
    idea_variants: ClassVar[Sequence[type[BaseIdea]]] = [
        HorrorUrbanLegendIdea,
    ]
