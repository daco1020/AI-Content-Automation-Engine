import os
import requests
import random
from pathlib import Path
from typing import Optional, List
from dotenv import load_dotenv

from tools.common.messenger import Messenger

load_dotenv()

class PixabayImageGenerator:
    """
    Image Generator using Pixabay API (Stock Photos).
    """
    base_url: str = "https://pixabay.com/api/"

    def __init__(self):
        self.api_key = os.getenv("PIXABAY_API_KEY")
        if not self.api_key:
            Messenger.warning("PIXABAY_API_KEY not found in .env. Pixabay tool will fail until configured.")

    def generate_image(self, prompt: str, output_path: Path) -> None:
        """
        Searches Pixabay for a relevant image and downloads it.
        """
        if not self.api_key:
            raise RuntimeError("PIXABAY_API_KEY missing. Please add it to your .env file.")

        import re
        # Clean prompt: remove punctuation and keep max 5 words to stay well under 100 chars limit
        clean_prompt = re.sub(r'[^\w\s]', ' ', prompt)
        clean_prompt = re.sub(r'\s+', ' ', clean_prompt).strip()
        words = clean_prompt.split()
        optimized_query = " ".join(words[:5]) if words else "background"

        params = {
            "key": self.api_key,
            "q": optimized_query,
            "lang": "es", # Support Spanish queries as they are common
            "image_type": "photo",
            "orientation": "vertical", 
            "safesearch": "true",
            "per_page": 5
        }

        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            hits = data.get("hits", [])
            if not hits:
                # Fallback: try first two words only for broader search
                fallback_query = " ".join(words[:2]) if len(words) >= 2 else "background"
                Messenger.warning(f"No Pixabay images for '{optimized_query}'. Retrying with '{fallback_query}'...")
                params["q"] = fallback_query
                response = requests.get(self.base_url, params=params, timeout=30)
                hits = response.json().get("hits", [])

            if not hits:
                raise RuntimeError(f"No Pixabay images found for query: {optimized_query}")

            hit = random.choice(hits)
            image_url = hit.get("largeImageURL") or hit.get("webformatURL")

            img_data = requests.get(image_url).content
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'wb') as f:
                f.write(img_data)
            
            Messenger.success(f"Stock image downloaded: {output_path.name}")

        except Exception as e:
            Messenger.error(f"Error in Pixabay: {str(e)}")
            raise e

    def generate_images(self, tasks: List) -> None:
        """
        Generates multiple images sequentially.
        """
        total = len(tasks)
        Messenger.info(f"🎞️ Fetching {total} stock images from Pixabay...")
        for i, task in enumerate(tasks):
            # The pipeline passes task.prompt which we expect to be the search keywords
            self.generate_image(task.prompt, task.output_path)
