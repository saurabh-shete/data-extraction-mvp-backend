from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Environment setting
    environment: str

    # Server settings
    host: str
    port: int

    # Database settings for local PostgreSQL
    database_url: str = None

    # Supabase settings for production
    database_host: str = None
    database_port: int = None
    database_name: str = None
    database_username: str = None
    database_password: str = None

    # AWS settings (optional)
    aws_access_key_id: str = None
    aws_secret_access_key: str = None
    aws_region: str = None

    # openai key
    openai_api_key: str
    
    # JWT Secret
    jwt_secret: str

    # free ocr api key
    free_ocr_api_key: str
    class Config:
        # Load the .env file from the project root directory
        env_file = ".env"
        env_file_encoding = 'utf-8'

# Create an instance of the settings
settings = Settings()