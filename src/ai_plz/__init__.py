import logging

import click
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import ValidationError

from .config import Config
from .prompt import prompt_map
from .reply import ModelReply

logger = logging.getLogger(__name__)


@click.command()
@click.option(
    "env_path",
    "--env",
    "-e",
    type=click.Path(exists=True, dir_okay=False),
    help="Path to optional env file",
)
@click.option(
    "auto_run",
    "--run/--no-run",
    "-y/-n",
    help="Enable/Disable automatic execution",
    default=None,
)
@click.option(
    "prompt_key",
    "--prompt",
    "-p",
    type=click.Choice(prompt_map.keys()),
    help="Select prompt",
    default="en",
)
@click.option(
    "prompt_key", "--zh", "-z", flag_value="zh", help="Shortcut for --prompt=zh"
)
@click.option("--show-vars", is_flag=True, help="Show environment vars")
@click.option("--show-prompt", is_flag=True, help="Show prompt")
@click.option("--debug", is_flag=True, help="Enable debug logging")
@click.help_option("--help", "-h", help="Show this message and exit")
@click.argument("user_input", nargs=-1)
def main(
    env_path: str | None,
    auto_run: bool | None,
    prompt_key: str,
    show_vars: bool,
    show_prompt: bool,
    debug: bool,
    user_input: list[str],
) -> None:
    """A simple command-line helper powered by LLM."""

    # Setup logging
    logging.basicConfig(
        format="[%(asctime)s] %(levelname)s (%(name)s) %(message)s",
        level=(logging.DEBUG if debug else logging.WARNING),
    )

    # Show env vars when requested
    if show_vars:
        print("Recognizable environment variables:")
        env_prefix = Config.model_config.get("env_prefix", "")
        for key, field in Config.model_fields.items():
            var_name = env_prefix + key.upper()
            field_type = field.annotation
            if isinstance(field_type, type):
                type_name = field_type.__name__
            else:
                type_name = str(field_type)
            description = field.description or ""
            print(f"- {var_name} ({type_name}): {description}")
        return

    # Load prompt
    prompt = prompt_map[prompt_key]
    logger.debug(f"prompt={prompt!r}")
    if show_prompt:
        print(prompt)
        return

    # Load config
    if env_path is not None:
        load_dotenv(env_path)
    config = Config(auto_run=auto_run)

    # Create AI completion
    client = OpenAI(
        api_key=config.api_key.get_secret_value(),
        base_url=config.base_url,
        max_retries=config.max_retries,
    )
    completion = client.chat.completions.create(
        model=config.model,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": " ".join(user_input)},
        ],
        response_format={"type": "json_object"},
        temperature=0.1,
    )
    logger.debug(f"{completion=!r}")

    # Check message availability
    message = completion.choices[0].message
    if message.refusal:
        raise RuntimeError(f"Model refusal: {message.refusal}")
    if message.content is None:
        raise RuntimeError("Model completion unavailable")

    # Parse model reply
    try:
        reply = ModelReply.model_validate_json(message.content)
    except ValidationError as error:
        raise RuntimeError(f"Invalid model reply: {message.content!r}") from error
    logger.debug(f"{reply=!r}")

    # Execute
    reply.action.execute(config=config)
