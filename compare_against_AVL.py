#!/usr/bin/env python3
### /usr/bin/python3
# -*- coding: utf-8 -*-
# -*- mode: python; python-indent-offset: 4 -*-
#
# ./compare_against_AVL.py
# 
# Compare the entries in AVL against other dictionaries/word list.
#  The Academic Vocabulary list (AVL) is based on the "All COCA-Academic" data set - see https://www.academicwords.info/download.asp
# These ~20K words were identified by Mark Davies and Dee Gardner from the Corpus of Contemporary American English (COCA).
#
# Examples:
# To compare the AVL word list with a number of te different sources I am using and the words I have collected from courses and thesis abstracts, run ght peogram
#
# ./compare_against_AVL.py
#
# To compare the entires from the spreadsheet with words augmentd with CEFR levels and POS do:
# ./compare_against_AVL.py --self
# 
# The program will report the number of words that are missing.
#
# Yuo can also use the --avl options to include the list of AVL words that I have CEFR and POS information for when looking at which AVL words do not occurs in one of the English word lists tha Ihave used.
#
# ./compare_against_AVL.py --avl
# The program lists the missing words and the POS information as well as the total number of missing words. Note that this number will include each word entry on a line in the spreadsheet. As the spreadsheet has a number of words that appear on multiple lines because their origin in the corpus is different this number will be higher that you might expect.
#
# This program was ased on look_for_more_words.py
#
# 2024-05-26
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

# to use math.isnan(x) function
import math

import sys
sys.path.append('/z3/maguire/Canvas/Canvas-tools')  # Include the path to module_folder
sys.path.append('/home/maguire/Canvas/Canvas-tools')

#  as common_English_words, common_swedish_words, common_swedish_technical_words
import common_english_and_swedish
import common_acronyms
import miss_spelled_to_correct_spelling
import diva_merged_words
import diva_corrected_abstracts
import AVL_words_with_CEFR

# width to use for outputting numeric values
Numeric_field_width=7


def is_numeric_range(w):
    if w.count('-') == 1:
        sw=w.split('-')
        return is_number(sw[0]) and is_number(sw[1])
    if w.count('~') == 1:
        sw=w.split('~')
        return is_number(sw[0]) and is_number(sw[1])
    if w.count('‐') == 1:
        sw=w.split('‐')
        return is_number(sw[0]) and is_number(sw[1])
    if w.count('—') == 1:
        sw=w.split('—')
        return is_number(sw[0]) and is_number(sw[1])
    if w.count('..') == 1:
        sw=w.split('..')
        return is_number(sw[0]) and is_number(sw[1])
    # look for alternatives or ratios such as 2.1/2.5
    if w.count('/') == 1:
        sw=w.split('/')
        return is_number(sw[0]) and is_number(sw[1])
    # otherwise
    return False

def is_numeric_range_eith_units(w):
    for u in common_english_and_swedish.common_units:
        if w.endswith(u):
            w=w[:-len(u)]
            return is_numeric_range(w)
    return False

def remove_products_and_ranges(s):
    # the following is to avoid getting fooled by ISPO document numbers, such as 15765-1:2011
    if s.count(':') > 0:
        return s
    # check for triple product first
    matches = re.findall(r"(\d+[*x]\d+[*x]\d+)", s)
    if not matches:
        # note that the minus sign has to be last otherwise it things a range is being specified
        matches = re.findall(r"(\d+[\*x‐~—_-]\d+)", s)
        if not matches:
            return s
    matches = list( dict.fromkeys(matches) )
    matches.sort()
    for m in matches:
        s=s.replace(m, '')
    return s

def remove_percentage_range(s):
    # note that the minus sign has to be last otherwise it things a range is being specified
    matches = re.findall(r"(\d+%[~—_-]\d+)", s)
    if not matches:
        return s
    matches = list( dict.fromkeys(matches) )
    matches.sort()
    for m in matches:
        s=s.replace(m, '')
    return s


def remove_lbracket_number_rbracket(s):
    matches = re.findall(r"\[[0-9]+\]", s)
    if not matches:
        return s
    matches = list( dict.fromkeys(matches) )
    matches.sort()
    for m in matches:
        s=s.replace(m, '')
    return s

def remove_lbracket_text_rbracket(s):
    matches = re.findall(r"\[[A-Za-z/]+\]", s)
    if not matches:
        return s
    matches = list( dict.fromkeys(matches) )
    matches.sort()
    for m in matches:
        s=s.replace(m, '')
    return s

def remove_lbracket_rbracket_pair(s):
    if len(s) > 2 and s[0] == '[' and s[-1] == ']':
        return s[1:-1]
    else:
        return s

def remove_lparen_rparen_pair(s):
    if len(s) > 2 and s[0] == '(' and s[-1] == ')':
        return s[1:-1]
    else:
        return s

def remove_single_lbracket(s):
    if len(s) == 1 and s[0] == '[':
        return ''
    if len(s) > 1 and s[0] == '[' and s[-1] != ']':
        return s[1:]
    else:
        return s

def correct_for_hyphenation(s):
    offset=s.find('- ')
    and_offset=s.find('and ')
    if offset < 0:
        return s
    if and_offset < 0:
        return s[:offset]+correct_for_hyphenation(s[offset+2:])
    if and_offset > (offset + 2):
        return s[:offset]+correct_for_hyphenation(s[offset+2:])
    else:
        return s[:and_offset4]+correct_for_hyphenation(s[and_offset4:])



def save_collected_words(s, lang):
    global directory_prefix
    new_file_name=f'{directory_prefix}missing_words-{lang}.json'
    sl=sorted(s)
    with open(new_file_name, 'w') as f:
        f.write(json.dumps(sl, ensure_ascii=False))

def save_potential_acronyms(s):
    global directory_prefix
    new_file_name=f'{directory_prefix}potential_acronyms.json'
    sl=sorted(s)
    with open(new_file_name, 'w') as f:
        f.write(json.dumps(sl, ensure_ascii=False))

