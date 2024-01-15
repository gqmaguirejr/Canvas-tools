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
    'ˆ',
    '\\u0000', # remove the string \u0000 which is the null characters
    '0xFE0E',  # this is Variation Selector-15 - it modifies the character before it, but will end up at the start of the word after it
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
    '',
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
        if len(newword) > 0:
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

    s=s.replace('¨o', 'ö')
    s=s.replace('¨a', 'ä')
    s=s.replace('˚a', 'å')
    s=s.replace('¨O', 'Ö')
    s=s.replace('¨A', 'Ä')
    s=s.replace('˚A', 'Å')
    # there can also be spaces before and after the dicritical for the overprinted characters
    s=s.replace(' ¨ o', 'ö')
    s=s.replace(' ¨ a', 'ä')
    s=s.replace(' ¨ a', 'å')
    s=s.replace(' ¨ O', 'Ö')
    s=s.replace(' ¨ A', 'Ä')
    s=s.replace(' ˚ A', 'Å')

    
    # it is very likely that the TeX engine has inserted ligatures, but you can replace them
    if replace_ligatures_flag:
        s=replace_ligature(s)

    # for LaTeX produced PDF files, delete lines with an assignment in them
    if processing_a_PDF_file and delete_lines_with_assignments:
        lines=s.split('\n')
        clean_lines=[]
        for l in lines:
            if l.count('←') == 1:
                assignment_lines_removed=assignment_lines_removed+1
                if Verbose_Flag:
                    print(f'deleting line: {l}')
                continue
            clean_lines.append(l)
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
