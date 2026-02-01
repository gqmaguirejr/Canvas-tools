# -*- coding: utf-8 -*-
# -*- mode: python; python-indent-offset: 4 -*-
#
# Some useful dicts and lists - for Russian
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

#    'toroidalnaya kamera magnitnaya katushka', # toroidal chamber with magnetic coils - basis of the term "tokamak"
common_russian_words = {
    "toroidalnaya": {"C1": "Adjective (Feminine)", "n": "Toroidal; shaped like a torus (a doughnut shape). Refers to the geometry of the vacuum vessel."},
    "kamera": {"A1": "Noun (Feminine)", "n": "Chamber / Vessel; the container where the plasma is held."},
    "magnitnaya": {"A2": "Adjective (Feminine)", "n": "Magnetic; relating to the fields used to confine the hot plasma away from the chamber walls."},
    "katushka": {"B2": "Noun (Feminine)", "n": "Coil; specifically the electromagnetic coils that generate the confining magnetic fields."},
}

