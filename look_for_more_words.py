#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -*- mode: python; python-indent-offset: 4 -*-
#
# ./look_for_more_words.py filename
# 
# The program opens the file and filters the words aginst a set of dictionaries.
#
# Examples:
# ./look_for_more_words.py /tmp/unique_words-abstracts-English.json
#
# 2024-01-20
#
# G. Q. Maguire Jr.
#

import csv, time
from pprint import pprint
import optparse
import sys

import json
import re

# Use Python Pandas to create XLSX files
import pandas as pd

# for unicode support
import unicodedata

import sys
sys.path.append('/z3/maguire/Canvas/Canvas-tools')  # Include the path to module_folder

#  as common_English_words, common_swedish_words, common_swedish_technical_words
import common_english_and_swedish

# width to use for outputting numeric values
Numeric_field_width=7


def save_collected_words(s, lang):
    global directory_prefix

    new_file_name=f'{directory_prefix}missing_words-{lang}.json'
    sl=sorted(s)
    with open(new_file_name, 'w') as f:
        f.write(json.dumps(sl, ensure_ascii=False))

def is_float(string):
    try:
        float(string)
        return True
    except ValueError:
        return False
    
def is_number(string):
    if len(string) > 0 and not string[0].isdigit():
        return False
    rr = re.findall("[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?", string)
    if rr and len(rr) == 1:
        if rr[0].isnumeric():
            return True
        if is_float(rr[0]):
            return True
    # otherwise
    return False

words_to_ignore=[
    'gits-15', # a KTH local github instance
    'A/BSplit',
    'A/g',
    'A/m',
    'A/mm',
    'a/b',
    'a/g/n',
    '$µ$-calculus',
    '2-Amino-5-diethylaminopentane',
    '3-hexafluoro-2-propanol',
    'p+',
    'p+-poly',
    'p-InP',
    'p-i-n',
    'p-n',
    'p-p',
    'p-type',
    'poly-InP',
    'n+-poly',
    'n+-poly-Si',
    'n+-poly-Si/TiN',
    'n+/n+/n-/p+',
    'n-InP',
    'dv/dt',
    'dI/dt',
    'dV/dt',
    'YBa2Cu3O7',
    'YCbCr',
    'W/Kg', # unit
    'TlBaCaCuO',
    'Ti',
    'TiCl4',
    'TiO2/graphene',
    'Ta/Al/Ta',
    'Ta2O5',
    'Status]',
    'Si/SiO2',
    'Si0',
    'Si2H6',
    'Si3H8',
    'SiC/Si',
    'SiC/SiO2',
    'SiFe',
    'SiH4',
    'SiO2',
    'SiO2/Al2O3',
    'SiO2/HfO2',
    'SiO2/SiC',
    'SiO2/”Al2O3+TiO2',
    'SiO2',
    'SiO2–',
    'SiOx',
    'Se2',
    'Zn',
    'Zu104',
    'PbZrxTi1-xO3',
    'ZnO-Ts',
    'Si-Al2O3',
    'SiO2/a-Si/SiO2',
    'Si-Si',
    'Ni/Cu',
    'Ni/SiC/Si',
    'Neodymium',
    'Nd',
    'N2O/SiH4',
    'NaClO',
    'Na+',
    'Mg2+',
    'MdCN',
    'N-dimethyl',
    'L*a*b',
    'Log4J',
    'Log4jJ',
    'Isoflurane',
    'Ir/IrOx',
    'HxM',
    'III-V/Si',
    'III-nitride',
    'In2O3',
    'InAs/InP',
    'InGaAs',
    'InGaAsP',
    'InGaN',
    'MgxZn1-xO',
    'InP',
    'InSb/InAs',
    'Hz/cm2',
    'Hz]',
    'Ge/oxide',
    'GeH4',
    'GeSn',
    'GaAs',
    'GaInP',
    'Hf',
    'Hf3Al2',
    'Gain-128/80',
    'H/c-Si',
    'G-ω',
    'H∞-norm',
    'GHz-17',
    'Gm-C',
    'NdFeB',
    'Fe-14Cr-2W-0',
    'Eb/N0',
    'Eb/No',
    'EricssonÃ¢ÂÂs',
    'Er2O3',
    'Ethylenediamine',
    'Er3+-ions',
    'Deoxyribonucleic',
    'Desflurane',
    'Design-1',
    'Design-2',
    'Dit=3-4×1012', # equation see diva2:504573
    'CH4/H2/Ar',
    'CHF3/Ar',
    'Ca2+',
    'Cl',
    'Cl2',
    'Co4Sb12',
    'Cr',
    'Cu-I',
    'Cu3p',
    'Cu-nanoparticle-based',
    'Cu/SiC/Si',
    'Cerium',
    'Californium',
    'Ba2Cu3O7',
    'Bi0',
    'Beryllium',
    'BiAlO3',
    'BiTiFGAN',
    'Boron',
    '#BlackLivesMatter',
    '#Nike',
    '#metoo',
    'Argon',
    'Au-S',
    'Au@SiO2',
    'BaxSr1-xCoyFe1-yO3−δ',
    'Anal-ysis',
    'Amino-EG6-undecanethiol',
    'AlxGa1-xN/GaN',
    'Alcohol/Poly',
    'a-Si:H',
    'Al-Cu-Fe',
    'Al-Pd-Re',
    'Al-oxide',
    'Al/Hf-hybrid',
    'Al/Hf-hybrid/Ni',
    'Al203',
    'Al2O3+TiO2',
    'Al2O3/SiC',
    'Al2O3interface',
    'Al2O3on',
    'Al70',
    'AlGaN',
    'Ga',
    'Si',
    'Si-SiO',
    'Mg',
    'He-3',
    'Ni/Al',
    "&", "&amp;",
    "+", "-", "--",    
    "4H-SiC/SiO2",
    "Al2O3/4H-SiC", "AlGaAs/GaAs", "AlGaN/GaN",
    "AuSi",
    "Bi0.5Na0.5TiO3",
    "CdSe/ZnS",
    "GaN",
    "Ge/GeOx/Al2O3/HfO2",
    "HfO2",
    "InP/Si",
    "InSb",
    "MgZnO",
    "Sb/InAs",
    "Si-SiO2",
    "SiC",
    "Thiol-ene", 
    "Al2O3",
    "InAs",
    "InGaN/GaN", 
    "TiO2",
    "TaN",
    "MoS2",
    "NiGeSn",
    "NiSi",
    "ZnO",
    'Au-Si',
    'Ge/GeO',
    'HfO',


]

