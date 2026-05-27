import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Telegram
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    ADMIN_ID = int(os.getenv("ADMIN_ID", 0))

    # Groq AI
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GROQ_MODEL = "llama-3.1-8b-instant"

    # Agent Personality
    COMPANY_NAME = "TechAura"
    AGENT_NAME = "BookEase AI Agent"
    SERVICES = [
        "Web Development",
        "Mobile App",
        "AI Agent Development",
        "AI Chatbot",
        "Other"
    ]
    FOLLOWUP_HOURS = 24

    # Conversation settings
    MAX_REQUIREMENT_LENGTH = 500
