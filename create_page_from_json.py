#!/usr/bin/python3
#
# ./create_page_from_json.py course_id input.json
# 
# it outputs a file that could be put into a Canvas page with index related data for a Canvas course
#
# G. Q: Maguire Jr.
#
# 2020.03.31
#


import csv, requests, time
from pprint import pprint
import optparse
import sys
import os

import pathlib                  # to get each of the files

import json

from lxml import html

# Use Python Pandas to create XLSX files
import pandas as pd

# to handle regular expressions
import re
import nltk

language_info={
    "de_de": {'en': '<span lang="en_us">German</span>',    'sv': '<span lang="sv_se">tyska</span>'},
    "no_nb": {'en': '<span lang="en_us">Norwegian</span>', 'sv': '<span lang="sv_se">norska</span>'},
    "sv_se": {'en': '<span lang="en_us">Swedish</span>',   'sv': '<span lang="sv_se">svenska</span>'},
    "fr_fr": {'en': '<span lang="en_us">French</span>',    'sv': '<span lang="sv_se">franska</span>'},
}

StopWords=[
    u'a',
    u'à',
    u'able',
    u'about',
    u'above',
    u'additional',
    u'additionally',
    u'after',
    u'against',
    u'all',
    u'allows',
    u'along',
    u'almost',
    u'already',
    u'also',
    u'also:',
    u'although',
    u'an',
    u'and',
    u'another',
    u'any',
    u'anyone',
    u'are',
    u'as',
    u'at',
    u'average',
    u'be',
    u'been',
    u'because',
    u'before',
    u'being',
    u'below',
    u'between',
    u'both',
    u'but',
    u'by',
    u'can',
    u'could',
    u'course',
    u'currently',
    u'decrease',
    u'decreasing',
    u'did',
    u'do',
    u'doing',
    u'does',
    u'done',
    u'down',
    u'due',
    u'during',
    u'each',
    u'early',
    u'earlier',
    u'easy',
    u'e.g',
    u'eigth',
    u'either',
    u'else',
    u'end',
    u'especially',
    u'etc',
    u'even',
    u'every',
    u'far',
    u'few',
    u'five',
    u'first',
    u'follow',
    u'following',
    u'for',
    u'formerly',
    u'four',
    u'from',
    u'further',
    u'general',
    u'generally',
    u'get',
    u'going',
    u'good',
    u'had',
    u'has',
    u'have',
    u'having',
    u'he',
    u'hence',
    u'her',
    u'here',
    u'hers',
    u'herself',
    u'high',
    u'higher',
    u'him',
    u'himself',
    u'his', 
    u'how',
    u'however',
    u'i',    
    u'i.e',
    u'if',
    u'in',
    u'include',
    u'includes',
    u'including',
    u'increase',
    u'increasing',
    u'into',
    u'is',
    u'it',
    u"it's",
    u'its',
    u'itself',
    u'just',
    u'know',
    u'known',
    u'knows',
    u'last',
    u'later',
    u'large',
    u'least',
    u'like',
    u'long',
    u'longer',
    u'low',
    u'made',
    u'many',
    u'make',
    u'makes',
    u'me',
    u'might',
    u'much',
    u'more',
    u'most',
    u'must',
    u'my',
    u'myself',
    u'near',
    u'need',
    u'needs',
    u'needed',
    u'next',
    u'new',
    u'no',
    u'nor',
    u'not',
    u'now',
    u'of',
    u'off',
    u'often',
    u'on',
    u'once',
    u'one',
    u'only',
    u'or',
    u'other',
    u'others',
    u'otherwise',
    u'our',
    u'ours',
    u'ourselves',
    u'out', 
    u'over',
    u'own',
    u'pass',
    u'per',
    u'pg',
    u'pp',
    u'provides',
    u'rather',
    u'require',
    u's',
    u'same',
    u'see',
    u'several',
    u'she',
    u'should',
    u'simply',
    u'since',
    u'six',
    u'small',
    u'so',
    u'some',
    u'such',
    u'take',
    u'takes',
    u'th',
    u'than',
    u'that',
    u'the',
    u'then',
    u'their',
    u'theirs',
    u'them',
    u'themselves',
    u'then',
    u'there',
    u'therefore',
    u'these',
    u'three',
    u'they',
    u'this',
    u'those',
    u'through',
    u'thus',
    u'time',
    u'to',
    u'too',
    u'try',
    u'two',
    u'under',
    u'unit',
    u'until',
    u'up',
    u'used',
    u'verison',
    u'very',
    u'vs',
    u'want',
    u'was',
    u'we',
    u'were',
    u'what',
    u'when',
    u'where',
    u'which',
    u'while',
    u'who',
    u'whom',
    u'why',
    u'wide',
    u'will',
    u'with',
    u'within',
    u'would',
    u'you',
    u'your',
    u'yourself',
    u'yourselves'
]

