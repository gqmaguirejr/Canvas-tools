#!/usr/bin/env python3
#
# ./compute_unique_words_for_pages_in_course.py  course_id
# 
# it outputs a file with the unique words each on a line
# where xx is the course_id
#
# G. Q: Maguire Jr.
#
# 2023.12.01
#
# based on compute_stats_for_pages_in_course.py
#
# with the option "-v" or "--verbose" you get lots of output - showing in detail the operations of the program
#
# Can also be called with an alternative configuration file using the option --config config-test.json
#
# Examples:
# ./compute_unique_words_for_pages_in_course.py 11544
#
# ./compute_unique_words_for_pages_in_course.py  --config config-test.json 11544
#
# Notes
# The program is taking the text version of the Canvas wikipages and not the HTML version. It should probably be changed to use the HTML version so as to
# (1) take advntage of language tagging and other tagging
# (2) to avoid some of the problems that Canvas has when extract text from lists and definitions [it is not adding a space or other separator
#     between entires - so one can get the end of one element of a list mixed with the start of the next element in this list.
#


import csv, requests, time
from pprint import pprint
import optparse
import sys

import json
import re

from lxml import html

# Use Python Pandas to create XLSX files
import pandas as pd

import nltk

import faulthandler

from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar, LTLine, LAParams, LTFigure, LTImage, LTTextLineHorizontal, LTTextBoxHorizontal, LTCurve
from typing import Iterable, Any
from pdfminer.layout import LAParams, LTTextBox, LTText, LTChar, LTAnno
import pdfminer.psparser
from pdfminer.pdfdocument import PDFNoValidXRef
from pdfminer.psparser import PSEOF

#############################
###### EDIT THIS STUFF ######
#############################

global baseUrl	# the base URL used for access to Canvas
global header	# the header for all HTML requests
global payload	# place to store additionally payload when needed for options to HTML requests

# Based upon the options to the program, initialize the variables used to access Canvas gia HTML requests
def initialize(options):
    global baseUrl, header, payload

    # styled based upon https://martin-thoma.com/configuration-files-in-python/
    if options.config_filename:
        config_file=options.config_filename
    else:
        config_file='config.json'

    try:
        with open(config_file) as json_data_file:
            configuration = json.load(json_data_file)
            access_token=configuration["canvas"]["access_token"]
            baseUrl="https://"+configuration["canvas"]["host"]+"/api/v1"

            header = {'Authorization' : 'Bearer ' + access_token}
            payload = {}
    except:
        print("Unable to open configuration file named {}".format(config_file))
        print("Please create a suitable configuration file, the default name is config.json")
        sys.exit()

prefixes_to_ignore=[
    "'",
    "\\",
    "¨",
    '+',
    ',',
    '-',
    './',
    ':',
    '=',
    '\u034f', # graphics joiner - non spacing mark
    '\u03bb',
    '\u200b', #Zero Width Space
    '\ud835\udc36', # MATHEMATICAL ITALIC CAPITAL C'
    '^',
    '_.',
    '|',
    '¡',
    '§',
    'µ',
    '¼',
    '¿',
    '×',
    'Þ',
    'α',
    'μ',
    'χ',
    '‒',
    '–',
    '—',
    '―',
    '†',
    '‡',
    '•',
    '…',
    '←',
    '↑',
    '→',
    '↔',
    '⇐',
    '⇒',
    '⇨',
    '≡',
    '≪',
    '☡',
    '☺',
    '⚠',
    '✔',
    '✝',
    '❌',
    '〃',
    '',
    '',
    '',
    '',
    '（',
    '👋',
]

suffixes_to_ignore=[
    "'",
    "§",
    '-',
    '.',
    '/',
    '\\',
    '\\n',
    '_',
    '®',
    '°',
    '–',
    '—',
    '†',
    '‡',
    '•',
    '…',
    '™',
    '⇒',
    '⚠',
    'ﾔ',
    '¶',
]

