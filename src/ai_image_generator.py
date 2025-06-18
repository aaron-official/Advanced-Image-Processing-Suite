import requests
import logging
from PIL import Image
import io
from pathlib import Path

class AIImageGenerator:
    def __init__(self, openai_key=None, anthropic_key=None):
        self.openai_key = openai_key
        self.anthropic_key = anthropic_key

    def generate_image_openai(self, prompt, model="dall-e-3", size="1024x1024"):
        if not self.openai_key:
            return None, "❌ OpenAI API key not provided"
        try:
            headers = {
                "Authorization": f"Bearer {self.openai_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": model,
                "prompt": prompt,
                "size": size,
                "n": 1
            }
            response = requests.post(
                "https://api.openai.com/v1/images/generations",
                headers=headers,
                json=data,
                timeout=60
            )
            if response.status_code == 200:
                result = response.json()
                image_url = result["data"][0]["url"]
                img_response = requests.get(image_url)
                img = Image.open(io.BytesIO(img_response.content))
                output_path = f"generated_image_{hash(prompt) % 10000}.png"
                img.save(output_path)
                return output_path, f"✅ Image generated successfully with {model}"
            else:
                return None, f"❌ OpenAI API Error: {response.text}"
        except Exception as e:
            logging.exception("OpenAI image generation failed")
            return None, f"❌ Error generating image: {str(e)}"

    def generate_image_anthropic(self, prompt):
        if not self.anthropic_key:
            return None, "❌ Anthropic API key not provided"
        try:
            headers = {
                "x-api-key": self.anthropic_key,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            }
            data = {
                "model": "claude-3-5-sonnet-20241022",
                "max_tokens": 1024,
                "messages": [{
                    "role": "user",
                    "content": f"Create a detailed visual description for an AI image generator based on this prompt: {prompt}. Make it artistic and detailed."
                }]
            }
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=data,
                timeout=30
            )
            if response.status_code == 200:
                result = response.json()
                enhanced_prompt = result["content"][0]["text"]
                return None, f"✅ Enhanced prompt created: {enhanced_prompt[:200]}..."
            else:
                return None, f"❌ Anthropic API Error: {response.text}"
        except Exception as e:
            logging.exception("Anthropic image generation failed")
            return None, f"❌ Error with Anthropic API: {str(e)}"
