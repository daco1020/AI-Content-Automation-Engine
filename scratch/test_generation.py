import os
from pathlib import Path
from flows.image_content_generator.pipeline.pipeline import Pipeline
from flows.image_content_generator.pipeline.schemas import VideoOrientation
from tools.common.messenger import Messenger
from dotenv import load_dotenv

load_dotenv()

def test_full_generation():
    # 1. Config
    out_base = Path("flows/image_content_generator/out_short")
    resource_base = Path("flows/image_content_generator/resources")
    
    pipeline = Pipeline(
        out_base=out_base,
        resource_base=resource_base,
        orientation=VideoOrientation.SHORT
    )
    
    topic = "Consejos prácticos de ahorro para niños: La alcancía mágica"
    language = "es"
    
    try:
        Messenger.info(f"🚀 INICIANDO PRUEBA COMPLETA: {topic}")
        
        # Step 1: Generate Story
        idea_id = pipeline.step1_generate_story(topic=topic, language="SPANISH (LATAM)")
        Messenger.success(f"Paso 1 completado. Idea ID: {idea_id}")
        
        # Step 2: Generate Images (Pixabay)
        pipeline.step2_generate_images(idea_id=idea_id)
        Messenger.success("Paso 2 completado: Imágenes descargadas de Pixabay.")
        
        # Step 3: Generate Audios (Edge-TTS)
        pipeline.step3_generate_audios(language=language, idea_id=idea_id)
        Messenger.success("Paso 3 completado: Audios generados con Edge-TTS.")
        
        # Step 4: Generate Videos (FFmpeg)
        pipeline.step4_generate_videos(idea_id=idea_id)
        Messenger.success("Paso 4 completado: Clips de video generados.")
        
        # Step 5: Assemble Final Video
        pipeline.step5_assemble_final_video(idea_id=idea_id)
        Messenger.success("Paso 5 completado: Video final ensamblado.")
        
        # Step 6: Add Captions
        pipeline.step6_add_captions(idea_id=idea_id)
        Messenger.success("Paso 6 completado: Subtítulos añadidos.")
        
        Messenger.success(f"✨ ¡PRUEBA FINALIZADA CON ÉXITO! El video está listo en la carpeta de la idea {idea_id}")
        
    except Exception as e:
        Messenger.error(f"FALLO EN LA PRUEBA: {str(e)}")

if __name__ == "__main__":
    test_full_generation()
