from pydantic import BaseModel


class Messenger(BaseModel):
    """
    Standardized tool for terminal feedback.
    Rules:
    - info: No emoji.
    - success: ✅ emoji (for minor actions).
    - step_success: 🚀 emoji (for major pipeline steps).
    - warning: ⚠️ emoji.
    - error: ❌ emoji.
    """

    @staticmethod
    def info(message: str) -> None:
        print(message)

    @staticmethod
    def success(message: str) -> None:
        print(f"🚀 {message}")

    @staticmethod
    def step_success(message: str) -> None:
        print(f"✅ {message}")

    @staticmethod
    def warning(message: str) -> None:
        print(f"⚠️ {message}")

    @staticmethod
    def error(message: str) -> None:
        print(f"❌ {message}")

    @staticmethod
    def image(message: str) -> None:
        print(f"🖼️ {message}")

    @staticmethod
    def audio(message: str) -> None:
        print(f"🔊 {message}")

    @staticmethod
    def usage(model: str, prompt: int, thoughts: int, output: int, total: int) -> None:
        print(f"\n📊 [Usage Report: {model}]")
        print(f"   ├─ Prompt: {prompt}")
        print(f"   ├─ Thoughts: {thoughts}")
        print(f"   ├─ Output: {output}")
        print(f"   └─ Total Tokens: {total}\n")
