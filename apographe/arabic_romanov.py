#
# This file is part of apographe
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2022 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
Arabic to ASCII by Maxim Romanov (Simplified Buckwalter)
copies code from https://github.com/maximromanov/Arabic_Ascii_Arabic/blob/master/translit_converter.py
"""

import re


def deNoise(text):
    noise = re.compile(
        """ ّ    | # Tashdid
                             َ    | # Fatha
                             ً    | # Tanwin Fath
                             ُ    | # Damma
                             ٌ    | # Tanwin Damm
                             ِ    | # Kasra
                             ٍ    | # Tanwin Kasr
                             ْ    | # Sukun
                             ـ     # Tatwil/Kashida
                         """,
        re.VERBOSE,
    )
    text = re.sub(noise, "", text)
    return text


def removeNonArabic(text):
    text = re.sub("[A-Za-z0-9]", "@", text)
    return text


def dictReplace(text, dic):
    for k, v in dic.items():
        text = text.replace(k, v)
    return text


def dictReplaceRev(text, dic):
    for k, v in dic.items():
        text = text.replace(v, k)
    return text


translit = {
    "،": ",",
    # letters
    "ء": "c",
    "ؤ": "u",
    "ئ": "i",
    "ا": "A",
    "إ": "I",
    "أ": "a",
    "آ": "O",
    "ب": "b",
    "ة": "o",
    "ت": "t",
    "ث": "v",
    "ج": "j",
    "ح": "H",
    "خ": "x",
    "د": "d",
    "ذ": "V",
    "ر": "r",
    "ز": "z",
    "س": "s",
    "ش": "E",
    "ص": "S",
    "ض": "D",
    "ط": "T",
    "ظ": "Z",
    "ع": "C",
    "غ": "g",
    "ف": "f",
    "ق": "q",
    "ك": "k",
    "ل": "l",
    "م": "m",
    "ن": "n",
    "ه": "h",
    "و": "w",
    "ى": "Y",
    "ي": "y",
}


def romanov(s: str):
    """Produce Romanov (simplified Buckwalter) romanization of Arabic string"""
    r = deNoise(s)
    r = removeNonArabic(r)
    return dictReplace(r, translit)
