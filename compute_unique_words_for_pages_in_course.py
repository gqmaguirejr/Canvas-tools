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
    '+',
    ',',
    '-',
    './',
    ':',
    '=',
    '|',
    '¡',
    '§',
    '¿',
    '–',
    '†',
    '‡',
    '•',
    '⇒',
    '',
    '',
    "¨",
    '≡',
    '✔',
    '✝',
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
    '°',
    '®',
    '™',
    "§",
]

# based on the words at https://en.wikipedia.org/wiki/Most_common_words_in_English
top_100_English_words={
    "the": "Article",
    "be": "Verb",
    "to": "Preposition",
    "of": "Preposition",
    "and": "Coordinator",
    "a": "Article",
    "in": "Preposition",
    "that": "determiner",
    "have": "Verb",
    "I": "Pronoun",
    "it": "Pronoun",
    "for": "Preposition",
    "not": "Adverb et al.",
    "on": "Preposition",
    "with": "Preposition",
    "he": "Pronoun",
    "as": "Adverb, preposition",
    "you": "Pronoun",
    "do": "Verb, noun",
    "at": "Preposition",
    "this": "Determiner, adverb, noun",
    "but": "Preposition, adverb, coordinator",
    "his": "Possessive pronoun",
    "by": "Preposition",
    "from": "Preposition",
    "they": "Pronoun",
    "we": "Pronoun",
    "say": "Verb et al.",
    "her": "Possessive pronoun",
    "she": "Pronoun",
    "or": "Coordinator",
    "an": "Article",
    "will": "Verb, noun",
    "my": "Possessive pronoun",
    "one": "Noun, adjective, et al.",
    "all": "Adjective",
    "would": "Verb",
    "there": "Adverb, pronoun, et al.",
    "their": "Possessive pronoun",
    "what": "Pronoun, adverb, et al.",
    "so": "Coordinator, adverb, et al.",
    "up": "Adverb, preposition, et al.",
    "out": "Preposition",
    "if": "Preposition",
    "about": "Preposition, adverb, et al.",
    "who": "Pronoun, noun",
    "get": "Verb",
    "which": "Pronoun",
    "go": "Verb, noun",
    "me": "Pronoun",
    "when": "Adverb",
    "make": "Verb, noun",
    "can": "Verb, noun",
    "like": "Preposition, verb",
    "time": "Noun",
    "no": "Determiner, adverb",
    "just": "Adjective",
    "him": "Pronoun",
    "know": "Verb, noun",
    "take": "Verb, noun",
    "people": "Noun",
    "into": "Preposition",
    "year": "Noun",
    "your": "Possessive pronoun",
    "good": "Adjective",
    "some": "Determiner",
    "could": "Verb",
    "them": "Pronoun",
    "see": "Verb",
    "other": "Adjective, pronoun",
    "than": "Preposition",
    "then": "Adverb",
    "now": "Preposition",
    "look": "Verb",
    "only": "Adverb",
    "come": "Verb",
    "its": "Possessive pronoun",
    "over": "Preposition",
    "think": "Verb",
    "also": "Adverb",
    "back": "Noun, adverb",
    "after": "Preposition",
    "use": "Verb, noun",
    "two": "Noun",
    "how": "Adverb",
    "our": "Possessive pronoun",
    "work": "Verb, noun",
    "first": "Adjective",
    "well": "Adverb",
    "way": "Noun, adverb",
    "even": "Adjective",
    "new": "Adjective et al.",
    "want": "Verb",
    "because": "Preposition",
    "any": "Pronoun",
    "these": "Pronoun",
    "give": "Verb",
    "day": "Noun",
    "most": "Adverb",
    "us": "Pronoun"
}

