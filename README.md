# ai_plz

> A simple command-line helper powered by LLM.

## Introduction

`ai_plz` is a minimalist command-line helper that sends your need to LLM,
asks for a shell command, and executes it if permitted. This helper is designed
to be a one-time command generator, not a full AI agent. The command-line
entrypoint of this package is "plz" (short for "please").

## Usage

```shell
# Install
$ uv tool install ai_plz  # or: pipx install ai_plz

# Get help
$ plz --help
Usage: plz [OPTIONS] [USER_INPUT]...

  A simple command-line helper powered by LLM.

Options:
  -e, --env FILE            Path to optional env file
  -y, --run / -n, --no-run  Enable/Disable automatic execution
  -p, --prompt [en|zh]      Select prompt
  -z, --zh                  Shortcut for --prompt=zh
  --show-vars               Show environment vars
  --show-prompt             Show prompt
  --debug                   Enable debug logging
  -h, --help                Show this message and exit

# Example (User inputs will be concatenated by spaces)
$ plz Clear conda cache
Clear the conda cache to free up disk space and remove outdated packages.
>>> conda clean --all
Run the above command? [y/n]:
```

## Configuration

Model settings should be provided through environment variables, which can be
listed by `plz --show-vars`. Usually, you need to specify your own LLM provider
through `AI_PLZ_API_KEY`, `AI_PLZ_BASE_URL`, and `AI_PLZ_MODEL`.

| Variable name      | Type         | Description                                        |
|--------------------|--------------|----------------------------------------------------|
| AI_PLZ_API_KEY     | SecretStr    | LLM API key (Required)                             |
| AI_PLZ_BASE_URL    | str \| None  | Base URL to LLM API                                |
| AI_PLZ_MODEL       | str          | The LLM model name (Required)                      |
| AI_PLZ_MAX_RETRIES | int          | Max retries                                        |
| AI_PLZ_AUTO_RUN    | bool \| None | Automatic execution (None for manual confirmation) |

## Caveats

When permitted, the command provided by LLM will be executed in a shell subprocess.
It is recommended to check the command before execution, so a confirmation
is required by default, as shown in the example usage above.
You can pass the `-y` option to skip confirmation and take your own risk.
You can also pass `-n` to skip execution without ask.