prefix_to_ignore=[
    '|',
    '~',
    '®',
    '­',
    '°',
    '±',
    '‐',
    '—',
    "'",
    ":",
    "?", 
    "‘",
    "’",
    '*',
    '-',
    '/',
    '“',
    '”',
    '„',
    '•',
    '{',
    '#',
    '>',
    '=',
    '<',
    '+',
    '$',
    '\\',
    '`',
    
]

suffix_to_ignore=[
    '%',
    '}',
    '”',
    '.',
    ',',
    ';',
    ':',
    "?", 
    "'",
    #'-',
    '*',
    "’",
    '/',
    '…',
]


def remove_prefixes(w):
    if len(w) < 1:
        return w
    if w[0] in prefix_to_ignore:
        w=w[1:]
        return remove_prefixes(w)
    return w

def remove_suffixes(w):
    if len(w) < 1:
        return w
    if w[-1] in suffix_to_ignore:
        w=w[:-1]
        return remove_suffixes(w)
    return w


# return a tripple of words, words_plurals, dataframe
def read_cefr_data(filenamme, sheetname):
    global Verbose_Flag

    df = pd.read_excel(open(filenamme, 'rb'), sheet_name=sheetname)

    # use a list as there may be multiple instances of a given word, due to multiple contexts
    words = []

    # use a set as we only care about the unique plural words
    words_plurals = set()

    for index, row in  df.iterrows():
        word=row['word']
        word_plural=row['plural']
        if isinstance(word_plural, str):
            words_plurals.add(word_plural.strip())

        # some words have a parentetical description, remove these from the word
        if word.endswith(')') and word.count('(') == 1 and word.count(')') == 1:
            offset=word.find('(')
            word=word[:offset].strip()

        if Verbose_Flag:
            print(f"{index=} {word=}")

        # the spreadsheet has pairs of columns of the part(s) of speech and the CEFR level associated with that usage
        # no rows in the spreadsheet have more than 3 such pairs of colums
        pos1=row['pos1']
        cefr_level1=row['CEFR_level1']
        if isinstance(pos1, str) and isinstance(cefr_level1, str):
            entry={'word': word, cefr_level1.strip(): pos1.strip()}
        else:
            entry={'word': word}

        pos2=row['pos2']
        cefr_level2=row['CEFR_level2']
        if isinstance(pos2, str) and isinstance(cefr_level2, str):
            entry[cefr_level2.strip()]=pos2.strip()

        pos3=row['pos3']
        cefr_level3=row['CEFR_level3']
        if isinstance(pos3, str) and isinstance(cefr_level3, str):
            entry[cefr_level3.strip()]=pos3.strip()

        word_plural=row['plural']
        if isinstance(word_plural, str):
            entry['plural']=word_plural.strip()

        words.append(entry)

    if Verbose_Flag:
        print(f'{words=}')
        print(f'{words_plurals=}')

    print(f'{len(words):>{Numeric_field_width}} entries in {sheetname}')

    return [words, words_plurals, df]

