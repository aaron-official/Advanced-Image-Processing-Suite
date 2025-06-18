import logging
import os

def setup_logging():
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        handlers=[logging.StreamHandler()]
    )
    logging.getLogger('PIL').setLevel(logging.WARNING)
    logging.getLogger('gradio').setLevel(logging.WARNING)

setup_logging()