# A helpful function
# def generate_chars(start, end):
#     for i in range(start, end+1, 6):
#         print(f"'{chr(i)}', '{chr(i+1)}', '{chr(i+2)}', '{chr(i+3)}', '{chr(i+4)}', '{chr(i+5)}',")

def is_MathSymbol(s):
    if not len(s) == 1:
        return False
    #
    if 0x2100 <= ord(s) and ord(s) <= 0x214FF:         # Letterlike Symbols
        return True
    if 0x2200 <= ord(s) and ord(s) <= 0x22FF:     # Mathematical Operators
        return True
    if 0X2A00 <= ord(s) and ord(s) <= 0x2AFF:     # Supplemental Mathematical Operators
        return True
    if 0xE000 <= ord(s) and ord(s) <= 0xF8FF:     # Private Use Area - seems to be used by conveertnb (to print Jupyter notebooks)
        return True
    if 0x1D400 <= ord(s) and ord(s) <= 0x1D4FF:    # Mathematical Alphanumeric Symbols
        return True
    else:
        return False


def is_GreekSymbol(s):
    if not len(s) == 1:
        return False
    if 0x0370 <= ord(s) and ord(s) <= 0x03FF:
        return True
    else:
        return False

def is_Miscellaneous_Technical(s):
    if not len(s) == 1:
        return False
    if 0x2300 <= ord(s) and ord(s) <= 0x23FF:
        return True
    else:
        return False


def is_equation(s):
    math_symbols=[ # generate_chars(0x2200, 0x22ff)
        '∀', '∁', '∂', '∃', '∄', '∅',
        '∆', '∇', '∈', '∉', '∊', '∋',
        '∌', '∍', '∎', '∏', '∐', '∑',
        '−', '∓', '∔', '∕', '∖', '∗',
        '∘', '∙', '√', '∛', '∜', '∝',
        '∞', '∟', '∠', '∡', '∢', '∣',
        '∤', '∥', '∦', '∧', '∨', '∩',
        '∪', '∫', '∬', '∭', '∮', '∯',
        '∰', '∱', '∲', '∳', '∴', '∵',
        '∶', '∷', '∸', '∹', '∺', '∻',
        '∼', '∽', '∾', '∿', '≀', '≁',
        '≂', '≃', '≄', '≅', '≆', '≇',
        '≈', '≉', '≊', '≋', '≌', '≍',
        '≎', '≏', '≐', '≑', '≒', '≓',
        '≔', '≕', '≖', '≗', '≘', '≙',
        '≚', '≛', '≜', '≝', '≞', '≟',
        '≠', '≡', '≢', '≣', '≤', '≥',
        '≦', '≧', '≨', '≩', '≪', '≫',
        '≬', '≭', '≮', '≯', '≰', '≱',
        '≲', '≳', '≴', '≵', '≶', '≷',
        '≸', '≹', '≺', '≻', '≼', '≽',
        '≾', '≿', '⊀', '⊁', '⊂', '⊃',
        '⊄', '⊅', '⊆', '⊇', '⊈', '⊉',
        '⊊', '⊋', '⊌', '⊍', '⊎', '⊏',
        '⊐', '⊑', '⊒', '⊓', '⊔', '⊕',
        '⊖', '⊗', '⊘', '⊙', '⊚', '⊛',
        '⊜', '⊝', '⊞', '⊟', '⊠', '⊡',
        '⊢', '⊣', '⊤', '⊥', '⊦', '⊧',
        '⊨', '⊩', '⊪', '⊫', '⊬', '⊭',
        '⊮', '⊯', '⊰', '⊱', '⊲', '⊳',
        '⊴', '⊵', '⊶', '⊷', '⊸', '⊹',
        '⊺', '⊻', '⊼', '⊽', '⊾', '⊿',
        '⋀', '⋁', '⋂', '⋃', '⋄', '⋅',
        '⋆', '⋇', '⋈', '⋉', '⋊', '⋋',
        '⋌', '⋍', '⋎', '⋏', '⋐', '⋑',
        '⋒', '⋓', '⋔', '⋕', '⋖', '⋗',
        '⋘', '⋙', '⋚', '⋛', '⋜', '⋝',
        '⋞', '⋟', '⋠', '⋡', '⋢', '⋣',
        '⋤', '⋥', '⋦', '⋧', '⋨', '⋩',
        '⋪', '⋫', '⋬', '⋭', '⋮', '⋯',
        '⋰', '⋱', '⋲', '⋳', '⋴', '⋵',
        '⋶', '⋷', '⋸', '⋹', '⋺', '⋻',
        '⋼', '⋽', '⋾', '⋿'
    ]
    #
    math_possible_excludes=['−', '∣', '∶', '∷', '∼']
    #
    extra_symbols = ['×', '…', '=', '÷', '+', '–', '^', '·', '¹', '²', '³', '±', '¬', 'µ', '¼', '½', '¾', 'Ø']
    #
    if len(s) < 1:
        return False
    #
    if len(s) == 1:
        if is_MathSymbol(s):  # alternative it could be "if s in math_symbols:"
            return True
        if is_GreekSymbol(s):
            return True
        if is_Miscellaneous_Technical(s):
            return True
        if s in extra_symbols:
            return True
        else:
            return False
    #
    # exception for minus sign and tilde before a digit - these should be taken care of elsewhere
    if (s[0] == '−' or  s[0] == '∼') and s[1].isdigit():
        return False
    #
    if s[0] in ['¬']:
        return True
    #
    if s.count('=') == 1:
        return True
    #
    # if there is any math symbol in the string, consider it an equation
    for c in s:
        if is_MathSymbol(c): # alternatively "c in math_symbols:"
            return True
        if is_GreekSymbol(c):
            return True
        if is_Miscellaneous_Technical(c):
            return True
        if c in extra_symbols:
            return True
    #
    if s.count('|') > 1:
        return True
    #
    # if there is an assignment symbol
    if s.count('←') == 1:
        # and there is at least one letter for the lefthand side
        if s.find('←') >= 1:
            return True
    #
    # otherwise
    return False

