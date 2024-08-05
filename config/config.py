from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """
    Class responsible for parsing environment variables.
    Default looks for .env.development at the root of the project.
    Can be overridden by instantiating the class with a different env_file through _env_file parameter.
    Environment variables take priority over the .env files.
    """
    model_config = SettingsConfigDict(env_file='.env.development')

    POSTGRES_HOST: str
    POSTGRES_PORT: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    ECHO_POSTGRES: bool
    UBERSUGGEST_EMAILS: str
    UBERSUGGEST_PASSWORDS: str
