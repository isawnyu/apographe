#
# This file is part of apographe
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2022 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
Command-line interface for apographe
"""

from airtight.cli import configure_commandline
from apographe.interpreter import Interpreter, InvalidCommandError, UsageError
import logging
from pyfiglet import Figlet
from rich.console import Console


logger = logging.getLogger(__name__)

DEFAULT_LOG_LEVEL = logging.WARNING
OPTIONAL_ARGUMENTS = [
    [
        "-l",
        "--loglevel",
        "NOTSET",
        "desired logging level ("
        + "case-insensitive string: DEBUG, INFO, WARNING, or ERROR",
        False,
    ],
    ["-v", "--verbose", False, "verbose output (logging level == INFO)", False],
    [
        "-w",
        "--veryverbose",
        False,
        "very verbose output (logging level == DEBUG)",
        False,
    ],
    ["-c", "--config", "NOTSET", "path to config file if other than default", False],
    [
        "-s",
        "--scan",
        False,
        "scan all project root trees for projects and tasks",
        False,
    ],
]
POSITIONAL_ARGUMENTS = [
    # each row is a list with 3 elements: name, type, help
]


def interact(config_path, scan):
    c = Console(record=True)
    f = Figlet()
    # c.print("[bold]Apographe[/bold]")
    c.print("[bold blue]" + f.renderText("Apographe") + "[/bold blue]")
    i = Interpreter()
    c.print(i._cmd_gazetteers())
    c.print("[italic blue]type 'help' for a list of commands[/italic blue]")
    while (
        True
    ):  # keep taking commands until something breaks us out to finish the program
        try:
            s = c.input("[bold blue]> [/bold blue]")
        except KeyboardInterrupt:
            r = i.execute("quit")
        else:
            try:
                r = i.execute(s)
            except InvalidCommandError as err:
                c.print(f"[orange][bold]INVALID COMMAND: [/bold]{str(err)}[/orange]")
            except UsageError as err:
                c.print(
                    f"[orange][bold]COMMAND USAGE ERROR: [/bold]{str(err)}[/orange]"
                )
            else:
                c.print(r)


def main(**kwargs):
    """
    main function
    """
    # logger = logging.getLogger(sys._getframe().f_code.co_name)
    config_path = kwargs["config"]
    if config_path == "NOTSET":
        config_path = None
    interact(config_path=config_path, scan=kwargs["scan"])


if __name__ == "__main__":
    main(
        **configure_commandline(
            OPTIONAL_ARGUMENTS, POSITIONAL_ARGUMENTS, DEFAULT_LOG_LEVEL
        )
    )
