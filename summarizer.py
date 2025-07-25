import os
import time
from PIL import Image
import google.generativeai as genai
from key_manager import GeminiKeyManager

key_manager = GeminiKeyManager()
text_model = genai.GenerativeModel("models/gemini-1.5-flash-latest")
vision_model = genai.GenerativeModel("models/gemini-1.5-pro-latest")

def summarize_text(text: str) -> str:
    try:
        response = text_model.generate_content(f"Summarize this documentation clearly:\n{text}")
        return response.text
    except Exception as e:
        if "429" in str(e):
            time.sleep(1)
            try:
                key_manager.rotate_key()
                return summarize_text(text)
            except RuntimeError as ex:
                return f"[Quota Error]: {ex}"
        return f"[Error]: {e}"

def summarize_images(image_paths: list) -> str:
    if not image_paths:
        return "No images found in PDF."

    summaries = []
    for path in image_paths:
        try:
            image = Image.open(path)
            response = vision_model.generate_content(
                [f"Summarize the content of this image briefly:", image],
                stream=False
            )
            summaries.append(f"{os.path.basename(path)}: {response.text.strip()}")
        except Exception as e:
            if "429" in str(e):
                time.sleep(1)
                try:
                    key_manager.rotate_key()
                    return summarize_images(image_paths)
                except RuntimeError as ex:
                    return f"[Quota Error]: {ex}"
            summaries.append(f"{os.path.basename(path)}: [Vision Error]: {e}")
    return "\n".join(summaries)
