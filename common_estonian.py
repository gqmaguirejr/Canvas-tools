# -*- coding: utf-8 -*-
# -*- mode: python; python-indent-offset: 4 -*-
#
# Some useful dicts and lists - for Estonian
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
common_estonian_words = {
    "uurimisest": {"B2": "Noun (Elative Case)", "n": "From/About the investigation; refers to the scientific 'forskning' or 'undersökning' of a site"},
    "ja": {"A1": "Conjunction", "n": "And; the fundamental connector used in titles and technical 'beskrivning'"},
    "restaureerimisest": {"B2": "Noun (Elative Case)", "n": "From/About the restoration; refers to the 'intervento' and physical 'Instandsetzung' of an object"},
    "seinamaalingute": {"C1": "Noun (Genitive Plural - Estonian)", "n": "Murals' / Wall paintings'; found in Danish research on 'Eesti' (Estonian) 'kalkmålningar'"},
    "Kunstiteaduslikke": {"C1": "Adjective (Plural Partitive)", "n": "Art-scientific / Relating to art history; derived from 'kunstiteadus' (art history/science). In Estonian, this refers to the rigorous academic study of art and visual culture"},
    "Uurimusi": {"B2": "Noun (Plural Partitive)", "n": "Studies / Research / Investigations; refers to scholarly inquiries or papers. When paired with 'Kunstiteaduslikke', it denotes a collection of art historical research"},
    "muinsuskaitse": {"B2": "Noun (Common)", "n": "Heritage protection / Preservation of antiquities; literally 'protection of the ancient.' This is the standard term for the administrative and legal framework governing cultural monuments in Estonia"},
    "restaurimine": {"B1": "Noun (Common)", "n": "Restoration; the physical and technical act of returning a building or object to a known earlier state. Often discussed in contrast to 'konserveerimine' (conservation)"},
    "seinamaalingud": {"B2": "Noun (Plural)", "n": "Wall paintings / Murals; figurative or decorative paintings applied to wall surfaces"},
}

