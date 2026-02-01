# -*- coding: utf-8 -*-
# -*- mode: python; python-indent-offset: 4 -*-
#
# Some useful dicts and lists - for Icelandic
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
common_icelandic_words = {
    # Proper Names (People)
    "Þóra": {"B2": "Proper Noun (Feminine)", "n": "Thóra; a common Icelandic female name derived from 'Thor' (the god of thunder)."},

    # Geography (Hydronyms)
    "Þjórsá": {"B2": "Proper Noun (Feminine)","n": "Thjórsá; Iceland's longest river, located in the south of the island."},
    
    "Tungnaá": {"B2": "Proper Noun (Feminine)","n": "Tungnaá; a glacier river in the southern highlands, known for its milky blue volcanic silt."},
}

