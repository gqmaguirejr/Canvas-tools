#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# ./extract_text_split_on_stopwords.py PDF_file
#
# Extract text from PDF file, splitting lines before/after stopwords and punctuation.
#
# with option '-v' use verbose output
# with option '-s' consider Swedish words
# with option '-M' include terms in chemical_names_and_formulas and misc_words_to_ignore
# with option '-Q' do special processing (skipping more pages before extracting text)
# with option '-W' keep words from WordsToFilterOutSet
#
# G. Q. Maguire Jr.
#
# 2025-10-16
#

import sys
import os
import optparse
import pymupdf # import PyMuPDF
import faulthandler
import re
import pprint
import json

from collections import Counter
from collections import defaultdict

import sys
sys.path.append('/z3/maguire/Canvas/Canvas-tools')  # Include the path to module_folder
sys.path.append('/home/maguire/Canvas-tools')
sys.path.append('/home/maguire/Canvas/Canvas-tools')

#  as common_English_words, common_swedish_words, common_swedish_technical_words
import common_english
import common_swedish
import common_acronyms
import common_danish
import common_dutch
import common_estonian
import common_finnish
import common_french
import common_german
import common_greek
import common_icelandic
import common_italian
import common_japanese
import common_latin
import common_norwegian
import common_portuguese
import common_russian
import common_spanish
import common_turkish

import AVL_words_with_CEFR
import ACM_CCS
import IEEE_thesaurus

# List of words that will trigger a line break.
StopWords=[
    u'a', u'à', u'able', u'about', u'above', u'additional', u'additionally', u'after',
    u'against', u'all', u'allows', u'along', u'almost', u'already', u'also', u'also:',
    u'although', u'an', u'and', u'another', u'any', u'anyone', u'are', u'as', u'at',
    u'average', u'be', u'been', u'because', u'before', u'being', u'below', u'between',
    u'both', u'but', u'by', u'can', u'could', u'course', u'currently', u'decrease',
    u'decreasing', u'did', u'do', u'doing', u'does', u'done', u'down', u'due', u'during',
    u'each', u'early', u'earlier', u'easy', u'e.g', u'eigth', u'either', u'else', u'end',
    u'especially', u'etc', u'even', u'every', u'far', u'few', u'five', u'first',
    u'follow', u'following', u'for', u'formerly', u'four', u'from', u'further',
    u'general', u'generally', u'get', u'going', u'good', u'had', u'has', u'have',
    u'having', u'he', u'hence', u'her', u'here', u'hers', u'herself', u'high',
    u'higher', u'him', u'himself', u'his',  u'how', u'however', u'i', u'i.e', u'if',
    u'in', u'include', u'includes', u'including', u'increase', u'increasing', u'into',
    u'is', u'it', u"it's", u'its', u'itself', u'just', u'know', u'known', u'knows',
    u'last', u'later', u'large', u'least', u'like', u'long', u'longer', u'low',
    u'made', u'many', u'make', u'makes', u'me', u'might', u'much', u'more', u'most',
    u'must', u'my', u'myself', u'near', u'need', u'needs', u'needed', u'next', u'new',
    u'no', u'nor', u'not', u'now', u'of', u'off', u'often', u'on', u'once', u'one',
    u'only', u'or', u'other', u'others', u'otherwise', u'our', u'ours', u'ourselves',
    u'out', u'over', u'own', u'pass', u'per', u'pg', u'pp', u'provides', u'rather',
    u'require', u's', u'same', u'see', u'several', u'she', u'should', u'simply',
    u'since', u'six', u'small', u'so', u'some', u'such', u'take', u'takes', u'th',
    u'than', u'that', u'the', u'then', u'their', u'theirs', u'them', u'themselves',
    u'then', u'there', u'therefore', u'these', u'three', u'they', u'this', u'those',
    u'through', u'thus', u'time', u'to', u'too', u'try', u'two', u'under', u'unit',
    u'until', u'up', u'used', u'verison', u'very', u'vs', u'want', u'was', u'we',
    u'were', u'what', u'when', u'where', u'which', u'while', u'who', u'whom', u'why',
    u'wide', u'will', u'with', u'within', u'would', u'you', u'your', u'yourself',
    u'yourselves'
]

# Convert to a set for efficient O(1) lookups
StopWordsSet = set(StopWords)

WordsToFilterOut=[
    'KTH',
    # names of parts of document
    'Abstract',
    'Academic Dissertation',
    'Acknowledgments',
    'Background',
    'CONTENTS',
    'Chapter',
    'Conclusions',
    'Equation',
    'FIGURES', 'FIGURES LIST',
    'Figure',  'Figures',
    'Future Work',
    'Future work',
    'Introduction',
    'Licentiate thesis',
    'Listing',
    'LISTINGS List',
    'Related Work',
    'Research Method',
    'Research Methodology',
    'Results',
    'Results and Analysis',
    'Section',
    'Sections',
    'Table',
    'TABLES',
    'TABLES LISTINGS',
    'kth royal institute',
    'Universitetsservice US-AB',
    'abstract',
    'acknowledgments',
    'background',
    'contents',
    'keywords',
    'introduction',
    'references',
    'thesis',
    'work',

    # days of the week
    'Monday',
    'Tuesday',
    'Wednesday',
    'Thursday',
    'Friday',
    'Saturday',
    'Sunday',

    # names of the months
    'January',
    'February',
    'March',
    'April',
    'May',
    'June',
    'July',
    'August',
    'September',
    'October',
    'November',
    'December',


    # places
    'Electrum',
    'Kistagången',
    'Myanmar',
    'Stockholm',
    'Sweden',


    # Swedish words
    'Nyckelord',
]


WordsToFilterOutSet=set(WordsToFilterOut)
WordsToFilterOutSet.update(ACM_CCS.ACM_toplevel)
WordsToFilterOutSet.update(ACM_CCS.ACM_categories)
WordsToFilterOutSet.update(IEEE_thesaurus.IEEE_thesaurus_2023_broad_terms)



def is_integer(s):
    """
    Returns True if the string s can be converted to an integer, False otherwise.
    """
    try:
        int(s)
        return True
    except ValueError:
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


# both 10% and 10th
def is_percentage(s):
    if len(s) > 1 and s[-1] == '%' and is_integer(s[:-1]):
        return True
    if len(s) > 2 and s[-2:] == 'th' and is_integer(s[:-2]):
        return True
    return False

def is_approximate_integer(s):
    if len(s) > 1 and (s[0] == '~' or s[0] == '∼' or s[0] == '≈') and is_integer(s[1:]):
        return True
    return False

def is_ISO_date(s):
    if s.count('-') == 2:
        ds = s.split('-')
        if is_integer(ds[0]) and is_integer(ds[1]) and is_integer(ds[2]):
            return True
    return False

def is_ISBN(s):
    if s.startswith("978-") and (s.count('-') == 4 or s.count('-') == 3):
        s=s.replace("-", "")
        if s.isnumeric():
            return True
    # ISBN-13 without additional dashes
    elif (s.startswith("978-") and s[4:].count('-') == 0) and s[4:].isdigit:
            return True
    elif s.count('-') == 3:
        s=s.replace("-", "")
        if s.isnumeric():
            return True
    # otherwise
    return False
    

def is_value_units(w):
    suffixes = sorted(common_english.common_units, key=len, reverse=True) #
    # check all suffixes.
    for s in suffixes:
        if w.endswith(s):
            # If a match is found, strip it and break the inner loop.
            if is_integer(w[:-len(s)].strip()):
                return True
            if is_unicode_power_of_ten(w[:-len(s)].strip()):
                return True
    #  If no suffix was found for this word, return False
    return False

def is_value_range_units(w):
    if w.count('-') == 1:
        ws=w.split('-')
        if len(ws) == 2: 
            if is_integer(ws[0]):
                return is_value_units(ws[1])
            elif is_unicode_power_of_ten(ws[0]):
                return is_value_units(ws[1])
            elif is_value_units(ws[0]) and is_value_units(ws[1]):
                return True
            else:
                return False
        else:
            return False
    elif w.count('–') == 1:
        ws=w.split('–')
        if len(ws) == 2: 
            if is_integer(ws[0]):
                return is_value_units(ws[1])
            elif is_unicode_power_of_ten(ws[0]):
                return is_value_units(ws[1])
            elif is_value_units(ws[0]) and is_value_units(ws[1]):
                return True
            else:
                return False
        else:
            return False
    return False



def is_value_dash_units(s):
    if s.count('-') == 1:
        ds = s.split('-')
        if is_integer(ds[0]) and ds[1] in common_english.common_units:
            return True
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
    
def is_TRITA_number(s):
    if s.startswith("TRITA-ABE-DLT") or\
       s.startswith("TRITA-CBH-FOU") or\
       s.startswith("TRITA-EECS-AVL") or\
       s.startswith("TRITA-ITM-AVL") or\
       s.startswith("TRITA-SCI-FOU"):
        return True
    return False

