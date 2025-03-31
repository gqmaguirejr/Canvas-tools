#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -*- mode: python; python-indent-offset: 4 -*-
#
# ./prune_unique_words.py course_id
# 
# The program takes the dictionary stored as JSON as output of compute_unique_words_for_pages_in_course.py, specifically the
# unique_words-for-course-frequency-<course_id>.txt file and prunes out words based on different
# filtering.
#
# One aim is to understand the language level used in the course. The levels are based on the Common European Framework of Reference for Languages: Learning, teaching, assessment (CEFR).
#
#
#
# The outputs a reduced file with the filtered dictionary.
#
# The second aim of the effort was to help a teacher extract words that might be put in a vocabulary list for the course.
# Ideally, a pair language list of English and Swedish (assuming that the course is taught in one of these two languages).
#
# with the option "-v" or "--verbose" you get lots of output - showing in detail the operations of the program
#
# Examples:
# ./prune_unique_words.py 11544
#
# ./prune_unique_words.py --bar --slash --dir Course_41668 41668
#
# ./prune_unique_words.py --bar --slash --combined --dir Course_41668 41668
#
# Note: It does not access the Canvas course, but rather uses the output from another program.
#
#       The program is currently mainly focused on courses taught in (American) English.
#
# ======================================================================
#
# For general background about CEFR see https://www.cambridgeenglish.org/images/126011-using-cefr-principles-of-good-practice.pdf
# 
# The six levels are:
#
# C2 Mastery                           ]
#                                      ]  ---- Proficient user ---
# C1 Effective Operational Proficiency ]
#
# B2 Vantage        ]
#                   ]  ---- Independent user ---
# B1 Threshold      ]
#
#
# A2 Waystage       ]
#                   ]   ---- Basic user ---
# A1 Breakthrough   ]
#
#
#
# A number of different sources have been used to provide CEFR data for a given word.
#
# The first sources for CEFR values were:
#    The Oxford 3000™ (American English)
#    The Oxford 5000™ (American English)
# Information was extraced from the PDF files and used to create a spreadsheet with pages for the above two sources.
# Each row in the spreadhseet can have multiple CEFR levels. each will have a list of parts of speech (pos).
#
# A major source for CEFR levles is: https://languageresearch.cambridge.org/wordlists/text-inspector
# The cefrlex materials was used to improve the CEFR levels in common_English_words
# Google's Bart was used to add more CEFR level information to common_English_words
#
# Another source of data is from CEFRLex:
#
# For more background see:
#   Dürlich, L. and François, T., EFLLex: A Graded Lexical Resource for Learners of English as a Foreign Language.
#   In Proceedings of the 11th International Conference on Language Resources and Evaluation (LREC 2018). Miyazaki, Japan, 7-12 May.
#
# See their site: https://cental.uclouvain.be/cefrlex/efllex/
# They have EFLLex with NLP4J parts of speech - English in receptive context · CEFR levels: A1 A2 B1 B2 C1 -- as a downloadable CSV file.
# They have done 6 different languages, see https://cental.uclouvain.be/cefrlex/
# Downloads of the CSV files can be done from: https://cental.uclouvain.be/cefrlex/download/
# Note that the multiple word entries have underscores where there would be spaces. [Currently the program does not deal with multiple words
#   - since these do not come out of the tokenization done with the other program.]
#
# One of these languages is Swedish:
#   and they have split this into two parts: 
#     SVALex is a lexicon of receptive vocabulary for Swedish as a second/foreign language (SVA) 
#     SweLLex is a lexicon of productive vocabulary for Swedish as a second/foreign language (SVA)
#
#   Elena Volodina, Ildikó Pilán, Ingegerd Enström, Lorena Llozhi, Peter Lundkvist, Gunlög Sundberg, Monica Sandell. 2016.
#   SweLL on the rise: Swedish Learner Language corpus for European Reference Level studies. Proceedings of LREC 2016, Slovenia.
#
#   Elena Volodina, Ildikó Pilán, Lorena Llozhi, Baptiste Degryse, Thomas François. 2016. SweLLex: second language learners'
#    productive vocabulary. Proceedings of the workshop on NLP4CALL&LA. NEALT Proceedings Series / Linköping Electronic Conference Proceedings
#
# The SVALex_Korp, SweLLex_Korp, and EFLLex_NLP4 have entries for a word with a specific part of speech and then
# the frequency with which this word and this specific POS. The program uses the most frequent CEFR level.
# If there are multiple entries (due to different POS), then the lowest CEFR level is used when calculating statistics.
# 
# Note that the orignal CEFRLex CSV files contain the statistics for the frequency of a give word and a specific part of speech
# for each of the sourses that was used. The columns related to the sources have been eliminated and all of the three sources have been
# placed as separate sheets in a single spreadsheet file.
# Before removing the source frequencies the spreadsheet was 20,403,059 bytes, while the reduced spreadsheet is 2,019,937 bytes in size.
#
# There is a also a French version:
# For FLELex (Treetagger and CRF Tagger) :
#   François, T., Gala, N., Watrin, P. & Fairon, C. FLELex: a graded lexical resource for French foreign learners. In the 9th International Conference on Language Resources and Evaluation (LREC 2014). Reykjavik, Iceland, 26-31 May.
# For FLELex / Beacco :
#  Pintard, A. and François, T. (2020). Combining expert knowledge with frequency information to infer CEFR levels for words. In Proceedings of the 1st Workshop on Tools and Resources to Empower People with REAding DIfficulties (READI) (pp. 85-92).
#
# Note that the two french sources use different part of speech tagging than the Swedish sheets.
# The 'FLELex_CRF Tagger' include multiple word entries. The words are separated by spaces.
#
# There is also the Kelly (Keywords for Language Learning for Young and adults alike) list for Swedish:
# See https://spraakbanken.gu.se/en/resources/kelly
# cite:
#    Kilgarriff, Adam; Charalabopoulou, Frieda; Gavrilidou, Maria; Johannessen, Janne Bondi; Khalil, Saussan; Kokkinakis, Sofie Johansson; Lew, Robert; Sharoff, Serge; Vadlapudi, Ravikiran & Volodina, Elena. 2014. Corpus-based vocabulary lists for language learners for nine languages. Language Resources and Evaluation, 48:121–163, DOI 10.1007/s10579-013-9251-2.
#
# Note that the sources do not necessarily agree on a CEFR level. For example, for the word 'tillfälle'
# Google Bard says it is *A2', while in SVALex it most frequently occurs as 'C1'. and the Kelly list says it is 'A1'.
# It is common that when there is disagreement, that the levels are +/-1 of the other source(s).
#
# 2025.03.31 add levels: 'D1', 'D2' for the Oxford academic levels
#
# 2023.12.05
#
# G. Q. Maguire Jr.
#


import csv, time
from pprint import pprint
import optparse
import sys

import json
import re

import copy  # so that we can make a deep copy


from lxml import html

# Use Python Pandas to create XLSX files
import pandas as pd

# to use math.isnan(x) function
import math

import nltk

# width to use for outputting numeric values
Numeric_field_width=7

import sys
sys.path.append('/z3/maguire/Canvas/Canvas-tools')  # Include the path to module_folder
sys.path.append('/home/maguire/Canvas/Canvas-tools')

#  as common_English_words, common_swedish_words, common_swedish_technical_words
import common_english_and_swedish
import miss_spelled_to_correct_spelling
import diva_merged_words
import diva_corrected_abstracts


prefixes_to_ignore=[
    "'",
    "\\",
    "­",
    "×",
    "‘",
    "’",
    "’",    
    #‘",
    '$',
    '%',
    '+',
    ',',
    '-',
    './',
    ':',
    '=',
    '>',
    '[',
    '\u00b4\u00b4', # double right quote marks
    '{',
    '|',
    '¡',
    '§',
    '­',
    '¿',
    '˜',
    '‐',
    '–',
    '—',
    '―',
    '“',
    '”',
    '”',
    '„',
    '†',
    '‡',
    '•',
    '⇒',
    '−',
    '∼',
    '✓',
    '✔',
    '✝',
    '',
    '',
    '􀀀',
]

suffixes_to_ignore=[
    "'",
    '-',
    '.',
    '/',
    '\\',
    '†',
    '‡',
    '…',
    ']',
    '$',
    '%',
    '‟',
    '”',
    "’",
    '}',
]

def check_spelling_errors(s, url):
    if s in common_english_and_swedish.miss_spelled_words:
        print(f'miss spelling {s} at {url=}')


# remove prefixs
def prune_prefix(s):
    for pfx in prefixes_to_ignore:
        if s.startswith(pfx):
            s=s[len(pfx):]
            return prune_prefix(s)
    return s

# remove suffix
def prune_suffix(s):
    for sfx in suffixes_to_ignore:
        if s.endswith(sfx):
            s=s[:-len(sfx)]
            return prune_suffix(s)
    return s

def remove_lbracket_number_rbracket(s):
    matches = re.findall("\[[0-9]+\]", s)
    matches = list( dict.fromkeys(matches) )
    matches.sort()
    for m in matches:
        s=s.replace(m, '')
    return s



currency_symbols=[
    '$',
    '£',
    '€',
]

words_to_ignore=[
    '\n',
    '\x0a',
    "'",
    "''",
    '!',
    '#',
    '$',
    '%',
    '&',
    '(',
    ')',
    '*',
    '+',
    '+/-',
    ',',
    '-',
    '--',
    '.',
    '..',
    '...',
    '/',
    ':',
    ';',
    '<',
    '=',
    '==',
    '>',
    '?',
    '@',
    '[',
    ']',
    '`',
    '``',
    '{',
    '|',
    '}',
    '§',
    '§',
    '©',
    '½',
    '–',
    '‘',
    '’',
    '“',
    '”',
    '†',
    '‡',
    '…',
    '→',
    '⇒',
    '∴',
    '≅',
    '≥',
    '①',
    '②',
    '③',
    '④',
    '⑤',
    '✔',
    '✛',

]


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

hex_digits='0123456789abcdefABCDEF'

def is_hex_number(string):
    if string.startswith('0x'):
        for c in string[2:]:
            if c not in hex_digits:
                return False
        return True
    else:
        return False

def is_number_with_commas(string):
    if string.count(',') > 0:
        string=string.replace(',', '')
        if string.isdigit():
            return is_number(string)
    # otherwise
    return False

def is_integer_range_or_ISSN(string):
    if string.count('-') == 1:
        string=string.replace('-', "")
        return string.isdigit()
    elif string.count('–') == 1:
        string=string.replace('–', "")
        return string.isdigit()
    # otherwise
    return False
    
def is_ISBN(string):
    # if there is a trailing period remove it
    if len(string) > 2 and string.endswith("."):
        string=string[:-1]
    #
    if string.startswith("978-") and (string.count('-') == 4 or string.count('-') == 3):
        string=string.replace("-", "")
        if string.isnumeric():
            return True
    # ISBN-13 without additional dashes
    elif (string.startswith("978-") and string[4:].count('-') == 0) and string[4:].isdigit:
            return True
    elif string.count('-') == 3:
        string=string.replace("-", "")
        if string.isnumeric():
            return True
    # otherwise
    return False
    
# a DOI has the form: <DOI prefix>/<DOI suffix>
# <DOI prefix> has the form <directory indicator>.<registrant code>
# <directory indicator> is always '10'
def is_DOI(string):
    global Verbose_Flag
    if string.startswith("DOI:"):
        string=string[4:]
    if string.startswith("10.") and string.count('/') >= 1:
        doi_suffix_offset=string.find('/')
        doi_prefix=string[0:doi_suffix_offset]
        registrant_code=doi_prefix[3:]
        doi_suffix=string[doi_suffix_offset+1:]
        if Verbose_Flag:
            print(f'{doi_prefix=} with {registrant_code=} and {doi_suffix=}')
        return True
    # otherwise
    return False

def is_IPv4_dotted_decimal(string):
    if string.count('.') == 3:
        ipv=string.split(".")
        for n in ipv:
            if n.isnumeric() and int(n) < 256:
                continue
            else:
                return False            
        # if all numbers are less than 256
        return True
    # otherwise
    return False

def is_IPv4_dotted_decimal_with_prefix_length(string):
    if string.count('.') == 3 and string.count('/') == 1 and string.rfind('.') < string.find('/'):
        parts=string.split("/")
        if int(parts[1]) <= 32:
            return is_IPv4_dotted_decimal(parts[0])
    # otherwise
    return False

def is_MAC_address(string):
    global Verbose_Flag
    if string.count(':') == 5:
        mv=string.split(":")
        for n in mv:
            if Verbose_Flag:
                print(f"{n=} {is_hex_number('0x'+n)=} and {int('0x'+n, 0)=}")
            if is_hex_number('0x'+n) and int('0x'+n, 0) < 256:
                continue
            else:
                return False            
        # if all numbers are less than 256
        return True
    # otherwise
    return False

def is_IPv6_address(string):
    global Verbose_Flag
    if string.count(':') == 7 or (string.count('::') == 1 and string.count(':') < 7):
        mv=string.split(":")
        for n in mv:
            if len(n) == 0:
                continue
            if Verbose_Flag:
                print(f"{n=} {is_hex_number('0x'+n)=} and {int('0x'+n, 0)=}")
            if is_hex_number('0x'+n) and int('0x'+n, 0) < 65536:
                continue
            else:
                return False            
        # if all numbers are less than 65535
        return True
    # otherwise
    return False



def is_phone_number(string):
    # note that it does not do a range check on the numbers
    if string.startswith('+'):
        string=string[1:].replace("-", "")
        if string.isnumeric():
            return True
    # otherwise
    return False

# time offsets in the transcripts have the form dd:dd:dd
def is_time_offset(string):
    if string.count(':') == 2:
        string=string.split(":")
        for n in string:
            if n.isnumeric() and int(n) < 60:
                continue
            else:
                return False
        return True
    # otherwise
    return False

# start-end times have the form dd:dd-dd:dd
def is_start_end_time(string):
    if string.count('-') == 1 and string.count(':') == 2:
        string=string.split("-")
        for m in string:
            m=m.split(":")
            for n in m:
                if n.isnumeric() and int(n) < 60:
                    continue
                else:
                    return False
        return True
    # otherwise
    return False

# look for strings of the form yyyy-mm-dd or yyyy.mm.dd
def is_YYYY_MM_DD(s):
    global Verbose_Flag
    # define an empty d
    d = ('', '', '')

    if not isinstance(s, str):
        return False
    if not len(s) == 10:
        return False
    if s.count('.') == 2:
        if s[4] == '.' and s[7] == '.':
            d=s.split('.')
        else:
            return False
    elif s.count('-') == 2:
        if s[4] == '-' and s[7] == '-':
            d=s.split('-')
        else:
            return False
    else:
        return False
    #
    #print(f'{d=}')
    if len(d[0]) == 4 and d[0].isdigit():
        yyyy=d[0]
    else:
        return False
    #
    if len(d[1]) == 2 and d[1].isdigit():
        if int(d[1]) < 13:
            mm=d[1]
        else:
            print(f'problem in month number in {string}')
            return False
    else:
        return False
    #
    if d[2].isdigit():
        if int(d[2]) < 32:
            dd=d[2]
        else:
            print(f'problem in day number in {string}')
    else:
        return False
    #
    if Verbose_Flag:
        print(f'{yyyy=} {mm=} {dd=}')
    return True

