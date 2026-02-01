# -*- coding: utf-8 -*-
# -*- mode: python; python-indent-offset: 4 -*-
#
# Some useful dicts and lists - for Turkish
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
common_turkish_words={
    "Yarpiz": {"C1": "Proper Noun", "n": "A Turkish-developed academic project/software framework providing source code for evolutionary algorithms, often used in 'swarm optimization' and 'wireless communications' research"},
    "yarpiz": {"B2": "Noun", "n": "Pennyroyal (Mentha pulegium); a medicinal and aromatic flowering plant in the mint family, native to Europe, North Africa, and the Middle East; Azeri Turkish spelling"},
    "yarpuz": {"B2": "Noun", "n": "Pennyroyal (Mentha pulegium); a medicinal and aromatic flowering plant in the mint family, native to Europe, North Africa, and the Middle East"},

}