punctuation_list=[
    u'.',                       # add some punctuation to this list
    u',',
    u';',
    u'?',
    u'!',
    u'\t',
    u'\n',
    u'⇒',
    u'…',
    u'(',
    u')',

]

def get_text_for_tag(document, tag, dir):
    tag_xpath='.//'+tag
    text_dir=tag+'_text'
    tmp_path=document.xpath(tag_xpath)
    if tmp_path:
        tmp=[item.text for item in tmp_path]
        tmp[:] = [item for item in tmp if item != None and item != "\n"]
        if tmp:
            dir[text_dir]=tmp

def remove_tag(document, tag):
    tag_xpath='//'+tag
    for bad in document.xpath(tag_xpath):
        bad.getparent().remove(bad)

def split_into_sentences(txt):
    regexPattern = '|'.join(map(re.escape, punctuation_list))
    #print(regexPattern)
    return re.split(regexPattern, txt)
    #return re.split('[.,;?!()]\s', txt)

    
def split_into_words(txt):
    #return re.findall(r"[\w']+", txt)
    #return re.findall(r"[\w']+|[.,!?;]", txt)
    #return re.findall(r"[a-zA-Z0-9_:åäö']+|[.,!?;]", txt)
    return re.findall(r"[a-zA-Z0-9_:/]+|[.!?;]", txt)

def split_on_stop_words(s1):
    global Verbose_Flag
    global Stop_flag

    output_list=list()
    working_list=list()
    lower_case_next_word=True
    if Stop_flag:
        #lwords=split_into_words(s1)
        #words=[w[0] for w in lwords]
        words=split_into_words(s1)
    else:
        #words=nltk.word_tokenize(s1)
        # The method below does fine grain tokenization that the method above
        lwords=[nltk.word_tokenize(t) for t in nltk.sent_tokenize(s1)]
        words=[w[0] for w in lwords]

    for w in words:
        if (w not in StopWords) and (w not in punctuation_list):
            working_list.append(w)
        else:
            output_list.append(working_list)
            working_list=list()
            # handle remainder - if necessary
            
    if len(working_list) > 0:
        output_list.append(working_list)
        # remove empty list from the list
    output_list = [x for x in output_list if x != []]
    return output_list

def combine_sublists_into_strings(l1):
    new_list=list()
    for l in l1:
        working_string=""
        for w in l:
            working_string=working_string+' '+w
            new_list.append(working_string.strip())
    return new_list

