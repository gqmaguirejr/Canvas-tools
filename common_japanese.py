# -*- coding: utf-8 -*-
# -*- mode: python; python-indent-offset: 4 -*-
#
# Some useful dicts and lists - for Japanese
#
#
# 2026-02-01
#
# G. Q. Maguire Jr.
#
#
# Abbreviations used:
#  CEFR   Common European Framework of Reference for Languages: Learning, teaching, assessment.
#  POS    Part Of Speech
#
# This file contains several dicts and lists - these contain 'word' entries, but a 'word' can actually be a string of several words.
#
# Lists have been used when there can be multiple entries for the same 'word' and where there is not CEFR and POS information.
#
#
# Each dict's structure is:
# dict_name = {
#    entry,
#    entry,
# }
# Each entry is a 'word': CEFR_POS_dict
#
# a CEFR_POS_dict entry is a dict with the keys being CEFR levels (A1, A2, B1, B2, C1, C2, XX, and NA)
# followed by a string that contains comma separated POS
#
# The code 'XX' is used for an unknown CEFR level, while NA is for use when no level is applicable:
# 
# 

common_japanese_words = {
    "Daigaku": {"A1": "Noun", "n": "University or college; literally 'Great Learning'. In a historical context, it refers to the Imperial University established under the Ritsuryo system"},
    "Bunrika": {"C1": "Noun", "n": "The combination of Humanities/Literature (Bun) and Science (Ri); often used to refer to 'Liberal Arts and Sciences' or the integration of cross-disciplinary fields"},
    "hiragana": {"B1": "Noun", "n": "A Japanese syllabary used for native words and grammatical markers"},
    "idoru": {"B2": "Noun", "n": "Idol; media personalities (singers, actors, models) manufactured to be highly relatable and adored by fanbases"},
    "kanji": {"B1": "Noun", "n": "Logographic Chinese characters used in the Japanese writing system"},
    "keiretsu": {"C1": "Noun", "n": "A Japanese business network of companies with interlocking business relationships and shareholdings"},
    "keitai": {"B2": "Noun", "n": "Mobile phone; specifically refers to the unique mobile internet culture that developed in Japan in the early 2000s"},
    "otaku": {"B2": "Noun", "n": "A person with obsessive interests, particularly in anime, manga, or video games"},
    "romaji": {"B1": "Noun", "n": "The representation of Japanese sounds using the Roman (Latin) alphabet"},
}

