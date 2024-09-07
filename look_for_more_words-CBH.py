#!/usr/bin/env python3
### /usr/bin/python3
# -*- coding: utf-8 -*-
# -*- mode: python; python-indent-offset: 4 -*-
#
# ./look_for_more_words-CBH.py filename
# 
# The program opens the file and filters the words aginst a set of dictionaries.
#
# Examples:
# ./look_for_more_words-CBH.py /tmp/unique_words-abstracts-English.json
# ./look_for_more_words-CBH.py /tmp/paired-keywords-CBH.json
#
# to process paired keywords file - key is the english term and the value is the corresponding Swedish term
# ./look_for_more_words.py --keywords /tmp/unique_words-abstracts-English.json
#
# You can also take the multiple word entries in common_English_words, split into individual words
# and feed these into the program - as if they were in the input unique words:
# ./look_for_more_words.py --self /tmp/unique_words-abstracts-English.json
#
# Useful Gemini prompt: 
#Please generate python dict with the POS and CEFR levels of the following Swedish words. The format of each dict  element should be {'word': {'A1': 'pos', 'A2': 'pos', 'B1': 'pos', 'B2': 'pos', 'C1': 'pos', 'C2': 'pos'}, The levels and part of speech only need to be included when relevant to the word.
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
sys.path.append('/home/maguire/Canvas/Canvas-tools')

#  as common_English_words, common_swedish_words, common_swedish_technical_words
import common_english
import common_swedish
import miss_spelled_to_correct_spelling_CBH
import common_acronyms_CBH
import diva_merged_words
import diva_merged_words_CBH
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
    for u in common_english.common_units:
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
    '17.3/17.3-coating',
    '17.3/17.3-coatings',
    '17.3/4.3-coating',
    '17.3/4.3-coatings',
    '18:1n-9',
    '18:2n-6',
    '3:8b:Instruct',
    '4,467,000Nm',
    '47%70',
    '48:52',
    '4:1',
    "tris[4,4'-bis",
    "tris[poly",
    "􀃅",
    "􀜥􁈻",
    "􀜴",
    "􀜴􀜱",
    "􀜸",
    "􀜸􀜤􀜫􀜱",
    "􀜸􀜴􀜱",
    "􀵆",
    "􀵆24.4",
    'pp.926-937',
    '́',
    '́s',
    '̊',
    '‑',
    '‡',
    '€335,000',
    "5-,10",
    "5-­‐40",
    "5.6*10",
    "50:50",
    "6,6,6,14",
    "6.8*10",
    "60:40",
    "61000-2-6:1995",
    "6509-1:2014",
    "650m2/g",
    "6:1",
    "7.2.1",
    "7.2.3",
    "7.3.1",
    "7.3.2",
    "70:30",
    "75:50",
    "7:3",
    "8.99*10-6",
    "80g/m2",
    "84:1997",
    "9001:2015",
    "95:5",
    "98‑116",
    "9:6",
    "9:8,5:2,5",
    "9p21.3",
    "0.0210.045",
    "0.032,0.023",
    "0.10.28",
    "1%Pt/Al2O3",
    "1,065,000",
    "1,1x10-4",
    "1,219,000",
    "1.03.0",
    "1.49*10-6",
    "1.5:1",
    "1.5mm2",
    "1.6.2",
    "10%-~50",
    "104.6270.3",
    "10:1",
    "12464-1:2011",
    "12:88",
    "12s1p",
    "13485:2016",
    "14040:2006",
    "150x150mm",
    "16:1n-7",
    "1924-2:1994",
    "1994;367",
    "1998:1",
    "1:1,5",
    "1:1-1:4",
    "1:100",
    "1:1000",
    "1:2",
    "1:20",
    "1:200",
    "1:3",
    "1:4",
    "1:5",
    "1:6",
    "1:9",
    "1h30",
    "2001:1",
    "2004;27",
    "2005:16",
    "2010;110",
    "2013:1",
    "2013;84",
    "2018:1",
    "204:2001",
    "20:5n-3",
    "20:80",
    "22:46717860C&gt;T",
    "22:6-n-3",
    "22q11.2",
    "24m2",
    "250x4.6",
    "2df.2p",
    "2x10",
    "2‑35",
    "3,4,6,7",
    "3.040Vs1m",
    "3.2.1.78",
    "3.62*10-5",
    "3.90*10-6",
    "300m2/g",
    "30:70",
    "35/65,20/80",
    "39.27cm3",
    "3:43:44:0mm3with",
    "3:8b",
    "mg/m2",
    'IEC',
    'IEC--1',
    'IEC-60255-187-1',
    'IEC-60287',
    'IEC-61508',
    'IEC-63442',
    'IEC61499,',
    'KPIECE',
    "cm􀀀3",
    '​', # 0x200b
    '‌', # 0x200c
    'nm/4',
    'H<sub>∞</sub>',
    'style=\'text-decoration:overline\'>2</span>1',
    "style=\"text-decoration:overline\">2</span>1",
    '-',
    '--',
    '&amp;',
    '&lt;',
    '[.]',
    "\'",
    '<7p>',
    'IEC--1',
    'IEC-60255-187-1',
    'IEC-61508',
    'ISO26262',
    '[BIT16]',
    '[mac71]',
    'v1',
    'v1080',
    '0-90',
    '2..6',
    '2..69',
    '24:5',
    '4{5',
    '6m/s2',
    '6m/s2.',
    '89.85',
    '8×8',
    '1,486,800,000',
    '185,665.97',
    'swastika/penis', # diva2:1198914
    '9.515.8',
    'v4.2',
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