ligrature_table= {'\ufb00': 'ff', # 'ﬀ'
                  '\ufb03': 'f‌f‌i', # 'ﬃ'
                  '\ufb04': 'ffl', # 'ﬄ'
                  '\ufb01': 'fi', # 'ﬁ'
                  '\ufb02': 'fl', # 'ﬂ'
                  '\ua732': 'AA', # 'Ꜳ'
                  '\ua733': 'aa', # 'ꜳ'
                  '\ua733': 'aa', # 'ꜳ'
                  '\u00c6': 'AE', # 'Æ'
                  '\u00e6': 'ae', # 'æ'
                  '\uab31': 'aə', # 'ꬱ'
                  '\ua734': 'AO', # 'Ꜵ'
                  '\ua735': 'ao', # 'ꜵ'
                  '\ua736': 'AU', # 'Ꜷ'
                  '\ua737': 'au', # 'ꜷ'
                  '\ua738': 'AV', # 'Ꜹ'
                  '\ua739': 'av', # 'ꜹ'
                  '\ua73a': 'AV', # 'Ꜻ'  - note the bar
                  '\ua73b': 'av', # 'ꜻ'  - note the bar
                  '\ua73c': 'AY', # 'Ꜽ'
                  '\ua76a': 'ET', # 'Ꝫ'
                  '\ua76b': 'et', # 'ꝫ'
                  '\uab41': 'əø', # 'ꭁ'
                  '\u01F6': 'Hv', # 'Ƕ'
                  '\u0195': 'hu', # 'ƕ'
                  '\u2114': 'lb', # '℔'
                  '\u1efa': 'IL', # 'Ỻ'
                  '\u0152': 'OE', # 'Œ'
                  '\u0153': 'oe', # 'œ'
                  '\ua74e': 'OO', # 'Ꝏ'
                  '\ua74f': 'oo', # 'ꝏ'
                  '\uab62': 'ɔe', # 'ꭢ'
                  '\u1e9e': 'SS', # 'ẞ' -- rather than 'fs' replace with 'SS'
                  '\u00df': 'ss', # 'ß' -- rather than 'fz', replace with 'ss'
                  '\ufb06': 'st', # 'ﬆ'
                  '\ufb05': 'ſt', # 'ﬅ'  -- long ST
                  '\ua728': 'Tz', # 'Ꜩ'
                  '\ua729': 'tz', # 'ꜩ'
                  '\u1d6b': 'ue', # 'ᵫ'
                  '\uab63': 'uo', # 'ꭣ'
                  #'\u0057': 'UU', # 'W'
                  #'\u0077': 'uu', # 'w'
                  '\ua760': 'VY', # 'Ꝡ'
                  '\ua761': 'vy', # 'ꝡ'
                  # 
                  # '\u0238': 'db', # 'ȸ'
                  # '\u02a3': 'dz', # 'ʣ'
                  # '\u1b66': 'dʐ', # 'ꭦ'
                  # '\u02a5': 'dʑ', # 'ʥ'
                  # '\u02a4': 'dʒ', # 'ʤ'
                  # '\u02a9': 'fŋ', # 'ʩ'
                  # '\u02aa': 'ls', # 'ʪ'
                  # '\u02ab': 'lz', # 'ʫ'
                  # '\u026e': 'lʒ', # 'ɮ'
                  # '\u0239': 'qp', # 'ȹ'
                  # '\u02a8': 'tɕ', # 'ʨ'
                  # '\u02a6': 'ts', # 'ʦ'
                  # '\uab67': 'tʂ', # 'ꭧ'
                  # '\u02a7': 'tʃ', # 'ʧ'
                  # '\uab50': 'ui', # 'ꭐ'
                  # '\uab51': 'ui', # 'ꭑ' -- turned ui
                  # '\u026f': 'uu', # 'ɯ'
                  # # digraphs with single code points
                  # '\u01f1': 'DZ', # 'Ǳ'
                  # '\u01f2': 'Dz', # 'ǲ'
                  # '\u01f3': 'dz', # 'ǳ'
                  # '\u01c4': 'DŽ', # 'Ǆ'
                  # '\u01c5': 'Dž', # 'ǅ'
                  # '\u01c6': 'dž', # 'ǆ'
                  # '\u0132': 'IJ', # 'Ĳ'
                  # '\u0133': 'ij', # 'ĳ'
                  # '\u01c7': 'LJ', # 'Ǉ'
                  # '\u01c8': 'Lj', # 'ǈ'
                  # '\u01c9': 'lj', # 'ǉ'
                  # '\u01ca': 'NJ', # 'Ǌ'
                  # '\u01cb': 'Nj', # 'ǋ'
                  # '\u01cc': 'nj', # 'ǌ'
                  # '\u1d7a': 'th', # 'ᵺ'
                  }

def replace_ligature(s):
    """
    Replaces all ligatures in a string with their expanded equivalents in a single pass.
    """
    if not s:
        return s

    # 1. Create a regex pattern by joining all ligature keys with the OR operator '|'
    # The keys are escaped to handle any special regex characters.
    ligature_keys = sorted(ligrature_table.keys(), key=len, reverse=True)
    pattern = re.compile("|".join(re.escape(key) for key in ligature_keys))

    # 2. Define a lookup function for re.sub()
    def lookup(match):
        return ligrature_table[match.group(0)]

    # 3. Use re.sub with the lookup function to perform all replacements
    return pattern.sub(lookup, s)

abbreviations_map = {
    '⎧⎨⎩': '{', # a large left curly brace
    'i.e.': 'id est',
    'e.g.': 'for example',
    'et al.': 'et alii', # 'and others'
    'etc.': 'et cetera',
    'vs.': 'versus',
    'Dr.': 'Doctor',
    'Prof.': 'Professor',
    'prof.': 'professor',
    'Asst.': 'assistant',
    'Assoc.': 'asso0ciate',
    'Mr.': 'Mister',
    'Mrs.': 'Missus',
    'Ms.': 'Miss',
    'U.S.': 'United States',
    'U.K.': 'United Kingdom',
    'Inc.': 'Incorporated',
    'Ltd.': 'Limited',
    'M.Sc.': 'Master of Science', # Must come before M.S.
    'M.S.': 'Master of Science',

    # abbreviations for months
    'Jan.': 'January',
    'Feb.': 'February',
    'Mar.': 'March',
    'Apr.': 'April',
    # May
    'Jun.': 'June',
    'Jul.': 'July',
    'Aug.': 'August',
    'Sep.': 'September',
    'Sept.': 'September',
    'Oct.': 'October',
    'Nov.': 'November',
    'Dec.': 'December',

    # Add the rest of your month/other abbreviations here
}

def replace_abbreviations(text):
    """
    Replaces abbreviations in a string with their full-text equivalents.
    """
    if not text:
        return text

    # Sort keys by length (descending) to replace longer matches first
    sorted_keys = sorted(abbreviations_map.keys(), key=len, reverse=True)

    for abbr in sorted_keys:
        escaped_abbr = re.escape(abbr)
        
        # Start with a word boundary to prevent matching "see.g."
        start_boundary = r'\b'
        
        # --- THE FIX ---
        # Only add a word boundary at the end if the abbreviation
        # itself ends with a word character (a-z, 0-9, _).
        if abbr[-1].isalnum():
             end_boundary = r'\b'
        else:
             # If it ends with '.', don't add a boundary, as the '.'
             # already acts as the boundary.
             end_boundary = r''
        # --- END FIX ---

        # Build the final pattern
        pattern = start_boundary + escaped_abbr + end_boundary
        
        # Use a lambda function to handle case-insensitivity in the replacement
        # This makes sure "E.G." is replaced with "FOR EXAMPLE"
        def get_replacement(match):
            replacement = abbreviations_map[abbr]
            if match.group(0).isupper():
                return replacement.upper()
            elif match.group(0).istitle():
                return replacement.title()
            else:
                return replacement

        text = re.sub(pattern, get_replacement, text, flags=re.IGNORECASE)
        
    return text

def remove_suffixes(wl):
    # Sort suffixes by length (longest first) to fix the bug.
    # This ensures '<=' is checked before '='.
    suffixes = sorted(['-', '–', '>', '≤', '=', '<=', '*', '**', '†', '††', '‡', '‡‡', '§', '§§', '¶', '¶¶', '∥', '∥∥', '{', '*/', '&', '*', '…', '\u2019', "‚", '»'], key=len, reverse=True) #
    
    new_wl = []
    
    # 1. Loop through the word list (wl) ONCE.
    for w in wl:
        found_suffix = False
        
        # 2. For each word, check all suffixes.
        for s in suffixes:
            if w.endswith(s):
                # 3. If a match is found, strip it and break the inner loop.
                new_wl.append(w[:-len(s)].strip())
                found_suffix = True
                break # Suffix found, move to the next word
                
        # 4. If no suffix was found for this word, append the original word.
        if not found_suffix:
            new_wl.append(w)
            
    return new_wl

def remove_prefixes(wl):
    # Sort prefixes by length (longest first) to fix the bug.
    # This ensures '††' is checked before '†'
    prefixes = sorted(['*', '**', '†', '††', '‡', '‡‡', '§', '§§', '¶', '¶¶', '∥', '∥∥', '&', '- ', '/*', '//', '<', '>','⋆', '\uf091', '\uf09b', '—', '−', '–', '-', 'x', '&', '∝', '≥', '/', '=', '->', '∼', '▷', '…', '……', '✓', '', '⋮', '·', '∈', '∥', '©', '\u2019', '●', '±', '~', "‘", '®', '«'], key=len, reverse=True) # 
    
    new_wl = []
    
    # 1. Loop through the word list (wl) ONCE.
    for w in wl:
        found_prefix = False
        
        # 2. For each word, check all prefixes.
        for s in prefixes:
            if w.startswith(s):
                # 3. If a match is found, strip it and break the inner loop.
                new_wl.append(w[len(s):].strip())
                found_prefix = True
                break # prefix found, move to the next word
                
        # 4. If no prefix was found for this word, append the original word.
        if not found_prefix:
            new_wl.append(w)
            
    return new_wl

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

def compute_column_positions(current_page_words):
    global Verbose_Flag
    global header_bottom
    all_x0_values = []

    for idx, b in enumerate(current_page_words):
        x0, y0, x1, y1, word, block_no, line_no, word_no=b
        if y1 < header_bottom + 0.01:
            continue
        all_x0_values.append(round(x0))

    # Count the frequency of each x0 value.
    x0_counts = Counter(all_x0_values)
    
    # Get the two most common x0 values and their counts.
    # .most_common(2) returns a list of [ (value, count), (value, count) ]
    most_common_x0 = x0_counts.most_common(2)

    if len(most_common_x0) < 2:
        print("Could not find two distinct column positions.")
        return None, None
    
    # Extract just the x0 values from the result.
    column1_x0 = most_common_x0[0][0]
    column2_x0 = most_common_x0[1][0]
    
    # Ensure column1 is always the leftmost one.
    if column1_x0 < column2_x0:
        return column1_x0, column2_x0
    else:
        return column2_x0, column1_x0

