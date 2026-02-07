# -*- coding: utf-8 -*-
# -*- mode: python; python-indent-offset: 4 -*-
#
# Some useful dicts and lists - for Latin
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

common_latin_words={
    "Aves": {"B2": "Noun", "n": "The class of vertebrate animals that 'characterises' birds; they 'unify' features like feathers, toothless beaked jaws, and the laying of hard-shelled eggs"},
    "mays": {"C1": "Specific Epithet", "n": "The species name in the binomial 'Zea mays'; derived from an indigenous word for 'life-giver' or 'maize'"},
    "Zea": {"C1": "Genus", "n": "A genus of flowering plants in the grass family (Poaceae), to which the 'crop' maize belongs"},

    "declamatio": {"B2": "Noun", "n": "Declamation / Formal speech; used in 'Rinascimento' studies to describe 'ritualiserad' rhetorical performances"},

    "sacri": {"B1": "Adjective", "n": "Sacred; as in 'Palatia Sacri' or 'vasa sacra' (sacred vessels)"},

    "illvstrata": {"B2": "Adjective / Participle (Feminine)", "n": "Illustrated / Made clear; often used in titles like 'Suecia Antiqua et Hodierna Illvstrata' (Sweden Ancient and Modern Illustrated)"},
    "Ecclesiae": {"A2": "Noun (Genitive/Dative Singular or Nom/Voc Plural)", "n": "Of the Church / Churches; the central subject of 'liturgik' and 'kyrkoförnyelsens' studies"},
    "Arcus": {"B1": "Noun (Masculine)", "n": "Arch / Bow; referring to structural 'bågen' elements like the 'Arcus Triumphalis' (triumphal arch) in a 'katedralen'"},
    "AEdes": {"B2": "Noun (Feminine)", "n": "Building / Temple / House; often used in archival 'descrizione' to denote a grand 'edifice' or sacred space"},

    "necesse": {"B1": "Adjective", "n": "Necessary; often found in older 'istruzione' regarding 'necesse' repairs"},
    "Conservare": {"B1": "Verb (Infinitive)", "n": "To preserve / To keep; the foundational Latin root of 'konservering', meaning to maintain the 'substanz' in its current state"},
    "cum": {"A1": "Preposition", "n": "With; used in archival titles like 'Cum Privilegio' (With Privilege) or to denote combined functions, such as 'Architectus cum conservatore'"},
    "Fac-Simile": {"B1": "Noun (Compound)", "n": "An exact copy or reproduction; literally 'make similar'. Used for high-fidelity 'färglitografin' of medieval murals"},
    "Fac Simile": {"B1": "Noun (Variant)", "n": "Variant of Fac-Simile; the standard term in 'arkivforskning' for the systematic documentation of 'diplomatarium' scripts"},
    "Monumenta": {"C1": "Proper Noun", "n": "Monuments; often referring to the 'Monumenta' tradition of systematic survey (e.g., Rhezelius)"},
    "diplomatarium": {"C1": "Noun (Neuter)", "n": "A collection of diplomatic documents, charters, and deeds; in a Nordic context, often refers to 'Diplomatarium Suecanum' (Svenskt Diplomatarium)"},
    "pietas": {"B2": "Noun (Feminine)", "n": "Piety / Devotion; in a classical and Renaissance sense, it refers to duty and respect toward one's gods, family, and country (the root of 'Pietà')"},
    "pius": {"A2": "Adjective (Masculine)", "n": "Pious / Devout; describing someone who fulfills their duties to the divine or their homeland. Often used as a title for kings or popes"},
    "patriam": {"B1": "Noun (Feminine Accusative)", "n": "Homeland / Fatherland; the direct object form of 'patria.' Frequently found in the context of 'serving' or 'illustrating' one's country"},
    "illustrandam": {"C1": "Gerundive (Feminine Accusative)","n": "To be illustrated / To be made famous; from 'illustrare.' Often used in the phrase 'ad patriam illustrandam' (to illustrate the homeland), describing the goal of a topographic or historical work"},
    "Renovatum": {"C1": "Verb (Past Participle - Neuter)", "n": "Renewed / Restored; often found in inscriptions or on title pages to indicate that a building or a legal document has been refreshed or re-certified."},
    "Registrum Iconopragphicum": {"C2": "Noun Phrase (Proper)", "n": "Iconographic Register; specifically referring to the Swedish 'Registrum Iconographicum'—a vast national card index and archive of religious art and church interiors."},
    "iste": {"B2": "Pronoun (Demonstrative)", "n": "That / That one; often used to refer to something close to the person being addressed, sometimes with a pejorative or emphatic tone"},
    "speculum": {"C1": "Noun (Neuter)", "n": "Mirror / Looking-glass; also a common title for medieval encyclopedic works intended to 'reflect' the world or a specific branch of knowledge"},

    "noli": {"B2": "Verb (Imperative)", "n": "Do not / Be unwilling (used with an infinitive to form a negative command)"},
    "me": {"A1": "Pronoun (Accusative)", "n": "Me"},
    "tangere": {"B2": "Verb (Infinitive)", "n": "To touch / To reach / To affect"},
    
    "Acta": {"B2": "Noun (Plural)", 'n': "Acts / Proceedings; records of transactions or scholarly publications (e.g., 'Acta Ophthalmologica')"},
    "Anno domini": {"B1": "Phrase", 'n': "In the year of our Lord; AD"},
    "Anno": {"B1": "Noun", 'n': "In the year; used in dating historical documents"},
    "Biblia": {"A1": "Noun", 'n': "Bible; the central sacred text of Christianity"},
    "Communitatis": {"C1": "Noun (Genitive)", 'n': "Of the community; often found in legal charters or European Union law ('Communitatis Europeae')"},
    "Egregium": {"C2": "Adjective", 'n': "Outstanding / Distinguished; used in older academic praise or descriptions"},
    "Europeae": {"B2": "Adjective", 'n': "European"},
    "Gambusia": {"C1": "Noun (Taxonomic)", 'n': "A genus of fish; 'Gambusia affinis' is the mosquitofish"},
    "Nota": {"A2": "Verb/Noun", 'n': "Note / Mark; as in 'Nota bene' (Observe well)"},
    "Opera": {"B1": "Noun (Neuter Plural)", "n": "Works; often used in 'Opera Omnia' (Complete Works)"},
    "Ophthalmologica": {"C1": "Adjective", 'n': "Ophthalmological; relating to the branch of medicine concerned with the eye"},
    "Pauperum": {"B2": "Noun (Genitive Plural)", 'n': "Of the poor; from 'pauper' (poor person)"},
    "Salmo": {"C1": "Noun (Taxonomic)", 'n': "A genus of fish including salmon ('Salmo salar') and trout ('Salmo trutta')"},
    "Sveciae": {"B1": "Proper Noun (Genitive/Dative)", "n": "Of Sweden / To Sweden"},
    "Theorema": {"B2": "Noun", 'n': "Theorem; a mathematical or logical proposition to be proved"},
    "Universitas": {"B1": "Noun", 'n': "University / The whole; originally referring to a corporation or guild of scholars"},
    "ab": {"A2": "Preposition", 'n': "From / By; as in 'ab initio' (from the beginning)"},
    "ad": {"A2": "Preposition", 'n': "To / Toward; as in 'ad hoc' (for this specific purpose)"},
    "ad-hoc": {"B2": "Adjective/Adverb", 'n': "Created or done for a particular purpose only"},
    "affinis": {"C1": "Adjective", 'n': "Related to / Adjacent; in biology, used to indicate a species with affinities to another"},
    "al": {"B1": "Abbreviation", 'n': "And others; short for 'alii' or 'alia' in 'et al.'"},
    "alia": {"B2": "Adjective (Neuter Plural)", 'n': "Other things; as in 'inter alia' (among other things)"},
    "alii": {"B2": "Adjective (Masculine Plural)", 'n': "Other people; as in 'et alii' (and others)"},
    "ante": {"B1": "Preposition", 'n': "Before; as in 'ante meridiem' (A.M.)"},
    "antiquarius": {"B2": "Noun (Masculine)", "n": "Antiquarian; a student or collector of antiquities"},
    "antiquis": {"B1": "Adjective (Dative/Ablative Plural)", "n": "Ancient / Old / From the ancients"},
    "artes": {"A2": "Noun (Feminine Plural)", "n": "Arts / Skills / Liberal arts"},
    "beate": {"B2": "Adverb, Adjective (Vocative)", "n": "Blessedly / Happily (often used in honorific titles)"},
    "bene": {"B1": "Adverb", 'n': "Well"},
    "corus": {"B2": "Noun (Masculine)", "n": "Choir / Chancel; the part of a church between the nave and the sanctuary (Latin variant of 'chorus')"},
    "de": {"B1": "Preposition", 'n': "Of / Concerning / About; used in 'de facto', 'de jure', or 'de novo'"},
    "depictus": {"B2": "Participle, Adjective", "n": "Depicted / Painted / Portrayed (from 'depingere')"},
    "errata": {"C1": "Noun (Plural)", 'n': "Errors; a list of corrections for a printed text"},
    "est": {"A1": "Verb", 'n': "Is"},
    "et alii": {"B2": "Phrase", 'n': "And others; used in bibliographic citations to shorten a list of authors"},
    "et": {"A1": "Conjunction", "n": "And"},
    "et": {"A1": "Conjunction", 'n': "And"},
    "etcetera": {"A1": "Phrase", 'n': "From Latin 'et' (and) and 'cetera' (the rest). Often abbreviated as 'etc.' in Swedish and international inventories to indicate that a list of similar items (e.g., 'kyrksilver, mässhakar, etcetera') continues"},
    "facto": {"B2": "Noun", 'n': "Fact; as in 'de facto' (in practice, regardless of law)"},
    "habitus": {"C1": "Noun", "n": "Habitus; the ingrained habits, skills, and dispositions of an individual or group"},
    "hallux": {"C1": "Noun", 'n': "The big toe; 'hallux rigidus' is a stiffening of the joint"},
    "hoc": {"B1": "Pronoun", 'n': "This"},
    "ibid": {"B2": "Abbreviation", 'n': "In the same place; short for 'ibidem'"},
    "ibidem": {"B2": "Adverb", 'n': "In the same place; used in footnotes to refer to the same source cited previously"},
    "in silicio": {"C1": "Phrase", 'n': "In silicon; performed via computer simulation (variant of 'in silico')"},
    "in situ": {"C1": "Phrase", 'n': "In place; in its original position (archaeological finds or medical tumors)"},
    "in vivo": {"C1": "Phrase", 'n': "Within the living; biological processes taking place in a living organism"},
    "initio": {"C1": "Noun (Ablative)", 'n': "Beginning; 'ab initio' means from the very start"},
    "insignibus": {"B2": "Noun (Dative/Ablative Plural)", "n": "Insignia / Marks / Distinguishing signs / Coats of arms"},
    "interent": {"C2": "Verb (Variant)", 'n': "They were between / among; likely a variant or typo for 'intererant'"},
    "ista": {"B1": "Pronoun (Feminine)", "n": "That / This (often used to point out something specific, sometimes with a pejorative or emphatic tone)"},
    "jure": {"B2": "Noun (Ablative)", 'n': "Law / Right; 'de jure' means according to the law"},
    "lipsum": {"B1": "Abbreviation", 'n': "Shortened form of 'lorem ipsum'"},
    "lorem ipsum": {"B1": "Phrase", 'n': "Filler text; used in typesetting and design to demonstrate visual form without content"},
    "machina": {"B2": "Noun", 'n': "Machine; as in 'deus ex machina'"},
    "mea": {"A1": "Pronoun (Feminine)", "n": "My / Mine"},
    "memoriam": {"B1": "Prepositional Phrase", "n": "In memory of / To the memory of. Commonly used in 'In memoriam' titles for obituaries of scholars or dedications in commemorative publications"},
    "meridiem": {"B1": "Noun", 'n': "Midday; used in time-telling"},
    "modus operandi": {"C1": "Phrase", 'n': "Method of operating; a characteristic way of doing something"},
    "naturam": {"A2": "Noun (Accusative)", "n": "Nature / The natural world"},
    "novo": {"B2": "Adjective (Ablative)", 'n': "New; 'de novo' means starting over or anew"},
    "occurre": {"B2": "Verb", "n": "Occurs / Happens"},
    "pietas": {"C1": "Noun (Latin)", "n": "Pietas; a complex Roman virtue involving duty, religious devotion, and loyalty to family and country. Not to be confused with the Italian 'Pietà' (the mourning Virgin Mary)"},
    "prima facie": {"C1": "Phrase", 'n': "At first sight; based on the first impression"},
    "principia": {"C1": "Noun (Plural)", 'n': "Principles / Foundations; often found in titles of scientific treatises (e.g., Newton)"},
    "privilegium": {"C1": "Noun (Neuter)", "n": "Privilege / Private law; a special ordinance, right, or immunity granted to a specific individual or corporation"},
    "refero": {"B2": "Verb", 'n': "I carry back / I report; the root of 'reference'"},
    "regni": {"B1": "Noun (Genitive Singular)", "n": "Of the kingdom / Of the realm"},
    "rigidus": {"B2": "Adjective", 'n': "Rigid / Stiff"},
    "situ operando": {"C2": "Phrase (Technical)", 'n': "Operating in position; likely used in engineering or clinical contexts"},
    "situ": {"C1": "Noun (Ablative)", 'n': "Position / Site"},
    "vide": {"B2": "Verb", 'n': "See; used to direct a reader to another part of a text or a different work"}
}

