from logging import getLogger
from typing import Any, Self, override

from pydantic import Field, SecretStr, model_validator
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

    @model_validator(mode="after")
    def validate_required_fields(self) -> Self:
        missing_fields = set(
            field_name
            for field_name in ("api_key", "model")
            if not getattr(self, field_name)
        )
        if len(missing_fields) > 0:
            fields_str = ", ".join(missing_fields)
            vars_str = ", ".join(map(self.get_env_var_name, missing_fields))
            base_url_str = self.get_env_var_name("base_url")
            raise RuntimeError(
                f"The following config items are required but not set: {fields_str}. "
                f"You should provide the following environment variables for them: {vars_str}. "
                f"You may also specify the base URL for LLM API through {base_url_str}."
            )
        return self

    @classmethod
    def get_env_var_name(cls, field_name: str) -> str:
        return cls.model_config.get("env_prefix", "") + field_name.upper()
