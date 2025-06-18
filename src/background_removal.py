import requests
import logging
from PIL import Image
import io
from pathlib import Path

class BackgroundRemover:
    def __init__(self, removebg_key=None):
        self.removebg_key = removebg_key

    def remove_local(self, input_path):
        from rembg import remove
        try:
            img = Image.open(input_path)
            result = remove(img)
            out_path = Path(input_path).with_name(f"nobg_{Path(input_path).name}")
            result.save(out_path)
            return str(out_path), "✅ Background removed locally"
        except Exception as e:
            logging.exception("Local background removal failed")
            return None, f"❌ Background removal error: {str(e)}"

    def remove_with_removebg(self, input_path):
        if not self.removebg_key:
            return None, "❌ Remove.bg API key not provided"
        try:
            with open(input_path, 'rb') as img_file:
                response = requests.post(
                    'https://api.remove.bg/v1.0/removebg',
                    files={'image_file': img_file},
                    data={'size': 'auto'},
                    headers={'X-Api-Key': self.removebg_key},
                    timeout=30
                )
            if response.status_code == 200:
                out_path = Path(input_path).with_name(f"removebg_{Path(input_path).name}")
                with open(out_path, 'wb') as out_file:
                    out_file.write(response.content)
                return str(out_path), "✅ Background removed with Remove.bg"
            else:
                return None, f"❌ Remove.bg API Error: {response.text}"
        except Exception as e:
            logging.exception("Remove.bg API background removal failed")
            return None, f"❌ Remove.bg error: {str(e)}"