def collect_acronyms_from_page(pageno, page):
    global Verbose_Flag
    global acronyms_dict
    global header_bottom

    print(f"collect_acronyms_from_page({pageno}, {page})")

    potential_key = ""
    potential_value = ""
    last_line_number=0
    last_block_no=0
    current_page_words=page.get_text("words", sort=True) # get plain text encoded as UTF-8
    column1, column2 = compute_column_positions(current_page_words)
    print(f"{column1=}, {column2=}")

    for idx, b in enumerate(current_page_words):
        x0, y0, x1, y1, word, block_no, line_no, word_no=b
        if y1 < header_bottom + 0.01:
            continue
        if Verbose_Flag:
            print(f"acronyms {idx} {b}")


        if x0 < (column2 - 1):
            if block_no > last_block_no or line_no > last_line_number:
                last_block_no = block_no
                # if this is a new line number, then it is a new key - save old key and value
                last_line_number = line_no
                potential_key = potential_key.strip()
                potential_value = potential_value.strip()
                if len(potential_key) > 0 and len(potential_value) > 0:
                    # filter out heading on first page of the list of acronyms and abbreviations
                    if potential_key.lower() != 'list of acronyms':
                        acronyms_dict[potential_key] = potential_value
                        if Verbose_Flag:
                            print(f"{potential_key.strip()} = {potential_value.strip()}")
                    potential_key = ""
                    potential_value = ""
                    
            potential_key += word + ' '

        if x0 > (column2 - 1):
            potential_value += word + ' '

    # save last key and value
    if len(potential_key.strip()) > 0 and len(potential_value.strip()) > 0:
        acronyms_dict[potential_key.strip()] = potential_value.strip()
        if Verbose_Flag:
            print(f"{potential_key.strip()} = {potential_value.strip()}")


# --- NEW HELPER FUNCTION (WITH FIX 3) ---
def _is_page_number_label(s):
    """
    Checks if a string is a valid page number label (digit or lowercase Roman).
    """
    s = s.strip('()[]|') # Clean up common punctuation
    if not s:
        return False
    
    # Regex for common lowercase roman numerals (e.g., i, v, x, xix, xxii)
    is_roman = bool(re.fullmatch(r'^(m*(c[md]|d?c{0,3})(x[cl]|l?x{0,3})(i[xv]|v?i{0,3}))$', s))
    
    # FIX 3: Page number must be a digit AND <= 4 chars (e.g., 9999)
    # This excludes ISBNs and years like 2023.
    is_digit = s.isdigit() and len(s) <= 4
    
    return is_digit or is_roman


def _analyze_pdf_layout(doc):
    """
    First-pass analysis to find the document's structure.
    
    This pass iterates once to find:
    1. Common header/footer coordinates.
    2. A map of section titles (e.g., "Contents", "References") to page numbers.
    3. A map of page number labels (e.g., "1", "iv") to their actual page index.
    
    Returns:
        A dictionary (or "profile") of the document layout.
    """
    print("--- Starting layout analysis pass ---")
    if Verbose_Flag:
        print(f"Analyzing {doc.page_count} pages...")

    section_map = {}
    page_number_map = {}
    
    # --- FIX: Collect all candidates for references ---
    references_candidates = []
    
    header_y_counter = Counter()
    footer_y_counter = Counter()

    page_height = doc[0].rect.height if doc.page_count > 0 else 792 # Default A4
    FOOTER_Y_THRESHOLD = page_height * 0.90 
    HEADER_Y_THRESHOLD = page_height * 0.10 
    MAX_PAGENUM_BLOCK_HEIGHT = 25 

    for pageno, page in enumerate(doc):
        
        # Skip first 3 pages (cover, title, info)
        if pageno < 3: 
            continue
            
        blocks = page.get_text("blocks", sort=True)
        if not blocks:
            continue
        
        page_header_blocks = []
        page_footer_blocks = []

        for b in blocks:
            x0, y0, x1, y1, text, block_no, block_type = b
            text = text.strip()
            text_lower = text.lower()
            block_height = y1 - y0 
            
            if not text:
                continue

            # --- 1. Find Section Titles ---
            if (y0 < HEADER_Y_THRESHOLD * 3) or (block_no==0) or (block_no==1): # Top 30%
                
                # --- FIX: Collect all candidates for references ---
                if (text_lower.startswith("references") or text_lower.startswith("bibliography")):
                    if len(text_lower) < 20: 
                        references_candidates.append(pageno)
                elif (text_lower.endswith("references") or text_lower.endswith("bibliography")):
                    if len(text_lower) < 20: 
                        references_candidates.append(pageno)

                
                    elif "acronyms" not in section_map and \
                         (text_lower.startswith("list of acronyms") or text_lower == "acronyms" or text_lower.startswith("list of abbreviations") or text_lower.find("list of abbreviations") >= 0):
                        if len(text_lower) < 40:
                            section_map["acronyms"] = pageno
                
                elif "contents" not in section_map and \
                     (text_lower.startswith("contents") or text_lower.startswith("table of contents")):
                    if len(text_lower) < 25:
                        section_map["contents"] = pageno
                
                elif "introduction" not in section_map and "introduction" in text_lower and \
                     ("1" in text or "chapter 1" in text_lower):
                     section_map["introduction"] = pageno

            # --- 2. Collect potential Page Number Blocks (must be short) ---
            if block_height < MAX_PAGENUM_BLOCK_HEIGHT:
                if y0 < HEADER_Y_THRESHOLD: # Top 10%
                    page_header_blocks.append(b)
                elif y1 > FOOTER_Y_THRESHOLD: # Bottom 10%
                    page_footer_blocks.append(b)

        # --- 3. Log common header/footer *visual* positions ---
        if page_header_blocks:
            lowest_header_y1 = round(max(b[3] for b in page_header_blocks))
            header_y_counter[lowest_header_y1] += 1
            
        if page_footer_blocks:
            highest_footer_y0 = round(min(b[1] for b in page_footer_blocks))
            footer_y_counter[highest_footer_y0] += 1
            
        # --- 4. Log page number labels from ONLY the candidate blocks ---
        for block in page_header_blocks + page_footer_blocks:
            page_num_text = block[4].strip()
            
            words = page_num_text.split()
            if not words:
                continue

            first_word = words[0]
            last_word = words[-1]
            page_label_found = None
            
            if _is_page_number_label(last_word):
                page_label_found = last_word.strip('()[]|')
            elif _is_page_number_label(first_word):
                page_label_found = first_word.strip('()[]|')
            
            if page_label_found and page_label_found not in page_number_map:
                page_number_map[page_label_found] = pageno

    
    # --- Analyze collected data and build the layout profile ---
    layout = {
        "header_bottom_y": 0,
        "footer_top_y": page_height,
        "start_page": 0,
        "end_page": doc.page_count, # Default
        "acronyms_page": False,
    }

    if header_y_counter:
        layout["header_bottom_y"] = header_y_counter.most_common(1)[0][0]
        
    if footer_y_counter:
        layout["footer_top_y"] = footer_y_counter.most_common(1)[0][0]

    # --- Find Start Page (Cascade logic) ---
    if '1' in page_number_map:
        layout["start_page"] = page_number_map['1']
    elif 'introduction' in section_map:
        layout["start_page"] = section_map['introduction']
    else:
        start_page = max(section_map.get("contents", -1), section_map.get("acronyms", -1)) + 1
        layout["start_page"] = max(0, start_page)

    # --- FIX: Find End Page (using start_page) ---
    for p in sorted(references_candidates):
        if p >= layout["start_page"]:
            layout["end_page"] = p
            break # Found the first real "References" page
        
    if "acronyms" in section_map:
        layout["acronyms_page"] = section_map["acronyms"]

    # --- Final Sanity Check ---
    if layout["start_page"] >= layout["end_page"]:
        print(f"*** WARNING: Start page ({layout['start_page']}) is after end page ({layout['end_page']}). Defaulting end page to end of doc.")
        layout["end_page"] = doc.page_count

    print("--- Layout analysis complete ---")
    print(f"  Header bottom estimated at: {layout['header_bottom_y']}")
    print(f"  Footer top estimated at: {layout['footer_top_y']}")
    print(f"  Acronyms page found at: {layout['acronyms_page']}")
    print(f"  Main content START page: {layout['start_page']}")
    print(f"  Main content END page (references): {layout['end_page']}")
    if Verbose_Flag:
        print(f"  DEBUG: page_number_map = {page_number_map}")
        print(f"  DEBUG: references_candidates = {references_candidates}")
        print(f"  DEBUG: layout = {layout=}")
    print("-----------------------------------")

    return layout

