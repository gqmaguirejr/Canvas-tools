# -*- coding: utf-8 -*-
# -*- mode: python; python-indent-offset: 4 -*-
#
# Some useful dicts and lists - for Norwegian
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
common_norwegian_words={
    "kirklige": {"B1": "Adjective (Archaic/Variant)", "n": "Ecclesiastical / Church-related; (Modern: kirkelige). Relating to the 'Kirchenraum' or 'liturgiska' matters"},

    "Fortidsminnen": {"B2": "Noun (Plural Definite - Variant)", "n": "The ancient monuments / The heritage; (Modern: Fortidsminnene). Referring to 'kulturminnena' and 'fornlevningar' managed by 'Riksantikvaren'"},
    "oppgave": {"B1": "Noun (Masculine/Feminine)", "n": "Task / Assignment / Statement; in heritage, refers to the 'oppgave' (report or inventory) of church assets or a specific restoration task"},
    "Kirkevaeggene": {"B1": "Noun (Plural Definite)", "n": "The church walls; specifically the interior or exterior vertical surfaces of a church. In 19th-century reports, this usually refers to the 'canvas' for medieval murals or the structural substrate requiring 'kalkpuds' (lime plaster)."},
    "kirkeveggene": {"B1": "Noun (Plural Definite)", "n": "The church walls; specifically the interior or exterior vertical surfaces of a church. In 19th-century reports, this usually refers to the 'canvas' for medieval murals or the structural substrate requiring 'kalkpuds' (lime plaster)."},
    "arkitektkongressen": {"C1": "Noun (Definite)", "n": "The architecture congress; refers to formal international or Nordic gatherings of architects (e.g., the Nordic Architecture Congress). These events were pivotal for establishing 'yrkesregler' (professional rules) and discussing the 'Restaurationsfieber' (restoration fever) sweeping Europe."},
    "oldsaksamling": {"C1": "Noun (Feminine/Masculine)", "n": "Collection of antiquities; specifically refers to the 'Universitets Oldsaksamling' in Oslo, founded in 1811, which was the primary repository for Viking and medieval artifacts"},
    "innlegg": {"B1": "Noun (Neuter)", "n": "Contribution / Submission; can refer to a written argument in a debate, a physical insert, or a formal statement in an administrative process"},
    "stenvittring": {"C1": "Noun (Feminine/Masculine)", "n": "Stone weathering; the physical disintegration or chemical decomposition of rocks and building stones"},
    "privilegium": {"C1": "Noun (Neuter)", "n": "Privilege / Prerogative; a special right or immunity granted by a sovereign or authority to a specific person, group, or institution."},

    "vers": {"A1": "Noun (Neuter)", "n": "Verse / Line of poetry / Stanza"},
    "fremfor": {"B2": "Preposition", "n": "In front of / Ahead of / Rather than / Above (preferring one over another)"},
    "et": {"A1": "Article (Neuter)", "n": "A / An (the indefinite article for neuter nouns)"},
    "prosastykke": {"B2": "Noun (Neuter)", "n": "A piece of prose; a short prose text or passage"},

    "tilbakeblikk": {"B1": "Noun", 'n': "Retrospective / Look back; occasionally found in Scandinavian cross-border scholarship"},
    "fremdrage": {"C1": "Verb", "n": "To stand out / To project / To emerge; to be prominent (equivalent to Swedish 'framträda')"},

    "forklare": {"B1": "Verb", "n": "To explain (Swedish: förklara)"},
    "inntrykk": {"A2": "Noun", 'n': "Impression; (Swedish: intryck)."},
    "institutt": {"B1": "Noun", 'n': "Institute"},
    "Statens vegvesen": {"B1": "Proper Noun", 'n': "The government agency responsible for the planning, construction, and maintenance of the national and county road networks in Norway", 'eng': '"The Norwegian Public Roads Administration'},
    "vegvesen": {"B1": "Noun", 'n': "Road administration / Highway department; A general term for the public body managing road infrastructure"},
    "undersøkelsen": {"B1": "Noun (Definite)", 'n': "The investigation / The survey / The study; Refers to a specific systematic examination or research project"},
    "løsninger": {"A2": "Noun (Plural)", 'n': "Solutions; Answers to problems or specific technical methods used to address a challenge"},

    "profesjonalisme": {"B2": "Noun", 'n': "Professionalism. The competence or skill expected of a professional"},
    "pasjon": {"B1": "Noun", 'n': "Passion; A strong or extravagant fondness, enthusiasm, or desire for anything"},

    "og": {"A1": "Conjunction", 'n': "And; The most common word used to connect words, phrases, or clauses"},
}
