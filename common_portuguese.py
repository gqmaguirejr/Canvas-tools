# -*- coding: utf-8 -*-
# -*- mode: python; python-indent-offset: 4 -*-
#
# Some useful dicts and lists - for Portuguese
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

common_portuguese_words = {
    "corporativa": {"B2": "Adjective (Feminine)", "n": "Corporate / Guild-related; refers to the 'identidade corporativa' (corporate identity) or the historical 'corporações de ofícios' (trade guilds)"},
    "Atmosfera": {"B2": "Noun (Feminine)", "n": "Atmosphere; the layer of gases surrounding Earth. A focus of meteorological and climate studies"},
    "Instituto": {"B1": "Noun (Masculine)", "n": "Institute; an organization created for scientific, educational, or administrative purposes"},
    "Mar": {"A1": "Noun (Masculine)", "n": "Sea; salt water body. A fundamental pillar of Portugal's economy and scientific research"},
    "Município": {"B1": "Noun (Masculine)", "n": "Municipality; an administrative division of territory managed by a City Council (Câmara Municipal)"},
    "Português": {"A1": "Adjective / Noun", "n": "Portuguese; relating to Portugal or its language. In institutional names, it defines national jurisdiction"},
    "da": {"A1": "Contraction", "n": "Of the (Feminine); contraction of the preposition 'de' (of) and the definite article 'a' (the)"},
    "de": {"A1": "Preposition", "n": "Of / From; indicates possession, origin, or material composition"},
    "do": {"A1": "Contraction", "n": "Of the (Masculine); contraction of the preposition 'de' (of) and the definite article 'o' (the)"},
    "e": {"A1": "Conjunction", "n": "And; used to coordinate words or phrases in a list"},
    "água": {"A1": "Noun (Feminine)", "n": "Water; essential substance. In technical contexts, often refers to territorial waters or aquatic resources"},
}

