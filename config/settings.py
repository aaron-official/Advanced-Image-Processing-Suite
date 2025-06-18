import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
REMOVE_BG_API_KEY = os.getenv('REMOVE_BG_API_KEY')
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
GRADIO_SERVER_NAME = os.getenv('GRADIO_SERVER_NAME', '0.0.0.0')
GRADIO_SERVER_PORT = int(os.getenv('GRADIO_SERVER_PORT', 7860))
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