def extract_text_from_pdf(pdf_path):
    """
    Extracts text from a PDF file, splits it by stopwords and punctuation,
    and saves it to a text file.
    """
    global Verbose_Flag
    global acronyms_found
    global acronyms_text
    global header_bottom
    global options

    output_lines=[]

    try:
        doc = pymupdf.open(pdf_path)
        print(f"Successfully opened '{pdf_path}'...")

        # test the analysis procedure
        layout = _analyze_pdf_layout(doc)
        
        full_text = ""
        # Extract text from all pages
        if False and Verbose_Flag:
            for page in doc:
                full_text += page.get_text()
            print(f"{full_text=}")

        full_text = ""
        acronyms_text = ""

        acronyms_found=False
        first_page_found=False
        references_found=False
        current_header=False
        if layout and layout.get('header_bottom_y') > 0:
            header_bottom=layout['header_bottom_y']
        else:
            header_bottom=0
        first_page=False
        list_of_X_on_this_page=False
        list_of_X_page=False

        for pageno, page in enumerate(doc): # iterate the document pages
            # the cover text near the bottom of the page with the year, so skip the cover page, similar for title page, and book information page
            if pageno < 3:
                continue

            if Verbose_Flag:
                print(f"{pageno=}")
            current_page=page.get_text("blocks", sort=True) # get plain text encoded as UTF-8

            for idx, b in enumerate(current_page):
                if Verbose_Flag:
                    print(f"**** {idx=} {type(b)}****")
                x0, y0, x1, y1, lines_in_the_block, block_no, block_type=b
                if Verbose_Flag:
                    print(f"{x0=}, {y0=}, {x1=}, {y1=}, {lines_in_the_block=}, {block_no=}, {block_type=}")

                # look for the first abstract page and use the bottom of its bounding box as the bottom of the header
                if header_bottom == 0 and lines_in_the_block.startswith('Abstract |'):
                    header_bottom = y1
                    print(f"found header_bottom {header_bottom}")
                    continue
                
                # We assume that the list of acronyms is before the first page of the main matter
                # and has the expected header.
                # look for acronyms
                if header_bottom > 0 and not acronyms_found and (lines_in_the_block.startswith('List of Acronyms and abbreviations | ') or lines_in_the_block.startswith('List of acronyms and abbreviations | ') or lines_in_the_block.startswith('List of Abbreviations') or lines_in_the_block.startswith('Abbreviations')):
                    acronyms_found=True
                    current_header='Acronyms'
                    print(f"found acronyms {pageno}")

                # look for headers other than acronyms to stop collecting acronyms
                if (idx == 0 or idx == 1) and not (lines_in_the_block.startswith('List of Acronyms and abbreviations | ') or lines_in_the_block.startswith('List of acronyms and abbreviations | ') or lines_in_the_block.startswith('List of Abbreviations') or lines_in_the_block.startswith('Abbreviations')):
                    current_header=lines_in_the_block.strip()
                    
                # collect acronyms
                if acronyms_found and current_header == 'Acronyms' and not first_page_found:
                    if y1 > header_bottom and not lines_in_the_block.lower() == 'list of acronyms and abbreviations\n':
                        acronyms_text += lines_in_the_block
                        collect_acronyms_from_page(pageno, page)
                        break # go to the next page

                # look for first page of the main matter second page: lines_in_the_block.startswith('2 | ')
                if header_bottom > 0 and not first_page_found and (lines_in_the_block.endswith(' | 1\n')):
                    first_page_found = True
                    print(f"found first page {pageno}")

                # look for first of the references
                if header_bottom > 0 and first_page_found and not references_found and (lines_in_the_block.lower().startswith('references | ') or lines_in_the_block.lower().startswith('bibliography | ')):
                    references_found=True
                    print(f"found references page {pageno}")

                if first_page_found and not references_found and (lines_in_the_block.startswith('References') or lines_in_the_block.lower().endswith('references')):
                    references_found=True
                    print(f"found references page {pageno}")


                # if we are in the main matter and before the start of the references
                # add a small amount to the header_bottom to skip text in the header
                if y1 > (header_bottom + 1) and first_page_found and not references_found:
                    full_text += lines_in_the_block
                    print(f"collecting text using method 1 from page {pageno}")
                # else:
                #     continue

        if not first_page_found and not references_found:
            print(f"*** Try a second method to identify the pages ***")
            page_number_positions=dict()
            maximum_y0=0
            maximum_y1=0
            for pageno, page in enumerate(doc): # iterate the document pages
                # the cover text near the bottom of the page with the year, so skip the cover page, similar for title page, and book information page
                if pageno < 3:
                    continue

                if Verbose_Flag:
                    print(f"{pageno=}")
                current_page=page.get_text("blocks", sort=True) # get plain text encoded as UTF-8

                for idx, b in enumerate(current_page):
                    if Verbose_Flag:
                        print(f"**** {idx=} {type(b)}****")
                    x0, y0, x1, y1, lines_in_the_block, block_no, block_type=b
                    if Verbose_Flag:
                        print(f"{x0=}, {y0=}, {x1=}, {y1=}, {lines_in_the_block=}, {block_no=}, {block_type=}")

                    if y0 > maximum_y0:
                        maximum_y0 = y0

                    if y1 > maximum_y1:
                        maximum_y1 = y1

            print(f"{maximum_y0=} {maximum_y1=}")


            contents_page=False
            acronyms_page=False
            first_reference_page=False
            for pageno, page in enumerate(doc): # iterate the document pages
                # the cover text near the bottom of the page with the year, so skip the cover page, similar for title page, and book information page
                if pageno < 3:
                    continue
                
                # special case for thesis with miss numbered page 1
                if options.Qcase and pageno < 16:
                    continue
                

                if Verbose_Flag:
                    print(f"{pageno=}")
                current_page=page.get_text("blocks", sort=True) # get plain text encoded as UTF-8
                contents_on_this_page=False
                acronyms_on_this_page=False
                list_of_X_on_this_page=False
                references_on_this_page=False

                for idx, b in enumerate(current_page):
                    if Verbose_Flag:
                        print(f"**** {idx=} {type(b)}****")
                    x0, y0, x1, y1, lines_in_the_block, block_no, block_type=b
                    if Verbose_Flag:
                        print(f"{x0=}, {y0=}, {x1=}, {y1=}, {lines_in_the_block=}, {block_no=}, {block_type=}")

                    if y0 > int(maximum_y0) and y1 < int(maximum_y1) + 2:
                        page_number_positions[pageno] = lines_in_the_block.replace('\n', '')

                    if not acronyms_on_this_page and (y0 < maximum_y0 or block_no==0 or block_no==1) and (lines_in_the_block.lower().find('list of acronyms and abbreviations') >= 0 or lines_in_the_block.find('Acronyms') >= 0 or lines_in_the_block.lower().find('list of abbreviations') >= 0 or lines_in_the_block.lower().find('abbreviations') >= 0):
                        acronyms_on_this_page=True
                        print(f"{acronyms_on_this_page=}")
                        if contents_page != pageno:
                            acronyms_found=True
                            acronyms_page=pageno
                            
                    if not contents_on_this_page and y0 < maximum_y0 and (lines_in_the_block.lower().find('contents') >= 0 or lines_in_the_block.find('Contents') >= 0):
                        contents_on_this_page=True
                        print(f"{contents_on_this_page=}")

                    if not contents_on_this_page and not list_of_X_on_this_page and y0 < maximum_y0 and lines_in_the_block.startswith('List of'):
                        list_of_X_on_this_page=True
                        list_of_X_page=pageno
                        print(f"{list_of_X_on_this_page=}")

                    if not first_reference_page and not references_on_this_page and not contents_on_this_page and y0 < maximum_y0 and\
                       (lines_in_the_block.lower().startswith('references') or\
                        lines_in_the_block.lower().strip().endswith('references') or\
                        lines_in_the_block.lower().startswith('bibliography')):
                        references_on_this_page=True
                        first_reference_page=pageno
                        print(f"{first_reference_page=}")

                if contents_on_this_page: #  and list_of_X_on_this_page
                    contents_page=pageno
                    print(f"found contents page {contents_page}")

            print(f"{page_number_positions=}")
            for idx, i in enumerate(page_number_positions):
                if not first_page_found:
                    if page_number_positions[i] == '1':
                        first_page_found=True
                        first_page=int(i)
                        print(f"found first page {first_page} at {idx=}")
                    else:
                        if layout and layout.get('start_page') > 0:
                            first_page_found=True
                            first_page=layout['start_page']
                            print(f"Using first page {first_page}")
            if contents_page:
                print(f"{contents_page=}")
            if acronyms_page:
                print(f"{acronyms_page=}")
            if first_reference_page < first_page and layout and layout.get('end_page'):
                first_reference_page=layout['end_page']
            if not first_reference_page and layout and layout.get('end_page'):
                first_reference_page=layout['end_page']
            if first_reference_page:
                print(f"{first_reference_page=}")
        
            for pageno, page in enumerate(doc): # iterate the document pages
                if first_page_found and first_page and pageno < first_page:
                    continue

                if Verbose_Flag:
                    print(f"{pageno=}")
                current_page=page.get_text("blocks", sort=True) # get plain text encoded as UTF-8

                # look for first of the references, when found break out of the loop
                if pageno >= first_reference_page:
                    print(f"Reached references, no longer processing pages")
                    break

                # collect acronyms
                # Assume the acronyms page is before the first "List of X" pages OR
                # the acronyms page is just before the first page
                if acronyms_page < list_of_X_page:
                    if acronyms_found and pageno >= acronyms_page and pageno < list_of_X_page and pageno < first_page:
                        acronyms_text += lines_in_the_block
                        collect_acronyms_from_page(pageno, page)
                else:
                    if acronyms_found and pageno >= acronyms_page and pageno < first_page:
                        prefix1='Acronyms'
                        prefix2='ACRONYMS'
                        if lines_in_the_block.startswith(prefix1) or lines_in_the_block.startswith(prefix2):
                            acronyms_text += lines_in_the_block[len(prefix1):]
                        else:
                            acronyms_text += lines_in_the_block
                        collect_acronyms_from_page(pageno, page)

                if pageno >= first_page:
                    # if we are in the main matter and before the start of the references
                    for idx, b in enumerate(current_page):
                        if Verbose_Flag:
                            print(f"**** {idx=} {type(b)}****")
                        x0, y0, x1, y1, lines_in_the_block, block_no, block_type=b
                        # skip header lines (when collecting text)
                        if y1 < (header_bottom + 1):
                            continue
                        # replace end of line hyphens in the block
                        # note this replacement is too agressive
                        # lines_in_the_block=lines_in_the_block.replace('-\n', '')
                        if Verbose_Flag:
                            print(f"{x0=}, {y0=}, {x1=}, {y1=}, {lines_in_the_block=}, {block_no=}, {block_type=}")

                        # collect the contents of the page
                        print(f"collecting text using method 2 from page {pageno}")
                        full_text += lines_in_the_block

        if Verbose_Flag:
            print(f"length of full_text is {len(full_text)}")

        full_text=replace_ligature(full_text)
        full_text=replace_abbreviations(full_text)

        # combine to deal with hypehnation at the end of a line
        #full_text=full_text.replace('-\n', '')
        #print(f"****{full_text=}****")

        # replace Narrow No-Break Space (NNBSP) U+202F with a space
        full_text=full_text.replace('\u202f', ' ')

        # --- NEW ROBUST DE-HYPHENATION ---
        
        # take care of some special cases
        full_text=full_text.replace('-\ntype', '-type')

        # Case 1: Handle word breaks (e.g., "comput-\ner" -> "computer")
        # This ONLY matches if there is a lowercase letter *before*
        # AND *after* the hyphen-newline.
        full_text = re.sub(r'([a-z])-\n([a-z])', r'\1\2', full_text)

        # Case 2: Handle all remaining compound words (e.g., "HR-\ngeneralist")
        # This rule now only finds hyphen-newlines that were *not* word breaks
        # (like acronyms, names, or other compounds) and replaces the
        # newline with a hyphen.
        full_text = re.sub(r'-\n', '-', full_text)

        # handle Em Dash '—' U+2014
        full_text = full_text.replace('—', ' — ')
        
        # replace remaining new lines with a double space
        full_text = full_text.replace('\n', '  ')

        # --- NEW LOGIC TO SPLIT TEXT ---
        
        # 1. Define a regex pattern for splitting.
        # This splits the text by any whitespace or by the desired punctuation marks.
        # The parentheses () ensure the delimiters (spaces and punctuation) are kept.
        #splitter_pattern = re.compile(r'(\s+|[.,?!:;()#"“”])')
        # The new, corrected pattern with escaped brackets and braces:
        splitter_pattern = re.compile(r'(\s+|[.,?!:;()#"“”„\[\]\{\}\+\∗×•∗])')
        
        tokens = splitter_pattern.split(full_text)
        #print(f"{tokens=}")

        # 2. Reconstruct the text, creating newlines around delimiters.
        output_lines = []
        current_phrase = ""
        for token in tokens:
            # Ignore empty strings or tokens that are only whitespace
            if not token:
                continue
            if token == '\n' or token == '\xa0':
                if current_phrase:
                    output_lines.append(current_phrase.strip())
                    current_phrase = ""
                    continue

            cleaned_token = token.strip().lower()
            is_stopword = cleaned_token in StopWordsSet
            # A simple check if the token itself is one of the punctuation marks
            is_punctuation = cleaned_token in {'.', ',', '?', '!', ':', ';', '(', ')', '"', '“', '”', '|', '#', '[', ']', '{', '}', '×', '*', '•', '∗', '+', '„'}

            if is_stopword or is_punctuation or is_integer(token) or is_percentage(token) or is_approximate_integer(token):
                # If we were building a phrase, add it to the output first.
                if current_phrase:
                    output_lines.append(current_phrase.strip())
                    current_phrase = ""
                # Add the delimiter (stopword/punctuation) as its own line.
                if not options.stop:
                    output_lines.append(token)
            else: # It's a normal word
                # Append the word to the current phrase, adding a space if needed.
                if not current_phrase:
                    current_phrase = token
                else:
                    # current_phrase += " " + token
                    current_phrase += token

        # Add any leftover phrase at the end of the text
        if current_phrase:
            output_lines.append(current_phrase.strip())

        # remove the start of some lines
        output_lines = [l[2:] if l.startswith('% ') else l for l in output_lines]
        output_lines = [l[2:] if l.startswith('= ') else l for l in output_lines]

        # optionally, filter out words from WordsToFilterOutSet
        if not options.Wcase:
            output_lines = [l for l in output_lines if l not in WordsToFilterOutSet]

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if 'doc' in locals() and doc:
            doc.close()

    return output_lines


