from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import numpy as np
import cv2
from pathlib import Path
from rembg import remove
import logging

class ImageProcessor:
    def convert_image(self, input_path, output_format, quality=95):
        try:
            img = Image.open(input_path)
            if output_format.upper() in ["JPEG", "JPG", "BMP", "PDF"]:
                if img.mode in ("RGBA", "LA", "P"):
                    background = Image.new("RGB", img.size, (255, 255, 255))
                    if img.mode == "P":
                        img = img.convert("RGBA")
                    background.paste(img, mask=img.split()[-1] if img.mode in ("RGBA", "LA") else None)
                    img = background
                else:
                    img = img.convert("RGB")
            elif output_format.upper() == "PNG":
                if img.mode != "RGBA":
                    img = img.convert("RGBA")
            elif output_format.upper() in ["TIFF", "TIF"]:
                pass
            else:
                img = img.convert("RGB")
            out_path = Path(input_path).with_suffix(f".{output_format.lower()}")
            save_kwargs = {}
            if output_format.upper() in ["JPEG", "JPG"]:
                save_kwargs = {"quality": quality, "optimize": True}
            elif output_format.upper() == "PNG":
                save_kwargs = {"optimize": True}
            elif output_format.upper() == "WEBP":
                save_kwargs = {"quality": quality, "method": 6}
            img.save(out_path, format=output_format.upper(), **save_kwargs)
            return str(out_path), f"✅ Converted to {output_format.upper()}"
        except Exception as e:
            logging.exception("Image conversion failed")
            return None, f"❌ Error: {str(e)}"

    def enhance_image(self, input_path, enhancement_type, intensity=1.0):
        try:
            img = Image.open(input_path)
            if enhancement_type == "AI Super Resolution":
                img = img.resize((img.width * 2, img.height * 2), Image.LANCZOS)
            elif enhancement_type == "Noise Reduction":
                cv_img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
                denoised = cv2.fastNlMeansDenoisingColored(cv_img, None, 10, 10, 7, 21)
                img = Image.fromarray(cv2.cvtColor(denoised, cv2.COLOR_BGR2RGB))
            elif enhancement_type == "Color Enhancement":
                enhancer = ImageEnhance.Color(img)
                img = enhancer.enhance(1.0 + intensity * 0.5)
            elif enhancement_type == "Brightness/Contrast":
                brightness = ImageEnhance.Brightness(img)
                img = brightness.enhance(1.0 + intensity * 0.2)
                contrast = ImageEnhance.Contrast(img)
                img = contrast.enhance(1.0 + intensity * 0.3)
            elif enhancement_type == "Sharpening":
                enhancer = ImageEnhance.Sharpness(img)
                img = enhancer.enhance(1.0 + intensity)
            elif enhancement_type == "HDR Effect":
                img_array = np.array(img, dtype=np.float32) / 255.0
                img_array = np.power(img_array, 0.5 + intensity * 0.3)
                img = Image.fromarray((img_array * 255).astype(np.uint8))
            elif enhancement_type == "Black & White":
                img = img.convert("L").convert("RGB")
            elif enhancement_type == "Sepia":
                img = ImageOps.colorize(img.convert("L"), "#704214", "#C8B99C")
            elif enhancement_type == "Vintage Filter":
                img = ImageEnhance.Contrast(img).enhance(0.8)
                img = ImageEnhance.Brightness(img).enhance(1.1)
                img = ImageEnhance.Color(img).enhance(0.7)
            elif enhancement_type == "Vignette":
                mask = Image.new("L", img.size, 0)
                center_x, center_y = img.size[0] // 2, img.size[1] // 2
                max_dist = min(center_x, center_y)
                for y in range(img.size[1]):
                    for x in range(img.size[0]):
                        dist = ((x - center_x) ** 2 + (y - center_y) ** 2) ** 0.5
                        alpha = max(0, 255 - int(255 * dist / max_dist * intensity))
                        mask.putpixel((x, y), alpha)
                img.putalpha(mask)
                background = Image.new("RGB", img.size, (0, 0, 0))
                background.paste(img, img)
                img = background
            out_path = Path(input_path).with_name(f"enhanced_{Path(input_path).name}")
            img.save(out_path)
            return str(out_path), f"✅ Applied {enhancement_type} enhancement"
        except Exception as e:
            logging.exception("Image enhancement failed")
            return None, f"❌ Enhancement error: {str(e)}"

    def remove_background(self, input_path, service="local"):
        try:
            if service == "local":
                img = Image.open(input_path)
                result = remove(img)
                out_path = Path(input_path).with_name(f"nobg_{Path(input_path).name}")
                result.save(out_path)
                return str(out_path), "✅ Background removed locally"
            else:
                return None, f"❌ Service {service} not implemented in this module"
        except Exception as e:
            logging.exception("Background removal failed")
            return None, f"❌ Background removal error: {str(e)}"
