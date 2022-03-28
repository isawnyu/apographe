#
# This file is part of apographe
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2022 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
Metadata, vocabularies, and utilities for languages and scripts
"""
from apographe.arabic_romanov import romanov

# cltk does not work yet under python 3.10.x
# from cltk.phonology.arabic import romanization as cltk_arabic_romanization

# camel-tools does not work yet under python 3.10.x
import iuliia
from language_tags import tags
import logging
import pinyin

# polyglot throws errors
# from polyglot.downloader import downloader as polygot_downloader
# https://polyglot.readthedocs.io/en/latest/Transliteration.html
# from polyglot.text import Text as PolyglotText
# from polyglot.transliteration import Transliterator as PolyglotTransliterator
import regex
import romanize3
from slugify import slugify
import transliterate as barseghyan_transliterate
import unicodedata

polyglot_transliterators = dict()

# Script codes supported by regex package
REGEX_SCRIPT_CODES = [
    "Adlm",
    "Aghb",
    "Ahom",
    "Arab",
    "Armi",
    "Armn",
    "Avst",
    "Bali",
    "Bamu",
    "Bass",
    "Batk",
    "Beng",
    "Bhks",
    "Bopo",
    "Brah",
    "Brai",
    "Bugi",
    "Buhd",
    "Cakm",
    "Cans",
    "Cari",
    "Cham",
    "Cher",
    "Copt",
    "Cprt",
    "Cyrl",
    "Deva",
    "Dogr",
    "Dsrt",
    "Dupl",
    "Egyp",
    "Elba",
    "Elym",
    "Ethi",
    "Geor",
    "Glag",
    "Gong",
    "Gonm",
    "Goth",
    "Gran",
    "Grek",
    "Gujr",
    "Guru",
    "Hang",
    "Hani",
    "Hano",
    "Hatr",
    "Hebr",
    "Hira",
    "Hluw",
    "Hmng",
    "Hmnp",
    "Hrkt",
    "Hung",
    "Ital",
    "Java",
    "Kali",
    "Kana",
    "Khar",
    "Khmr",
    "Khoj",
    "Knda",
    "Kthi",
    "Lana",
    "Laoo",
    "Latn",
    "Lepc",
    "Limb",
    "Lina",
    "Linb",
    "Lisu",
    "Lyci",
    "Lydi",
    "Mahj",
    "Maka",
    "Mand",
    "Mani",
    "Marc",
    "Medf",
    "Mend",
    "Merc",
    "Mero",
    "Mlym",
    "Modi",
    "Mong",
    "Mroo",
    "Mtei",
    "Mult",
    "Mymr",
    "Nand",
    "Narb",
    "Nbat",
    "Newa",
    "Nkoo",
    "Nshu",
    "Ogam",
    "Olck",
    "Orkh",
    "Orya",
    "Osge",
    "Osma",
    "Palm",
    "Pauc",
    "Perm",
    "Phag",
    "Phli",
    "Phlp",
    "Phnx",
    "Plrd",
    "Prti",
    "Qaac",
    "Qaai",
    "Rjng",
    "Rohg",
    "Runr",
    "Samr",
    "Sarb",
    "Saur",
    "Sgnw",
    "Shaw",
    "Shrd",
    "Sidd",
    "Sind",
    "Sinh",
    "Sogd",
    "Sogo",
    "Sora",
    "Soyo",
    "Sund",
    "Sylo",
    "Syrc",
    "Tagb",
    "Takr",
    "Tale",
    "Talu",
    "Taml",
    "Tang",
    "Tavt",
    "Telu",
    "Tfng",
    "Tglg",
    "Thaa",
    "Thai",
    "Tibt",
    "Tirh",
    "Ugar",
    "Vaii",
    "Wara",
    "Wcho",
    "Xpeo",
    "Xsux",
    "Yiii",
    "Zanb",
    "Zinh",
]

# regular expressions for matching scripts
rxx_scripts = dict()
for code in REGEX_SCRIPT_CODES:
    rx = r"^[\s\p{Common}\p{Diacriticals}\p{" + code + r"}]+$"
    rxx_scripts[code] = regex.compile(rx)


def check_script(s: str):
    """Returns script code or None"""
    for script_code, rx in rxx_scripts.items():
        if rx.match(s):
            return script_code
    return None


def is_latn(s: str):
    """Returns True or False"""
    if rxx_scripts["Latn"].match(s):
        return True
    else:
        return False


def romanize(s: str, language_code="und"):
    """Returns romanizations for string."""
    logger = logging.getLogger(__file__ + ":romanize()")

    romanizations = set()
    script = check_script(s)
    if script:
        # polyglot transliterators - won't install
        # if language_code != "und":
        #    try:
        #        suppress_script = tags.language(language_code).script.format
        #    except AttributeError:
        #        pass
        #    else:
        #        if script == suppress_script:
        #            transliterator_key = f"{language_code}:en"
        #            try:
        #                polyglot_transliterators[transliterator_key]
        #            except KeyError:
        #                polyglot_transliterators[
        #                    transliterator_key
        #                ] = PolyglotTransliterator(
        #                    source_lang=language_code, target_lang="en"
        #                )
        #            finally:
        #                transliterator = polyglot_transliterators[transliterator_key]
        #            romanizations.add(transliterator.transliterate(s))
        #
        # other transliterators
        if script == "Arab":
            # Arabic script
            if language_code == "ar":
                r = romanize3.__dict__["ara"]
                romanizations.add(r.convert(s))
                romanizations.add(romanov(s))
            # for mode in cltk_arabic_romanization.available_romanization_systems:
            #    romanizations.add(cltk_arabic_romanization.transliterate(mode, s))
        elif script == "Armi":
            # Armenian script
            r = romanize3.__dict__["arm"]
            romanizations.add(r.convert(s))
            if language_code == "hy":
                romanizations.add(
                    barseghyan_transliterate.translit(s, "hy", reversed=True)
                )
        elif script == "Brah":
            # Brahmi script
            r = romanize3.__dict__["brh"]
            romanizations.add(r.convert(s))
        elif script == "Copt":
            # Coptic script
            r = romanize3.__dict__["cop"]
            romanizations.add(r.convert(s))
        elif script == "Cyrl":
            # Cyrillic script
            if language_code == "ru":
                romanizations.add(
                    barseghyan_transliterate.translit(s, "ru", reversed=True)
                )
            for sname, schema in iuliia.Schemas.items():
                romanizations.add(iuliia.translate(s, schema))
        elif script == "Geor":
            romanizations.add(barseghyan_transliterate.translit(s, "ka", reversed=True))
        elif script == "Grek":
            # Greek script
            r = romanize3.__dict__["grc"]
            rom = r.convert(s)
            if not is_latn(rom):
                if "ί" in rom:
                    romanizations.add(rom.replace("ί", "í"))
                else:
                    logger.error(
                        f'romanize3.__dict__("grc") produced a romanization containing non-Latin characters: {rom}'
                    )
            else:
                romanizations.add(rom)
            rom = barseghyan_transliterate.translit(s, "el", reversed=True)
            romanizations.add(rom)
        elif script == "Hani":
            # Han script
            romanizations.add(pinyin.get(s))
            romanizations.add(pinyin.get(s, format="strip", delimiter=" "))
            romanizations.add(pinyin.get(s, format="numerical"))
        elif script == "Hebr":
            # Hebrew script
            r = romanize3.__dict__["heb"]
            romanizations.add(r.convert(s))
        elif script == "Latn":
            # Latin script
            romanizations.add(s)
        elif script == "Phnx":
            # Phoenician script
            r = romanize3.__dict__["phn"]
            romanizations.add(r.convert(s))
        elif script == "Syrc":
            r = romanize3.__dict__["syc"]
            romanizations.add(r.convert(s))
        else:
            raise RuntimeError(script)
    slug = slugify(s, separator=" ", lowercase=False)
    if slug:
        romanizations.add(slug)
    for normal_form in ["NFC", "NFD", "NFKC", "NFKD"]:
        name_strings = list(romanizations)
        romanizations.update(
            [unicodedata.normalize(normal_form, s) for s in name_strings]
        )
    romanizations = set([r for r in romanizations if is_latn(r)])
    return romanizations


class LanguageAware:
    """A mixin base class for making types language-aware."""

    def __init__(self, **kwargs):
        self._language_tag = None
        self._language_subtag = None
        self._script_subtag = None
        self._region_subtag = None

        for k, v in kwargs.items():
            try:
                setattr(self, k, v)
            except AttributeError:
                pass

    @property
    def language_tag(self):
        if self._language_tag:
            return self._language_tag.format
        else:
            return "und"

    @language_tag.setter
    def language_tag(self, value: str):
        tag = tags.tag(value)
        if tag.valid:
            self._language_tag = tag
            self._language_subtag = tag.language
            self._region_subtag = tag.region
            self._script_subtag = tag.script
            if self._script_subtag is None:
                self._script_subtag = self._language_subtag.script
        else:
            # eventually try to fix this
            raise ValueError(
                f"Invalid language tag '{value}': {'; '.join([str(e) for e in tag.errors])}"
            )

    @property
    def language_subtag(self):
        try:
            return self._language_subtag.format
        except AttributeError:
            return None

    @property
    def region_subtag(self):
        try:
            return self._region_subtag.format
        except AttributeError:
            return None

    @property
    def script_subtag(self):
        try:
            return self._script_subtag.format
        except AttributeError:
            return None