# return a tripple of words, words_plurals, dataframe
def read_CEFRLLex_data(filenamme, sheetname):
    global Verbose_Flag

    df = pd.read_excel(open(filenamme, 'rb'), sheet_name=sheetname)
    # the spreadsheet columns are:
    # word	tag	level_freq@a1	level_freq@a2	level_freq@b1	level_freq@b2	level_freq@c1	total_freq@total
    # for the English data, there are the following tags - along with other tags from Appendix 1 and Appendix 4 of 
    # 'Att söka i Korp med CQP och Regexp – en introduktion' by Klas Hjortstam, 2018
    #    available from https://www.gu.se/sites/default/files/2021-03/Att%20so%CC%88ka%20i%20Korp%20med%20CQP%20och%20Regexp.pdf
    # see also https://spraakbanken.gu.se/en/resources/saldo/tagset
    #
    # 'AB': {'Adverb'}, 
    # 'ABM_MWE': {''},
    # 'DT': {'Determiner, determiner'},
    # 'HA': {'Interrogative/relative adverb'},
    # 'HD': {'Interrogative/relative determination'},
    # 'HP': {'Interrogative/relative pronoun'},
    # 'HS': {'Interrogative/relative possessive expression'},
    # 'IE': {'infinitive particle'},
    # 'IN': {'interjection'},
    # 'INM_MWE': {''},
    # 'JJ': {'Adjective'},
    # 'JJM_MWE': {''},
    # 'KN': {'Conjunction'},
    # 'KNM_MWE',
    # 'NN': {'Noun'},
    # 'NN_NEU': {'Moun - Neuter'},
    # 'NN_UTR': {'Noun - Utrum'},
    # 'NNM_MWE': {'Noun multiword'},
    # 'NNM_UTR': {'Noun multiword - Utrum'},
    # 'PC': {'Participant'},
    # 'PL': {'Particle'}
    # 'PL_MWE': {''},
    # 'PM': {'Proper name'},
    # 'PMM_MWE': {'Proper noun'},
    # 'PN': {'Pronoun'},
    # 'PNM_MWE',
    # 'PP': {'Preposition'},
    # 'PPM_MWE': {''},
    # 'PS': {'Possessive expressions'},
    # 'RG': {'Arithmetic: base number'},
    # 'RO': {'Arithmetic: ordinal number'},
    # 'SN': {'Subjunction'},
    # 'SNM_MWE': {''},
    # 'UO': {'Foreign word'},
    # 'VB': {'Verb'},
    # 'VBM_MWE': {''},
    # 'MAD': {'Discriminating punctuation'],
    # 'MID': {'Punctuation'},
    # 'PAD': {'Punctuation'},

    # use a list as there may be multiple instances of a given word, due to multiple contexts
    words = []

    # use a set as we only care about the unique plural words
    words_plurals = set()

    for index, row in  df.iterrows():
        word=row['word']
        # skip words that are just a space
        if word == ' ':
            continue
        if Verbose_Flag:
            print(f"{index=} {word=}")

        pos=row['tag']

        # level_freq@a2	level_freq@b1	level_freq@b2	level_freq@c1
        cefr_levela1=row['level_freq@a1']
        cefr_levela2=row['level_freq@a2']
        cefr_levelb1=row['level_freq@b1']
        cefr_levelb2=row['level_freq@b2']
        cefr_levelc1=row['level_freq@c1']
        cefr_levels={'A1': cefr_levela1,
                     'A2': cefr_levela2,
                     'B1': cefr_levelb1,
                     'B2': cefr_levelb2,
                     'C1': cefr_levelc1,
                     }

        # use the POS from the most frequently occuring usage
        key_max = max(zip(cefr_levels.values(), cefr_levels.keys()))[1]  

        entry={'word': word, 'pos': pos, 'cefr_level': key_max}

        words.append(entry)

    if Verbose_Flag:
        print(f'{words=}')
        print(f'{words_plurals=}')

    print(f'{len(words):>{Numeric_field_width}} entries in {sheetname}')

    return [words, words_plurals, df]

