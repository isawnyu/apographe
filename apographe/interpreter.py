#
# This file is part of apographe
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2022 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
Provide Interpreter class for scripting apographe
"""
from apographe.idai import IDAI, IDAIQuery
from apographe.pleiades import Pleiades, PleiadesQuery
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
        self._gazetteers = {
            "idai": (IDAI(), IDAIQuery),
            "pleiades": (Pleiades(), PleiadesQuery),
        }
        self._search_results = dict()
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

    def _cmd_gazetteers(self, *args, **kwargs):
        """List supported gazetteers."""
        gazetteer_names = sorted(list(self._gazetteers.keys()))
        rows = list()
        for gn in gazetteer_names:
            desc = getdoc(self._gazetteers[gn][0])
            desc = desc.replace("Interface for the ", "")
            if desc[-1] == ".":
                desc = desc[:-1]
            rows.append((gn, desc))
        return self._rich_table(
            title="Supported gazetteers",
            columns=(("name", {}), ("description", {})),
            rows=rows,
        )

    def _cmd_help(self, *args, **kwargs):
        """List available commands."""
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

    def _cmd_search(self, *args, **kwargs):
        """
        Search a gazetteer.
            > search pleiades title:Zucchabar
            > search pleiades Zucchabar
              (searches all available text fields in the gazetteer for "Zucchabar")
            > search results
              (list all results from searches so far in this session)
        """
        gazetteer_name = args[0].lower()
        if gazetteer_name == "results":
            return self._search_result_table()
        gazetteer_interface, gazetteer_query_class = self._invoke_gazetteer(
            gazetteer_name, "search"
        )
        query = gazetteer_query_class()
        if len(args) > 1:
            query.set_parameter("text", list(args[1:]))
        for name, value in kwargs.items():
            query.set_parameter(name, value)
        results = gazetteer_interface.search(query)
        if results["hits"]:
            try:
                self._search_results[gazetteer_name]
            except KeyError:
                self._search_results[gazetteer_name] = dict()
            finally:
                memcache = self._search_results[gazetteer_name]
            for hit in results["hits"]:
                memcache[hit["id"]] = hit
        return self._rich_table(
            title=f"{gazetteer_name.title()} search results",
            columns=(("ID", {}), ("Summary", {})),
            rows=[
                (
                    f"[bold]{h['id']}[/bold]",
                    f"[bold]{h['title']}[/bold]\n{h['uri']}\n{h['summary']}",
                )
                for h in results["hits"]
            ],
        )

    def _invoke_gazetteer(self, gazetteer_name: str, cmd_name: str):
        """Retrieve appropriate gazetteer interface (initialize if necessary)"""
        try:
            gaz_info = self._gazetteers[gazetteer_name]
        except KeyError:
            gazetteers = " ".join(list(self._gazetteers.keys()))
            msg = f"Could not invoke gazetteer named '{gazetteer_name}'. Expected one of: {gazetteers.sort()}"
            raise UsageError(self, cmd_name, msg)
        return gaz_info

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

    def _search_result_table(self):
        """Structure a rich table of all search results in the memcache"""
        rows = list()
        gazetteer_names = sorted(list(self._search_results.keys()))
        for gazetteer_name in gazetteer_names:
            ids = sorted(
                [int(id) for id in list(self._search_results[gazetteer_name].keys())]
            )
            for id in ids:
                hit = self._search_results[gazetteer_name][str(id)]
                rows.append(
                    (
                        f"[bold]{gazetteer_name} {hit['id']}[/bold]",
                        f"[bold]{hit['title']}[/bold]\n{hit['uri']}\n{hit['summary']}",
                    )
                )
        return self._rich_table(
            title=f"All search results",
            columns=(("gazetteer ID", {}), ("Summary", {})),
            rows=rows,
        )

    def _usage(self, cmd):
        """Extract cmd usage information from method docstring."""
        doc = getdoc(getattr(self, f"_cmd_{cmd}"))
        return "\n".join(doc.splitlines()[1:])
