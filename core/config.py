from pydantic_settings import BaseSettings, SettingsConfigDict


class ProjectConfig(BaseSettings):
    salt: str
    user_login_state: str
    db_name: str
    db_user: str
    db_password: str
    db_host: str
    db_port: str
    debug: bool
    secret_key: str
    default_role: int
    admin_role: int

    model_config = SettingsConfigDict(env_file="core/.env")
