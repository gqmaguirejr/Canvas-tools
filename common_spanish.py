# -*- coding: utf-8 -*-
# -*- mode: python; python-indent-offset: 4 -*-
#
# Some useful dicts and lists - for Spanish
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
common_spanish_words={

    "generosidad": {"B1": "Noun", "n": "Generosity; the quality of being kind and sharing, often mentioned in the 'Kiitos' or acknowledgments section"},
    "gracias por": {"A1": "Phrase", "n": "Thank you for; used to express gratitude for a specific action, such as 'gracias por su apoyo' (thank you for your support)"},
    "todos": {"A1": "Adjective/Pronoun", "n": "All / Everyone; refers to a group of masculine or mixed-gender people or items"},
    "días": {"A1": "Noun (Plural)", "n": "Days; commonly used in the phrase 'buenos días' (good morning) or to describe a period of time"},
    "gracias": {"A1": "Interjection/Noun", "n": "Thanks / Thank you; the standard expression of gratitude"},
    "siempre": {"A1": "Adverb", "n": "Always; used to describe a constant state or 'sustained' effort"},
    "todas": {"A1": "Adjective/Pronoun", "n": "All / Everyone; refers to a group of feminine people or items, such as 'todas las células' (all the cells)"},
    "cuando": {"A1": "Conjunction/Adverb", "n": "When; used to introduce a temporal clause or a specific 'mobility scenario' in time"},
    "los": {"A1": "Article", "n": "The (Plural Masculine); used before nouns like 'los motoneurones' (the motoneurons)"},
    "más": {"A1": "Adverb/Adjective", "n": "More; used to indicate a higher quantity or to form the superlative (e.g., 'el más importante')"},
    "apoyo": {"B1": "Noun", "n": "Support; can refer to emotional encouragement or physical 'motor function' support provided by a brace"},
    "casa": {"A1": "Noun", "n": "House / Home; the primary 'living' environment or place of residence"},
    "eres": {"A1": "Verb", "n": "You are (singular informal); the 'ser' conjugation used for 'different actors' or peers"},

    "y": {"A1": "Conjunction (Spanish)", "n": "And"},
    'Bueno': {'A1': 'Adjective'},
    'Nuestra Señora': {'B1': 'Noun Phrase'}, # Our Lady, a religious title for Mary, mother of Jesus
    'nuestra': {'A2': 'Possessive Adjective (Feminine, Singular)'}, # our
    'señora': {'A2': 'Noun'},
    'Soledad': {'A2': 'Noun'}, # Solitude, loneliness, or a female given name
    'Tifón': {'B1': 'Noun'}, # Typhoon
    'Universitat': {'B2': 'Noun (Catalan)'},  # University - This is the Catalan spelling of the word
    'agua': {'A1': 'Noun'}, # Water
    'alfombra': {'A2': 'Noun'},
    'alinear': {'B2': 'Verb'},
    'de':  {'A1': 'Preposition'}, # Of, from
    'higuera': {'B1': 'Noun'}, # fig tree
    'la': {'A1': 'Article'}, # The, feminine singular
    'plata': {'A2': 'Noun'}, # silver and money
    'salud': {'A2': 'Interjection'},
    'Ajuntament de Barcelona': {'B1 (Proper Noun Phrase)': 'Noun'},  # NOTE: This is Catalan for "Barcelona City Council," not Spanish.

}
