from typing import Sequence, Tuple, Type

from flows.image_content_generator.pipeline.prompt_base.manager import BasePromptManager
from flows.image_content_generator.pipeline.prompt_base.models import (
    BaseIdea,
    CategoryHandler,
    VideoScript,
)
from flows.image_content_generator.pipeline.prompt_shorts.finances import (
    constants as finances_constants,
)
from flows.image_content_generator.pipeline.prompt_shorts.finances.models import FinancesHandler
from flows.image_content_generator.pipeline.prompt_shorts.terror.models import TerrorHandler
from tools.common.messenger import Messenger


class PromptManagerShorts(BasePromptManager):
    """Manager specific to Short videos (9:16), aggregating modular categories."""

    # Finance voice & audio style
    AUDIO_PROMPT: str = finances_constants.AUDIO_PROMPT

    CATEGORIES: Sequence[Type[CategoryHandler]] = [
        FinancesHandler,
        TerrorHandler,
    ]

    def generate_full_story(
        self, 
        content_gen,
        language: str = "SPANISH (LATAM)",
        topic: str = "",
        style: str = "Modern cinematic style",
        category_name: str = "RANDOM"
    ) -> Tuple[BaseIdea, VideoScript, str]:
        """
        Executes the generation loop with CHUNKED script generation:
        1. Selection: Pick a category or use custom topic.
        2. Idea Generation: Prompt for initial idea.
        3. Script Generation: Build script in chunks of ~15 scenes until ~120 total.
        """
        # 1. Selection
        config = None
        if category_name != "RANDOM":
            for cat in self.CATEGORIES:
                if cat.__name__ == category_name:
                    from flows.image_content_generator.pipeline.prompt_base.models import SelectedConfig
                    idea_model = cat.get_random_idea_variant()
                    config = SelectedConfig(
                        category=f"{cat.__name__}_{idea_model.__name__}",
                        handler=cat,
                        idea_prompt=idea_model.get_idea_prompt(),
                        idea_model=idea_model,
                    )
                    break
        
        if config is None:
            config = self.select_random_config()
        
        idea_prompt = config.idea_prompt
        if topic:
            idea_prompt += f"\n\n**TEMA ESPECÍFICO / IDEA SEMILLA:** {topic}"

        # 2. Idea Generation
        idea_data = content_gen.generate_text(idea_prompt, config.idea_model)

        # 3. Chunked Script Generation
        Messenger.info(f"\n--- Generating chunked script for: {idea_data.title} ---")
        
        TARGET_SCENES = 120
        SCENES_PER_CHUNK = 15
        NUM_CHUNKS = TARGET_SCENES // SCENES_PER_CHUNK  # 8 chunks
        
        all_scenes = []
        
        for chunk_idx in range(NUM_CHUNKS):
            start_scene = chunk_idx * SCENES_PER_CHUNK + 1
            end_scene = start_scene + SCENES_PER_CHUNK - 1
            
            Messenger.info(f"📝 Generating chunk {chunk_idx+1}/{NUM_CHUNKS} (Scenes {start_scene}-{end_scene})...")
            
            # Build context from previous scenes
            if all_scenes:
                last_3 = all_scenes[-3:]
                context_summary = "\n".join([
                    f"Scene {s.scene_number}: {s.narration[:80]}..." for s in last_3
                ])
                continuation_note = (
                    f"\n\n**CONTINUACIÓN:** Este es el chunk {chunk_idx+1} de {NUM_CHUNKS}. "
                    f"Genera las escenas {start_scene} a {end_scene}. "
                    f"IMPORTANTE: Los scene_number DEBEN empezar en {start_scene}. "
                    f"Contexto previo (últimas escenas):\n{context_summary}"
                )
            else:
                continuation_note = (
                    f"\n\n**INICIO:** Este es el chunk 1 de {NUM_CHUNKS}. "
                    f"Genera las escenas 1 a {SCENES_PER_CHUNK}. "
                    f"Empieza con el HOOK potente."
                )
            
            script_prompt = config.handler.get_full_script_prompt(
                idea_data, 
                language=language, 
                style=style
            )
            script_prompt += continuation_note
            
            try:
                chunk_script = content_gen.generate_text(script_prompt, VideoScript)
                
                # Re-number scenes to be sequential
                for i, scene in enumerate(chunk_script.scenes):
                    scene.scene_number = start_scene + i
                
                all_scenes.extend(chunk_script.scenes)
                Messenger.success(f"Chunk {chunk_idx+1}: {len(chunk_script.scenes)} scenes generated. Total: {len(all_scenes)}")
                
            except Exception as e:
                Messenger.warning(f"Chunk {chunk_idx+1} failed: {str(e)}. Continuing with {len(all_scenes)} scenes.")
                if len(all_scenes) >= 30:  # At least 30 scenes = ~30 seconds
                    break
                continue
        
        if not all_scenes:
            raise RuntimeError("Failed to generate any scenes.")
        
        # Build final merged VideoScript
        final_script = VideoScript(scenes=all_scenes)
        Messenger.success(f"✨ Final script: {len(all_scenes)} scenes generated!")

        return idea_data, final_script, config.category