def process_page(page, remove):
    global Verbose_Flag
    global null
    
    d=dict()

    # handle the case of an empty document
    if not page or len(page) == 0:
        return d
    
    # remove material after <hr>
    if remove:
        page=page[page.rfind("<hr>")+1:]

    document = html.document_fromstring(page)
    # raw_text = document.text_content()

    # remove those parts that are not going to be index or otherwise processed
    #
    # exclude regions inside <code> ... </code>
    for bad in document.xpath("//code"):
        bad.getparent().remove(bad)

    # remove <iframe> .. </iframe>
    for bad in document.xpath("//iframe"):
        bad.getparent().remove(bad)

    # process the different elements
    #
    # get the alt text for each image - as this should describe the image
    tmp_path=document.xpath('.//img')
    if tmp_path:
        tmp=[item.get('alt') for item in tmp_path]
        tmp[:] = [item for item in tmp if item != None and item != "\n"]
        if tmp:
            d['img_alt_text']=tmp

    # now that we have the alt strings, remove <img> .. </img>
    for bad in document.xpath("//img"):
        bad.getparent().remove(bad)

    # get figcapations
    tmp_path=document.xpath('.//figcaption')
    if tmp_path:
        tmp=[item.text for item in tmp_path]
        tmp[:] = [item for item in tmp if item != None and item != "\n"]
        if tmp:
            d['figcaption_text']=tmp


    # tmp_path=document.xpath('.//pre')
    # if tmp_path:
    #     tmp=[item.text for item in tmp_path]
    #     tmp[:] = [item for item in tmp if item != None and item != "\n"]
    #     if tmp:
    #         d['pre_text']=tmp
    get_text_for_tag(document, 'pre', d)
    print("d is {}".format(d))

    # # after getting the <pre>...</pre> text - remove it so that it is not further processed
    # for bad in document.xpath("//pre"):
    #     bad.getparent().remove(bad)
    remove_tag(document, 'pre')

    # get the headings at levels 1..4
    tmp_path=document.xpath('.//h1')
    if tmp_path:
        tmp=[item.text for item in tmp_path]
        tmp[:] = [item for item in tmp if item != None and item != "\n"]
        if tmp:
            d['h1_text']=tmp

    tmp_path=document.xpath('.//h2')
    if tmp_path:
        tmp=[item.text for item in tmp_path]
        tmp[:] = [item for item in tmp if item != None and item != "\n"]
        if tmp:
            d['h2_text']=tmp

    tmp_path=document.xpath('.//h3')
    if tmp_path:
        tmp=[item.text for item in tmp_path]
        tmp[:] = [item for item in tmp if item != None and item != "\n"]
        if tmp:
            d['h3_text']=tmp

    tmp_path=document.xpath('.//h4')
    if tmp_path:
        tmp=[item.text for item in tmp_path]
        tmp[:] = [item for item in tmp if item != None and item != "\n"]
        if tmp:
            d['h4_text']=tmp

    # get list items - note that we ignore ul and ol
    tmp_path=document.xpath('.//li')
    if tmp_path:
        tmp=[item.text for item in tmp_path]
        tmp[:] = [item for item in tmp if item != None and item != "\n"]
        if tmp:
            d['list_item_text']=tmp

    # get table cells and headings - note that a empty cell will return a value of null
    # note that we ignore tr, thead, tbody, and table - as we are only interested in the contents of the table or its caption
    tmp_path=document.xpath('.//caption')
    if tmp_path:
        tmp=[item.text for item in tmp_path]
        tmp[:] = [item for item in tmp if item != None and item != "\n"]
        if tmp:
            d['caption_text']=tmp

    tmp_path=document.xpath('.//td')
    if tmp_path:
        tmp=[item.text for item in tmp_path]
        tmp[:] = [item for item in tmp if item != None and item != "\n"]
        if tmp:
            d['table_cell_text']=tmp

    tmp_path=document.xpath('.//th')
    if tmp_path:
        tmp=[item.text for item in tmp_path]
        tmp[:] = [item for item in tmp if item != None and item != "\n"]
        if tmp:
            d['table_heading_text']=tmp

    # get paragraphs
    tmp_path=document.xpath('.//p')
    if tmp_path:
        tmp=[item.text for item in tmp_path]
        tmp[:] = [item for item in tmp if item != None and item != "\n"]
        if tmp:
            d['paragraph_text']=tmp

    tmp_path=document.xpath('.//blockquote')
    if tmp_path:
        tmp=[item.text for item in tmp_path]
        tmp[:] = [item for item in tmp if item != None and item != "\n"]
        if tmp:
            d['blockquote_text']=tmp

    tmp_path=document.xpath('.//q')
    if tmp_path:
        tmp=[item.text for item in tmp_path]
        tmp[:] = [item for item in tmp if item != None and item != "\n"]
        if tmp:
            d['q_text']=tmp

    tmp_path=document.xpath('.//span')
    if tmp_path:
        tmp=[item.text for item in tmp_path]
        tmp[:] = [item for item in tmp if item != None and item != "\n"]
        if tmp:
            d['span_text']=tmp

    #get the different types of emphasized text strong, bold, em, underlined, italics
    tmp_path=document.xpath('.//strong')
    if tmp_path:
        tmp=[item.text for item in tmp_path]
        tmp[:] = [item for item in tmp if item != None and item != "\n"]
        if tmp:
            d['strong_text']=tmp

    tmp_path=document.xpath('.//b')
    if tmp_path:
        tmp=[item.text for item in tmp_path]
        tmp[:] = [item for item in tmp if item != None and item != "\n"]
        if tmp:
            d['b_text']=tmp

    tmp_path=document.xpath('.//em')
    if tmp_path:
        tmp=[item.text for item in tmp_path]
        tmp[:] = [item for item in tmp if item != None and item != "\n"]
        if tmp:
            d['em_text']=tmp

    tmp_path=document.xpath('.//u')
    if tmp_path:
        tmp=[item.text for item in tmp_path]
        tmp[:] = [item for item in tmp if item != None and item != "\n"]
        if tmp:
            d['u_text']=tmp

    tmp_path=document.xpath('.//i')
    if tmp_path:
        tmp=[item.text for item in tmp_path]
        tmp[:] = [item for item in tmp if item != None and item != "\n"]
        if tmp:
            d['i_text']=tmp

    # get superscripts and subscripts
    tmp_path=document.xpath('.//sup')
    if tmp_path:
        tmp=[item.text for item in tmp_path]
        tmp[:] = [item for item in tmp if item != None and item != "\n"]
        if tmp:
            d['sup_text']=tmp

    tmp_path=document.xpath('.//sub')
    if tmp_path:
        tmp=[item.text for item in tmp_path]
        tmp[:] = [item for item in tmp if item != None and item != "\n"]
        if tmp:
            d['sub_text']=tmp

    # for anchors - if there is a title remember it
    tmp_path=document.xpath('.//a[@title]')
    if tmp_path:
        tmp=[item.get('title') for item in tmp_path]
        tmp[:] = [item for item in tmp if item != None and item != "\n"]
        if tmp:
            d['anchor_title_text']=tmp

    # collect text of specially tagged elements with the lang attribute
    tmp_path=document.xpath('//*[@lang]')
    if tmp_path:
        language_specific_tagged_material=list()
        for item in tmp_path:
            entry=dict()
            entry['tag']=item.tag
            entry['lang']=item.get('lang')
            entry['text']=item.text
            language_specific_tagged_material.append(entry)
            # add collected material
        d['lang_specific']=language_specific_tagged_material
        

    if Verbose_Flag:
        print("page is now {}".format(html.tostring(document)))

    return d


