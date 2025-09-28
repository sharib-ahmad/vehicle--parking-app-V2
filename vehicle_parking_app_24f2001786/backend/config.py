import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

class Config:
    """Base configuration."""
    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    RESTX_MASK_SWAGGER = False

class LocalDevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

    # --- JWT Configuration ---
    JWT_TOKEN_LOCATION = ["headers", "cookies"]
    JWT_COOKIE_SECURE = False 
    JWT_COOKIE_CSRF_PROTECT = True 
    
    # Access token is valid for 15 minutes.
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
    
    # Refresh token allows for re-authentication for up to 7 days.
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)

