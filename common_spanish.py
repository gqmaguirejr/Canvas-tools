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
    'agua': {'A1': 'Noun'}, # Water
    'alfombra': {'A2': 'Noun'},
    'alinear': {'B2': 'Verb'},
    'de':  {'A1': 'Preposition'}, # Of, from
    'higuera': {'B1': 'Noun'}, # fig tree
    'la': {'A1': 'Article'}, # The, feminine singular
    'plata': {'A2': 'Noun'}, # silver and money
    'salud': {'A2': 'Interjection'},
    'Ajuntament de Barcelona': {'B1 (Proper Noun Phrase)': 'Noun'},  # NOTE: This is Catalan for "Barcelona City Council," not Spanish.
    'Universidad Nacional de La Plata': {'B2': 'Proper Noun', 'n': 'A major public university in Argentina, known for influential research in territorial planning and geography'},
    'Teorías Territoriales y Planificación Territorial': {'C1': 'Noun phrase', 'n': 'Territorial Theories and Territorial Planning; a common academic course or field of study in Spanish-speaking urbanism'},
    'Teoría': {'B1': 'Noun', 'n': 'Theory; the systematic explanation of principles governing a subject like urban morphology'},
    'Anatomía de Una Metrópoli Discontinua': {'C1': 'Proper Noun', 'n': "'Anatomy of a Discontinuous Metropolis'; a thematic study of fragmented urban growth patterns."},
    'Anthropos': {'C1': 'Proper Noun', 'n': 'A prominent Spanish publishing house specializing in social sciences, humanities, and urban theory'},
    'Ciudad de Los Ricos y La Ciudad de Los Pobres': {'B2': 'Noun phrase', 'n': "'City of the Rich and City of the Poor'; a concept describing urban segregation and socio-economic fragmentation."},
    'Ciudadanismo': {'C1': 'Noun', 'n': 'Citizenism; an ideology or social movement focused on the rights and active participation of city residents'},
    'Ildefonso Cerdà y el nacimiento de la urbanística moderna': {'C1': 'Proper Noun', 'n': "A seminal work regarding Cerdà, the engineer who designed Barcelona's Eixample and founded the discipline of 'Urbanistica'."},
    'Imprenta Española': {'B2': 'Proper Noun', 'n': 'Spanish Press; referring to the historical printing and publication of technical and urbanist texts'},
    'Grecia': {'A1': 'Proper Noun', 'n': 'Greece; often studied in urbanism for the origins of the "polis" and classical city planning'},
    'Fondo de Cultura Económica': {'B2': 'Proper Noun', 'n': 'A major Spanish-language publisher (FCE) based in Mexico, essential for distributing urban and social theory'},
    'Estudios': {'A2': 'Noun (plural)', 'n': 'Studies; systematic academic investigations into urban phenomena'},
    'Rurizad': {'C1': 'Noun', 'n': 'A variant or specific term related to "rurality" or the process of ruralization within a territory'},
    'Regió Metropolitana de Barcelona': {'B2': 'Proper Noun', 'n': 'The Barcelona Metropolitan Region; a key case study for polycentricity and regional planning'},
    'Revista': {'A2': 'Noun', 'n': 'Magazine or journal; a periodic publication for academic or professional urban discourse'},
    'Prefacio': {'B1': 'Noun', 'n': 'Preface; the introductory section of a book or planning document'},
    'Planificación': {'B1': 'Noun', 'n': 'Planning; the technical and political process of organizing land use and infrastructure'},
    'Planos': {'B1': 'Noun (plural)', 'n': 'Plans or maps; technical drawings used to represent urban designs and layouts'},
    'Pasados': {'A2': 'Noun (plural)', 'n': 'Pasts; the historical layers or previous states of a city (see palimpsest)'},
    'Necesides': {'B1': 'Noun (plural)', 'n': 'A variant or misspelling of "necesidades" (needs); referring to the social requirements of a population'},
    'Múltiples': {'B1': 'Adjective (plural)', 'n': 'Multiple; used to describe the diverse factors influencing urban growth'},
    'Morfología': {'C1': 'Noun', 'n': 'Morphology; the study of the form and structure of human settlements'},
    'Mito': {'B1': 'Noun', 'n': 'Myth; in urban theory, a narrative that shapes how a city is perceived or planned'},
    'vacíos': {'B2': 'Noun (plural)', 'n': 'Voids or empty spaces; the non-built areas within an urban fabric'},
    'reforma': {'B1': 'Noun', 'n': 'Reform; a planned change or improvement to an existing urban or social system'},
    'fraternidad': {'B2': 'Noun', 'n': 'Fraternity or brotherhood; a social ideal often linked to the design of public spaces'},
    'familia': {'A1': 'Noun', 'n': 'Family; the basic social unit for which residential housing is designed'},
    'crecimiento': {'B1': 'Noun', 'n': 'Growth; the physical expansion or population increase of a city'},
    'ciudad': {'A1': 'Noun', 'n': 'City; the primary subject of urbanistic study and intervention'},
    'Espacien': {'C1': 'Verb, Noun', 'n': 'A variant related to "espaciar" (to space out) or the conceptualization of space'},
    'Cuarto': {'A1': 'Noun, Adjective', 'n': 'Room or fourth; referring to a specific division of space or a numerical order'},
    'segunda': {'A1': 'Adjective', 'n': 'Second; often used in "segunda residencia" (second home) or secondary urban phases'},

    'proyecto': {'B1': 'Noun', 'n': 'Project; the formal design, plan, or proposal for an architectural or urban intervention'},
    'metrópolis': {'B2': 'Noun', 'n': 'Metropolis; a very large and densely populated city that serves as a regional or national hub'},
    'leyes': {'A2': 'Noun (plural)', 'n': 'Laws; the legal frameworks and regulations that govern land use and urban development'},
    'ensanche': {'C1': 'Noun', 'n': 'Expansion; specifically the 19th-century planned extensions of Spanish cities, such as the Cerdà plan in Barcelona'},
    'Revolución': {'B1': 'Noun', 'n': 'Revolution; often referring to the Industrial Revolution and its radical impact on urban structures'},
    'Ricos': {'A1': 'Noun (plural), Adjective', 'n': 'The rich; in urban theory, referring to affluent social classes and their influence on spatial segregation'},
    'circulación': {'B2': 'Noun', 'n': 'Circulation; the movement of people, vehicles, and goods through the city’s street network'},
    'Paisaje': {'B1': 'Noun', 'n': 'Landscape; the visible features of an area of land, including both natural and human-made elements'},
    'Libros': {'A1': 'Noun (plural)', 'n': 'Books; the written records and theoretical texts that document urban history and planning'},
    'Filosofía': {'B2': 'Noun', 'n': 'Philosophy; the study of the fundamental nature of knowledge and ethics in relation to urban life'},
    'Caminos': {'A2': 'Noun (plural)', 'n': 'Paths or roads; the physical routes that connect different points within a territory'},
    'Colapso': {'C1': 'Noun', 'n': 'Collapse; the breakdown of urban systems or social structures due to crises or over-exploitation'},
    'Ecológico': {'B1': 'Adjective', 'n': 'Ecological; relating to the relationship between living organisms and their urban or natural environment'},
    'vecinos de las calles con respecto': {'B2': 'Noun phrase', 'n': 'Neighbors of the streets with respect to; referring to the relationship or rights of residents regarding their local urban environment'},
    'Memoria Revolucionaria': {'C1': 'Noun phrase', 'n': 'Revolutionary Memory; the collective remembrance of radical social or political shifts that have reshaped the city'},
    'Siglo Después': {'B1': 'Noun phrase', 'n': 'A Century Later; a temporal perspective often used in longitudinal studies to assess the long-term impact of urban reforms'},

}
