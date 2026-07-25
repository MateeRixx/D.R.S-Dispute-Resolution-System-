from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/drs"
    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiry_minutes: int = 60
    cors_origins: str = ""

    razorpay_webhook_secret: str = ""
    shiprocket_webhook_secret: str = ""

    aws_s3_bucket: str = ""
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    gemini_api_key: str = ""
    groq_api_key: str = ""

    resend_api_key: str = ""
    resend_from_email: str = "onboarding@resend.dev"
    frontend_url: str = "http://localhost:5173"
    webhook_secret: str = ""

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
