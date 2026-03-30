import sys
from abc import ABC, abstractmethod
from subprocess import run
from typing import override

import click
from pydantic import BaseModel, ConfigDict

from .config import Config


class ActionBase(BaseModel, ABC):
    model_config = ConfigDict(frozen=True)

    explanation: str

    @abstractmethod
    def execute(self, *, config: Config) -> None: ...


class CommandAction(ActionBase):
    argv: list[str]

    @override
    def execute(self, *, config: Config) -> None:
        # Command display
        print(self.explanation)
        print(">>>", " ".join(self.argv))
        # Confirmation
        match config.auto_run:
            case False:
                print("(Command not run. Execute it manually if wanted.)")
                return
            case True:
                pass
            case None:
                click.confirm("Run the above command?", default=None, abort=True)
        # Execution
        run(
            self.argv,
            shell=True,
            check=True,
            stdout=sys.stdout,
            stderr=sys.stderr,
        )


class ModelReply(BaseModel):
    model_config = ConfigDict(frozen=True)

    action: CommandAction