def is_MiscSymbol_or_Pictograph(s):
    if not len(s) == 1:
        return False
    #
    if 0x2190 <= ord(s) and ord(s) <= 0x21FF:    # Arrows
        return True
    if 0x25A0 <= ord(s) and ord(s) <= 0x25FF:    # Geometric Shapes
        return True
    if 0x2600 <= ord(s) and ord(s) <= 0x26FF:    # Miscellaneous Symbols
        return True
    if 0xFFF0 <= ord(s) and ord(s) <= 0xFFFD:    # Specials
        return True
    if 0x27F0 <= ord(s) and ord(s) <= 0x27FF:    #    Supplemental Arrows-A
        return True
    if 0x1F300 <= ord(s) and ord(s) <= 0x1F5FF:  # Miscellaneous Symbols and Pictographs
        return True
    if 0x1F900 <= ord(s) and ord(s) <= 0x1F9FF:  # Supplemental Symbols and Pictographs
        return True
    return False

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
    # check for comma as decimail point
    if string.count(',') == 1:
        string=string.replace(',', '.')
        return is_number(string)
    # otherwise
    return False

words_to_ignore=[
    'swastika/penis', # diva2:1198914
    '0,0,1',
    '0.4,0.6',
    '1,0,0',
    '1,322,361',
    '1.1.2',
    '1080x1920',
    '17p13',
    '2,0,2',
    '2.1.3',
    '2001:512',
    '309m2/s',
    '33min13.7s',
    '3x3x3',
    '4-􀀀5',
    '45x15mm',
    '8,060,000',
    'm/84',
    'mAP@0.5',
    'mAP[0.5:0.95]',
    '32x32',
    '9906:2012',
    #
    '61175IEC',
    '61499IEC',
    '61850-9-2IEC61499,',
    '61850IEC',
    'IEC',
    'IEC--1',
    'IEC-60255-187-1',
    'IEC-60255-187-1standarden',
    'IEC-61508ISO26262.',
    'IEC-standarden',
    'IEC-standarder',
    'IEC61499',
    'IEC61499-systemspecifikation',
    'IEC61499standarden',
    'IEC61850',
    'IEC61850-9-2LE',
    'IEC61850-IEC61499',
    'IEC61850-kommunikationsprotokollet',
    'IEC61850-specifikationsbeskrivning',
    'IEC61850-standarden',
    'IEC61850-struktur',
    'ISO/IEC',
    'ISO/IECMPEG-standarden',
    '61850-9-2IEC61499',
    '"9:1373GW,4:76GW',
    'GQ', # my first two initials - diva2:510423
    '18:00',
    '24:00',
    '50x50',
    '9x9',
    '8;9􀀀18;6',
    '1/11-2015',
    '11x11',
    '13284-1:2017',
    '7:5',
    '87.41%89.85',
    '30/4-2016',
    ",", # ignore a single comma by itself
    '􀀀0:01',
    's.67]',
    'p.67]', # part of a citation in diva2:1599067
    'saadua@kth.se',
    'r,v',
    'r>0.6',
    'L*a*b',
    '2nm/4.2nm',
    '2nm/4.5nm',
    'Chart.js',
    'Nightmare.js',
    'OfficeUtils.dll',
    'PeerfactSim.KOM',
    'PowerModels.jl',
    '[27°C-300°C]',
    '27°C-300°C',
    'IEC-2',
    'IEC-60255-187-1',
    'IEC61850-9-2'
    'IEC61850-IEC61499',
    'ISO-26262/IEC-61508',
    'IEC-61508IEC',
    'K-1',
    'N-1',
    'N-2',
    'N1',
    'N2',
    'N3',
    '27°C-300°C',
    '>1',
    '>1999', 
    'org/cgi-bin/mimetex',
    '&amp',
    '&gt',
    '&lt',
    '\\',
    ']',
    '_29', # used for ×29.7 in  diva2:1514163
    '􀀀0', # [−0. in diva2:1463798
    '􀀀100', # [−100 in diva2:1463798
    'oi/fc_thesis', # part of github URL in diva2:1836829
    'v1',
    'v2',
    'v4',
    'v8',
    'di/dt',
    'sub-7',
    's-1',
    's/c',
    's2',
    '30cmX30cmX10cm',
    'x1',
    'x2',
    'x3',
    'x4',
    'f0',
    'f1',
    'f2',
    'k1',
    'k2',
    'p1',
    'p15',
    'p2',
    'p5',
    'n1',
    'n2',
    'n3',
    'n~1',
    'r>0',
    'Eg', #  diva2:577757
    "10¯6",
    "13”-17",
    "150’000",
    "1’240’000",
    "1⁄3",
    "2014-i2b2",
    "20{20{20",
    "20¯21",
    "4%23",
    "41%{89",
    "4{5",
    "4”-7",
    "99%/10",
    "3GHz-5GHz",
    "400-to-1",
    '5Pd21Re8',
    'ℓ1-penalised',
    'slideD',      # check - correct it is a template where D is one or more digits
    'H∞norm',
    'April2012',
    'April2018',
    "AmI'11", # International Joint Conference on Ambient Intelligent (AmI'11
    'tommasop@kth',
    'renhuldt/TiramiProt', # part of the URL:  https://gitlab.com/nikos.t.renhuldt/TiramiProt
    'gits-15', # a KTH local github instance
    'A/BSplit',
    'A/g',
    'A/m',
    'A/mm',
    'a/b',
    'a/g/n',
    '$µ$-calculus',
    'dv/dt',
    'dI/dt',
    'dV/dt',
    'W/Kg', # unit
    'Status]',
    'L*a*b',
    'Log4J',
    'Log4jJ',
    'HxM',
    'Hz/cm2',
    'Hz]',
    'Gain-128/80',
    'G-ω',
    'H∞-norm',
    'GHz-17',
    'Gm-C',
    'Eb/N0',
    'Eb/No',
    'EricssonÃ¢ÂÂs',
    'Design-1',
    'Design-2',
    'Dit=3-4×1012', # equation see diva2:504573
    '#BlackLivesMatter',
    '#Nike',
    '#metoo',
    'Anal-ysis',
    "&", "&amp;",
    "+", "-", "--",    
    '[Mac71]', # from a citation
]

