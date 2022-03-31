#
# This file is part of apographe
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2022 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
Provide Interpreter class for scripting apographe
"""
from inspect import getdoc
import logging
from pathlib import Path, PurePath
from pprint import pformat
import re
import readline
from rich.markdown import Markdown
from rich.table import Table
import shlex
import traceback

rx_linestart = re.compile(r"^")


class InvalidCommandError(ValueError):
    def __init__(self, cmd, supported, raw):
        self.message = f"'{cmd}' is not a supported command. Try: {supported}."
        self.raw = raw
        ValueError.__init__(self, self.message)


class UsageError(ValueError):
    def __init__(self, interp, cmd, msg, *args, **kwargs):
        raw = [cmd]
        if args:
            raw.append(" ".join(*args))
        if kwargs:
            raw.append(" ".join([f"k:v" for k, v in kwargs.items()]))
        raw = " ".join(raw)
        self.message = f"'{raw}' is invalid usage for command '{cmd}' because {msg}.\nUsage:\n{self._usage(interp, cmd)}"
        self.raw = raw
        ValueError.__init__(self, self.message)

    def _usage(self, interp, cmd):
        try:
            return "\n".join(getdoc(getattr(interp, f"_cmd_{cmd}")).splitlines[1:])
        except AttributeError:
            return ""


class Interpreter:
    def __init__(self):
        # what?
        self.logger = logging.getLogger(self.__class__.__name__)

    def execute(self, cmd_string: str):
        """Carry out a single-line command."""
        if isinstance(cmd_string, str):
            cmd = self._parse(cmd_string)
        else:
            raise TypeError(f"cmd_string: {type(cmd_string)}. Expected {str}.")
        try:
            result = getattr(self, f"_cmd_{cmd[0]}")(*cmd[1], **cmd[2])
        except AttributeError as err:
            tb = traceback.format_exception(err)
            self.logger.error(f".execute:\n{''.join(tb)}")
            raise InvalidCommandError(cmd[0], self.supported_commands, raw=cmd_string)
        return result

    @property
    def supported_commands(self):
        logger = logging.getLogger(self.__class__.__name__ + ".supported_commands")
        return [m[5:] for m in dir(self) if m.startswith("_cmd_")]

    def _cmd_help(self, *args, **kwargs):
        """List available commands with descriptions extracted from corresponding method docstrings."""
        commands = self.supported_commands
        table = self._rich_table(
            title="Supported Commands",
            columns=(("Command", {}), ("Description", {})),
            rows=[
                (c, getdoc(getattr(self, f"_cmd_{c}")).splitlines()[0])
                for c in commands
            ],
        )
        return table

    def _cmd_quit(self, *args, **kwargs):
        """Quit the program."""
        exit()

    def _parse(self, cmd_string: str):
        """Parse a single-line command from cmd_string."""
        parts = [p for p in shlex.split(cmd_string) if p]
        cmd = parts[0]
        args = parts[1:]
        raw_kwargs = [a for a in args if ":" in a and " " not in a]
        args = [a for a in args if a not in raw_kwargs]
        raw_kwargs = [a.split(":") for a in raw_kwargs]
        kwargs = {a[0]: a[1] for a in raw_kwargs}
        return (cmd, args, kwargs)

    def _rich_table(self, title, columns, rows):
        """Structure a rich table for output."""
        table = Table(
            title=title,
            row_styles=["blue", ""],
            title_justify="left",
            title_style="bold",
        )
        for column in columns:
            table.add_column(column[0], **column[1])
        for row in rows:
            table.add_row(*row)
        return table

    def _usage(self, cmd):
        """Extract cmd usage information from method docstring."""
        doc = getdoc(getattr(self, f"_cmd_{cmd}"))
        return "\n".join(doc.splitlines()[1:])
