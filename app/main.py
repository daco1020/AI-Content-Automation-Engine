import asyncio
import os
import shutil
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from flows.image_content_generator.pipeline.pipeline import Pipeline
from flows.image_content_generator.pipeline.schemas import VideoOrientation, State
from tools.common.messenger import Messenger

app = FastAPI(title="AI Content Automation Engine")

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "app" / "static"
OUT_SHORT = BASE_DIR / "flows" / "image_content_generator" / "out_short"
RESOURCE_BASE = BASE_DIR / "flows" / "image_content_generator" / "resource"

# In-memory status tracking
class GenerationStatus(BaseModel):
    is_running: bool = False
    current_step: str = "Idle"
    progress: int = 0
    last_error: Optional[str] = None
    last_video_url: Optional[str] = None
    log_messages: List[str] = []

status = GenerationStatus()

# Custom Messenger to capture logs for the UI
class UIMessenger:
    @staticmethod
    def log(msg: str):
        status.log_messages.append(msg)
        if len(status.log_messages) > 100:
            status.log_messages.pop(0)
        print(msg)

class GenerateRequest(BaseModel):
    language: str = "SPANISH (LATAM)"
    topic: str = ""
    style: str = "Modern cinematic style"
    quantity: int = 1
    category: str = "RANDOM"
    image_source: str = "pixabay"

# Language mapping for Whisper
LANG_MAP = {
    "SPANISH (LATAM)": "es",
    "ENGLISH": "en",
    "FRENCH": "fr",
    "GERMAN": "de"
}

# Pipeline wrapper
async def run_full_pipeline(req: GenerateRequest):
    global status
    status.is_running = True
    status.log_messages = []
    status.last_error = None
    status.progress = 0
    
    lang_code = LANG_MAP.get(req.language, "es")
    
    try:
        pipeline = Pipeline(
            out_base=OUT_SHORT,
            resource_base=RESOURCE_BASE,
            orientation=VideoOrientation.SHORT
        )
        
        for i in range(req.quantity):
            video_prefix = f"[Video {i+1}/{req.quantity}] "
            UIMessenger.log(f"🎬 Iniciando generación de video {i+1} de {req.quantity}...")
            
            # Step 1 with custom parameters
            status.current_step = f"{video_prefix}Generando historia..."
            UIMessenger.log(f"{video_prefix}Generando historia ({req.language})...")
            current_idea_id = await asyncio.to_thread(
                pipeline.step1_generate_story, 
                language=req.language, 
                topic=req.topic, 
                style=req.style,
                category_name=req.category
            )
            # Progress calculation: i/total + (step_prog/total)
            status.progress = int((i / req.quantity) * 100 + (15 / req.quantity))

            steps = [
                ("Generando imágenes...", pipeline.step2_generate_images, [current_idea_id, req.image_source], 40),
                ("Generando audios y alineación...", pipeline.step3_generate_audios, [lang_code, current_idea_id], 60),
                ("Ensamblando escenas...", pipeline.step4_generate_videos, [current_idea_id], 75),
                ("Agregando subtítulos...", pipeline.step5_generate_subtitles, [lang_code, current_idea_id], 85),
                ("Mezclando música de fondo...", pipeline.step6_add_background_music, [current_idea_id], 95),
                ("Finalizando video...", pipeline.step7_rename_final_video, [current_idea_id], 100),
            ]
            
            for msg, func, args, prog in steps:
                status.current_step = f"{video_prefix}{msg}"
                UIMessenger.log(f"{video_prefix}{msg}")
                await asyncio.to_thread(func, *args)
                status.progress = int((i / req.quantity) * 100 + (prog / req.quantity))
            
            UIMessenger.log(f"✅ Video {i+1} completado.")
            
        status.current_step = "Serie Completada"
        status.progress = 100
        UIMessenger.log("✨ Serie de videos generada con éxito!")
        
        # Find the last video of the series using the last known ID
        if 'current_idea_id' in locals():
            latest_idea_dir = pipeline.get_idea_path(current_idea_id)
            # We look for mp4 files ONLY in the root of the idea folder (the named ones)
            video_files = [f for f in latest_idea_dir.glob("*.mp4") if f.is_file()]
            if video_files:
                # Use the most recent one
                video_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                final_v = video_files[0]
                # Map to static URL
                rel_path = final_v.relative_to(OUT_SHORT / "ideas")
                status.last_video_url = f"/outputs/{rel_path}"
                UIMessenger.log(f"🎬 Video final disponible en: {status.last_video_url}")
            else:
                UIMessenger.log("⚠️ No se encontró el archivo .mp4 final en la carpeta del proyecto.")
        else:
            UIMessenger.log("⚠️ No se pudo determinar el ID del último proyecto generado.")

    except Exception as e:
        status.last_error = str(e)
        UIMessenger.log(f"❌ Error: {str(e)}")
    finally:
        status.is_running = False

@app.post("/api/generate")
async def start_generation(req: GenerateRequest, background_tasks: BackgroundTasks):
    if status.is_running:
        raise HTTPException(status_code=400, detail="Ya hay una generación en curso")
    background_tasks.add_task(run_full_pipeline, req)
    return {"message": "Generación iniciada"}

@app.get("/api/status")
async def get_status():
    return status

# Serve outputs as static files
app.mount("/outputs", StaticFiles(directory=str(OUT_SHORT / "ideas")), name="outputs")

# Serve UI
if STATIC_DIR.exists():
    app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
