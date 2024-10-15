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
    database_host: str
    database_port: int
    database_name: str
    database_username: str
    database_password: str

    # AWS settings (optional)
    aws_access_key_id: str = None
    aws_secret_access_key: str = None
    aws_region: str = None

    # openai key
    openai_api_key: str
    
    # JWT Secret
    jwt_secret: str

    class Config:
        # Load the .env file from the project root directory
        env_file = ".env"
        env_file_encoding = 'utf-8'

# Create an instance of the settings
settings = Settings()