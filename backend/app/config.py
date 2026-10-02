from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "mysql+pymysql://root:password@localhost:3306/geofencing"
    gps_accuracy_buffer_meters: float = 15.0
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