months_and_abbrevs=[
    'Jan',
    'January',
    'Feb',
    'February',
    'Mar',
    'March',
    'Apr',
    'April',
    'May',
    'Jun',
    'June',
    'Jul',
    'July',
    'Aug',
    'August',
    'Sep',
    'Sept',
    'September',
    'Oct',
    'October',
    'Nov',
    'November',
    'Dec',
    'December',
]    

# look for strings of the form dd-mmm-yyyy
def is_DD_MMM_YYYY(string):
    global Verbose_Flag
    if string.count('-') == 2:
        d=string.split('-')
    else:
        return False
    if Verbose_Flag:
        print(f'is_DD_MMM_YYYY({string}) {d=}')
    if len(d) == 3 and d[2].isdigit() and ((len(d[2]) == 4 or len(d[2]) == 2)):
        yyyy=d[2]
    else:
        return False
    #
    if d[0].isdigit():
        if int(d[0]) < 32:
            dd=d[0]
        else:
            print(f'Error in day in {string} "{d[0]}"')
            return False
    else:
        return False
    #
    # Note that the month abbreviation must be three characters long
    if len(d[1]) >= 3 and not d[1].isdigit():
        if d[1].lower().capitalize() in months_and_abbrevs:
            mm=d[1]
        else:
            print(f'Error in month in {string}  "{d[1]}"')
            return False
    else:
        return False
    #
    if Verbose_Flag:
        print(f'{yyyy=} {mm=} {dd=}')
    return True

def approximate_number(string):
    # remove tilde prefix
    if len(string) > 1 and string[0]=='~':
        string=string[1:]
    #
    if string.count(',') > 0:
        string=string.replace(',', "")
    return is_number(string)

def is_colon_range_or_HH_colon_MM(string):
    if string.count(':') == 1:
        string=string.replace(':', "")
        return string.isdigit()
    # otherwise
    return False

def is_fraction(string):
    if string.count('/') == 1:
        string=string.replace('/', "")
        # if a fractional part, remove the 'th' before checking further
        if string.endswith('th'):
            string=string[:-2]
        return string.isdigit()
    # otherwise
    return False

    
def is_part_of_DiVA_identifier(string):
    if string.startswith('3Adiva-'):
        return True
    # otherwise
    return False
    
# to deal with things of the form: 2016-06-10T08:16:13Z
def is_date_time_string(string):
    if string.endswith('Z'):
        string=string[:-1]
    if string.count('-') == 2 and  string.count(':') == 2:
        if string[4] == '-' and string[7] == '-' and string[10] == 'T' and string[13] == ':' and string[16] == ':':
            # print(f'{string[0:4]=}')
            # print(f'{string[5:7]=}')
            # print(f'{string[8:10]=}')
            # print(f'{string[11:13]=}')
            # print(f'{string[14:16]=}')
            # print(f'{string[17:]=}')
            string=string[0:4]+string[5:7]+string[8:10]+string[11:13]+string[14:16]+string[17:]
            #print(f'{string=}')
            if string.isdigit():
                return True
    # otherwise
    return False
    
filename_extentions_to_skip=[
    '.bib',
    '.c',
    '.csv',
    '.doc',
    '.docx',
    '.html',
    '.ipynb',
    '.jpg',
    '.js',
    #'.json',
    '.mods',
    '.pdf',
    '.png',
    '.ppt',
    '.pptx',
    '.py',
    '.srt',
    '.svg',
    '.xls',
    '.xlsx',
    '.xml',
    '.zip',
]
    
def is_filename_to_skip(string):
    for f in filename_extentions_to_skip:
        if string.endswith(f):
            return True
    # otherwise
    return False

# if there are multiple capital letters
def is_multiple_caps(s):
    len_s=len(s)
    count_caps=0
    count_lower_case=0
    #
    # to skip hyphenated words which are title cased
    if s == s.lower().title():
        return False        
    #
    if len_s > 1:
        for l in s:
            if l.isupper():
                count_caps=count_caps+1
            if l.islower():
                count_lower_case=count_lower_case+1
        #print(f'{count_caps=} {count_lower_case=}')
        if count_caps > 1:
            if count_lower_case > count_caps:
                return False
            else:
                return True
    # otherwise
    return False

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

def isVowel(ch):
    # given a list of vowels 
    vowels = "aeiouåäöAEIOUÅÄÖ"
    return (vowels.find(ch) != -1) 


domains_to_filter=[
    '.aero',
    '.arpa',
    '.biz',
    '.com',
    '.coop',
    '.cooperatives',
    '.edu',
    '.gov',
    '.info',
    '.int',
    '.mil',
    '.museum',
    '.name',
    '.net',
    '.org',
    '.pro',
    # country TLDs
    '.ac',
    '.ad',
    '.ae',
    '.af',
    '.ag',
    '.ai',
    '.al',
    '.am',
    '.ao',
    '.aq',
    '.ar',
    '.as',
    '.at',
    '.au',
    '.aw',
    '.ax',
    '.az',
    '.ba',
    '.bb',
    '.bd',
    '.be',
    '.bf',
    '.bg',
    '.bh',
    '.bi',
    '.bj',
    '.bm',
    '.bn',
    '.bo',
    '.bq',
    '.br',
    '.bs',
    '.bt',
    '.bw',
    '.by',
    '.bz',
    '.ca',
    '.cc',
    '.cd',
    '.cf',
    '.cg',
    '.ch',
    '.ci',
    '.ck',
    '.cl',
    '.cm',
    '.cn',
    '.co',
    '.cr',
    '.cu',
    '.cv',
    '.cw',
    '.cx',
    '.cy',
    '.cz',
    '.de',
    '.dj',
    '.dk',
    '.dm',
    '.do',
    '.dz',
    '.ec',
    '.ee',
    '.eg',
    '.er',
    '.es',
    '.et',
    '.eu',
    '.di',
    '.fj',
    '.fm',
    '.fo',
    '.fr',
    '.ga',
    '.gd',
    '.',
    '.ge',
    '.gf',
    '.gg',
    '.gh',
    '.gi',
    '.gl',
    '.gm',
    '.gp',
    '.gq',
    '.ge',
    '.gs',
    '.gt',
    '.gu',
    '.gw',
    '.gy',
    '.hk',
    '.hm',
    '.hn',
    '.hr',
    '.hu',
    '.id',
    '.ie',
    '.il',
    '.im',
    '.in',
    '.io',
    '.iq',
    '.ir',
    '.is',
    '.it',
    '.je',
    '.jm',
    '.jo',
    '.jp',
    '.ke',
    '.kg',
    '.kh',
    '.ki',
    '.km',
    '.kn',
    '.kp',
    '.kr',
    '.kw',
    '.kz',
    '.la',
    '.lb',
    '.lc',
    '.li',
    '.lk',
    '.lr',
    '.ls',
    '.lt',
    '.lu',
    '.lv',
    '.ly',
    '.ma',
    '.mc',
    '.md',
    '.me',
    '.mg',
    '.mh',
    '.mk',
    '.ml',
    '.mm',
    '.mn',
    '.mo',
    '.mp',
    '.mq',
    '.me',
    '.ms',
    '.mt',
    '.mu',
    '.mv',
    '.mw',
    '.mx',
    '.my',
    '.mz',
    '.na',
    '.nc',
    '.ne',
    '.nf',
    '.ng',
    '.ni',
    '.nl',
    '.no',
    '.np',
    '.nr',
    '.nu',
    '.nz',
    '.om',
    '.pa',
    '.pe',
    '.pf',
    '.ph',
    '.pk',
    '.ol',
    '.om',
    '.pn',
    '.pr',
    '.ps',
    '.pt',
    '.pw',
    '.py',
    '.qa',
    '.re',
    '.ro',
    '.rs',
    '.ru',
    '.rw',
    '.sa',
    '.sb',
    '.sc',
    '.sd',
    '.se',
    '.sg',
    '.sh',
    '.si',
    '.sk',
    '.sl',
    '.sm',
    '.sn',
    '.so',
    '.sr',
    '.ss',
    '.st',
    '.su',
    '.sv',
    '.sx',
    '.sy',
    '.sz',
    '.tc',
    '.tf',
    '.tg',
    '.th',
    '.tj',
    '.tk',
    '.tl',
    '.tm',
    '.tn',
    '.to',
    '.tr',
    '.tt',
    '.tv',
    '.tw',
    '.tz',
    '.ua',
    '.ug',
    '.uk',
    '.us',
    '.uy',
    '.uz',
    '.va',
    '.vc',
    '.ve',
    '.vg',
    '.vi',
    '.vn',
    '.vu',
    '.wf',
    '.ws',
    '.ye',
    '.yt',
    '.za',
    '.zm',
    '.zw',
]

def is_domainname(s):
    for d in domains_to_filter:
        if s.endswith(d) or s.endswith(d.upper()):
            return True
    return False

# A helpful function
# def generate_chars(start, end):
#     for i in range(start, end+1, 6):
#         print(f"'{chr(i)}', '{chr(i+1)}', '{chr(i+2)}', '{chr(i+3)}', '{chr(i+4)}', '{chr(i+5)}',")

def is_MathSymbol(s):
    if not len(s) == 1:
        return False

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


def is_improbable_word(s):
    if s.count('=') > 0 :
        return True
    if s.count('.') > 3 or s.count('/') > 2 or s.count('_') > 1 or s.count(':') > 1:
        return True
    if s.startswith('.') or s.startswith('/') or s.startswith('0x'):
        return True
    if len(s) > 0 and s[0].isdigit() and (s.count('.') > 1 or s.count('/') > 1):
        return True
    if s.startswith('~'):
        return True
    # otherwise
    return False

def choose_lowest_cefr_level(wl):
    level_order=['A1', 'A2', 'B1', 'B2', 'C1', 'C2', 'D1', 'D2', 'xx']
    for l in level_order:
        if l in wl:
            return l
    # otherwise
    print(f'Error in choose_lowest_cefr_level({wl})')
    return False

def cefr_level_index(wl):
    level_order=['A1', 'A2', 'B1', 'B2', 'C1', 'C2', 'D1', 'D2', 'xx']
    for l in level_order:
        if l in wl:
            return l
    # otherwise
    print(f'error in cefr_level_index({w1})')

def choose_lowest_cefr_level_from_two(w1, w2):
    level_order=['A1', 'A2', 'B1', 'B2', 'C1', 'C2', 'D1', 'D2', 'xx']
    if cefr_level_index(w1) < cefr_level_index(w2):
        return w1
    else:
        return w2
    

    # otherwise
    print(f'Error in choose_lowest_cefr_level_from_two({w1}, {w2})')
    return False

def cefr_level_to_index(li):
    level_order=['A1', 'A2', 'B1', 'B2', 'C1', 'C2', 'D1', 'D2', 'xx']
    for indx, l in enumerate(level_order):
        if li == l:
            return indx
    return False

def compare_cefr_levels(l1, l2):
    level_order=['A1', 'A2', 'B1', 'B2', 'C1', 'C2', 'D1', 'D2', 'xx']
    l1i=cefr_level_to_index(l1)
    l2i=cefr_level_to_index(l2)
    if isinstance(l1i, int) and isinstance(l2i, int):
        return l2i - l1i
    # otherwise
    print(f'Error in compare_cefr_level({l1}, {l2})')
    return False


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
def read_CEFRLLex_French_data(filenamme, sheetname):
    global Verbose_Flag

    df = pd.read_excel(open(filenamme, 'rb'), sheet_name=sheetname)
    # the spreadsheet columns are:
    # word	tag	freq_a1	freq_a2	freq_b1	freq_b2	freq_c1	freq_c2	freq_total	
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
        cefr_levela1=row['freq_a1']
        cefr_levela2=row['freq_a2']
        cefr_levelb1=row['freq_b1']
        cefr_levelb2=row['freq_b2']
        cefr_levelc1=row['freq_c1']
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


# takes in words and a filter_list
#  returns [updated_words, reduction]
def filter_words_by_list(words, filter_list):
    updated_words=dict()
    initial_number_of_words=len(words)

    for w in words:
        if w in filter_list:
            continue
        if w.lower() in filter_list:
            continue
        else:
            updated_words.update({w: words[w]})

    reduction=initial_number_of_words-len(updated_words)
    return [updated_words, reduction]

def filter_words_by_list_ending_in_period(words, filter_list):
    updated_words=dict()
    initial_number_of_words=len(words)

    for w in words:
        if w in filter_list:
            continue
        if w.lower() in filter_list:
            continue
        w_period=w+'.'
        if w_period in filter_list:
            continue
        if w_period.lower() in filter_list:
            continue
        else:
            updated_words.update({w: words[w]})

    reduction=initial_number_of_words-len(updated_words)
    return [updated_words, reduction]

def filter_words_by_list_case_sensitive(words, filter_list):
    updated_words=dict()
    initial_number_of_words=len(words)
    #
    for w in words:
        if w in filter_list:
            continue
        else:
            updated_words.update({w: words[w]})
    #
    reduction=initial_number_of_words-len(updated_words)
    return [updated_words, reduction]

# takes in words and a filter_list
#  returns [updated_words, reduction]
def filter_words_by_list(words, filter_list):
    updated_words=dict()
    initial_number_of_words=len(words)

    for w in words:
        if w in filter_list:
            continue
        if w.lower() in filter_list:
            continue
        else:
            updated_words.update({w: words[w]})

    reduction=initial_number_of_words-len(updated_words)
    return [updated_words, reduction]

# takes in words and a filter_function
#  returns [updated_words, reduction]
def filter_words_by_function(words, filter_function):
    updated_words=dict()
    initial_number_of_words=len(words)

    for w in words:
        if filter_function(w):
            continue
        else:
            updated_words.update({w: words[w]})

    reduction=initial_number_of_words-len(updated_words)
    return [updated_words, reduction]


singular_plural_forms={
    'company': 'companies',
    'process': 'processes',
}

# takes in words and expands those that have a | symbol indicating the singular and plural
# Note it does not deal with the count of the underlying words, i.e., the singular and plural
#  returns [updated_words, reduction]
def expand_bar_plurals(words):
    updated_words=dict()
    initial_number_of_words=len(words)

    for w in words:
        if w.count('|') == 1:
            s1=w.split('|')
            if len(s1) == 2:
                # check if the singular form is already present
                if s1[0] in words:
                    continue
                else:
                    updated_words.update({s1[0]: 1})

                if s1[0] in singular_plural_forms:
                    plural=singular_plural_forms[s1[0]]
                else:
                    plural=s1[0]+s1[1] 
                # check if the plular form is already present
                if plural in words:
                    continue
                else:
                    updated_words.update({s1[0]+s1[1]: 1})
        else:
            updated_words.update({w: words[w]})

    reduction=initial_number_of_words-len(updated_words)
    return [updated_words, reduction]

