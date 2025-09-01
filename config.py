import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for the AI Study Buddy application"""
    
    # Flask Configuration
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-here')
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'demo-mode-no-api-key')
    
    # Database Configuration
    DB_CONFIG = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', ''),
        'database': os.getenv('DB_NAME', 'flashcards_db')
    }
    
    # Application Configuration
    MAX_FLASHCARDS = 10
    MIN_FLASHCARDS = 3
    DEFAULT_FLASHCARDS = 5
    
    # OpenAI Model Configuration
    OPENAI_MODEL = "gpt-3.5-turbo"
    OPENAI_MAX_TOKENS = 1000
    OPENAI_TEMPERATURE = 0.7

