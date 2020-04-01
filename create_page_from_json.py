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

language_info={
    "de_de": {'en': '<span lang="en_us">German</span>',    'sv': '<span lang="sv_se">Tyska</span>'},
    "no_nb": {'en': '<span lang="en_us">Norwegian</span>', 'sv': '<span lang="sv_se">Norska</span>'},
    "sv_se": {'en': '<span lang="en_us">Swedish</span>',   'sv': '<span lang="sv_se">Svenska</span>'},
    }

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
        d['lang_specifiv']=language_specific_tagged_material
        

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

    print("(lang={0}, words={1}, url={2})".format(lang, words, url))
    # get or make the dict for the target language
    dict_for_target_lang=page_entries.get(lang, False)
    if not dict_for_target_lang:
        page_entries[lang]=dict()

    print("dict_for_target_lang={}".format(dict_for_target_lang))

    # look up urls for given words in the dict or start an empty list
    url_list_for_words=page_entries[lang].get(words, list())
    url_list_for_words.append(url)
    print("url_list_for_words={}".format(url_list_for_words))

    page_entries[lang][words]=url_list_for_words


def main():
    global Verbose_Flag
    global page_entries

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
            print("lang_specific_data is {0}, p={1}".format(lang_specific_data, p))
            html_url_and_title=html_url_from_page_url(course_info, p)
            if html_url_and_title:
                print("html_url_and_title={}".format(html_url_and_title))
                for i in lang_specific_data:
                    add_words_to_dict(i['lang'], i['text'], html_url_and_title)
            else:
                print("did not find matching entry for {}".format(p))

    print("page_entries is {}".format(page_entries))

    # create page
    page=""
    for lang in sorted(page_entries.keys()):
        page=page+'<h3>'+lang+': '+language_info[lang]['en']+': '+language_info[lang]['sv']+'</h3><ul>'
        for words in sorted(page_entries[lang].keys()):
            page=page+'<li>'+words+'<ul>'
            for url in page_entries[lang][words]:
                page=page+'<li><a href="'+url[0]+'"><span lang="'+lang+'">'+url[1]+'</span></a></li>'
            page=page+'</ul></li>'
        page=page+'</ul>'

    print("page is {}".format(page))
    # write out body of response as a .html page
    new_file_name="stats_for_course-{}.html".format(course_id)
    with open(new_file_name, 'wb') as f:
        encoded_output = bytes(page, 'UTF-8')
        f.write(encoded_output)




if __name__ == "__main__": main()

