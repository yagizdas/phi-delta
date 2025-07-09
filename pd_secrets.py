from dotenv import load_dotenv
import os

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
WOLFRAM_ALPHA_APPID = os.getenv("WOLFRAM_ALPHA_APPID")