def group_by_prefix(phrase_list, min_group_size=2):
    """
    Groups phrases by their first word (prefix).
    """
    prefix_groups = defaultdict(list)
    
    for phrase in phrase_list:
        words = phrase.split()
        if len(words) > 1:
            prefix = words[0].strip()
            # Ignore groups based on a stopword
            if prefix.lower() not in StopWords:
                prefix_groups[prefix].append(phrase)
    
    # Filter out groups that are too small to be meaningful
    return {
        prefix: members for prefix, members in prefix_groups.items()
        if len(members) >= min_group_size
    }

def group_by_suffix(phrase_list, min_group_size=2):
    """
    Groups phrases by their last word (suffix).
    """
    suffix_groups = defaultdict(list)
    
    for phrase in phrase_list:
        words = phrase.split()
        if len(words) > 1:
            suffix = words[-1].strip()
            # Ignore groups based on a stopword
            if suffix.lower() not in StopWords:
                suffix_groups[suffix].append(phrase)
    
    # Filter out groups that are too small to be meaningful
    return {
        suffix: members for suffix, members in suffix_groups.items()
        if len(members) >= min_group_size
    }



def remove_known_words(output_lines):
    global Verbose_Flag
    global well_known_acronyms
    global grand_union

    remove_list=[]
    for w in output_lines:
        # replace double spaces in a word with a single space
        if '  ' in w:
            w=w.replace('  ', ' ')

        # some individual characters to remove
        if w in ['\u0013', '\u0017', '%', '&', '-']:
            remove_list.append(w)
            
        # remove entries of the form 'Figure 4-2'
        if w.startswith('Figure ') or w.startswith('Table '):
            remove_list.append(w)

        # remove ordinals
        if w in common_english.ordinals_list:
            remove_list.append(w)

        # remove proper names
        for pn in sorted(common_english.proper_names, key=len, reverse=True):
            if w.startswith(pn):
                remove_list.append(pn)

        if w in common_english.top_100_English_words:
            remove_list.append(w)
            continue

        if w in common_english.thousand_most_common_words_in_English:
            remove_list.append(w)
            continue

        if w in AVL_words_with_CEFR.avl_words:
            remove_list.append(w)
            continue

        if w in common_english.common_English_words:
            remove_list.append(w)
            continue

        if w in common_english.KTH_ordbok_English_with_CEFR:
            remove_list.append(w)
            continue

        if w in common_english.chemical_elements_symbols:
            remove_list.append(w)
            continue

        if w in common_english.chemical_elements:
            remove_list.append(w)
            continue

        if w in common_swedish.common_swedish_words:
            remove_list.append(w)
            continue

        if w in common_swedish.common_swedish_technical_words:
            remove_list.append(w)
            continue

        if w in common_swedish.KTH_ordbok_Swedish_with_CEFR:
            remove_list.append(w)
            continue

        if w in common_english.programming_keywords:
            remove_list.append(w)
            continue

        if w in common_english.names_of_persons:
            remove_list.append(w)
            continue

        if options.swedish and w[-1] == 's' and w[:-1] in common_english.names_of_persons:
            remove_list.append(w)
            continue

        if w in sorted(common_english.proper_names, key=len, reverse=True):
            remove_list.append(w)
            continue

        # if w is a series of names of persons, then remove it
        if ' ' in w:
            ws = w.split(' ')
            name_flag=True
            for ww in ws:
                if ww not in common_english.names_of_persons:
                    name_flag=False
            if name_flag:
                remove_list.append(w)
            continue

        if is_TRITA_number(w):
            remove_list.append(w)
            continue

        if w in common_english.language_tags:
            remove_list.append(w)
            continue

        if w in common_english.KTH_ordbok_English_with_CEFR:
            remove_list.append(w)
            continue

        if w in common_english.amino_acids:
            remove_list.append(w)
            continue

        if w in common_english.common_units:
            remove_list.append(w)
            continue

        if is_value_range_units(w):
            remove_list.append(w)
            continue
        
        if is_value_units(w):
            remove_list.append(w)
            continue

        if w in common_english.binary_prefixes:
            remove_list.append(w)
            continue

        # remove MiB and similar units
        if len(w) > 2 and  w[0:2] in common_english.binary_prefixes and w[2:] in ['B', 'b']:
            remove_list.append(w)
            continue

        if w in common_english.decimal_prefixes:
            remove_list.append(w)
            continue

        if w in common_english.place_names:
            remove_list.append(w)
            continue

        if w in common_swedish.swedish_place_names:
            remove_list.append(w)
            continue

        if w in common_swedish.swedish_names_for_foreign_places:
            remove_list.append(w)
            continue


        if w in well_known_acronyms:
             remove_list.append(w)
             continue

        # remove acronyms possessives
        if w.endswith('’s') and w[:-2] in well_known_acronyms:
            remove_list.append(w)
            continue

        if w.endswith('S’') and w[:-1] in well_known_acronyms:
            remove_list.append(w)
            continue

        # remove names possessives
        if w.endswith('’s') and w[:-2] in common_english.names_of_persons:
            remove_list.append(w)
            continue

        if options.swedish and w.endswith('s') and w[:-1] in common_english.names_of_persons:
            remove_list.append(w)
            continue

        if w.endswith('s’') and w[:-1] in common_english.names_of_persons:
            remove_list.append(w)
            continue

        # remove place possessives
        if w.endswith('’s') and w[:-2] in common_english.place_names:
            remove_list.append(w)
            continue

        if options.swedish and w.endswith('s') and w[:-1] in common_swedish.swedish_place_names:
            remove_list.append(w)
            continue

        if options.swedish and w.endswith('s') and w[:-1] in common_swedish.swedish_names_for_foreign_places:
            remove_list.append(w)
            continue

        # remove company and product possessives
        if w.endswith('’s') and w[:-2] in common_english.company_and_product_names:
            remove_list.append(w)
            continue

        if w in common_english.chemical_names_and_formulas:
            remove_list.append(w)
            continue

        if w in common_english.common_urls:
            remove_list.append(w)
            continue

        if w in common_english.java_paths:
            remove_list.append(w)
            continue

        if w in common_english.company_and_product_names:
            remove_list.append(w)
            continue

        if w in common_english.common_programming_languages:
            remove_list.append(w)
            continue

        if w in common_english.KTH_ordbok_English_with_CEFR:
            remove_list.append(w)
            continue

        if w in common_english.names_of_persons:
            remove_list.append(w)
            continue

        if w in common_english.mathematical_words_to_ignore:
            remove_list.append(w)
            continue

        if w in common_english.miss_spelled_words:
            remove_list.append(w)
            continue
        
        if w in common_latin.common_latin_words:
            remove_list.append(w)
            continue

        if w in common_german.common_german_words:
            remove_list.append(w)
            continue

        if w in common_greek.common_greek_words:
            remove_list.append(w)
            continue

        if w in common_swedish.common_swedish_words:
            remove_list.append(w)
            continue

        if w in common_swedish.common_swedish_technical_words:
            remove_list.append(w)
            continue

        if w in common_swedish.common_Swingish_words:
            remove_list.append(w)
            continue

        if w in common_swedish.KTH_ordbok_Swedish_with_CEFR:
            remove_list.append(w)
            continue

        if w in common_norwegian.common_norwegian_words:
            remove_list.append(w)
            continue

        if w in common_portuguese.common_portuguese_words:
            remove_list.append(w)
            continue

        if w in common_russian.common_russian_words:
            remove_list.append(w)
            continue

        if w in common_spanish.common_spanish_words:
            remove_list.append(w)
            continue

        if w in common_turkish.common_turkish_words:
            remove_list.append(w)
            continue

        if w in common_french.common_french_words:
            remove_list.append(w)
            continue

        if w in common_danish.common_danish_words:
            remove_list.append(w)
            continue

        if w in common_dutch.common_dutch_words:
            remove_list.append(w)
            continue

        if w in common_estonian.common_estonian_words:
            remove_list.append(w)
            continue

        if w in common_finnish.common_finnish_words:
            remove_list.append(w)
            continue

        if w in common_icelandic.common_icelandic_words:
            remove_list.append(w)
            continue

        if w in common_italian.common_italian_words:
            remove_list.append(w)
            continue

        if w in common_japanese.common_japanese_words:
            remove_list.append(w)
            continue

        #  check for lower case version
        if w.lower() in common_english.top_100_English_words:
            remove_list.append(w)
            continue

        if w.lower() in common_english.thousand_most_common_words_in_English:
            remove_list.append(w)
            continue

        if w.lower() in AVL_words_with_CEFR.avl_words:
            remove_list.append(w)
            continue

        if w.lower() in common_english.common_English_words:
            remove_list.append(w)
            continue

        # if w in common_english.chemical_elements_symbols:
        #     remove_list.append(w)
        #     continue

        if w.lower() in common_english.chemical_elements:
            remove_list.append(w)
            continue

        # if w in common_english.programming_keywords:
        #     remove_list.append(w)
        #     continue

        # if w in common_english.names_of_persons:
        #     remove_list.append(w)
        #     continue

        # if w in common_english.language_tags:
        #     remove_list.append(w)
        #     continue

        if w.lower() in common_english.KTH_ordbok_English_with_CEFR:
            remove_list.append(w)
            continue

        # if w.lower() in common_english.common_units:
        #     remove_list.append(w)
        #     continue

        # if w.lower() in common_english.amino_acids:
        #     remove_list.append(w)
        #     continue

        # if w.lower() in common_english.binary_prefixes:
        #     remove_list.append(w)
        #     continue

        # if w.lower() in common_english.decimal_prefixes:
        #     remove_list.append(w)
        #     continue

        # if w.lower() in common_english.place_names:
        #     remove_list.append(w)
        #     continue

        # if w.lower() in well_known_acronyms:
        #     remove_list.append(w)
        #     continue

        # if w.lower() in common_english.chemical_names_and_formulas:
        #     remove_list.append(w)
        #     continue

        if w.lower() in common_english.common_urls:
            remove_list.append(w)
            continue

        if w.lower() in common_english.java_paths:
            remove_list.append(w)
            continue

        if w in common_english.company_and_product_names:
            remove_list.append(w)
            continue

        if w.lower() in common_english.common_programming_languages:
            remove_list.append(w)
            continue

        if w.lower() in common_english.KTH_ordbok_English_with_CEFR:
            remove_list.append(w)
            continue

        # if w in common_english.names_of_persons:
        #     remove_list.append(w)
        #     continue

        if w.lower() in common_english.mathematical_words_to_ignore:
            remove_list.append(w)
            continue

        if w.lower() in common_english.miss_spelled_words:
            remove_list.append(w)
            continue
        
        if w.lower() in common_latin.common_latin_words:
            remove_list.append(w)
            continue

        if w.lower() in common_swedish.common_swedish_words:
            remove_list.append(w)
            continue

        if w.lower() in common_swedish.common_swedish_technical_words:
            remove_list.append(w)
            continue

        if w.lower() in common_swedish.common_Swingish_words:
            remove_list.append(w)
            continue
            
        if w.lower() in common_swedish.KTH_ordbok_Swedish_with_CEFR:
            remove_list.append(w)
            continue

        if w.isupper() and w.title() in common_english.names_of_persons:
            remove_list.append(w)
            continue

        # take care of simple assignments, such as MTU=1500
        if w.count('=') == 1:
            ws=w.split('=')
            if grand_union:
                if ws[0] in grand_union and is_integer(ws[1]):
                    remove_list.append(w)
                    continue
                if ws[0] in grand_union and is_value_units(ws[1]):
                    remove_list.append(w)
                    continue

        # normalize U+2013 to U+2D
        if '–' in w:
            wtransformed=w.replace('–', '-')
            if wtransformed in common_english.names_of_persons:
                remove_list.append(w)
                continue

        if Verbose_Flag:
            print(f"'{w}' not in common_English_words and friends")

    return remove_list

