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

    "aan": {"A1": "Preposition", "n": "To or at; often used to indicate a recipient or a state of being."},
    "al": {"A2": "Adverb", "n": "Already; used to indicate that something has happened sooner than expected."},
    "alle": {"A1": "Determiner", "n": "All; referring to the whole quantity or every member of a group."},
    "allemaal": {"A1": "Adverb, Pronoun", "n": "All of them / everyone; used to emphasize a group as a whole."},
    "bedankt": {"A1": "Interjection, Verb", "n": "Thank you; the past participle of 'bedanken' (to thank)."},
    "de": {"A1": "Article", "n": "The; one of the two definite articles in Dutch (used for masculine and feminine nouns)."},
    "die": {"A1": "Pronoun, Determiner", "n": "That or those; used for 'de-words' that are further away or previously mentioned."},
    "erg": {"A2": "Adverb, Adjective", "n": "Very or bad; frequently used as an intensifier similar to 'very much'"},
    "familie": {"A1": "Noun", "n": "Family; refers to a group of people related by blood or marriage."},
    "geen": {"A1": "Determiner", "n": "None / no; used to negate a noun that would otherwise have an indefinite article or no article."},
    "gekregen": {"A2": "Verb", "n": "Received; the past participle of 'krijgen' (to get/receive)."},
    "geweldig": {"A2": "Adjective", "n": "Great, wonderful, or amazing."},
    "heb": {"A1": "Verb", "n": "Have; the first-person singular present form of 'hebben'"},
    "heel": {"A1": "Adverb, Adjective", "n": "Very or whole; used to intensify adjectives or describe a complete object."},
    "hulp": {"A2": "Noun", "n": "Help or assistance."},
    "ik": {"A1": "Pronoun", "n": "I; the first-person singular subject pronoun."},
    "inspiratie": {"B1": "Noun", "n": "Inspiration; the process of being mentally stimulated to do or feel something creative."},
    "jullie": {"A1": "Pronoun", "n": "You (plural); used when addressing more than one person."},
    "Jullie": {"A1": "Pronoun", "n": "You (plural); capitalized version, often used at the beginning of a sentence."},
    "kan": {"A1": "Verb", "n": "Can; the first and third-person singular present form of 'kunnen' (to be able to)."},
    "lievere": {"B1": "Adjective", "n": "Dearer or sweeter; the inflected comparative form of 'lief' (sweet/dear)."},
    "me": {"A1": "Pronoun", "n": "Me; the unstressed object or reflexive pronoun for the first-person singular."},
    "mijn": {"A1": "Determiner", "n": "My; the first-person singular possessive pronoun."},
    "Nederlandse": {"A1": "Adjective, Noun", "n": "Dutch; referring to the language, people, or something from the Netherlands."},
    "ook": {"A1": "Adverb", "n": "Also or too; used to indicate addition."},
    "van": {"A1": "Preposition", "n": "Of or from; used to indicate possession, origin, or composition."},
    "vertrouwen": {"B1": "Noun, Verb", "n": "Trust or confidence; the act of relying on someone or the feeling of certainty."},
    "voor": {"A1": "Preposition", "n": "For or in front of; indicates a purpose, recipient, or spatial position."},
    "voorstellen": {"A2": "Verb", "n": "To imagine or to introduce; 'me voorstellen' often means 'to imagine'"},
    "vrienden": {"A1": "Noun (Plural)", "n": "Friends; people with whom one has a bond of mutual affection."},
    "zijn": {"A1": "Verb, Determiner", "n": "To be (infinitive) or his (possessive pronoun)."},

}
