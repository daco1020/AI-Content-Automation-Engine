import time
from pathlib import Path
from typing import Any, Optional

from google.genai import types

from tools.common.gemini_base import GeminiBase
from tools.common.messenger import Messenger


class GeminiVideoGenerator(GeminiBase):
    """
    Tool for generating videos using Gemini Veo 3.1 models.
    Supports text-to-video and image-to-video interpolation.
    """
    video_model: str = "veo-3.1-fast-generate-preview"

    def generate_video(
        self,
        prompt: str,
        out_path: str,
        img_start_path: Optional[str] = None,
        img_end_path: Optional[str] = None
    ) -> None:
        """
        Generates a high-fidelity video using Veo 3.1 and saves it to disk.
        Supports three modes of generation based on provided inputs:

        Modes:
        1. Text-to-Video: Provide ONLY 'prompt'. Generates video from scratch.
        2. Image-to-Video: Provide 'prompt' + 'img_start_path'. Generates video
           starting from the provided initial frame.
        3. Frame Interpolation: Provide 'prompt' + 'img_start_path' + 'img_end_path'.
           Generates a transition where 'img_start' is the first frame and
           'img_end' is the last frame constraint.

        Technical Parameters:
        - Resolution: 1080p (Optimized for generation cost/performance).
        - Aspect Ratio: 9:16 (Portrait format for mobile/social media).
        - Model: veo-3.1-fast-generate-preview.
        """
        out_path_obj = Path(out_path)
        out_path_obj.parent.mkdir(parents=True, exist_ok=True)

        Messenger.info(f"🚀 Starting AI Video generation: {out_path_obj.name}...")

        # 1. Setup Configuration
        # We enforce 9:16 and 1080p for consistency across the pipeline.
        config_args: dict[str, Any] = {
            "aspect_ratio": "9:16",
            "resolution": "1080p"
        }

        # 'last_frame' serves as a visual constraint for the end of the video.
        if img_end_path:
            config_args["last_frame"] = types.Image(
                image_bytes=Path(img_end_path).read_bytes(),
                mime_type="image/png"
            )
        config = types.GenerateVideosConfig(**config_args)

        # 2. Prepare Primary Image Input
        # For Veo 3, image data MUST be passed as a types.Image object with
        # explicit bytes and mime_type to satisfy the API contract.
        image_input = None
        if img_start_path:
            image_input = types.Image(
                image_bytes=Path(img_start_path).read_bytes(),
                mime_type="image/png"
            )

        # 3. Trigger Asynchronous Generation with internal retry for Code 13
        max_internal_retries = 3
        for attempt in range(max_internal_retries):
            try:
                operation = self.client.models.generate_videos(
                    model=self.video_model,
                    prompt=prompt,
                    image=image_input,
                    config=config
                )

                # 4. Polling for Completion
                # Video generation is a heavy process. We poll every 15 seconds.
                while not operation.done:
                    Messenger.info(f"⏳ Waiting for video generation (polling, attempt {attempt+1})...")
                    time.sleep(15)
                    operation = self.client.operations.get(operation)

                # 5. Result Validation
                if operation.error:
                    # Check if it's an internal error (code 13)
                    error_str = str(operation.error)
                    if "'code': 13" in error_str and attempt < max_internal_retries - 1:
                        Messenger.warning(f"⚠️ Internal Server Error (13) detected. Retrying in 30s... (Attempt {attempt+1}/{max_internal_retries})")
                        time.sleep(30)
                        continue
                    raise RuntimeError(f"❌ Video generation failed: {operation.error}")
                
                # If we reach here, operation succeeded
                break

            except Exception as e:
                if attempt < max_internal_retries - 1:
                    Messenger.warning(f"⚠️ Connection error during generation: {str(e)}. Retrying...")
                    time.sleep(10)
                    continue
                raise e

        # 6. Success: Download and Persist
        # The operation response contains metadata and the generated video object.
        if not operation.response:
            raise RuntimeError("❌ Video generation succeeded but operation.response is empty.")

        generated_videos = getattr(operation.response, "generated_videos", [])
        if not generated_videos:
            raise RuntimeError("❌ Video generation succeeded but no videos were found in response.")

        video_metadata = generated_videos[0]
        video_obj = getattr(video_metadata, "video", None)
        if not video_obj:
            raise RuntimeError("❌ Video metadata found but video object is missing.")

        self.client.files.download(file=video_obj)
        video_obj.save(out_path)

        Messenger.success(f"Video saved: {out_path}")
