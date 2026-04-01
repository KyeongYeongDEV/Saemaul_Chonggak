from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # DB
    DATABASE_URL: str = "mysql+aiomysql://root:password@localhost:3306/saemaul"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT
    JWT_SECRET_KEY: str = "change-me"
    JWT_ACCESS_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_EXPIRE_DAYS: int = 7

    # 토스페이먼츠
    TOSS_SECRET_KEY: str = "test_sk_xxxxx"
    TOSS_CLIENT_KEY: str = "test_ck_xxxxx"

    # AWS S3
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_S3_BUCKET: str = "saemaul-bucket"
    AWS_REGION: str = "ap-northeast-2"

    # FCM
    FCM_CREDENTIALS_PATH: str = "firebase-credentials.json"

    # 환경
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    ALLOWED_ORIGINS: str = "http://localhost:3000"


settings = Settings()
