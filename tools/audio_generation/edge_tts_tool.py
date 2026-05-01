import asyncio
import edge_tts
from pathlib import Path
from typing import List, Optional

from tools.common.messenger import Messenger

class EdgeAudioGenerator:
    """
    Free high-quality TTS using Microsoft Edge TTS (via edge-tts library).
    """
    
    # Map for common languages to high-quality neural voices
    VOICE_MAP = {
        "es": "es-MX-DaliaNeural",
        "en": "en-US-GuyNeural",
        "fr": "fr-FR-DeniseNeural",
        "de": "de-DE-ConradNeural"
    }

    def generate_audio(self, text: str, output_path: Path, language: str = "es") -> None:
        """
        Generates audio file from text using edge-tts.
        """
        voice = self.VOICE_MAP.get(language.lower(), "es-MX-DaliaNeural")
        
        async def _generate():
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(str(output_path))

        try:
            asyncio.run(_generate())
        except Exception as e:
            Messenger.error(f"Error generating Edge TTS: {str(e)}")
            # Fallback could go here if needed
            raise e

    def generate_batch_audio(self, texts: List[str], paths: List[Path], language: str = "es") -> None:
        """
        Generates multiple audio files sequentially.
        """
        Messenger.info(f"🎙️ Generating {len(texts)} audio segments via Edge TTS (Free)...")
        for text, path in zip(texts, paths):
            self.generate_audio(text, path, language)