def html_url_from_page_url(course_info, page_url):
    if page_url.endswith('.html'):
        page_url=page_url[:-5]
    for m in course_info:
        #print("course_info[m] m={}".format(m))
        for mi in course_info[m]['module_items']:
            #print("course_info[m]['module_items'][mi]={}".format(course_info[m]['module_items'][mi]))
            url=course_info[m]['module_items'][mi].get('page_url', [])
            if url == page_url:
                html_url=course_info[m]['module_items'][mi]['html_url']
                ofset_to_modules=html_url.find('/modules/')
                if ofset_to_modules > 1:
                    trimmed_html_url='..'+html_url[ofset_to_modules:]
                    return [trimmed_html_url, course_info[m]['module_items'][mi]['title']]
                else:
                    return [html_url, course_info[m]['module_items'][mi]['title']]
            else:
                continue
            # else
    return None

def add_words_to_dict(lang, words, url):
    global Verbose_Flag
    global page_entries

    if Verbose_Flag:
        print("(lang={0}, words={1}, url={2})".format(lang, words, url))
        # get or make the dict for the target language
    dict_for_target_lang=page_entries.get(lang, False)
    if not dict_for_target_lang:
        page_entries[lang]=dict()

    if Verbose_Flag:
        print("dict_for_target_lang={}".format(dict_for_target_lang))

    # look up urls for given words in the dict or start an empty list
    url_list_for_words=page_entries[lang].get(words, set())
    url_list_for_words.add(url)
    if Verbose_Flag:
        print("url_list_for_words={}".format(url_list_for_words))

    page_entries[lang][words]=url_list_for_words


def add_words_to_default_dict(words, url):
    global Verbose_Flag
    global page_entries_in_language_of_course
    #
    # look up URLs for given words in the dict or start an empty set
    # sets are used so that the only unique URLs are added
    #  (i.e., if a word is used multiple times on the page, it will only have one URL)
    urls_for_words=page_entries_in_language_of_course.get(words, set())
    urls_for_words.add(url)
    #
    # if numbers separated by commas or spaces, do not index
    #s1=wprds.split(' ')
    
    words=words.strip()
    if len(words) == 0:
        return None        

    # do not index stop words, starting characters to be removed, or numbers
    if (words in StopWords) or (words in starting_characters_to_remove) or is_number(words):
        return None
    else:
        if words.find('yourself') >= 0:
            print("found yourself in {0} of length={1}".format(words, len(words)))
        page_entries_in_language_of_course[words]=urls_for_words
        return words
 