miss_spelled_words=[
    'under-utilizationLearnability',
    'interneting',
    'interent',
    "u-Law",
    'identi\ufb01cation',
    "you're",
    'ßtudent',     # should be "student"
    'similarily',  # should be 'similarly',
    'slideD',      # check - correct it is a template where D is one or more digits
]

def check_spelling_errors(s, url):
    if s in miss_spelled_words:
        if url:
            print(f'miss spelling {s} at {url=}')
        else:
            print(f'miss spelling {s}')

# remove first prefix
def prune_prefix(s):
    for pfx in prefixes_to_ignore:
        if s.startswith(pfx):
            s=s[len(pfx):]
            return s
    return s

# remove first suffix
def prune_suffix(s):
    for sfx in suffixes_to_ignore:
        if s.endswith(sfx):
            s=s[:-len(sfx)]
            return s
    return s

def unique_words_for_pages_in_course(course_id, pages_to_skip):
    global total_words_processed
    global all_text
    global total_raw_text
    list_of_all_pages=[]

    # Use the Canvas API to get the list of pages for this course
    #GET /api/v1/courses/:course_id/pages

    url = "{0}/courses/{1}/pages".format(baseUrl, course_id)
    if Verbose_Flag:
        print("url: " + url)

    r = requests.get(url, headers = header)
    if r.status_code == requests.codes.ok:
        page_response=r.json()
    else:
        print("No pages for course_id: {}".format(course_id))
        return False

    for p_response in page_response:  
        list_of_all_pages.append(p_response)

    # the following is needed when the reponse has been paginated
    # i.e., when the response is split into pieces - each returning only some of the list of modules
    while r.links.get('next', False):
        r = requests.get(r.links['next']['url'], headers=header)  
        page_response = r.json()  
        for p_response in page_response:  
            list_of_all_pages.append(p_response)

    for p in list_of_all_pages:
        # skip index page as tex runs the list items toegher
        if p['url'] in pages_to_skip:
            print(f"skipping page {p['url']}")
            continue

        if Verbose_Flag:
            print("title is '{0}' with url {1}".format(p['title'], p['url']))
        # Use the Canvas API to GET the page
        #GET /api/v1/courses/:course_id/pages/:url
                
        url = "{0}/courses/{1}/pages/{2}".format(baseUrl, course_id, p["url"])
        if Verbose_Flag:
            print(url)
        payload={}
        r = requests.get(url, headers = header, data=payload)
        if r.status_code == requests.codes.ok:
            page_response = r.json()  
            if Verbose_Flag:
                print("body: {}".format(page_response["body"]))

            body=page_response["body"]
            if isinstance(body, str) and len(body) > 0:
                document = html.document_fromstring(body)
                raw_text = document.text_content()
            else:               # nothing to process
                raw_text = ""
                continue

            if Verbose_Flag:
                print("raw_text: {}".format(raw_text))
            total_raw_text=total_raw_text+'\n'+raw_text
                
        else:
            print("No pages for course_id: {}".format(course_id))
            return False

        # to look for spectivic text on a page
        # if raw_text.find("Boyle") >= 0:
        #     print(f'Boyle on page {url}')

        if not raw_text or len(raw_text) < 1:
            print('nothing to processes')
            return
        words = nltk.word_tokenize(raw_text)
        all_text.extend(words)
        for word in words:
            total_words_processed=total_words_processed+1
            # words that start with certain characters/strings should be treated as if this character/string is not there
            # this is to address footnotes and some other special cases
            newword=word.strip()
            newword=prune_prefix(newword)
            newword=prune_suffix(newword)
            if len(newword) > 0:
                if newword.count('\n') > 0:
                    newwords=newword.split('\n')
                    for w in newwords:
                        unique_words.add(w)
                        check_spelling_errors(w, p["url"])
                else:
                    unique_words.add(newword)
                    check_spelling_errors(newword, p["url"])
    return True

