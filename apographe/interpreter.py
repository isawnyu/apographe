#
# This file is part of apographe
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2022 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
Provide Interpreter class for scripting apographe
"""
from curses.ascii import US
from apographe.linked_places_format import dumps
from apographe.manager import Manager
from inspect import getdoc
import logging
from pprint import pformat
import re
import readline
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
            raw.append(" ".join(args))
        if kwargs:
            raw.append(" ".join([f"{k}:{v}" for k, v in kwargs.items()]))
        raw = " ".join(raw)
        full_msg = f"'{raw}' is invalid usage for command '{cmd}' because {msg}.\nUsage:\n{self._usage(interp, cmd)}"
        full_msg = full_msg.replace("..", ".")
        self.message = full_msg
        self.raw = raw
        ValueError.__init__(self, self.message)

    def _usage(self, interp, cmd):
        try:
            return "\n".join(getdoc(getattr(interp, f"_cmd_{cmd}")).splitlines()[1:])
        except AttributeError:
            return ""


class Interpreter:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.manager = Manager()

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

    def _cmd_accession(self, *args, **kwargs):
        """
        Collect a place from a gazetteer and convert/copy it to the internal gazetteer.
            > accession pleiades 295374
        """
        if len(args) != 2:
            raise UsageError(
                self,
                "accession",
                f"Expected two arguments, but got {len(args)}",
                args,
            )
        try:
            hit = self.manager.accession(*args)
        except RuntimeError as err:
            return str(err)
        return self._rich_table(
            title="Accessioned place",
            columns=(("place key", {}), ("place", {})),
            rows=[
                (
                    f"[bold]{hit['place_key']}[/bold]",
                    f"[bold]{hit['title']}[/bold]\n{hit['uri']}\n{hit['summary']}",
                )
            ],
        )

    def _cmd_change(self, *args, **kwargs):
        """
        Change the value of a field of a place in the internal gazetteer
            > change {id} {fieldname}:{new value}
            > change miliana id:zucchabar
            > change miliana title:Zucchabar
        """
        if len(args) != 1 or not kwargs:
            raise UsageError(
                self,
                "change",
                (
                    "Expected one positional argument (id of place to change) and at least one keyword "
                    f"argument pair (target fieldname and new value), but got {len(args)} positional "
                    f"arguments and {len(kwargs)} keyword arguments."
                ),
            )
        self.logger.debug(f"args: {args}")
        self.logger.debug(pformat(kwargs, indent=4))
        return self.manager.change(place_id=args[0], **kwargs)

    def _cmd_full(self, *args, **kwargs):
        """
        Show full information about a place in the internal gazetteer.
            > full pleiades:295374
              (assumes a place with place key 'pleiades:295374' is already in the internal gazetteer)
        """
        if len(kwargs) == 1 and not args:
            # colon in the place key
            k = list(kwargs.keys())[0]
            place_key = f"{k}:{kwargs[k]}"
        elif len(args) == 1:
            place_key = args[0]
        else:
            raise UsageError(
                self,
                "full",
                f"Expected one argument (the place key), but got {len(args)} positional arguments and {len(kwargs)} keyword arguments.",
                *args,
                **kwargs,
            )
        try:
            place = self.manager.get_place(place_key)
        except ValueError as err:
            raise UsageError(
                self,
                "full",
                f"the id '{place_key}' is not in the internal gazetteer.",
                *args,
                **kwargs,
            )
        return dumps(place, ensure_ascii=False, indent=4, sort_keys=True)

    def _cmd_gazetteers(self, *args, **kwargs):
        """List supported gazetteers."""
        return self._rich_table(
            title="Supported gazetteers",
            columns=(("name", {}), ("description", {})),
            rows=self.manager.supported_gazetteers,
        )

    def _cmd_help(self, *args, **kwargs):
        """
        List available commands or get help with using an individual command.
            > help
            > help search
        """
        if args:
            return self._usage(args[0])
        commands = self.supported_commands
        table = self._rich_table(
            title="Supported commands",
            columns=(("Command", {}), ("Description", {})),
            rows=[
                (c, getdoc(getattr(self, f"_cmd_{c}")).splitlines()[0])
                for c in commands
            ],
        )
        return table

    def _cmd_import(self, *args, **kwargs):
        if len(args) != 1 or len(kwargs) != 1:
            raise UsageError(
                self,
                "import",
                f"Expected one argument (file path) and one keyword argument (filetype:) specifying the type of file, "
                f"but got {len(args)} arguments and {len(kwargs)} keyword arguments.",
                *args,
                **kwargs,
            )
        try:
            kwargs["filetype"]
        except KeyError:
            raise UsageError(
                self,
                "import",
                "Expected a keyword argument 'filetype' indicating the type of file, but "
                f"got {pformat(list(kwargs.keys()))}",
                *args,
                **kwargs,
            )
        filepath = args[0]
        return self.manager.import_file(filepath, **kwargs)

    def _cmd_internal(self, *args, **kwargs):
        """
        List all places in the internal gazetteer.
        """
        table = self._rich_table(
            title="Contents of the internal gazetteer",
            columns=(("place key", {}), ("place", {})),
            rows=[
                (
                    f"[bold]{hit['place_key']}[/bold]",
                    f"[bold]{hit['title']}[/bold]\n{hit['uri']}\n{hit['summary']}",
                )
                for hit in self.manager.internal()
            ],
        )
        return table

    def _cmd_load(self, *args, **kwargs):
        """
        Load LPF JSON files on the local filesystem into the internal gazetteer.
            > load /where/there/mygazetteer
            > load ~/gazetteers/thisgazetteer
        """
        if len(args) != 1:
            raise UsageError(
                self,
                "load",
                f"Expected one argument for the directory pathname to use in load the internal gazetteer, but instead got {len(args)} arguments.",
            )
        return self.manager.load(args[0])

    def _cmd_quit(self, *args, **kwargs):
        """Quit the program."""
        exit()

    def _cmd_save(self, *args, **kwargs):
        """
        Save the contents of the internal gazetteer to the local filesystem.
            > save all /where/there/mygazetteer
              (saves all places to a single file named "all.json" in the "mygazetteer" directory)
            > save all /where/there/mygazetteer.json
              (saves all places to a single file named "mygazetteer.json" in the "there" directory)
            > save each ~/gazetteers/thisgazetteer
              (saves each place to a separate json file in the "thisgazetteer" directory)
        """
        if len(args) > 2:
            raise UsageError(
                self,
                "save",
                f"Expected no more than two arguments to use in saving the internal gazetteer, but instead got {len(args)} arguments.",
            )
        return self.manager.save(*args)

    def _cmd_search(self, *args, **kwargs):
        """
        Search a gazetteer.
            > search pleiades title:Zucchabar
            > search pleiades Zucchabar
              (searches all available text fields in the gazetteer for "Zucchabar")
            > search results
              (list all results from searches so far in this session)
        """
        if not args:
            raise UsageError(self, "search", "A gazetteer name is required.")
        gazetteer_name = args[0].lower()
        if gazetteer_name == "results":
            return self._search_result_table()
        try:
            hits = self.manager.search(gazetteer_name, *args, **kwargs)
        except ValueError as err:
            raise UsageError(self, "search", str(err))
        return self._rich_table(
            title=f"{gazetteer_name.title()} search results",
            columns=(("ID", {}), ("Summary", {})),
            rows=[
                (
                    f"[bold]{h['id']}[/bold]",
                    f"[bold]{h['title']}[/bold]\n{h['uri']}\n{h['summary']}",
                )
                for h in hits
            ],
        )

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
        for hit in self.manager.search_results:
            rows.append(
                (
                    f"[bold]{hit['gazetteer_name']} {hit['id']}[/bold]",
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
