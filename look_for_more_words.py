#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -*- mode: python; python-indent-offset: 4 -*-
#
# ./look_for_more_words.py filename
# 
# The program opens the file and filters the words aginst a set of dictionaries.
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
    'a-Si:H',
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
    '“',
    "'",
    '-',
    '*',
    '/',
    ":",
    "?", 
    
]

suffix_to_ignore=[
    '”',
    '.',
    ',',
    ';',
    ':',
    "?", 
    "'",
    '-',
    '*',
    "’",
    '/',
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

    print(f'{len(common_english_and_swedish.common_English_words):>{Numeric_field_width}} words in common English words')

    print(f'{len(common_english_and_swedish.common_swedish_words):>{Numeric_field_width}} words in common Swedish words')

    print(f'{len(common_english_and_swedish.common_swedish_technical_words):>{Numeric_field_width}} words in common Swedish technical words')

    #print(f'{len(common_english_and_swedish.common_french_words):>{Numeric_field_width}} words in common French words')
    
    #print(f'{len(common_english_and_swedish.common_latin_words):>{Numeric_field_width}} words in common Latin words')
        
    print(f'{len(common_english_and_swedish.common_german_words):>{Numeric_field_width}} words in common German words')

    #print(f'{len(common_english_and_swedish.common_finnish_words):>{Numeric_field_width}} words in common Finnish words')

    print(f'{len(common_english_and_swedish.common_italian_words):>{Numeric_field_width}} words in common Italian words')

    #print(f'{len(common_english_and_swedish.common_danish_words):>{Numeric_field_width}} words in common Danish words')

    print(f'{len(common_english_and_swedish.names_of_persons):>{Numeric_field_width}} words in names_of_persons')
    print(f'{len(common_english_and_swedish.place_names):>{Numeric_field_width}} words in place_names')
    print(f'{len(common_english_and_swedish.company_and_product_names):>{Numeric_field_width}} words in company_and_product_names')
    #print(f'{len(misc_words_to_ignore):>{Numeric_field_width}} words in misc_words_to_ignore')
    #print(f'{len(mathematical_words_to_ignore):>{Numeric_field_width}} words in mathematical_words_to_ignore')
    #print(f'{len(programming_keywords):>{Numeric_field_width}} words in programming_keywords')
    #print(f'{len(language_tags):>{Numeric_field_width}} words in language_tags')



    print(f'{len(unique_words):>{Numeric_field_width}} read in')

    words_not_found=set()
    number_skipped=0
    number_of_potential_acronyms=0
    
    for w in unique_words:
        w = unicodedata.normalize('NFC',w) #  put everything into NFC form - to make comparisons simpler; also NFC form is the W3C recommended web form
        w=remove_prefixes(w)
        w=remove_suffixes(w)

        if len(w) < 1:
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

        words_not_found.add(w)

    print(f'{len(words_not_found)} in words_not_found')
    #print(f'{words_not_found} in words_not_found')
    print(f'{number_skipped=}')
    print(f'{number_of_potential_acronyms=}')

    if options.swedish:
        save_collected_words(words_not_found, 'Swedish')
    else:
        save_collected_words(words_not_found, 'English')

if __name__ == "__main__": main()