def list_pages(course_id):
    list_of_all_pages=[]

    # Use the Canvas API to get the list of pages for this course
    #GET /api/v1/courses/:course_id/pages
    url = "{0}/courses/{1}/pages".format(baseUrl, course_id)

    if Verbose_Flag:
        print("url: " + url)

    r = requests.get(url, headers = header)
    if r.status_code == requests.codes.ok:
        page_response=r.json()

    for p_response in page_response:  
        list_of_all_pages.append(p_response)

        # the following is needed when the reponse has been paginated
        # i.e., when the response is split into pieces - each returning only some of the list of modules
        while r.links.get('next', False):
            r = requests.get(r.links['next']['url'], headers=header)  
            page_response = r.json()  
            for p_response in page_response:  
                list_of_all_pages.append(p_response)

    for p in list_of_all_pages:
        print("{}".format(p["title"]))

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


abbreviations_ending_in_period=[
    'i.e.',
    'e.g.',
    'al.',
    'etc.',
    'vs.',
    'Assoc.',
    'Corp.',
    'D.C.',
    'Dr.',
    'Inc.',
    'Jr.',
    'Ltd.',
    'Mr.',
    'Mrs.',
    'Ms.',
    'M.S.',
    'M.Sc.',
    'N.J.',
    'prof.',
    'Prof.',
    'U.S.',
    'U.S.C.',
    'U.K.',
    'Jan.',
    'Feb.',
    'Mar.',
    'Apr.',
    'Jun.',
    'Jul.',
    'Aug.',
    'Sep.',
    'Sept.',
    'Oct.',
    'Nov.',
    'Dec.',
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
    
# The check digit at the end of the ISBN can be an "X"
def is_ISBN(s):
    # if there is a trailing period remove it
    if len(s) > 2 and s.endswith("."):
        s=s[:-1]
    #
    if s.startswith("978-") and (s.count('-') == 4 or s.count('-') == 3):
        s=s.replace("-", "")
        if s.isnumeric():
            return True
        if s[-1] =='X' and s[:-1].isnumeric():
            return True

    # ISBN-13 without additional dashes
    elif (s.startswith("978-") and s[4:].count('-') == 0) and s[4:].isdigit:
            return True
    elif s.count('-') == 3:
        s=s.replace("-", "")
        if s.isnumeric():
            return True
        if s[-1] =='X' and s[:-1].isnumeric():
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

# there can be a while card X at the end of the field
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
            elif n[-1] == 'X' and is_hex_number('0x'+n[:-1]) and int('0x'+n[:-1], 0) < 65536:
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

    
def is_part_of_springerlink_identifier(s):
    if s.startswith('springerlink:'):
        return True
    # otherwise
    return False


def is_part_of_DiVA_identifier(s):
    if s.startswith('3Adiva-'):
        return True
    if s.startswith('diva-'):
        return s[5:].isdigit()
    # otherwise
    return False

def is_part_of_arXiv_identifier(s):
    if s.startswith('arXiv:'):
        return True
    # otherwise
    return False

#TRITA-ICT-EX-2009:104
def is_TRITA_identifier(string):
    if string.startswith('TRITA-'):
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
    #'.json',
    '.bib',
    '.bash',
    '.c',
    '.conf',
    '.csv',
    '.doc',
    '.docx',
    '.dtd',
    '.ethereal',
    '.gz',
    '.h',
    '.html',
    '.jpg',
    '.js',
    '.list',
    '.mods',
    '.pcap',
    '.pdf',
    '.php',
    '.png',
    '.ps',
    '.py',
    '.sh',
    '.srt',
    '.tar',
    '.tcpdump',
    '.tex',
    '.tsv',
    '.txt',
    '.xls',
    '.xlsx',
    '.xml',
    '.xsd',
    '.zip',
]
    
def is_filename_to_skip(string):
    for f in filename_extentions_to_skip:
        if string.endswith(f):
            return True
    # otherwise
    return False

def is_slide_number(s):
    if s.startswith('slide'):
        s=s[5:]
        if s.isdigit():
            return True
    # otherwise
    return False


