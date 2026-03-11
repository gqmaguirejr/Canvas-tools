# -*- coding: utf-8 -*-
# -*- mode: python; python-indent-offset: 4 -*-
#
# Some useful dicts and lists - for Faroese
#
#
# 2026-03-11
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
common_faroese_words = {
    'Føroya': {'B2': 'Proper Noun', 'n': 'The Faroe Islands (Faroese: Føroyar); an autonomous territory within the Kingdom of Denmark, often included in Nordic regional planning studies'},
    'Javnadarflokkurin': {'C1': 'Proper Noun', 'n': 'The Social Democratic Party of the Faroe Islands; a political party advocating for social welfare and strong ties within the Danish Realm'},
}

