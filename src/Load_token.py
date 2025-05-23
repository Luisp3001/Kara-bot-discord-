from dotenv import load_dotenv, dotenv_values
import os
load_dotenv()

def discord():
    discord_token = os.getenv("DISCORD_TOKEN")
    return discord_token

def gemini():
    gemini_token = os.getenv("GENAI_TOKEN")
    return gemini_token