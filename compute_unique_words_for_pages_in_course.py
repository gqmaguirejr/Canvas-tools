#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# ./compute_unique_words_for_pages_in_course.py  course_id
# 
# The content is taken from the wikipages in the specified course or from PDF files that have been retried ffrom the course.
#
# it outputs a file with the unique words each on a line
# where xx is the course_id.
#
# It also outputs others files, such as one with the raw text from all the wikipages.
# The pages are separated with lines, such as:
# ⌘⏩routing-table-search-classless⏪
# where the page URL is between the markers. This makes it easy to look at the source material, for example when tryign to locate misspellings.
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
# To process the wikipages:
#
# ./compute_unique_words_for_pages_in_course.py 11544
#
# ./compute_unique_words_for_pages_in_course.py  --config config-test.json 11544
#
# To process the files from a course:
## The option --dir can be used to specify a directory to be used to get the input tiles and to put the output files in.
# There is also a -P options to process a PDF file.
# ./compute_unique_words_for_pages_in_course.py --dir ./Internetworking_course/ -P Lecture1-notes-2019.pdf
#
# For example when procesing the PDF files retrieved from a course:
#  ./compute_unique_words_for_pages_in_course.py 41668 --ligature --dir "./Course_41668/course files/Uploaded Media/" -P F01.pdf
# will output:
# Process a PDF file
# found ligrature ﬀ replacing with ff
# found ligrature ﬁ replacing with fi
# found ligrature ﬂ replacing with fl
# found ligrature ﬀ replacing with ff
# found ligrature ﬁ replacing with fi
# found ligrature ﬂ replacing with fl
# a total of 1588 words processed
# 559 unique words
# 484 unique words output to ./Course_41668/course files/Uploaded Media/unique_words-for-course-41668_F01.pdf.txt
# 484 filtered_unique_words
# output ./Course_41668/course files/Uploaded Media/unique_words-for-course-frequency-41668_F01.pdf.txt
#
# It also generates the following additional files:
#  unique_words-for-course-41668_F01.pdf.txt
#  unique_words-for-course-raw_text-41668_F01.pdf.txt
#  unique_words-for-course-skipped-41668_F01.pdf.txt
#
#
# Notes
# The program is processing the text of Canvas wikipages (it get the HTML content, but simply extracts all of the text).
# It should probably be changed to be smarter - for example, to utilize the langugage tagged parts of the page to use the correct auxiliary information.
#
# To have the correct version of PDFminer, do:
#     pip install pdfminer.six
#

import csv, requests, time
from pprint import pprint
import optparse
import sys

import json
import re

from types import FunctionType
from inspect import getmembers

def api(obj):
    return [name for name in dir(obj) if name[0] != '_']

def attrs(obj):
    disallowed_properties = {
        name for name, value in getmembers(type(obj)) 
        if isinstance(value, (property, FunctionType))
    }
    return {
        name: getattr(obj, name) for name in api(obj) 
        if name not in disallowed_properties and hasattr(obj, name)
    }

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

# note that caseless comparison on unicode characters or strings requires some gymnastics (see https://docs.python.org/3/howto/unicode.html)
import unicodedata

def compare_caseless(s1, s2):
    def NFD(s):
        return unicodedata.normalize('NFD', s)

    return NFD(NFD(s1).casefold()) == NFD(NFD(s2).casefold())

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
    "′", # prime
    '+',
    ',',
    '-',
    '.',
    './',
    '0xFE0E',  # this is Variation Selector-15 - it modifies the character before it, but will end up at the start of the word after it
    ':',
    '=',
    '\\u0000', # remove the string \u0000 which is the null characters
    '\u034f', # graphics joiner - non spacing mark
    '\u03bb',
    '\u200b', #Zero Width Space
    '\ud835\udc36', # MATHEMATICAL ITALIC CAPITAL C'
    '^',
    '_.',
    '|',
    '~',
    '¡',
    '§',
    'µ',
    '¼',
    '¿',
    '×',
    'Þ',
    'ˆ',
    'α',
    'μ',
    'χ',
    '‒',
    '–',
    '—',
    '―',
    '„',
    '†',
    '‡',
    '•',
    '‣',
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
    '✓',  # 0x2713
    '✔',  # 0x2714
    '✝',
    '❌',
    '〃',
    '',
    '',
    '',
    '（',
    '👋',
]

suffixes_to_ignore=[
    "'",
    "§",
    #',
    '-',
    '.',
    '/',
    '\\',
    '\\n',
    '_',
    '¢',
    '®',
    '°',
    '¶',
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
    '✷',
    '',
    '',
    '',
    '',
    '\u0000', # null character
]

