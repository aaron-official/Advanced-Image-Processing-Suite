from PIL import Image, ImageEnhance, ImageOps
import numpy as np
from pathlib import Path
import colorsys
import logging

def apply_custom_filter(img_path, bright, cont, sat, hue):
    if not img_path:
        return None, "❌ Please upload an image"
    try:
        img = Image.open(img_path)
        if bright != 0:
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(1 + bright / 100)
        if cont != 0:
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1 + cont / 100)
        if sat != 0:
            enhancer = ImageEnhance.Color(img)
            img = enhancer.enhance(1 + sat / 100)
        if hue != 0 and img.mode == "RGB":
            img_array = np.array(img)
            hsv = np.array([colorsys.rgb_to_hsv(r/255, g/255, b/255) for r, g, b in img_array.reshape(-1, 3)])
            hsv[:, 0] = (hsv[:, 0] + hue / 360) % 1.0
            rgb = np.array([colorsys.hsv_to_rgb(h, s, v) for h, s, v in hsv])
            img_array = (rgb * 255).astype(np.uint8).reshape(img_array.shape)
            img = Image.fromarray(img_array)
        out_path = Path(img_path).with_name(f"filtered_{Path(img_path).name}")
        img.save(out_path)
        return str(out_path), "✅ Custom filter applied successfully"
    except Exception as e:
        logging.exception("Custom filter failed")
        return None, f"❌ Filter error: {str(e)}"
