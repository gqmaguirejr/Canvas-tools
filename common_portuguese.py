# -*- coding: utf-8 -*-
# -*- mode: python; python-indent-offset: 4 -*-
#
# Some useful dicts and lists - for Portuguese
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

common_portuguese_words = {

    "Atmosfera": {"B2": "Noun (Feminine)", "n": "Atmosphere; the layer of gases surrounding Earth. A focus of meteorological and climate studies"},
    "Instituto": {"B1": "Noun (Masculine)", "n": "Institute; an organization created for scientific, educational, or administrative purposes"},
    "Mar": {"A1": "Noun (Masculine)", "n": "Sea; salt water body. A fundamental pillar of Portugal's economy and scientific research"},
    "Município": {"B1": "Noun (Masculine)", "n": "Municipality; an administrative division of territory managed by a City Council (Câmara Municipal)"},
    "Português": {"A1": "Adjective / Noun", "n": "Portuguese; relating to Portugal or its language. In institutional names, it defines national jurisdiction"},
    "corporativa": {"B2": "Adjective (Feminine)", "n": "Corporate / Guild-related; refers to the 'identidade corporativa' (corporate identity) or the historical 'corporações de ofícios' (trade guilds)"},
    "da": {"A1": "Contraction", "n": "Of the (Feminine); contraction of the preposition 'de' (of) and the definite article 'a' (the)"},
    "de": {"A1": "Preposition", "n": "Of / From; indicates possession, origin, or material composition"},
    "do": {"A1": "Contraction", "n": "Of the (Masculine); contraction of the preposition 'de' (of) and the definite article 'o' (the)"},
    "e": {"A1": "Conjunction", "n": "And; used to coordinate words or phrases in a list"},
    "água": {"A1": "Noun (Feminine)", "n": "Water; essential substance. In technical contexts, often refers to territorial waters or aquatic resources"},
    'Acesso': {'B1': 'Noun', 'n': 'Access; frequently used regarding "acesso ao tratamento" (access to treatment) for HIV/SIDA'},
    'Activistas': {'B1': 'Noun (Plural)', 'n': 'Activists; individuals working in health and human rights, such as those in the Kindlimuka association'},
    'Acçolini': {'C1': 'Proper Noun', 'n': 'Likely a specific surname or specialized term appearing in Mozambican historical or archival documents'},
    'Associação': {'B2': 'Noun', 'n': 'Association; often referring to organized groups like the "Associação dos Médicos Tradicionais de Moçambique" (AMETRAMO)'},
    'Boca': {'A2': 'Noun', 'n': 'Mouth; used metaphorically in "boca do crocodilo" (mouth of the crocodile) to describe danger or oppression'},
    'COVAX': {'B2': 'Proper Noun', 'n': 'The global initiative aimed at equitable access to COVID-19 vaccines, including in Mozambique'},
    'Cabo': {'A2': 'Noun', 'n': 'Cape; specifically referring to "Cabo Delgado", the northern province of Mozambique'},
    'Cair': {'A2': 'Verb', 'n': 'To fall; used to describe the collapse of infrastructure or the drop in deaths (mortes)'},
    'Ciclones': {'B1': 'Noun (Plural)', 'n': 'Cyclones; devastating weather events like Idai and Kenneth that impacted Sofala and Cabo Delgado'},
    'Civil': {'B1': 'Adjective', 'n': 'Civil; relating to "sociedade civil" (civil society) organizations involved in the HIV response'},
    'Combate': {'B1': 'Noun', 'n': 'Combat or fight; used in the context of the "Combate ao HIV/SIDA" (Fight against HIV/AIDS)'},
    'Comissão': {'B2': 'Noun', 'n': 'Commission; a formal group like a "comissão nacional" (national commission) for health or human rights'},
    'Conselho': {'B2': 'Noun', 'n': 'Council; such as the "Conselho Nacional de Combate ao HIV/SIDA" (National AIDS Council)'},
    'Contra': {'A2': 'Preposition', 'n': 'Against; used in campaigns "contra o silêncio" (against the silence) surrounding HIV stigma'},
    'Coordenação': {'B2': 'Noun', 'n': 'Coordination; the management of "ajuda humanitária" (humanitarian aid) across different provinces'},
    'Cristão': {'B1': 'Noun, Adjective', 'n': 'Christian; referring to religious actors providing social and health assistance'},
    'Crocodilo': {'B1': 'Noun', 'n': 'Crocodile; a cultural symbol often appearing in local narratives or metaphors for the "mouth" of danger'},
    'Delgado': {'A1': 'Adjective, Proper Noun', 'n': 'Thin; part of the geographic name "Cabo Delgado"'},
    'Dentes': {'A2': 'Noun (Plural)', 'n': 'Teeth; part of the metaphor "dentes do crocodilo" (teeth of the crocodile)'},
    'Desenvolvimento': {'B2': 'Noun', 'n': 'Development; referring to socio-economic growth and international "assistência" (assistance)'},
    'Devemos': {'A2': 'Verb', 'n': 'We must/should; used in social calls for solidarity: "devemos estar juntos" (we must be together)'},
    'Direitos': {'B1': 'Noun (Plural)', 'n': 'Rights; specifically "direitos humanos" (human rights) for people living with HIV'},
    'Empresários': {'B2': 'Noun (Plural)', 'n': 'Entrepreneurs/Businesspeople; private sector actors involved in national development'},
    'Escapar': {'B1': 'Verb', 'n': 'To escape; used regarding "pessoas deslocadas" (displaced people) fleeing conflict or cyclones'},
    'Estado': {'B1': 'Noun', 'n': 'State; the government of the Republic of Mozambique (Estado moçambicano)'},
    'Estamos': {'A1': 'Verb', 'n': 'We are; used in phrases of shared status: "estamos juntos" (we are together/in solidarity)'},
    'Estratégico': {'B2': 'Adjective', 'n': 'Strategic; relating to a high-level plan, like the "Plano Estratégico Nacional" (National Strategic Plan)'},
    'Família': {'A1': 'Noun', 'n': 'Family; the basic social unit affected by HIV/SIDA and natural disasters'},
    'HIV': {'A1': 'Noun', 'n': 'Human Immunodeficiency Virus; the central focus of national health programs'},
    'HIV/SIDA': {'A1': 'Noun', 'n': 'The Portuguese acronym for HIV/AIDS'},
    'Humanos': {'B1': 'Adjective (Plural)', 'n': 'Human; part of "direitos humanos" (human rights)'},
    'Há': {'A1': 'Verb', 'n': 'There is/are; also used for time duration ("há três anos" - three years ago)'},
    'Idai': {'B2': 'Proper Noun', 'n': 'Cyclone Idai; the 2019 tropical cyclone that caused catastrophic damage in Sofala province'},
    'Integração': {'B2': 'Noun', 'n': 'Integration; the process of including displaced populations into new communities'},
    'International': {'A2': 'Adjective', 'n': 'International; describing the "comunidade internacional" (international community)'},
    'Islâmico': {'B1': 'Adjective', 'n': 'Islamic; relating to the religious community in northern Mozambique (Norte)'},
    'Kenneth': {'B2': 'Proper Noun', 'n': 'Cyclone Kenneth; the strong tropical cyclone that hit northern Mozambique shortly after Idai'},
    'Kindlimuka': {'C1': 'Proper Noun', 'n': 'A pioneer association of people living with HIV in Mozambique, meaning "wake up"'},
    'Manica': {'A2': 'Proper Noun', 'n': 'A central province in Mozambique often affected by climate events'},
    'Mensuel': {'C1': 'Adjective', 'n': 'Monthly; likely from French "mensuel" appearing in international "l\'Office" documents'},
    'Movimento': {'B1': 'Noun', 'n': 'Movement; such as a social or political "movimento" for liberation or health rights'},
    'Moçambicana': {'A1': 'Adjective', 'n': 'Mozambican (feminine); relating to the people, culture, or institutions of Mozambique'},
    'Moçambique': {'A1': 'Proper Noun', 'n': 'The Republic of Mozambique'},
    'Nacional': {'A2': 'Adjective', 'n': 'National; part of "Plataforma Nacional" (National Platform) for disaster management'},
    'Nacional': {'A2': 'Adjective', 'n': 'National; referring to the state-level response or country-wide initiatives'},
    'Norte': {'A2': 'Noun', 'n': 'North; specifically the northern region including Cabo Delgado'},
    'Notícias': {'A2': 'Noun (Plural)', 'n': 'News; also the name of a major Mozambican daily newspaper ("Jornal Notícias") used for historical research'},
    'Plano': {'B1': 'Noun', 'n': 'Plan; a set of intended actions, especially official government or health policies'},
    'Plataforma': {'B2': 'Noun', 'n': 'Platform; a collaborative forum for civil society and the state'},
    'Programa': {'B1': 'Noun', 'n': 'Program; such as the "Programa Nacional" (National Program) for health or reabilitatação'},
    'Publique': {'B2': 'Verb', 'n': 'Publish; often an instruction in archival research or "Publique-se" in official decrees'},
    'Quebrar': {'B2': 'Verb', 'n': 'To break; used regarding "quebrar o silêncio" (break the silence) against stigma'},
    'Reabilitação': {'B2': 'Noun', 'n': 'Rehabilitation; the process of recovery for "vítimas" (victims) of conflict or cyclones'},
    'Resumo': {'B1': 'Noun', 'n': 'Summary; a brief statement of "estudos" (studies) or findings'},
    'SIDA': {'A1': 'Noun', 'n': 'Acquired Immunodeficiency Syndrome (AIDS)'},
    'Saúde': {'A1': 'Noun', 'n': 'Health; part of the "Ministério da Saúde" (Ministry of Health)'},
    'Saúde': {'A1': 'Noun', 'n': 'Health; referring to the "Ministério da Saúde" (Ministry of Health) or general medical well-being'},
    'Social': {'B1': 'Adjective', 'n': 'Social; relating to "solidariedade social" (social solidarity)'},
    'Sociedade': {'B1': 'Noun', 'n': 'Society; specifically "sociedade civil" (civil society)'},
    'Sofala': {'A2': 'Proper Noun', 'n': 'A central Mozambican province hit hard by Cyclone Idai'},
    'Somos': {'A1': 'Verb', 'n': 'We are; used in "somos um povo" (we are one people)'},
    'Tratamento': {'B1': 'Noun', 'n': 'Treatment; the medical care for "pessoas" living with HIV'},
    'Ucrânia': {'A1': 'Proper Noun', 'n': 'Ukraine; often mentioned in 2026 reports regarding global "ajuda" redirection'},
    'actores': {'B2': 'Noun (Plural)', 'n': 'Actors; referring to the individuals or organizations (national and global) involved in the HIV response'},
    'ajuda': {'A2': 'Noun', 'n': 'Help or aid; "ajuda humanitária" is critical for displaced populations'},
    'americano': {'A1': 'Adjective', 'n': 'American; relating to "povo americano" (American people) or US-based doador aid'},
    'anos': {'A1': 'Noun (Plural)', 'n': 'Years; used to track "número de mortes" over time'},
    'ao': {'A1': 'Contraction', 'n': 'To the (masculine singular)'},
    'aos': {'A1': 'Contraction', 'n': 'To the (masculine plural)'},
    'assistência': {'B1': 'Noun', 'n': 'Assistance; the provision of "vacinas" or food to "populações"'},
    'através': {'B1': 'Preposition', 'n': 'Through; used for "através da cooperação" (through cooperation)'},
    'com': {'A1': 'Preposition', 'n': 'With'},
    'comunidade': {'B1': 'Noun', 'n': 'Community; referring to the "comunidade internacional" or local village groups'},
    'contra': {'A2': 'Preposition', 'n': 'Against'},
    'd\'Hygiène': {'C1': 'Noun', 'n': 'Hygiene (French); often found in international "d\'Hygiène Publique" (Public Hygiene) archives'},
    'da': {'A1': 'Contraction', 'n': 'Of the (feminine singular)'},
    'de': {'A1': 'Preposition', 'n': 'Of/From'},
    'deslocadas': {'B2': 'Adjective, Noun', 'n': 'Displaced (feminine plural); "pessoas deslocadas" fleeing Cabo Delgado'},
    'doador': {'B2': 'Noun', 'n': 'Donor; the "doador internacional" (international donor) funding health initiatives'},
    'dos': {'A1': 'Contraction', 'n': 'Of the (masculine plural)'},
    'e': {'A1': 'Conjunction', 'n': 'And'},
    'em': {'A1': 'Preposition', 'n': 'In/On'},
    'entre': {'A2': 'Preposition', 'n': 'Between/Among'},
    'estar': {'A1': 'Verb', 'n': 'To be (temporary state)'},
    'estudos': {'A2': 'Noun (Plural)', 'n': 'Studies; academic or scientific research papers concerning social and biological issues'},
    'globais': {'B2': 'Adjective (Plural)', 'n': 'Global; relating to international organizations and worldwide health policies'},
    'humanitária': {'B1': 'Adjective', 'n': 'Humanitarian; relating to "ajuda" given in times of "ciclones"'},
    'iniciativa': {'B2': 'Noun', 'n': 'Initiative; like a new "iniciativa internacional" for "vacinas"'},
    'internacional': {'A2': 'Adjective', 'n': 'International'},
    'juntos': {'A2': 'Adjective, Adverb', 'n': 'Together'},
    'l\'Office': {'C1': 'Noun', 'n': 'The Office (French); referring to "l\'Office International d\'Hygiène Publique"'},
    'maior': {'A2': 'Adjective', 'n': 'Greater/Larger'},
    'metade': {'B1': 'Noun', 'n': 'Half; used to quantify a reduction: "metade das mortes"'},
    'mortes': {'B1': 'Noun (Plural)', 'n': 'Deaths'},
    'moçambicano': {'A1': 'Adjective', 'n': 'Mozambican (masculine)'},
    'na': {'A1': 'Contraction', 'n': 'In the (feminine singular)'},
    'nacionais': {'A2': 'Adjective (Plural)', 'n': 'National; relating to actors or policies originating within Mozambique'},
    'não': {'A1': 'Adverb', 'n': 'No/Not'},
    'número': {'A2': 'Noun', 'n': 'Number'},
    'o': {'A1': 'Article', 'n': 'The (masculine singular)'},
    'onde': {'A2': 'Adverb', 'n': 'Where'},
    'outras': {'A2': 'Adjective (Plural)', 'n': 'Other (feminine)'},
    'para': {'A1': 'Preposition', 'n': 'For or toward; used to indicate the objective or recipient of a plan or study'},
    'permitiu': {'B2': 'Verb', 'n': 'Allowed/Permitted; e.g., "permitiu que reduzíssemos" (allowed us to reduce)'},
    'pessoas': {'A1': 'Noun (Plural)', 'n': 'People'},
    'populações': {'B1': 'Noun (Plural)', 'n': 'Populations'},
    'por': {'A1': 'Preposition', 'n': 'By/Through/For'},
    'post-independence': {'B2': 'Adjective', 'n': 'The era following Mozambique\'s liberation from Portugal in 1975'},
    'postindependence': {'B2': 'Adjective', 'n': 'See "post-independence"'},
    'poverty': {'B1': 'Noun', 'n': 'The state of being extremely poor; a major factor addressed in the "Plano de Acção para a Redução da Pobreza" (PARPA)'},
    'povo': {'B1': 'Noun', 'n': 'People/Nation'},
    'províncias': {'B1': 'Noun (Plural)', 'n': 'Provinces; such as Sofala, Manica, and Cabo Delgado'},
    'quase': {'A2': 'Adverb', 'n': 'Almost'},
    'que': {'A1': 'Pronoun, Conjunction', 'n': 'That/Which/Who'},
    'reduzíssemos': {'C1': 'Verb', 'n': 'That we would reduce (imperfect subjunctive); expressing a goal or hope'},
    'resposta': {'B1': 'Noun', 'n': 'Response; the organized effort by the state and civil society to address the AIDS epidemic'},
    'silêncio': {'B1': 'Noun', 'n': 'Silence; "quebrar o silêncio" is vital for "direitos humanos"'},
    'sobre': {'A2': 'Preposition', 'n': 'About or on; used in titles of "estudos sobre" (studies about) specific social or health phenomena'},
    'solidariedade': {'B2': 'Noun', 'n': 'Solidarity'},
    'três': {'A1': 'Number', 'n': 'Three'},
    'vacinas': {'B1': 'Noun (Plural)', 'n': 'Vaccines; delivered through "COVAX" or other "iniciativa" programs'},
    'vencermos': {'B2': 'Verb', 'n': 'To win/overcome (personal infinitive); "para vencermos o HIV"'},
    'vítimas': {'B1': 'Noun (Plural)', 'n': 'Victims'},
    'às': {'A1': 'Contraction', 'n': 'To the (feminine plural)'},
    'Voluntários': {'B1': 'Noun (Plural)', 'n': 'Volunteers; individuals who freely offer their time and skills to support humanitarian aid, health services, or community development'},

}