# if there are multiple capital letters
def is_multiple_caps(s):
    len_s=len(s)
    count_caps=0
    
    if len_s > 1:
        for l in s:
            if l.isupper():
                count_caps=count_caps+1
    if count_caps > 1:
        return True
    # otherwise
    return False

# mixed case is any lower _and_ upprsease in one string
def ismixed(s):
    return any(c.islower() for c in s) and any(c.isupper() for c in s)

# added functions to get text from PDF files
def show_ltitem_hierarchy(o: Any, depth=0):
    """Show location and text of LTItem and all its descendants"""
    if depth == 0:
        print('element                        x1  y1  x2  y2   text')
        print('------------------------------ --- --- --- ---- -----')

    print(
        f'{get_indented_name(o, depth):<30.30s} '
        f'{get_optional_bbox(o)} '
        f'{get_optional_text(o)}'
    )

    if isinstance(o, Iterable):
        for i in o:
            show_ltitem_hierarchy(i, depth=depth + 1)


def get_indented_name(o: Any, depth: int) -> str:
    """Indented name of LTItem"""
    return '  ' * depth + o.__class__.__name__


def get_optional_bbox(o: Any) -> str:
    """Bounding box of LTItem if available, otherwise empty string"""
    if hasattr(o, 'bbox'):
        return ''.join(f'{i:<4.0f}' for i in o.bbox)
    return ''


def get_optional_text(o: Any) -> str:
    """Text of LTItem if available, otherwise empty string"""
    if hasattr(o, 'get_text'):
        return o.get_text().strip()
    return ''

def process_element(o: Any):
    global extracted_data
    global total_raw_text
    
    last_x_offset=None
    last_x_width=None

    last_y_offset=None            # y_offset of text characters
    font_size=None                # when in doublt, the font_size is None

    if isinstance(o, LTTextBoxHorizontal):
        for text_line in o:
            if hasattr(text_line, 'bbox'):
                last_x_offset=text_line.bbox[0]
                last_y_offset=text_line.bbox[1]
                last_x_width=text_line.bbox[2]-text_line.bbox[0]
            if Verbose_Flag:
                print(f'text_line={text_line}')
            if hasattr(text_line, 'size'):
                font_size=text_line.size
            else:
                font_size=0
            if isinstance(text_line, LTAnno):
                if Verbose_Flag:
                    print("found an LTAnno")

            # if isinstance(text_line, LTChar):
            #     print("fount an LTChar")
            # elif isinstance(text_line, LTAnno):
            #     print("fount an LTAnno")
            # else:
            #     for character in text_line:
            #         if isinstance(character, LTChar):
            #             font_size=character.size
        extracted_data.append([font_size, last_x_offset, last_y_offset, last_x_width, (o.get_text())])

    elif isinstance(o, LTTextContainer):
        if Verbose_Flag:
            print("element is LTTextContainer")
        for text_line in o:
            if Verbose_Flag:
                print(f'text_line={text_line}')
            if isinstance(text_line, LTAnno):
                if Verbose_Flag:
                    print("found an LTAnno")
            else:
                font_size=text_line.size
                if Verbose_Flag:
                    print("font_size of text_line={}".format(text_line.size))
            if hasattr(text_line, 'bbox'):
                last_x_offset=text_line.bbox[0]
                last_y_offset=text_line.bbox[1]
                last_x_width=text_line.bbox[2]-text_line.bbox[0]
            # if isinstance(text_line, LTChar):
            #     print("found an LTChar")
            #     font_size=text_line.size
            # elif isinstance(text_line, LTAnno):
            #     print("found an LTAnno")
            # else:
            #     for character in text_line:
            #         if isinstance(character, LTChar):
            #             font_size=character.size
        extracted_data.append([font_size, last_x_offset, last_y_offset, last_x_width, (o.get_text())])
    elif isinstance(o, LTLine): #  a line
        if Verbose_Flag:
            print(f'found an LTLine {o=}')
    elif isinstance(o, LTFigure):
        if isinstance(o, Iterable):
            for i in o:
                process_element(i)
    elif isinstance(o, LTImage):
        if Verbose_Flag:
            print(f'found an LTImage {o=}')
    elif isinstance(o, LTChar):
        if Verbose_Flag:
            print("found LTChar: {}".format(o.get_text()))
        if hasattr(o, 'bbox'):
            last_x_offset=o.bbox[0]
            last_y_offset=o.bbox[1]
            last_x_width=o.bbox[2]-o.bbox[0]
            font_size=o.size
        extracted_data.append([font_size, last_x_offset, last_y_offset, last_x_width, (o.get_text())])
    elif isinstance(o, LTAnno):
        if Verbose_Flag:
            print("fount an LTAnno")
        if hasattr(o, 'bbox'):
            last_x_offset=o.bbox[0]
            last_y_offset=o.bbox[1]
            last_x_width=o.bbox[2]-o.bbox[0]
            font_size=o.size
        extracted_data.append([font_size, last_x_offset, last_y_offset, last_x_width, ' '])
    elif isinstance(o, LTCurve): #  a curve
        if Verbose_Flag:
            print("found an LTCurve")
        extracted_data.append([font_size, last_x_offset, last_y_offset, last_x_width, ' '])
    else:
        if Verbose_Flag:
            print(f'unprocessed element: {o}')
        if isinstance(o, Iterable):
            for i in o:
                process_element(i)