prefix_to_ignore=[
    "'",
    ":",
    "?", 
    "‘",
    "’",
    ",",
    ".",
    ">",
    '#',
    '$',
    '%',
    '*',
    '+',
    '-',
    '/',
    #'<',
    '=',
    #'>',
    '@',
    '\\',
    '`',
    '{',
    '|',
    '~',
    '­',
    '®',
    #'°',
    '±',
    '​', # 'ZERO WIDTH SPACE' (U+200B)
    '‌', # 'ZERO WIDTH NON-JOINER' (U+200C)
    '‐',
    '–',
    '—',
    '―',
    '“',
    '”',
    '„',
    '•',
    '→',
    '⇡',
    '−',
    '∼',
    '≈',
    '≥',
    '⌈',
    '□',
    '◦',
    '♣',
    '、',
    '・',
    '',
    '￼',
    '�',    
    "􀀀", # 'DATA LINK ESCAPE' (U+0010)
]

suffix_to_ignore=[
    '',
    '‚', # u+201a
    '-',
    '­',
    '—',
    '”',
    "'",
    "?",
    "!", 
    "’",
    ".",
    #'-',
    '%',
    '*',
    ',',
    '.',
    '/',
    ':',
    ';',
    '}',
    '´',
    '”',
    '…',
    '�',
    '\\',
    '\u200c', # ZERO WIDTH NON-JOINER' (U+200C)
    '\u200b', # ZERO WIDTH SPACE' (U+200B)
    '•',
]

# milticharacter prefixs
long_prefix_to_ignore=[
    '&gt;',
    '&lt;',
    '...',
]

long_suffix_to_ignore=[
    '...',
    '"&lt;',
]

def remove_prefixes(w):
    if len(w) < 1:
        return w
    for lp in long_prefix_to_ignore:
        if w.startswith(lp):
            w=w[len(lp):]
            return remove_prefixes(w)
    if w[0] in prefix_to_ignore:
        w=w[1:]
        return remove_prefixes(w)
    return w

def remove_suffixes(w):
    if len(w) < 1:
        return w
    for lp in long_suffix_to_ignore:
        if w.endswith(lp):
            w=w[:-len(lp)]
            return remove_suffixes(w)
    if w[-1] in suffix_to_ignore:
        w=w[:-1]
        return remove_suffixes(w)
    return w


# return a tripple of words, words_plurals, dataframe
def read_cefr_data(filenamme, sheetname):
    global Verbose_Flag
    #
    df = pd.read_excel(open(filenamme, 'rb'), sheet_name=sheetname)
    #
    # use a list as there may be multiple instances of a given word, due to multiple contexts
    words = []
    #
    # use a set as we only care about the unique plural words
    words_plurals = set()
    #
    for index, row in  df.iterrows():
        word=row['word']
        word_plural=row['plural']
        if isinstance(word_plural, str):
            words_plurals.add(word_plural.strip())
        #
        # some words have a parentetical description, remove these from the word
        if word.endswith(')') and word.count('(') == 1 and word.count(')') == 1:
            offset=word.find('(')
            word=word[:offset].strip()
        #
        if Verbose_Flag:
            print(f"{index=} {word=}")
        #
        # the spreadsheet has pairs of columns of the part(s) of speech and the CEFR level associated with that usage
        # no rows in the spreadsheet have more than 3 such pairs of colums
        pos1=row['pos1']
        cefr_level1=row['CEFR_level1']
        if isinstance(pos1, str) and isinstance(cefr_level1, str):
            entry={'word': word, cefr_level1.strip(): pos1.strip()}
        else:
            entry={'word': word}
        #
        pos2=row['pos2']
        cefr_level2=row['CEFR_level2']
        if isinstance(pos2, str) and isinstance(cefr_level2, str):
            entry[cefr_level2.strip()]=pos2.strip()
        #
        pos3=row['pos3']
        cefr_level3=row['CEFR_level3']
        if isinstance(pos3, str) and isinstance(cefr_level3, str):
            entry[cefr_level3.strip()]=pos3.strip()
        #
        word_plural=row['plural']
        if isinstance(word_plural, str):
            entry['plural']=word_plural.strip()
        #
        words.append(entry)
    #
    if Verbose_Flag:
        print(f'{words=}')
        print(f'{words_plurals=}')
    #
    print(f'{len(words):>{Numeric_field_width}} entries in {sheetname}')
    #
    return [words, words_plurals, df]

# return a tripple of words, words_plurals, dataframe
def read_CEFRLLex_data(filenamme, sheetname):
    global Verbose_Flag
    #
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
    #
    # use a list as there may be multiple instances of a given word, due to multiple contexts
    words = []
    #
    # use a set as we only care about the unique plural words
    words_plurals = set()
    #
    for index, row in  df.iterrows():
        word=row['word']
        # skip words that are just a space
        if word == ' ':
            continue
        if Verbose_Flag:
            print(f"{index=} {word=}")
        #
        pos=row['tag']
        #
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
        #
        # use the POS from the most frequently occuring usage
        key_max = max(zip(cefr_levels.values(), cefr_levels.keys()))[1]  
        #
        entry={'word': word, 'pos': pos, 'cefr_level': key_max}
        #
        words.append(entry)
    #
    if Verbose_Flag:
        print(f'{words=}')
        print(f'{words_plurals=}')
    #
    print(f'{len(words):>{Numeric_field_width}} entries in {sheetname}')
    #
    return [words, words_plurals, df]

