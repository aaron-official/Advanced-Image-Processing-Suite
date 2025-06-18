import os
from config.settings import (
    OPENAI_API_KEY, ANTHROPIC_API_KEY, REMOVE_BG_API_KEY, DEEPSEEK_API_KEY,
    GRADIO_SERVER_NAME, GRADIO_SERVER_PORT
)
from config.logging_config import setup_logging
from src.image_processing import ImageProcessor
from src.ai_image_generator import AIImageGenerator
from src.background_removal import BackgroundRemover
from src.image_analysis import ImageAnalysis
from src.custom_filters import apply_custom_filter
from src.resize_crop import resize_crop_image
import logging
import io
import zipfile
import tempfile
from PIL import Image

setup_logging()
logger = logging.getLogger(__name__)

import gradio as gr

SUPPORTED_FORMATS = [
    "JPEG", "JPG", "PNG", "BMP", "TIFF", "TIF", "WEBP", "GIF", 
    "ICO", "EPS", "PDF", "PSD", "SVG", "HEIC", "AVIF", "JXL"
]
ENHANCEMENT_OPTIONS = [
    "AI Super Resolution", "Noise Reduction", "Color Enhancement", "Brightness/Contrast", "Sharpening", "HDR Effect", "Vintage Filter", "Black & White", "Sepia", "Vignette", "Blur Background"
]

processor = ImageProcessor()
ai_generator = AIImageGenerator(openai_key=OPENAI_API_KEY, anthropic_key=ANTHROPIC_API_KEY)
bg_remover = BackgroundRemover()

# Restore AI_MODELS and BG_REMOVAL_SERVICES constants
AI_MODELS = {
    "OpenAI DALL-E 3": "dall-e-3",
    "OpenAI DALL-E 2": "dall-e-2",
    "Anthropic Claude (via API)": "claude-3-5-sonnet-20241022",
    "DeepSeek": "deepseek-chat"
}
BG_REMOVAL_SERVICES = {
    "Remove.bg": "removebg",
    "Removal.ai": "removelai",
    "Local rembg": "local",
    "Clipdrop": "clipdrop"
}

# Custom CSS for better styling
custom_css = """
.gradio-container {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: #f4f6fb;
    color: #222 !important;
}
.tab-nav {
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
}
.tab-nav button {
    background: transparent !important;
    border: none !important;
    color: #fff !important;
    font-weight: 600 !important;
    font-size: 1.1rem !important;
    text-shadow: 0 1px 2px rgba(0,0,0,0.15);
}
.tab-nav button.selected {
    background: rgba(255,255,255,0.2) !important;
    border-radius: 8px !important;
}
.upload-container {
    border: 2px dashed #667eea;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    color: #222 !important;
    font-size: 1.05rem;
    transition: all 0.3s ease;
}
.upload-container:hover {
    border-color: #764ba2;
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.15);
}
.feature-card {
    background: #fff;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    margin: 10px 0;
    border-left: 4px solid #667eea;
    color: #222 !important;
}
.success-message {
    color: #22c55e;
    font-weight: 600;
    font-size: 1.05rem;
}
.error-message {
    color: #ef4444;
    font-weight: 600;
    font-size: 1.05rem;
}
.gr-textbox label, .gr-dropdown label, .gr-slider label, .gr-number label, .gr-checkbox label {
    color: #222 !important;
    font-weight: 600;
    font-size: 1.05rem;
}
.gr-textbox input, .gr-dropdown select, .gr-slider input, .gr-number input, .gr-checkbox input {
    color: #222 !important;
    background: #f8fafc !important;
    border-radius: 6px !important;
    border: 1px solid #c3cfe2 !important;
    font-size: 1.05rem;
}
.gr-button {
    font-size: 1.08rem !important;
    font-weight: 600 !important;
}
"""

# Android icon sizes (density: size in px)
ANDROID_ICON_SIZES = {
    "mdpi": 48,
    "hdpi": 72,
    "xhdpi": 96,
    "xxhdpi": 144,
    "xxxhdpi": 192,
}