def compute_page_for_tag(tag, heading, json_data, course_info):
    global Verbose_Flag
    global     page_entries_in_language_of_course

    page_entries_in_language_of_course=dict()
    
    for p in json_data:
        data=json_data[p].get(tag, [])
        if data and len(data) > 0:
            for i in data:
                add_words_to_default_dict(i, p)

    if Verbose_Flag:
        print("tag={0}, page_entries_in_language_of_course is {1}".format(tag, page_entries_in_language_of_course))

    # create page for entries in the default lamguage of the course
    page=""
    page=page+'<h3><a id="'+heading+'">'+heading+'</h3><ul>'
    for words in sorted(page_entries_in_language_of_course.keys()):
        page=page+'<li>'+words+'<ul>'
        for p in page_entries_in_language_of_course[words]:
            url=html_url_from_page_url(course_info, p)
            if not url:
                print("could not find URL and title for {}".format(p))
            else:
                page=page+'<li><a href="'+url[0]+'">'+url[1]+'</a></li>'
        page=page+'</ul></li>'
    page=page+'</ul>'
    return page


def cleanup_list(l1):
    global Verbose_Flag
    new_list=list()
    for e in l1:
        if Verbose_Flag:
            print("e: {}".format(e))
        cs=cleanup_string(e)
        if Verbose_Flag:
            print("cs is {}".format(cs))
        if cs:
            new_list.append(cs)
    if Verbose_Flag:
        print("new_list is {}".format(new_list))
    return new_list

#[['Internet', 'Corporation'], ['Assigned', 'Names'], ['Numbers']]
# becomes: ['Internet Corporation'], ['Assigned Names'], ['Numbers']]
def cleanup_two_layer_list(l1):
    global Verbose_Flag
    new_list=list()
    for l2 in l1:
        new_string=''
        for e in l2:
            if Verbose_Flag:
                print("e: {}".format(e))
            cs=cleanup_string(e)
            if Verbose_Flag:
                print("cs is {}".format(cs))
            if cs:
                new_string=new_string+' '+cs
        new_list.append(new_string.strip())
    if Verbose_Flag:
        print("new_list is {}".format(new_list))
    return new_list


def is_number(n):
    try:
        float(n)   # Type-casting the string to `float`.
        # If string is not a valid `float`, 
        # it'll raise `ValueError` exception
    except ValueError:
        return False
    return True

starting_characters_to_remove =[
    u' ',
    u',',
    u':',
    u';',
    u'&',
    u'"',
    u'(',
    u')',
    u'[',
    u']',
    u'{',
    u'}',
    u'+',
    u'-',                       # 0x2d
    u'‒',                       # 0x2012
    u'–',                       # 0x2013
    u'―',                       # 0x2015
    u'--',
    # u'.', # note that we cannot remove a leading period as this might be an example of a domain name
    u'..',
    u'...',
    u'...',
    u'…',
    u'*',
    u'< < <',
    u'†',
    u'‡',
    u'``',
    u"`",
    u"’",
    u'“',
    u"=",
    u'<',
    u'&lt;',
    u'&le;',
    u'&gt;',
    u'&hellip;',
    u'¨',
    u'®',
    u'→',
    u'⇒',
    u'⇨',
    u'⇨ '
    u'∴',
    u'≡',
    u'≤',
    u'✔️',
    u'✔',
    u'✝',
    u'❌ ',
    u'❌',
    u'#',
    ]



ending_characters_to_remove =[
    u',',
    u'.',
    u'!',
    u'?',
    u':',
    u';',
    u'&',
    u'%',
    u"''",
    u'"',                      # a double quote mark
    u"‘",
    u'(',
    u')',
    u'[',
    u']',
    u'{',
    u'}',
    u'-',
    u'[ online',
    u'*',
    u'&dagger;',
    u'†',
    u'✝',
    u'‡',
    u" ’",
    #u' (see',
    u' e.g',
    u"`",
    u"=",
    u'&lt;',
    u'&le;',
    u'&gt;',
    u'&hellip;',
    u'®',
    u'→',
    u'⇒',
    u'&rArr;',
    u'⇨',
    u'∴',
    u'≡',
    u'≤',
    u'✔️',
    u'✔',
    u'❌',
]

def cleanup_string(s):
    s=s.strip()                 # first remove any trailing or leading white space
    if s.endswith(')') and s.endswith('('): #  remove initial and trailing parentheses
        s=cleanup_string(s[1:-1])

    if s.endswith('[') and s.endswith(']'): #  remove initial and trailing brackets
        s=cleanup_string(s[1:-1])

    if s.endswith('{') and s.endswith('}'): #  remove initial and trailing brackets
        s=cleanup_string(s[1:-1])

    for c in ending_characters_to_remove:
        if s.endswith(c):
            s=cleanup_string(s[:-(len(c))])

    for c in starting_characters_to_remove:
        if s.startswith(c):
            s=cleanup_string(s[len(c):])

    if is_number(s):
        return ""
    #
    return s.strip()