# return a tripple of words, words_plurals, dataframe
def read_Kelly_data(filenamme, sheetname):
    global Verbose_Flag

    df = pd.read_excel(open(filenamme, 'rb'), sheet_name=sheetname)

    if Verbose_Flag:
        print(f'{df.columns=}')

    # use a list as there may be multiple instances of a given word, due to multiple contexts
    words = []

    # use a set as we only care about the unique plural words
    words_plurals = set()

    for index, row in  df.iterrows():
        word=row['Swedish items for translation\n'] #  note the original has a new line at the end of the string!
        if Verbose_Flag:
            print(f"{index=} {word=}")

        pos=row['Word classes\n'] #  note the original has a new line at the end of the string!
        cefr_level=row['CEFR levels']
        if isinstance(pos, str) and isinstance(cefr_level, str):
            entry={'word': word, cefr_level.strip(): pos.strip()}
        else:
            entry={'word': word}

        words.append(entry)

    if Verbose_Flag:
        print(f'{words=}')

    words_dict=convert_Kelly_list_to_dict(words)
    print(f'{len(words_dict):>{Numeric_field_width}} entries in {sheetname}')

    return [words_dict, words_plurals, df]

# convert multiple instance in the list to combined entries in a dict
# for example: 'adjö': {'C2': 'interj,noun-ett'}
# and 'ett': {'A1': 'numeral,det', 'B1': 'pronoun'}
# and  'sex': {'A1': 'numeral', 'B2': 'noun-ett'}
def convert_Kelly_list_to_dict(kelly_list):
    global Verbose_Flag
    kelly_set=set()
    words_kelly_swedish_dict=dict()
    
    kelly_duplicate_set=set()
    for w in kelly_list:
        word=w['word']
        if word in kelly_set:
            kelly_duplicate_set.add(word)
            if Verbose_Flag:
                print(f'duplicate word in Kelly data: {word}')
        else:
            kelly_set.add(word)

    if Verbose_Flag:
        print(f'duplicate words: {kelly_duplicate_set=}')

    for w in kelly_list:
        word=w['word']
        current_entry=dict()
        for k in w.keys():
            if k and not (k == 'word'):
                current_entry=words_kelly_swedish_dict.get(word, {})
                current_key_contents=current_entry.get(k, "") # an emptry string if nothing yet stored
                if len(current_key_contents) == 0:
                    current_entry.update({k: w[k]})
                else:
                    current_entry.update({k: current_key_contents+','+w[k]})
            words_kelly_swedish_dict[word]=current_entry

    if Verbose_Flag:
        print(f'{words_kelly_swedish_dict=}')

    if Verbose_Flag:
        print(f'list of {len(kelly_list)} converted to a dict with {len(words_kelly_swedish_dict)} entries')
    return words_kelly_swedish_dict

# return a tripple of swedish_words, english_words, dataframe
def read_KTH_svensk_engelska_ordbok_file(filenamme, sheetname):
    global Verbose_Flag

    df = pd.read_excel(open(filenamme, 'rb'), sheet_name=sheetname)

    if Verbose_Flag:
        print(f'{df.columns=}')
    if not 'Svensk term' in df.columns or\
       not 'Engelsk översättning' in df.columns or\
       not 'Synonymer' in df.columns:
        print('Unexpected missisng column(s) in spreadsheet')
        return [swedish_words, english_words, df]

    # use a set as each entry should be unique
    swedish_words = set()
    english_words = set()
    english_synonyms = set()

    for index, row in  df.iterrows():
        swedish_word=row['Svensk term'] # note that these strings may include spaces
        english_word=row['Engelsk översättning'] # note that these strings may include spaces
        english_synonym=row['Synonymer'] # note that these strings may include spaces
        if Verbose_Flag:
            print(f"{index=} {swedish_word=} {english_word=} {english_synonym=}")
        if isinstance(swedish_word, str):
            swedish_words.add(swedish_word)
        if isinstance(english_word, str):
            english_words.add(english_word)
            


    if Verbose_Flag:
        print(f'{swedish_words=} {english_words=}')

    # words_dict=convert_Kelly_list_to_dict(words)
    # print(f'{len(words_dict):>{Numeric_field_width}} entries in {sheetname}')
    print(f'{len(swedish_words):>{Numeric_field_width}} Swedish entries in KTH svensk-engelska ordbok')
    return [swedish_words, english_words, df]



def in_dictionary(s, words):
    global Verbose_Flag
    for w in words:
        word=w['word']
        if s == word:
            if Verbose_Flag:
                print(f'found {s=}')
            return True
    # otherwise
    return False