# We escape names to handle special characters and sort by length (longest first)
sorted_names = sorted(common_english.proper_names, key=len, reverse=True)
# The pattern: (Name1|Name2|Name3)(followed by space OR end of string)
proper_name_pattern_string = r'^(?:' + '|'.join(map(re.escape, sorted_names)) + r')(?=\s|$)'

def remove_proper_names(w):
    # re.sub with a count of 1 ensures we only strip from the start, 
    return re.sub(proper_name_pattern_string, "", w, count=1).lstrip()


def prune_known_from_left(unique_terms_sorted, grand_union, acronym_filter_set, iteration_step):
    new_unique_terms=[]

    # remove suffixes and prefixes
    unique_terms_sorted = remove_prefixes(unique_terms_sorted)
    unique_terms_sorted = remove_suffixes(unique_terms_sorted)

    print(f"prune_known_from_left start: {len(unique_terms_sorted)=}")
    for w in unique_terms_sorted:
        # print(f"{iteration_step}:: {w}")

        # if len(w) > 2 and w[0:2] == '& ': # unnecessary with the remove_prefixes() above
        #     w=w[2:]
        w=w.strip()

        # replace double spaces in a word with a single space
        if '  ' in w:
            w=w.replace('  ', ' ')

        if len(w) == 0:
            continue

        # normalize U+2013 to U+2D
        if '–' in w:
            w=w.replace('–', '-')

        # normalize U+2019 to U+27
        if "’" in w:
            w=w.replace("’", "'")


        # if w.startswith('SSE'):
        #     print(f"processing {w}")

        # if w in sorted(common_english.proper_names, key=len, reverse=True):
        #     continue

        w=remove_proper_names(w)
        if len(w) == 0:
            continue

        # remove Swedish possessive names 
        if options.swedish and w.endswith("s") and w[:-1] in common_english.names_of_persons:
            continue


        # known term, so nothing to do
        if w in grand_union:
            # if w == 'SSE':
            #     print(f"removed {w}")
            continue
        if w.istitle() and w.lower() in grand_union:
            continue

        if w.lower() in grand_union:
            continue

        # handle terms such as 'Intra-TP'
        if '-' in w:
            ws=w.split('-')
            if len(ws) >= 2:
                if ws[0].istitle() and ws[1].isupper() and ws[0].lower() + '-' + ws[1] in grand_union:
                    continue

        # remove possessives
        if w.endswith('’s') and w[:-2] in grand_union:
            continue

        # remove possessives
        if w.endswith("s'") and w[:-2] in grand_union:
            continue

        if is_integer(w):
            continue

        if is_hex_number(w):
            continue
        
        if is_ISO_date(w):
            continue
        
        if is_ISBN(w):
            continue
        
        if is_TRITA_number(w):
            continue
        
        if is_value_range_units(w):
            continue
        
        if is_value_units(w):
            continue
        
        if is_value_dash_units(w):
            continue

        if is_integer_range_or_ISSN(w):
            continue

        # remove conference years
        if w.startswith("’") and len(w) >= 3 and is_integer(w[1:]):
            continue

        # remove conference names with apostrophy year
        if w.count("’") == 1:
            ws=w.split("’")
            if len(ws[0]) > 0 and ws[0] in grand_union and len(ws[1]) > 0 and is_integer(ws[1]):
                continue

        if is_equation(w):
            continue

        # take care of simple assignments, such as MTU=1500
        if w.count('=') == 1:
            ws=w.split('=')
            if ws[0] in grand_union and is_integer(ws[1]):
                continue
            if ws[0] in grand_union and is_value_units(ws[1]):
                continue

        if w in acronym_filter_set:
            print(f"{w} found in acronym_filter_set")
            continue

        if (w not in grand_union) and len(w) > 2 and w[0].isupper() and w[1:].islower():
            if w.lower() in grand_union:
                continue

        # consider alternatives such as "A/B" as "A B", but only do this in later steps
        if iteration_step > 5 and '/' in w:
            w=w.replace('/', ' ')
            w=w.strip()

        if ' ' not in w:
            new_unique_terms.append(w)
        else:
            ws = w.split(' ')
            # prune known words from the front
            new_term=''
            for idx, ww in enumerate(ws):
                # remove Swedish possessive names 
                if options.swedish and ww.endswith("s") and ww[:-1] in common_english.names_of_persons:
                    continue
                if ww in grand_union:
                    continue
                if ww.isupper() and ww.lower() in grand_union:
                    continue
                if ww.istitle() and ww.lower() in grand_union:
                    continue
                if ww.lower() in grand_union:
                    continue
                                          
                # remove possessives
                if ww.endswith("'s") and (ww[:-2] in grand_union or ww[:-2].lower() in grand_union):
                    continue

                # remove possessives
                if ww.endswith('’s') and (ww[:-2] in grand_union or ww[:-2].lower() in grand_union):
                    continue

                # remove possessives
                if ww.endswith("s'") and ww[:-2] in grand_union or ww[:-2].lower in grand_union:
                    continue

                # plural possessive
                if ww.endswith('s’') and (ww[:-2] in grand_union or ww[:-2].lower() in grand_union):
                    continue

                # remove words with trailing hyphens
                if ww.endswith('-') and ww[:-1] in grand_union:
                    continue
                if ww.endswith('-') and ww[:-1].lower() in grand_union:
                    continue

                if ww.count('-') == 1 and not ww.endswith('-'):
                    wws=ww.split('-')
                    if len(wws[0]) > 2 and len(wws[1]) > 2 and\
                       wws[0][0].isupper() and wws[0][1:].islower() and\
                       wws[1][0].isupper() and wws[1][1:].islower() and\
                       wws[0].lower() in grand_union and\
                       wws[1].lower() in grand_union:
                       continue
                    if len(wws[0]) > 2 and len(wws[1]) > 2 and\
                       wws[0][0].isupper() and wws[0][1:].islower() and\
                       wws[1].islower() and\
                       wws[0].lower() in grand_union and\
                       wws[1] in grand_union:
                       continue

                if is_integer(ww):
                    continue
                if is_hex_number(ww):
                    continue
                if is_ISO_date(ww):
                    continue
                if is_ISBN(ww):
                    continue
                if is_value_range_units(ww):
                    continue
                if is_value_units(ww):
                    continue
                if is_value_dash_units(ww):
                    continue
                if is_integer_range_or_ISSN(ww):
                    continue
                # take care of simple assignments, such as MTU=1500
                if ww.count('=') == 1:
                    ws=ww.split('=')
                    if ws[0] in grand_union and is_integer(ws[1]):
                        continue
                    if ws[0] in grand_union and is_value_units(ws[1]):
                        continue

                if ww in acronym_filter_set:
                    print(f"{ww} found in acronym_filter_set")
                    continue
                if len(ww) >= 2 and ww[0].isupper() and ww[1:].islower() and ww.lower() in grand_union:
                    continue

                if ww not in grand_union:
                    new_term=" ".join(ws[idx:])
                    break
            if new_term:
                new_unique_terms.append(new_term)

    return new_unique_terms