miss_spelled_words=[
    "FF01:0:0:0:0:0:1",
    "BibTex",
    "procotol", 
    "concpets",
    "acknowldgement",
    "acknowldgement",
    "Tra\ufb03c",
    "Traf\ufb01c",
    "u-Law",
    'wo'
    'sFor',
    'presental',
    #'n\u00e4t',
    #'nat',
    #'natfriend',
    #'in-active',
    #'information.Nostratic',
    #'isn',
    #'l\u00e5ng',
    'identi\ufb01cation',
    "you're",
    'ßtudent',     # should be "student"
    'â€˜Security',  # should be 'Security',
    'Â§',
    'wiklipage',   # should be 'wikipage'
    'Addres',      # should be 'Address'
    'Carrera',     # should be 'Carrara'
    'Copmmunication',  # should be 'Communication'
    'Dezember',    # should be 'December'
    'Europeens',   # should be 'Européens'
    'Glassfish',   # should be 'GlassFish'
    'Kamailo',     # should be 'Kamailio'
    'QCLEP',       # should be 'QCELP'
    'Sigcomp',     # should be 'SigComp',
    'Sinreich',    # should be 'Sinnreich',
    'Stcokholm',   # should be 'Stockholm'
    'acknowdlged', # should be 'acknowledged'
    'acknowldged', # should be 'acknowledged'
    'acknowledgment', # should be 'acknowledgement'
    'acknowledgments', # should be 'acknowledgements'
    'acroynms',    # should be 'acronyms'
    'addrees',     # should be 'address'
    'addressesing',  # should be 'addressing'
    'addtion',     # should be 'addition'
    'adpators',    # should be 'adaptors'
    'annouce',     # should be 'announce'
    'annouced',    # should be 'announced'
    'annoucement', # should be 'announcement',
    'anseers',     # 'answer' ?
    'ansers',      # 'answers' ?
    'answrs',      # 'answers' ?
    'apointments', # 'appointments',
    'april',       # check
    'aqsks',       # check
    'audable',     # check
    'buiold',      # should be "build"
    'cancelling',  # US preference is 'canceling'
    'congesiton',  # should be 'congestion'
    'declaritive', # should be 'declarative'
    'dialling',    # US preference is 'dialing'
    'erros',       # should be 'errors'
    'escow',       # should be 'escrow'
    'evrsion',     # should be 'version'
    'exampe',      # should be 'example'
    'existance',   # should be 'existence',
    'faillure',    # should be 'failure'
    'fielda',      # should be 'fields'
    'f¨r',         # should be 'för'
    'fÃ¼r',        # should be 'för'
    'gots',	   # should be 'got'
    'inaudable',   # should be 'inaudible'
    'indepth',     # should be 'in-depth'
    'intecept',    # should be 'intercept'
    'interensed',  # should be 'interested'
    'keypd',       # should be 'keypad'
    'lnow',        # should be 'know'
    'lookes',      # should be 'looks'
    'messsage',    # should be 'message'
    'negociate',   # should be 'negotiate'
    'nonadways',   # possibly should be 'nowadays'
    'nowadways',   # possibly should be 'nowadays'
    'offfice',     # should be 'office'
    'particularily', # should be 'particularly'
    'passd',       # should be 'passed'
    'pemissible',  # should be 'permissible'
    'plaout',      # should be 'playout'
    'plut',        # should be 'put'
    'presense',    # possibly 'presence'
    'probems',     # should be 'probems'
    'procotol',    # should be 'protocol'
    'proctocols',  # should be 'protocols'
    'procy',       # should be 'proxy'
    'protability', # should be 'portability'
    'protocls',    # should be 'protocols'
    'proﬁle',      # should be 'profile'
    'publically',  # should be 'publicly'
    'reall',       # check
    'reciever',    # should be 'receiver'
    'refences',    # should be 'references'
    'regularily',  # should be 'regularly'
    'relse',       # check
    'reponse',     # should be 'response'
    'resliiance',  # should be 'resilience'
    'rining',      # should be 'ringing'
    'runiing',     # should be 'running'
    'satistics',   # should be 'statistics'
    'scehdule',    # should be 'schedule'
    'sents',       # should be 'sends'
    'seperators',  # should be 'separators'
    'servelets',   # should be 'servlets'
    'serverlets',  # should be 'servlets'
    'sesssion',    # should be 'session'
    'similarily',  # should be 'similarly',
    'slideD',      # check - correct it is a template where D is one or more digits
    'spresd',      # should be 'spread'
    'statistcis',  # should be 'statistics'
    'stduent',     # should be 'student'
    'streamaing',  # should be 'streaming'
    'tah',         # check
    'taugh',       # should be 'taught'
    'thiing',      # should be 'things'
    'thursday',    # should be 'Thursday'
    'trigegr',     # should be 'trigger'
    'vality',      # should be 'vanity'
    'verson',      # should be 'version'
    'voila',       # should be 'voilà'
    'witht',       # check
    'Greasmoneky',  # should be 'Greasemoneky'
    'appendicees',  # should be 'appendices'
]

def check_spelling_errors(s, url):
    if s in miss_spelled_words:
        print(f'miss spelling {s} at {url=}')


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

def unique_words_for_pages_in_course(course_id):
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

    
def is_part_of_DiVA_identifier(s):
    if s.startswith('3Adiva-'):
        return True
    if s.startswith('diva-'):
        return s[5:].isdigit()
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
    '.bib',
    '.c',
    '.conf',
    '.csv',
    '.dtd',
    '.doc',
    '.docx',
    '.ethereal',
    '.html',
    '.jpg',
    '.js',
    #'.json',
    '.list',
    '.mods',
    '.pdf',
    '.png',
    '.ps',
    '.py',
    '.srt',
    '.tcpdump',
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

    options, remainder = parser.parse_args()

    Verbose_Flag=options.verbose
    if Verbose_Flag:
        print("ARGV      : {}".format(sys.argv[1:]))
        print("VERBOSE   : {}".format(options.verbose))
        print("REMAINING : {}".format(remainder))
        print("Configuration file : {}".format(options.config_filename))

    initialize(options)

    if (len(remainder) < 1):
        print("Inusffient arguments\n must provide course_id\n")
    else:
        total_words_processed=0
        unique_words=set()
        number_of_unique_words_output=0
        filtered_unique_words=set()
        skipped_words=set()
        all_text=list()
        total_raw_text=''
        
        course_id=remainder[0]
        unique_words_for_pages_in_course(course_id)

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
