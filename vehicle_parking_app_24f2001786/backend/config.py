import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

class Config:
    """Base configuration."""
    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    RESTX_MASK_SWAGGER = False
    
    # --- Base JWT Configuration ---
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    JWT_TOKEN_LOCATION = ["headers", "cookies"]
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)
    JWT_COOKIE_CSRF_PROTECT = True

    SMTP_SERVER_HOST = os.getenv("SMTP_SERVER_HOST", "localhost")
    SMTP_SERVER_PORT = int(os.getenv("SMTP_SERVER_PORT", 1025))
    SMTP_USERNAME = os.getenv("SMTP_USERNAME")
    SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
    SENDER_ADDRESS = os.getenv("SENDER_ADDRESS")

class LocalDevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    JWT_COOKIE_SECURE = False 