def make_android_icons_zip(image: Image.Image) -> str:
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
        with zipfile.ZipFile(tmp, mode="w") as zf:
            for density, size in ANDROID_ICON_SIZES.items():
                icon = image.resize((size, size), Image.LANCZOS)
                icon_bytes = io.BytesIO()
                icon.save(icon_bytes, format="PNG")
                icon_bytes.seek(0)
                zf.writestr(f"ic_launcher_{density}.png", icon_bytes.read())
        return tmp.name  # Return the file path for gr.File

# Main Gradio Interface
with gr.Blocks(css=custom_css, title="🎨 Advanced Image Processing Suite", theme=gr.themes.Soft()) as demo:
    
    gr.HTML("""
    <div style="text-align: center; padding: 20px; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 12px; margin-bottom: 20px;">
        <h1 style="margin: 0; font-size: 2.5rem; font-weight: 700;">🎨 Advanced Image Processing Suite</h1>
        <p style="margin: 10px 0 0 0; font-size: 1.1rem; opacity: 0.9;">Professional-grade image processing, AI generation, and enhancement tools</p>
    </div>
    """)
    
    with gr.Tabs() as tabs:
        # Tab 1: Format
        with gr.Tab("🖼️ Format", elem_classes="feature-card"):
            gr.Markdown("### Convert images between multiple formats with advanced options")
            
            with gr.Row():
                with gr.Column(scale=1):
                    conv_input = gr.Image(label="📎 Upload Image", type="filepath", elem_classes="upload-container")
                    conv_format = gr.Dropdown(
                        choices=SUPPORTED_FORMATS, 
                        value="PNG", 
                        label="🎯 Target Format"
                    )
                    conv_quality = gr.Slider(
                        minimum=10, maximum=100, value=95, 
                        label="🎛️ Quality (for JPEG/WebP)", step=5
                    )
                    conv_btn = gr.Button("🚀 Convert Image", variant="primary")
                
                with gr.Column(scale=1):
                    conv_output = gr.File(label="📥 Download Converted Image")
                    conv_status = gr.Textbox(label="📊 Status", interactive=False)
            
            conv_btn.click(
                fn=lambda img, fmt, qual: processor.convert_image(img, fmt, qual) if img else (None, "❌ Please upload an image"),
                inputs=[conv_input, conv_format, conv_quality],
                outputs=[conv_output, conv_status]
            )
        
        # Tab 2: AI Gen
        with gr.Tab("🤖 AI Gen", elem_classes="feature-card"):
            gr.Markdown("### Generate stunning images using state-of-the-art AI models")
            
            with gr.Row():
                with gr.Column():
                    gr.Markdown("#### 🔑 API Configuration")
                    openai_key = gr.Textbox(
                        label="OpenAI API Key", 
                        type="password", 
                        placeholder="sk-..."
                    )
                    anthropic_key = gr.Textbox(
                        label="Anthropic API Key", 
                        type="password", 
                        placeholder="sk-ant-..."
                    )
                    deepseek_key = gr.Textbox(
                        label="DeepSeek API Key", 
                        type="password", 
                        placeholder="sk-..."
                    )
                    
                    save_keys_btn = gr.Button("💾 Save API Keys", size="sm")
                    key_status = gr.Textbox(label="🔐 Key Status", interactive=False)
            
            with gr.Row():
                with gr.Column():
                    ai_prompt = gr.Textbox(
                        label="🎨 Image Prompt", 
                        placeholder="A serene landscape with mountains and a lake at sunset...",
                        lines=3
                    )
                    ai_model = gr.Dropdown(
                        choices=list(AI_MODELS.keys()),
                        value="OpenAI DALL-E 3",
                        label="🧠 AI Model"
                    )
                    ai_size = gr.Dropdown(
                        choices=["256x256", "512x512", "1024x1024", "1792x1024", "1024x1792"],
                        value="1024x1024",
                        label="📐 Image Size"
                    )
                    
                    generate_btn = gr.Button("✨ Generate Image", variant="primary")
                
                with gr.Column():
                    ai_output = gr.Image(label="🖼️ Generated Image")
                    ai_status = gr.Textbox(label="📊 Generation Status", interactive=False)
            
            # API key saving (refactored)
            def save_api_keys(openai, anthropic, deepseek):
                ai_generator.openai_key = openai
                ai_generator.anthropic_key = anthropic
                # DeepSeek can be added to ai_generator if implemented
                saved_keys = []
                if openai:
                    saved_keys.append("OpenAI")
                if anthropic:
                    saved_keys.append("Anthropic")
                if deepseek:
                    saved_keys.append("DeepSeek")
                if saved_keys:
                    return f"✅ Saved keys for: {', '.join(saved_keys)}"
                return "❌ No keys provided"

            save_keys_btn.click(
                fn=save_api_keys,
                inputs=[openai_key, anthropic_key, deepseek_key],
                outputs=key_status
            )

            # Image generation (fixed: pass API keys directly)
            def generate_image(prompt, model, size, openai, anthropic):
                if not prompt:
                    return None, "❌ Please enter a prompt"
                if "OpenAI" in model:
                    model_name = AI_MODELS[model]
                    temp_gen = AIImageGenerator(openai_key=openai, anthropic_key=anthropic)
                    return temp_gen.generate_image_openai(prompt, model_name, size)
                elif "Anthropic" in model:
                    temp_gen = AIImageGenerator(openai_key=openai, anthropic_key=anthropic)
                    return temp_gen.generate_image_anthropic(prompt)
                else:
                    return None, f"❌ {model} not yet implemented"

            generate_btn.click(
                fn=generate_image,
                inputs=[ai_prompt, ai_model, ai_size, openai_key, anthropic_key],
                outputs=[ai_output, ai_status]
            )
        
        # Tab 3: Enhance
        with gr.Tab("✨ Enhance", elem_classes="feature-card"):
            gr.Markdown("### Enhance your images with professional-grade filters and AI")
            
            with gr.Row():
                with gr.Column():
                    enhance_input = gr.Image(label="📎 Upload Image to Enhance", type="filepath")
                    enhance_type = gr.Dropdown(
                        choices=ENHANCEMENT_OPTIONS,
                        value="Color Enhancement",
                        label="🎭 Enhancement Type"
                    )
                    enhance_intensity = gr.Slider(
                        minimum=0.1, maximum=2.0, value=1.0, step=0.1,
                        label="🎛️ Enhancement Intensity"
                    )
                    enhance_btn = gr.Button("🚀 Enhance Image", variant="primary")
                
                with gr.Column():
                    enhance_output = gr.Image(label="✨ Enhanced Image")
                    enhance_status = gr.Textbox(label="📊 Enhancement Status", interactive=False)
            
            enhance_btn.click(
                fn=lambda img, enh_type, intensity: processor.enhance_image(img, enh_type, intensity) if img else (None, "❌ Please upload an image"),
                inputs=[enhance_input, enhance_type, enhance_intensity],
                outputs=[enhance_output, enhance_status]
            )
        
        # Tab 4: BG Remove
        with gr.Tab("🎭 BG Remove", elem_classes="feature-card"):
            gr.Markdown("### Remove backgrounds instantly with AI-powered tools")
            
            with gr.Row():
                with gr.Column():
                    gr.Markdown("#### 🔑 API Keys for Premium Services")
                    removebg_key = gr.Textbox(
                        label="Remove.bg API Key", 
                        type="password", 
                        placeholder="Your Remove.bg API key"
                    )
                    save_bg_key_btn = gr.Button("💾 Save Remove.bg Key", size="sm")
                    bg_key_status = gr.Textbox(label="🔐 API Status", interactive=False)
            
            with gr.Row():
                with gr.Column():
                    bg_input = gr.Image(label="📎 Upload Image", type="filepath")
                    bg_service = gr.Dropdown(
                        choices=list(BG_REMOVAL_SERVICES.keys()),
                        value="Local rembg",
                        label="🛠️ Background Removal Service"
                    )
                    bg_btn = gr.Button("🎭 Remove Background", variant="primary")
                
                with gr.Column():
                    bg_output = gr.Image(label="🖼️ Result (Transparent Background)")
                    bg_status = gr.Textbox(label="📊 Processing Status", interactive=False)
            
            # Save background removal API key (refactored)
            def save_bg_api_key(key):
                bg_remover.removebg_key = key
                if key:
                    return "✅ Remove.bg API key saved"
                return "❌ No key provided"
            save_bg_key_btn.click(
                fn=save_bg_api_key,
                inputs=removebg_key,
                outputs=bg_key_status
            )
            # Background removal (fixed: pass Remove.bg key directly)
            def remove_bg(img, service, removebg):
                if not img:
                    return None, "❌ Please upload an image"
                service_key = BG_REMOVAL_SERVICES.get(service, "local")
                if service_key == "local":
                    return bg_remover.remove_local(img)
                elif service_key == "removebg":
                    temp_remover = BackgroundRemover(removebg_key=removebg)
                    return temp_remover.remove_with_removebg(img)
                else:
                    return None, f"❌ {service} not implemented"
            bg_btn.click(
                fn=remove_bg,
                inputs=[bg_input, bg_service, removebg_key],
                outputs=[bg_output, bg_status]
            )
        
        # Tab 5: Batch
        with gr.Tab("📦 Batch", elem_classes="feature-card"):
            gr.Markdown("### Process multiple images simultaneously")
            
            with gr.Row():
                with gr.Column():
                    batch_files = gr.Files(label="📎 Upload Multiple Images", file_types=["image"])
                    batch_operation = gr.Dropdown(
                        choices=["Format Conversion", "Enhancement", "Background Removal"],
                        value="Format Conversion",
                        label="🔧 Batch Operation"
                    )
                    batch_btn = gr.Button("🚀 Process Batch", variant="primary")
                
                with gr.Column():
                    batch_output = gr.Files(label="📥 Download Processed Images")
                    batch_status = gr.Textbox(label="📊 Batch Status", interactive=False, lines=5)
            
            # Batch processing (refactored)
            def process_batch(files, operation):
                if not files:
                    return None, "❌ Please upload images for batch processing"
                results = []
                status_messages = []
                for i, file in enumerate(files):
                    try:
                        if operation == "Format Conversion":
                            result, msg = processor.convert_image(file.name, "PNG")
                        elif operation == "Enhancement":
                            result, msg = processor.enhance_image(file.name, "Color Enhancement")
                        elif operation == "Background Removal":
                            result, msg = bg_remover.remove_local(file.name)
                        if result:
                            results.append(result)
                        status_messages.append(f"File {i+1}: {msg}")
                    except Exception as e:
                        status_messages.append(f"File {i+1}: ❌ Error - {str(e)}")
                return results if results else None, "\n".join(status_messages)
            batch_btn.click(
                fn=process_batch,
                inputs=[batch_files, batch_operation],
                outputs=[batch_output, batch_status]
            )
        
        # Tab 6: Tools
        with gr.Tab("🔬 Tools", elem_classes="feature-card"):
            gr.Markdown("### Professional image analysis and specialized processing")
            
            with gr.Tabs():
                with gr.Tab("🔍 Image Analysis"):
                    with gr.Row():
                        with gr.Column():
                            analysis_input = gr.Image(label="📎 Upload Image for Analysis", type="filepath")
                            analysis_btn = gr.Button("🔬 Analyze Image", variant="primary")
                        
                        with gr.Column():
                            analysis_output = gr.JSON(label="📊 Image Analysis Results")
                    
                    # Advanced Tools: Image Analysis (refactored)
                    def analyze_image(img_path):
                        return ImageAnalysis.analyze_image(img_path)
                    analysis_btn.click(
                        fn=analyze_image,
                        inputs=analysis_input,
                        outputs=analysis_output
                    )
                
                with gr.Tab("🎨 Custom Filters"):
                    with gr.Row():
                        with gr.Column():
                            filter_input = gr.Image(label="📎 Upload Image", type="filepath")
                            
                            # Custom filter controls
                            brightness = gr.Slider(-100, 100, 0, label="☀️ Brightness")
                            contrast = gr.Slider(-100, 100, 0, label="🌓 Contrast")
                            saturation = gr.Slider(-100, 100, 0, label="🎨 Saturation")
                            hue_shift = gr.Slider(-180, 180, 0, label="🌈 Hue Shift")
                            
                            apply_filter_btn = gr.Button("🎭 Apply Custom Filter", variant="primary")
                        
                        with gr.Column():
                            filter_output = gr.Image(label="🖼️ Filtered Image")
                            filter_status = gr.Textbox(label="📊 Filter Status", interactive=False)
                    
                    # Advanced Tools: Custom Filters (refactored)
                    apply_filter_btn.click(
                        fn=apply_custom_filter,
                        inputs=[filter_input, brightness, contrast, saturation, hue_shift],
                        outputs=[filter_output, filter_status]
                    )
                
                with gr.Tab("📏 Resize & Crop"):
                    with gr.Row():
                        with gr.Column():
                            resize_input = gr.Image(label="📎 Upload Image", type="filepath")
                            
                            resize_mode = gr.Radio(
                                choices=["Resize", "Crop", "Smart Crop", "Canvas Resize"],
                                value="Resize",
                                label="🔧 Operation Mode"
                            )
                            
                            new_width = gr.Number(label="📐 Width", value=800)
                            new_height = gr.Number(label="📐 Height", value=600)
                            
                            maintain_ratio = gr.Checkbox(label="🔒 Maintain Aspect Ratio", value=True)
                            resize_quality = gr.Dropdown(
                                choices=["NEAREST", "LANCZOS", "BILINEAR", "BICUBIC"],
                                value="LANCZOS",
                                label="🎯 Resize Quality"
                            )
                            
                            resize_btn = gr.Button("📏 Process Image", variant="primary")
                        
                        with gr.Column():
                            resize_output = gr.Image(label="🖼️ Processed Image")
                            resize_status = gr.Textbox(label="📊 Processing Status", interactive=False)
                    
                    # Advanced Tools: Resize & Crop (refactored)
                    resize_btn.click(
                        fn=resize_crop_image,
                        inputs=[resize_input, resize_mode, new_width, new_height, maintain_ratio, resize_quality],
                        outputs=[resize_output, resize_status]
                    )
        
        # Tab 7: Android Icons
        with gr.Tab("📱 Android Icons", elem_classes="feature-card"):
            gr.Markdown("### Generate all Android app icon sizes and download as a ZIP")
            android_icon_input = gr.Image(type="pil", label="Android Icon Source")
            android_icon_btn = gr.Button("Generate Android Icons")
            android_icon_zip = gr.File(label="Download Icons ZIP")

            def handle_android_icon(image):
                if image is None:
                    return None
                return make_android_icons_zip(image)

            android_icon_btn.click(
                fn=handle_android_icon,
                inputs=android_icon_input,
                outputs=android_icon_zip
            )
    
    # Footer with additional information
    gr.HTML("""
    <div style="margin-top: 40px; padding: 20px; background: #f8fafc; border-radius: 12px; text-align: center;">
        <h3 style="color: #374151; margin-bottom: 15px;">🚀 Professional Image Processing Suite</h3>
        <div style="display: flex; justify-content: center; gap: 30px; flex-wrap: wrap;">
            <div>
                <strong>📋 Supported Formats:</strong><br>
                JPEG, PNG, BMP, TIFF, WEBP, GIF, ICO, EPS, PDF, PSD, SVG, HEIC, AVIF, JXL
            </div>
            <div>
                <strong>🤖 AI Services:</strong><br>
                OpenAI DALL-E 2/3, Anthropic Claude, DeepSeek, Remove.bg, Clipdrop
            </div>
            <div>
                <strong>✨ Features:</strong><br>
                Format Conversion, AI Generation, Enhancement, Background Removal, Batch Processing
            </div>
        </div>
        <p style="margin-top: 15px; color: #6b7280; font-size: 0.9rem;">
            • Made with ❤️ & Gradio — by Aaron 🚀 • 
        </p>
    </div>
    """)


# Launch configuration
if __name__ == "__main__":
    demo.launch(
        server_name="localhost",
        server_port=7860,
        share=True,
        favicon_path=None,
        pwa=True,
        ssl_verify=False,
        show_api=False
    )