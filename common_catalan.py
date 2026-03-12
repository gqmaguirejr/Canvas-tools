# -*- coding: utf-8 -*-
# -*- mode: python; python-indent-offset: 4 -*-
#
# Some useful dicts and lists - for Catalan
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
common_catalan_words={
    'Ciutat funcional': {'B2': 'Noun (Catalan)', 'n': 'The functional city; the modernist planning ideal where urban zones are strictly divided by use'},
    'Identitat del territori': {'C1': 'Noun (Catalan)', 'n': 'Territorial identity; the unique cultural and physical character of a specific geographic region'},
    'Quaderns': {'B2': 'Noun (Catalan)', 'n': 'Notebooks or journals; specifically referring to "Quaderns d\'Arquitectura i Urbanisme," an influential Catalan publication'},
    'Universitat': {'B2': 'Noun (Catalan)'},  # University - This is the Catalan spelling of the word
    "d'arquitectura": {'B2': 'Noun phrase', 'n': 'Of architecture; the possessive form used to describe principles, journals, or schools related to the building arts'},
    'Mediterrània': {'B1': 'Proper Noun', 'n': 'Mediterranean; referring to the sea, the climatic region, and the specific urban culture shared by coastal Southern Europe'},

}