def remove_double_spaces(text_string):
    """
    Replaces all double spaces with a single space until no double spaces remain.
    """
    # Keep looping as long as two spaces are found
    while "  " in text_string:
        text_string = text_string.replace("  ", " ")
    return text_string

def is_unicode_power_of_ten(s):
    """
    Checks if an entire string is "10" followed by a Unicode superscript exponent.
    
    The string must be encoded in UTF-8 for the characters to be read correctly.
    
    Args:
        s (str): The input string to check.

    Returns:
        bool: True if the string is a Unicode power of 10, False otherwise.
    """
    # This regex pattern breaks down as follows:
    # ^     - Asserts the start of the string
    # 10    - Matches the literal characters "10"
    # [⁺⁻]? - Optionally matches one superscript plus (⁺) or minus (⁻)
    # [⁰¹²³⁴⁵⁶⁷⁸⁹]+ - Matches one or more superscript digits (0-9)
    # $     - Asserts the end of the string
    
    # NOTE: Your source file must be saved as UTF-8 for this to work.
    pattern = re.compile(r"^10[⁺⁻]?[⁰¹²³⁴⁵⁶⁷⁸⁹]+$")
    
    # re.match() checks for a match at the beginning of the string.
    # Because we use ^ and $, it ensures the *entire* string matches.
    if pattern.match(s):
        return True
    else:
        return False

def extract_potential_acronyms(text_block):
    """
    Finds potential acronyms/abbreviations enclosed in parentheses based on
    strict linguistic and numeric rules.

    Rules for the string inside parentheses:
    1. Must contain two or more characters that are letters (a-z, A-Z).
    2. May contain hyphens (-) or dashes.
    3. Must NOT be a purely numerical value (e.g., 123, 1.0, 1e-6).
    
    Args:
        text_block (str): The input text to search within.

    Returns:
        list: A list of strings found inside the parentheses (the acronyms).
    """
    
    # 1. Define the pattern for valid acronym content.
    #    It must contain at least two letters and can have hyphens/dashes.
    #    [^)]+ - Matches one or more characters that are NOT a closing parenthesis.
    #    [a-zA-Z].*[a-zA-Z] - Ensures there are at least two letters anywhere inside.
    #    [\-–—] - Matches various forms of hyphens/dashes.
    
    # Pattern explanation:
    # \(             - Literal opening parenthesis
    # (              - Start of capturing group (the acronym itself)
    #   (?![\d\.\+\-e]+$) - Negative Lookahead: Ensures the content is NOT JUST numbers, signs, and 'e'.
    #   [a-zA-Z\d\-\–—\s]{2,} - Must have at least 2 characters (letters, numbers, hyphens, spaces).
    # )
    # \)             - Literal closing parenthesis
    
    # We refine the pattern to be more strict about containing *at least two letters*
    # which is often the best indicator of a true acronym/abbreviation.
    # We also ensure the content is at least 2 characters long.
    
    # Combined Robust Pattern: 
    # 1. Matches: (XX), (X-Y), (X-Y-Z), (X2-Y), (A/B), (NFV), (DPDK)
    # 2. Excludes: (123), (1.0), (a), (I), (i), (X), (3)
    # 3. Excludes: (NF-V) if the content is just NF-V.
    
    
    # The simplest way to satisfy all rules without overly complex lookaheads 
    # is to require at least two letters and then filter out purely numeric strings post-match.
    
    # Pattern to capture anything inside parentheses that contains letters and hyphens:
    # Requires: 2 or more characters, including at least one letter.
    raw_pattern = re.compile(r'\(([a-zA-Z][a-zA-Z\d\-\–—\s\/]{1,}|[a-zA-Z\d\-\–—\s\/]{1,}[a-zA-Z])\)')
    
    # Find all candidates
    candidates = raw_pattern.findall(text_block)
    
    final_acronyms = []

    for acronym in candidates:
        # Strip extraneous whitespace and normalize the case
        clean_acronym = acronym.strip()
        
        # Rule 1 & 2 Check: Length and letter content is largely handled by the regex.
        if len(clean_acronym) < 2:
            continue

        # Rule 3 Check: Must NOT be purely numerical.
        # This checks if the string contains *only* numbers, periods, and standard scientific notation characters.
        # We must ignore those that were meant to be math/numbers but were complex strings (e.g., "1.2.3").
        is_numeric = re.fullmatch(r'[\d\s\.\,\+\-e]+', clean_acronym)
        
        # Check for strings that are numbers or very short single letters/symbols
        if is_numeric:
            continue
            
        # Specific check for content that is mostly letters, enforcing the spirit of the rule:
        letter_count = sum(1 for char in clean_acronym if char.isalpha())
        if letter_count >= 2:
             final_acronyms.append(clean_acronym)

    return sorted(list(set(final_acronyms))) # Return unique, sorted list