# return a tripple of words, words_plurals, dataframe
def read_Kelly_data(filenamme, sheetname):
    global Verbose_Flag
    #
    df = pd.read_excel(open(filenamme, 'rb'), sheet_name=sheetname)
    #
    if Verbose_Flag:
        print(f'{df.columns=}')
    #
    # use a list as there may be multiple instances of a given word, due to multiple contexts
    words = []
    #
    # use a set as we only care about the unique plural words
    words_plurals = set()
    #
    for index, row in  df.iterrows():
        word=row['Swedish items for translation\n'] #  note the original has a new line at the end of the string!
        if Verbose_Flag:
            print(f"{index=} {word=}")
        #
        pos=row['Word classes\n'] #  note the original has a new line at the end of the string!
        cefr_level=row['CEFR levels']
        if isinstance(pos, str) and isinstance(cefr_level, str):
            entry={'word': word, cefr_level.strip(): pos.strip()}
        else:
            entry={'word': word}
        #
        words.append(entry)
    #
    if Verbose_Flag:
        print(f'{words=}')
    #
    words_dict=convert_Kelly_list_to_dict(words)
    print(f'{len(words_dict):>{Numeric_field_width}} entries in {sheetname}')
    #
    return [words_dict, words_plurals, df]

# convert multiple instance in the list to combined entries in a dict
# for example: 'adjö': {'C2': 'interj,noun-ett'}
# and 'ett': {'A1': 'numeral,det', 'B1': 'pronoun'}
# and  'sex': {'A1': 'numeral', 'B2': 'noun-ett'}
def convert_Kelly_list_to_dict(kelly_list):
    global Verbose_Flag
    kelly_set=set()
    words_kelly_swedish_dict=dict()
    #
    kelly_duplicate_set=set()
    for w in kelly_list:
        word=w['word']
        if word in kelly_set:
            kelly_duplicate_set.add(word)
            if Verbose_Flag:
                print(f'duplicate word in Kelly data: {word}')
        else:
            kelly_set.add(word)
    #
    if Verbose_Flag:
        print(f'duplicate words: {kelly_duplicate_set=}')
    #
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
    #
    if Verbose_Flag:
        print(f'{words_kelly_swedish_dict=}')
    #
    if Verbose_Flag:
        print(f'list of {len(kelly_list)} converted to a dict with {len(words_kelly_swedish_dict)} entries')
    return words_kelly_swedish_dict

# return a tripple of swedish_words, english_words, dataframe
def read_KTH_svensk_engelska_ordbok_file(filenamme, sheetname):
    global Verbose_Flag
    #
    df = pd.read_excel(open(filenamme, 'rb'), sheet_name=sheetname)
    #
    if Verbose_Flag:
        print(f'{df.columns=}')
    if not 'Svensk term' in df.columns or\
       not 'Engelsk översättning' in df.columns or\
       not 'Synonymer' in df.columns:
        print('Unexpected missisng column(s) in spreadsheet')
        return [swedish_words, english_words, df]
    #
    # use a set as each entry should be unique
    swedish_words = set()
    english_words = set()
    english_synonyms = set()
    #
    for index, row in  df.iterrows():
        swedish_word=row['Svensk term'] # note that these strings may include spaces
        english_word=row['Engelsk översättning'] # note that these strings may include spaces
        english_synonym=row['Synonymer'] # note that these strings may include spaces
        if Verbose_Flag:
            print(f"{index=} {swedish_word=} {english_word=} {english_synonym=}")
        #
        if isinstance(swedish_word, str):
            swedish_words.add(swedish_word)
        if isinstance(english_word, str):
            english_words.add(english_word)
    #
    if Verbose_Flag:
        print(f'{swedish_words=} {english_words=}')
    #
    # words_dict=convert_Kelly_list_to_dict(words)
    # print(f'{len(words_dict):>{Numeric_field_width}} entries in {sheetname}')
    print(f'{len(swedish_words):>{Numeric_field_width}} Swedish entries in KTH svensk-engelska ordbok')
    return [swedish_words, english_words, df]

# return a tripple of words, words_plurals, dataframe
def read_AVL_data(filename, sheetname):
    global Verbose_Flag
    #
    df = pd.read_excel(open(filename, 'rb'), sheet_name=sheetname)
    # the spreadsheet columns are:
    # ID	band	status	word	Pos	COCA-All	COCA-Acad	ratio	disp	range
    # use a list as there may be multiple instances of a given word, due to multiple contexts
    words = []
    #
    if Verbose_Flag:
        print(f"processing '{filename}'")
    for index, row in  df.iterrows():
        id=row['ID']
        word=row['word']
        if Verbose_Flag:
            print(f"{index=} {id=} {word=}")
        #
        pos=row['Pos']

        if not (word) and id == 2523: #  2523 the word is FALSE, but the pos is 'j'
            if Verbose_Flag:
                print(f"{index=} {id=} {word=} {pos=}")
            word='false'
        elif not isinstance(word, str):
            if isinstance(word, float) and math.isnan(word):
                if Verbose_Flag:
                    print(f"{index=} {id=} {word=} {pos=}")
                if id == 8729:
                    word ='null' # with pos j
                if id == 17841:
                    word ='nan' # with pos n

        entry={'word': word, 'pos': pos}
        #
        words.append(entry)
    #
    if Verbose_Flag:
        print(f'{words=}')
    #
    print(f'{len(words):>{Numeric_field_width}} entries in {sheetname}')
    #
    return [words, df]


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