Letter_in_Index=[
    u'A',
    u'B',
    u'C',
    u'D',
    u'E',
    u'F',
    u'G',
    u'H',
    u'I',
    u'J',
    u'K',
    u'L',
    u'M',
    u'N',
    u'O',
    u'P',
    u'Q',
    u'R',
    u'S',
    u'T',
    u'U',
    u'V',
    u'W',
    u'X',
    u'Y',
    u'Z',
    u'Å',
    u'Ä',
    u'Ö'
]

def id_in_Index(s):
    return '*'+s+'*'

def label_in_Index(s):
    return '- '+s+' -'


def main():
    global Verbose_Flag
    global Stop_flag
    global page_entries
    global page_entries_in_language_of_course

    parser = optparse.OptionParser()

    parser.add_option('-v', '--verbose',
                      dest="verbose",
                      default=False,
                      action="store_true",
                      help="Print lots of output to stdout"
    )

    parser.add_option('-s', '--stop',
                      dest="stop",
                      default=False,
                      action="store_true",
                      help="split on stopwords with regular expression and not NLTK tokenizer"
    )

    options, remainder = parser.parse_args()

    Verbose_Flag=options.verbose
    Stop_flag=options.stop

    if Verbose_Flag:
        print("ARGV      : {}".format(sys.argv[1:]))
        print("VERBOSE   : {}".format(options.verbose))
        print("REMAINING : {}".format(remainder))

    if (len(remainder) < 2):
        print("Inusffient arguments\n must provide the course number and name of file to process\n")
        sys.exit()

    course_id=remainder[0]
    file_name=remainder[1]

    course_info_file="modules-in-course-{}.json".format(course_id)

    if Verbose_Flag:
        print("processing course_info JSON from {}".format(course_info_file))

    try:
        with open(course_info_file) as json_file:
            course_info=json.load(json_file)
    except:
        print("Unable to open file named {}".format(course_info_file))
        sys.exit()

    if Verbose_Flag:
        print("processing JSON from {}".format(file_name))

    try:
        with open(file_name) as json_file:
            json_data=json.load(json_file)
    except:
        print("Unable to open file named {}".format(file_name))
        sys.exit()


    # load words for the course, if the file exists
    course_words_file="words-for-course-{}.json".format(course_id)
    if Verbose_Flag:
        print("loading course words from {}".format(course_words_file))

    try:
        with open(course_words_file) as json_file:
            course_words=json.load(json_file)
    except:
        #print("Unable to open file named {}".format(course_words_file))
        print("No file {} - so no course words to specially process".format(course_words_file))
        course_words=dict()
        course_words['words_to_ignore']=[] # empty list

    if Verbose_Flag:
        print("course_words is {}".format(course_words))

    # for each of the stop words add a version with an initial capital letter - so that these can also be removed
    oldStopWords=StopWords.copy()
    for w in oldStopWords:
        if len(w) > 0:
            capitalized_word=w[0].upper()+w[1:]
            StopWords.append(capitalized_word)

    if Verbose_Flag:
        print("Extended StopWords are {}".format(StopWords))

    print("Processing language specific elements")

    # page_entries will have the structure
    # {"sv_se": {
    #            "words1": (url1, url2, ...),
    #            "words2": (url1, url2, ...),
    #           },
    # "no_nb": {
    #            "words3": (url1, url2, ...),
    #            "words4": (url1, url2, ...),
    #           },
    # ...
    # }
    page_entries=dict()
    

    for p in json_data:
        # [{"tag": "span", "lang": "sv_se", "text": "
        lang_specific_data=json_data[p].get("lang_specific", [])
        if lang_specific_data and len(lang_specific_data) > 0:
            if Verbose_Flag:
                print("lang_specific_data is {0}, p={1}".format(lang_specific_data, p))
            for i in lang_specific_data:
                add_words_to_dict(i['lang'], i['text'], p)

    if Verbose_Flag:
        print("page_entries is {}".format(page_entries))

    # create page
    page='<h3><a id="Foreign_words_and_phrases">Foreign words and phrases</h3>'
    for lang in sorted(page_entries.keys(), key=lambda v: (v.casefold(), v)):
        page=page+'<h3>'+lang+': '+language_info[lang]['en']+': '+language_info[lang]['sv']+'</h3><ul>'
        for words in sorted(page_entries[lang].keys(), key=lambda v: (v.casefold(), v)):
            page=page+'<li>'+words+'<ul>'
            for p in page_entries[lang][words]:
                url=html_url_from_page_url(course_info, p)
                if not url:
                    print("could not find URL and title for {}".format(p))
                else:
                    page=page+'<li><a href="'+url[0]+'"><span lang="'+lang+'">'+url[1]+'</span></a></li>'
            page=page+'</ul></li>'
        page=page+'</ul>'

    if Verbose_Flag:
        print("page is {}".format(page))


    print("Processing figcaption text")
    page_figcaption=compute_page_for_tag('figcaption_text', "Figure captions", json_data, course_info)
    if Verbose_Flag:
        print("page_figcaption is {}".format(page_figcaption))
    page=page+page_figcaption

    print("Processing caption text")
    page_caption=compute_page_for_tag('caption_text', "Table captions", json_data, course_info)
    if Verbose_Flag:
        print("page_caption is {}".format(page_caption))
    page=page+page_caption

    if Verbose_Flag:
        print("page is {}".format(page))
        
    save_page=page              # save current page contents

    print("Processing all of the word groups")
    # process all of the things that were extracted and index them
    page_entries=dict()

    for p in json_data:
        format("p={}".format(p))
        d1=json_data[p]
        list_of_strings=list()
        for de in d1:
            if de == 'pre_text': # do not index <pre> tagged content
                continue
            l=json_data[p][de]
            if Verbose_Flag:
                print("de is {0}, l is {1}".format(de, l))
            if de == 'span_text':
                if Verbose_Flag:
                    print("special case of span l={}".format(l))
                if len(l) == 0:
                    continue
                elif len(l) == 1: 
                    # check for single characters to skip
                    if l[0].strip() in starting_characters_to_remove:
                        if Verbose_Flag:
                            print("special case of span with single element in l[0]={0}, len={1}".format(l[0], len(l[0])))
                        continue
                    else:
                        add_words_to_default_dict(l[0], p)
                else:
                    for s in l:
                        add_words_to_default_dict(s, p)
                continue
            # do not index superscripts or subscripts
            if de == 'sup_text' or de == 'sub_text':
                continue
            # other cases
            if Verbose_Flag:
                print("de is {0}, l is {1}".format(de, l))
            for s in l:
                if Verbose_Flag:
                    print("s={}".format(s))
                    
                if isinstance(s, dict):
                    s_text=s.get('text', '')
                    s_lang=s.get('lang', [])
                    if s_text:
                        if s_lang:
                            add_words_to_dict(s_lang, s_text, p)
                        else:
                            add_words_to_default_dict(s_text, p)
                    continue

                if isinstance(s, str):
                    l1=split_into_sentences(s)
                    if Verbose_Flag:
                        print("l1 is {}".format(l1))
                    if len(l1) >= 1:
                        if Verbose_Flag:
                            print("l1 is longer than 1")
                        for s1 in l1:
                            if Verbose_Flag:
                                print("s1 is {}".format(s1))
                            l2=split_on_stop_words(s1)
                            if Verbose_Flag:
                                print("l2 is {}".format(l2))
                            l3=cleanup_two_layer_list(l2)
                            for s3 in l3:
                                if Verbose_Flag:
                                    print("s3 is {}".format(s3))
                                add_words_to_default_dict(s3, p)
                    else:
                        l2=split_on_stop_words(s)
                        l3=cleanup_two_layer_list(l2)
                        for words in l3:
                            w2=cleanup_string(words)
                            if Verbose_Flag:
                                print("w2 is {}".format(w2))
                            add_words_to_default_dict(w2, p)
                    continue
                else:
                    print("not a dict or str - s is {}".format(s))
        else:
            if Verbose_Flag:
                print("There is no content to index on page: {}".format(p))
            continue

    if Verbose_Flag:
        print("page_entries is {}".format(page_entries))

    # create index page
    index_page=""
    # added quick references to the different parts of the index
    #<ul>
    #    <li><a href="#*A*"><strong>*A*</strong></a></li>
    #    <li><a href="#*B*"><strong>*B*</strong></a></li>
    # </ul>
    #
    # Use id_in_Index(s) to name the IDs

    # At each letter one needs to add:
    # </ul><a id="*A*" name="*A*"></a><h3>- A -</h3><ul>
    #
    # Use label_in_Index(s) to name the visible heading

    index_page_heading='<h3><a id="Quick_Index">Quick Index</h3><ul>'
    for l in Letter_in_Index:
        index_page_heading=index_page_heading+'<li><a href="#'+id_in_Index(l)+'"><strong>'+label_in_Index(l)+'</strong></a></li>'
    index_page_heading=index_page_heading+'</ul>'

    index_page=index_page+'<h3>groups of words</h3><ul>'
    current_index_letter=""
    previous_word=""
    url_entry=""    

    url_dict=dict()

    global page_entries_in_language_of_course
    #merge entries
    sorted_page_entries=sorted(page_entries_in_language_of_course.keys(), key=lambda v: (v.casefold(), v))
    for words in sorted_page_entries:
        #merge entries
        for w in course_words['words_to_merge']:
            if words in course_words['words_to_merge'][w]:
                if Verbose_Flag:
                    print("words is {0} and w is {1}".format(words, w))
                    print("merging for {}".format(words))

                urls_for_words=page_entries_in_language_of_course.get(words, set())
                if Verbose_Flag:
                    print("page_entries_in_language_of_course[words] is {}".format(urls_for_words))
                if len(urls_for_words) > 0:
                    if Verbose_Flag:
                        print("clearing page entry for {}".format(words))
                    page_entries_in_language_of_course[words]=set()
                    unified_url_entries=page_entries_in_language_of_course.get(w, set())
                    page_entries_in_language_of_course[w]=unified_url_entries.union(urls_for_words)
                    if Verbose_Flag:
                        print("unified_url_entries is {}".format(unified_url_entries))

    # the casefold sorts upper and lower case together, but gives a stable result
    # see Christian Tismer, Sep 13 '19 at 12:15, https://stackoverflow.com/questions/13954841/sort-list-of-strings-ignoring-upper-lower-case
    for words in sorted(page_entries_in_language_of_course.keys(), key=lambda v: (v.casefold(), v)):
        # ignore words in the course's 'words_to_ignore' list
        if words in course_words['words_to_ignore']:
            print("ignoring {}".format(words))
            continue

        # if the previous word was an acronym or the new word is different, output the record
        if previous_word.isupper() or words.casefold() != previous_word:
            previous_word=words.casefold()
            #if len(url_entry) > 0:  # only add an entry for this word if there is atleast one URL
            if len(url_dict)> 0:
                for d in sorted(url_dict, key=url_dict.get, reverse=False):
                    if d == 'Learning outcomes' or d == 'Learning Outcomes':
                        continue
                    url_entry=url_entry+'<li><a href="'+url_dict[d]+'">'+d+'</a></li>'
                
                index_page=index_page+word_entry+url_entry+'</ul></li>'
            url_entry=""
            url_dict=dict()
            print("new words={}".format(words))
        
        if len(words) == 0:
            print("words={0} and len(words)={1}".format(words, len(words)))
        first_letter=words[0].upper()
        if (first_letter in Letter_in_Index) and (first_letter != current_index_letter):
            if Verbose_Flag:
                print("first_letter={0} current_index_letter={1}".format(first_letter,current_index_letter))
            current_index_letter=first_letter
            index_page=index_page+'</ul><a id="'+id_in_Index(current_index_letter)+'" name="'+id_in_Index(current_index_letter)+'"></a><h3>'+label_in_Index(current_index_letter)+'</h3><ul>'

        word_entry='<li>'+words+'<ul>'
        for p in page_entries_in_language_of_course[words]:
            url=html_url_from_page_url(course_info, p)
            if not url:
                print("for words '{0}' could not find URL and title for page {1}".format(words, p))
            else:
                url_dict[url[1]]=url[0]

    index_page=index_page+'</ul>'

    if Verbose_Flag:
        print("index_page is {}".format(index_page))

    page_heading='<h3>Automatically extracted index information</h3><ul>'
    page_heading=page_heading+'<li><a href="#Foreign_words_and_phrases">Foreign_words_and_phrases</li>'
    page_heading=page_heading+'<li><a href="#Figure captions">Figure captions</li>'
    page_heading=page_heading+'<li><a href="#Table captions">Table captions</li>'
    page_heading=page_heading+'<li><a href="#Quick_Index">Quick Index</li></ul>'

    page=page_heading+save_page+index_page_heading+index_page

    print("sizes index_page={0} ({3} MB), page_caption={1}, save_page={2}".format(len(index_page),
                                                                                  len(page_caption),
                                                                                  len(save_page),
                                                                                  (len(index_page)/(1024*1024))))

    # write out body of response as a .html page
    new_file_name="stats_for_course-{}.html".format(course_id)
    with open(new_file_name, 'wb') as f:
        encoded_output = bytes(page, 'UTF-8')
        f.write(encoded_output)




if __name__ == "__main__": main()