def main():
    global Verbose_Flag
    global options
    global acronyms_found
    global acronyms_text
    global acronyms_dict
    global well_known_acronyms
    global grand_union

    parser = optparse.OptionParser()
    parser.add_option('-v', '--verbose',
                      dest="verbose",
                      default=False,
                      action="store_true",
                      help="Print lots of output to stdout")

    parser.add_option('--stop',
                      dest="stop",
                      default=False,
                      action="store_true",
                      help="remove stopwords and punctuation from output")

    parser.add_option('-i', '--info',
                      dest="info",
                      default=False,
                      action="store_true",
                      help="Print information about the document")

    parser.add_option('-t', '--toc',
                      dest="toc",
                      default=False,
                      action="store_true",
                      help="Print information about the toc")

    parser.add_option('-M', '--Misc',
                      dest="Misc",
                      default=False,
                      action="store_true",
                      help="keep terms from misc_words_to_ignore")

    parser.add_option('-Q', '--Qcase',
                      dest="Qcase",
                      default=False,
                      action="store_true",
                      help="Special Q case")

    parser.add_option('-W', '--Wcase',
                      dest="Wcase",
                      default=False,
                      action="store_true",
                      help="keep words from WordsToFilterOutSet")


    parser.add_option('-s', '--swedish',
                      dest="swedish",
                      default=False,
                      action="store_true",
                      help="When processing a thesis in Swedish")

    options, remainder = parser.parse_args()
    Verbose_Flag = options.verbose


    if Verbose_Flag:
        print(f"ARGV      : {sys.argv[1:]}")
        print(f"VERBOSE   : {options.verbose}")
        print(f"REMAINING : {remainder}")

    if len(remainder) != 1:
        print("Usage: ./extract_text_split_on_stopwords.py [-v] <PDF_file>")
        sys.exit(1)

    input_file = remainder[0]

    if not os.path.exists(input_file):
        # Corrected bug: was using 'input_pdf' which was not defined
        print(f"Error: The file '{input_file}' was not found.")
        sys.exit(1)
        
    if options.info:
        try:
            doc = pymupdf.open(input_file)
            print(f"Successfully opened '{input_file}'...")

            print(f"{doc.metadata=}")

        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            if 'doc' in locals() and doc:
                doc.close()
        return
        
    if options.toc:
        try:
            doc = pymupdf.open(input_file)
            print(f"Successfully opened '{input_file}'...")

            for t in doc.get_toc():
                print(t) 

        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            if 'doc' in locals() and doc:
                doc.close()
        return
        

    # Use os.path.splitext to safely get the base filename
    base_output_name, extension = os.path.splitext(input_file)

    output_txt = base_output_name + ".txt"

    
    acronyms_dict=dict()
    acronyms_found=False

    output_lines = extract_text_from_pdf(input_file)
    saved_output_lines = output_lines
    potential_acronyms=[]
    processed_text = " ".join(saved_output_lines)
    processed_text=processed_text.replace("( ", "(")
    processed_text=processed_text.replace(" )", ")")
    print(f"{len(processed_text)=}")
    full_text_file = base_output_name + f"-full_text.txt"
    with open(full_text_file, "w", encoding="utf-8") as out_file:
        out_file.write(processed_text)
    potential_acronyms=extract_potential_acronyms(processed_text)
    if len(potential_acronyms) > 0:
        print(f"{potential_acronyms=}")


    # replace double spaces with one space
    output_lines = [remove_double_spaces(l) for l in output_lines]

    # Create a new, combined set for filtering
    acronym_filter_set = set()

    if acronyms_found:
        #print(f"{acronyms_text}")
        pprint.pprint(f"{acronyms_dict}")

        # Loop through dictionary keys ONCE to build the set
        for key in acronyms_dict.keys():
            acronym_filter_set.add(key)  # Add the base acronym (e.g., "cdf")
    
            # Use pluralization rule on the lowercase key
            if key.endswith('s') or key.endswith('S'):
                acronym_filter_set.add(key + 'es')  # e.g., "manrses"
            else:
                acronym_filter_set.add(key + 's')   # e.g., "cdfs"

        # Now, your list comprehension is simple, clean, and case-insensitive
        output_lines = [l for l in output_lines if l not in acronym_filter_set]

        output_lines = [l for l in output_lines if l not in acronyms_dict.values()]

    well_known_acronyms = [a[0] for a in common_acronyms.well_known_acronyms_list]

    # augment the well_known_acronyms with plurals
    well_known_acronym_filter_set=set()
    for key in well_known_acronyms:
        well_known_acronym_filter_set.add(key)

        # Use pluralization rule on the lowercase key
        if key.endswith('s') or key.endswith('S'):
            well_known_acronym_filter_set.add(key + 'es')  # e.g., "manrses"
        else:
            well_known_acronym_filter_set.add(key + 's')   # e.g., "cdfs"

    # add the spelled out version of the acronyms
    well_known_acronyms_meanings = [a[1] for a in common_acronyms.well_known_acronyms_list]
    for w in well_known_acronyms_meanings:
        well_known_acronyms.append(w)

    for w in well_known_acronym_filter_set:
        well_known_acronyms.append(w)

    grand_union = set()
    for w in common_english.top_100_English_words:
        grand_union.add(w)

    for w in common_english.thousand_most_common_words_in_English:
        grand_union.add(w)

    for w in AVL_words_with_CEFR.avl_words:
        grand_union.add(w)

    for w in common_english.common_English_words:
        grand_union.add(w)

    # to catch words with a hyphen that has been elided
    for w in common_english.common_English_words:
        if '-' in w:
            we = w.replace('-', '')
            grand_union.add(we)

    for w in common_english.ordinals_list:
        grand_union.add(w)

    for w in common_english.chemical_elements_symbols:
        grand_union.add(w)

    for w in common_english.chemical_elements:
        grand_union.add(w)

    for w in common_english.programming_keywords:
        grand_union.add(w)

    for w in common_english.names_of_persons:
        grand_union.add(w)

    for w in common_english.language_tags:
        grand_union.add(w)

    for w in common_english.KTH_ordbok_English_with_CEFR:
        grand_union.add(w)

    for w in common_norwegian.common_norwegian_words:
        grand_union.add(w)

    for w in common_portuguese.common_portuguese_words:
        grand_union.add(w)

    for w in common_russian.common_russian_words:
        grand_union.add(w)


    for w in common_spanish.common_spanish_words:
        grand_union.add(w)

    for w in common_french.common_french_words:
        grand_union.add(w)

    for w in common_danish.common_danish_words:
        grand_union.add(w)

    for w in common_dutch.common_dutch_words:
        grand_union.add(w)

    for w in common_estonian.common_estonian_words:
        grand_union.add(w)

    for w in common_finnish.common_finnish_words:
        grand_union.add(w)

    for w in common_german.common_german_words:
        grand_union.add(w)

    for w in common_greek.common_greek_words:
        grand_union.add(w)

    for w in common_icelandic.common_icelandic_words:
        grand_union.add(w)

    for w in common_italian.common_italian_words:
        grand_union.add(w)

    for w in common_japanese.common_japanese_words:
        grand_union.add(w)

    for w in common_turkish.common_turkish_words:
        grand_union.add(w)

    for w in common_english.amino_acids:
        grand_union.add(w)

    for w in common_english.common_units:
        grand_union.add(w)

    for w in common_english.binary_prefixes:
        grand_union.add(w)

    for w in common_english.decimal_prefixes:
        grand_union.add(w)

    for w in common_english.proper_names:
        grand_union.add(w)

    for w in common_english.place_names:
        grand_union.add(w)

    for w in common_swedish.swedish_place_names:
        grand_union.add(w)

    # deal with possive form of Swedish placename
    if options.swedish:
        for w in common_swedish.swedish_place_names:
            grand_union.add(w+'s')

    for w in common_swedish.swedish_names_for_foreign_places:
        grand_union.add(w)


    #print(f"{well_known_acronyms=}")
    for w in well_known_acronyms:
        if isinstance(w, dict):
            print(f"{w} is a dict")
        grand_union.add(w)


    if not options.Misc:
        print("Ignore terms in chemical_names_and_formulas")
        for w in common_english.chemical_names_and_formulas:
            grand_union.add(w)

    for w in common_english.common_urls:
        grand_union.add(w)

    for w in common_english.java_paths:
        grand_union.add(w)

    for w in common_english.company_and_product_names:
        grand_union.add(w)

    for w in common_english.common_programming_languages:
        grand_union.add(w)

    for w in common_english.KTH_ordbok_English_with_CEFR:
        grand_union.add(w)

    for w in common_english.mathematical_words_to_ignore:
        grand_union.add(w)

    for w in common_english.miss_spelled_words:
        grand_union.add(w)
        
    for w in common_latin.common_latin_words:
        grand_union.add(w)

    for w in acronym_filter_set:
        grand_union.add(w)

    if not options.Misc:
        print("Ignore terms in misc_words_to_ignore")
        for w in common_english.misc_words_to_ignore:
            grand_union.add(w)

    for w in common_swedish.common_swedish_words:
        grand_union.add(w)

    for w in common_swedish.common_Swingish_words:
        grand_union.add(w)

    for w in common_swedish.common_swedish_technical_words:
        grand_union.add(w)

    for w in common_swedish.KTH_ordbok_Swedish_with_CEFR:
        grand_union.add(w)

    if Verbose_Flag:
        print(f"begin processing the {len(output_lines)} lines")

    # remove unnecessary capitals
    output_lines = [l for l in output_lines if l.lower() not in output_lines]

    author_et_al = [l for l in output_lines if l.endswith(' et alii')]
    authors = [l[:-6] for l in output_lines if l.endswith(' et alii')]
    output_lines = [l for l in output_lines if l not in author_et_al]

    # drop strings with underscores, as these are not words, but probably variables
    output_lines = [l for l in output_lines if '_' not in l]

    # drop strings with '==', as these are not words, but probably an equation
    output_lines = [l for l in output_lines if '==' not in l]

    # remove suffixes and prefixes
    output_lines = remove_suffixes(output_lines)
    output_lines = remove_prefixes(output_lines)

    remove_list = remove_known_words(output_lines)
    remove_list = set(remove_list)
    if Verbose_Flag:
        print(f"to remove from output_lines: {remove_list=}")

    output_lines = [l for l in output_lines if l not in remove_list]

    processed_text = "\n".join(output_lines)

    # Write the processed text to the output file
    with open(output_txt, "w", encoding="utf-8") as out_file:
        out_file.write(processed_text)
        
    print(f"Successfully extracted and processed text to '{output_txt}'.")

    # Convert the list to a set to get unique terms
    unique_terms_set = set(output_lines)

    # Convert the set back to a list and sort it alphabetically
    unique_terms_sorted = sorted(list(unique_terms_set))
    processed_text = "\n".join(unique_terms_sorted)

    output_txt_unique = base_output_name + "-unique.txt"
    # Write the processed text to the output file
    with open(output_txt_unique, "w", encoding="utf-8") as out_file:
        out_file.write(processed_text)

    # if 'offloading' in grand_union:
    #     print("'offloading' is in grand_union")

    remove_list = []

    # split on new lines
    new_unique_terms_sorted=[]
    for w in unique_terms_sorted:
        if '\n' in w:
            ws = w.split('\n')
            for wws in ws:
                new_unique_terms_sorted.append(wws)
        else:
            new_unique_terms_sorted.append(w)

    unique_terms_sorted = new_unique_terms_sorted


    for w in unique_terms_sorted:
        # if w is a series of known words, then remove it
        if ' ' in w:
            ws = w.split(' ')
            common_flag=True
            for ww in ws:
                if ww not in grand_union or ww.lower() not in grand_union:
                    common_flag=False
            if common_flag:
                remove_list.append(w)
            continue

    unique_terms_sorted = [l for l in unique_terms_sorted if l not in remove_list]

    unique_terms=set(unique_terms_sorted)
    for i in range(0, 11):
        print(f"{i} {len(unique_terms)=}")
        if len(unique_terms) < 1:
            print("Nothing left to process")
            break
        new_terms=prune_known_from_left(unique_terms, grand_union, acronym_filter_set, i)


        new_terms_set = set(new_terms)
        if unique_terms == new_terms_set:
            break # nothing more was removed
        # set up for next iteration
        unique_terms = new_terms_set

        # make a sorted list for output
        unique_terms_sorted = sorted(list(new_terms_set))
        # for idx, t in enumerate(unique_terms_sorted):
        #     print(f"{i}: {idx}\t{t}")

        # Write the processed text to the output file
        output_txt_pruned = base_output_name + f"-pruned-{i}.txt"

        with open(output_txt_pruned, "w", encoding="utf-8") as out_file:
            processed_text = "\n".join(unique_terms_sorted)
            out_file.write(processed_text)



    prefix_results = group_by_prefix(output_lines)
    suffix_results = group_by_suffix(output_lines)

    print("--- PREFIX GROUPS (Central Concepts) ---")
    remove_list = remove_known_words(prefix_results)
    # keep entries that are in the acronyms for this document
    remove_list = [w for w in remove_list if w not in acronyms_dict]
    if Verbose_Flag:
        print(f"{remove_list=}")

    new_prefix_results=dict()
    for w in prefix_results:
        if w not in remove_list:
            new_prefix_results[w]=prefix_results[w]

    if Verbose_Flag:
        print(f"{new_prefix_results=}")
    prefix_results=new_prefix_results

    if Verbose_Flag:
        print(f"{len(prefix_results)=}")
    for idx, w in enumerate(prefix_results):
        print(f"prefix: {idx} {w} {len(prefix_results[w])}")

    print(json.dumps(prefix_results, indent=2, ensure_ascii=False))

    print("\n--- SUFFIX GROUPS (Concept Variants) ---")
    remove_list = remove_known_words(suffix_results)
    # keep entries that are in the acronyms for this document
    remove_list = [w for w in remove_list if w not in acronyms_dict]
    if Verbose_Flag:
        print(f"{remove_list=}")

    new_suffix_results=dict()
    for w in suffix_results:
        if w not in remove_list:
            new_suffix_results[w]=suffix_results[w]

    if Verbose_Flag:
        print(f"{new_suffix_results=}")
    suffix_results=new_suffix_results

    if Verbose_Flag:
        print(f"{len(suffix_results)=}")

    for idx, w in enumerate(sorted(suffix_results)):
        print(f"suffix: {idx} {w} {len(suffix_results[w])}")
    print(json.dumps(suffix_results, indent=2, ensure_ascii=False))



    # if 'CPU' in well_known_acronyms:
    #     print(f"CPU in well_known_acronyms")
    test_words=[
    ]
    for w in test_words:
        if w not in grand_union:
            print(f"{w} not in grand_union")

    if 'alii' in grand_union:
        print(f"'alii' in grand_union")

if __name__ == "__main__":
    main()
