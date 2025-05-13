from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "School Bot API"
    
    # Настройки базы данных
    DATABASE_URL: str = "sqlite+aiosqlite:///./school.db"
    
    # Настройки CORS
    BACKEND_CORS_ORIGINS: list = ["*"]
    
    class Config:
        case_sensitive = True

settings = Settings() 