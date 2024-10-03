# app/config/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Add environment setting
    environment: str
    
    # Server settings
    host: str
    port: int

    # Database settings
    database_url: str

    # AWS settings
    aws_access_key_id: str = None
    aws_secret_access_key: str = None
    aws_region: str = None

    # JWT Secret
    jwt_secret: str

    class Config:
        # Load the .env file from the project root directory
        env_file = ".env"
        env_file_encoding = 'utf-8'

# Create an instance of the settings
settings = Settings()