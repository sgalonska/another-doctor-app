from typing import Any, Dict, List, Optional, Union
from pydantic import AnyHttpUrl, field_validator, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "your-secret-key-change-this"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = "another_doctor"
    SQLALCHEMY_DATABASE_URI: Optional[str] = None

    @field_validator("SQLALCHEMY_DATABASE_URI", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], info) -> Any:
        if isinstance(v, str):
            return v
        values = info.data if hasattr(info, 'data') else {}
        return f"postgresql+psycopg://{values.get('POSTGRES_USER')}:{values.get('POSTGRES_PASSWORD')}@{values.get('POSTGRES_SERVER')}/{values.get('POSTGRES_DB')}"

    # Redis/Queue
    REDIS_URL: str = "redis://localhost:6379"
    
    # Qdrant Vector DB
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: Optional[str] = None
    
    # Google Cloud Storage
    GCS_BUCKET_NAME: str = "another-doctor-uploads"
    GCP_PROJECT_ID: str = ""
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None
    
    # Google Cloud Tasks
    GCP_LOCATION: str = "us-central1"
    GCP_TASK_QUEUE_NAME: str = "diagnosis-processing"
    
    # Environment settings
    ENVIRONMENT: str = "development"  # development, staging, production
    
    # Stripe
    STRIPE_PUBLIC_KEY: str = ""
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    
    # External APIs
    PUBMED_API_KEY: Optional[str] = None
    CROSSREF_EMAIL: str = "your-email@domain.com"
    
    # CORS  
    _BACKEND_CORS_ORIGINS: str = "http://localhost:3000"
    
    @property
    def BACKEND_CORS_ORIGINS(self) -> List[str]:
        import os
        cors_env = os.getenv("BACKEND_CORS_ORIGINS", self._BACKEND_CORS_ORIGINS)
        if isinstance(cors_env, str):
            return [origin.strip() for origin in cors_env.split(",") if origin.strip()]
        return ["http://localhost:3000"]

    # Security
    _ALLOWED_HOSTS: str = "localhost,127.0.0.1"
    
    @property
    def ALLOWED_HOSTS(self) -> List[str]:
        import os
        hosts_env = os.getenv("ALLOWED_HOSTS", self._ALLOWED_HOSTS)
        if isinstance(hosts_env, str):
            return [host.strip() for host in hosts_env.split(",") if host.strip()]
        return ["localhost", "127.0.0.1"]
    
    # Environment
    ENVIRONMENT: str = "development"

    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=".env"
    )

settings = Settings()