def main():
    global Verbose_Flag
    global directory_prefix

    directory_prefix='/tmp/'

    parser = optparse.OptionParser()

    parser.add_option('-v', '--verbose',
                      dest="verbose",
                      default=False,
                      action="store_true",
                      help="Print lots of output to stdout"
    )

    parser.add_option('--testing',
                      dest="testing",
                      default=False,
                      action="store_true",
                      help="Run in testing mode"
    )

    parser.add_option('--Swedish',
                      dest="swedish",
                      default=False,
                      action="store_true",
                      help="Run in testing mode"
    )


    options, remainder = parser.parse_args()

    Verbose_Flag=options.verbose
    if Verbose_Flag:
        print("ARGV      : {}".format(sys.argv[1:]))
        print("VERBOSE   : {}".format(options.verbose))
        print("REMAINING : {}".format(remainder))

    if (len(remainder) < 1):
        print("Insuffient arguments\n must provide file_name\n")
        return

    input_file_name=remainder[0]
    try:
        if Verbose_Flag:
            print(f'Trying to read: {input_file_name}')
        with open(input_file_name, 'r') as f:
            unique_words=json.load(f)
    except:
        print(f'Unable to open file named {input_file_name}')
        return

    # load in the information about CEFR levels from the various sources
    #################################################################################
    print('Loading some directories')
    directory_location="/z3/maguire/Language_Committee/"
    american_3000_file=directory_location+"American_Oxford_3000.xlsx"
    
    american_3000_words, american_3000_words_plurals, american_3000_df=read_cefr_data(american_3000_file, 'American3000')
    
    american_5000_words, american_5000_words_plurals, american_5000_df=read_cefr_data(american_3000_file, 'American5000')
    
    cefrlex_file=directory_location+"cefrlex-reduced.xlsx"
    words_EFLLex, plurals_EFLLex, df_EFLLex=read_CEFRLLex_data(cefrlex_file, 'EFLLex_NLP4J')

    words_SVALex, plurals_SVALex, df_SVALex=read_CEFRLLex_data(cefrlex_file, 'SVALex_Korp')

    kelly_swedish_file=directory_location+"Swedish-Kelly_M3_CEFR.xlsx"
    words_kelly_swedish, plurals_kelly_swedish, df_kelly_swedish=read_Kelly_data(kelly_swedish_file, 'Swedish_M3_CEFR')
 
    # KTH:s svensk-engelska ordbok
    KTH_svensk_engelska_ordbok_file=directory_location+"kth-ordboken-version-2023-07-01.xlsx"
    words_KTH_swedish, words_KTH_english, df_KTH_svensk_engelska_ordbok=read_KTH_svensk_engelska_ordbok_file(KTH_svensk_engelska_ordbok_file, 'Sheet1')

    # look for the levels for the KTH words
    for w in words_KTH_swedish:
        if w.endswith('(amerikansk engelska)'):
            w=w.replace('(amerikansk engelska)', '')
        w=w.strip()
        if w not in common_english_and_swedish.KTH_ordbok_Swedish_with_CEFR:
            # skip acronyms
            if w in common_english_and_swedish.well_known_acronyms:
                continue
            if w in common_english_and_swedish.miss_spelled_words:
                continue
            levels=common_english_and_swedish.common_swedish_words.get(w, False)
            if levels:
                print(f"'{w}': {levels},")
            else:
                if Verbose_Flag:
                    print(f'missing Swedish: {w}')

    for w in words_KTH_english:
        if w.endswith('(amerikansk engelska)'):
            w=w.replace('(amerikansk engelska)', '')
        w=w.strip()
        if w not in common_english_and_swedish.KTH_ordbok_English_with_CEFR:
            # skip acronyms
            if w in common_english_and_swedish.well_known_acronyms:
                continue
            if w in common_english_and_swedish.miss_spelled_words:
                continue
            levels=common_english_and_swedish.common_English_words.get(w, False)
            if levels:
                print(f"'{w}': {levels},")
            else:
                if Verbose_Flag:
                    print(f'missing English: {w}')
    

    print(f'{len(common_english_and_swedish.common_English_words):>{Numeric_field_width}} words in common English words')

    print(f'{len(common_english_and_swedish.common_swedish_words):>{Numeric_field_width}} words in common Swedish words')

    print(f'{len(common_english_and_swedish.common_swedish_technical_words):>{Numeric_field_width}} words in common Swedish technical words')

    #print(f'{len(common_english_and_swedish.common_danish_words):>{Numeric_field_width}} words in common Danish words')

    print(f'{len(common_english_and_swedish.common_french_words):>{Numeric_field_width}} words in common French words')
    
    print(f'{len(common_english_and_swedish.common_finnish_words):>{Numeric_field_width}} words in common Finnish words')

    print(f'{len(common_english_and_swedish.common_german_words):>{Numeric_field_width}} words in common German words')

    print(f'{len(common_english_and_swedish.common_italian_words):>{Numeric_field_width}} words in common Italian words')

    print(f'{len(common_english_and_swedish.common_latin_words):>{Numeric_field_width}} words in common Latin words')

    print(f'{len(common_english_and_swedish.common_portuguese_words):>{Numeric_field_width}} words in common Portuguese words')

    print(f'{len(common_english_and_swedish.common_spanish_words):>{Numeric_field_width}} words in common Spanish words')

    print(f'{len(common_english_and_swedish.common_units):>{Numeric_field_width}} words in common units')
    
    print(f'{len(common_english_and_swedish.names_of_persons):>{Numeric_field_width}} words in names_of_persons')
    print(f'{len(common_english_and_swedish.place_names):>{Numeric_field_width}} words in place_names')
    print(f'{len(common_english_and_swedish.company_and_product_names):>{Numeric_field_width}} words in company_and_product_names')
    print(f'{len(common_english_and_swedish.misc_words_to_ignore):>{Numeric_field_width}} words in misc_words_to_ignore')
    print(f'{len(words_to_ignore):>{Numeric_field_width}} words in words_to_ignore')
    print(f'{len(common_english_and_swedish.mathematical_words_to_ignore):>{Numeric_field_width}} words in mathematical_words_to_ignore')
    #print(f'{len(programming_keywords):>{Numeric_field_width}} words in programming_keywords')
    #print(f'{len(language_tags):>{Numeric_field_width}} words in language_tags')
    print(f'{len(common_english_and_swedish.merged_words):>{Numeric_field_width}} words in merged_words')


    print(f'{len(unique_words):>{Numeric_field_width}} read in')

    # after removing spaces and dashses, put all of the common_english_words in lower case in a fall_back list 
    fall_back_words=set()
    added_to_unique_words_count=0
    
    for w in common_english_and_swedish.common_English_words:
        w=w.replace(' ', '')
        w=w.replace('-', '')
        fall_back_words.add(w.lower())

    for w in common_english_and_swedish.merged_words:
        wx=w.replace(' ', '')
        wx=wx.replace('-', '')
        wx=wx.lower()
        fall_back_words.add(wx)
        # if necessary add the words in multiple words to unique_words
        if w.count(' ') > 0:
            ws=w.split(' ')
            for wsw in ws:
                if wsw in unique_words:
                    unique_words[wsw]= unique_words[wsw] + 1
                else:
                    unique_words[wsw]=1
                    added_to_unique_words_count=added_to_unique_words_count + 1

    print(f'{added_to_unique_words_count:>{Numeric_field_width}} added to the unique words based on those that occurred in merged_words')

    words_not_found=set()
    number_skipped=0
    number_of_potential_acronyms=0
    count_fall_back_cases=0
    
    # for some testing
    if options.testing and 'detection zone' in common_english_and_swedish.merged_words:
        print('detection zone present')
        if 'detection zone' in fall_back_words:
            print('detection zone in fall-back_words')
        if 'detectionzone' in fall_back_words:
            print('detectionzone in fall-back_words')


    for w in unique_words:
        w = unicodedata.normalize('NFC',w) #  put everything into NFC form - to make comparisons simpler; also NFC form is the W3C recommended web form
        w=remove_prefixes(w)
        w=remove_suffixes(w)

        if len(w) < 1:
            continue
        
        if w in common_english_and_swedish.common_units:
            number_skipped=number_skipped+1
            continue

        if w in common_english_and_swedish.mathematical_words_to_ignore:
            number_skipped=number_skipped+1
            continue

        # remove possessives
        if w.endswith("'s"):
            w=w[:-2]

        if w.endswith("´s"):
            w=w[:-2]

        if w.endswith("’s"):
            w=w[:-2]

        if w.replace('-', '').isdigit():
            number_skipped=number_skipped+1
            continue

        if w.replace('/', '').isdigit():
            number_skipped=number_skipped+1
            continue

        if w in common_english_and_swedish.miss_spelled_words:
            number_skipped=number_skipped+1
            continue
            
        if w in words_to_ignore:
            number_skipped=number_skipped+1
            continue

        if is_number(w):
            number_skipped=number_skipped+1
            continue

        if in_dictionary(w, american_3000_words) or (w in american_3000_words_plurals):
            number_skipped=number_skipped+1
            continue

        if in_dictionary(w, american_5000_words) or (w in american_5000_words_plurals):
            number_skipped=number_skipped+1
            continue

        # check for lower case evrsion
        if in_dictionary(w.lower(), american_3000_words) or (w in american_3000_words_plurals):
            number_skipped=number_skipped+1
            continue

        if in_dictionary(w.lower(), american_5000_words) or (w in american_5000_words_plurals):
            number_skipped=number_skipped+1
            continue

        if in_dictionary(w.lower(), words_EFLLex): # all the words in EFLLex are in lower case
            number_skipped=number_skipped+1
            continue
    
        if in_dictionary(w.lower(), words_SVALex): # all the words in SVALex are in lower case
            number_skipped=number_skipped+1
            continue

        if w in kelly_swedish_file:
            number_skipped=number_skipped+1
            continue
            
        if w.lower() in common_english_and_swedish.thousand_most_common_words_in_English_old:
            number_skipped=number_skipped+1
            continue

        if w in common_english_and_swedish.misc_words_to_ignore:
            number_skipped=number_skipped+1
            continue

        if w in common_english_and_swedish.well_known_acronyms:
            number_skipped=number_skipped+1
            continue

        # ignore plural of acronyms
        if w.endswith('s') and len(w) > 1:
            if w[:-1] in common_english_and_swedish.well_known_acronyms:
                number_skipped=number_skipped+1
                continue

        if w in common_english_and_swedish.place_names:
            number_skipped=number_skipped+1
            continue

        if w in common_english_and_swedish.company_and_product_names:
            number_skipped=number_skipped+1
            continue

        if w in common_english_and_swedish.common_programming_languages:
            number_skipped=number_skipped+1
            continue
            
        if w in common_english_and_swedish.common_swedish_words:
            number_skipped=number_skipped+1
            continue

        if w.lower() in common_english_and_swedish.common_swedish_words:
            number_skipped=number_skipped+1
            continue

        if w in common_english_and_swedish.common_swedish_technical_words:
            number_skipped=number_skipped+1
            continue

        if w.lower() in common_english_and_swedish.common_swedish_technical_words:
            number_skipped=number_skipped+1
            continue

        if w in common_english_and_swedish.names_of_persons:
            number_skipped=number_skipped+1
            continue
            
        if w in common_english_and_swedish.common_English_words:
            number_skipped=number_skipped+1
            continue

        if w.lower() in common_english_and_swedish.common_English_words:
            number_skipped=number_skipped+1
            continue

        if w in common_english_and_swedish.common_german_words:
            number_skipped=number_skipped+1
            continue

        if w.lower() in common_english_and_swedish.common_german_words:
            number_skipped=number_skipped+1
            continue

        if w in common_english_and_swedish.common_latin_words:
            number_skipped=number_skipped+1
            continue

        if w.lower() in common_english_and_swedish.common_latin_words:
            number_skipped=number_skipped+1
            continue

        if w in common_english_and_swedish.common_portuguese_words:
            number_skipped=number_skipped+1
            continue

        if w.lower() in common_english_and_swedish.common_portuguese_words:
            number_skipped=number_skipped+1
            continue

        if w in common_english_and_swedish.common_finnish_words:
            number_skipped=number_skipped+1
            continue

        if w in common_english_and_swedish.common_french_words:
            number_skipped=number_skipped+1
            continue

        if w.lower() in common_english_and_swedish.common_french_words:
            number_skipped=number_skipped+1
            continue

        if w in common_english_and_swedish.common_spanish_words:
            number_skipped=number_skipped+1
            continue

        if w.lower() in common_english_and_swedish.common_spanish_words:
            number_skipped=number_skipped+1
            continue

        if w in common_english_and_swedish.common_italian_words:
            number_skipped=number_skipped+1
            continue

        if w.lower() in common_english_and_swedish.common_italian_words:
            number_skipped=number_skipped+1
            continue


        # check for temrs like "FPGA-Based" if "FPGA-based" is in the dict()
        if w.count('-') > 0:
            ws=w.split('-')
            new_wl=list()
            for widx, wsw in enumerate(ws):
                if widx == 0:
                    new_wl.append(wsw)
                else:
                    new_wl.append(wsw.lower())
            new_w="-".join(new_wl)
            if new_w in common_english_and_swedish.common_English_words:
                number_skipped=number_skipped+1
                continue

        # also look at the case of an word with a title case word or words following it
        if w.count('-') > 0:
            ws=w.split('-')
            new_wl=list()
            for widx, wsw in enumerate(ws):
                if widx == 0:
                    new_wl.append(wsw)
                else:
                    new_wl.append(wsw.title())
            new_w="-".join(new_wl)
            if new_w in common_english_and_swedish.common_English_words:
                number_skipped=number_skipped+1
                continue

        # also look at the case of an word with a title case word or words following it
        if w.count('-') > 0:
            ws=w.split('-')
            new_wl=list()
            for widx, wsw in enumerate(ws):
                if widx == 0:
                    new_wl.append(wsw)
                else:
                    new_wl.append(wsw.title())
            new_w="-".join(new_wl)
            if new_w in common_english_and_swedish.common_English_words:
                number_skipped=number_skipped+1
                continue

        # also look at the case of an word with a title case word or words following it
        if w.count('-') > 0:
            ws=w.split('-')
            new_wl=list()
            for widx, wsw in enumerate(ws):
                if widx == 0:
                    new_wl.append(wsw.lower())
                else:
                    if wsw.isupper():
                        new_wl.append(wsw)
                    else:
                        new_wl.append(wsw.title())
            new_w="-".join(new_wl)
            if new_w in common_english_and_swedish.common_English_words:
                number_skipped=number_skipped+1
                continue

        # also look at the case of an word with a title case word or words following it
        if w.count('-') > 0:
            ws=w.split('-')
            new_wl=list()
            for widx, wsw in enumerate(ws):
                if widx == 0:
                    new_wl.append(wsw)
                else:
                    new_wl.append(wsw.title())
            new_w="-".join(new_wl)
            if new_w in common_english_and_swedish.common_English_words:
                number_skipped=number_skipped+1
                continue


        if w.lower() in common_english_and_swedish.common_English_words:
            number_skipped=number_skipped+1
            continue

        # check for temrs like "FPGA-Based" if "FPGA-based" is in the dict()
        if w.count('-') > 0:
            ws=w.split('-')
            new_wl=list()
            for widx, wsw in enumerate(ws):
                if widx == 0:
                    new_wl.append(wsw)
                else:
                    new_wl.append(wsw.lower())
            new_w="-".join(new_wl)
            if new_w in common_english_and_swedish.common_swedish_words:
                number_skipped=number_skipped+1
                continue

        # also look at the case of an word with a title case word or words following it
        if w.count('-') > 0:
            ws=w.split('-')
            new_wl=list()
            for widx, wsw in enumerate(ws):
                if widx == 0:
                    new_wl.append(wsw)
                else:
                    new_wl.append(wsw.title())
            new_w="-".join(new_wl)
            if new_w in common_english_and_swedish.common_swedish_words:
                number_skipped=number_skipped+1
                continue

        # also look at the case of an word with a title case word or words following it
        # if the 2nd and other word parts are in upper case, leave them in uppercase
        if w.count('-') > 0:
            ws=w.split('-')
            new_wl=list()
            for widx, wsw in enumerate(ws):
                if widx == 0:
                    if wsw.istitle():
                        new_wl.append(wsw.lower())
                    else:
                        new_wl.append(wsw)
                else:
                    if wsw.isupper():
                        new_wl.append(wsw)
                    else:
                        new_wl.append(wsw.title())
            new_w="-".join(new_wl)
            if new_w in common_english_and_swedish.common_swedish_words:
                number_skipped=number_skipped+1
                continue

        # also look at the case of an word with a lower case first part but upper or title case following it
        if w.count('-') > 0:
            ws=w.split('-')
            new_wl=list()
            for widx, wsw in enumerate(ws):
                if widx == 0:
                    if wsw.istitle():
                        new_wl.append(wsw.lower())
                    else:
                        new_wl.append(wsw)
                else:
                    if wsw.isupper():
                        new_wl.append(wsw)
                    else:
                        new_wl.append(wsw.title())
            new_w="-".join(new_wl)
            if new_w in common_english_and_swedish.common_swedish_words:
                number_skipped=number_skipped+1
                continue


        if w.isupper():
            number_of_potential_acronyms=number_of_potential_acronyms+1
            continue

        if w.lower() in common_english_and_swedish.well_known_acronyms:
            number_skipped=number_skipped+1
            continue

        # ignore plural of acronyms
        if w.lower().endswith('s') and len(w) > 1:
            if w[:-1] in common_english_and_swedish.well_known_acronyms:
                number_skipped=number_skipped+1
                continue

        # check the fall_back case
        wl=w.replace(' ', '')
        wl=wl.replace('-', '')
        wl=wl.lower()
        if wl in fall_back_words:
            count_fall_back_cases=count_fall_back_cases+1
            continue

        words_not_found.add(w)


    print(f'{len(words_not_found)} in words_not_found')
    #print(f'{words_not_found} in words_not_found')
    print(f'{number_skipped=}')
    print(f'{number_of_potential_acronyms=}')
    print(f'{count_fall_back_cases=}')

    if options.swedish:
        save_collected_words(words_not_found, 'Swedish')
    else:
        save_collected_words(words_not_found, 'English')

if __name__ == "__main__": main()

