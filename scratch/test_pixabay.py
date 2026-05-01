import os
from pathlib import Path
from tools.image_generation.pixabay import PixabayImageGenerator
from tools.common.messenger import Messenger
from dotenv import load_dotenv

load_dotenv()

def test_pixabay():
    gen = PixabayImageGenerator()
    out_path = Path("scratch/test_pixabay.jpg")
    out_path.parent.mkdir(exist_ok=True)
    
    query = "modern office skyscraper sunset"
    print(f"Testing Pixabay with query: {query}")
    try:
        gen.generate_image(query, out_path)
        if out_path.exists():
            print(f"SUCCESS: Image downloaded to {out_path}")
            print(f"Size: {out_path.stat().st_size} bytes")
        else:
            print("FAILED: Image file not found.")
    except Exception as e:
        print(f"ERROR: {str(e)}")

if __name__ == "__main__":
    test_pixabay()