def extract_acronym(w):
    # definitions have the forms:
    # "variational autoencoder (VAE)"
    # or
    # "AI - Artificial Intelligence"
    if w.endswith(')'):
        left_paren_offset=w.find('(')
        if left_paren_offset >= 0 and left_paren_offset < (len(w)-1):
            return w[left_paren_offset+1:-1]
    if w.count(' - ') == 1:
        end_of_acronym=w.find(' - ')
        return w[:end_of_acronym]
    return ''


def noun_cefr_levels(my_dict):
    levels=dict()
    for cl in ['A1', 'A2', 'B1', 'B2', 'C1', 'C2', 'XX']:
        cefr_level=my_dict.get(cl, False)
        if cefr_level and isinstance(cefr_level, str):
            pos = [s.strip() for s in cefr_level.split(',')]
            for ps in pos:
                if ps == 'noun':
                    levels[cl]='noun'
    return levels

def main():
    global Verbose_Flag
    global directory_prefix
    #
    directory_prefix='/tmp/'
    #
    parser = optparse.OptionParser()
    #
    parser.add_option('-v', '--verbose',
                      dest="verbose",
                      default=False,
                      action="store_true",
                      help="Print lots of output to stdout"
    )
    #
    parser.add_option('--testing',
                      dest="testing",
                      default=False,
                      action="store_true",
                      help="Run in testing mode"
    )
    #
    parser.add_option('--self',
                      dest="self",
                      default=False,
                      action="store_true",
                      help="compare the AVL words with avl_words, i.e. those with CEFR information"
    )
    #
    parser.add_option('--avl',
                      dest="avl",
                      default=False,
                      action="store_true",
                      help="include the avl_words when checking for missing words"
    )
    #
    parser.add_option('--Swedish',
                      dest="swedish",
                      default=False,
                      action="store_true",
                      help="Run in testing mode"
    )
    #
    options, remainder = parser.parse_args()
    #
    Verbose_Flag=options.verbose
    if Verbose_Flag:
        print("ARGV      : {}".format(sys.argv[1:]))
        print("VERBOSE   : {}".format(options.verbose))
        print("REMAINING : {}".format(remainder))
    #
    unique_words=dict()
    #
    # load in the information about CEFR levels from the various sources
    #################################################################################
    print('Loading some directories')
    directory_location="/z3/maguire/Language_Committee/"
    #directory_location="/home/maguire/Language_Committee/"
    # american_3000_file=directory_location+"American_Oxford_3000.xlsx"
    # american_3000_words, american_3000_words_plurals, american_3000_df=read_cefr_data(american_3000_file, 'American3000')
    # american_5000_words, american_5000_words_plurals, american_5000_df=read_cefr_data(american_3000_file, 'American5000')
    import oxford
    american_3000_words=dict()
    american_3000_words_plurals=dict()
    for w in oxford.american3000_English_words:
        my_dict = {k: v for k, v in oxford.american3000_English_words.get(w).items() if k != 'plural'}
        american_3000_words[w]=my_dict
        p = oxford.american3000_English_words.get(w).get('plural', False)
        if p:
            if isinstance(p, str):
                american_3000_words_plurals[p]=noun_cefr_levels(my_dict)
            elif isinstance(p, list):
                for pi in p:
                    american_3000_words_plurals[pi]=noun_cefr_levels(my_dict)
            else:
                print(f'*** unexpected case in handling plural for {w} in  american3000_English_words')

    american_5000_words=dict()
    american_5000_words_plurals=dict()
    for w in oxford.american5000_English_words:
        my_dict = {k: v for k, v in oxford.american5000_English_words.get(w).items() if k != 'plural'}
        american_5000_words[w]=my_dict
        p = oxford.american5000_English_words.get(w).get('plural', False)
        if p:
            if isinstance(p, str):
                american_5000_words_plurals[p]=noun_cefr_levels(my_dict)
            elif isinstance(p, list):
                for pi in p:
                    american_5000_words_plurals[pi]=noun_cefr_levels(my_dict)
            else:
                print(f'*** unexpected case in handling plural for {w} in  american5000_English_words')

    # include also the British English words
    # note that plurals are not in the original list of words - but were added
    oxford_3000_words=dict()
    oxford_3000_words_plurals=dict()
    for w in oxford.oxford3000_English_words:
        my_dict = {k: v for k, v in oxford.oxford3000_English_words.get(w).items() if k != 'plural'}
        oxford_3000_words[w]=my_dict
        if p:
            if isinstance(p, str):
                oxford_3000_words_plurals[p]=noun_cefr_levels(my_dict)
            elif isinstance(p, list):
                for pi in p:
                    oxford_3000_words_plurals[pi]=noun_cefr_levels(my_dict)
            else:
                print(f'*** unexpected case in handling plural for {w} in  oxford3000_English_words')

    oxford_5000_words=dict()
    oxford_5000_words_plurals=dict()
    for w in oxford.oxford5000_English_words:
        oxford_5000_words[w]=my_dict
        if p:
            if isinstance(p, str):
                oxford_5000_words_plurals[p]=noun_cefr_levels(my_dict)
            elif isinstance(p, list):
                for pi in p:
                    oxford_5000_words_plurals[pi]=noun_cefr_levels(my_dict)
            else:
                print(f'*** unexpected case in handling plural for {w} in  oxford5000_English_words')

    if Verbose_Flag:
        print(f'{american_3000_words=}')
        print(f'{american_3000_words_plurals=}')

    print(f'{(len(american_3000_words)+len(american_3000_words_plurals)):>{Numeric_field_width}} words in Oxford American 3000 words (including plurals)')
    print(f'{(len(american_5000_words)+len(american_5000_words_plurals)):>{Numeric_field_width}} words in Oxford American 5000 words  (including plurals)')
    print(f'{(len(oxford_3000_words)+len(oxford_3000_words_plurals)):>{Numeric_field_width}} words in Oxford 3000 words (with added plurals)')
    print(f'{(len(oxford_5000_words)+len(oxford_5000_words_plurals)):>{Numeric_field_width}} words in Oxford 5000 words  (with added plurals)')

    #
    cefrlex_file=directory_location+"cefrlex-reduced.xlsx"
    words_EFLLex, plurals_EFLLex, df_EFLLex=read_CEFRLLex_data(cefrlex_file, 'EFLLex_NLP4J')
    #
    words_SVALex, plurals_SVALex, df_SVALex=read_CEFRLLex_data(cefrlex_file, 'SVALex_Korp')
    #
    kelly_swedish_file=directory_location+"Swedish-Kelly_M3_CEFR.xlsx"
    words_kelly_swedish, plurals_kelly_swedish, df_kelly_swedish=read_Kelly_data(kelly_swedish_file, 'Swedish_M3_CEFR')

    # entries in the dict will have the form: 'acronym': ['expanded form 1', 'expanded form 2',  ... ]
    well_known_acronyms=dict()
    for e in common_acronyms.well_known_acronyms_list:
        if len(e) >= 1:
            ack=e[0]
            if len(e) >= 2:
                d=e[1]
                current_entry=well_known_acronyms.get(ack, list())
                current_entry.append(d)
                well_known_acronyms[ack]=current_entry
    print(f'{(len(well_known_acronyms)):>{Numeric_field_width}} unique acronyms in ({len(common_acronyms.well_known_acronyms_list)}) (unique) well_known_acronyms')

    #
    # KTH:s svensk-engelska ordbok
    KTH_svensk_engelska_ordbok_file=directory_location+"kth-ordboken-version-2023-07-01.xlsx"
    words_KTH_swedish, words_KTH_english, df_KTH_svensk_engelska_ordbok=read_KTH_svensk_engelska_ordbok_file(KTH_svensk_engelska_ordbok_file, 'Sheet1')
    #
    # look for the levels for the KTH words
    for w in words_KTH_swedish:
        if w.endswith('(amerikansk engelska)'):
            w=w.replace('(amerikansk engelska)', '')
        w=w.strip()
        if len(w) == 1 and ord(w) == 776: # if just a COMBINING DIAERESIS, skip it
            continue
        
        if w not in common_english_and_swedish.KTH_ordbok_Swedish_with_CEFR:
            # skip acronyms
            if w in well_known_acronyms:
                continue
            if w in miss_spelled_to_correct_spelling.miss_spelled_to_correct_spelling:
                continue
            levels=common_english_and_swedish.common_swedish_words.get(w, False)
            if levels:
                print(f"'{w}': {levels},")
            else:
                if Verbose_Flag:
                    print(f'missing Swedish: {w}')
    #
    for w in words_KTH_english:
        if w.endswith('(amerikansk engelska)'):
            w=w.replace('(amerikansk engelska)', '')
        w=w.strip()
        if w not in common_english_and_swedish.KTH_ordbok_English_with_CEFR:
            # skip acronyms
            if w in well_known_acronyms:
                continue
            if w in miss_spelled_to_correct_spelling.miss_spelled_to_correct_spelling:
                continue
            levels=common_english_and_swedish.common_English_words.get(w, False)
            if levels:
                print(f"'{w}': {levels},")
            else:
                if Verbose_Flag:
                    print(f'missing English: {w}')

    avl_file=directory_location+"AVL-allWords.xlsx"
    words_AVL, df_AVL=read_AVL_data(avl_file, 'list')


    #
    print(f'{len(common_english_and_swedish.common_English_words):>{Numeric_field_width}} words in common English words')
    #
    print(f'{len(common_english_and_swedish.common_swedish_words):>{Numeric_field_width}} words in common Swedish words')
    #
    print(f'{len(common_english_and_swedish.common_swedish_technical_words):>{Numeric_field_width}} words in common Swedish technical words')
    #
    print(f'{len(common_english_and_swedish.common_danish_words):>{Numeric_field_width}} words in common Danish words')
    #
    print(f'{len(common_english_and_swedish.common_french_words):>{Numeric_field_width}} words in common French words')
    #
    print(f'{len(common_english_and_swedish.common_finnish_words):>{Numeric_field_width}} words in common Finnish words')
    #
    print(f'{len(common_english_and_swedish.common_german_words):>{Numeric_field_width}} words in common German words')
    #
    print(f'{len(common_english_and_swedish.common_icelandic_words):>{Numeric_field_width}} words in common Icelandic words')
    #
    print(f'{len(common_english_and_swedish.common_italian_words):>{Numeric_field_width}} words in common Italian words')
    #
    print(f'{len(common_english_and_swedish.common_latin_words):>{Numeric_field_width}} words in common Latin words')
    #
    print(f'{len(common_english_and_swedish.common_norwegian_words):>{Numeric_field_width}} words in common Norwegian words')
    #
    print(f'{len(common_english_and_swedish.common_portuguese_words):>{Numeric_field_width}} words in common Portuguese words')
    #
    print(f'{len(common_english_and_swedish.common_spanish_words):>{Numeric_field_width}} words in common Spanish words')
    #
    print(f'{len(common_english_and_swedish.common_units):>{Numeric_field_width}} words in common units')
    #
    print(f'{len(common_english_and_swedish.names_of_persons):>{Numeric_field_width}} words in names_of_persons')
    print(f'{len(common_english_and_swedish.place_names):>{Numeric_field_width}} words in place_names')
    print(f'{len(common_english_and_swedish.company_and_product_names):>{Numeric_field_width}} words in company_and_product_names')
    print(f'{len(common_english_and_swedish.misc_words_to_ignore):>{Numeric_field_width}} words in misc_words_to_ignore')
    print(f'{len(words_to_ignore):>{Numeric_field_width}} words in words_to_ignore')
    print(f'{len(common_english_and_swedish.mathematical_words_to_ignore):>{Numeric_field_width}} words in mathematical_words_to_ignore')
    print(f'{len(common_english_and_swedish.programming_keywords):>{Numeric_field_width}} words in programming_keywords')
    print(f'{len(common_english_and_swedish.language_tags):>{Numeric_field_width}} words in language_tags')
    print(f'{len(diva_merged_words.merged_words):>{Numeric_field_width}} words in merged_words')
    print(f'{len(miss_spelled_to_correct_spelling.miss_spelled_to_correct_spelling):>{Numeric_field_width}} words in miss_spelled_to_correct_spelling')
    print(f'{len(common_english_and_swedish.abbreviations_ending_in_period):>{Numeric_field_width}} words in abbreviations_ending_in_period')
    print(f'{len(words_AVL):>{Numeric_field_width}} words in AVL')
    print(f'{len(AVL_words_with_CEFR.avl_words):>{Numeric_field_width}} words in AVL_words_with_CEFR.avl_words')

    #
    # entries in the dict will have the form: 'acronym': ['expanded form 1', 'expanded form 2',  ... ]
    well_known_acronyms=dict()
    for e in common_acronyms.well_known_acronyms_list:
        if len(e) >= 1:
            ack=e[0]
            if len(e) >= 2:
                d=e[1]
                current_entry=well_known_acronyms.get(ack, list())
                current_entry.append(d)
                well_known_acronyms[ack]=current_entry
    print(f'{(len(well_known_acronyms)):>{Numeric_field_width}} unique acronyms in ({len(common_acronyms.well_known_acronyms_list)}) (dict) well_known_acronyms')
    #
    words_not_found=[]
    #
    if options.self:
        for word in words_AVL:
            w=word['word']
            pos=word['pos']
            if w in AVL_words_with_CEFR.avl_words:
                continue
            words_not_found.append(word)
            print(f"{w=}, {pos}")
        print(f'{len(words_not_found)} in words_not_found')
        return
    
    # if the self option is not specified, execute the following code
    for word in words_AVL:
        w=word['word']
        pos=word['pos']
        if w in common_english_and_swedish.top_100_English_words:
            continue
        if w in common_english_and_swedish.thousand_most_common_words_in_English:
            continue
        if w in american_3000_words:
            continue
        if w in american_5000_words:
            continue
        if w in oxford_3000_words:
            continue
        if w in oxford_5000_words:
            continue
        if w in words_EFLLex:
            continue
        if w in well_known_acronyms:
            continue
        if w in common_english_and_swedish.common_English_words:
            continue

        if options.avl:
            if w in AVL_words_with_CEFR.avl_words:
                continue
        words_not_found.append(word)
        print(f"{w=}, {pos}")
    print(f'{len(words_not_found)} in words_not_found')
    #
    # look at POS information
    #
    words_not_found=[]
    #
    levels_found=set()
    bogus_levels=set()
    all_pos_found=set()
    #
    available_cefr_levels=['A1', 'A2', 'B1', 'B2', 'C1', 'C2', 'XX']
    # for word in words_AVL:
    #     w=word['word']
    #     pos=word['pos']
    #     if w in AVL_words_with_CEFR.avl_words:
    for w in AVL_words_with_CEFR.avl_words:
        pos_for_word=AVL_words_with_CEFR.avl_words[w]
        entry_found_level= [k for k, v in pos_for_word.items()]

        #print(f"{w}: {pos_for_word=}: {entry_found_level}")
        for cl in entry_found_level:
            if cl not in available_cefr_levels:
                print(f"{w}: {pos_for_word=}: {entry_found_level}")
                bogus_levels.add(cl)
                
        if pos_for_word:
            for cl in available_cefr_levels:
                cefr_level=pos_for_word.get(cl, False)
                if cefr_level and isinstance(cefr_level, str):
                    pos = [s.strip() for s in cefr_level.split(',')]
                    for ps in pos:
                        if ps == 'verb' or ps == 'noun' or ps == "Adj":
                            print(f"{w}: {pos_for_word=}: {entry_found_level}")
                        all_pos_found.add(ps)

    if len(bogus_levels) > 0:
        print("Found some bogus CEFR levels, for the following entries")
        print(f"{bogus_levels=}")

    print(f"{sorted(all_pos_found)=}")

    # check overlapp with other sources
    avl_missing_from_american_3000_words=[]
    for w in american_3000_words:
        if w not in AVL_words_with_CEFR.avl_words:
            avl_missing_from_american_3000_words.append(w)

    print(f"{len(avl_missing_from_american_3000_words)=}")
    if len(avl_missing_from_american_3000_words) > 0:
        print(f"{avl_missing_from_american_3000_words=}")

    avl_missing_from_american_5000_words=[]
    for w in american_5000_words:
        if w not in AVL_words_with_CEFR.avl_words:
            avl_missing_from_american_5000_words.append(w)

    print(f"{len(avl_missing_from_american_5000_words)=}")
    if len(avl_missing_from_american_5000_words) > 0:
        print(f"{avl_missing_from_american_5000_words=}")

    ce_missing_words=[]
    for w in avl_missing_from_american_3000_words:
        if w in well_known_acronyms:
            continue
        if w not in common_english_and_swedish.common_English_words:
            ce_missing_words.append(w)
    for w in avl_missing_from_american_5000_words:
        if w in well_known_acronyms:
            continue
        if w not in common_english_and_swedish.common_English_words:
            ce_missing_words.append(w)

    print(f"{len(ce_missing_words)=} {ce_missing_words=}")

    #american_5000_words:
    #oxford_3000_words:
    #oxford_5000_words:

    avl_missing_words=[]
    for w in AVL_words_with_CEFR.avl_words:
        if w not in common_english_and_swedish.common_English_words:
            avl_missing_words.append(w)

    print(f"{len(avl_missing_words)=} {avl_missing_words=}")

    
#
if __name__ == "__main__": main()