CBH_capitals={
    'A-mode': {'B2': 'Noun'},
    'AOs': {'C2': 'Noun'},
    'ATPase': {'B2': 'Noun'},
    'Ac-CoA': {'B2': 'Noun'},
    'B-cell': {'B2': 'Noun'},
    'B-cells': {'B2': 'Noun'},
    'B-domain': {'C1': 'Noun'},
    'B-particles': {'C2': 'Noun'},
    'B.subtili': {'B2': 'Noun'},
    'B.subtilis': {'B1': 'Noun'},
    'B0-inhomogeneities': {'C1': 'Noun'},
    'BA-operation': {'B2': 'Noun'},
    'BA-operations': {'B2': 'Noun'},
    'BA-operatives': {'B2': 'Noun'},
    'BALB/c': {'C1': 'Noun'},
    'BAM-files': {'C1': 'Noun'},
    'BBM:s': {'B2': 'Noun'},
    'BCRs': {'B2': 'Noun'},
    'BCa': {'B2': 'Noun'},
    'BED-files': {'C1': 'Noun'},
    'BEVs': {'B1': 'Noun'},
    'BFB-boiler': {'C1': 'Noun'},
    'BFRs': {'B2': 'Noun'},
    'BFs': {'B2': 'Noun'},
    'BGEs': {'B2': 'Noun'},
    'BICseq': {'B2': 'Noun'},
    'BIS-lists': {'C1': 'Noun'},
    'BMCs': {'B2': 'Noun'},
    'BMD-levels': {'C1': 'Noun'},
    'BMD-values': {'C1': 'Noun'},
    'BMI,diabetes': {'B2': 'Noun'},
    'BP-b-PSBMA': {'C2': 'Noun'},
    'BP-b-PSBMA200': {'C2': 'Noun'},
    'BRFs': {'B2': 'Noun'},
    'BSA-containing': {'C1': 'Adjective'},
    'BSc': {'A2': 'Noun'},
    'BaO': {'B2': 'Noun'},
    'BaSO': {'B2': 'Noun'},
    'Bacillus': {'B1': 'Noun'},
    'Bacteroides': {'B1': 'Noun'},
    'Bacteroidetes': {'B1': 'Noun'},
    'Bacteroidia': {'B2': 'Noun'},
    'Balm': {'B2': 'Noun'},
    'Begonia': {'B2': 'Noun'},
    'Begoniaceae': {'B2': 'Noun'},
    'Bendtsen': {'B2': 'Noun'},
    'Benson': {'B2': 'Noun'},
    'Benzophenone': {'B2': 'Noun'},
    'Benzylalcohol': {'B2': 'Noun'},
    'Berga': {'B2': 'Noun'},
    'Beta-synuclein': {'B2': 'Noun'},
    'Biacore': {'B2': 'Noun'},
    'Bifidobacterium': {'B2': 'Noun'},
    'Biodesign': {'B2': 'Noun'},
    'Bioelectronic': {'B2': 'Adjective'},
    'Biologique': {'B1': 'Adjective'},
    'Blanc': {'B1': 'Adjective'},
    'Boer': {'B2': 'Noun'},
    'Bolivar': {'B1': 'Noun'},
    'Botch': {'B2': 'Verb'},
    'Bradford': {'B1': 'Noun'},
    'Braga': {'B1': 'Noun'},
    'Brest': {'B1': 'Noun'},
    'Bueno': {'A1': 'Adjective'},
    'C-pep': {'C1': 'Noun'},
    'C-peptide': {'B2': 'Noun'},
    'C-terminus': {'C1': 'Noun'},
    'C1q': {'C1': 'Noun'},
    'C:N-ratio': {'C1': 'Noun'},
    'CAD-software': {'B2': 'Noun'},
    'CAZymes': {'C1': 'Noun'},
    'CBMs': {'C1': 'Noun'},
    'CBs': {'C1': 'Noun'},
    'CD16a': {'C1': 'Noun'},
    'CDPFs': {'C1': 'Noun'},
    'CE-mark': {'B2': 'Noun'},
    'CFMEs': {'C1': 'Noun'},
    'CFs': {'C1': 'Noun'},
    'CGMs': {'C1': 'Noun'},
    'Carmen': {'A1': 'Noun'},
    'Cas9': {'C2': 'Noun'},
    'Casein-Yeast': {'C2': 'Noun'},
    'Caspase-3': {'C2': 'Noun'},
    'Caspian': {'B1': 'Adjective'},
    'Caulobacter': {'C2': 'Noun'},
    'CdS': {'C2': 'Noun'},
    'CdTe': {'C2': 'Noun'},
    'Ce3-Ce4': {'C2': 'Noun'},
    'CeBr': {'C2': 'Noun'},
    'CeCl': {'C2': 'Noun'},
    'Cell-picker': {'C2': 'Noun'},
    'Cell-pickers': {'C2': 'Noun'},
    'CellCelektor': {'C2': 'Noun'},
    'CellTM': {'C2': 'Noun'},
    'Cellcolabs': {'C2': 'Noun'},
    'Cellruptor': {'C2': 'Noun'},
    'Cellufil': {'C2': 'Noun'},
    'Cellupsheres': {'C2': 'Noun'},
    'Cellutech': {'C2': 'Noun'},
    'Centriair': {'C2': 'Noun'},
    'Centro': {'A1': 'Noun'},
    'Centro-group': {'B1': 'Noun'},
    'Cepheid': {'B2': 'Noun'},
    'Ceratocystis': {'C2': 'Noun'},
    'Cetrimonium': {'C2': 'Noun'},
    'ChIP-qPCR': {'C2': 'Noun'},
    'ChIP-sequencing': {'C2': 'Noun'},
    'Chapagain': {'B1': 'Noun'},
    'Chapman-Jouget': {'C2': 'Noun'},
    'Charpy': {'B2': 'Noun'},
    'Chat-Bison': {'C2': 'Noun'},
    'Chat-bison': {'C2': 'Noun'},
    'Chatbot-optimization': {'C1': 'Noun'},
    'Chem': {'B1': 'Noun'},
    'Chemcad': {'C2': 'Noun'},
    'Chemical/solvent': {'B1': 'Noun'},
    'Chimie': {'B1': 'Noun'},
    'Cinderella': {'A1': 'Noun'},
    'Circulated': {'B1': 'Verb'},
    'Cochabamba': {'B1': 'Noun'},
    'Coconut-based': {'B2': 'Adjective'},
    'CodeLink': {'B2': 'Noun'},
    'Coeruleus': {'C2': 'Adjective'},
    'Collagen-PEG-Maleimide': {'C2': 'Noun'},
    'Collagen-PEG-maleimide': {'C2': 'Noun'},
    'Collect/Click': {'A2': 'Verb'},
    'Comamonas': {'C2': 'Noun'},
    'Communcication': {'A2': 'Noun'}, 
    'CompactRIO': {'B2': 'Noun'},
    'Compl': {'B2': 'Noun'}, 
    'Compton': {'B2': 'Noun'}, 
    'Comptoninteractions': {'C1': 'Noun'},
    'Con-24hrs': {'B1': 'Noun'},
    'ConTA': {'B2': 'Noun'},
    'Concanavalin': {'C2': 'Noun'},
    'Conclusion:Powered': {'B1': 'Noun'},
    'ConclusionThe': {'B1': 'Noun'},
    'Concurring': {'C1': 'Adjective'},
    'Condensée': {'B1': 'Adjective'}, 
    'Condias': {'B2': 'Noun'},
    'Confidentiality-Integrity-Availability': {'C1': 'Noun'},
    'Conscia': {'B2': 'Noun'},
    'Consid': {'B2': 'Noun'},
    'ControlFreeC': {'B2': 'Noun'},
    'Cordillera': {'B2': 'Noun'},
    'Corringer': {'B2': 'Noun'}, 
    'Cortus': {'C2': 'Noun'},
    'Coscinodiscus': {'C2': 'Noun'},
    'CountVectorsFeaturizer': {'C2': 'Noun'},
    'CpG': {'C2': 'Noun'},
    'Cpigenome-Wide': {'C2': 'Adjective'},
    'Cpin': {'C2': 'Noun'},
    'Cpin_2580': {'C2': 'Noun'},
    'Cpin_2580-18s': {'C2': 'Noun'},
    'CrN': {'C2': 'Noun'},
    'Crespo': {'B1': 'Noun'}, 
    'Crispant': {'C1': 'Adjective'}, 
    'Cristian': {'A2': 'Noun'},
    'Crompack': {'B2': 'Noun'},
    'Cross-hatch': {'B2': 'Verb'},
    'CrossFit®': {'B1': 'Noun'},
    'Cruciate': {'C1': 'Adjective'},
    'CrystalViolet': {'C1': 'Noun'},
    'Cu-based': {'C1': 'Adjective'},
    'Cura': {'A1': 'Noun'},
    'Cyanobateria': {'B2': 'Noun'},
    'Cyperus': {'B2': 'Noun'},
    'D-dimer': {'C1': 'Noun'},
    'DNA-regions': {'C1': 'Noun'},
    'DNAintegrity': {'C1': 'Noun'},
    'DNNs': {'C1': 'Noun'},
    'DNS-queries': {'C1': 'Noun'},
    'DNSSEC-secured': {'C1': 'Adjective'},
    'DNSSEC-signed': {'C1': 'Adjective'},
    'DOC-concentration': {'C1': 'Noun'},
    'DOC-levels': {'C1': 'Noun'},
    'DOC-reduction': {'C1': 'Noun'},
    'DOC-removal': {'C1': 'Noun'},
    'DOTA-chelator': {'C1': 'Noun'},
    'DPFs': {'C1': 'Noun'},
    'DPP-catalysed': {'C1': 'Adjective'},
    'DREADDs': {'C1': 'Noun'},
    'DSAc': {'C1': 'Noun'},
    'DSSCs': {'C1': 'Noun'},
    'DTs': {'C1': 'Noun'},
    'DTx': {'C1': 'Noun'},
    'DWTPs': {'C1': 'Noun'},
    'Dactylium': {'C1': 'Noun'},
    'Dahan': {'B1': 'Noun'},
    'Dajugezhuang': {'B2': 'Noun'},
    'Dame': {'A1': 'Noun'},
    'Danderyds': {'B2': 'Noun'},
    'Daniels': {'B1': 'Noun'},
    'Danio': {'C1': 'Noun'},
    'Daphnia': {'C1': 'Noun'},
    'Darcy': {'B2': 'Noun'},
    'Darknet': {'B2': 'Noun'},
    'Daudi': {'C1': 'Noun'},
    'Dax': {'B2': 'Noun'},
    'Daxx': {'C1': 'Noun'},
    'Day-1': {'B2': 'Adjective'},
    'DeCLIC': {'C1': 'Noun'},
    'DeWitte': {'B2': 'Noun'},
    'Deacetylated': {'C1': 'Adjective'},
    'Death-domain': {'C1': 'Noun'},
    'Defibrillators': {'B2': 'Noun'},
    'Dehydrins': {'C1': 'Noun'},
    'Design-study': {'B2': 'Noun'},
    'Dexa-mediated': {'C1': 'Adjective'},
    'Diazepam': {'C1': 'Noun'},
    'Diels': {'C1': 'Noun'},
    'Diels-Alderase': {'C1': 'Noun'},
    'Difformable': {'C1': 'Adjective'},
    'Diflunisal': {'C1': 'Noun'},
    'Dimensionally': {'B2': 'Adverb'},
    'Dimethicone': {'C1': 'Noun'},
    'Dipalmitoylphosphatidylcholine': {'C1': 'Noun'},
    'Discretising': {'C1': 'Verb'},
    'Dispersin': {'C1': 'Noun'},
    'DispersinB': {'C1': 'Noun'},
    'Dithiobis': {'C1': 'Noun'},
    'Dlib': {'A2': 'Noun'},
    'Dn-treated': {'B2': 'Adjective'},
    'DoD': {'B2': 'Noun'},
    'DoH': {'B2': 'Noun'},
    'Dobbins': {'B1': 'Noun'}, 
    'Docklin': {'A2': 'Noun'}, 
    'Dodecyltrimethylammonium': {'B2': 'Adjective'},
    'Domain-Derived': {'B2': 'Adjective'},
    'Dopazo': {'A2': 'Noun'}, 
    'Dosgin': {'A2': 'Noun'},
    'Dougherty': {'A2': 'Noun'},
    'Doxygen': {'B2': 'Noun'},
    'DpnI-digested': {'B2': 'Adjective'},
    'Dramatify': {'B2': 'Verb'},
    'Drevviken': {'A2': 'Noun'},
    'Drosophila': {'B2': 'Noun'},
    'Drug-loaded': {'B2': 'Adjective'},
    'Dual-Luciferase': {'B2': 'Adjective'},
    'Duan': {'A2': 'Noun'}, 
    'Duesenfeld': {'A2': 'Noun'}, 
    'Dunaliella': {'B2': 'Noun'},
    'Dut': {'A2': 'Noun'}, 
    'Dynavox': {'B1': 'Noun'},
    'Dystrophy': {'B2': 'Noun'},
    'Däckservice': {'A2': 'Noun'},
    'E-modulus': {'B2': 'Noun'},
    'E-value': {'B2': 'Noun'},
    'E4orf6': {'B2': 'Noun'},
    'EC:PC-based': {'B2': 'Adjective'},
    'ECF-mass': {'B2': 'Noun'},
    'ECFmass': {'B2': 'Noun'},
    'ECG-gated': {'B2': 'Adjective'},
    'ECM-like': {'B2': 'Adjective'},
    'ECM-scaffold': {'B2': 'Noun'},
    'ECUs': {'B2': 'Noun'},
    'ECVs': {'B2': 'Noun'},
    'ECoG': {'C2': 'Noun'},
    'ED-coatings': {'C2': 'Noun'},
    'EEGNet': {'C2': 'Noun'},
    'EF-hand': {'C2': 'Noun'},
    'EHRs': {'C1': 'Noun'},
    'EIpW': {'C2': 'Noun'},
    'EMG-based': {'C2': 'Adjective'},
    'EMG-electrodes': {'C2': 'Noun'},
    'EMG-equipment': {'C2': 'Noun'},
    'EMG-measurements': {'C2': 'Noun'},
    'EMG-shields': {'C2': 'Noun'},
    'EML4-ALK-driven': {'C2': 'Adjective'},
    'EML4-ALK-positive': {'C2': 'Adjective'},
    'EMekT': {'C2': 'Noun'},
    'EOF-measurements': {'C2': 'Noun'},
    'EOL”-battery': {'B2': 'Noun'},
    'EPR/Spin-trapping': {'C2': 'Noun'},
    'ERE-TATA-Luc': {'C2': 'Noun'},
    'ERb': {'C2': 'Noun'},
    'ESI-current': {'C2': 'Noun'},
    'ESI-needles': {'C2': 'Noun'},
    'ESI-voltage': {'C2': 'Noun'},
    'ESP-feed': {'C1': 'Noun'},
    'ESPs': {'C1': 'Noun'},
    'ESTs': {'C1': 'Noun'},
    'EUR/kg': {'B1': 'Noun'},
    'EVQuant': {'C2': 'Noun'},
    'Earthbased': {'B2': 'Adjective'},
    'Easton': {'B1': 'Noun'},
    'EasyMag': {'C2': 'Noun'},
    'EasyMining': {'C2': 'Noun'},
    'Ebecryl': {'C2': 'Noun'},
    'EchoPAC': {'C2': 'Noun'},
    'Eclat': {'C1': 'Noun'},
    'EcoSwell': {'C2': 'Noun'},
    'Ecobränsle': {'B2': 'Noun'},
    'Ecobränsles': {'B2': 'Noun'},
    'Ecohelix': {'C2': 'Noun'},
    'Ecolabel': {'B2': 'Noun'},
    'Ecoscope': {'C2': 'Noun'},
    'Electrocorticogram': {'C2': 'Noun'},
    'Enthalpy': {'C2': 'Noun'},
    'Environmental®': {'B1': 'Adjective'},
    'Environ\\xadment': {'B1': 'Noun'},
    'Eon': {'C2': 'Noun'},
    'Esther': {'A1': 'Noun'},
    'Expectedly': {'B1': 'Adverb'},
    'Falu': {'B1': 'Noun'}, 
    'Fragaria': {'B2': 'Noun'},
    'Freestyle': {'B1': 'Noun'},
    'Furtherly': {'C1': 'Adverb'},
    'Furthermore': {'B2': 'Adverb'},
    'Fussarium': {'B2': 'Noun'},
    'GC-columns': {'C1': 'Noun'},
    'GFP-fusion': {'C1': 'Noun'},
    'GFP-tagged': {'C1': 'Adjective'},
    'GMOs': {'B2': 'Noun'},
    'GPa': {'C1': 'Noun'},
    'GSMs': {'B2': 'Noun'},
    'GTPase': {'C1': 'Noun'},
    'GTPase-activating': {'C1': 'Adjective'},
    'GUIs': {'B2': 'Noun'},
    'Gadus': {'C1': 'Noun'},
    'Gage': {'B1': 'Noun'},
    'Galactoglucomannan': {'C1': 'Noun'},
    'Gamry': {'C1': 'Noun'},
    'Ganoderma': {'C1': 'Noun'},
    'Gasterosteus': {'A2': 'Noun'},
    'Gastroenterology': {'B2': 'Noun'},
    'GeneXpert': {'B1': 'Noun'},
    'Giotto': {'B1': 'Noun'},
    'Giraffe®': {'A1': 'Noun'},
    'Griffin': {'B2': 'Noun'},
    'Griffiths': {'B2': 'Noun'},
    'Grot': {'B2': 'Noun'},
    'Guillard': {'B2': 'Noun'},
    'Gutiérrez': {'B2': 'Noun'},
    'Gutmann': {'B2': 'Noun'},
    'HEPA-filtered': {'C1': 'Adjective'},
    'HER2-binding': {'C1': 'Adjective'},
    'HER2-overexpression': {'C1': 'Noun'},
    'HER2-positive': {'C1': 'Adjective'},
    'HFD-feeding': {'C1': 'Noun'},
    'HFD-induced': {'C1': 'Adjective'},
    'HIV-1-derived': {'C1': 'Adjective'},
    'HSA-coupled': {'C1': 'Adjective'},
    'Habenula': {'B2': 'Noun'},
    'Haber-Bosch': {'B1': 'Noun'},
    'Hagby': {'A1': 'Noun'},
    'Halobacterium': {'A2': 'Noun'},
    'Halomonas': {'A2': 'Noun'},
    'Halophiles': {'A2': 'Noun'},
    'Headlong': {'B2': 'Adjective'},
    'Hepatitis-C': {'B1': 'Noun'},
    'Her2': {'B1': 'Noun'},
    'Heredity': {'B2': 'Noun'},
    'Hermetia': {'A2': 'Noun'},
    'Heterobasidion': {'A2': 'Noun'},
    'Heteronuclear': {'B2': 'Adjective'},
    'His-tag': {'C1': 'Noun'},
    'His6': {'C1': 'Noun'},
    'Histamine': {'B2': 'Noun'},
    'Histocompatibillity': {'C2': 'Noun'},
    'Histrap': {'C1': 'Noun'},
    'Homopropargylglycine': {'C2': 'Noun'},
    'Horseradish': {'B1': 'Noun'},
    'Hostpial': {'C2': 'Adjective'},
    'Hot-water': {'A2': 'Adjective'},
    'HpaII': {'C2': 'Noun'},
    'Htt-protein': {'C2': 'Noun'},
    'Human-Machine-Interface': {'C1': 'Noun'},
    'Human-derived': {'B2': 'Adjective'},
    'Hydrocortisone': {'C1': 'Noun'},
    'Hydrolyzation': {'C1': 'Noun'},
    'Hydrotreated': {'C1': 'Adjective'},
    'Hydrotreated-oil': {'C1': 'Noun'},
    'Hyflon': {'C2': 'Noun'},
    'Hylobius': {'C2': 'Noun'},
    'Hyperfine': {'C2': 'Adjective'},
    'Hyperlight': {'C1': 'Adjective'},
    'IAs': {'C1': 'Noun'},
    'IBD-risk': {'C1': 'Noun'},
    'IC-booster': {'C1': 'Noun'},
    'ICUs': {'C1': 'Noun'},
    'Ig': {'B2': 'Noun'},
    'IgA': {'B2': 'Noun'},
    'IgM': {'B2': 'Noun'},
    'I’m': {'A1': 'Pronoun'}, 
    'Jag1': {'A1': 'Noun'},
    'Jag2': {'A1': 'Noun'},
    'Jak2': {'A1': 'Noun'},
    'Jak2V617F': {'A1': 'Noun'},
    'Jamadi': {'A1': 'Noun'},
    'Janeway': {'A1': 'Noun'},
    'Janthinobacterium': {'A1': 'Noun'},
    'Jatropha': {'A1': 'Noun'},
    'Jeffamine': {'A1': 'Noun'},
    'Jeffamines': {'A1': 'Noun'},
    'Jehander': {'A1': 'Noun'},
    'Jernkontoret': {'A1': 'Noun'},
    'Jessore': {'A1': 'Noun'},
    'Jhumjhumpur': {'A1': 'Noun'},
    'Jiraand': {'A1': 'Noun'},
    'Job-Demands-Control-Support': {'A1': 'Noun'},
    'Jonasson': {'A1': 'Noun'},
    'Joncryl': {'A1': 'Noun'},
    'Jordbro': {'A1': 'Noun'},
    'Jordbruksverket': {'A1': 'Noun'},
    'Jordbruksverkets': {'A1': 'Noun'},
    'Josefin': {'A1': 'Noun'},
    'Josephine': {'A1': 'Noun'},
    'Jumpsuit': {'A1': 'Noun'},
    'Juno-Izumo1': {'A1': 'Noun'},
    'Jurkat': {'A1': 'Noun'},
    'JurkatCD16a': {'A1': 'Noun'},
    'Jérôme': {'A1': 'Noun'},
    'K-alumina': {'A1': 'Noun'},
    'K-promoted': {'A1': 'Adjective'},
    'K-wire': {'A1': 'Noun'},
    'K100and': {'A1': 'Noun'},
    'K2Sensation': {'A1': 'Noun'},
    'KDvalues': {'A1': 'Noun'},
    'KP-Acra': {'A1': 'Noun'},
    'KP-Euca': {'A1': 'Noun'},
    'KPIs': {'A1': 'Noun'},
    'KPPs': {'A1': 'Noun'},
    'Ka-bands': {'A1': 'Noun'},
    'Kaa': {'A1': 'Noun'},
    'Kai': {'A1': 'Noun'},
    'Kaiser': {'B2': 'Noun'},
    'Katarina': {'A1': 'Noun'},
    'Kattegat': {'A2': 'Noun'},
    'Khulna': {'B1': 'Noun'},
    'Kikkoman': {'B2': 'Noun'},
    'Kingfisher': {'B2': 'Noun'},
    'Knight': {'A2': 'Noun'},
    'Kumla': {'A1': 'Noun'},
    'Kuro': {'A1': 'Noun'},
    'Kyushu': {'A1': 'Noun'},
    'König': {'A1': 'Noun'},
    'L-Arginine': {'B2': 'Noun'},
    'L-Glutamic': {'B2': 'Adjective'},
    'L-Lactide': {'B2': 'Noun'},
    'L-arabinose': {'B2': 'Noun'},
    'L-asparagine': {'B2': 'Noun'},
    'L-cells': {'B2': 'Noun'},
    'L-cysteine': {'B2': 'Noun'},
    'L-lactate': {'B2': 'Noun'},
    'L-lactic': {'B2': 'Adjective'},
    'LFP-based': {'B2': 'Adjective'},
    'Laboratoire': {'B1': 'Noun'},
    'Laminated': {'B2': 'Adjective'},
    'Leukocyte': {'A2': 'Noun'},
    'Litsea': {'C2': 'Noun'},
    'Liungman': {'C2': 'Noun'},
    'Live/dead': {'B2': 'Adjective'},
    'Livsmedelverket': {'C1': 'Noun'},
    'LoGSA': {'C2': 'Noun'},
    'Local-field-potential': {'C2': 'Noun'},
    'LodeSTAR': {'C2': 'Noun'},
    'Log-transforemd': {'C2': 'Adjective'},
    'LogD': {'C2': 'Noun'},
    'Logan': {'B1': 'Noun'},
    'Longmont': {'B2': 'Noun'},
    'Loudden': {'C2': 'Noun'},
    'Loupas': {'C2': 'Noun'},
    'Low-Carbonmedium': {'C1': 'Noun'},
    'Low-LA-factor': {'C2': 'Noun'},
    'Ls-Dyna': {'C2': 'Noun'},
    'Ls-PrePost': {'C2': 'Noun'},
    'Lubrizol': {'C2': 'Noun'},
    'Lucy': {'A1': 'Noun'},
    'Luffa': {'B2': 'Noun'},
    'Lumify': {'C2': 'Noun'},
    'Luminex': {'C2': 'Noun'},
    'Lunaphore': {'C2': 'Noun'},
    'Luv': {'B2': 'Noun'},
    'Luvly': {'B2': 'Adjective'},
    'Lyme': {'B2': 'Noun'},
    'Lytic': {'C2': 'Adjective'},
    'Länssjukhus': {'C1': 'Noun'},
    'Lärarförbundet': {'C1': 'Noun'},
    'Löt': {'C1': 'Noun'},
    'Löttingelund': {'C2': 'Noun'},
    'M-HEOs': {'C2': 'Noun'},
    'M/G-ratio': {'C2': 'Noun'},
    'MAGs': {'C2': 'Noun'},
    'MALDI-ToF': {'C2': 'Noun'},
    'MAP-curve': {'C2': 'Noun'},
    'MATLAB-algorithm': {'C2': 'Noun'},
    'MATLAB-script': {'C2': 'Noun'},
    'MBAs': {'B2': 'Noun'},
    'MBR-pilot': {'C2': 'Noun'},
    'MBR-reactors': {'C1': 'Noun'},
    'MBs': {'C1': 'Noun'},
    'MBs/ml': {'C1': 'Noun'},
    'MCAo': {'C1': 'Noun'},
    'MCLs': {'C1': 'Noun'},
    'MDSC-like': {'C1': 'Adjective'},
    'MDSCs': {'C1': 'Noun'},
    'MEA-based': {'C1': 'Adjective'},
    'MED1-occupied': {'C1': 'Adjective'},
    'MEFs': {'C1': 'Noun'},
    'MFC-XG-Pectin': {'C1': 'Noun'},
    'MFCs': {'C1': 'Noun'},
    'MHC/peptide': {'C1': 'Noun'},
    'MHSas': {'C1': 'Noun'},
    'MILD-net': {'C1': 'Noun'},
    'MJ/Kg': {'C1': 'Noun'},
    'MJ/kg': {'C1': 'Noun'},
    'MJ/m': {'C1': 'Noun'},
    'ML/year': {'C1': 'Noun'},
    'MLCtracking': {'C1': 'Noun'},
    'MLGs': {'C1': 'Noun'},
    'MMP-cleavable': {'C1': 'Adjective'},
    'MMUs': {'C1': 'Noun'},
    'MPNs': {'C1': 'Noun'},
    'MRBrainS13': {'C1': 'Noun'},
    'MRBrainsS13': {'C1': 'Noun'},
    'MRI-only': {'C1': 'Adjective'},
    'MRTrix3Tissue': {'C1': 'Noun'},
    'MRVox2D': {'C1': 'Noun'},
    'MRtrix': {'C1': 'Noun'},
    'MS1-spectra': {'C1': 'Noun'},
    'MS2-spiked': {'C1': 'Adjective'},
    'MSDs': {'C1': 'Noun'},
    'MSEK/year': {'C1': 'Noun'},
    'MSMs': {'C1': 'Noun'},
    'MTO-models/theories': {'C1': 'Noun'},
    'MVC/mL': {'C1': 'Noun'},
    'MW/kg-CO2': {'C1': 'Noun'},
    'MXene/CNF': {'C1': 'Noun'},
    'MacKenzie': {'B1': 'Noun'},
    'Macclesfield': {'B2': 'Noun'},
    'Macular': {'C2': 'Adjective'},
    'Magnusson': {'B1': 'Noun'},
    'Maillard': {'B2': 'Noun'},
    'Malaren': {'B1': 'Noun'},
    'Malmberget': {'B2': 'Noun'},
    'Mannich': {'B2': 'Noun'},
    'March-April': {'A1': 'Noun'},
    'Marginalization': {'C1': 'Noun'},
    'Mars-like': {'A2': 'Adjective'},
    'Materiel': {'C1': 'Noun'},
    'Matière': {'B1': 'Noun'},
    'Mears': {'B2': 'Noun'},
    'MediaFire': {'B1': 'Noun'},
    'Metabolome': {'B2': 'Noun'},
    'Metachromatic': {'C1': 'Adjective'},
    'Methanosarcina': {'C2': 'Noun'},
    'Mettler': {'B2': 'Noun'},
    'Mettler-Toledo': {'B1': 'Noun'},
    'Michaelis-Menten': {'B2': 'Noun'},
    'Milena': {'A1': 'Noun'}, 
    'Miljöbyggnad': {'B1': 'Noun'}, 
    'Miljökontor': {'B1': 'Noun'}, 
    'Miljöteknik': {'B1': 'Noun'}, 
    'Milorad': {'A1': 'Noun'}, 
    'Montes': {'B2': 'Noun'},
    'Moringa': {'B2': 'Noun'},
    'Mucilaginibacter': {'B2': 'Noun'},
    'Mycobacterium': {'B2': 'Noun'},
    'Mycoplasma': {'B2': 'Noun'},
    'N-terminal': {'C1': 'Adjective'},
    'NFkB': {'B2': 'Noun'},
    'Nacka': {'B1': 'Noun'},
    'Nasim': {'B1': 'Noun'},
    'Nernstian': {'C2': 'Adjective'},
    'Neutropenia': {'C2': 'Noun'},
    'Nicotiana': {'C1': 'Noun'},
    'Nile': {'B1': 'Noun'},
    'Nm3/h': {'C1': 'Noun'},
    'NmL': {'C1': 'Noun'},
    'NmL/min': {'C1': 'Noun'},
    'Nmap': {'C1': 'Noun'},
    'No-shift': {'B2': 'Adjective'},
    'NoBi': {'B2': 'Noun'},
    'Node-Red': {'B2': 'Noun'},
    'Nok/kg': {'B2': 'Noun'},
    'Non-IP': {'B2': 'Adjective'},
    'Non-Sequenced': {'B2': 'Adjective'},
    'Non-parametrical': {'B2': 'Adjective'},
    'Nonactin-based': {'C1': 'Adjective'},
    'Nordic-produced': {'B2': 'Adjective'},
    'Nordicstation': {'B1': 'Noun'},
    'Nordicstationset': {'B1': 'Noun'},
    'Nordlund': {'B2': 'Noun'},
    'Norner': {'B2': 'Noun'},
    'Norosensor': {'B2': 'Noun'},
    'Norén': {'B2': 'Noun'},
    'Notch1': {'C1': 'Noun'},
    'Notch1-3': {'C1': 'Noun'},
    'Notch2': {'C1': 'Noun'},
    'Notch3': {'C1': 'Noun'},
    'Notch4': {'C1': 'Noun'},
    'Notcvh': {'C1': 'Noun'},
    'Notoph-thalmus': {'C1': 'Noun'},
    'Notre': {'B1': 'Noun'},
    'Novelda': {'B2': 'Noun'},
    'Novus': {'B2': 'Noun'},
    'Nowdays': {'A2': 'Adverb'},
    'Noxon': {'B2': 'Noun'},
    'Ntot': {'C1': 'Noun'},
    'Nucleotide-binding': {'C1': 'Adjective'},
    'Nudt2': {'C1': 'Noun'},
    'Nuwiq®': {'B2': 'Noun'},
    'Nylon11': {'B2': 'Noun'},
    'Nyström': {'B2': 'Noun'},
    'O-N/Influent': {'C1': 'Noun'},
    'O-centered': {'B2': 'Adjective'},
    'O-content': {'B2': 'Noun'},
    'O-glycans': {'C2': 'Noun'},
    'O-impregnated': {'C2': 'Adjective'},
    'O-linked': {'C2': 'Adjective'},
    'OARs': {'C1': 'Noun'},
    'OAuth': {'A2': 'Noun'},
    'OBPs': {'C2': 'Noun'},
    'OCR-engine': {'B2': 'Noun'},
    'OCR-engines': {'B2': 'Noun'},
    'OCV-curve': {'C2': 'Noun'},
    'OEGMA-co-TFEMA': {'C2': 'Noun'},
    'OETCs': {'C2': 'Noun'},
    'OH-],providing': {'C2': 'Adjective'},
    'OH-group': {'C2': 'Noun'},
    'OH-production': {'C2': 'Noun'},
    'OH-region': {'C2': 'Noun'},
    'OH-signals': {'C2': 'Noun'},
    'OHSSs': {'C2': 'Noun'},
    'OHion': {'C2': 'Noun'},
    'OLS-model': {'C2': 'Noun'},
    'OLTs': {'C1': 'Noun'},
    'ONs': {'C1': 'Noun'},
    'OPCLs': {'C2': 'Noun'},
    'OSTE/Glass-beads': {'C2': 'Noun'},
    'Oasis': {'A1': 'Noun'},
    'Ockelbo': {'B1': 'Noun'},
    'Octa-BDE': {'C2': 'Noun'},
    'Octagam': {'B2': 'Noun'},
    'Octanate': {'B2': 'Noun'},
    'Octapharma': {'B2': 'Noun'},
    'Octet-analysis': {'C2': 'Noun'},
    'Octetanalys': {'C2': 'Noun'},
    'Odnevall': {'B1': 'Noun'},
    'Oilspill': {'B2': 'Noun'},
    'Olefin-to-paraffin': {'C2': 'Noun'},
    'Olfactometry': {'C2': 'Noun'},
    'Olink': {'B2': 'Noun'},
    'OlinkR': {'B2': 'Noun'},
    'Olink®': {'B2': 'Noun'},
    'Olkiluoto': {'B1': 'Noun'},
    'Orthostatic': {'C1': 'Adjective'},
    'PEGs': {'C1': 'Noun'},
    'PEGylation': {'C1': 'Noun'},
    'PET-bottles': {'B1': 'Noun'},
    'PET-imaging': {'C1': 'Noun'},
    'PFAAs': {'C1': 'Noun'},
    'PFAS-containing': {'C1': 'Adjective'},
    'PFCAs': {'C1': 'Noun'},
    'PHAs': {'C1': 'Noun'},
    'PLA-based': {'C1': 'Adjective'},
    'Pablo': {'A1': 'Noun'},
    'Paganin': {'B1': 'Noun'},
    'Pampers': {'A1': 'Noun'},
    'Paralympics': {'A2': 'Noun'},
    'Petri-dishes': {'B2': 'Noun'},
    'Pharamacovigilance': {'C1': 'Noun'},
    'Pharmacopeias': {'C1': 'Noun'},
    'Phase-Liquid': {'B2': 'Noun'},
    'Phase-change': {'B2': 'Noun'},
    'Phelps': {'B1': 'Noun'},
    'Pheno': {'B2': 'Noun'},
    'PhenoImager': {'B2': 'Noun'},
    'Phi3': {'B2': 'Noun'},
    'Phosphatase': {'C1': 'Noun'},
    'Phosphorus-31': {'C1': 'Noun'},
    'Photoconjugation': {'C1': 'Noun'},
    'Phragmites': {'C1': 'Noun'},
    'Phu': {'A1': 'Noun'},
    'PhyloWGS': {'C1': 'Noun'},
    'Phylogenomic': {'C1': 'Adjective'},
    'Phytophthora': {'C1': 'Noun'},
    'PiFace': {'B2': 'Noun'},
    'Piazza': {'A2': 'Noun'},
    'Pichia': {'C1': 'Noun'},
    'Pickering': {'B2': 'Noun'},
    'PicsArt': {'B1': 'Noun'},
    'Pieris': {'C1': 'Noun'},
    'Pioneiros': {'B1': 'Noun'},
    'Pioneros': {'B1': 'Noun'},
    'Pixelation': {'B2': 'Noun'},
    'Pixelgen': {'B2': 'Noun'},
    'PknB_PASTA_kin': {'C1': 'Noun'},
    'Plamen': {'A1': 'Noun'},
    'Plantagon': {'B2': 'Noun'},
    'Plata': {'A2': 'Noun'},
    'Playing-related': {'B2': 'Adjective'},
    'Pleurotus': {'C1': 'Noun'},
    'Plug-in-Gait': {'B2': 'Noun'},
    'Pluronic': {'C1': 'Noun'},
    'Pluronic-based': {'C1': 'Adjective'},
    'Pluronic®': {'C1': 'Noun'},
    'PlySs2': {'C1': 'Noun'},
    'PlysS2': {'C1': 'Noun'},
    'Poisson-Boltzmann': {'C1': 'Noun'},
    'Polarn': {'B1': 'Noun'},
    'Polestar': {'B2': 'Noun'},
    'Polonica': {'C2': 'Noun'},
    'Polyadenylated': {'C2': 'Adjective'},
    'Polybrominated': {'C2': 'Adjective'},
    'Polybutylene': {'C2': 'Noun'},
    'Polycarboxylate': {'C2': 'Noun'},
    'Polygenic': {'C1': 'Adjective'},
    'Polypropylen/PP': {'C2': 'Noun'},
    'Polypropylene-blend': {'C2': 'Noun'},
    'Ponseti': {'B2': 'Noun'},
    'Porras': {'B1': 'Noun'},
    'Porsgrunn': {'B2': 'Noun'},
    'Post-exertional': {'C2': 'Adjective'},
    'PostureScore': {'C1': 'Noun'},
    'PotentialEP': {'C1': 'Noun'},
    'PotentialODP': {'C1': 'Noun'},
    'Považay': {'B2': 'Noun'},
    'PrEST': {'C1': 'Noun'},
    'PrESTs': {'C1': 'Noun'},
    'PrETSs': {'C1': 'Noun'},
    'Prada': {'B1': 'Noun'},
    'Praktikertjänst': {'B2': 'Noun'},
    'PreZero': {'B2': 'Noun'},
    'Pretargeted': {'C2': 'Adjective'},
    'Primaloft': {'B2': 'Noun'},
    'Primona': {'B2': 'Noun'},
    'Printex': {'B2': 'Noun'},
    'Pro-loop': {'B2': 'Noun'},
    'ProCalc': {'B2': 'Noun'},
    'ProCeas': {'C2': 'Noun'},
    'ProFlex-XC': {'B2': 'Noun'},
    'Probiotic': {'B2': 'Noun', 'C1': 'Adjective'},
    'Procedia': {'C1': 'Noun'},
    'Procudan': {'B2': 'Noun'},
    'ProfileScore': {'C1': 'Noun'},
    'Profoto': {'B2': 'Noun'},
    'Progressor': {'B2': 'Noun'},
    'Promis.e': {'B1': 'Noun'},
    'Promulgen': {'C2': 'Noun'},
    'Pronationsupination': {'C2': 'Noun'},
    'Prontoderm': {'C2': 'Noun'},
    'Prostate-specific': {'C2': 'Adjective'},
    'Prostatectomy': {'C2': 'Noun'},
    'Protamines': {'C2': 'Noun'},
    'Proteinase': {'C2': 'Noun'},
    'Protégé': {'B2': 'Noun'},
    'Pseudomonas': {'C2': 'Noun'},
    'Puntland': {'B2': 'Noun'},
    'Purdue': {'B2': 'Noun'},
    'Purkinje': {'C2': 'Noun'},
    'Putrescine': {'C2': 'Noun'},
    'RNA-binding': {'C2': 'Adjective'},
    'Radiant': {'B1': 'Adjective'},
    'Raven': {'A1': 'Noun'},
    'Relic': {'B1': 'Noun'},
    'Research': {'B1': 'Noun', 'B1': 'Verb'},
    'Repetitive': {'B2': 'Adjective'},
    'Romboutsia': {'C2': 'Noun'},
    'Rosdahl': {'C2': 'Noun'},
    'Ru-involved': {'C2': 'Adjective'},
    'RuBP': {'C2': 'Noun'},
    'RuBisCO,TIM': {'C2': 'Noun'},
    'Rubisco-PRK': {'C2': 'Noun'},
    'Ruddlesden-Popper': {'C2': 'Noun'},
    'Rugosa': {'C2': 'Noun'},
    'Ruza': {'C2': 'Noun'},
    'RxLR': {'C2': 'Noun'},
    'Rytter': {'C2': 'Noun'},
    'Rz': {'C2': 'Noun'},
    'S-linked': {'C2': 'Adjective'},
    'S-phase': {'C2': 'Noun'},
    'S-transferase': {'C2': 'Noun'},
    'S.cerevisiae': {'C2': 'Noun'},
    'S/ton': {'C2': 'Noun'},
    'SAM-testet': {'C2': 'Noun'},
    'SAMD9Lhave': {'C2': 'Noun'},
    'SAPs': {'C2': 'Noun'},
    'SCNAs': {'C2': 'Noun'},
    'SCR-\\xad‐catalyst': {'C2': 'Noun'},
    'SCZs': {'C2': 'Noun'},
    'SDGs': {'C2': 'Noun'},
    'SDKs': {'C2': 'Noun'},
    'SDS-PAGE-quantified': {'C2': 'Adjective'},
    'SDSPAGE.G5-FN-4RepCT': {'C2': 'Noun'},
    'SDeS': {'C2': 'Noun'},
    'SDeS/DDAB': {'C2': 'Noun'},
    'SEC-analysis': {'C2': 'Noun'},
    'SEC-resin': {'C2': 'Noun'},
    'SECA-directive': {'C2': 'Noun'},
    'SEHPOS-process': {'C2': 'Noun'},
    'SEI-free': {'C2': 'Adjective'},
    'SEK/MWh': {'C2': 'Noun'},
    'SEK/hour': {'C2': 'Noun'},
    'SEK/kg': {'C2': 'Noun'},
    'STING-dependent': {'C1': 'Adjective'},
    'STING-mediated': {'C1': 'Adjective'},
    'STRs': {'B2': 'Noun'},
    'SUMDs': {'C1': 'Noun'},
    'SUVA-value': {'C1': 'Noun'},
    'SUVA-values': {'C1': 'Noun'},
    'SUVAvalues': {'C1': 'Noun'},
    'SWOT-model': {'B2': 'Noun'},
    'SaO2': {'C1': 'Noun'},
    'SaSt': {'B2': 'Noun'},
    'Sabic': {'B1': 'Noun'},
    'Saccharina': {'C1': 'Noun'},
    'Saccharomyces': {'C1': 'Noun'},
    'Saeman': {'B2': 'Noun'},
    'Safelines': {'B2': 'Noun'},
    'Saffman-Taylor': {'C1': 'Adjective'},
    'Sahlens': {'B2': 'Noun'},
    'Sahlén': {'B2': 'Noun'},
    'Saint-Gobain': {'B1': 'Noun'},
    'Sal-1': {'C1': 'Noun'},
    'Sal-1coupled': {'C1': 'Adjective'},
    'Salems': {'B2': 'Noun'},
    'Salk': {'B2': 'Noun'},
    'Salmén': {'B2': 'Noun'},
    'SaltX': {'B1': 'Noun'},
    'Samei': {'B2': 'Noun'},
    'Sanchi': {'B2': 'Noun'},
    'Sand/or': {'B1': 'Conjunction'},
    'Sandqvist': {'B2': 'Noun'},
    'Sanfilippo': {'C1': 'Noun'},
    'Sangair': {'B2': 'Noun'},
    'Sangairs': {'B2': 'Noun'},
    'Sanger': {'B2': 'Noun'},
    'Sao2': {'C1': 'Noun'},
    'Saprolegnia': {'C1': 'Noun'},
    'Sarcina': {'C1': 'Noun'},
    'Sartorius': {'B2': 'Noun'},
    'Satija': {'B2': 'Noun'},
    'Sativa': {'C1': 'Noun'},
    'Sauguet': {'B2': 'Noun'},
    'Sealer': {'B2': 'Noun'}, 
    'Secretory': {'C1': 'Adjective'}, 
    'Serpent': {'B2': 'Noun'}, 
    'Shania': {'A1': 'Noun'}, 
    'Shear-Lag': {'C1': 'Noun'},
    'Solanum': {'B2': 'Noun'},
    'Solute': {'B2': 'Noun'},
    'Sonora': {'B1': 'Noun'},
    'Sox': {'B1': 'Noun'},
    'Spinocerebellar': {'C2': 'Adjective'},
    'Staphylococcus': {'B2': 'Noun'},
    'Strangler': {'B2': 'Noun'},
    'Streptococcus': {'B2': 'Noun'},
    'T-helper': {'A2': 'Adjective'},
    'Talon': {'B2': 'Noun'},
    'Terminally': {'B2': 'Adverb'},
    'Thalassiosira': {'A2': 'Noun'},
    'Thibault': {'B1': 'Noun'},
    'Tianjin': {'B1': 'Noun'},
    'Tokuda': {'B1': 'Noun'},
    'Toledo': {'B1': 'Noun'},
    'Topsoe': {'B1': 'Noun'},
    'Topsøe': {'B1': 'Noun'},
    'Transcranial': {'C2': 'Adjective'},
    'Triceps': {'C2': 'Noun'},
    'Tunic': {'B2': 'Noun'},
    'Two-wire': {'B2': 'Adjective'},
    'UCSTs': {'C2': 'Noun'},
    'UDP-Glucose': {'C2': 'Noun'},
    'UDP-sugar': {'C2': 'Noun'},
    'UEDs': {'C2': 'Noun'},
    'UF-filter': {'C2': 'Noun'},
    'UHPLC-MSanalysis': {'C2': 'Noun'},
    'UMIpool': {'C2': 'Noun'},
    'UPLC-equipment': {'C2': 'Noun'},
    'UPS-systems': {'C2': 'Noun'},
    'UPS:s': {'C2': 'Noun'},
    'UV-B-absorbing': {'C2': 'Adjective'},
    'UV-absorbance': {'C2': 'Noun'},
    'UV-absorbing': {'C2': 'Adjective'},
    'UV-based': {'C2': 'Adjective'},
    'UV-conjugation': {'C2': 'Noun'},
    'UV-curable': {'C2': 'Adjective'},
    'UV-cured': {'C2': 'Adjective'},
    'UV-detection': {'C2': 'Noun'},
    'UV-exposure': {'C2': 'Noun'},
    'UV-induced': {'C2': 'Adjective'},
    'UV-lamps': {'C2': 'Noun'},
    'UV-protection': {'C2': 'Noun'},
    'UV-protective': {'C2': 'Adjective'},
    'UV-radiation': {'C2': 'Noun'},
    'UV-reactor': {'C2': 'Noun'},
    'UV-spectroscopy': {'C2': 'Noun'},
    'UV-stabilisers': {'C2': 'Noun'},
    'UV-treatment': {'C2': 'Noun'},
    'UV-\\xad‐lamp': {'C2': 'Noun'},
    'UV-\\xad‐light': {'C2': 'Noun'},
    'UV/Ozone/H': {'C2': 'Noun'},
    'UV/Vis': {'C2': 'Noun'},
    'Ubbelohde': {'C2': 'Noun'},
    'Uddeholm': {'C2': 'Noun'},
    'Uddevalla': {'C2': 'Noun'},
    'Ulcer': {'B1': 'Noun'},
    'Ultrasonix': {'C2': 'Noun'},
    'Ultrasound-mediated': {'C2': 'Adjective'},
    'Umbraco': {'C2': 'Noun'},
    'Umicore': {'C2': 'Noun'},
    'UniSart': {'A1': 'Noun'},
    'Unscrambler': {'A1': 'Noun'},
    'Uponor': {'A1': 'Noun'},
    'VAEs': {'B2': 'Noun'},
    'VLANs': {'B2': 'Noun'},
    'VOCs': {'B2': 'Noun'},
    'Vaio': {'A1': 'Noun'},
    'Valdescorriel': {'A1': 'Noun'},
    'Valentini': {'A1': 'Noun'},
    'Vanax': {'A1': 'Noun'},
    'VarScan2': {'A1': 'Noun'},
    'Varona': {'A1': 'Noun'},
    'Vasa': {'A1': 'Noun'},
    'Vegetative': {'B2': 'Adjective'},
    'Veide': {'A1': 'Noun'},
    'Veridex': {'A1': 'Noun'},
    'VoIP': {'B1': 'Noun'},

    }

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
    parser.add_option('--keywords',
                      dest="keywords",
                      default=False,
                      action="store_true",
                      help="process paired keywords"
    )
    #
    parser.add_option('--self',
                      dest="self",
                      default=False,
                      action="store_true",
                      help="process paired keywords"
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
    if (len(remainder) < 1):
        print("Insuffient arguments\n must provide file_name\n")
        return
    #
    unique_words=dict()
    if options.keywords:
        paired_keywords_file_name=f'{directory_prefix}paired-keywords.json'
        try:
            if Verbose_Flag:
                print(f'Trying to read: {paired_keywords_file_name}')
            with open(paired_keywords_file_name, 'r') as f:
                unique_words=json.load(f)
                print(f'read in {len(unique_words)} keywords')
        except:
            print(f'Unable to open file named {paired_keywords_file_name}')
            return
    else:
        input_file_name=remainder[0]
        if input_file_name.find('paired') >= 0:
            options.keywords=True
        try:
            if Verbose_Flag:
                print(f'Trying to read: {input_file_name}')
            with open(input_file_name, 'r') as f:
                unique_words=json.load(f)
        except:
            print(f'Unable to open file named {input_file_name}')
            return
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
    for e in common_acronyms_CBH.well_known_acronyms_list:
        if len(e) >= 1:
            ack=e[0]
            if len(e) >= 2:
                d=e[1]
                current_entry=well_known_acronyms.get(ack, list())
                current_entry.append(d)
                well_known_acronyms[ack]=current_entry
    print(f'{(len(well_known_acronyms)):>{Numeric_field_width}} unique acronyms in ({len(common_acronyms_CBH.well_known_acronyms_list)}) well_known_acronyms_CBH')

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
        
        if w not in common_swedish.KTH_ordbok_Swedish_with_CEFR:
            # skip acronyms
            if w in well_known_acronyms:
                continue
            if w in miss_spelled_to_correct_spelling_CBH.miss_spelled_to_correct_spelling:
                continue
            levels=common_swedish.common_swedish_words.get(w, False)
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
        if w not in common_english.KTH_ordbok_English_with_CEFR:
            # skip acronyms
            if w in well_known_acronyms:
                continue
            if w in miss_spelled_to_correct_spelling_CBH.miss_spelled_to_correct_spelling:
                continue
            levels=common_english.common_English_words.get(w, False)
            if levels:
                print(f"'{w}': {levels},")
            else:
                if Verbose_Flag:
                    print(f'missing English: {w}')
    #
    print(f'{len(common_english.common_English_words):>{Numeric_field_width}} words in common English words')
    #
    print(f'{len(common_swedish.common_swedish_words):>{Numeric_field_width}} words in common Swedish words')
    #
    print(f'{len(common_swedish.common_swedish_technical_words):>{Numeric_field_width}} words in common Swedish technical words')
    #
    print(f'{len(common_english.chemical_elements):>{Numeric_field_width}} words in chemical_elements')
    print(f'{len(common_english.chemical_elements_symbols):>{Numeric_field_width}} words in chemical_elements_symbols')

    print(f'{len(common_english.common_danish_words):>{Numeric_field_width}} words in common Danish words')
    #
    print(f'{len(common_english.common_french_words):>{Numeric_field_width}} words in common French words')
    #
    print(f'{len(common_english.common_finnish_words):>{Numeric_field_width}} words in common Finnish words')
    #
    print(f'{len(common_english.common_german_words):>{Numeric_field_width}} words in common German words')
    #
    print(f'{len(common_english.common_icelandic_words):>{Numeric_field_width}} words in common Icelandic words')
    #
    print(f'{len(common_english.common_italian_words):>{Numeric_field_width}} words in common Italian words')
    #
    print(f'{len(common_english.common_latin_words):>{Numeric_field_width}} words in common Latin words')
    #
    print(f'{len(common_english.common_norwegian_words):>{Numeric_field_width}} words in common Norwegian words')
    #
    print(f'{len(common_english.common_portuguese_words):>{Numeric_field_width}} words in common Portuguese words')
    #
    print(f'{len(common_english.common_spanish_words):>{Numeric_field_width}} words in common Spanish words')
    #
    print(f'{len(common_english.common_units):>{Numeric_field_width}} words in common units')
    #
    print(f'{len(common_english.names_of_persons):>{Numeric_field_width}} words in names_of_persons')
    print(f'{len(common_english.place_names):>{Numeric_field_width}} words in place_names')
    print(f'{len(common_english.company_and_product_names):>{Numeric_field_width}} words in company_and_product_names')
    print(f'{len(common_english.misc_words_to_ignore):>{Numeric_field_width}} words in misc_words_to_ignore')
    print(f'{len(words_to_ignore):>{Numeric_field_width}} words in words_to_ignore')
    print(f'{len(common_english.mathematical_words_to_ignore):>{Numeric_field_width}} words in mathematical_words_to_ignore')
    print(f'{len(common_english.programming_keywords):>{Numeric_field_width}} words in programming_keywords')
    print(f'{len(common_english.language_tags):>{Numeric_field_width}} words in language_tags')
    print(f'{len(diva_merged_words_CBH.merged_words):>{Numeric_field_width}} words in merged_words CBH')
    print(f'{len(miss_spelled_to_correct_spelling_CBH.miss_spelled_to_correct_spelling):>{Numeric_field_width}} words in miss_spelled_to_correct_spelling CBH')
    print(f'{len(common_english.abbreviations_ending_in_period):>{Numeric_field_width}} words in abbreviations_ending_in_period')
    #
    print(f'{len(unique_words):>{Numeric_field_width}} read in')
    #
    # add the individual words from multiple words in the common_English_words to the unique_words - as if they were used
    if options.self:
        for w in common_english.common_English_words:
            if w.count(' ') > 0:
                ws=w.split(' ')
                for wsw in ws:
                    if wsw not in unique_words:
                        unique_words[wsw] = 0
    #
    # remove the words to be ignored
    for w in words_to_ignore:
        if w in unique_words:
            del unique_words[w]
    #
    if '27°C-300°C' in unique_words:
        print("found 1: '27°C-300°C'")
    #
    # after removing spaces and dashses, put all of the common_english_words in lower case in a fall_back list 
    fall_back_words=set()
    #
    for w in common_english.common_English_words:
        w=w.replace(' ', '')
        w=w.replace('-', '')
        fall_back_words.add(w.lower())
    #
    # add lower case version of varioous lists of words to the fall_back list - to cover cases such as "sinkhorn"
    for w in common_english.names_of_persons:
        fall_back_words.add(w.lower())
    #
    for w in common_english.place_names:
        fall_back_words.add(w.lower())
    #
    for w in common_english.company_and_product_names:
        fall_back_words.add(w.lower())
    #
    for w in common_english.common_programming_languages:
        fall_back_words.add(w.lower())
    #
    for w in well_known_acronyms:
        fall_back_words.add(w.lower())
    #
    added_to_unique_words_count=0
    list_of_added_words=[]
    # remove spaces and hypens in merged words to compute fall back words to match unique_words against
    for w in diva_merged_words_CBH.merged_words:
        wx=w.replace(' ', '')
        usage_cnt=1
        # remove the merged word
        if wx in unique_words:
            usage_cnt=unique_words[wx]
            del unique_words[wx]
        #
        wx=wx.replace('-', '')
        wx=wx.lower()
        fall_back_words.add(wx)
        #
        # if necessary add the words in multiple words to unique_words
        if w.count(' ') > 0:
            ws=w.split(' ')
            for wsw in ws:
                if wsw in unique_words:
                    if not options.keywords:
                        unique_words[wsw]= unique_words[wsw] + usage_cnt
                else:
                    unique_words[wsw]=1
                    list_of_added_words.append(wsw)
                    if Verbose_Flag:
                        print(f'adding {wsw=}')
                    if not options.keywords:
                        added_to_unique_words_count=added_to_unique_words_count + usage_cnt
    #
    print(f'{added_to_unique_words_count:>{Numeric_field_width}} added to the unique words based on those that occurred in merged_words')
    #
    added_to_unique_words_count=0
    for w in miss_spelled_to_correct_spelling_CBH.miss_spelled_to_correct_spelling:
        entry=miss_spelled_to_correct_spelling_CBH.miss_spelled_to_correct_spelling[w]
        if not entry:
            continue
        if not isinstance(entry, dict):
            print(f'{entry=}')
            continue
        actuaL_word=entry.get('c', False)
        if not actuaL_word:
            continue
        #
        usage_cnt=1
        # remove the miss spelled word
        if w in unique_words:
            usage_cnt=unique_words[w]
            del unique_words[w]
        #
        # if necessary add the words to unique_words
        if actuaL_word.count(' ') > 0:
            ws=actuaL_word.split(' ')
            for wsw in ws:
                if wsw in unique_words:
                    if not options.keywords:
                        unique_words[wsw]= unique_words[wsw] + usage_cnt
                else:
                    unique_words[wsw]=1
                    list_of_added_words.append(wsw)
                    if not options.keywords:
                        added_to_unique_words_count=added_to_unique_words_count + usage_cnt
                    if Verbose_Flag:
                        print(f'adding word: {wsw=}')

    #
    print(f'{added_to_unique_words_count:>{Numeric_field_width}} added to the unique words based on those that occurred in miss_spelled_to_correct_spelling_CBH')
    
    add_words_file_name=f'{directory_prefix}extra_added_words_CBH.json'
    real_additional_words=[]
    for w in list_of_added_words:
        if w in words_to_ignore:
            continue
        # ignore known misspelled words
        if w in miss_spelled_to_correct_spelling_CBH.miss_spelled_to_correct_spelling:
            continue
        # ignore abbreviations ending in period
        if w in common_english.abbreviations_ending_in_period:
            continue

        if len(w) >= 2:
            if w[0] == '-':
                w=w[1:]
        if is_number(w):
            continue

        # remove matching parens
        if True:
            if w.startswith('(') and w.endswith(")"):
                w=w[1:-1]

            if w.endswith("..."):
                w=w[:-3]


            if w.endswith(',') or w.endswith(';') or  w.endswith('-') or\
               w.endswith('?') or w.endswith('!') or w.endswith('.') or w.endswith(':'):
                w=w[:-1]
            if  w.endswith('“') or w.endswith("’") or w.endswith('”'):
                w=w[:-1]
            if w.startswith("``"):
                w=w[2:]
            if w.startswith("\\"):
                w=w[1:]
            if w.endswith("''"):
                w=w[:-2]
            if w.startswith('•') or w.startswith('.') or w.startswith('”') or w.startswith('“') or\
               w.startswith("'") or w.startswith("{") or w.startswith("‘") or w.startswith("‚") or\
               w.startswith("’") or w.startswith("%") or w.startswith(":"):
                w=w[1:]
            # repeat these for once that were inside quotation marks
            if w.endswith(',') or w.endswith(';') or  w.endswith('-') or\
               w.endswith('?') or w.endswith('!') or w.endswith('.') or w.endswith(':'):
                w=w[:-1]


        if len(w) == 0:
            continue

        if w in words_to_ignore:
            continue
        if w in well_known_acronyms:
            continue
        if w in common_english.common_English_words:
            continue
        if w in common_english.names_of_persons:
            continue
        if w in common_english.abbreviations_ending_in_period:
            continue
        if w in common_english.thousand_most_common_words_in_English:
            continue
        if w in common_english.chemical_names_and_formulas:
            continue
        if w in common_english.common_urls:
            continue
        if w in common_english.place_names:
            continue
        if w in common_english.company_and_product_names:
            continue
        if w in common_english.common_programming_languages:
            continue
        if w in common_english.common_units:
            continue
        if w in AVL_words_with_CEFR.avl_words:
            continue
    
        if w in common_swedish.common_swedish_words:
            continue
        if w in common_swedish.common_swedish_technical_words:
            continue
        if w in words_kelly_swedish:
            continue

        if w in well_known_acronyms:
            continue
        if w in common_english.abbreviations_ending_in_period:
            continue
        if w in common_english.thousand_most_common_words_in_English:
            continue
        if w in common_english.common_English_words:
            continue
        if w in common_english.names_of_persons:
            continue
        if w in common_english.abbreviations_ending_in_period:
            continue
        if w in common_english.chemical_names_and_formulas:
            continue
        if w in common_english.common_urls:
            continue
        if w in common_english.place_names:
            continue
        if w in common_english.company_and_product_names:
            continue
        if w in common_english.common_programming_languages:
            continue
        if w in common_english.common_units:
            continue
        if w in AVL_words_with_CEFR.avl_words:
            continue
        if w in common_swedish.common_swedish_words:
            continue
        if w in common_swedish.common_swedish_technical_words:
            continue
        if w in common_english.common_german_words:
            continue
        if w in words_kelly_swedish:
            continue

        if w.istitle():
            wl=w.lower()
            if wl in common_english.common_English_words:
                continue
            if wl in AVL_words_with_CEFR.avl_words:
                continue
            if wl in common_swedish.common_swedish_words:
                continue
            if wl in common_swedish.common_swedish_technical_words:
                continue
            if wl in words_kelly_swedish:
                continue

        if w in miss_spelled_to_correct_spelling_CBH.miss_spelled_to_correct_spelling:
            continue

        # some last trash to remove
        if w in ['Tr', 'e.g', "dumb'", 'ss', "cost'cost'", 's.k', 'H', '´', 'A∗', 'T', 'Q', 'al', "­", "–", "—", "…", "→", "_",]:
            continue
        
        real_additional_words.append(w)

    with open(add_words_file_name, 'w') as f:
        f.write(json.dumps(real_additional_words, ensure_ascii=False))
        print(f"finished writing {add_words_file_name} with {len(real_additional_words)} words")
    #
    if options.keywords: # extract acronym definitions from keyword
        words_to_remove=set()
        added_to_unique_words_count=0
        for w in unique_words:
            a=extract_acronym(w)
            if len(a) >= 1 and a in well_known_acronyms:
                words_to_remove.add(w)
                added_to_unique_words_count=added_to_unique_words_count-1
                continue
            # deal with plurals of acronyms
            if a.endswith('s'):
                if len(a) >= 1:
                    a=a[ :-1]
                    if len(a) >= 1 and a in well_known_acronyms:
                        words_to_remove.add(w)
                        added_to_unique_words_count=added_to_unique_words_count-1
                        continue
        #
        if Verbose_Flag:
            print(f"{len(words_to_remove)}: {words_to_remove}=")
        # remove those that were found
        if len(words_to_remove) > 0:
            for w in words_to_remove:
                # remove this entry
                if w in unique_words:
                    if Verbose_Flag:
                        print(f"removing '{w}'")
                    del unique_words[w]
                else:
                    print(f"should remove '{w}' but it is no longer in unique_words")
        #
        print(f'{added_to_unique_words_count:>{Numeric_field_width}} removed the unique words that defined an acronym that is known')
    #
    words_not_found=set()
    number_skipped=0
    number_of_potential_acronyms=0
    potential_acronyms=set()
    count_fall_back_cases=0
    #
    # for some testing
    if options.testing and 'detection zone' in diva_merged_words_CBH.merged_words:
        print('detection zone present')
        if 'detection zone' in fall_back_words:
            print('detection zone in fall-back_words')
        if 'detectionzone' in fall_back_words:
            print('detectionzone in fall-back_words')
    #
    words_with_IEC=[]
    for w in unique_words:
        if w.find('IEC') >= 0:
            words_with_IEC.append(w)
    save_collected_words(words_with_IEC, 'IEC')
    #
    for w in unique_words:
        initial_w=w[:]
        w=w.strip()
        #
        # remove the following product unimbers - as other wise the remove_products_and_ranges() turns them into 'iU'
        if w in ['i7-6600U', 'i5-5200U', ]:
            number_skipped=number_skipped+1
            continue
        #
        w = unicodedata.normalize('NFC',w) #  put everything into NFC form - to make comparisons simpler; also NFC form is the W3C recommended web form
        #
        # these should all have been removed
        if w in words_to_ignore:
            number_skipped=number_skipped+1
            continue
        #
        # skip URLs
        if w.startswith('http://') or w.startswith('https://'):
            number_skipped=number_skipped+1
            continue
        #
        # skip IEC standard document numbers
        if w.startswith('IEC-'):
            number_skipped=number_skipped+1
            continue
        #
        w=remove_prefixes(w)
        w=remove_suffixes(w)
        w=remove_lbracket_number_rbracket(w) # remove [ddd] from words
        if len(w) == 0:
            number_skipped=number_skipped+1
            continue
        #
        if is_numeric_range(w):
            number_skipped=number_skipped+1
            continue
        #
        if is_numeric_range_eith_units(w):
            number_skipped=number_skipped+1
            continue
        #
        # w=remove_products_and_ranges(w)
        # if len(w) == 0:
        #     number_skipped=number_skipped+1
        #     continue
        #
        w=remove_percentage_range(w)
        if len(w) == 0:
            number_skipped=number_skipped+1
            continue
        #
        w=remove_lbracket_rbracket_pair(w) # remove brackets around a word
        if len(w) == 0:
            continue
        #
        w=remove_lparen_rparen_pair(w) # remove parentheses around word
        if len(w) == 0:
            continue
        #
        w=remove_single_lbracket(w)
        if len(w) == 0:
            number_skipped=number_skipped+1
            continue
        #
        if is_MiscSymbol_or_Pictograph(w):
            number_skipped=number_skipped+1
            continue
        if is_equation(w):
            number_skipped=number_skipped+1
            continue
        #
        if w.endswith('&amp'):
            w=w[:-4]
        #
        if len(w) < 1:
            number_skipped=number_skipped+1
            continue
        #
        # check for names and symbols of elements
        if w in common_english.chemical_elements:
            number_skipped=number_skipped+1
            continue
        if w.lower() in common_english.chemical_elements:
            number_skipped=number_skipped+1
            continue

        if w in common_english.chemical_elements_symbols:
            number_skipped=number_skipped+1
            continue
        #
        if w in common_english.common_units:
            number_skipped=number_skipped+1
            continue
        # check for units after converting to lower case
        if w.lower() in common_english.common_units:
            number_skipped=number_skipped+1
            continue
        #
        if w in common_english.mathematical_words_to_ignore:
            number_skipped=number_skipped+1
            continue
        #
        # remove possessives
        if w.endswith("'s"):
            w=w[:-2]
        #
        if w.endswith("´s"):
            w=w[:-2]
        #
        if w.endswith("’s"):
            w=w[:-2]
        #
        wtemp=w[:]
        if wtemp.replace('-', '').isdigit():
            number_skipped=number_skipped+1
            continue
        #
        wtemp=w[:]
        if wtemp.replace('/', '').isdigit():
            number_skipped=number_skipped+1
            continue
        #
        if w in miss_spelled_to_correct_spelling_CBH.miss_spelled_to_correct_spelling:
            number_skipped=number_skipped+1
            continue
        #
        if is_number(w):
            number_skipped=number_skipped+1
            continue
        #
        w_with_period=w+'.'
        if w in common_english.abbreviations_ending_in_period or \
           w_with_period in common_english.abbreviations_ending_in_period or \
           w_with_period.lower() in common_english.abbreviations_ending_in_period:
            number_skipped=number_skipped+1
            continue
        #
        if w in common_english.programming_keywords:
            number_skipped=number_skipped+1
            continue
        #
        # check Oxford 3000 & 5000 both American and British
        #
        if (w in american_3000_words) or (w in american_3000_words_plurals):
            number_skipped=number_skipped+1
            continue
        #
        if (w in american_5000_words) or (w in american_5000_words_plurals):
            number_skipped=number_skipped+1
            continue
        #
        # check for lower case version
        if (w.lower() in american_3000_words) or (w.lower() in american_3000_words_plurals):
            number_skipped=number_skipped+1
            continue
        #
        if (w.lower() in american_5000_words) or (w.lower() in american_5000_words_plurals):
            number_skipped=number_skipped+1
            continue
        #
        if (w in oxford_3000_words) or (w in oxford_3000_words_plurals):
            number_skipped=number_skipped+1
            continue
        #
        if (w in oxford_5000_words) or (w in oxford_5000_words_plurals):
            number_skipped=number_skipped+1
            continue
        #
        # check for lower case version
        if (w.lower() in oxford_3000_words) or (w.lower() in oxford_3000_words_plurals):
            number_skipped=number_skipped+1
            continue
        #
        if (w.lower() in oxford_5000_words) or (w.lower() in oxford_5000_words_plurals):
            number_skipped=number_skipped+1
            continue

        #
        if in_dictionary(w.lower(), words_EFLLex): # all the words in EFLLex are in lower case
            number_skipped=number_skipped+1
            continue
        #
        if in_dictionary(w.lower(), words_SVALex): # all the words in SVALex are in lower case
            number_skipped=number_skipped+1
            continue
        #
        if w in kelly_swedish_file:
            number_skipped=number_skipped+1
            continue
        #
        if w.lower() in common_english.thousand_most_common_words_in_English_old:
            number_skipped=number_skipped+1
            continue
        #
        if w in common_english.misc_words_to_ignore:
            number_skipped=number_skipped+1
            continue
        #
        if w in well_known_acronyms:
            number_skipped=number_skipped+1
            continue
        #
        # ignore plural of acronyms
        if w.endswith('s') and len(w) > 1:
            if w[:-1] in well_known_acronyms:
                number_skipped=number_skipped+1
                continue
        #
        if w in common_english.place_names:
            number_skipped=number_skipped+1
            continue
        #
        if w in common_english.company_and_product_names:
            number_skipped=number_skipped+1
            continue
        #
        if w in common_english.common_programming_languages:
            number_skipped=number_skipped+1
            continue
        #
        if w in common_swedish.common_swedish_words:
            number_skipped=number_skipped+1
            continue
        #
        if w.lower() in common_swedish.common_swedish_words:
            number_skipped=number_skipped+1
            continue
        #
        if w in common_swedish.common_swedish_technical_words:
            number_skipped=number_skipped+1
            continue
        #
        if w.lower() in common_swedish.common_swedish_technical_words:
            number_skipped=number_skipped+1
            continue
        #
        if w in common_english.names_of_persons:
            number_skipped=number_skipped+1
            continue
        #
        if w in common_english.common_English_words:
            number_skipped=number_skipped+1
            continue
        #
        if w.lower() in common_english.common_English_words:
            number_skipped=number_skipped+1
            continue
        #
        if w in common_english.common_danish_words:
            number_skipped=number_skipped+1
            continue
        #
        if w in common_english.common_german_words:
            number_skipped=number_skipped+1
            continue
        #
        if w.lower() in common_english.common_german_words:
            number_skipped=number_skipped+1
            continue
        #
        if w in common_english.common_icelandic_words:
            number_skipped=number_skipped+1
            continue
        #
        if w.lower() in common_english.common_icelandic_words:
            number_skipped=number_skipped+1
            continue
        #
        if w in common_english.common_latin_words:
            number_skipped=number_skipped+1
            continue
        #
        if w.lower() in common_english.common_latin_words:
            number_skipped=number_skipped+1
            continue
        #
        if w in common_english.common_norwegian_words:
            number_skipped=number_skipped+1
            continue
        #
        if w.lower() in common_english.common_norwegian_words:
            number_skipped=number_skipped+1
            continue
        #
        if w in common_english.common_portuguese_words:
            number_skipped=number_skipped+1
            continue
        #
        if w.lower() in common_english.common_portuguese_words:
            number_skipped=number_skipped+1
            continue
        #
        if w in common_english.common_finnish_words:
            number_skipped=number_skipped+1
            continue
        #
        if w in common_english.common_french_words:
            number_skipped=number_skipped+1
            continue
        #
        if w.lower() in common_english.common_french_words:
            number_skipped=number_skipped+1
            continue
        #
        if w in common_english.common_spanish_words:
            number_skipped=number_skipped+1
            continue
        #
        if w.lower() in common_english.common_spanish_words:
            number_skipped=number_skipped+1
            continue
        #
        if w in common_english.common_italian_words:
            number_skipped=number_skipped+1
            continue
        #
        if w.lower() in common_english.common_italian_words:
            number_skipped=number_skipped+1
            continue
        #
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
            if new_w in common_english.common_English_words:
                number_skipped=number_skipped+1
                continue
        #
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
            if new_w in common_english.common_English_words:
                number_skipped=number_skipped+1
                continue
        #
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
            if new_w in common_english.common_English_words:
                number_skipped=number_skipped+1
                continue
        #
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
            if new_w in common_english.common_English_words:
                number_skipped=number_skipped+1
                continue
        #
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
            if new_w in common_english.common_English_words:
                number_skipped=number_skipped+1
                continue
        #
        if w.lower() in common_english.common_English_words:
            number_skipped=number_skipped+1
            continue
        #
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
            if new_w in common_swedish.common_swedish_words:
                number_skipped=number_skipped+1
                continue
        #
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
            if new_w in common_swedish.common_swedish_words:
                number_skipped=number_skipped+1
                continue
        #
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
            if new_w in common_swedish.common_swedish_words:
                number_skipped=number_skipped+1
                continue
        #
        # also look at the case of a word with a lower case first part but upper or title case following it
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
            if new_w in common_swedish.common_swedish_words:
                number_skipped=number_skipped+1
                continue
        #
        if w in well_known_acronyms:
            number_skipped=number_skipped+1
            continue
        #
        if w.isupper():
            if  w.endswith('-'):
                if w[:-1] not in well_known_acronyms and w[:-1] not in common_english.company_and_product_names:
                    potential_acronyms.add(w[:-1])
                    number_of_potential_acronyms=number_of_potential_acronyms+1
            else:
                potential_acronyms.add(w)
            number_of_potential_acronyms=number_of_potential_acronyms+1
            continue
        #
        if w.lower() in well_known_acronyms:
            number_skipped=number_skipped+1
            continue
        #
        # ignore plural of acronyms
        if options.swedish:
            if w.lower().endswith(':s') and len(w) > 2:
                if w[:-2] in well_known_acronyms:
                    number_skipped=number_skipped+1
                    continue
        else:
            if w.lower().endswith('s') and len(w) > 1:
                if w[:-1] in well_known_acronyms:
                    number_skipped=number_skipped+1
                    continue
        #
        # check the fall_back case
        wl=w.replace(' ', '')
        wl=wl.replace('-', '')
        wl=wl.lower()
        if wl in fall_back_words:
            count_fall_back_cases=count_fall_back_cases+1
            continue
        #
        # re check - as the word my pop up again after the above manipulations
        if w in words_to_ignore:
            continue
        #
        if w == 'HCl':
            nf = w in words_to_ignore
            print(f'not found: {w} - {initial_w} - {nf=}')
        words_not_found.add(w)
    #
    print(f'{len(words_not_found)} in words_not_found')
    #print(f'{words_not_found} in words_not_found')
    print(f'{number_skipped=}')
    print(f'{number_of_potential_acronyms=}')
    print(f'{count_fall_back_cases=}')
    #
    if options.swedish:
        save_collected_words(words_not_found, 'Swedish')
    else:
        save_collected_words(words_not_found, 'English')
    #
    # save the potential acronyms
    save_potential_acronyms(potential_acronyms)
    print(f'unique potential acronyms: {len(potential_acronyms)}')
    #
    if not (Verbose_Flag or True):
        return
    #
    first_two_letters=set()
    for w in potential_acronyms:
        if len(w) == 1:
            first_two_letters.add(w)
        elif len(w) == 2:
            first_two_letters.add(w)
        else:
            first_two_letters.add(w[0]+w[1])
    #
    if len(first_two_letters) > 0:
        print(f'{first_two_letters=}')

#
if __name__ == "__main__": main()

