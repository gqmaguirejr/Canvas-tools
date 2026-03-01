# -*- coding: utf-8 -*-
# -*- mode: python; python-indent-offset: 4 -*-
#
# Some useful dicts and lists - for Dutch
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
common_dutch_words={
    "Lucasscholen": {"B2": "Noun (Plural)", "n": "St. Luke Schools; educational institutions or guilds named after St. Luke, the patron saint of painters. Historically, these schools oversaw the training and quality standards of artists and craftsmen"},
    "Lacqverwerk": {"C1": "Noun (Archaic)", "n": "Lacquerwork; refers to the art of coating objects (often wood or metal) with lacquer to create a hard, durable, and glossy finish. Common in 17th–19th century decorative arts and furniture"},
    "lakwerk": {"C1": "Noun", "n": "Lacquerwork; refers to the art of coating objects (often wood or metal) with lacquer to create a hard, durable, and glossy finish"},
    "Middeleeuwse": {"B1": "Adjective", "n": "Medieval; relating to the Middle Ages (approx. 500–1500 AD). Often used to describe Gothic or Romanesque architectural styles."},
    "muurschilderingen": {"B2": "Noun (Plural)", "n": "Wall paintings / Murals; figurative or decorative paintings applied to wall surfaces, such as frescoes or secco paintings in historical churches."},
    'fietspaden': {'B1': 'Noun (Plural)', 'n': 'Cycle paths; dedicated lanes or tracks designed specifically for bicycle traffic, similar to Swedish cykelvägar'},
    'ontwerp': {'B2': 'Noun', 'n': 'Design or blueprint; the structural plan or engineering layout for a road or path structure'},
    'en': {'A1': 'Conjunction', 'n': 'And; a basic coordinating conjunction used to link terms or phrases'},
    'keuze': {'B1': 'Noun', 'n': 'Choice or selection; refers to the decision-making process in selecting materials or design parameters'},
    'materiaal': {'A2': 'Noun', 'n': 'Material; the physical substances (such as asphalt, concrete, or aggregate) used in construction'},

}
