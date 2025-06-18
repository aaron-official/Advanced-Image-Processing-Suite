import logging
from PIL import Image
import numpy as np
from pathlib import Path

class ImageAnalysis:
    @staticmethod
    def analyze_image(img_path):
        if not img_path:
            return {"error": "No image provided"}
        try:
            img = Image.open(img_path)
            analysis = {
                "dimensions": f"{img.width} x {img.height}",
                "format": img.format,
                "mode": img.mode,
                "file_size": f"{Path(img_path).stat().st_size / 1024:.1f} KB",
                "has_transparency": img.mode in ("RGBA", "LA") or "transparency" in img.info,
                "color_palette": "Analyzed" if img.mode == "P" else "N/A"
            }
            if img.mode == "RGB":
                img_array = np.array(img)
                analysis["average_color"] = {
                    "red": int(np.mean(img_array[:,:,0])),
                    "green": int(np.mean(img_array[:,:,1])),
                    "blue": int(np.mean(img_array[:,:,2]))
                }
                analysis["brightness"] = int(np.mean(img_array))
            return analysis
        except Exception as e:
            logging.exception("Image analysis failed")
            return {"error": f"Analysis failed: {str(e)}"}