# takes in words that have a / symbol - generally indicating A/B
# add them as separe words
#  returns [updated_words, reduction]
def split_slashes(words):
    updated_words=dict()
    initial_number_of_words=len(words)

    for w in words:
        if not w.startswith('www') and w.count('/') == 1:
            s1=w.split('/')
            if len(s1) == 2:
                # check if the first word is already present
                if len(s1[0]) > 0:
                    if s1[0] in words:
                        updated_words.update({s1[0]: words[s1[0]]+1})
                    else:
                        updated_words.update({s1[0]: 1})

                if len(s1[1]) > 0:
                    if  s1[1] in words:
                        updated_words.update({s1[1]: words[s1[1]]+1})
                    else:
                        updated_words.update({s1[1]: 1})
            # always add the original
            updated_words.update({w: words[w]})
        else:
            updated_words.update({w: words[w]})

    reduction=initial_number_of_words-len(updated_words)
    return [updated_words, reduction]



# collect the set of CEFR levels for each owrd in a lex where the world can have different levels for different parts of speach all in one entry
def collect_CEFR_levels_from_dict(lex, lex_name):
    global Verbose_Flag

    levels=dict()
    for w in lex:
        collected_levels=[]
        collected_levels_CEFR_levels=[]
        if Verbose_Flag:
            print(f'{w=} {lex[w]}')
        
        if not isinstance(lex[w], dict):
            if Verbose_Flag:
                print(f'error in common_English_words at {w} as the value is not a dict! Skiping this word.')
            continue
        
        for k in lex[w].keys():
            if k and not (k == 'word' or k == 'plural'):
                collected_levels_CEFR_levels.append(k)

        if len(collected_levels_CEFR_levels) > 1:
            if Verbose_Flag:
                print(f"For {w['word']}: {collected_levels_CEFR_levels=}")
            # need to choose the lowest level
            collected_levels_CEFR_levels=choose_lowest_cefr_level(collected_levels_CEFR_levels)

        levels[w]=collected_levels_CEFR_levels

    if Verbose_Flag:
        print(f'collected levels for {lex_name}={levels}')
    return levels

def collect_CEFR_levels_from_list(lex, lex_name):
    global Verbose_Flag

    levels=dict()
    for w in lex:
        collected_levels=[]
        collected_levels_CEFR_levels=[]
        if Verbose_Flag:
            print(f'{w=} {lex[w]}')
        for k in w.keys():
            if k and not (k == 'word' or k == 'plural'):
                collected_levels_CEFR_levels.append(k)

        if len(collected_levels_CEFR_levels) > 1:
            if Verbose_Flag:
                print(f"For {w['word']}: {collected_levels_CEFR_levels=}")
            # need to choose the lowest level
            collected_levels_CEFR_levels=choose_lowest_cefr_level(collected_levels_CEFR_levels)

        levels[w['word']]=collected_levels_CEFR_levels

    if Verbose_Flag:
        print(f'collected levels for {lex_name}={levels}')
    return levels

def collect_CEFR_levels_for_plurals_from_list(lex, lex_name):
    global Verbose_Flag

    level_plural=dict()
    for w in lex:
        plural_form=w.get('plural', False)
        if plural_form:
            collected_levels=[]
            collected_levels_CEFR_levels=[]
            for k in w.keys():
                if k and not (k == 'word' or k == 'plural'):
                    # we only look for plural nouns and verbs
                    if 'n.' in w[k]:
                        collected_levels_CEFR_levels.append(k)
                    if 'v.' in w[k]:
                        collected_levels_CEFR_levels.append(k)
                #
            level_plural[plural_form]=collected_levels_CEFR_levels
    
    if Verbose_Flag:
        print(f'{level_plural=}')
        
    return level_plural

def collect_CEFR_levels_from_dict_common(lex, lex_name):
    global Verbose_Flag

    levels=dict()
    for w in lex:
        collected_levels=[]
        collected_levels_CEFR_levels=[]
        if Verbose_Flag:
            print(f'{w=} {lex[w]}')
        
        if not isinstance(lex[w], dict):
            print(f'error in {lex_name} at {w} as the value is not a dict! Skiping this word.')
            continue
        
        for k in lex[w].keys():
            if k and not (k == 'word' or k == 'plural'):
                collected_levels_CEFR_levels.append(k)

        if len(collected_levels_CEFR_levels) > 1:
            if Verbose_Flag:
                print(f"For {w}: {collected_levels_CEFR_levels=}")
            # need to choose the lowest level
            collected_levels_CEFR_levels=choose_lowest_cefr_level(collected_levels_CEFR_levels)

        levels[w]=collected_levels_CEFR_levels

    if Verbose_Flag:
        print(f'collected levels for {lex_name}={levels}')
    return levels


# each entry in the lex is of the form {'word': word, 'pos': pos, 'cefr_level': key_max}
def compute_lowest_CEFR_level(lex, lex_name):
    global Verbose_Flag

    level_words=dict()
    for w in lex:
        word=w['word']
        new_level=w['cefr_level']
            
        current_level=level_words.get(word, False)
        if current_level:
            lowest=choose_lowest_cefr_level_from_two(current_level, new_level)
        else:
            lowest=new_level
        level_words[word]=lowest

    if Verbose_Flag:
        print(f'loest levels for {lex_name}={level_words=}')

    return level_words

# returns updated words_count, level_words_SVALex_counts
def increment_usage_count_and_CEFR_level_counts(words_count, level_words_counts, word, level_words_lex,  lex_name):
    words_count=words_count+1
    cefr_level=level_words_lex.get(word, False)
    if cefr_level:
        if not isinstance(cefr_level, str) and len(cefr_level) >= 1:
            cefr_level=cefr_level[0]

        if isinstance(cefr_level, str):
            level_words_counts.update({cefr_level: level_words_counts.get(cefr_level, 0) +1})
        else:
            print(f'warning in computing level_words_counts for {lex_name}: {word=} {cefr_level=}')

    return [words_count, level_words_counts]

# check that the word is in the levels_to_use and update the entry with the level found, trying in the order the word, the title case, lower case, and uppercse
def conditionally_get_level(word, source_name, levels_to_use, entry):
    cefr_levels=False
    if word in levels_to_use:
        cefr_levels=levels_to_use.get(word, False)
    if not cefr_levels:
        cefr_levels=levels_to_use.get(word.title(), False)
    if not cefr_levels:
        cefr_levels=levels_to_use.get(word.lower(), False)
    if not cefr_levels:
            cefr_levels=levels_to_use.get(word.upper(), False)
    if cefr_levels:
        entry[source_name]=cefr_levels
    return entry

# only make an entry if the word is in the source
def conditionally_check_list(word, source_name, source_list, entry):
    if word in source_list:
        entry[source_name]=True
    return entry

def conditionally_check_list_case_insensitive(word, source_name, source_list, entry):
    if word in source_list:
        entry[source_name]=True
    if word.lower() in source_list:
        entry[source_name]=True
    return entry

def conditionally_check_with_function(word, source_name, filter_function, entry):
    if filter_function(word):
        entry[source_name]=True
    return entry


# Use ANSI escape sequence to output bold text on linux or surround by underline characters
def bold_text(text):
    if sys.platform.startswith('linux'):
        return "\033[1m" + text + "\033[0m"
    else:
        return "_not_"


