# -*- coding: utf-8 -*-
# -*- mode: python; python-indent-offset: 4 -*-
#
# Some useful dicts and lists - for Kurdish ('Kurmanji')
#
#
# 2026-02-08
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

common_kurdish_words={
    'Komitey': {'B1': 'Noun', 'n': 'Committee; a group of people appointed to perform a specific function, such as organizing a festival or project'},
    'Amadekar': {'B2': 'Noun', 'n': 'Organizer or Preparer; a person responsible for the practical arrangements of an event or publication'},
    'Belediye': {'B1': 'Noun', 'n': 'Municipality; the local government body responsible for city services and administration'},
    'Diyarbakırlıyı': {'C1': 'Noun (Accusative)', 'n': 'A person from Diyarbakır (Amed); specifically refers to an individual belonging to this Kurdish-majority city'},
    'tanıdı': {'B2': 'Verb', 'n': 'Recognized or identified; often used when a person or authority officially acknowledges a status or identity'},
    'Kürtçe': {'A2': 'Noun', 'n': 'The Kurdish language; specifically the Turkish name for the language'},
    'konuşuyor': {'A1': 'Verb', 'n': 'Speaking or talks; describing the act of using a language (e.g., "Kürtçe konuşuyor" means "speaking Kurdish")'},
    "Diyarbakır’da": {"B1": "Proper Noun", "n": "In Diyarbakır; the locative form of the city name, indicating where the event occurred"},
    "Nevruz": {"A2": "Noun", "n": "The spring festival celebrating the New Year, especially significant in Kurdish culture"},
    "coşkusu": {"B2": "Noun", "n": "Enthusiasm or excitement; refers to the festive spirit and joy of the crowd"},
    "İşte": {"B1": "Adverb", "n": "Here it is; used to introduce a specific detail or piece of information like a quote or a list"},
    "ve": {"A1": "Conjunction", "n": "And; used to connect words or phrases"},
    "Yüksekdağ’ın": {"B1": "Proper Noun (Genitive)", "n": "Belonging to Figen Yüksekdağ, former HDP co-chair; the possessive form indicates it is her message"},
    "mesajı": {"A2": "Noun", "n": "The message; referring to the specific statement or greeting sent by the leaders"},
    'Dema': {'B1': 'Noun/Conjunction', 'n': 'Time or "When"; used to indicate a specific period or to start a temporal clause'},
    'Kurdi': {'A2': 'Adjective/Noun', 'n': 'Kurdish; relating to the Kurdish language or the people'},
    'Swêdî': {'A2': 'Adjective/Noun', 'n': 'Swedish; relating to the Swedish language, country, or people'},
    'Federasyona': {'B2': 'Noun', 'n': 'The Federation; the formal organizational structure for a group of associations'},
    'Komeleyên': {'B2': 'Noun (Plural)', 'n': 'Associations or societies; plural form often used in the titles of umbrella organizations'},
    'Kurdistanê': {'B1': 'Proper Noun (Genitive)', 'n': "Of Kurdistan; the possessive form of the region's name."},
    'Ji': {'A1': 'Preposition', 'n': 'From, of, or than; used to indicate origin, belonging, or comparison'},
    'Gele': {'B1': 'Noun', 'n': 'The people or the public; referring to a folk or national community'},
    'Kitêbxaneya': {'B1': 'Noun', 'n': 'Library; the definite form usually followed by a name or adjective'},
    'Kurdî': {'A2': 'Adjective/Noun', 'n': 'Kurdish; relating to the Kurdish language or people'},
    'Kîme': {'B1': 'Phrase', 'n': 'Who am I; a common introspective or poetic question (Kî + me)'},
    'Ez': {'A1': 'Pronoun', 'n': 'I; the first-person singular subject pronoun'},
    'Mem': {'B1': 'Proper Noun', 'n': 'The male protagonist in the famous Kurdish epic "Mem û Zîn"'},
    'û': {'A1': 'Conjunction', 'n': 'And; used to connect words or clauses'},
    'Zîn': {'B1': 'Proper Noun', 'n': 'The female protagonist in the famous Kurdish epic "Mem û Zîn"'},
    'Pîroz': {'B1': 'Adjective', 'n': 'Holy, sacred, or blessed; commonly used in greetings such as "Newroz pîroz be" (Happy Newroz)'},
    'Rabe': {'B2': 'Verb/Imperative', 'n': 'Stand up or rise; often used as a political or social call to action or mobilization'},
    'Rojava': {'B1': 'Proper Noun', 'n': "West; specifically refers to Western Kurdistan or the autonomous administration in northern Syria."},
    'Rojelat': {'B1': 'Proper Noun', 'n': 'East; specifically refers to Eastern Kurdistan located within the borders of Iran'},
    'Roz': {'B2': 'Noun', 'n': 'A variant of "Roj" meaning day or sun; frequently used in names and poetic contexts'},
    'Sersal': {'B1': 'Noun', 'n': 'New Year; literally "head of the year," marking the beginning of the calendar'},
    'Tora': {'B2': 'Noun', 'n': 'Network; used to describe social, digital, or organizational webs of connection'},
    'Yüksekdağ’ın': {'B1': 'Proper Noun (Genitive)', 'n': "Belonging to Figen Yüksekdağ; the possessive form of the former HDP co-chair's surname."},

}
