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
    "de_de": {'en': '<span lang="en_us">German</span>',    'sv': '<span lang="sv_se">Tyska</span>'},
    "no_nb": {'en': '<span lang="en_us">Norwegian</span>', 'sv': '<span lang="sv_se">Norska</span>'},
    "sv_se": {'en': '<span lang="en_us">Swedish</span>',   'sv': '<span lang="sv_se">Svenska</span>'},
    }

StopWords=[
    u'a',
    u'à',
    u'able',
    u'about',
    u'above',
    u'after',
    u'against',
    u'all',
    u'allows',
    u'along',
    u'already',
    u'also',
    u'although',
    u'an',
    u'and',
    u'another',
    u'any',
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
    u'on',
    u'once',
    u'one',
    u'only',
    u'or',
    u'other',
    u'others',
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
    u'there',
    u'theirs',
    u'them',
    u'themselves',
    u'then',
    u'there',
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
    u'your'
    u'yourself',
    u'yourselves'
    ]

punctuation_list=[
    u'.',                       # add some punctuation to this list
    u','
    u';'
    u'?',
    u'!',
    u'\t'
    u'\n',
    u'⇒',
    u'…'

]

def split_into_words(txt):
    return re.findall(r"[\w']+", txt)

def split_on_stop_words(s1):
    global Verbose_Flag
    output_list=list()
    working_list=list()
    lower_case_next_word=True
    #words=split_into_words(s1)
    words=nltk.word_tokenize(s1)
    for w in words:
        if len(w) > 1 and w.isupper():         # preserve aconyms
            lower_case_next_word=False
        if lower_case_next_word and w[0].isupper(): # if the first word in a sentence is capitalized, then lower case it
            #w=w.lower()                             # needs a better tests as this is too agressive
            lower_case_next_word=False
        if w in punctuation_list:
            lower_case_next_word=True
        if (w not in StopWords) and (w not in punctuation_list):
            working_list.append(w)
        else:
            output_list.append(working_list)
            working_list=list()
        if Verbose_Flag:
            print("w={0} lower_case_next_word={1}".format(w, lower_case_next_word))
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

    # get table cells and headings - not that a empty cell will return a value of null
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

    tmp_path=document.xpath('.//pre')
    if tmp_path:
        tmp=[item.text for item in tmp_path]
        tmp[:] = [item for item in tmp if item != None and item != "\n"]
        if tmp:
            d['pre_text']=tmp

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
                return [course_info[m]['module_items'][mi]['html_url'], course_info[m]['module_items'][mi]['title']]
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
    page_entries_in_language_of_course[words]=urls_for_words

 
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
    page=page+'<h3>'+heading+'</h3><ul>'
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

def is_number(n):
    try:
        float(n)   # Type-casting the string to `float`.
                   # If string is not a valid `float`, 
                   # it'll raise `ValueError` exception
    except ValueError:
        return False
    return True

starting_characters_to_remove =[
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
    u'-',
    u'--',
    # u'.', # note that we cannot remove a leading period as this might be an example of a domain name
    u'..',
    u'...',
    u'...',
    u'*',
    u'< < <',
    ]


ending_characters_to_remove =[
    u',',
    u'.',
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



def main():
    global Verbose_Flag
    global page_entries
    global page_entries_in_language_of_course

    parser = optparse.OptionParser()

    parser.add_option('-v', '--verbose',
                      dest="verbose",
                      default=False,
                      action="store_true",
                      help="Print lots of output to stdout"
    )

    options, remainder = parser.parse_args()

    Verbose_Flag=options.verbose

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


    # for each of the stop words add a version with an initial capital letter - so that these can also be removed
    oldStopWords=StopWords.copy()
    for w in oldStopWords:
        if len(w) > 1:
            capitalized_word=w[0].upper()+w[1:]
            StopWords.append(capitalized_word)

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
    page=""
    for lang in sorted(page_entries.keys()):
        page=page+'<h3>'+lang+': '+language_info[lang]['en']+': '+language_info[lang]['sv']+'</h3><ul>'
        for words in sorted(page_entries[lang].keys()):
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
    page_figcaption=compute_page_for_tag('figcaption_text', "Figure caption text", json_data, course_info)
    if Verbose_Flag:
        print("page_figcaption is {}".format(page_figcaption))
    page=page+page_figcaption

    print("Processing caption text")
    page_caption=compute_page_for_tag('caption_text', "Caption text", json_data, course_info)
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
                print("l is {}".format(l))
            for s in l:
                if Verbose_Flag:
                    print("s={}".format(s))
                
                if isinstance(s, str):
                    l1=split_on_stop_words(s)
                else:
                    s_prime=s.get('text', '')
                    if s_prime:
                        l1=split_on_stop_words(s_prime)
                    else:
                        continue
                if Verbose_Flag:
                    print("l1 is {}".format(l1))
                c1=combine_sublists_into_strings(l1)
                if Verbose_Flag:
                    print("c1 is {}".format(c1))
                c2=cleanup_list(c1)
                if c2:
                    list_of_strings.extend(c2)
        if Verbose_Flag:
            print("list_of_strings is {}".format(list_of_strings))

        if list_of_strings and len(list_of_strings) > 0:
            if Verbose_Flag:
                print("o={}".format(p))
            for words in list_of_strings:
                add_words_to_default_dict(words, p)
        else:
            if Verbose_Flag:
                print("There is no content to index on page: {}".format(p))
            continue

    if Verbose_Flag:
        print("page_entries is {}".format(page_entries))

    # create page
    page=""
    page=page+'<h3>groups of words</h3><ul>'
    for words in sorted(page_entries_in_language_of_course.keys()):
        word_entry='<li>'+words+'<ul>'
        url_entry=""
        for p in page_entries_in_language_of_course[words]:
            url=html_url_from_page_url(course_info, p)
            if not url:
                print("for words '{0}' could not find URL and title for page {1}".format(words, p))
            else:
                url_entry=url_entry+'<li><a href="'+url[0]+'">'+url[1]+'</a></li>'
        if len(url_entry) > 0:  # only add an entry for this word if there is atleast one URL
            page=page+word_entry+url_entry+'</ul></li>'
    page=page+'</ul>'

    if Verbose_Flag:
        print("page is {}".format(page))

    page=save_page+page

    # write out body of response as a .html page
    new_file_name="stats_for_course-{}.html".format(course_id)
    with open(new_file_name, 'wb') as f:
        encoded_output = bytes(page, 'UTF-8')
        f.write(encoded_output)




if __name__ == "__main__": main()