def main():
    global Verbose_Flag
    global unique_words
    global total_words_processed
    global all_text

    directory_location="/z3/maguire/Language_Committee/"

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

    parser.add_option('-a', '--all',
                      dest="keepAll",
                      default=False,
                      action="store_true",
                      help="keep all unique words without filtering"
    )

    parser.add_option('--annotate',
                      dest="annotate",
                      default=False,
                      action="store_true",
                      help="added CEFR data for each of the words indicating the source"
    )


    parser.add_option('--bar',
                      dest="bar_plurals",
                      default=False,
                      action="store_true",
                      help="Process strings that have the form, singular|s - to indicate the plural form"
    )

    parser.add_option('--combined',
                      dest="combined",
                      default=False,
                      action="store_true",
                      help="process a combined frequency file"
    )

    parser.add_option("--dir", dest="dir_prefix",
                      default='./',
                      help="read configuration from FILE", metavar="FILE")

    parser.add_option('--slash',
                      dest="slash",
                      default=False,
                      action="store_true",
                      help="split words with a single slash in them"
    )

    parser.add_option('-P', '--PDF',
                      dest="processPDF_file",
                      default=False,
                      help="Processed the named PDF file rather than a Canvas course",
                      metavar="FILE"
    )



    options, remainder = parser.parse_args()

    Verbose_Flag=options.verbose
    if Verbose_Flag:
        print("ARGV      : {}".format(sys.argv[1:]))
        print("VERBOSE   : {}".format(options.verbose))
        print("REMAINING : {}".format(remainder))

    # compute the directory prefix for files to be used for the program's I/O
    # This does not apply to the CEFR spreadsheet files.
    directory_prefix=options.dir_prefix
    if not directory_prefix.endswith('/'):
        directory_prefix=directory_prefix+'/'
    if Verbose_Flag:
        print(f'{directory_prefix=}')

    if (len(remainder) < 1):
        print("Insuffient arguments\n must provide course_id or file_name\n")
    else:
        total_words_processed=0
        unique_words=set()
        number_of_unique_words_output=0
        filtered_unique_words_dict=dict()
        new_filtered_unique_words_dict=dict()
        skipped_words=set()
        all_text=list()
        likely_acronyms=set()

        if options.processPDF_file:
            course_id=remainder[0]
            print('Process a PDF file')
            
            if options.processPDF_file.startswith('./'):
                print('triming ./ when making new file name')
                f_name=options.processPDF_file[2:].replace('/', '_')
                course_id=f'{course_id}_{f_name}'         #  make a place holder course_id
            else:
                f_name=options.processPDF_file.replace('/', '_')
                course_id=f'{course_id}_{f_name}'         #  make a place holder course_id
        else:
            course_id=remainder[0]
            # if not str(course_id).isdigit():
            #     print("Error in course_id")
            #     return

        #### caution about the program
        print(f'{bold_text("Caution")}: This program considers words in isolation, whereas the actual CEFR levels may depend upon part of speech and context. See the source code for further information.')

        #################################################################################
        # load in the information about CEFR levels from the various sources
        #################################################################################
        print('Loading some directories')
        american_3000_file=directory_location+"American_Oxford_3000.xlsx"

        american_3000_words, american_3000_words_plurals, american_3000_df=read_cefr_data(american_3000_file, 'American3000')

        american_5000_words, american_5000_words_plurals, american_5000_df=read_cefr_data(american_3000_file, 'American5000')

        cefrlex_file=directory_location+"cefrlex-reduced.xlsx"
        # ['SVALex_Korp', 'SweLLex_Korp', 'EFLLex_NLP4J'])
        words_EFLLex, plurals_EFLLex, df_EFLLex=read_CEFRLLex_data(cefrlex_file, 'EFLLex_NLP4J')
        words_SVALex, plurals_SVALex, df_SVALex=read_CEFRLLex_data(cefrlex_file, 'SVALex_Korp')

        words_FLELex, plurals_FLELex, df_FLELex=read_CEFRLLex_French_data(cefrlex_file, 'FLELex_CRF Tagger')

        
        kelly_swedish_file=directory_location+"Swedish-Kelly_M3_CEFR.xlsx"
        words_kelly_swedish, plurals_kelly_swedish, df_kelly_swedish=read_Kelly_data(kelly_swedish_file, 'Swedish_M3_CEFR')

        print(f'{len(common_english_and_swedish.common_English_words):>{Numeric_field_width}} words in common English words')

        print(f'{len(common_english_and_swedish.common_swedish_words):>{Numeric_field_width}} words in common Swedish words')

        print(f'{len(common_english_and_swedish.common_swedish_technical_words):>{Numeric_field_width}} words in common Swedish technical words')

        print(f'{len(common_english_and_swedish.common_danish_words):>{Numeric_field_width}} words in common Danish words')

        print(f'{len(common_english_and_swedish.common_finnish_words):>{Numeric_field_width}} words in common Finnish words')

        print(f'{len(common_english_and_swedish.common_french_words):>{Numeric_field_width}} words in common French words')

        print(f'{len(common_english_and_swedish.common_german_words):>{Numeric_field_width}} words in common German words')

        print(f'{len(common_english_and_swedish.common_icelandic_words):>{Numeric_field_width}} words in common Icelandic words')

        print(f'{len(common_english_and_swedish.common_italian_words):>{Numeric_field_width}} words in common Italian words')

        print(f'{len(common_english_and_swedish.common_latin_words):>{Numeric_field_width}} words in common Latin words')

        print(f'{len(common_english_and_swedish.common_norwegian_words):>{Numeric_field_width}} words in common Norwegian words')
        
        print(f'{len(common_english_and_swedish.common_portuguese_words):>{Numeric_field_width}} words in common Portuguese words')

        print(f'{len(common_english_and_swedish.common_spanish_words):>{Numeric_field_width}} words in common Spanish words')

        print(f'{len(common_english_and_swedish.names_of_persons):>{Numeric_field_width}} words in names_of_persons')
        print(f'{len(common_english_and_swedish.place_names):>{Numeric_field_width}} words in place_names')
        print(f'{len(common_english_and_swedish.company_and_product_names):>{Numeric_field_width}} words in company_and_product_names')
        print(f'{len(common_english_and_swedish.misc_words_to_ignore):>{Numeric_field_width}} words in misc_words_to_ignore')
        print(f'{len(common_english_and_swedish.miss_spelled_words):>{Numeric_field_width}} words in miss_spelled_words')

        print(f'{len(common_english_and_swedish.mathematical_words_to_ignore):>{Numeric_field_width}} words in mathematical_words_to_ignore')
        print(f'{len(common_english_and_swedish.programming_keywords):>{Numeric_field_width}} words in programming_keywords')
        print(f'{len(common_english_and_swedish.language_tags):>{Numeric_field_width}} words in language_tags')
        print(f'{len(diva_merged_words.merged_words):>{Numeric_field_width}} words in merged_words')

        squished_merged_words=dict()
        # netries are indexed by the squished word and the value is the unsquished word(s)
        for w in diva_merged_words.merged_words:
            wx=w.replace(' ', '')
            squished_merged_words[wx]=w

        # entries in the dict will have the form: 'acronym': ['expanded form 1', 'expanded form 2',  ... ]
        well_known_acronyms=dict()
        for e in common_english_and_swedish.well_known_acronyms_list:
            if len(e) >= 1:
                ack=e[0]
                if len(e) >= 2:
                    d=e[1]
                    current_entry=well_known_acronyms.get(ack, list())
                    current_entry.append(d)
                    well_known_acronyms[ack]=current_entry
        print(f'{(len(well_known_acronyms)):>{Numeric_field_width}} unique acronyms in ({len(common_english_and_swedish.well_known_acronyms_list)}) well_known_acronyms')



        ###############################################################################
        # compute the lowest CEFR levels for each of the words, when there are CEFR levels specified
        ###############################################################################
        level_3000_singular=collect_CEFR_levels_from_list(american_3000_words, 'American 3000 singlular')
        level_5000_singular=collect_CEFR_levels_from_list(american_5000_words, 'American 5000 singlular')

        level_3000_plural=collect_CEFR_levels_for_plurals_from_list(american_3000_words, 'American 3000 plurals')
        level_5000_plural=collect_CEFR_levels_for_plurals_from_list(american_5000_words, 'American 5000 plurals')

        # compute the lowest CEFR level for each word in words_EFLLex
        level_words_EFLLex=compute_lowest_CEFR_level(words_EFLLex, 'EFLLex')
        # compute the lowest CEFR level for each word in words_SVALex
        level_words_SVALex=compute_lowest_CEFR_level(words_SVALex, 'SVALex')
        # compute the lowest CEFR level for each word in words_FLELex
        level_words_FLELex=compute_lowest_CEFR_level(words_FLELex, 'FLELex')

        level_common_English=collect_CEFR_levels_from_dict(common_english_and_swedish.common_English_words, 'common_English_words')
        level_top_100_English_words=collect_CEFR_levels_from_dict(common_english_and_swedish.top_100_English_words, 'top_100_English_words')
        level_thousand_most_common_words_in_English=collect_CEFR_levels_from_dict_common(common_english_and_swedish.thousand_most_common_words_in_English, 'thousand_most_common_words_in_English')

        level_common_swedish_words=collect_CEFR_levels_from_dict(common_english_and_swedish.common_swedish_words, 'common_swedish_words')
        level_common_swedish_technical_words=collect_CEFR_levels_from_dict(common_english_and_swedish.common_swedish_technical_words, 'common_swedish_technical_words')

        level_KTH_ordbok_English_with_CEFR=collect_CEFR_levels_from_dict(common_english_and_swedish.KTH_ordbok_English_with_CEFR, 'KTH_ordbok_English_with_CEFR')
        level_KTH_ordbok_Swedish_with_CEFR=collect_CEFR_levels_from_dict(common_english_and_swedish.KTH_ordbok_Swedish_with_CEFR, 'KTH_ordbok_Swedish_with_CEFR')
        if Verbose_Flag:
            print(f'{level_KTH_ordbok_English_with_CEFR=}')
            print(f'{level_KTH_ordbok_Swedish_with_CEFR=}')

        #################################################################################
        # process the input unique words from the JSON file
        #################################################################################
        print('\nPruning the input')
        # read in the frequecy data that was written as JSON
        if options.combined:
            input_file_name=f'{directory_prefix}combined_frequency-{course_id}.json'
        else:
            input_file_name=f'{directory_prefix}unique_words-for-course-frequency-{course_id}.txt'        
        try:
            if Verbose_Flag:
                print(f'Trying to read: {input_file_name}')
            with open(input_file_name, 'r') as f:
                unique_words=json.load(f)
        except:
            print(f'Unable to open file named {input_file_name}')
            return

        if not len(unique_words) > 0:
            print('Nothing to process')
            return

        print(f'{len(unique_words):>{Numeric_field_width}} unique words - before starting ')
        # get reid of any zero wdith spaces
        zero_width_space='\u200B'
        if zero_width_space in unique_words:
            del unique_words[zero_width_space]
        # similarly get rid of any zero length srings
        for word in unique_words:
            if len(word) < 1:
                del unique_words[word]

        updated_unique_words=copy.deepcopy(unique_words)
        count_of_squished_words=0
        for word in unique_words:
            if word in squished_merged_words:
                count_of_squished_words=count_of_squished_words+1
                wrds=squished_merged_words[word].split(' ')
                if len(wrds) > 1:
                    for w in wrds:
                        # update the word frequencies - after splitting the merged words
                        updated_unique_words[w]=updated_unique_words.get(w, 0)+1
                    del updated_unique_words[word] # remove the squished word

        if  len(updated_unique_words) - len(unique_words) < 0:
            print(f'{len(updated_unique_words) - len(unique_words):>{Numeric_field_width}} fewer unique words - after exapanding merged words ')
        elif len(updated_unique_words) - len(unique_words) > 0:
            print(f'{len(updated_unique_words) - len(unique_words):>{Numeric_field_width}} more unique words - after exapanding merged words ')
        else:
            print('no change in number of words after processing merged words')


        unique_words=updated_unique_words
        print(f'{len(unique_words):>{Numeric_field_width}} unique words - to start ')

        filtered_unique_words_dict=dict()
        for word in unique_words:
            pword=remove_lbracket_number_rbracket(word)  # removed citations of the form [ddd]
            pword=prune_prefix(pword)
            pword=prune_suffix(pword)
            if len(pword) > 0:
                filtered_unique_words_dict[pword]=unique_words[word] + unique_words.get(pword, 0)

        unique_words = filtered_unique_words_dict

        # make a deep copy of the dict, so that any operations do not affect the original set of unique_words
        filtered_unique_words_dict=copy.deepcopy(unique_words)

        if options.bar_plurals:
            filtered_unique_words_dict, reduction = expand_bar_plurals(filtered_unique_words_dict)
            print(f'{len(filtered_unique_words_dict):>{Numeric_field_width}} words left, {reduction:>{Numeric_field_width}} words plurals with | were expanded')
            
        if options.slash:
            filtered_unique_words_dict, reduction = split_slashes(filtered_unique_words_dict)
            print(f'{len(filtered_unique_words_dict):>{Numeric_field_width}} words left, {reduction:>{Numeric_field_width}} words with / were expanded')

        

        filtered_unique_words_dict, reduction = filter_words_by_list_case_sensitive(filtered_unique_words_dict, common_english_and_swedish.miss_spelled_words)
        print(f'{len(filtered_unique_words_dict):>{Numeric_field_width}} words left, {reduction:>{Numeric_field_width}} known misspelled words removed')


        filtered_unique_words_dict, reduction = filter_words_by_list_case_sensitive(filtered_unique_words_dict, common_english_and_swedish.place_names)
        print(f'{len(filtered_unique_words_dict):>{Numeric_field_width}} words left, {reduction:>{Numeric_field_width}} place names removed')

        filtered_unique_words_dict, reduction = filter_words_by_list_case_sensitive(filtered_unique_words_dict, common_english_and_swedish.company_and_product_names)
        print(f'{len(filtered_unique_words_dict):>{Numeric_field_width}} words left, {reduction:>{Numeric_field_width}} company_and_product_names removed')

        filtered_unique_words_dict, reduction = filter_words_by_list_case_sensitive(filtered_unique_words_dict, common_english_and_swedish.names_of_persons)
        print(f'{len(filtered_unique_words_dict):>{Numeric_field_width}} words left, {reduction:>{Numeric_field_width}} names_of_persons removed')

        filtered_unique_words_dict, reduction = filter_words_by_list_case_sensitive(filtered_unique_words_dict, common_english_and_swedish.common_programming_languages)
        print(f'{len(filtered_unique_words_dict):>{Numeric_field_width}} words left, {reduction:>{Numeric_field_width}} common_programming_languages removed')

        filtered_unique_words_dict, reduction = filter_words_by_list(filtered_unique_words_dict, common_english_and_swedish.mathematical_words_to_ignore)
        print(f'{len(filtered_unique_words_dict):>{Numeric_field_width}} words left, {reduction:>{Numeric_field_width}} mathematical_words_to_ignore removed')

        filtered_unique_words_dict, reduction = filter_words_by_list_case_sensitive(filtered_unique_words_dict, common_english_and_swedish.programming_keywords)
        print(f'{len(filtered_unique_words_dict):>{Numeric_field_width}} words left, {reduction:>{Numeric_field_width}} programming_keywords removed')

        filtered_unique_words_dict, reduction = filter_words_by_list(filtered_unique_words_dict, common_english_and_swedish.language_tags)
        print(f'{len(filtered_unique_words_dict):>{Numeric_field_width}} words left, {reduction:>{Numeric_field_width}} language_tags removed')


        filtered_unique_words_dict, reduction = filter_words_by_list(filtered_unique_words_dict, common_english_and_swedish.misc_words_to_ignore)
        print(f'{len(filtered_unique_words_dict):>{Numeric_field_width}} words left, {reduction:>{Numeric_field_width}} misc_words_to_ignore removed')

        filtered_unique_words_dict, reduction = filter_words_by_list(filtered_unique_words_dict, common_english_and_swedish.miss_spelled_words)
        print(f'{len(filtered_unique_words_dict):>{Numeric_field_width}} words left, {reduction:>{Numeric_field_width}} miss spelled words removed')


        filtered_unique_words_dict, reduction = filter_words_by_list_ending_in_period(filtered_unique_words_dict, common_english_and_swedish.abbreviations_ending_in_period)
        print(f'{len(filtered_unique_words_dict):>{Numeric_field_width}} words left, {reduction:>{Numeric_field_width}} abbreviations_ending_in_period removed')

        filtered_unique_words_dict, reduction = filter_words_by_function(filtered_unique_words_dict, is_MiscSymbol_or_Pictograph)
        print(f'{len(filtered_unique_words_dict):>{Numeric_field_width}} words left, {reduction:>{Numeric_field_width}} MiscSymbol_or_Pictograph removed')

        filtered_unique_words_dict, reduction = filter_words_by_function(filtered_unique_words_dict, is_number)
        print(f'{len(filtered_unique_words_dict):>{Numeric_field_width}} words left, {reduction:>{Numeric_field_width}} numbers removed')


        filtered_unique_words_dict, reduction = filter_words_by_function(filtered_unique_words_dict, is_filename_to_skip)
        print(f'{len(filtered_unique_words_dict):>{Numeric_field_width}} words left, {reduction:>{Numeric_field_width}} filenames removed')

        filtered_unique_words_dict, reduction = filter_words_by_function(filtered_unique_words_dict, is_fraction)
        print(f'{len(filtered_unique_words_dict):>{Numeric_field_width}} words left, {reduction:>{Numeric_field_width}} fractions removed')

        filtered_unique_words_dict, reduction = filter_words_by_function(filtered_unique_words_dict, is_integer_range_or_ISSN)
        print(f'{len(filtered_unique_words_dict):>{Numeric_field_width}} words left, {reduction:>{Numeric_field_width}} range or ISSN removed')

        filtered_unique_words_dict, reduction = filter_words_by_function(filtered_unique_words_dict, is_YYYY_MM_DD)
        print(f'{len(filtered_unique_words_dict):>{Numeric_field_width}} words left, {reduction:>{Numeric_field_width}} YYYY_MM_DD strings removed')

        filtered_unique_words_dict, reduction = filter_words_by_function(filtered_unique_words_dict, is_equation)
        print(f'{len(filtered_unique_words_dict):>{Numeric_field_width}} words left, {reduction:>{Numeric_field_width}} equations (i.e., includes math & technical symbols and Greek letters) removed')

        filtered_unique_words_dict, reduction = filter_words_by_function(filtered_unique_words_dict, is_domainname)
        print(f'{len(filtered_unique_words_dict):>{Numeric_field_width}} words left, {reduction:>{Numeric_field_width}} domainnames removed')

        filtered_unique_words_dict, reduction = filter_words_by_list(filtered_unique_words_dict, common_english_and_swedish.KTH_ordbok_Swedish_with_CEFR)
        print(f'{len(filtered_unique_words_dict):>{Numeric_field_width}} words left, {reduction:>{Numeric_field_width}} KTH_ordbok Swedish words removed')

        filtered_unique_words_dict, reduction = filter_words_by_list(filtered_unique_words_dict, common_english_and_swedish.KTH_ordbok_English_with_CEFR)
        print(f'{len(filtered_unique_words_dict):>{Numeric_field_width}} words left, {reduction:>{Numeric_field_width}} KTH_ordbok English removed')

        filtered_unique_words_dict, reduction = filter_words_by_function(filtered_unique_words_dict, is_improbable_word)
        print(f'{len(filtered_unique_words_dict):>{Numeric_field_width}} words left, {reduction:>{Numeric_field_width}} improbable words removed')

        filtered_unique_words_dict, reduction = filter_words_by_list(filtered_unique_words_dict, well_known_acronyms)
        print(f'{len(filtered_unique_words_dict):>{Numeric_field_width}} words left, {reduction:>{Numeric_field_width}} acronyms removed')

        # look for acronyms
        # reset the new dict
        new_filtered_unique_words_dict=dict()

        single_letter_count=0

        for word in filtered_unique_words_dict:
            # skip single letters
            if len(word) == 1:
                single_letter_count=single_letter_count+1
                if Verbose_Flag:
                    print(f'removing letter {word}')
                continue

            # look for acronyms that end with a "s"
            if len(word) > 2 and word.endswith('s'):
                trimmed_word=word[:-1]
            else:
                trimmed_word=word

            if trimmed_word.isupper() and trimmed_word.count('.') == 0 and trimmed_word.count('/') == 0\
               and trimmed_word.count('=') == 0 and\
               trimmed_word.count('→') == 0 and trimmed_word.count(':') == 0:
                likely_acronyms.add(trimmed_word)
            elif is_multiple_caps(trimmed_word):
                likely_acronyms.add(trimmed_word)
            elif trimmed_word.count('/') == 1:
                trimmed_word_split=trimmed_word.split("/")
                if len(trimmed_word_split) == 2 and is_multiple_caps(trimmed_word_split[0]) and is_multiple_caps(trimmed_word_split[1]):
                    likely_acronyms.add(trimmed_word)
                else:
                    new_filtered_unique_words_dict[word]=filtered_unique_words_dict[word]
            else:
                new_filtered_unique_words_dict[word]=filtered_unique_words_dict[word]

        #print(f'\t{single_letter_count} single letters removed')
        print(f'\t{len(likely_acronyms)} likely acronyms')
        print(f'{len(new_filtered_unique_words_dict):>{Numeric_field_width}} unique words after filtering acronyms and single letters')

        filtered_unique_words_dict=new_filtered_unique_words_dict

        # reset the new dict
        new_filtered_unique_words_dict=dict()

        for word in filtered_unique_words_dict:
            if word.istitle() and filtered_unique_words_dict.get(word.lower(), False):
                # if word is title case and there is a lower case version, then turn it into on a lower casse version
                number_of_instances=unique_words.get(word, 0)+unique_words.get(word.lower(), 0)
                new_filtered_unique_words_dict[word.lower()]=number_of_instances
            else:
                # otherwise preserve case
                if Verbose_Flag:
                    print(f'case 3: {word=}')
                new_filtered_unique_words_dict[word]=filtered_unique_words_dict[word]

        print(f'{len(new_filtered_unique_words_dict):>{Numeric_field_width}} unique words after filtering if there is a title case and lower case version of the word  turn to lower case')

        filtered_unique_words_dict=new_filtered_unique_words_dict
        # reset the new dict
        new_filtered_unique_words_dict=dict()

        filtered_unique_words_dict, reduction = filter_words_by_list(filtered_unique_words_dict, common_english_and_swedish.top_100_English_words)
        print(f'{len(filtered_unique_words_dict):>{Numeric_field_width}} words left, {reduction:>{Numeric_field_width}} top_100_English_words removed')

        filtered_unique_words_dict, reduction = filter_words_by_list(filtered_unique_words_dict, common_english_and_swedish.thousand_most_common_words_in_English)
        print(f'{len(filtered_unique_words_dict):>{Numeric_field_width}} words left, {reduction:>{Numeric_field_width}} thousand_most_common_words_in_English removed')

        # filter with tbe american 3000 and 5000 lists
        # reset the new dict
        new_filtered_unique_words_dict=dict()

        for word in filtered_unique_words_dict:
            if not in_dictionary(word, american_3000_words) and not (word in american_3000_words_plurals):
                new_filtered_unique_words_dict[word]=filtered_unique_words_dict[word]

        print(f'{len(new_filtered_unique_words_dict):>{Numeric_field_width}} words left, {len(filtered_unique_words_dict) - len(new_filtered_unique_words_dict):>{Numeric_field_width}} Oxford American 3000 words removed')


        filtered_unique_words_dict=new_filtered_unique_words_dict
        # reset the new dict
        new_filtered_unique_words_dict=dict()

        for word in filtered_unique_words_dict:
            if not in_dictionary(word, american_5000_words) and not (word in american_5000_words_plurals):
                new_filtered_unique_words_dict[word]=filtered_unique_words_dict[word]

        print(f'{len(new_filtered_unique_words_dict):>{Numeric_field_width}} words left, {len(filtered_unique_words_dict) - len(new_filtered_unique_words_dict):>{Numeric_field_width}} Oxford American 5000 words removed')

        filtered_unique_words_dict=new_filtered_unique_words_dict
        # reset the new dict
        new_filtered_unique_words_dict=dict()

        for word in filtered_unique_words_dict:
            if not in_dictionary(word.lower(), words_EFLLex): # all the words in EFLLex are in lower case
                new_filtered_unique_words_dict[word]=filtered_unique_words_dict[word]

        print(f'{len(new_filtered_unique_words_dict):>{Numeric_field_width}} words left, {len(filtered_unique_words_dict) - len(new_filtered_unique_words_dict):>{Numeric_field_width}} EFLLex_NLP4J words removed')

        filtered_unique_words_dict=new_filtered_unique_words_dict
        # reset the new dict
        new_filtered_unique_words_dict=dict()

        for word in filtered_unique_words_dict:
            if not in_dictionary(word.lower(), words_SVALex): # all the words in EFLLex are in lower case
                new_filtered_unique_words_dict[word]=filtered_unique_words_dict[word]

        print(f'{len(new_filtered_unique_words_dict):>{Numeric_field_width}} words left, {len(filtered_unique_words_dict) - len(new_filtered_unique_words_dict):>{Numeric_field_width}} SVALex_Korp words removed')

        filtered_unique_words_dict=new_filtered_unique_words_dict
        # reset the new dict
        new_filtered_unique_words_dict=dict()

        for word in filtered_unique_words_dict:
            if not in_dictionary(word.lower(), words_FLELex): # all the words in EFLLex are in lower case
                new_filtered_unique_words_dict[word]=filtered_unique_words_dict[word]

        print(f'{len(new_filtered_unique_words_dict):>{Numeric_field_width}} words left, {len(filtered_unique_words_dict) - len(new_filtered_unique_words_dict):>{Numeric_field_width}} FLELex_CRF Tagger words removed')


        filtered_unique_words_dict=new_filtered_unique_words_dict
        # reset the new dict
        new_filtered_unique_words_dict=dict()

        for word in filtered_unique_words_dict:
            if word in common_english_and_swedish.common_English_words:
                continue
            elif word.lower() in common_english_and_swedish.common_English_words:
                continue
            else:
                new_filtered_unique_words_dict[word]=filtered_unique_words_dict[word]

        print(f'{len(new_filtered_unique_words_dict):>{Numeric_field_width}} words left, {len(filtered_unique_words_dict) - len(new_filtered_unique_words_dict):>{Numeric_field_width}} common English words removed')

        filtered_unique_words_dict=new_filtered_unique_words_dict

        filtered_unique_words_dict, reduction = filter_words_by_list(filtered_unique_words_dict, common_english_and_swedish.common_swedish_words)
        print(f'{len(filtered_unique_words_dict):>{Numeric_field_width}} words left, {reduction:>{Numeric_field_width}} common Swedish words removed')

        filtered_unique_words_dict, reduction = filter_words_by_list(filtered_unique_words_dict, common_english_and_swedish.common_swedish_technical_words)
        print(f'{len(filtered_unique_words_dict):>{Numeric_field_width}} words left, {reduction:>{Numeric_field_width}} common Swedish technical words removed')


        filtered_unique_words_dict, reduction = filter_words_by_list(filtered_unique_words_dict, common_english_and_swedish.common_french_words)
        print(f'{len(filtered_unique_words_dict):>{Numeric_field_width}} words left, {reduction:>{Numeric_field_width}} common French words removed')

        filtered_unique_words_dict, reduction = filter_words_by_list(filtered_unique_words_dict, common_english_and_swedish.common_latin_words)
        print(f'{len(filtered_unique_words_dict):>{Numeric_field_width}} words left, {reduction:>{Numeric_field_width}} common Latin words removed')

        filtered_unique_words_dict, reduction = filter_words_by_list(filtered_unique_words_dict, common_english_and_swedish.common_german_words)
        print(f'{len(filtered_unique_words_dict):>{Numeric_field_width}} words left, {reduction:>{Numeric_field_width}} common German words removed')

        filtered_unique_words_dict, reduction = filter_words_by_list(filtered_unique_words_dict, common_english_and_swedish.common_finnish_words)
        print(f'{len(filtered_unique_words_dict):>{Numeric_field_width}} words left, {reduction:>{Numeric_field_width}} common Finnish words removed')

        filtered_unique_words_dict, reduction = filter_words_by_list(filtered_unique_words_dict, common_english_and_swedish.common_icelandic_words)
        print(f'{len(filtered_unique_words_dict):>{Numeric_field_width}} words left, {reduction:>{Numeric_field_width}} common Icelandic words removed')

        filtered_unique_words_dict, reduction = filter_words_by_list(filtered_unique_words_dict, common_english_and_swedish.common_italian_words)
        print(f'{len(filtered_unique_words_dict):>{Numeric_field_width}} words left, {reduction:>{Numeric_field_width}} common Italian words removed')

        filtered_unique_words_dict, reduction = filter_words_by_list(filtered_unique_words_dict, common_english_and_swedish.common_danish_words)
        print(f'{len(filtered_unique_words_dict):>{Numeric_field_width}} words left, {reduction:>{Numeric_field_width}} common Danish words removed')

        filtered_unique_words_dict, reduction = filter_words_by_list(filtered_unique_words_dict, common_english_and_swedish.common_norwegian_words)
        print(f'{len(filtered_unique_words_dict):>{Numeric_field_width}} words left, {reduction:>{Numeric_field_width}} common Norwegian words removed')

        filtered_unique_words_dict, reduction = filter_words_by_list(filtered_unique_words_dict, common_english_and_swedish.common_portuguese_words)
        print(f'{len(filtered_unique_words_dict):>{Numeric_field_width}} words left, {reduction:>{Numeric_field_width}} common Portugese words removed')

        filtered_unique_words_dict, reduction = filter_words_by_list(filtered_unique_words_dict, common_english_and_swedish.common_spanish_words)
        print(f'{len(filtered_unique_words_dict):>{Numeric_field_width}} words left, {reduction:>{Numeric_field_width}} common Spanish words removed')


        # reset the new dict
        new_filtered_unique_words_dict=dict()

        for word in filtered_unique_words_dict:

            working_word=word
            # if the word is lower case and it appears in lower case in the input, then leave in lower case
            if word.islower() and word in unique_words:
                new_filtered_unique_words_dict[word]=copy.deepcopy(unique_words[word])

            # if word only appears in title case in the original words, then put this version in
            elif word.title() in unique_words:
                if not word.lower() in unique_words:
                    if not word.title() in common_english_and_swedish.misc_words_to_ignore:
                        new_filtered_unique_words_dict[word.title()]=copy.deepcopy(unique_words[word.title()])
                        if Verbose_Flag:
                            print(f'case 1a: {word.title()} updated with {unique_words[word.title()]}')
                else:
                    if not word.title() in common_english_and_swedish.misc_words_to_ignore:
                        new_filtered_unique_words_dict[word.title()]=copy.deepcopy(unique_words[word.title()])
                    if not word.lower() in common_english_and_swedish.misc_words_to_ignore:
                        new_filtered_unique_words_dict[word.lower()]=copy.deepcopy(unique_words[word.lower()])
                    if Verbose_Flag:
                        print(f'case 2: {word}')
            else:
                if Verbose_Flag:
                    print(f'case 3: {word}')
                original_entry=unique_words.get(word, False)
                if original_entry:
                    new_filtered_unique_words_dict[word]=copy.deepcopy(original_entry)
                else:
                    new_filtered_unique_words_dict[word]=1 # assume one instance

        if len(new_filtered_unique_words_dict) > len(filtered_unique_words_dict):
            print(f'{len(new_filtered_unique_words_dict):>{Numeric_field_width}} words left, {len(new_filtered_unique_words_dict) - len(filtered_unique_words_dict):>{Numeric_field_width}} words added after processing words that appear in title case')
        else:
            print(f'{len(new_filtered_unique_words_dict)} words left, {len(filtered_unique_words_dict) - len(new_filtered_unique_words_dict) } words removed after processing words that appear in title case')

        set_difference=set(new_filtered_unique_words_dict).difference(set(filtered_unique_words_dict))
        if len(set_difference) > 0:
            print(f'added word(s): {set_difference}')

        filtered_unique_words_dict=new_filtered_unique_words_dict
        # reset the new dict
        new_filtered_unique_words_dict=dict()

        # in case any words have become zero length get rid of them now
        for word in filtered_unique_words_dict:
            if len(word) < 1:
                continue
            else:
                new_filtered_unique_words_dict[word]=filtered_unique_words_dict[word]

        filtered_unique_words_dict=new_filtered_unique_words_dict
        # reset the new dict
        new_filtered_unique_words_dict=dict()

        frequency_sorted=dict(sorted(filtered_unique_words_dict.items(), key=lambda x:x[1]))
      
        new_file_name=f'{directory_prefix}unique_words-for-course-frequency-updated-{course_id}.txt'        
        with open(new_file_name, 'w') as f:
            f.write(json.dumps(frequency_sorted, ensure_ascii=False))

        # compute some stats for the remiaing words
        number_leading_capital_letter=0
        number_leading_lower_case_letter=0
        number_leading_other=0

        for word in frequency_sorted:
            if word[0].isupper():
                number_leading_capital_letter=number_leading_capital_letter+1
            elif word[0].islower():
                number_leading_lower_case_letter=number_leading_lower_case_letter+1
            else:
                number_leading_other=number_leading_other+1

        if len(frequency_sorted) > 0:
            print(f'{number_leading_capital_letter:>{Numeric_field_width}} starting with a capital letter ({number_leading_capital_letter/len(frequency_sorted)*100:.2f}%)')
            print(f'{number_leading_lower_case_letter:>{Numeric_field_width}} starting with a lower case letter ({number_leading_lower_case_letter/len(frequency_sorted)*100:.2f}%)')
            print(f'{number_leading_other:>{Numeric_field_width}} starting with another type of letter ({number_leading_other/len(frequency_sorted)*100:.2f}%)')
        else:
            print('No remaining words')
        

        # compute difference between the words coming in and the remaining words
        for word in unique_words:
            if not word in filtered_unique_words_dict:
                skipped_words.add(word)

        # output likely acronyms
        new_file_name=f'{directory_prefix}unique_words-for-course-likely-acronyms-{course_id}.txt'        
        with open(new_file_name, 'w') as f:
            for word in sorted(likely_acronyms):
                f.write(f"{word}\n")

        new_file_name=f'{directory_prefix}unique_words-for-course-skipped-in-update-{course_id}.txt'        
        with open(new_file_name, 'w') as f:
            for word in skipped_words:
                f.write(f"{word}\n")

        # compute some simple stats about which courses and CEFR levels the unique words were in

        level_3000_singular_counts=dict()
        level_5000_singular_counts=dict()
        american_3000_words_singular_count=0
        american_3000_words_plurals_count=0
        american_3000_words_count=0

        level_3000_plural_counts=dict()
        level_5000_plural_counts=dict()
        american_5000_words_singular_count=0
        american_5000_words_plurals_count=0
        american_5000_words_count=0

        efllex_words_count=0
        level_words_EFLLex_counts={}

        svalex_words_count=0
        level_words_SVALex_counts={}


        flelex_words_count=0
        level_words_FLELex_counts={}

        level_common_English_counts=dict()
        common_English_words_count=0

        top_100_English_words_set=set()
        level_top_100_English_words_counts=dict()
        top_100_English_words_count=0

        level_thousand_most_common_words_in_English_counts=dict()
        thousand_most_common_words_in_English_count=0

        # note that the common_x_words (for x = swedish, french, and latin) do not have CEFR level information
        # hecne we do not have to calculate the lowest CEFR level for each word
        common_swedish_words_set=set()
        #common_swedish_technical_words_set=set()
        common_french_words_set=set()
        common_latin_words_set=set()
        common_german_words_set=set()
        common_finnish_words_set=set()
        common_italian_words_set=set()
        common_danish_words_set=set()

        level_common_swedish_words_counts=dict()
        common_swedish_words_count=0

        level_common_swedish_technical_words_counts=dict()
        common_swedish_technical_words_count=0

        level_KTH_ordbok_Swedish_with_CEFR_counts=dict()
        count_KTH_ordbok_Swedish_with_CEFR=0

        level_KTH_ordbok_English_with_CEFR_counts=dict()
        count_KTH_ordbok_English_with_CEFR=0

        #
        # Process all of the unique words and see which CEFR level they fall into for each of the sources
        #
        for word in unique_words:
            if in_dictionary(word, american_3000_words):
                american_3000_words_count=american_3000_words_count+1
            if in_dictionary(word, american_3000_words):
                american_3000_words_singular_count=american_3000_words_singular_count+1
                cefr_levels=level_3000_singular.get(word.lower(), False)
                if Verbose_Flag:
                    print(f'{word=} {cefr_levels=}')
                if cefr_levels:
                    if isinstance(cefr_levels, str):
                        if Verbose_Flag:
                            print(f'case 1 (3000): {word=} {cefr_levels=}')
                        level_3000_singular_counts.update({cefr_levels: level_3000_singular_counts.get(cefr_levels, 0) +1})
                    elif isinstance(cefr_levels, list) and len(cefr_levels) >= 1:
                        if Verbose_Flag:
                            print(f'case 2 (3000): {word=} {cefr_levels[0]=}')
                        level_3000_singular_counts.update({cefr_levels[0]: level_3000_singular_counts.get(cefr_levels[0], 0) +1})
                    else:
                        print(f'warning in computing level_3000_singular_counts: {word=} {cefr_levels=}')

            if word in american_3000_words_plurals:
                american_3000_words_plurals_count=american_3000_words_plurals_count+1
                cefr_levels=level_3000_plural.get(word.lower(), False)
                if cefr_levels:
                    if isinstance(cefr_levels, str):
                        if Verbose_Flag:
                            print(f'case 1 (3000 plural): {word=} {cefr_levels=}')
                        level_3000_plural_counts.update({cefr_levels: level_3000_plural_counts.get(cefr_levels, 0) +1})
                    elif isinstance(cefr_levels, list) and len(cefr_levels) >= 1:
                        if Verbose_Flag:
                            print(f'case 2 (3000 plural): {word=} {cefr_levels[0]=}')
                        level_3000_plural_counts.update({cefr_levels[0]: level_3000_singular_counts.get(cefr_levels[0], 0) +1})
                    else:
                        print(f'warning in computing level_3000_pluralsingular_counts: {word=} {cefr_levels=}')

            if in_dictionary(word, american_5000_words):
                american_5000_words_count=american_5000_words_count+1
            if in_dictionary(word, american_5000_words):
                american_5000_words_singular_count=american_5000_words_singular_count+1
                cefr_levels=level_5000_singular.get(word.lower(), False)
                if Verbose_Flag:
                    print(f'{word=} {cefr_levels=}')
                if cefr_levels:
                    if isinstance(cefr_levels, str):
                        if Verbose_Flag:
                            print(f'case 1 (5000): {word=} {cefr_levels=}')
                        level_5000_singular_counts.update({cefr_levels: level_5000_singular_counts.get(cefr_levels, 0) +1})
                    elif isinstance(cefr_levels, list) and len(cefr_levels) >= 1:
                        if Verbose_Flag:
                            print(f'case 2  (5000): {word=} {cefr_levels[0]=}')
                        level_5000_singular_counts.update({cefr_levels[0]: level_5000_singular_counts.get(cefr_levels[0], 0) +1})
                    else:
                        print(f'warning in computing level_5000_singular_counts: {word=} {cefr_levels=}')



            if word in american_5000_words_plurals:
                american_5000_words_plurals_count=american_5000_words_plurals_count+1
                cefr_levels=level_5000_plural.get(word.lower(), False)
                if cefr_levels:
                    if isinstance(cefr_levels, str):
                        if Verbose_Flag:
                            print(f'case 1 (5000 plural): {word=} {cefr_levels=}')
                        level_000_plural_counts.update({cefr_levels: level_5000_plural_counts.get(cefr_levels, 0) +1})
                    elif isinstance(cefr_levels, list) and len(cefr_levels) >= 1:
                        if Verbose_Flag:
                            print(f'case 2  (5000 plural): {word=} {cefr_levels[0]=}')
                        level_5000_plural_counts.update({cefr_levels[0]: level_5000_plural_counts.get(cefr_levels[0], 0) +1})
                    else:
                        print(f'warning in computing level_5000_plural_counts: {word=} {cefr_levels=}')


            if word.lower() in level_words_EFLLex:
                efllex_words_count, level_words_EFLLex_counts = increment_usage_count_and_CEFR_level_counts(efllex_words_count, level_words_EFLLex_counts, word.lower(), level_words_EFLLex,  'EFLLex')

            if word.lower() in level_words_SVALex:
                svalex_words_count, level_words_SVALex_counts = increment_usage_count_and_CEFR_level_counts(svalex_words_count, level_words_SVALex_counts, word.lower(), level_words_SVALex,  'SVALex')

            if word.lower() in level_words_FLELex:
                flelex_words_count, level_words_FLELex_counts = increment_usage_count_and_CEFR_level_counts(flelex_words_count, level_words_FLELex_counts, word.lower(), level_words_FLELex,  'FLELex')


            if word in common_english_and_swedish.common_English_words or word.lower() in common_english_and_swedish.common_English_words:
                common_English_words_count=common_English_words_count+1
                cefr_levels=level_common_English.get(word, False)
                if not cefr_levels:
                    cefr_levels=level_common_English.get(word.title(), False)
                if not cefr_levels:
                    cefr_levels=level_common_English.get(word.lower(), False)
                if not cefr_levels:
                    cefr_levels=level_common_English.get(word.upper(), False)

                if Verbose_Flag:
                    print(f'{word=} {cefr_levels=}')
                if cefr_levels:
                    if isinstance(cefr_levels, str):
                        level_common_English_counts.update({cefr_levels: level_common_English_counts.get(cefr_levels, 0) +1})
                    elif isinstance(cefr_levels, list) and len(cefr_levels) >= 1:
                        level_common_English_counts.update({cefr_levels[0]: level_common_English_counts.get(cefr_levels[0], 0) +1})
                    else:
                        print(f'warning in computing level_common_English_counts: {word=} {cefr_levels=}')


            # if word in common_swedish_words:
            #     common_swedish_words_set.add(word)
            # if word.lower() in common_swedish_words:
            #     common_swedish_words_set.add(word.lower())

            if word in common_english_and_swedish.common_swedish_words or word.lower() in common_english_and_swedish.common_swedish_words:
                common_swedish_words_count=common_swedish_words_count+1
                cefr_levels=level_common_swedish_words.get(word, False)
                if not cefr_levels:
                    cefr_levels=level_common_swedish_words.get(word.title(), False)
                if not cefr_levels:
                    cefr_levels=level_common_swedish_words.get(word.lower(), False)
                if not cefr_levels:
                    cefr_levels=level_common_swedish_words.get(word.upper(), False)

                if Verbose_Flag:
                    print(f'{word=} {cefr_levels=}')
                if cefr_levels:
                    if isinstance(cefr_levels, str):
                        level_common_swedish_words_counts.update({cefr_levels: level_common_swedish_words_counts.get(cefr_levels, 0) +1})
                    elif isinstance(cefr_levels, list) and len(cefr_levels) >= 1:
                        level_common_swedish_words_counts.update({cefr_levels[0]: level_common_swedish_words_counts.get(cefr_levels[0], 0) +1})
                    else:
                        print(f'warning in computing level_common_swedish_words_counts: {word=} {cefr_levels=}')


            # if word in common_english_and_swedish.common_swedish_technical_words:
            #     common_swedish_technical_words_set.add(word)
            # if word.lower() in common_swedish_technical_words:
            #     common_swedish_technical_words_set.add(word.lower())

            if word in common_english_and_swedish.common_swedish_technical_words or word.lower() in common_english_and_swedish.common_swedish_technical_words:
                common_swedish_technical_words_count=common_swedish_technical_words_count+1
                cefr_levels=level_common_swedish_technical_words.get(word, False)
                if not cefr_levels:
                    cefr_levels=level_common_swedish_technical_words.get(word.title(), False)
                if not cefr_levels:
                    cefr_levels=level_common_swedish_technical_words.get(word.lower(), False)
                if not cefr_levels:
                    cefr_levels=level_common_swedish_technical_words.get(word.upper(), False)

                if Verbose_Flag:
                    print(f'{word=} {cefr_levels=}')
                if cefr_levels:
                    if isinstance(cefr_levels, str):
                        level_common_swedish_technical_words_counts.update({cefr_levels: level_common_swedish_technical_words_counts.get(cefr_levels, 0) +1})
                    elif isinstance(cefr_levels, list) and len(cefr_levels) >= 1:
                        level_common_swedish_technical_words_counts.update({cefr_levels[0]: level_common_swedish_technical_words_counts.get(cefr_levels[0], 0) +1})
                    else:
                        print(f'warning in computing level_common_swedish_technical_words_counts: {word=} {cefr_levels=}')

            if word in common_english_and_swedish.KTH_ordbok_Swedish_with_CEFR or word.lower() in common_english_and_swedish.KTH_ordbok_Swedish_with_CEFR:
                count_KTH_ordbok_Swedish_with_CEFR=count_KTH_ordbok_Swedish_with_CEFR+1
                cefr_levels=level_KTH_ordbok_Swedish_with_CEFR.get(word, False)
                if not cefr_levels:
                    cefr_levels=level_KTH_ordbok_Swedish_with_CEFR.get(word.title(), False)
                if not cefr_levels:
                    cefr_levels=level_KTH_ordbok_Swedish_with_CEFR.get(word.lower(), False)
                if not cefr_levels:
                    cefr_levels=level_KTH_ordbok_Swedish_with_CEFR.get(word.upper(), False)

                if Verbose_Flag:
                    print(f'{word=} {cefr_levels=}')
                if cefr_levels:
                    if isinstance(cefr_levels, str):
                        level_KTH_ordbok_Swedish_with_CEFR_counts.update({cefr_levels: level_KTH_ordbok_Swedish_with_CEFR_counts.get(cefr_levels, 0) +1})
                    elif isinstance(cefr_levels, list) and len(cefr_levels) >= 1:
                        level_KTH_ordbok_Swedish_with_CEFR_counts.update({cefr_levels[0]: level_KTH_ordbok_Swedish_with_CEFR_counts.get(cefr_levels[0], 0) +1})
                    else:
                         print(f'warning in computing KTH_ordbok_Swedish_with_CEFR_count: {word=} {cefr_levels=}')

            if word in common_english_and_swedish.KTH_ordbok_English_with_CEFR or word.lower() in common_english_and_swedish.KTH_ordbok_English_with_CEFR:
                count_KTH_ordbok_English_with_CEFR=count_KTH_ordbok_English_with_CEFR+1
                cefr_levels=level_KTH_ordbok_English_with_CEFR.get(word, False)
                if not cefr_levels:
                    cefr_levels=level_KTH_ordbok_English_with_CEFR.get(word.title(), False)
                if not cefr_levels:
                    cefr_levels=level_KTH_ordbok_English_with_CEFR.get(word.lower(), False)
                if not cefr_levels:
                    cefr_levels=level_KTH_ordbok_English_with_CEFR.get(word.upper(), False)

                if Verbose_Flag:
                    print(f'{word=} {cefr_levels=}')
                if cefr_levels:
                    if isinstance(cefr_levels, str):
                        level_KTH_ordbok_English_with_CEFR_counts.update({cefr_levels: level_KTH_ordbok_English_with_CEFR_counts.get(cefr_levels, 0) +1})
                    elif isinstance(cefr_levels, list) and len(cefr_levels) >= 1:
                        level_KTH_ordbok_English_with_CEFR_counts.update({cefr_levels[0]: level_KTH_ordbok_English_with_CEFR_counts.get(cefr_levels[0], 0) +1})
                    else:
                         print(f'warning in computing KTH_ordbok_English_with_CEFR_count: {word=} {cefr_levels=}')


            if word in common_english_and_swedish.common_french_words:
                common_french_words_set.add(word)
            if  word.lower() in common_english_and_swedish.common_french_words:
                common_french_words_set.add(word.lower())

            if word in common_english_and_swedish.common_latin_words:
                common_latin_words_set.add(word)
            if word.lower() in common_english_and_swedish.common_latin_words:
                common_latin_words_set.add(word.lower())

            if word in common_english_and_swedish.common_german_words:
                common_german_words_set.add(word)
            if word.lower() in common_english_and_swedish.common_german_words:
                common_german_words_set.add(word.lower())

            if word in common_english_and_swedish.common_finnish_words:
                common_finnish_words_set.add(word)
            if word.lower() in common_english_and_swedish.common_finnish_words:
                common_finnish_words_set.add(word.lower())

            if word in common_english_and_swedish.common_italian_words:
                common_italian_words_set.add(word)
            if word.lower() in common_english_and_swedish.common_italian_words:
                common_italian_words_set.add(word.lower())

            if word in common_english_and_swedish.common_danish_words:
                common_danish_words_set.add(word)
            if word.lower() in common_english_and_swedish.common_danish_words:
                common_danish_words_set.add(word.lower())

            if word in common_english_and_swedish.top_100_English_words:
                top_100_English_words_set.add(word)

            if word.lower() in common_english_and_swedish.top_100_English_words:
                top_100_English_words_set.add(word.lower())
                
            # For count of words at each level we do not consider case; this might msilead of there are only words such as "US" or "i".
            if word.lower() in common_english_and_swedish.thousand_most_common_words_in_English:
                thousand_most_common_words_in_English_count, level_thousand_most_common_words_in_English_counts = increment_usage_count_and_CEFR_level_counts(thousand_most_common_words_in_English_count, level_thousand_most_common_words_in_English_counts, word.lower(), level_thousand_most_common_words_in_English,  'thousand_most_common_words_in_English')

        #
        # Output counts
        #

        # Create a data frame to put the satsiical data in
        col_names =  ['Input', 'Source', 'total', 'percentage', 'A1', 'A2', 'B1', 'B2', 'C1', 'C2', 'D1', 'D2', 'xx']
        stats_df  = pd.DataFrame(columns = col_names)


        print('\nSome statistics about the CEFR levels of the words as determined by the five main data sources')
        print('The totals are the total numbers of the input words that appear in this source.')
        print('The percentage shown following the totals indicates what portion of the words from this source were used in the course pages.')
        print('The American 3000 and 5000 sources have an explicit column of plurals; the rest are considered "singular".')
        print('EFLLex_NLP4J, SVALex_Korp, and FLELex_CRF Tagger do {bold_text("not")} have any C2 words. The level used for a word based on these sources is based on the most frequent level for this word. In contrast for the other sources, the level used is the lowest level for that word or the highest level when the word is hyphenated.')
        print('The level xx indicates that the word does not have a known CEFR level.\n')

        print(f'American 3000: total: {american_3000_words_count} ({(american_3000_words_count/len(american_3000_words))*100:.2f}%), singular: {american_3000_words_singular_count}, plural: {american_3000_words_plurals_count}')
        #print(f'\t{level_3000_singular_counts=}')
        usage_sorted=dict(sorted(level_3000_singular_counts.items(), key=lambda x:x[0]))
        print(f'singular: {usage_sorted}')
        usage_sorted['Input']=f'course_id {course_id}'
        usage_sorted['Source']='American 3000 singular'
        usage_sorted['total']=american_3000_words_singular_count
        usage_sorted['percentage']=(american_3000_words_singular_count/len(level_3000_singular))*100.0
        stats_df.loc[len(stats_df)] = usage_sorted

        #print(f'\t{level_3000_plural_counts=}')
        usage_sorted=dict(sorted(level_3000_plural_counts.items(), key=lambda x:x[0]))
        print(f'  plural: {usage_sorted}')
        usage_sorted['Input']=f'course_id {course_id}'
        usage_sorted['Source']='American 3000 plural'
        usage_sorted['total']=american_3000_words_plurals_count
        usage_sorted['percentage']=(american_3000_words_plurals_count/len(level_3000_plural))*100.0
        stats_df.loc[len(stats_df)] = usage_sorted

        usage_sorted=dict()
        usage_sorted['Input']=f'course_id {course_id}'
        usage_sorted['Source']='American 3000'
        usage_sorted['total']=american_3000_words_singular_count + american_3000_words_plurals_count
        usage_sorted['percentage']=((american_3000_words_singular_count + american_3000_words_plurals_count)/(len(level_3000_singular)+len(level_3000_plural)))*100.0
        stats_df.loc[len(stats_df)] = usage_sorted


        print(f'American 5000: total: {american_5000_words_count} ({(american_5000_words_count/len(american_5000_words))*100:.2f}%), singular: {american_5000_words_singular_count}, plural: {american_5000_words_plurals_count}')
        #print(f'\t{level_5000_singular_counts=}')
        usage_sorted=dict(sorted(level_5000_singular_counts.items(), key=lambda x:x[0]))
        print(f'singular:                                 {usage_sorted}')
        usage_sorted['Input']=f'course_id {course_id}'
        usage_sorted['Source']='American 5000 singular'
        usage_sorted['total']=american_5000_words_singular_count
        usage_sorted['percentage']=(american_5000_words_singular_count/len(level_5000_singular))*100.0
        stats_df.loc[len(stats_df)] = usage_sorted

        #print(f'\t{level_5000_plural_counts=}')
        usage_sorted=dict(sorted(level_5000_plural_counts.items(), key=lambda x:x[0]))
        print(f'  plural:                                 {usage_sorted}')
        usage_sorted['Input']=f'course_id {course_id}'
        usage_sorted['Source']='American 5000 plural'
        usage_sorted['total']=american_5000_words_plurals_count
        usage_sorted['percentage']=(american_5000_words_plurals_count/len(level_5000_plural))*100.0
        stats_df.loc[len(stats_df)] = usage_sorted

        usage_sorted=dict()
        usage_sorted['Input']=f'course_id {course_id}'
        usage_sorted['Source']='American 5000'
        usage_sorted['total']=american_5000_words_singular_count + american_5000_words_plurals_count
        usage_sorted['percentage']=((american_5000_words_singular_count + american_5000_words_plurals_count)/(len(level_5000_singular)+len(level_5000_plural)))*100.0
        stats_df.loc[len(stats_df)] = usage_sorted




        print(f'EFLLex_NLP4J (English): total: {efllex_words_count} ({(efllex_words_count/len(level_words_EFLLex))*100:.2f}%)')
        usage_sorted=dict(sorted(level_words_EFLLex_counts.items(), key=lambda x:x[0]))
        print(f'\t{usage_sorted}')
        usage_sorted['Input']=f'course_id {course_id}'
        usage_sorted['Source']='EFLLex_NLP4J (English)'
        usage_sorted['total']=efllex_words_count
        usage_sorted['percentage']=(efllex_words_count/len(level_words_EFLLex))*100.0
        stats_df.loc[len(stats_df)] = usage_sorted


        print(f'SVALex_Korp (Swedish): total: {svalex_words_count} ({(svalex_words_count/len(level_words_SVALex))*100:.2f}%)')
        usage_sorted=dict(sorted(level_words_SVALex_counts.items(), key=lambda x:x[0]))
        print(f'\t{usage_sorted}')
        usage_sorted['Input']=f'course_id {course_id}'
        usage_sorted['Source']='SVALex_Korp (Swedish)'
        usage_sorted['total']=svalex_words_count
        usage_sorted['percentage']=(svalex_words_count/len(level_words_SVALex))*100.0
        stats_df.loc[len(stats_df)] = usage_sorted


        print(f'FLELex_CRF Tagger (French): total: {flelex_words_count} ({(flelex_words_count/len(level_words_FLELex))*100:.2f}%)')
        usage_sorted=dict(sorted(level_words_FLELex_counts.items(), key=lambda x:x[0]))
        print(f'\t{usage_sorted}')
        usage_sorted['Input']=f'course_id {course_id}'
        usage_sorted['Source']='FLELex_CRF Tagger (French)'
        usage_sorted['total']=flelex_words_count
        usage_sorted['percentage']=(flelex_words_count/len(level_words_FLELex))*100.0
        stats_df.loc[len(stats_df)] = usage_sorted


        print(f'common English words: total: {common_English_words_count} ({(common_English_words_count/len(common_english_and_swedish.common_English_words))*100:.2f}%)')
        #print(f'{level_common_English_counts=}')
        usage_sorted=dict(sorted(level_common_English_counts.items(), key=lambda x:x[0]))
        print(f'\t{usage_sorted}')
        usage_sorted['Input']=f'course_id {course_id}'
        usage_sorted['Source']='common English words'
        usage_sorted['total']=common_English_words_count
        usage_sorted['percentage']=(common_English_words_count/len(common_english_and_swedish.common_English_words))*100.0
        stats_df.loc[len(stats_df)] = usage_sorted


        top_100_English_words_count=len(common_english_and_swedish.top_100_English_words)
        if Verbose_Flag:
            print(f'{len(top_100_English_words_set)=}')
        for word in top_100_English_words_set:
            top_100_English_words_count, level_top_100_English_words_counts = increment_usage_count_and_CEFR_level_counts(top_100_English_words_count, level_top_100_English_words_counts, word, level_top_100_English_words,  'top_100_English_words')


        print(f'top 100 English  words: total: {len(top_100_English_words_set)}  ({(len(top_100_English_words_set)/len(common_english_and_swedish.top_100_English_words))*100:.2f}%)')
        #usage_sorted=dict()
        usage_sorted=dict(sorted(level_top_100_English_words_counts.items(), key=lambda x:x[0]))
        print(f'\t{usage_sorted}')

        usage_sorted['Input']=f'course_id {course_id}'
        usage_sorted['Source']='top 100 English words'
        usage_sorted['total']=len(top_100_English_words_set)
        usage_sorted['percentage']=(len(top_100_English_words_set)/len(common_english_and_swedish.top_100_English_words))*100.0
        stats_df.loc[len(stats_df)] = usage_sorted

        unused_top_100_English_words=set(common_english_and_swedish.top_100_English_words).difference(top_100_English_words_set)
        if len(unused_top_100_English_words) > 0:
            print(f'top 100 words in English that were {bold_text("not")} used: {unused_top_100_English_words}')

        print(f'thousand most common words in_English: total: {thousand_most_common_words_in_English_count}  ({(thousand_most_common_words_in_English_count/len(common_english_and_swedish.thousand_most_common_words_in_English))*100:.2f}%)')
        usage_sorted=dict(sorted(level_thousand_most_common_words_in_English_counts.items(), key=lambda x:x[0]))
        print(f'\t{usage_sorted}')
        usage_sorted['Input']=f'course_id {course_id}'
        usage_sorted['Source']='thousand most common words in_English'
        usage_sorted['total']=thousand_most_common_words_in_English_count
        usage_sorted['percentage']=(thousand_most_common_words_in_English_count/len(common_english_and_swedish.thousand_most_common_words_in_English))*100
        stats_df.loc[len(stats_df)] = usage_sorted

        
        #common_swedish_words_count=len(common_swedish_words_set)
        print(f'common Swedish words: total: {common_swedish_words_count}  ({(common_swedish_words_count/len(common_english_and_swedish.common_swedish_words))*100:.2f}%)')
        usage_sorted=dict(sorted(level_common_swedish_words_counts.items(), key=lambda x:x[0]))
        print(f'\t{usage_sorted}')
        usage_sorted['Input']=f'course_id {course_id}'
        usage_sorted['Source']='common Swedish words'
        usage_sorted['total']=common_swedish_words_count
        usage_sorted['percentage']=(common_swedish_words_count/len(common_english_and_swedish.common_swedish_words))*100.0
        stats_df.loc[len(stats_df)] = usage_sorted


        #common_swedish_technical_words_count=len(common_english_and_swedish.common_swedish_technical_words_set)
        print(f'common Swedish technical words: total: {common_swedish_technical_words_count}  ({(common_swedish_technical_words_count/len(common_english_and_swedish.common_swedish_technical_words))*100:.2f}%)')
        usage_sorted=dict(sorted(level_common_swedish_technical_words_counts.items(), key=lambda x:x[0]))
        print(f'\t{usage_sorted}')
        usage_sorted['Input']=f'course_id {course_id}'
        usage_sorted['Source']='common Swedish technical words'
        usage_sorted['total']=common_swedish_technical_words_count
        usage_sorted['percentage']=(common_swedish_technical_words_count/len(common_english_and_swedish.common_swedish_technical_words))*100.0
        stats_df.loc[len(stats_df)] = usage_sorted

        print(f'KTH_ordbok_Swedish_with_CEFR: total: {count_KTH_ordbok_Swedish_with_CEFR}  ({(count_KTH_ordbok_Swedish_with_CEFR/len(common_english_and_swedish.KTH_ordbok_Swedish_with_CEFR))*100:.2f}%)')
        #print(f'{level_KTH_ordbok_Swedish_with_CEFR_counts=}')
        usage_sorted=dict(sorted(level_KTH_ordbok_Swedish_with_CEFR_counts.items(), key=lambda x:x[0]))
        print(f'\t{usage_sorted}')
        usage_sorted['Input']=f'course_id {course_id}'
        usage_sorted['Source']='KTH_ordbok_Swedish'
        usage_sorted['total']=count_KTH_ordbok_Swedish_with_CEFR
        usage_sorted['percentage']=(count_KTH_ordbok_Swedish_with_CEFR/len(common_english_and_swedish.KTH_ordbok_Swedish_with_CEFR))*100.0
        stats_df.loc[len(stats_df)] = usage_sorted

        print(f'KTH_ordbok_English_with_CEFR: total: {count_KTH_ordbok_English_with_CEFR}  ({(count_KTH_ordbok_English_with_CEFR/len(common_english_and_swedish.KTH_ordbok_English_with_CEFR))*100:.2f}%)')
        usage_sorted=dict(sorted(level_KTH_ordbok_English_with_CEFR_counts.items(), key=lambda x:x[0]))
        #print(f'{level_KTH_ordbok_English_with_CEFR_counts=}')
        print(f'\t{usage_sorted}')
        usage_sorted['Input']=f'course_id {course_id}'
        usage_sorted['Source']='KTH_ordbok_English'
        usage_sorted['total']=count_KTH_ordbok_English_with_CEFR
        usage_sorted['percentage']=(count_KTH_ordbok_English_with_CEFR/len(common_english_and_swedish.KTH_ordbok_English_with_CEFR))*100.0
        stats_df.loc[len(stats_df)] = usage_sorted

        common_french_words_count=len(common_french_words_set)
        print(f'common French words: total: {common_french_words_count}  ({(common_french_words_count/len(common_english_and_swedish.common_french_words))*100:.2f}%)')
        usage_sorted=dict()
        usage_sorted['Input']=f'course_id {course_id}'
        usage_sorted['Source']='common French words'
        usage_sorted['total']=common_french_words_count
        usage_sorted['percentage']=(common_french_words_count/len(common_english_and_swedish.common_french_words))*100.0
        stats_df.loc[len(stats_df)] = usage_sorted

        common_latin_words_count=len(common_latin_words_set)
        print(f'common Latin words: total: {common_latin_words_count}  ({(common_latin_words_count/len(common_english_and_swedish.common_latin_words))*100:.2f}%)')
        usage_sorted=dict()
        usage_sorted['Input']=f'course_id {course_id}'
        usage_sorted['Source']='common Latin words'
        usage_sorted['total']=common_latin_words_count
        usage_sorted['percentage']=(common_latin_words_count/len(common_english_and_swedish.common_latin_words))*100.0
        stats_df.loc[len(stats_df)] = usage_sorted

        common_german_words_count=len(common_german_words_set)
        print(f'common German words: total: {common_german_words_count}  ({(common_german_words_count/len(common_english_and_swedish.common_german_words))*100:.2f}%)')
        usage_sorted=dict()
        usage_sorted['Input']=f'course_id {course_id}'
        usage_sorted['Source']='common German words'
        usage_sorted['total']=common_german_words_count
        usage_sorted['percentage']=(common_german_words_count/len(common_english_and_swedish.common_german_words))*100.0
        stats_df.loc[len(stats_df)] = usage_sorted

        common_finnish_words_count=len(common_finnish_words_set)
        print(f'common Finnish words: total: {common_finnish_words_count}  ({(common_finnish_words_count/len(common_english_and_swedish.common_finnish_words))*100:.2f}%)')
        usage_sorted=dict()
        usage_sorted['Input']=f'course_id {course_id}'
        usage_sorted['Source']='common Finnish words'
        usage_sorted['total']=common_finnish_words_count
        usage_sorted['percentage']=(common_finnish_words_count/len(common_english_and_swedish.common_finnish_words))*100.0
        stats_df.loc[len(stats_df)] = usage_sorted

        common_italian_words_count=len(common_italian_words_set)
        print(f'common Italian words: total: {common_italian_words_count}  ({(common_italian_words_count/len(common_english_and_swedish.common_italian_words))*100:.2f}%)')
        usage_sorted=dict()
        usage_sorted['Input']=f'course_id {course_id}'
        usage_sorted['Source']='common Italian words'
        usage_sorted['total']=common_italian_words_count
        usage_sorted['percentage']=(common_italian_words_count/len(common_english_and_swedish.common_italian_words))*100.0
        stats_df.loc[len(stats_df)] = usage_sorted

        common_danish_words_count=len(common_danish_words_set)
        print(f'common Danish words: total: {common_danish_words_count}  ({(common_danish_words_count/len(common_english_and_swedish.common_danish_words))*100:.2f}%)')
        usage_sorted=dict()
        usage_sorted['Input']=f'course_id {course_id}'
        usage_sorted['Source']='common Danish words'
        usage_sorted['total']=common_danish_words_count
        usage_sorted['percentage']=(common_danish_words_count/len(common_english_and_swedish.common_danish_words))*100.0
        stats_df.loc[len(stats_df)] = usage_sorted

        # The following code compares the common_English_words with those in EFLLex. This was useful to find some of the
        # CEFR levels that were unknown. However, there were also 406 cases where the two had different CEFR levels.
        #
        # for word in level_common_English:
        #     # compare levels with EFLLex_NLP4J
        #     cefr_level=level_words_EFLLex.get(word.lower(), False)
        #     if cefr_level:
        #         cefs_level_common_English_words = level_common_English[word]
        #         if len(cefs_level_common_English_words) == 1:
        #             cefs_level_common_English_words=cefs_level_common_English_words[0]
        #             if cefr_level == cefs_level_common_English_words:
        #                 print(f'matching levels for {word}')
        #             else:
        #                 print(f'{word} {cefs_level_common_English_words} {cefr_level}')
        #         else:
        #             print(f'{word} {cefs_level_common_English_words} {cefr_level}')


        if Verbose_Flag:
            print(f'{american_5000_words=}')
            print(f'{american_5000_words_plurals=}')

        # set up the output write
        new_file_name=f'{directory_prefix}unique_words-for-course-likely-stats-{course_id}.xlsx'
        writer = pd.ExcelWriter(new_file_name, engine='xlsxwriter')
        stats_df.to_excel(writer, sheet_name='Stats')
        workbook = writer.book
        two_decimals_fmt_dict={'num_format': '0.00'}
        two_decimals_fmt = workbook.add_format(two_decimals_fmt_dict)

        bottom_thick_border_fmt_dict = {'bottom': 5, 'bold': True}
        bottom_thick_border_fmt = workbook.add_format(bottom_thick_border_fmt_dict)

        two_decimals_bottom_thick_border_fmt_dict = {'bottom': 5, 'bold': True, 'num_format': '0.00'}
        two_decimals_bottom_thick_border_fmt = workbook.add_format(two_decimals_bottom_thick_border_fmt_dict)

        worksheet = writer.sheets['Stats']
        worksheet.set_row(3, 20, bottom_thick_border_fmt)
        worksheet.set_row(6, 20, bottom_thick_border_fmt)
        worksheet.set_column('E:E', 20, two_decimals_fmt)
        worksheet.conditional_format('E4:E4', {'type': 'no_errors', 'format': two_decimals_bottom_thick_border_fmt})
        worksheet.conditional_format('E7:E7', {'type': 'no_errors', 'format': two_decimals_bottom_thick_border_fmt})
        worksheet.autofit()
        # Close the Pandas Excel writer and output the Excel file.
        writer.close()

        # compute which words in common_swedish_words need a CEFR level added
        words_missing_CEFR_levels=set()
        words_not_in_swedish_common_words=set()
        for word in unique_words:
            # ignore known misspellings
            if word in common_english_and_swedish.miss_spelled_words:
                continue
            if word in common_english_and_swedish.common_swedish_words:
                if common_english_and_swedish.common_swedish_words.get(word, False):
                    if not isinstance(common_english_and_swedish.common_swedish_words[word], dict):
                        print(f'check the entry in common_swedish_words for the word: {word}')
                        continue
                    for k in common_english_and_swedish.common_swedish_words[word].keys():
                        if k == 'xx':
                            words_missing_CEFR_levels.add(word)
            elif word.lower() in common_english_and_swedish.common_swedish_words:
                if common_english_and_swedish.common_swedish_words.get(word.lower(), False):
                    if not isinstance(common_english_and_swedish.common_swedish_words[word.lower()], dict):
                        print(f'check the entry in common_swedish_words for the word: {word}')
                        continue
                    for k in common_english_and_swedish.common_swedish_words[word.lower()].keys():
                        if k == 'xx':
                            words_missing_CEFR_levels.add(word.lower())
            else:
                if word.istitle():
                    words_not_in_swedish_common_words.add(word.lower())
                else:
                    words_not_in_swedish_common_words.add(word)
                
        missing_set_sorted=sorted(words_missing_CEFR_levels)
        if len(missing_set_sorted) > 0:
            print(f'{len(missing_set_sorted)} missing CEFR assignments')
            print(f'{missing_set_sorted=}')

        if options.annotate:
            sources={
                'common_English_words': level_common_English,
                'common_swedish_words': level_common_swedish_words, 
                'common_swedish_technical_words': level_common_swedish_technical_words,
                'SVALex': level_words_SVALex,
                'FLELex': level_words_FLELex,
                'EFLLex': level_words_EFLLex,
                'American 3000 singlular': level_3000_singular,
                'American 5000 singlular': level_5000_singular,

                'American 3000 plurals': level_3000_plural,
                'American 5000 plurals': level_5000_plural,
                'thousand_most_common_words_in_English': level_thousand_most_common_words_in_English,
                'top_100_English_words': level_top_100_English_words,
                'KTH_ordbok_Swedish': level_KTH_ordbok_Swedish_with_CEFR,
                'KTH_ordbok_English': level_KTH_ordbok_English_with_CEFR,
                }

            source_lists={
                'place': common_english_and_swedish.place_names,
                'company or product': common_english_and_swedish.company_and_product_names,
                'person_name': common_english_and_swedish.names_of_persons,
                'programming language or tool': common_english_and_swedish.common_programming_languages,
                'mathematical_word': common_english_and_swedish.mathematical_words_to_ignore,
                'misc': common_english_and_swedish.misc_words_to_ignore,
                'abbreviations_ending_in_period': abbreviations_ending_in_period,
                'misspelled': common_english_and_swedish.miss_spelled_words,
                'programming_keywords': common_english_and_swedish.programming_keywords,
                'language_tags': common_english_and_swedish.language_tags,
                'French': common_english_and_swedish.common_french_words,
            }

            case_insensitive_source_lists={
                'Latin': common_english_and_swedish.common_latin_words,
                'German': common_english_and_swedish.common_german_words,
                'Finnish': common_english_and_swedish.common_finnish_words,
                'Italian': common_english_and_swedish.common_italian_words,
                'Danish': common_english_and_swedish.common_danish_words,
            }
            source_filters={
                'number': is_number,
                'equation': is_equation,
                'domainname': is_domainname,
                'improbable word':  is_improbable_word,
                'MiscSymbol_or_Pictograph': is_MiscSymbol_or_Pictograph,
                'filename': is_filename_to_skip,
            }
            annotated_dict=dict()
            for word in unique_words:
                entry={'frequency': unique_words.get(word, 0)}
                for source in sources:
                    entry=conditionally_get_level(word, source, sources[source], entry)
                for source in case_insensitive_source_lists:
                    entry=conditionally_check_list_case_insensitive(word, source, case_insensitive_source_lists[source], entry)
                for source in source_lists:
                    entry=conditionally_check_list(word, source, source_lists[source], entry)
                for source in source_filters:
                    entry=conditionally_check_with_function(word, source, source_filters[source], entry)
                annotated_dict[word]=entry

            #print(f'{annotated_dict.items()}')
            frequency_sorted=dict(sorted(annotated_dict.items(), key=lambda x:x[1].get('frequency')))
      
            new_file_name=f'{directory_prefix}unique_words-for-course-frequency-annotated-{course_id}.txt'        
            with open(new_file_name, 'w') as f:
                f.write(json.dumps(frequency_sorted, ensure_ascii=False))


        if not options.testing:
            return

        print('Some experimnts to looking a the words that are not in swedish_common_words-for the content being processed.')
        words_Kelly_set=set()
        for w in words_kelly_swedish:
            words_Kelly_set.add(w)

        d1=words_not_in_swedish_common_words.difference(common_english_and_swedish.common_swedish_technical_words)
        print(f'{len(d1)=}')
        #print(f'{d1=}')

        d2=d1.difference(words_Kelly_set)
        print(f'{len(d2)=}')
        #print(f'{d2=}')

        d3=d2.difference(common_english_and_swedish.common_English_words)
        print(f'{len(d3)=}')
        print(f'{d3=}')

        # compare sets
        print('--------------------------------------------------------------------------------')
        print(f'The following is some analysis of the Swedish lexicons and do {bold_text("not")} concern the specific content described above.')
        print('\nSome comparison between the words I have collected and their levels and the words and values in SVALex.')
        print('\nComparison of the technical words')
        common_swedish_technical_words_set=set()
        for w in common_english_and_swedish.common_swedish_technical_words:
            common_swedish_technical_words_set.add(w)
        
        words_SVALex_set=set()
        for w in level_words_SVALex:
            words_SVALex_set.add(w)

        set_difference=common_swedish_technical_words_set.difference(words_SVALex_set)
        # print(f'{set_difference=}')

        d2=common_swedish_technical_words_set.difference(set_difference)
        # print(f'{d2=}')

        # compute words that are in common_swedish_technical_words that are in SVALex
        d3=d2.difference(set_difference)
        if len(d3) > 0:
            print('The words that appear in both common_swedish_technical_words and SVALex:')
            print(f'\t{d3}')

        if Verbose_Flag:
            for w in d3:
                print(f"\nlevels for '{w}' common_english_and_swedish.common_swedish_technical_words: {common_english_and_swedish.common_swedish_technical_words[w]} SVALex: {level_words_SVALex[w]=}")

        print('\nComparison of the non-technical words:')
        common_swedish_words_set=set()
        for w in common_english_and_swedish.common_swedish_words:
            common_swedish_words_set.add(w)

        set_difference=common_swedish_words_set.difference(words_SVALex_set)
        # print(f'{set_difference=}')

        d2=common_swedish_words_set.difference(set_difference)
        # print(f'{d2=}')

        # compute words that are in common_swedish_words that are in SVALex
        d3=d2.difference(set_difference)
        if len(d3) > 0:
            print(f'{len(d3)} words appear in both common_swedish_words and SVALex.')
            if Verbose_Flag:
                print(f'These words are: {d3}')

        # Of the words in both, check for words in common_swedish_words that have a level of 'xx'
        missing_set=set()
        for w in d3:
            for k in common_english_and_swedish.common_swedish_words[w].keys():
                if k == 'xx':
                    missing_set.add(w)
        if len(missing_set) > 0:
            print(f'Missing CEFR level for words from common_swedish_words - that appear in SVALex: {missing_set}')

        histo_level_differences=dict()

        for w in d3:
            for k in common_english_and_swedish.common_swedish_words[w].keys():
                level_diff=compare_cefr_levels(k, level_words_SVALex[w])
                current_count=histo_level_differences.get(level_diff, 0)
                histo_level_differences[level_diff]=current_count+1
                if Verbose_Flag:
                    if level_diff > 2 or level_diff < -2:
                        print(f"level difference {level_diff } for '{w}' {k=} common_english_and_swedish.common_swedish_words: {common_english_and_swedish.common_swedish_words[w]} SVALex: {level_words_SVALex[w]=}")
        histo_sorted=dict(sorted(histo_level_differences.items(), key=lambda x:x[0]))
        print('The histogram of differences between levels is (negative numbers indicate that the CEFR level for the word according to my common_swedish_words is larger that the level as per the most frequent use in SVALex):')
        print(f'{histo_sorted}')
        print('It is to be expected that the SVALex levels will be higher, as I have used the most frequetnly occuring level for a given word, rather than the lowest level. Moreover, the results are biased as there may be multiple CEFR levels associated with a word in common_swedish_words and each of these is used to update the histogram.')

        ## Compare the words I collected with the Kelly list
        print('\nSome comparison between the words I have collected and their levels and the words and values in Kelly list (Swedish_M3_CEFR).')
        print('\nComparison with Kelly list for Swedish:')
        words_Kelly_set=set()
        for w in words_kelly_swedish:
            words_Kelly_set.add(w)

        set_difference=common_swedish_words_set.difference(words_Kelly_set)
        # print(f'{set_difference=}')

        d2=common_swedish_words_set.difference(set_difference)
        # print(f'{d2=}')

        # compute words that are in common_swedish_words that are in Kelly list
        d3=d2.difference(set_difference)
        if len(d3) > 0:
            print(f'{len(d3)} words appear in both common_swedish_words and Kelly list.')
            if Verbose_Flag:
                print(f'These words are: {d3}')

        # Of the words in both, check for words in common_swedish_words that have a level of 'xx'
        missing_set=set()
        for w in d3:
            for k in common_english_and_swedish.common_swedish_words[w].keys():
                if k == 'xx':
                    missing_set.add(w)
        if len(missing_set) > 0:
            print(f'Missing CEFR level for {len(missing_set)} words from common_swedish_words - that appear in Kelly list:')
            if Verbose_Flag or True:
                missing_set_sorted=sorted(missing_set)
                print(f'{missing_set_sorted=}')

        histo_level_differences=dict()

        for w in d3:
            min_absolute_diff=1000
            saved_difference=1000
            for k1 in common_english_and_swedish.common_swedish_words[w].keys():
                for k2 in words_kelly_swedish[w].keys():
                    level_diff=compare_cefr_levels(k1, k2)
                    if abs(level_diff) < min_absolute_diff:
                        min_absolute_diff=abs(level_diff)
                        saved_difference=level_diff
            current_count=histo_level_differences.get(saved_difference, 0)
            histo_level_differences[saved_difference]=current_count+1
            if Verbose_Flag or True:
                if abs(saved_difference) > 4:
                    print(f"minimal level difference {level_diff } for '{w}' {k=} common_english_and_swedish.common_swedish_words: {common_english_and_swedish.common_swedish_words[w]} Kelly: {words_kelly_swedish[w]}")
        histo_sorted=dict(sorted(histo_level_differences.items(), key=lambda x:x[0]))
        print(f'{histo_sorted}')

        print('\nComparison with Kelly list for Swedish technical words:')
        set_difference=common_swedish_technical_words_set.difference(words_Kelly_set)
        # print(f'{set_difference=}')

        d2=common_swedish_technical_words_set.difference(set_difference)
        # print(f'{d2=}')

        # compute words that are in common_swedish_technical_words that are in Kelly list
        d3=d2.difference(set_difference)
        if len(d3) > 0:
            print('The words that appear in both common_swedish_technical_words and Kelly list:')
            print(f'\t{d3}')

        if Verbose_Flag:
            for w in d3:
                print(f"levels for '{w}' common_english_and_swedish.common_swedish_technical_words: {common_english_and_swedish.common_swedish_technical_words[w]} Kelly: {words_kelly_swedish[w]}")

        histo_level_differences=dict()

        for w in d3:
            min_absolute_diff=1000
            saved_difference=1000
            for k1 in common_english_and_swedish.common_swedish_technical_words[w].keys():
                for k2 in words_kelly_swedish[w].keys():
                    level_diff=compare_cefr_levels(k1, k2)
                    if abs(level_diff) < min_absolute_diff:
                        min_absolute_diff=abs(level_diff)
                        saved_difference=level_diff
            current_count=histo_level_differences.get(saved_difference, 0)
            histo_level_differences[saved_difference]=current_count+1
            if Verbose_Flag or True:
                if abs(saved_difference) > 3:
                    print(f"minimal level difference {level_diff } for '{w}' {k=} common_english_and_swedish.common_swedish_technical_words: {common_english_and_swedish.common_swedish_technical_words[w]} Kelly: {words_kelly_swedish[w]}")
        histo_sorted=dict(sorted(histo_level_differences.items(), key=lambda x:x[0]))
        print(f'{histo_sorted}')

if __name__ == "__main__": main()