def rough_comparison(a, b):
    if not a or not b:
        return False
    if abs(a-b) < 0.1:
        return True
    return False


def process_file(filename):
    global Verbose_Flag
    global testing
    global extracted_data
    global total_raw_text

    extracted_data=[]
    set_of_errors=set()
    set_of_evidence_for_new_cover=set()
    major_subject=None            # the major subject
    cycle=None                    # the cycle number
    place=None                    # the place from the cover
    font_size=None                # the latest font size
    last_x_offset=None
    last_x_width=None
    last_y_offset=None            # y_offset of text characters

    raw_text=''


    try:
        #for page in extract_pages(filename, page_numbers=[0], maxpages=1):
        for page in extract_pages(filename):
            if Verbose_Flag:
                print('showing show_ltitem_hierarchy')
                show_ltitem_hierarchy(page)

            if Verbose_Flag:
                print(f'{page=}')
            for element in page:
                if Verbose_Flag:
                    print(f'{element=}')
                process_element(element)

    except (PDFNoValidXRef, PSEOF, pdfminer.pdfdocument.PDFNoValidXRef, pdfminer.psparser.PSEOF) as e:
        print(f'Unexpected error in processing the PDF file: {filename} with error {e}')
        return False
    except Exception as e:
        print(f'Error in PDF extractor: {e}')
        return False

            
    if Verbose_Flag:
        print("extracted_data: {}".format(extracted_data))
    # Example of an old cover:
    # extracted_data: [[10.990000000000009, 'DEGREE PROJECT  COMPUTER SCIENCE AND ENGINEERING,\nSECOND CYCLE, 30 CREDITS\nSTOCKHOLM SWEDEN2021\n, \n'], [10.990000000000009, 'IN \n'], [19.99000000000001, 'title\n'], [16.00999999999999, 'author in caps\n'], [10.989999999999995, 'KTH ROYAL INSTITUTE OF TECHNOLOGY\nSCHOOL OF ELECTRICAL ENGINEERING AND COMPUTER SCIENCE\n'], [10.989999999999995, ' \n']]

    old_size=-1
    size=None
    current_string=''
    first_x_offset=None
    last_x_offset=None
    last_x_width=None
    last_y_offset=None
    last_size=None
    new_extracted_data=[]

    # collect individual characters and build into string - adding spaces as necessary
    for item in extracted_data:
        if isinstance(item, list):
            if len(item) == 5:
                size, current_x_offset, current_y_offset, current_x_width, txt = item
                if Verbose_Flag:
                    print(f'{current_x_offset},{current_y_offset} {size} {txt}')
                if not last_size:
                    last_size=size
                if not first_x_offset:
                    first_x_offset=current_x_offset
                if not last_y_offset:
                    last_y_offset=current_y_offset
                if rough_comparison(last_y_offset, current_y_offset):
                    if Verbose_Flag:
                        print(f'{txt} {current_x_offset} {last_x_offset} {last_x_width}')
                    if not last_x_offset:
                        last_x_offset=current_x_offset+current_x_width
                        last_x_width=current_x_width
                        current_string=current_string+txt
                        if Verbose_Flag:
                            print("direct insert current_string={}".format(current_string))
                    elif current_x_offset > (last_x_offset+0.2*last_x_width): # just a little faster than adjact characters
                        if Verbose_Flag:
                            print("last_x_offset+last_x_width={}".format(last_x_offset, last_x_width))
                        current_string=current_string+' '+txt
                        if Verbose_Flag:
                            print("inserted space current_string={}".format(current_string))
                        last_x_offset=current_x_offset+current_x_width
                        last_x_width=current_x_width
                    else:
                        current_string=current_string+txt
                        if Verbose_Flag:
                            print("second direct insert current_string={}".format(current_string))
                        last_x_offset=current_x_offset+current_x_width
                        last_x_width=current_x_width
                else:
                    if last_x_offset:
                        new_extracted_data.append([last_size, first_x_offset, last_y_offset, last_x_offset-first_x_offset, current_string])
                    else:
                        new_extracted_data.append([last_size, first_x_offset, last_y_offset, 0, current_string])
                        if Verbose_Flag:
                            print(f'current_string={current_string} and no last_x_offset')
                    current_string=""+txt
                    first_x_offset=current_x_offset
                    last_y_offset=current_y_offset
                    last_x_offset=None
                    last_x_width=None
                    last_size=None
    
    if last_x_offset:
        new_extracted_data.append([size, first_x_offset, current_y_offset, last_x_offset-first_x_offset, current_string])
    else:
        if Verbose_Flag:
            print(f'current_string={current_string} and no last_x_offset')

    if Verbose_Flag:
        print("new_extracted_data={}".format(new_extracted_data))

    extracted_data=new_extracted_data
    for item in extracted_data:
        if isinstance(item, list):
            if len(item) == 5:
                size, current_x_offset, current_y_offset, current_x_width, txt = item
                if Verbose_Flag:
                    print(f'{current_x_offset},{current_y_offset} {size} {txt}')

                raw_text = raw_text+' '+ txt.strip()

    total_raw_text=total_raw_text+raw_text

    return raw_text