miss_spelled_words=[
    #"algorithm|s",
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

# remove all prefixes
def prune_prefix(s):
    for pfx in prefixes_to_ignore:
        if s.startswith(pfx):
            s=s[len(pfx):]
    return s

# remove all suffixes
def prune_suffix(s):
    for sfx in suffixes_to_ignore:
        if s.endswith(sfx):
            s=s[:-len(sfx)]
    return s

def uniqe_words_from_rawtext(raw_text):
    global Verbose_Flag
    global total_words_processed
    global unique_words

    words = nltk.word_tokenize(raw_text)
    all_text.extend(words)
    for word in words:
        total_words_processed=total_words_processed+1
        # words that start with certain characters/strings should be treated as if this character/string is not there
        # this is to address footnotes and some other special cases
        newword=word.strip()
        newword=prune_prefix(newword)
        newword=prune_suffix(newword)
        if len(newword) > 0 and not newword == '\u200b': # eliminate a zero width space
            if newword.count('\n') > 0:
                newwords=newword.split('\n')
                for w in newwords:
                    unique_words.add(w)
            else:
                unique_words.add(newword)

    return True

def unique_words_for_pages_in_course(course_id, pages_to_skip):
    global Verbose_Flag
    global total_raw_text
    global total_raw_HTML

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

    # if Verbose_Flag:
    #     print(f'{list_of_all_pages=}')

    for p in list_of_all_pages:
        # skip unpublished pages
        if not p['published']:
            continue

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
                # save all of the bodies
                total_raw_HTML=total_raw_HTML+f"\n⌘⏩{p['url']}⏪\n"+body

                spaced_body = re.sub("</", " </", body)
                document = html.document_fromstring(spaced_body)
                # replace the BR tags with a space
                for br in document.xpath("*//br"):
                    br.tail = " " + br.tail if br.tail else " "
                for br in document.xpath("*//BR"):
                    br.tail = " " + br.tail if br.tail else " "


                raw_text = document.text_content()
            else:               # nothing to process
                raw_text = ""
                continue

            if Verbose_Flag:
                print("raw_text: {}".format(raw_text))
            total_raw_text=total_raw_text+f"\n⌘⏩{p['url']}⏪\n"+raw_text
                
        else:
            print("No pages for course_id: {}".format(course_id))
            return False

        # to look for spectivic text on a page
        # if raw_text.find("Boyle") >= 0:
        #     print(f'Boyle on page {url}')

        if not raw_text or len(raw_text) < 1:
            print(f"nothing to processes on page {p['url']}")
            continue
        
        uniqe_words_from_rawtext(raw_text)
    return True

def unique_words_for_syllabus_in_course(course_id):
    global Verbose_Flag
    global total_raw_text
    global total_raw_HTML

    payload={}

    # Note that the syllabus is simply an HTML page
    url=f"https://canvas.kth.se/courses/{course_id}/assignments/syllabus"

    r = requests.get(url, headers = header, data=payload)
    if Verbose_Flag:
        print("r.status_code: {}".format(r.status_code))
    if r.status_code == requests.codes.ok:
        body = r.content.decode("utf-8")

    else:
        print("Error in getting syllabus for course_id: {}".format(course_id))
        return False

    if Verbose_Flag:
        print(f'body after decode utf-8: {body}')

    env_pattern = re.compile('ENV = ({.*?});', re.DOTALL)

    matches = env_pattern.search(body)

    body=matches.group(1)

    if isinstance(body, str) and len(body) > 0:
        body=body.replace('\\u003c', '\u003c')
        body=body.replace('\\u003e', '\u003e')
        body=body.replace('\\"', '"')
        body=body.replace('\\n', '\n')
        body=body.replace( "\\u0026" , "&" )


        start_of_syllabus_body='"SYLLABUS_BODY":"'
        offset_to_body=body.find(start_of_syllabus_body)
        if offset_to_body < 0:
            print('No syllabus body found')
            return False

        effective_end_of_body='","notices":[],"active_context_tab":"syllabus"'
        offset_to_end_of_body=body.find(effective_end_of_body)
        if offset_to_end_of_body < offset_to_body:
            print('No end to syllabus body found')
            return False

        body='<html>'+body[offset_to_body+len(start_of_syllabus_body):offset_to_end_of_body]+'</html>'
        #save all of the bodies
        total_raw_HTML=total_raw_HTML+f"\n⌘⏩syllabus⏪\n"+body

        
        spaced_body = re.sub("</", " </", body)
        document = html.document_fromstring(spaced_body)
        # replace the BR tags with a space
        for br in document.xpath("*//br"):
            br.tail = " " + br.tail if br.tail else " "
            for br in document.xpath("*//BR"):
                br.tail = " " + br.tail if br.tail else " "

        raw_text = document.text_content()
    else:               # nothing to process
        raw_text = ""

    if Verbose_Flag:
        print("raw_text: {}".format(raw_text))
    total_raw_text=total_raw_text+f"\n⌘⏩syllabus⏪\n"+raw_text
                
    # to look for spectivic text on a page
    # if raw_text.find("Boyle") >= 0:
    #     print(f'Boyle on page {url}')

    if not isinstance(raw_text, str) or len(raw_text) < 1:
        print(f"nothing to processes in syllabus")
        return False
        
    uniqe_words_from_rawtext(raw_text)
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
    '\r',
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
    # deal with the fact that LaTeX can set a minus sign
    if len(string) > 1 and string[0] == '\u2212':
        string = '-' + string[1:]
    #
    if len(string) > 0:
        if not (string[0] == '-' or string[0] == '+'):
            if not string[0].isdigit():
                return False
    rr = re.findall("[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?", string)
    if rr and len(rr) == 1:
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
    if (s.startswith("978-") or s.startswith("979-")) and (s.count('-') == 4 or s.count('-') == 3):
        s=s.replace("-", "")
        if s.isnumeric():
            return True
        if s[-1] =='X' and s[:-1].isnumeric():
            return True

    # ISBN-13 without additional dashes
    elif (s.startswith("978-") or s.startswith("979-")) and s[4:].count('-') == 0 and s[4:].isdigit:
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
    else:
        return False
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
    '.c',
    '.conf',
    '.csv',
    '.dat',
    '.doc',
    '.docx',
    '.dtd',
    '.ethereal',
    '.g++',
    '.gz',
    '.h',
    '.html',
    '.jpg',
    '.js',
    '.list',
    '.mods',
    '.o',
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

# look for strings of the form "slideD" where D is a number
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

# mixed case is any lower _and_ uppercase in one string
def ismixed(s):
    return any(c.islower() for c in s) and any(c.isupper() for c in s)

# cid:dd indicates a CID font identifier
def is_cid_font_identifier(string):
    global Verbose_Flag
    if string.startswith("cid:"):
        string=string[4:]
        return is_number(string)
    # otherwise
    return False

# added functions to get text from PDF files
def show_ltitem_hierarchy(o: Any, depth=0):
    """Show location and text of LTItem and all its descendants"""
    if depth == 0:
        print('element                        x1  y1  x2  y2   w     h    s    text               fontname')
        print('------------------------------ --- --- --- ---- ---- ---- ----  -----              --------')

    print(
        f'{get_indented_name(o, depth):<30.30s} '
        f'{get_optional_bbox(o)} '
        f'{get_optional_size(o)} '
        f'{get_optional_text(o)}'
        f'{get_optional_fontname(o)}'
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

def get_optional_size(o: Any) -> str:
    """Bounding box of LTItem if available, otherwise empty string"""
    if hasattr(o, 'bbox'):
        x1, y1, x2, y2 = o.bbox
        width=x2-x1
        height=y2-y1
        if hasattr(o, 'size'):
            size=o.size
            return f'{width:<4.0f} {height:<4.0f} {size:<4.0f}'
        else:
            return f'{width:<4.0f} {height:<4.0f}      '
    return '        '

def get_optional_text(o: Any) -> str:
    """Text of LTItem if available, otherwise empty string"""
    if hasattr(o, 'get_text'):
        return f'{o.get_text().strip():<20.20s}'
    return ''

def get_optional_fontname(o: Any) -> str:
    """Text of LTItem if available, otherwise empty string"""
    if hasattr(o, 'fontname'):
        return o.fontname.strip()[7:] # remove the prefix
    return ''


def process_element(o: Any, png):
    global extracted_data
    global total_raw_text
    
    last_x_offset=None
    last_x_width=None

    last_y_offset=None            # y_offset of text characters
    font_size=None                # when in doublt, the font_size is None

    if isinstance(o, LTTextBoxHorizontal):
        if isinstance(o, Iterable):
            for i in o:
                process_element(i, png)

        # for text_line in o:
        #     if hasattr(text_line, 'bbox'):
        #         last_x_offset=text_line.bbox[0]
        #         last_y_offset=text_line.bbox[1]
        #         last_x_width=text_line.bbox[2]-text_line.bbox[0]
        #     if Verbose_Flag:
        #         print(f'text_line={text_line}')
        #     if hasattr(text_line, 'size'):
        #         font_size=text_line.size
        #     else:
        #         font_size=text_line.bbox[3]-text_line.bbox[1]
        #     if isinstance(text_line, LTAnno):
        #         if Verbose_Flag:
        #             print("found an LTAnno")

        #     # if isinstance(text_line, LTChar):
        #     #     print("fount an LTChar")
        #     # elif isinstance(text_line, LTAnno):
        #     #     print("fount an LTAnno")
        #     # else:
        #     #     for character in text_line:
        #     #         if isinstance(character, LTChar):
        #     #             font_size=character.size
        # fontname=''
        # extracted_data.append([font_size, last_x_offset, last_y_offset, last_x_width, (o.get_text()), fontname, png])

    elif isinstance(o, LTTextLineHorizontal):
        if Verbose_Flag:
            print("element is LTTextLineHorizontal")
        if isinstance(o, Iterable):
            for i in o:
                process_element(i, png)

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
                font_size=text_line.bbox[3]-text_line.bbox[1]
            # if isinstance(text_line, LTChar):
            #     print("found an LTChar")
            #     font_size=text_line.size
            # elif isinstance(text_line, LTAnno):
            #     print("found an LTAnno")
            # else:
            #     for character in text_line:
            #         if isinstance(character, LTChar):
            #             font_size=character.size
        font_name=''
        extracted_data.append([font_size, last_x_offset, last_y_offset, last_x_width, (o.get_text()), font_name, png])
    elif isinstance(o, LTLine): #  a line
        if Verbose_Flag:
            print(f'found an LTLine {o=}')
    elif isinstance(o, LTFigure):
        if isinstance(o, Iterable):
            for i in o:
                process_element(i, png)
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
        if hasattr(o, 'size'):
            font_size=o.size
        else:
            font_size=o.bbox[3]-o.bbox[1]
        if hasattr(o, 'fontname'):
            font_name=o.fontname.strip()[7:] # remove the prefix
        else:
            font_name=''
        extracted_data.append([font_size, last_x_offset, last_y_offset, last_x_width, (o.get_text()), font_name, png])
    elif isinstance(o, LTAnno):
        if Verbose_Flag:
            print(f'fount an LTAnno: {o} {o.get_text()}')
        font_name=''
        extracted_data.append([None, None, None, None, o.get_text(), font_name, png])
    elif isinstance(o, LTCurve): #  a curve
        if Verbose_Flag:
            print("found an LTCurve")
            if hasattr(o, 'bbox'):
                font_size=o.bbox[3]-o.bbox[1]
        font_name=''
        extracted_data.append([font_size, last_x_offset, last_y_offset, last_x_width, ' ', font_name, png])
    else:
        if Verbose_Flag:
            print(f'unprocessed element: {o}')
        if isinstance(o, Iterable):
            for i in o:
                process_element(i, png)

def rough_comparison(a, b):
    if not a or not b:
        return False
    if abs(a-b) < 0.1:
        return True
    return False

def rough_comparison_with_tolerance(a, b, tolerance):
    if not a or not b:
        return False
    if abs(a-b) < tolerance:
        return True
    return False


def add_diaeresis(txt):
    c=txt[0]
    if c == 'a':
        new_c='ä'
    elif c == 'A':
        new_c='Ä'
    elif c == 'e':
        new_c='ê'
    elif c == 'E':
        new_c='Ê'
    elif c == 'h':
        new_c='ḧ'
    elif c == 'H':
        new_c='Ḧ'
    elif (c == 'i') or  (c == 'ı'): # have to consider it might be a dotless "i"
        new_c='ï'
    elif c == 'I':
        new_c='Ï'
    elif c == 'o':
        new_c='ö'
    elif c == 'O':
        new_c='Ö'
    elif c == 't':
        new_c='ẗ'
    elif c == 'T':
        new_c='T̈'
    elif c == 'u':
        new_c='ü'
    elif c == 'U':
        new_c='Ü'
    elif c == 'w':
        new_c='ẅ'
    elif c == 'W':
        new_c='Ẅ'
    elif c == 'x':
        new_c='ẍ'
    elif c == 'X':
        new_c='Ẍ'
    elif c == 'y':
        new_c='ÿ'
    elif c == 'Y':
        new_c='Ÿ'
    elif c == '‐':              # hyphen and hyphen with Hyphen with Diaeresis
        new_c='⸚'
    else:                       # just replace it by itself - if you have no replacement
        new_c=c
    if len(txt) == 1:
        return new_c
    return new_c+txt[1:]


def add_ring(txt):
    c=txt[0]
    if c == 'a':
        new_c='å'
    elif c == 'A':
        new_c='Å'
    elif c == 'u':
        new_c='ů'
    elif c == 'U':
        new_c='Ů'
    elif c == 'y':
        new_c='ẙ'
    elif c == 'y':
        new_c='Y̊'
    else:                       # just replace it by itself - if you have no replacement
        new_c=c
    if len(txt) > 1:
        return new_c+txt[1:]
    return new_c

def add_acute_accent(txt):
    c=txt[0]
    if c == 'a':
        new_c='á'
    elif c == 'A':
        new_c='Á'
    elif c == 'c':
        new_c='ć'
    elif c == 'C':
        new_c='Ć'
    elif c == 'e':
        new_c='é'
    elif c == 'E':
        new_c='É'
    elif c == 'g':
        new_c='ǵ'
    elif c == 'G':
        new_c='Ǵ'
    elif (c == 'i') or  (c == 'ı'):
        new_c='í'
    elif c == 'I':
        new_c='Í'
    elif c == 'k':
        new_c='ḱ'
    elif c == 'K':
        new_c='Ḱ'
    elif c == 'l':
        new_c='ĺ'
    elif c == 'L':
        new_c='Ĺ'
    elif c == 'm':
        new_c='ḿ'
    elif c == 'M':
        new_c='Ḿ'
    elif c == 'n':
        new_c='ń'
    elif c == 'N':
        new_c='Ń'
    elif c == 'o':
        new_c='ó'
    elif c == 'O':
        new_c='Ó'
    elif c == 'p':
        new_c='ṕ'
    elif c == 'P':
        new_c='Ṕ'
    elif c == 'r':
        new_c='ŕ'
    elif c == 'R':
        new_c='Ŕ'
    elif c == 's':
        new_c='ś'
    elif c == 'S':
        new_c='Ś'
    elif c == 'u':
        new_c='ú'
    elif c == 'U':
        new_c='Ú'
    elif c == 'w':
        new_c='ẃ'
    elif c == 'W':
        new_c='Ẃ'
    elif c == 'y':
        new_c='ý'
    elif c == 'Y':
        new_c='Ý'
    elif c == 'z':
        new_c='ź'
    elif c == 'Z':
        new_c='Ź'
    else:                       # just replace it by itself - if you have no replacement
        new_c=c
    if len(txt) == 1:
        return new_c
    return new_c+txt[1:]

def add_grave_accent(txt):
    c=txt[0]
    if c == 'a':
        new_c='à'
    elif c == 'A':
        new_c='À'
    elif c == 'e':
        new_c='è'
    elif c == 'E':
        new_c='È'
    elif (c == 'i') or  (c == 'ı'):
        new_c='ì'
    elif c == 'I':
        new_c='Ì'
    elif c == 'n':
        new_c='ǹ'
    elif c == 'N':
        new_c='Ǹ'
    elif c == 'o':
        new_c='ò'
    elif c == 'O':
        new_c='Ò'
    elif c == 'u':
        new_c='ù'
    elif c == 'U':
        new_c='Ù'
    elif c == 'w':
        new_c='ẁ'
    elif c == 'W':
        new_c='Ẁ'
    elif c == 'y':
        new_c='ỳ'               # from "Latin Extended Additional"
    elif c == 'Y':
        new_c='Ỳ'		# from "Latin Extended Additional"
    else:                       # just replace it by itself - if you have no replacement
        new_c=c
    if len(txt) == 1:
        return new_c
    return new_c+txt[1:]



def add_circumflex_accent(txt):
    c=txt[0]
    if c == 'a':
        new_c='â'
    elif c == 'A':
        new_c='Â'
    elif c == 'c':
        new_c='ĉ'
    elif c == 'C':
        new_c='Ĉ'
    elif c == 'e':
        new_c='ê'
    elif c == 'E':
        new_c='Ê'
    elif c == 'g':
        new_c='ĝ'
    elif c == 'G':
        new_c='Ĝ'
    elif c == 'h':
        new_c='ĥ'
    elif c == 'H':
        new_c='Ĥ'
    elif (c == 'i') or  (c == 'ı'):
        new_c='î'
    elif c == 'I':
        new_c='Î'
    elif (c == 'j') or  (c == 'ȷ'):
        new_c='ĵ'
    elif (c == 'j'):
        new_c='Ĵ'
    elif c == 'o':
        new_c='ô'
    elif c == 'O':
        new_c='Ô'
    elif c == 's':
        new_c='ŝ'
    elif c == 'S':
        new_c='Ŝ'
    elif c == 'u':
        new_c='û'
    elif c == 'U':
        new_c='Û'
    elif c == 'w':
        new_c='ŵ'
    elif c == 'W':
        new_c='Ŵ'
    elif c == 'y':
        new_c='ŷ'               # from "Latin Extended Additional"
    elif c == 'Y':
        new_c='Ŷ'		# from "Latin Extended Additional"
    elif c == 'z':
        new_c='ẑ'
    elif c == 'Z':
        new_c='Ẑ'
    else:                       # just replace it by itself - if you have no replacement
        new_c=c
    if len(txt) == 1:
        return new_c
    return new_c+txt[1:]

def add_breve(txt):
    c=txt[0]
    if c == 'a':
        new_c='ă'
    elif c == 'A':
        new_c='Ă'
    elif c == 'e':
        new_c='ĕ'
    elif c == 'E':
        new_c='Ĕ'
    elif c == 'g':
        new_c='ğ'
    elif c == 'G':
        new_c='Ğ'
    elif (c == 'i') or  (c == 'ı'):
        new_c='ĭ'
    elif c == 'I':
        new_c='Ĭ'
    elif c == 'o':
        new_c='ŏ'
    elif c == 'O':
        new_c='Ŏ'
    elif c == 'u':
        new_c='ŭ'
    elif c == 'U':
        new_c='Ŭ'
    else:                       # just replace it by itself - if you have no replacement
        new_c=c
    if len(txt) == 1:
        return new_c
    return new_c+txt[1:]

def add_inverted_breve(txt):
    c=txt[0]
    if c == 'a':
        new_c='ȃ'
    elif c == 'A':
        new_c='Ȃ'
    elif c == 'e':
        new_c='ȇ'
    elif c == 'E':
        new_c='Ȇ'
    elif (c == 'i') or  (c == 'ı'):
        new_c='ȋ'
    elif c == 'I':
        new_c='Ȋ'
    elif c == 'o':
        new_c='ȏ'
    elif c == 'O':
        new_c='Ȏ'
    elif c == 'r':
        new_c='ȓ'
    elif c == 'R':
        new_c='Ȓ'
    elif c == 'u':
        new_c='ȗ'
    elif c == 'U':
        new_c='Ȗ'
    else:                       # just replace it by itself - if you have no replacement
        new_c=c
    if len(txt) == 1:
        return new_c
    return new_c+txt[1:]


def add_macron(txt):
    c=txt[0]
    if c == 'a':
        new_c='ā'
    elif c == 'A':
        new_c='Ā'
    elif c == 'e':
        new_c='ē'
    elif c == 'E':
        new_c='Ē'
    elif c == 'g':
        new_c='ḡ'
    elif c == 'G':
        new_c='Ḡ'
    elif (c == 'i') or  (c == 'i'):
        new_c='ī'
    elif c == 'i':
        new_c='Ī'
    elif c == 'o':
        new_c='ō'
    elif c == 'O':
        new_c='Ō'
    elif c == 'u':
        new_c='ū'
    elif c == 'U':
        new_c='Ū'
    elif c == 'y':
        new_c='ȳ'
    elif c == 'Y':
        new_c='Ȳ'
    elif c == 'α':              # Greek alpha
        new_c='ᾱ'               # Greek Small Letter Alpha with Macron from "Greek Extended"
    elif c == 'Α':              # Greek Alpha
        new_c='Ᾱ'               # Greek Capital Letter Alpha with Macron from "Greek Extended"
    elif c == 'ι':              # Greek Iota
        new_c='ῑ'               # Greek Small Letter Iota with Macron from "Greek Extended"
    elif c == 'Ι':              # Greek Iota
        new_c='Ῑ'               # Greek Capital Letter Iota with Macron from "Greek Extended"
    elif c == 'υ':              # Greek upsilon 
        new_c='ῡ'               # Greek Small Letter Upsilon with Macron from "Greek Extended"
    elif c == 'Υ':              # Greek Upsilon
        new_c='Ῡ'               # Greek Capital Letter Upsilon with Macron from "Greek Extended"
    else:                       # just replace it by itself - if you have no replacement
        new_c=c
    if len(txt) == 1:
        return new_c
    return new_c+txt[1:]

def add_tilde(txt):
    c=txt[0]
    if c == 'a':
        new_c='ã'
    elif c == 'A':
        new_c='Ã'
    elif c == 'e':
        new_c='ẽ'
    elif c == 'E':
        new_c='Ẽ'
    elif (c == 'i') or  (c == 'ı'):
        new_c='ĩ'
    elif c == 'I':
        new_c='Ĩ'
    elif c == 'n':
        new_c='ñ'
    elif c == 'N':
        new_c='Ñ'
    elif c == 'o':
        new_c='õ'
    elif c == 'O':
        new_c='Õ'
    elif c == 'u':
        new_c='ũ'
    elif c == 'Ũ':
        new_c='Û'
    elif c == 'v':
        new_c='ṽ'
    elif c == 'V':
        new_c='Ṽ'
    elif c == 'y':
        new_c='ỹ'               # from "Latin Extended Additional"
    elif c == 'Y':
        new_c='Ỹ'		# from "Latin Extended Additional"
    else:                       # just replace it by itself - if you have no replacement
        new_c=c
    if len(txt) == 1:
        return new_c
    return new_c+txt[1:]

def add_dot_above(txt):
    c=txt[0]
    if c == 'a':
        new_c='ȧ'
    elif c == 'A':
        new_c='Ȧ'
    elif c == 'b':
        new_c='ḃ'
    elif c == 'B':
        new_c='Ḃ'
    elif c == 'c':
        new_c='ċ'
    elif c == 'C':
        new_c='Ċ'
    elif c == 'd':
        new_c='ḋ'
    elif c == 'D':
        new_c='Ḋ'
    elif c == 'e':
        new_c='ė'
    elif c == 'E':
        new_c='Ė'
    elif c == 'f':
        new_c='ḟ'
    elif c == 'F':
        new_c='Ḟ'
    elif c == 'g':
        new_c='ġ'
    elif c == 'G':
        new_c='Ġ'
    elif c == 'h':
        new_c='ḣ'
    elif c == 'H':
        new_c='Ḣ'
    # elif (c == 'i') or  (c == 'ı'):
    #     new_c=''
    elif c == 'I':
        new_c='İ'
    elif c == 'm':
        new_c='ṁ'
    elif c == 'M':
        new_c='Ṁ'
    elif c == 'n':
        new_c='ṅ'
    elif c == 'N':
        new_c='Ṅ'
    elif c == 'o':
        new_c='ȯ'
    elif c == 'O':
        new_c='Ȯ'
    elif c == 'p':
        new_c='ṗ'
    elif c == 'P':
        new_c='Ṗ'
    elif c == 'r':
        new_c='ṙ'
    elif c == 'R':
        new_c='Ṙ'
    elif c == 's':
        new_c='ṡ'
    elif c == 'S':
        new_c='Ṡ'
    elif c == 't':
        new_c='ṫ'
    elif c == 'T':
        new_c='Ṫ'
    elif c == 'u':
        new_c='ụ'
    elif c == 'Ũ':
        new_c='Ụ'
    elif c == 'w':
        new_c='ẇ'
    elif c == 'W':
        new_c='Ẇ'
    elif c == 'x':
        new_c='ẋ'
    elif c == 'X':
        new_c='Ẋ'
    elif c == 'y':
        new_c='ẏ'
    elif c == 'Y':
        new_c='Ẏ'
    elif c == 'z':
        new_c='ż'
    elif c == 'Z':
        new_c='Ż'
    else:                       # just replace it by itself - if you have no replacement
        new_c=c
    if len(txt) == 1:
        return new_c
    return new_c+txt[1:]

def add_cedilla(txt):
    c=txt[0]
    if c == 'c':
        new_c='ç'
    elif c == 'C':
        new_c='Ç'
    elif c == 'd':
        new_c='ḑ'
    elif c == 'D':
        new_c='Ḑ'
    elif c == 'e':
        new_c='ȩ'
    elif c == 'E':
        new_c='Ȩ'
    elif c == 'g':
        new_c='ģ'
    elif c == 'G':
        new_c='Ģ'
    elif c == 'h':
        new_c='ḩ'
    elif c == 'H':
        new_c='Ḩ'
    elif c == 'k':
        new_c='ķ'
    elif c == 'K':
        new_c='Ķ'
    elif c == 'l':
        new_c='ļ'
    elif c == 'L':
        new_c='Ļ'
    elif c == 'n':
        new_c='ņ'
    elif c == 'N':
        new_c='Ņ'
    elif c == 'r':
        new_c='ŗ'
    elif c == 'R':
        new_c='Ŗ'
    elif c == 's':
        new_c='ş'
    elif c == 'S':
        new_c='Ş'
    elif c == 't':
        new_c='ţ'
    elif c == 'T':
        new_c='Ţ'
    else:                       # just replace it by itself - if you have no replacement
        new_c=c
    if len(txt) == 1:
        return new_c
    return new_c+txt[1:]

def add_hacek_caron(txt):
    c=txt[0]
    if c == 'a':
        new_c='ǎ'
    elif c == 'A':
        new_c='Ǎ'
    elif c == 'c':
        new_c='č'
    elif c == 'C':
        new_c='Č'
    elif c == 'd':
        new_c='ď'
    elif c == 'D':
        new_c='Ď'
    elif c == 'e':
        new_c='ě'
    elif c == 'E':
        new_c='Ě'
    elif c == 'g':
        new_c='ǧ'
    elif c == 'G':
        new_c='Ǧ'
    elif c == 'h':
        new_c='ȟ'
    elif c == 'H':
        new_c='Ȟ'
    elif (c == 'i') or  (c == 'ı'):
        new_c='ǐ'
    elif c == 'I':
        new_c='Ǐ'
    elif (c == 'j') or  (c == 'ȷ'):
        new_c='ǰ'
    elif c == 'k':
        new_c='ǩ'
    elif c == 'K':
        new_c='Ǩ'
    elif c == 'l':
        new_c='ľ'
    elif c == 'L':
        new_c='Ľ'
    elif c == 'n':
        new_c='ň'
    elif c == 'N':
        new_c='Ň'
    elif c == 'o':
        new_c='ǒ'
    elif c == 'O':
        new_c='Ǒ'
    elif c == 'r':
        new_c='ř'
    elif c == 'R':
        new_c='Ř'
    elif c == 's':
        new_c='š'
    elif c == 'S':
        new_c='Š'
    elif c == 't':
        new_c='ť'
    elif c == 'T':
        new_c='Ť'
    elif c == 'u':
        new_c='ǔ'
    elif c == 'U':
        new_c='Ǔ'
    elif c == 'z':
        new_c='ž'
    elif c == 'Z':
        new_c='Ž'
    else:                       # just replace it by itself - if you have no replacement
        new_c=c
    if len(txt) == 1:
        return new_c
    return new_c+txt[1:]

def add_double_acute_accent(txt):
    c=txt[0]
    if c == 'a':
        new_c='a̋'
    elif c == 'A':
        new_c='A̋'
    elif c == 'c':
        new_c='c̋'
    elif c == 'C':
        new_c='C̋'
    elif c == 'e':
        new_c='e̋'
    elif c == 'E':
        new_c='E̋'
    elif c == 'g':
        new_c='g̋'
    elif c == 'G':
        new_c='G̋'
    elif (c == 'i') or  (c == 'ı'):
        new_c='i̋'
    elif c == 'I':
        new_c='I̋'
    elif (c == 'j') or  (c == 'ȷ'):
        new_c=' j̋'
    elif c == 'J':
        new_c=' J̋'
    elif c == 'm':
        new_c='m̋'
    elif c == 'M':
        new_c='M̋'
    elif c == 'o':
        new_c='ő'
    elif c == 'O':
        new_c='Ő'
    elif c == 'u':
        new_c='ű'
    elif c == 'U':
        new_c='Ű'
    elif c == 'ү': # Cyrillic
        new_c='ӳ'
    elif c == 'Ү':
        new_c='Ӳ'
    else:                       # just replace it by itself - if you have no replacement
        new_c=c
    if len(txt) == 1:
        return new_c
    return new_c+txt[1:]
    
# for vectors
# note that the combing character has to come after the base character
def add_right_arrow_above(txt):
    c=txt[0]
    new_c=c+'\u20D7'             # Combining Right Arrow Above from "Combining Diacritical Marks for Symbols"
    if len(txt) == 1:
        return new_c
    return new_c+txt[1:]
    
def add_low_line(txt):
    c=txt[0]
    new_c=c+'\u0332'             # Combining Low Line (0x0332) from Combining Diacritical Marks
    if len(txt) == 1:
        return new_c
    return new_c+txt[1:]


def transform_txt(last_txt, txt, delta_y):
    print(f'transform_txt("{last_txt}", "{txt}", {delta_y})')

    # if character followed by a cedilla chracter, swap last_txt and txt
    if txt in ["¸"]:
        tmp=txt
        txt=last_txt
        last_txt=tmp
    if last_txt is None:
        return txt


    incoming_txt=txt
    last_txt=last_txt.strip()
    if last_txt == '¨':         # Diaeresis from "Latin-1 Supplement"
        txt=add_diaeresis(txt)
    elif last_txt == '˚':       # Ring Above from "Spacing Modifier Letters"
        txt=add_ring(txt)
    elif last_txt == '¯':       # Macron from "Latin-1 Supplement"
        txt=add_macron(txt)
    elif last_txt in ["ˊ", "´"]: # Modifier Letter Acute Accent from "Spacing Modifier Letters", Accute Accent from "Latin-1 Supplement"
        txt=add_acute_accent(txt)
    elif last_txt in ["ˋ", "`"]: # Modifier Letter Acute Accent from "Spacing Modifier Letters", Grave Accent from "Basic Latin"
        txt=add_grave_accent(txt)
    elif last_txt in ["ˆ", "^"]: # Modifier Letter Circumflex Accent from "Spacing Modifier Letters", Circumflex Accent from "Basic Latin"
        txt=add_circumflex_accent(txt)
    elif last_txt in ["˜", "~"]: # Small Tilde from "Spacing Modifier Letters", Tilde from "Basic Latin"
        txt=add_tilde(txt)
    elif last_txt in ["˘"]: # Breve from "Spacing Modifier Letters"
        txt=add_breve(txt)
    elif last_txt in ["⁀"]: # Character Tie from "General Punctuation" -- CHECK if this is what the PDF generator uses
        txt=add_inverted_breve(txt)
    elif last_txt in ["˙"]:     # Dot Above (0x02D9) from "Spacing Modifier Letters"
        txt=add_dot_above(txt)
    elif last_txt in ["¸"]: # note that the character cedilla (0xB8) has been used and not the Combining Cedilla (0x0327) from "Combining Diacritical Marks"
        txt=add_cedilla(txt)
    elif last_txt in ["ˇ"]: # Caron (0x02c7) from "Spacing Modifier Letters"
        txt=add_hacek_caron(txt)
    elif last_txt in ["˝"]: # Double Acute Accent (0x02DD) from "Spacing Modifier Letters"
        txt=add_double_acute_accent(txt)
    elif last_txt in ["̲"]: # Combining Low Line (0x0332) from "Combining Diacritical Marks"
        print(f'low line case: {last_txt} and {txt} and incoming: {incoming_txt}')
        txt=add_low_line(txt)
    elif last_txt in ["⃗"]: # Combining Right Arrow Above (0x20D7) from "Combining Diacritical Marks for Symbols"
        print(f'right arrow case: {last_txt} and {txt} and incoming: {incoming_txt}')
        txt=add_right_arrow_above(txt)
    else:
        print(f'unhandled case in transform_txt({last_txt}, {txt})')
        txt=f'{last_txt}{txt}'

    print(f'{last_txt}, {incoming_txt} -> {txt}')
    return txt

overlap_threshold=0.01

def overlap_q(last_current_x_offset, last_current_x_width, last_txt, last_png, current_x_offset, current_x_width, txt, png):
    if not (png == last_png):   # text on different pages cannot overlap
        return False
    if last_current_x_width is None:
        return False
    if abs(last_current_x_offset-current_x_offset) < overlap_threshold and abs(last_current_x_width-current_x_width) < overlap_threshold and last_txt == txt:
        return False            #  it is the same txt
    if last_current_x_offset <= current_x_offset:
        if last_current_x_offset + last_current_x_width <= current_x_offset: #  case 0a: no overlap
            return False
    if last_current_x_offset > current_x_offset:
        if last_current_x_offset >= current_x_offset + current_x_width: #  case 0b: no overlap
            return False
    return True


def combine_txt(last_txt, txt):
    print(f'combine_txt("{last_txt}", "{txt}")')
    return last_txt+txt
            
def combine_at_same_position(last_txt, txt, delta_y):
    print(f'combine_at_same_position("{last_txt}", "{txt}", "{delta_y}")')
    return transform_txt(last_txt, txt, delta_y)

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
        pgn=0
        for page in extract_pages(filename):
            pgn=pgn+1
            if Verbose_Flag:
                print('showing show_ltitem_hierarchy')
                show_ltitem_hierarchy(page)

            if Verbose_Flag:
                print(f'{page=}')
            for element in page:
                if Verbose_Flag:
                    print(f'{element=}')
                process_element(element, pgn)

    except (PDFNoValidXRef, PSEOF, pdfminer.pdfdocument.PDFNoValidXRef, pdfminer.psparser.PSEOF) as e:
        print(f'Unexpected error in processing the PDF file: {filename} with error {e}')
        return False
    except Exception as e:
        print(f'Error in PDF extractor: {e}')
        return False

            
    if Verbose_Flag:
        print("extracted_data: {}".format(extracted_data))
    # Example of overlapping characters:
    # extracted_data:
    # overlapping:
    #   [9.962600000000009, 398.67459937999996, 125.26025559999974, 7.33346985999998, 'R', 1],
    #   [9.962600000000009, 400.13013523999996, 125.26025559999974, 4.4273794399999815, '¸', 1],
    #   [None, None, None, None, ' ', 1],
    # non overlapping:
    #   [9.962600000000009, 406.0120542799999, 125.26025559999974, 4.981299999999976, 'a', 1],
    #   [9.962600000000009, 410.9933542799999, 125.26025559999974, 5.5352205600000275, 'b', 1],
    # [None, None, None, None, ' ', 1],

    #
    # look for overlapping characters
    #
    if Verbose_Flag:
        print('look for overlapping characters')

    last_current_x_offset=None
    last_current_y_offset=None
    last_current_x_width=None
    last_txt=None
    last_size=None
    last_png=None
    last_fontname=False

    new_extracted_data=list()
    
    for idx, item in enumerate(extracted_data):
        if isinstance(item, list):
            if len(item) == 7:
                size, current_x_offset, current_y_offset, current_x_width, txt, fontname, png = item
                if Verbose_Flag:
                    if not current_x_offset is None and not current_y_offset is None and not current_x_width is None and  not size is None and not txt is None:
                        print(f'{current_x_offset:<4.3f},{current_y_offset:<4.3f} {current_x_width:<4.3f} {size:<4.1f} "{txt}" {fontname}')
                    else:
                        print(f'{current_x_offset},{current_y_offset} {current_x_width} {size} "{txt}"')
                if current_x_width is None:
                    # an LTAnno has been reached, output last_txt
                    new_extracted_data.append([last_size, last_current_x_offset, last_current_y_offset, last_current_x_width, last_txt, last_fontname, last_png])
                    last_size=None
                    last_current_x_offset=None
                    last_current_y_offset=None
                    last_current_x_width=None
                    last_txt=None
                    last_png=png
                    last_fontname=fontname
                    continue
                
                if last_current_y_offset is None:
                    last_current_y_offset=current_y_offset
                    
                print(f'{last_current_y_offset=}')
                delta_y=last_current_y_offset-current_y_offset
                # (size * 0.1)  was 1.0, but change to 10% of font size
                if delta_y < 1.0:
                    print(f'{delta_y=}')
                    if last_current_x_offset is False:
                        print(f'last_current_x_offset is False, so just get started')
                        last_size=size
                        last_current_x_offset=current_x_offset
                        last_current_y_offset=current_y_offset
                        last_current_x_width=current_x_width
                        last_txt=txt
                        last_png=png
                        last_fontname=fontname
                        continue

                    if last_current_x_width is None:
                        last_current_x_width=current_x_width

                    print(f'{last_current_x_width=} and {rough_comparison_with_tolerance(last_current_x_offset, current_x_offset, min(last_current_x_width, current_x_width)/2.0)=}')
                    delta_x=rough_comparison_with_tolerance(last_current_x_offset, current_x_offset, min(last_current_x_width, current_x_width)/2.0)
                    print(f'{delta_x}')
                    if not last_current_x_width is None and delta_x:
                        new_txt=combine_at_same_position(last_txt, txt, delta_y)
                        new_extracted_data.append([last_size, last_current_x_offset, last_current_y_offset, last_current_x_width, new_txt, last_fontname, last_png])
                        last_size=size
                        last_current_x_offset=current_x_offset
                        last_current_y_offset=current_y_offset
                        last_current_x_width=current_x_width
                        last_txt=None # there will be nothing to output on the next character, as it has already been outputs
                        last_png=png
                        last_fontname=fontname
                        continue
                    
                    else:
                        # output the previous txt    
                        if not last_txt is None: #  If there previous txt was a combination, there is nothing to output now
                            new_extracted_data.append([last_size, last_current_x_offset, last_current_y_offset, last_current_x_width, last_txt, last_fontname, last_png])
                            #extracted_data.append([size, current_x_offset, current_y_offset, current_x_width, txt, fontname, png])
                        last_size=size
                        last_current_x_offset=current_x_offset
                        last_current_y_offset=current_y_offset
                        last_current_x_width=current_x_width
                        last_txt=txt
                        last_fontname=fontname
                        last_png=png
                else:
                    print(f'at bottom {delta_y=} was larger than 1.0')
                    # output the previous txt    
                    if not last_txt is None: #  If there previous txt was a combination, there is nothing to output now
                        new_extracted_data.append([last_size, last_current_x_offset, last_current_y_offset, last_current_x_width, last_txt, last_fontname, last_png])
                        #extracted_data.append([size, current_x_offset, current_y_offset, current_x_width, txt, fontname, png])
                    last_size=size
                    last_current_x_offset=current_x_offset
                    last_current_y_offset=current_y_offset
                    last_current_x_width=current_x_width
                    last_txt=txt
                    last_png=png
                    last_fontname=fontname

    if Verbose_Flag:
        print("New_extracted_data after dealing with overlapping characters: {}".format(new_extracted_data))

    extracted_data = new_extracted_data

    #
    # collect individual characters and build into string - adding spaces as necessary
    #
    old_size=-1
    size=None
    current_string=''
    first_x_offset=None
    last_x_offset=None
    last_x_width=None
    last_y_offset=None
    last_size=None
    new_extracted_data=[]

    for item in extracted_data:
        if isinstance(item, list):
            if len(item) == 5:
                print(f'5 unit item {item}')
                continue
            if len(item) == 7:
                size, current_x_offset, current_y_offset, current_x_width, txt, fontname, png = item
                if Verbose_Flag:
                    print(f'{current_x_offset:<4.3f},{current_y_offset:<4.3f} {size:<4.1f} "{txt}"')
                if not last_size:
                    last_size=size
                if not first_x_offset:
                    first_x_offset=current_x_offset
                if not last_y_offset:
                    last_y_offset=current_y_offset
                if rough_comparison_with_tolerance(last_y_offset, current_y_offset, size):
                    if Verbose_Flag:
                        print(f'on same line "{txt}" {current_x_offset:<4.3f} {last_x_offset} {last_x_width} {last_x_offset}')
                    if not last_x_offset:
                        if current_x_width is None or current_x_offset is None:
                            if Verbose_Flag:
                                print('processing an LTAnno')
                        else:
                            last_x_offset=current_x_offset+current_x_width
                        last_x_width=current_x_width
                        if not txt is None:
                            print(f'appending "{txt}"')
                            current_string=current_string+txt
                        if Verbose_Flag:
                            print("direct insert current_string={}".format(current_string))
                    elif not current_x_offset  is None and current_x_offset > (last_x_offset+0.250*size): # just a little faster than adjact characters
                        if Verbose_Flag:
                            print("last_x_offset+last_x_width={}".format(last_x_offset, last_x_width))
                        if not txt is None:
                            print(f'Inserting: "{txt}"')
                            current_string=current_string+' '+txt
                        if Verbose_Flag:
                            print("inserted space current_string={}".format(current_string))
                        if not current_x_width is None:
                            last_x_offset=current_x_offset+current_x_width
                        else:
                            last_x_offset=current_x_offset
                        last_x_width=current_x_width
                    else:
                        if not txt is None:
                            current_string=current_string+txt
                        if Verbose_Flag:
                            print("second direct insert current_string={}".format(current_string))
                        if not current_x_width is None:
                            last_x_offset=current_x_offset+current_x_width
                        last_x_width=current_x_width
                else:
                    if last_x_offset:
                        new_extracted_data.append([last_size, first_x_offset, last_y_offset, last_x_offset-first_x_offset, current_string+' ', fontname, png])
                    else:
                        new_extracted_data.append([last_size, first_x_offset, last_y_offset, 0.0, current_string+' ', fontname, png])
                        if Verbose_Flag:
                            print(f'current_string={current_string} and no last_x_offset')
                    if not txt is None:
                        print(f'Starting a new text string a y={current_y_offset} with "{txt}"')
                        current_string=""+txt
                    first_x_offset=current_x_offset
                    last_y_offset=current_y_offset
                    last_x_offset=current_x_offset+current_x_width
                    last_x_width=current_x_width
                    last_size=size
    
    if last_x_offset:
        new_extracted_data.append([size, first_x_offset, current_y_offset, last_x_offset-first_x_offset, current_string, fontname, png])
    else:
        if Verbose_Flag:
            print(f'current_string={current_string} and no last_x_offset')

    if Verbose_Flag:
        print("new_extracted_data={}".format(new_extracted_data))

    extracted_data=new_extracted_data

    last_size=None
    last_current_x_offset=None
    last_current_y_offset=None
    last_current_x_width=None
    last_txt=None
    last_png=None
    current_baseline=None
    
    #
    # Collect the strings and added it to raw_text
    #

    new_extracted_data=list()
    for idx, item in enumerate(extracted_data):
        if isinstance(item, list):
            if len(item) == 7:
                size, current_x_offset, current_y_offset, current_x_width, txt, fontname, png = item

                # if there is a new page number
                if last_png is None or not (last_png == png):
                    print(f'now processing page: {png}')
                    last_png=png
                    last_size=None
                    last_current_x_offset=None
                    last_current_y_offset=None
                    last_current_x_width=None
                    last_txt=None


                if Verbose_Flag:
                    print(f'{idx}: last: {last_current_x_offset},{last_current_y_offset} {last_size} {last_current_x_width} "{last_txt}"')
                    print(f'{raw_text=}')
                    print(f'{idx}: {current_x_offset:<4.3f},{current_y_offset:<4.3f} {size:<4.1f} {current_x_width:<4.3f} "{txt}" {png}')

                if current_x_width != 0:
                    # if this is the first line on a page, just add the txt
                    if last_current_y_offset is None:
                        last_current_y_offset=current_y_offset
                        current_baseline=current_y_offset

                    if last_current_x_offset is None:
                        if Verbose_Flag:
                            print(f'first line on page: {txt}')
                        raw_text = raw_text+txt.strip()
                        last_current_x_offset=current_x_offset
                    elif last_current_x_width == 0.0:
                        if Verbose_Flag:
                            print(f'{current_x_width=}')
                        delta_y=last_current_y_offset - current_y_offset
                        if Verbose_Flag:
                            print(f'after modified case: {delta_y} pt')

                        raw_text = raw_text+txt.strip()
                    else:
                        delta_y=last_current_y_offset - current_y_offset
                        if Verbose_Flag:
                            print(f'else case2: {delta_y} pt')
                        if size is None:
                            raw_text = raw_text+txt.strip()
                        elif abs(delta_y) > 0.8 * size: # GQM try to be more agreesive in finding new line opportunities
                            raw_text = raw_text+'\n'+ txt.strip()
                            current_baseline=current_y_offset
                        else:
                            raw_text = raw_text+txt.strip()
                    # if the current txt is zero width there is nothing to do add to the raw_txt, we simply remember tha last text to apply the modification to the next text
                else:
                    if current_y_offset is None:
                        delta_y=current_baseline - current_y_offset
                    else:
                        delta_y=0.0
                    if Verbose_Flag:
                        print(f'modified case: "{txt}" {delta_y} pt')
                    if not size is None:
                        if size > 0:
                            if abs(delta_y) > 0.8 * size:
                                if Verbose_Flag:
                                    print(f'Starting a new line of text')
                                raw_text = raw_text+'\n'+ txt.strip()
                                current_x_offset=None
                                current_baseline=current_y_offset
                            else:
                                raw_text = raw_text+' '+ txt.strip()
                        else:
                            # Note that if size is zero we do not add anything
                            if Verbose_Flag:
                                print(f'nothing to add to the raw text - as the current txt is "{txt}"')

                if current_x_offset is None:
                    last_current_x_offset=current_x_width
                else:
                    last_current_x_offset=current_x_offset+current_x_width

                last_current_y_offset=current_y_offset
                last_current_x_width=current_x_width
                last_txt=txt.strip()
                last_size=size


            else:
                continue

    total_raw_text=total_raw_text+clean_raw_text(raw_text)

    return clean_raw_text(raw_text)

# ligature. LaTeX commonly does it for ff, fi, fl, ffi, ffl, ...
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
                  '\u1e9e': 'fs', # 'ẞ'
                  '\u00df': 'fz', # 'ß'
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
                  '\u0238': 'db', # 'ȸ'
                  '\u02a3': 'dz', # 'ʣ'
                  '\u1b66': 'dʐ', # 'ꭦ'
                  '\u02a5': 'dʑ', # 'ʥ'
                  '\u02a4': 'dʒ', # 'ʤ'
                  '\u02a9': 'fŋ', # 'ʩ'
                  '\u02aa': 'ls', # 'ʪ'
                  '\u02ab': 'lz', # 'ʫ'
                  '\u026e': 'lʒ', # 'ɮ'
                  '\u0239': 'qp', # 'ȹ'
                  '\u02a8': 'tɕ', # 'ʨ'
                  '\u02a6': 'ts', # 'ʦ'
                  '\uab67': 'tʂ', # 'ꭧ'
                  '\u02a7': 'tʃ', # 'ʧ'
                  '\uab50': 'ui', # 'ꭐ'
                  '\uab51': 'ui', # 'ꭑ' -- turned ui
                  '\u026f': 'uu', # 'ɯ'
                  # digraphs with single code points
                  '\u01f1': 'DZ', # 'Ǳ'
                  '\u01f2': 'Dz', # 'ǲ'
                  '\u01f3': 'dz', # 'ǳ'
                  '\u01c4': 'DŽ', # 'Ǆ'
                  '\u01c5': 'Dž', # 'ǅ'
                  '\u01c6': 'dž', # 'ǆ'
                  '\u0132': 'IJ', # 'Ĳ'
                  '\u0133': 'ij', # 'ĳ'
                  '\u01c7': 'LJ', # 'Ǉ'
                  '\u01c8': 'Lj', # 'ǈ'
                  '\u01c9': 'lj', # 'ǉ'
                  '\u01ca': 'NJ', # 'Ǌ'
                  '\u01cb': 'Nj', # 'ǋ'
                  '\u01cc': 'nj', # 'ǌ'
                  '\u1d7a': 'th', # 'ᵺ'
                  }

def replace_ligature(s):
    # check for ligratures and replace them with separate characters
    if not s:
        return s
    
    for l in ligrature_table:
        if s.find(l) >= 0:
            print("found ligrature {0} replacing with {1}".format(l, ligrature_table[l]))  
            s=s.replace(l, ligrature_table[l])
    #
    return s

# do deal with PDF generators outputting Swedish chracters such as 'ö' as '¨o'
def clean_raw_text(s):
    global replace_ligatures_flag
    global processing_a_PDF_file
    global delete_lines_with_assignments
    global assignment_lines_removed

    # in some places in PDF files from LaTeX there is hypehnation at the end of a line leading to "-\n"
    s=s.replace('-\n', '')

    # s=s.replace('¨o', 'ö')
    # s=s.replace('¨a', 'ä')
    # s=s.replace('˚a', 'å')
    # s=s.replace('¨O', 'Ö')
    # s=s.replace('¨A', 'Ä')
    s=s.replace('¨a','ä')
    s=s.replace('¨A','Ä')
    s=s.replace('¨e','ê')
    s=s.replace('¨E','Ê')
    s=s.replace('¨h','ḧ')
    s=s.replace('¨H','Ḧ')
    s=s.replace('¨i', 'ï')
    s=s.replace('¨ı', 'ï')
    s=s.replace('¨I','Ï')
    s=s.replace('¨o','ö')
    s=s.replace('¨O','Ö')
    s=s.replace('¨t','ẗ')
    s=s.replace('¨T','T̈')
    s=s.replace('¨u','ü')
    s=s.replace('¨U','Ü')
    s=s.replace('¨w','ẅ')
    s=s.replace('¨W','Ẅ')
    s=s.replace('¨x','ẍ')
    s=s.replace('¨X','Ẍ')
    s=s.replace('¨y','ÿ')
    s=s.replace('¨Y','Ÿ')
    s=s.replace('¨‐','⸚')

    # ring above
    s=s.replace('˚A', 'Å')
    s=s.replace('˚a','å')
    s=s.replace('˚A','Å')
    s=s.replace('˚u','ů')
    s=s.replace('˚U','Ů')
    s=s.replace('˚y','ẙ')
    s=s.replace('˚y','Y̊')

    # acute accent
    s=s.replace('´a','á')
    s=s.replace('´A','Á')
    s=s.replace('´c','ć')
    s=s.replace('´C','Ć')
    s=s.replace('´e','é')
    s=s.replace('´E','É')
    s=s.replace('´g','ǵ')
    s=s.replace('´G','Ǵ')
    s=s.replace('´i','í')
    s=s.replace('´ı','í')
    s=s.replace('´I','Í')
    s=s.replace('´k','ḱ')
    s=s.replace('´K','Ḱ')
    s=s.replace('´l','ĺ')
    s=s.replace('´L','Ĺ')
    s=s.replace('´m','ḿ')
    s=s.replace('´M','Ḿ')
    s=s.replace('´n','ń')
    s=s.replace('´N','Ń')
    s=s.replace('´o','ó')
    s=s.replace('´O','Ó')
    s=s.replace('´p','ṕ')
    s=s.replace('´P','Ṕ')
    s=s.replace('´r','ŕ')
    s=s.replace('´R','Ŕ')
    s=s.replace('´s','ś')
    s=s.replace('´S','Ś')
    s=s.replace('´u','ú')
    s=s.replace('´U','Ú')
    s=s.replace('´w','ẃ')
    s=s.replace('´W','Ẃ')
    s=s.replace('´y','ý')
    s=s.replace('´Y','Ý')
    s=s.replace('´z','ź')
    s=s.replace('´Z','Ź')

    # grave accent
    s=s.replace('`a', 'à')
    s=s.replace('`A', 'À')
    s=s.replace('`e', 'è')
    s=s.replace('`E', 'È')
    s=s.replace('`i', 'ì')
    s=s.replace('`ı', 'ì')
    s=s.replace('`I', 'Ì')
    s=s.replace('`n', 'ǹ')
    s=s.replace('`N', 'Ǹ')
    s=s.replace('`o', 'ò')
    s=s.replace('`O', 'Ò')
    s=s.replace('`u', 'ù')
    s=s.replace('`U', 'Ù')
    s=s.replace('`w', 'ẁ')
    s=s.replace('`W', 'Ẁ')
    s=s.replace('`y', 'ỳ')
    s=s.replace('`Y', 'Ỳ')

    # macron
    s=s.replace('¯a','ā')
    s=s.replace('¯A','Ā')
    s=s.replace('¯e','ē')
    s=s.replace('¯E','Ē')
    s=s.replace('¯g','ḡ')
    s=s.replace('¯G','Ḡ')
    s=s.replace('¯i','ī')
    s=s.replace('¯i','ī')
    s=s.replace('¯i','Ī')
    s=s.replace('¯o','ō')
    s=s.replace('¯O','Ō')
    s=s.replace('¯u','ū')
    s=s.replace('¯U','Ū')
    s=s.replace('¯y','ȳ')
    s=s.replace('¯Y','Ȳ')
    s=s.replace('¯α','ᾱ')
    s=s.replace('¯Α','Ᾱ')
    s=s.replace('¯ι','ῑ')
    s=s.replace('¯Ι','Ῑ')
    s=s.replace('¯υ','ῡ')
    s=s.replace('¯Υ','Ῡ')

    # tilde
    s=s.replace('˜a','ã')
    s=s.replace('˜A','Ã')
    s=s.replace('˜e','ẽ')
    s=s.replace('˜E','Ẽ')
    s=s.replace('˜i','ĩ')
    s=s.replace('˜ı','ĩ')
    s=s.replace('˜I','Ĩ')
    s=s.replace('˜n','ñ')
    s=s.replace('˜N','Ñ')
    s=s.replace('˜o','õ')
    s=s.replace('˜O','Õ')
    s=s.replace('˜u','ũ')
    s=s.replace('˜Ũ','Û')
    s=s.replace('˜v','ṽ')
    s=s.replace('˜V','Ṽ')
    s=s.replace('˜y','ỹ')
    s=s.replace('˜Y','Ỹ')

    # circumflex
    s=s.replace('ˆa', 'â')
    s=s.replace('ˆA', 'Â')
    s=s.replace('ˆc', 'ĉ')
    s=s.replace('ˆC', 'Ĉ')
    s=s.replace('ˆe', 'ê')
    s=s.replace('ˆE', 'Ê')
    s=s.replace('ˆg', 'ĝ')
    s=s.replace('ˆG', 'Ĝ')
    s=s.replace('ˆh', 'ĥ')
    s=s.replace('ˆH', 'Ĥ')
    s=s.replace('ˆi', 'î')
    s=s.replace('ˆı', 'î')
    s=s.replace('ˆI', 'Î')
    s=s.replace('ˆj', 'ĵ')
    s=s.replace('ˆȷ', 'ĵ')
    s=s.replace('ˆj', 'Ĵ')
    s=s.replace('ˆo', 'ô')
    s=s.replace('ˆO', 'Ô')
    s=s.replace('ˆs', 'ŝ')
    s=s.replace('ˆS', 'Ŝ')
    s=s.replace('ˆu', 'û')
    s=s.replace('ˆU', 'Û')
    s=s.replace('ˆw', 'ŵ')
    s=s.replace('ˆW', 'Ŵ')
    s=s.replace('ˆy', 'ŷ')
    s=s.replace('ˆY', 'Ŷ')
    s=s.replace('ˆz', 'ẑ')
    s=s.replace('ˆZ', 'Ẑ')

    # breve
    s=s.replace('˘a', 'ă')
    s=s.replace('˘A', 'Ă')
    s=s.replace('˘e', 'ĕ')
    s=s.replace('˘E', 'Ĕ')
    s=s.replace('˘g', 'ğ')
    s=s.replace('˘G', 'Ğ')
    s=s.replace('˘i', 'ĭ')
    s=s.replace('˘ı', 'ĭ')
    s=s.replace('˘I', 'Ĭ')
    s=s.replace('˘o', 'ŏ')
    s=s.replace('˘O', 'Ŏ')
    s=s.replace('˘u', 'ŭ')
    s=s.replace('˘U', 'Ŭ')

    # dot above
    s=s.replace('˙a', 'ȧ')
    s=s.replace('˙A', 'Ȧ')
    s=s.replace('˙b', 'ḃ')
    s=s.replace('˙B', 'Ḃ')
    s=s.replace('˙c', 'ċ')
    s=s.replace('˙C', 'Ċ')
    s=s.replace('˙d', 'ḋ')
    s=s.replace('˙D', 'Ḋ')
    s=s.replace('˙e', 'ė')
    s=s.replace('˙E', 'Ė')
    s=s.replace('˙f', 'ḟ')
    s=s.replace('˙F', 'Ḟ')
    s=s.replace('˙g', 'ġ')
    s=s.replace('˙G', 'Ġ')
    s=s.replace('˙h', 'ḣ')
    s=s.replace('˙H', 'Ḣ')
    s=s.replace('˙I', 'İ')
    s=s.replace('˙m', 'ṁ')
    s=s.replace('˙M', 'Ṁ')
    s=s.replace('˙n', 'ṅ')
    s=s.replace('˙N', 'Ṅ')
    s=s.replace('˙o', 'ȯ')
    s=s.replace('˙O', 'Ȯ')
    s=s.replace('˙p', 'ṗ')
    s=s.replace('˙P', 'Ṗ')
    s=s.replace('˙r', 'ṙ')
    s=s.replace('˙R', 'Ṙ')
    s=s.replace('˙s', 'ṡ')
    s=s.replace('˙S', 'Ṡ')
    s=s.replace('˙t', 'ṫ')
    s=s.replace('˙T', 'Ṫ')
    s=s.replace('˙u', 'ụ')
    s=s.replace('˙Ũ', 'Ụ')
    s=s.replace('˙w', 'ẇ')
    s=s.replace('˙W', 'Ẇ')
    s=s.replace('˙x', 'ẋ')
    s=s.replace('˙X', 'Ẋ')
    s=s.replace('˙y', 'ẏ')
    s=s.replace('˙Y', 'Ẏ')
    s=s.replace('˙z', 'ż')
    s=s.replace('˙Z', 'Ż')

    # cedilla - note that there seems to be something odd in the order of the characters that the PDF driver is generating
    s=s.replace('c¸', 'ç')
    #s=s.replace('¸C', 'Ç')
    s=s.replace('C¸ ', 'Ç')      #  the cedilla seems to follow the character
    s=s.replace('d¸', 'ḑ')
    s=s.replace('D¸', 'Ḑ')
    s=s.replace('e¸', 'ȩ')
    s=s.replace('E¸', 'Ȩ')
    s=s.replace('g¸', 'ģ')
    s=s.replace('G¸', 'Ģ')
    s=s.replace('h¸', 'ḩ')
    s=s.replace('H¸', 'Ḩ')
    s=s.replace('k¸', 'ķ')
    s=s.replace('K¸', 'Ķ')
    s=s.replace('l¸', 'ļ')
    s=s.replace('L¸', 'Ļ')
    s=s.replace('n¸', 'ņ')
    s=s.replace('N¸', 'Ņ')
    s=s.replace('r¸', 'ŗ')
    s=s.replace('R¸', 'Ŗ')
    s=s.replace('s¸', 'ş')
    s=s.replace('S¸', 'Ş')
    #s=s.replace('¸t', 'ţ')
    s=s.replace('t¸', 'ţ') #  the cedilla seems to follow the character
    s=s.replace('T¸', 'Ţ')

    # háček caron
    s=s.replace('ˇa', 'ǎ')
    s=s.replace('ˇA', 'Ǎ')
    s=s.replace('ˇc', 'č')
    s=s.replace('ˇC', 'Č')
    s=s.replace('ˇd', 'ď')
    s=s.replace('ˇD', 'Ď')
    s=s.replace('ˇe', 'ě')
    s=s.replace('ˇE', 'Ě')
    s=s.replace('ˇg', 'ǧ')
    s=s.replace('ˇG', 'Ǧ')
    s=s.replace('ˇh', 'ȟ')
    s=s.replace('ˇH', 'Ȟ')
    s=s.replace(('ˇi') or  ('ˇı'), 'ǐ')
    s=s.replace('ˇI', 'Ǐ')
    s=s.replace(('ˇj') or  ('ˇȷ'), 'ǰ')
    s=s.replace('ˇk', 'ǩ')
    s=s.replace('ˇK', 'Ǩ')
    s=s.replace('ˇl', 'ľ')
    s=s.replace('ˇL', 'Ľ')
    s=s.replace('ˇn', 'ň')
    s=s.replace('ˇN', 'Ň')
    s=s.replace('ˇo', 'ǒ')
    s=s.replace('ˇO', 'Ǒ')
    s=s.replace('ˇr', 'ř')
    s=s.replace('ˇR', 'Ř')
    s=s.replace('ˇs', 'š')
    s=s.replace('ˇS', 'Š')
    s=s.replace('ˇt', 'ť')
    s=s.replace('ˇT', 'Ť')
    s=s.replace('ˇu', 'ǔ')
    s=s.replace('ˇU', 'Ǔ')
    s=s.replace('ˇz', 'ž')
    s=s.replace('ˇZ', 'Ž')

     # Double Acute Accent
    s=s.replace('˝a', 'a̋')
    s=s.replace('˝A', 'A̋')
    s=s.replace('˝c', 'c̋')
    s=s.replace('˝C', 'C̋')
    s=s.replace('˝e', 'e̋')
    s=s.replace('˝E', 'E̋')
    s=s.replace('˝g', 'g̋')
    s=s.replace('˝G', 'G̋')
    s=s.replace('˝i', 'i̋')
    s=s.replace('˝ı', 'i̋')
    s=s.replace('˝I', 'I̋')
    s=s.replace('˝ȷ', 'j̋')
    s=s.replace('˝J', 'J̋')
    s=s.replace('˝m', 'm̋')
    s=s.replace('˝M', 'M̋')
    s=s.replace('˝o', 'ő')
    s=s.replace('˝O', 'Ő')
    s=s.replace('˝u', 'ű')
    s=s.replace('˝U', 'Ű')
    s=s.replace('˝ү', 'ӳ')
    s=s.replace('˝Ү', 'Ӳ')

    # there can also be spaces before and after the dicritical for the overprinted characters
    # s=s.replace(' ¨ o', 'ö')
    # s=s.replace(' ¨ a', 'ä')
    # s=s.replace(' ¨ a', 'å')
    # s=s.replace(' ¨ O', 'Ö')
    # s=s.replace(' ¨ A', 'Ä')
    # s=s.replace(' ˚ A', 'Å')

    
    # it is very likely that the TeX engine has inserted ligatures, but you can replace them
    if replace_ligatures_flag:
        s=replace_ligature(s)

    # for LaTeX produced PDF files, delete lines with an assignment in them
    if processing_a_PDF_file:
        lines=s.split('\n')
        clean_lines=[]
        for l in lines:
            if delete_lines_with_assignments and l.count('←') == 1:
                assignment_lines_removed=assignment_lines_removed+1
                if Verbose_Flag:
                    print(f'deleting line: {l}')
                continue
            # remove trailing dashes or hyphens on a line otherwise insert a space
            if Verbose_Flag:
                print(f'{l=}')
            if l.endswith('-'):
                clean_lines.append(l[0:-1])
            else:
                clean_lines.append(l+' ')
        s="\n".join(clean_lines)
    return s


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
    global total_raw_HTML
    global replace_ligatures_flag
    global processing_a_PDF_file
    global delete_lines_with_assignments
    global assignment_lines_removed

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
                      help="Processed the named PDF file rather than a Canvas course",
                      metavar="FILE"
    )

    parser.add_option("--dir", dest="dir_prefix",
                      default='./',
                      help="read configuration from FILE", metavar="FILE")


    parser.add_option('-l', '--ligatures',
                      dest="replace_ligatures",
                      default=False,
                      action="store_true",
                      help="replace ligatures"
    )

    parser.add_option('--keepAssignments',
                      dest="keep_lines_with_assignments",
                      default=False,
                      action="store_true",
                      help="by default remove lines from PDFs with a '←' in them"
    )

    options, remainder = parser.parse_args()

    Verbose_Flag=options.verbose
    if Verbose_Flag:
        print("ARGV      : {}".format(sys.argv[1:]))
        print("VERBOSE   : {}".format(options.verbose))
        print("REMAINING : {}".format(remainder))
        print("Configuration file : {}".format(options.config_filename))

    initialize(options)

    if options.replace_ligatures:
        replace_ligatures_flag=True

    if options.keep_lines_with_assignments:
        delete_lines_with_assignments=False
    else:
        delete_lines_with_assignments=True

    assignment_lines_removed=0

    # compute the directory prefix for files to be used for the program's I/O
    directory_prefix=options.dir_prefix
    if not directory_prefix.endswith('/'):
        directory_prefix=directory_prefix+'/'
    if Verbose_Flag:
        print(f'{directory_prefix=}')

    if (len(remainder) < 1 and not options.processPDF_file):
        print("Insuffient arguments\n must provide course_id or file_name\n")
    else:
        total_words_processed=0
        unique_words=set()
        number_of_unique_words_output=0
        filtered_unique_words=set()
        skipped_words=set()
        all_text=list()
        total_raw_text=''
        total_raw_HTML=''
        
        if options.processPDF_file:
            print('Process a PDF file')
            course_id=remainder[0]
            processing_a_PDF_file=True
        else:
            processing_a_PDF_file=False
            course_id=remainder[0]
            if not str(course_id).isdigit():
                print("Error in course_id")
                return
            # skip index pages, for example:
            if int(course_id) == 41493:
                pages_to_skip=['index-for-course', 'with-quick-index', 'examples-of-some-titles-from-previous-p1p2-reports', 'ict-keywords-20141203']
            elif int(course_id) == 31168:
                pages_to_skip=['top-level-index-of-foreign-terms-with-figure-and-table-captions', 'index-special-and-a-r', 'index-r-z']
            else:
                pages_to_skip=[]

        
        if options.processPDF_file:
            input_PDF_file=f'{directory_prefix}{options.processPDF_file}'
            unique_words_in_PDF_file(input_PDF_file)
            if options.processPDF_file.startswith('./'):
                print('triming ./ when making new file name')
                f_name=options.processPDF_file[2:].replace('/', '_')
                course_id=f'{course_id}_{f_name}'         #  make a place holder course_id
            else:
                f_name=options.processPDF_file.replace('/', '_')
                course_id=f'{course_id}_{f_name}'         #  make a place holder course_id
        else:
            unique_words_for_syllabus_in_course(course_id)
            unique_words_for_pages_in_course(course_id, pages_to_skip)

        print(f'a total of {total_words_processed} words processed')
        if assignment_lines_removed > 0:
            print(f'{assignment_lines_removed} assignment lines removed')
        print(f'{len(unique_words)} unique words')
        if len(unique_words) > 0:
            new_file_name=f'{directory_prefix}unique_words-for-course-{course_id}.txt'

            # if not filtering, simply output the unique words and exit
            if options.keepAll:
                print(f'Writing file: {new_file_name}')
                with open(new_file_name+'raw_words', 'w') as f:
                    for word in unique_words:
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
                        if Verbose_Flag:
                            print(f'found slide number: {s}')
                        continue
                        
                    # ignore a specified set of words
                    if word in words_to_ignore:
                        if Verbose_Flag:
                            print(f'{word} in words_to_ignore')
                        continue

                    # eliminate what is left of URLs
                    if word.startswith("//"):
                        if Verbose_Flag:
                            print(f'{word} starts with a //')
                        continue

                    # skip a variety of file names
                    if is_filename_to_skip(word):
                        if Verbose_Flag:
                            print(f'{word} seems to be a filename that should be skipped')
                        continue

                    # skip currency ammounts
                    if len(word) > 1 and word[0] in currency_symbols:
                        if Verbose_Flag:
                            print(f'{word} seems to be a currency amount')
                        continue

                    # skip things that look like DOIs
                    if is_DOI(word):
                        if Verbose_Flag:
                            print(f'{word} seems to be a DOI')
                        continue

                    # skip things that look like ISBNs
                    if is_ISBN(word):
                        if Verbose_Flag:
                            print(f'{word} seems to be an ISBN')
                        continue

                    # if there is one hyphen it might be an integer range or ISSN, of so ignore it
                    if is_integer_range_or_ISSN(word):
                        if Verbose_Flag:
                            print(f'{word} seems to be an integer range or ISSN')
                        continue

                    # ignore things that look like IPv4 dotted decimal addresses
                    if is_IPv4_dotted_decimal(word):
                        if Verbose_Flag:
                            print(f'{word} seems to be an IPv4 dotted decimal address')
                        continue

                    # ignore IPv4 address with a specified prefix length
                    if is_IPv4_dotted_decimal_with_prefix_length(word):
                        if Verbose_Flag:
                            print(f'{word} seems to be an IPv4 dotted decimal address with prefix length')
                        continue

                    # ignore IPv6 addresses
                    if is_IPv6_address(word):
                        if Verbose_Flag:
                            print(f'{word} seems to be an IPv6 address')
                        continue

                    # ignore things that look like phone numbers
                    if is_phone_number(word):
                        if Verbose_Flag:
                            print(f'{word} seems to be a phone number')
                        continue

                    # ignore things that look like time offsets, i.e., dd:dd:dd
                    if is_time_offset(word):
                        if Verbose_Flag:
                            print(f'{word} seems to be a time offset')
                        continue

                    # ignore start and end time strings
                    if is_start_end_time(word):
                        if Verbose_Flag:
                            print(f'{word} seems to be a start and end time')
                        continue

                    # ignore YYYY.MM.DD and YYYY-MM-DD strings
                    if is_YYYY_MM_DD(word):
                        if Verbose_Flag:
                            print(f'{word} seems to be a YYYY.MM.DD or YYYY-MM-DD string')
                        continue

                    # ignore  DD-MMM-YYYY or DD-MMM-YY strings
                    if is_DD_MMM_YYYY(word):
                        if Verbose_Flag:
                            print(f'{word} seems to be DD_MMM_YYYY string')
                        continue

                    # ignore date time stamps
                    if is_date_time_string(word):
                        if Verbose_Flag:
                            print(f'{word} seems to be time string')
                        continue

                    # ignore words with a single colon in a set of digits
                    if is_colon_range_or_HH_colon_MM(word):
                        if Verbose_Flag:
                            print(f'{word} seems to be a colon range or HH:MM string')
                        continue

                    # ignore approximate numbers
                    if approximate_number(word):
                        if Verbose_Flag:
                            print(f'{word} seems to be a approximate number')
                        continue
                    
                    # ignore numbers with commas in them
                    if is_number_with_commas(word):
                        if Verbose_Flag:
                            print(f'{word} seems to contain one of more commas')
                        continue

                    # ignore fractions
                    if is_fraction(word):
                        if Verbose_Flag:
                            print(f'{word} seems to be a fraction')
                        continue

                    # ignore hex numbers
                    if is_hex_number(word):
                        if Verbose_Flag:
                            print(f'{word} seems to be a hexidecimal number')
                        continue

                    # ignore things that look like MAC addresses
                    if is_MAC_address(word):
                        if Verbose_Flag:
                            print(f'{word} seems to be a MAC address')
                        continue


                    # ignore things that look like CID font identifier
                    if is_cid_font_identifier(word):
                        if Verbose_Flag:
                            print(f'{word} seems to be a CID font identifier')
                        continue

                    # ignore things that look like single numbers (also ignore numbers with string, such as units, after them)
                    if is_number(word):
                        if Verbose_Flag:
                            print(f'{word} seems to be a number')
                        continue

                    # ignore DiVA identifiers
                    if is_part_of_DiVA_identifier(word):
                        if Verbose_Flag:
                            print(f'{word} seems to be part of a DiVA identifier')
                        continue

                    # ignore TRITA numbers
                    if is_TRITA_identifier(word):
                        if Verbose_Flag:
                            print(f'{word} seems to be part of a TRITA identifier')
                        continue

                    # ignore arXiv identifiers
                    if is_part_of_arXiv_identifier(word):
                        if Verbose_Flag:
                            print(f'{word} seems to be part of a arXiv identifier')
                        continue

                    # ignore spring links
                    if is_part_of_springerlink_identifier(word):
                        if Verbose_Flag:
                            print(f'{word} seems to be a Springer link')
                        continue

                    # moved this functionality to the prune phase
                    # # ignore equations
                    # if is_equation(word):
                    #     if Verbose_Flag:
                    #         print(f'{word} seems to be an equation')
                    #     continue


                    # finally output the remaining word
                    f.write(f"{word}\n")
                    if Verbose_Flag:
                        print(f'keeping: {word}')
                    filtered_unique_words.add(word)

                    number_of_unique_words_output=number_of_unique_words_output+1

            print(f'{number_of_unique_words_output} unique words output to {new_file_name}')

        # check type of filtered_unique_words
        print(f'{len(filtered_unique_words)} filtered_unique_words')

        # compute word frequency for the filtered unique words
        frequency=dict()
        for count, word in enumerate(all_text):
            if len(word) == 0:  #  skip zero length word
                continue
            #print(f'{word=}')
            if word in filtered_unique_words or word.lower() in filtered_unique_words:
                current_word_frequency=frequency.get(word, 0)
                frequency[word]=current_word_frequency+1
            elif len(word) > 1:
                # keep the base of words, such as "binär-" or suffixes, such as "-notationens"
                if word.endswith('-'):
                    current_word_frequency=frequency.get(word[:-1], 0)
                    frequency[word[:-1]]=current_word_frequency+1
                if word.startswith('-'):
                    current_word_frequency=frequency.get(word[1:], 0)
                    frequency[word[1:]]=current_word_frequency+1
                else:
                    if Verbose_Flag:
                        print(f'when computing frequency - skipping: {word}')
                    skipped_words.add(word)
            else:
                if Verbose_Flag:
                    print(f'when computing frequency - skipping: {word}')
                skipped_words.add(word)

        frequency_sorted=dict(sorted(frequency.items(), key=lambda x:x[1]))

        new_file_name=f'{directory_prefix}unique_words-for-course-frequency-{course_id}.txt'        
        with open(new_file_name, 'w') as f:
            f.write(json.dumps(frequency_sorted, ensure_ascii=False))
        print(f'output {new_file_name}')

        new_file_name=f'{directory_prefix}unique_words-for-course-skipped-{course_id}.txt'
        with open(new_file_name, 'w') as f:
            for word in skipped_words:
                f.write(f"{word}\n")

        # save all the raw text
        new_file_name=f'{directory_prefix}unique_words-for-course-raw_text-{course_id}.txt'
        with open(new_file_name, 'w') as f:
            f.write(total_raw_text)

        if not options.processPDF_file:
            # save all the raw HTML
            new_file_name=f'{directory_prefix}unique_words-for-course-raw_HTML-{course_id}.txt'
            with open(new_file_name, 'w') as f:
                f.write(total_raw_HTML)


if __name__ == "__main__": main()
