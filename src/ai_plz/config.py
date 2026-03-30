from logging import getLogger
from typing import Any, override

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = getLogger(__name__)


class Config(BaseSettings):
    model_config = SettingsConfigDict(from_attributes=True, env_prefix="AI_PLZ_")

    api_key: SecretStr = Field(
        default=SecretStr(""),
        description="LLM API key (Required)",
    )
    base_url: str | None = Field(
        default=None,
        description="Base URL to LLM API",
    )
    model: str = Field(
        default="",
        description="The LLM model name (Required)",
    )
    max_retries: int = Field(
        default=2,
        description="Max retries",
    )
    auto_run: bool | None = Field(
        ...,
        description="Automatic execution (None for manual confirmation)",
    )

    @override
    def model_post_init(self, context: Any) -> None:
        logger.debug(f"Config loaded: {self!r}")
