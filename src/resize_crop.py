from PIL import Image
from pathlib import Path
import logging

def resize_crop_image(img_path, mode, width, height, maintain_ratio, quality):
    if not img_path:
        return None, "❌ Please upload an image"
    try:
        img = Image.open(img_path)
        original_size = img.size
        quality_filter = getattr(Image, quality, Image.LANCZOS)
        if mode == "Resize":
            if maintain_ratio:
                img.thumbnail((int(width), int(height)), quality_filter)
            else:
                img = img.resize((int(width), int(height)), quality_filter)
        elif mode == "Crop":
            crop_width, crop_height = int(width), int(height)
            left = (img.width - crop_width) // 2
            top = (img.height - crop_height) // 2
            right = left + crop_width
            bottom = top + crop_height
            img = img.crop((left, top, right, bottom))
        elif mode == "Smart Crop":
            target_ratio = width / height
            current_ratio = img.width / img.height
            if current_ratio > target_ratio:
                new_width = int(img.height * target_ratio)
                left = (img.width - new_width) // 2
                img = img.crop((left, 0, left + new_width, img.height))
            else:
                new_height = int(img.width / target_ratio)
                top = (img.height - new_height) // 2
                img = img.crop((0, top, img.width, top + new_height))
            img = img.resize((int(width), int(height)), quality_filter)
        elif mode == "Canvas Resize":
            canvas = Image.new("RGB", (int(width), int(height)), (255, 255, 255))
            paste_x = (int(width) - img.width) // 2
            paste_y = (int(height) - img.height) // 2
            if img.mode == "RGBA":
                canvas.paste(img, (paste_x, paste_y), img)
            else:
                canvas.paste(img, (paste_x, paste_y))
            img = canvas
        out_path = Path(img_path).with_name(f"{mode.lower()}_{Path(img_path).name}")
        img.save(out_path)
        return str(out_path), f"✅ {mode} completed: {original_size} → {img.size}"
    except Exception as e:
        logging.exception("Resize/crop failed")
        return None, f"❌ Processing error: {str(e)}"
