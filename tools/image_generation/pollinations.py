import requests
from pathlib import Path
from typing import List, Optional
import time
import random

from tools.image_generation.midjourney import ImageTask # Reusing the Task model
from tools.common.messenger import Messenger

class PollinationsImageGenerator:
    """
    Free Image Generator using Pollinations.ai (No API key required).
    """
    base_url: str = "https://pollinations.ai/p/"

    def __init__(self, aspect_ratio: str = "9:16"):
        self.aspect_ratio = aspect_ratio
        # Map aspect ratios to dimensions for Pollinations
        if aspect_ratio == "9:16":
            self.width, self.height = 576, 1024
        else:
            self.width, self.height = 1024, 576

    def generate_images(self, tasks: List[ImageTask]) -> None:
        """
        Generates images for a list of tasks sequentially.
        """
        if not tasks:
            return

        Messenger.info(f"🎨 Generating {len(tasks)} images for free via Pollinations.ai...")
        
        for i, task in enumerate(tasks):
            try:
                Messenger.info(f"Generating image {i+1}/{len(tasks)}: {task.output_path.name}")
                
                # Encode prompt and add random seed for variety
                seed = random.randint(0, 999999)
                encoded_prompt = requests.utils.quote(task.prompt)
                
                # Pollinations URL format: /p/{prompt}?width={w}&height={h}&seed={s}&model=flux
                # We use flux for better quality
                url = f"{self.base_url}{encoded_prompt}?width={self.width}&height={self.height}&seed={seed}&model=flux&nologo=true"
                
                response = requests.get(url, timeout=60)
                if response.status_code == 200:
                    task.output_path.parent.mkdir(parents=True, exist_ok=True)
                    task.output_path.write_bytes(response.content)
                    Messenger.success(f"Saved: {task.output_path.name}")
                else:
                    Messenger.error(f"Failed to generate image {i+1}: Status {response.status_code}")
                
                # Small sleep to avoid rate limits
                time.sleep(1)
                
            except Exception as e:
                Messenger.error(f"Error in Pollinations generation: {str(e)}")

