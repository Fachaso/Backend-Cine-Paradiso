import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY") or "clave-local-solo-desarrollo"
    DEBUG = os.getenv("FLASK_ENV", "development") == "development"