def unique_words_in_PDF_file(input_PDF_file):
    global unique_words
    global total_words_processed

    raw_text=process_file(input_PDF_file)
    words = nltk.word_tokenize(raw_text)
    all_text.extend(words)
    for word in words:
        total_words_processed=total_words_processed+1
        # words that start with certain characters/strings should be treated as if this character/string is not there
        # this is to address footnotes and some other special cases
        newword=word.strip()
        newword=prune_prefix(newword)
        newword=prune_suffix(newword)
        if len(newword) > 0:
            if newword.count('\n') > 0:
                newwords=newword.split('\n')
                for w in newwords:
                    unique_words.add(w)
                    check_spelling_errors(w, None)
            else:
                unique_words.add(newword)
                check_spelling_errors(newword, None)

def main():
    global Verbose_Flag
    global unique_words
    global total_words_processed
    global all_text
    global total_raw_text

    parser = optparse.OptionParser()

    parser.add_option('-v', '--verbose',
                      dest="verbose",
                      default=False,
                      action="store_true",
                      help="Print lots of output to stdout"
    )
    parser.add_option("--config", dest="config_filename",
                      help="read configuration from FILE", metavar="FILE")
    
    parser.add_option('-a', '--all',
                      dest="keepAll",
                      default=False,
                      action="store_true",
                      help="keep all unique words without filtering"
    )

    parser.add_option('-P', '--PDF',
                      dest="processPDF_file",
                      default=False,
                      action="store_true",
                      help="Processed the named PDF file rather than a Canvas course"
    )

    options, remainder = parser.parse_args()

    Verbose_Flag=options.verbose
    if Verbose_Flag:
        print("ARGV      : {}".format(sys.argv[1:]))
        print("VERBOSE   : {}".format(options.verbose))
        print("REMAINING : {}".format(remainder))
        print("Configuration file : {}".format(options.config_filename))

    initialize(options)

    if (len(remainder) < 1):
        print("Insuffient arguments\n must provide course_id or file_name\n")
    else:
        total_words_processed=0
        unique_words=set()
        number_of_unique_words_output=0
        filtered_unique_words=set()
        skipped_words=set()
        all_text=list()
        total_raw_text=''
        
        if options.processPDF_file:
            input_PDF_file=remainder[0]
        else:
            course_id=remainder[0]
            if not str(course_id).isdigit():
                print("Error in course_id")
                return
            # skip index pages, for example:
            if course_id == 41493:
                pages_to_skip=['index-for-course', 'with-quick-index', 'examples-of-some-titles-from-previous-p1p2-reports']
            elif course_id == 31168:
                pages_to_skip=['top-level-index-of-foreign-terms-with-figure-and-table-captions', 'index-special-and-a-r', 'index-r-z']
            else:
                pages_to_skip=[]

        
        if options.processPDF_file:
            unique_words_in_PDF_file(input_PDF_file)
            course_id=input_PDF_file         #  just a place holder course_id
        else:
            unique_words_for_pages_in_course(course_id, pages_to_skip)

        print(f'a total of {total_words_processed} words processed')
        print(f'{len(unique_words)} unique words')
        if len(unique_words) > 0:
            new_file_name='unique_words-for-course-'+str(course_id)+'.txt'

            # if not filtering, simply output the unique words and exit
            if options.keepAll:
                with open(new_file_name, 'w') as f:
                    f.write(f"{word}\n")
                return

            # reduce unique_words to have only one entry when there is both a capitalized version and a lower case version
            # Note that this may eliminate capitalized names if the same string occurs for an uncapitalized version of the string.
            new_unique_words=set()
            for word in unique_words:
                # Put all upper case acronyms in unique_words
                if word.isupper():
                    new_unique_words.add(word)
                elif is_multiple_caps(word):
                    new_unique_words.add(word)
                elif (word.capitalize() in unique_words) and (word.lower() in unique_words):
                    new_unique_words.add(word.lower())
                else:
                    new_unique_words.add(word)
                    
            unique_words=new_unique_words
            new_unique_words=set()
            # when a word ends with a "=" (probably due to the tokenization), only include the word without the trailing "="
            for word in unique_words:
                if word.endswith('=') and (word in unique_words):
                    new_unique_words.add(word[:-1])
                else:
                    new_unique_words.add(word)

            unique_words=new_unique_words
            new_unique_words=set()
            # when a word ends with a "." (probably due to the tokenization), only include the word without the trailing "."
            for word in unique_words:
                if word.endswith('.'):
                    if word[0].isupper() or word in abbreviations_ending_in_period:
                        new_unique_words.add(word)
                    elif ismixed(word):
                        new_unique_words.add(word)
                    else:
                        if word[:-1].lower() in unique_words:
                            continue
                        else:
                            new_unique_words.add(word[:-1])
                elif word+'.' in abbreviations_ending_in_period:
                        new_unique_words.add(word+'.')
                else:
                    new_unique_words.add(word)

            unique_words=new_unique_words

            # otherwise, output the filtered list of words
            with open(new_file_name, 'w') as f:
                for word in unique_words:
                    # skip slide numbers
                    if is_slide_number(word):
                        continue
                        
                    # ignore a specified set of words
                    if word in words_to_ignore:
                        continue

                    # eliminate what is left of URLs
                    if word.startswith("//"):
                        continue

                    # skip a variety of file names
                    if is_filename_to_skip(word):
                        continue

                    # skip currency ammounts
                    if len(word) > 1 and word[0] in currency_symbols:
                        continue

                    # skip things that look like DOIs
                    if is_DOI(word):
                        continue

                    # skip things that look like ISBNs
                    if is_ISBN(word):
                        continue

                    # if there is one hyphen it might be an integer range or ISSN, of so ignore it
                    if is_integer_range_or_ISSN(word):
                        continue

                    # ignore things that look like IPv4 dotted decimal addresses
                    if is_IPv4_dotted_decimal(word):
                        continue

                    # ignore IPv4 address with a specified prefix length
                    if is_IPv4_dotted_decimal_with_prefix_length(word):
                        continue

                    # ignore IPv6 addresses
                    if is_IPv6_address(word):
                        continue

                    # ignore things that look like phone numbers
                    if is_phone_number(word):
                        continue

                    # ignore things that look like time offsets, i.e., dd:dd:dd
                    if is_time_offset(word):
                        continue

                    # ignore start and end time strings
                    if is_start_end_time(word):
                        continue

                    # ignore YYYY.MM.DD and YYYY-MM-DD strings
                    if is_YYYY_MM_DD(word):
                        continue

                    # ignore  DD-MMM-YYYY or DD-MMM-YY strings
                    if is_DD_MMM_YYYY(word):
                        continue

                    # ignore date time stamps
                    if is_date_time_string(word):
                        continue

                    # ignore words with a single colon in a set of digits
                    if is_colon_range_or_HH_colon_MM(word):
                        continue

                    # ignore approximate numbers
                    if approximate_number(word):
                        continue
                    
                    # ignore numbers with commas in them
                    if is_number_with_commas(word):
                        continue

                    # ignore fractions
                    if is_fraction(word):
                        continue

                    # ignore hex numbers
                    if is_hex_number(word):
                        continue

                    # ignore things that look like MAC addresses
                    if is_MAC_address(word):
                        continue

                    # ignore things that look like single numbers (also ignore numbers with string, such as units, after them)
                    if is_number(word):
                        continue

                    # ignore DiVA identifiers
                    if is_part_of_DiVA_identifier(word):
                        continue

                    # ignore TRITA numbers
                    if is_TRITA_identifier(word):
                        continue

                    # ignore arXiv identifiers
                    if is_part_of_arXiv_identifier(word):
                        continue

                    # ignore spring links
                    if is_part_of_springerlink_identifier(word):
                        continue

                    # finally output the remaining word
                    f.write(f"{word}\n")
                    filtered_unique_words.add(word)

                    number_of_unique_words_output=number_of_unique_words_output+1

            print(f'{number_of_unique_words_output} unique words output to {new_file_name}')

        # check type of filtered_unique_words
        print(f'{len(filtered_unique_words)} filtered_unique_words')

        # compute word frequency for the filtered unique words
        frequency=dict()
        for count, word in enumerate(all_text):
            #print(f'{word=}')
            if word in filtered_unique_words:
                current_word_frequency=frequency.get(word, 0)
                frequency[word]=current_word_frequency+1
            else:
                skipped_words.add(word)

        frequency_sorted=dict(sorted(frequency.items(), key=lambda x:x[1]))

        new_file_name='unique_words-for-course-frequency-'+str(course_id)+'.txt'        
        with open(new_file_name, 'w') as f:
            f.write(json.dumps(frequency_sorted))

        new_file_name='unique_words-for-course-skipped-'+str(course_id)+'.txt'        
        with open(new_file_name, 'w') as f:
            for word in skipped_words:
                f.write(f"{word}\n")

        # save all the raw text
        new_file_name='unique_words-for-course-raw_text-'+str(course_id)+'.txt'        
        with open(new_file_name, 'w') as f:
            f.write(total_raw_text)



if __name__ == "__main__": main()