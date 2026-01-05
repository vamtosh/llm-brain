"""Configuration for the Brainstorming Partner."""

import os
from dotenv import load_dotenv

load_dotenv()

# OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Primary model for brainstorming
PRIMARY_MODEL = "gpt-4o"

# Alternative models for multi-perspective brainstorming (optional)
# You can add more models here for richer brainstorming sessions
BRAINSTORM_MODELS = [
    "gpt-4o",
    "gpt-4o-mini",
]

# Data directory for conversation storage
DATA_DIR = "data/conversations"
