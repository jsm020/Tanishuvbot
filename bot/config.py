from pydantic import BaseModel
import os

class Settings(BaseModel):
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "7235348439:AAHYlvbJRlu2n8NC2H3XMMIxB4fwEjoQiPc")
    DJANGO_URL: str = os.getenv("DJANGO_URL", "http://127.0.0.1:8000")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

settings = Settings()
