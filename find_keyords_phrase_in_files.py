#!/usr/bin/python3
#
# ./find_keyords_phrase_in_files.py directory
# 
# it outputs a file with the name keywords_and_phrases_xx.json from the *-html files in the directory
#
# G. Q: Maguire Jr.
#
# 2020.03.30
#
# commands to use:
#
# ./modules-items-in-course.py 17234
# ./find_keyords_phrase_in_files.py -r /tmp/testdik1552
# ./create_page_from_json.py -s 17234 keywords_and_phrases_testdik1552.json
# cp ../Canvas-tools/stats_for_course-17234.html test-page-3.html
# ./ccreate.py https://kth.instructure.com/courses/11/pages/test-page-3 "Test page 3"


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


def get_text_for_tag(document, tag, dir):
    tag_xpath='.//'+tag
    text_dir=tag+'_text'
    tmp_path=document.xpath(tag_xpath)
    if tmp_path:
        # remove all inline-ref and dont-index spans
        tmp=[item.text for item in tmp_path]
        tmp[:] = [item for item in tmp if item != None and item != "\n"]
        if tmp:
            dir[text_dir]=tmp

def remove_tag(document, tag):
    tag_xpath='//'+tag
    for bad in document.xpath(tag_xpath):
        bad.getparent().remove(bad)

def remove_inline_and_dont_index_tags(str1):
    document2 = html.document_fromstring(str1)
    # remove span class="inline-ref">
    for bad in document2.xpath("//span[contains(@class, 'inline-ref')]"):
        bad.getparent().remove(bad)
   # remove span class="dont-index">
    for bad in document2.xpath("//span[contains(@class, 'dont-index')]"):
        bad.getparent().remove(bad)
    return html.tostring(document2, encoding=str, method="text", pretty_print=False )

def process_page(page_name, page, remove):
    global Verbose_Flag
    global null
    
    d=dict()

    if Verbose_Flag:
        print("processing page named: {}".format(page_name))
    # handle the case of an empty document
    if not page or len(page) == 0:
        return d
    
    # remove material after <hr>
    if remove:
        index=page.find("<hr>")
        if index >= 0:
            page=page[:index]
            if Verbose_Flag:
                print("<hr> found at {0} in {1}".format(index, page_name))

        index=page.find("<hr />")
        if index >= 0:
            page=page[:index]
            if Verbose_Flag:
                print("<hr /> found at {0} in {1}".format(index, page_name))


    # handle the case of an empty document
    if not page or len(page) == 0:
        return d

    document = html.document_fromstring(page)
    # raw_text = document.text_content()

    # remove those parts that are not going to be index or otherwise processed
    #
    # # exclude regions inside <code> ... </code>
    # for bad in document.xpath("//code"):
    #     bad.getparent().remove(bad)
    # exclude regions inside <code> ... </code>
    remove_tag(document, 'code')

    # remove <iframe> .. </iframe>
    # for bad in document.xpath("//iframe"):
    #     bad.getparent().remove(bad)
    remove_tag(document, 'iframe')

    # remove span class="inline-ref">
    if remove:
        for bad in document.xpath("//span[contains(@class, 'inline-ref')]"):
            bad.getparent().remove(bad)

    # remove span class="dont-index">
    if remove:
        for bad in document.xpath("//span[contains(@class, 'dont-index')]"):
            bad.getparent().remove(bad)

    # process the different elements
    #
    # get the alt text for each image - as this should describe the image
    tmp_path=document.xpath('.//img')
    if tmp_path:
        # note remove the inline-ref and dontindex spans
        tmp=[remove_inline_and_dont_index_tags(item.get('alt')) for item in tmp_path]
        # note: leave out the LaTeX alternatives
        tmp[:] = [item for item in tmp if item != None and item != "\n" and not item.startswith('LaTeX:')]
        if tmp:
            d['img_alt_text']=tmp

    # get figcapations
    # tmp_path=document.xpath('.//figcaption')
    #if tmp_path:
    #     tmp=[item.text for item in tmp_path]
    #     tmp[:] = [item for item in tmp if item != None and item != "\n"]
    #     if tmp:
    #         d['figcaption_text']=tmp
    get_text_for_tag(document, 'figcaption', d)

    # get the headings at levels 1..4
    # tmp_path=document.xpath('.//h1')
    # if tmp_path:
    #     tmp=[item.text for item in tmp_path]
    #     tmp[:] = [item for item in tmp if item != None and item != "\n"]
    #     if tmp:
    #         d['h1_text']=tmp
    get_text_for_tag(document, 'h1', d)

    # tmp_path=document.xpath('.//h2')
    # if tmp_path:
    #     tmp=[item.text for item in tmp_path]
    #     tmp[:] = [item for item in tmp if item != None and item != "\n"]
    #     if tmp:
    #         d['h2_text']=tmp
    get_text_for_tag(document, 'h2', d)

    # tmp_path=document.xpath('.//h3')
    # if tmp_path:
    #     tmp=[item.text for item in tmp_path]
    #     tmp[:] = [item for item in tmp if item != None and item != "\n"]
    #     if tmp:
    #         d['h3_text']=tmp
    get_text_for_tag(document, 'h3', d)

    # tmp_path=document.xpath('.//h4')
    # if tmp_path:
    #     tmp=[item.text for item in tmp_path]
    #     tmp[:] = [item for item in tmp if item != None and item != "\n"]
    #     if tmp:
    #         d['h4_text']=tmp
    get_text_for_tag(document, 'h4', d)

    # # get list items - note that we ignore ul and ol
    # tmp_path=document.xpath('.//li')
    # if tmp_path:
    #     tmp=[item.text for item in tmp_path]
    #     tmp[:] = [item for item in tmp if item != None and item != "\n"]
    #     if tmp:
    #         d['list_item_text']=tmp
    get_text_for_tag(document, 'li', d)

    # get table cells and headings - not that a empty cell will return a value of null
    # note that we ignore tr, thead, tbody, and table - as we are only interested in the contents of the table or its caption
    # tmp_path=document.xpath('.//caption')
    # if tmp_path:
    #     tmp=[item.text for item in tmp_path]
    #     tmp[:] = [item for item in tmp if item != None and item != "\n"]
    #     if tmp:
    #         d['caption_text']=tmp
    get_text_for_tag(document, 'caption', d)

    # tmp_path=document.xpath('.//td')
    # if tmp_path:
    #     tmp=[item.text for item in tmp_path]
    #     tmp[:] = [item for item in tmp if item != None and item != "\n"]
    #     if tmp:
    #         d['table_cell_text']=tmp
    get_text_for_tag(document, 'td', d)


    # tmp_path=document.xpath('.//th')
    # if tmp_path:
    #     tmp=[item.text for item in tmp_path]
    #     tmp[:] = [item for item in tmp if item != None and item != "\n"]
    #     if tmp:
    #         d['table_heading_text']=tmp
    get_text_for_tag(document, 'th', d)


    # get paragraphs
    # tmp_path=document.xpath('.//p')
    # if tmp_path:
    #     tmp=[item.text for item in tmp_path]
    #     tmp[:] = [item for item in tmp if item != None and item != "\n"]
    #     if tmp:
    #         d['paragraph_text']=tmp
    get_text_for_tag(document, 'p', d)

    # tmp_path=document.xpath('.//pre')
    # if tmp_path:
    #     tmp=[item.text for item in tmp_path]
    #     tmp[:] = [item for item in tmp if item != None and item != "\n"]
    #     if tmp:
    #         d['pre_text']=tmp
    get_text_for_tag(document, 'pre', d)

    # tmp_path=document.xpath('.//blockquote')
    # if tmp_path:
    #     tmp=[item.text for item in tmp_path]
    #     tmp[:] = [item for item in tmp if item != None and item != "\n"]
    #     if tmp:
    #         d['blockquote_text']=tmp
    get_text_for_tag(document, 'blockquote', d)

    # tmp_path=document.xpath('.//q')
    # if tmp_path:
    #     tmp=[item.text for item in tmp_path]
    #     tmp[:] = [item for item in tmp if item != None and item != "\n"]
    #     if tmp:
    #         d['q_text']=tmp
    get_text_for_tag(document, 'q', d)
    
    # tmp_path=document.xpath('.//span')
    # if tmp_path:
    #     tmp=[item.text for item in tmp_path]
    #     tmp[:] = [item for item in tmp if item != None and item != "\n"]
    #     if tmp:
    #         d['span_text']=tmp
    get_text_for_tag(document, 'span', d)

    #get the different types of emphasized text strong, bold, em, underlined, italics
    # tmp_path=document.xpath('.//strong')
    # if tmp_path:
    #     tmp=[item.text for item in tmp_path]
    #     tmp[:] = [item for item in tmp if item != None and item != "\n"]
    #     if tmp:
    #         d['strong_text']=tmp
    get_text_for_tag(document, 'strong', d)
    
    # tmp_path=document.xpath('.//b')
    # if tmp_path:
    #     tmp=[item.text for item in tmp_path]
    #     tmp[:] = [item for item in tmp if item != None and item != "\n"]
    #     if tmp:
    #         d['b_text']=tmp
    get_text_for_tag(document, 'b', d)
    
    # tmp_path=document.xpath('.//em')
    # if tmp_path:
    #     tmp=[item.text for item in tmp_path]
    #     tmp[:] = [item for item in tmp if item != None and item != "\n"]
    #     if tmp:
    #         d['em_text']=tmp
    get_text_for_tag(document, 'em', d)

    # tmp_path=document.xpath('.//u')
    # if tmp_path:
    #     tmp=[item.text for item in tmp_path]
    #     tmp[:] = [item for item in tmp if item != None and item != "\n"]
    #     if tmp:
    #         d['u_text']=tmp
    get_text_for_tag(document, 'u', d)
    
    # tmp_path=document.xpath('.//i')
    # if tmp_path:
    #     tmp=[item.text for item in tmp_path]
    #     tmp[:] = [item for item in tmp if item != None and item != "\n"]
    #     if tmp:
    #         d['i_text']=tmp
    get_text_for_tag(document, 'i', d)
    
    # get superscripts and subscripts
    # tmp_path=document.xpath('.//sup')
    # if tmp_path:
    #     tmp=[item.text for item in tmp_path]
    #     tmp[:] = [item for item in tmp if item != None and item != "\n"]
    #     if tmp:
    #         d['sup_text']=tmp
    get_text_for_tag(document, 'sup', d)
    
    # tmp_path=document.xpath('.//sub')
    # if tmp_path:
    #     tmp=[item.text for item in tmp_path]
    #     tmp[:] = [item for item in tmp if item != None and item != "\n"]
    #     if tmp:
    #         d['sub_text']=tmp
    get_text_for_tag(document, 'sub', d)

    # for anchors - if there is a title remember it
    tmp_path=document.xpath('.//a[@title]')
    if tmp_path:
        tmp=[remove_inline_and_dont_index_tags(item.get('title')) for item in tmp_path]
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


def main():
    global Verbose_Flag
    global null

    parser = optparse.OptionParser()

    parser.add_option('-v', '--verbose',
                      dest="verbose",
                      default=False,
                      action="store_true",
                      help="Print lots of output to stdout"
    )

    parser.add_option('-r', '--remove',
                      dest="remove",
                      default=False,
                      action="store_true",
                      help="remove notes after <hr>"
    )

    options, remainder = parser.parse_args()

    Verbose_Flag=options.verbose
    Remove_Flag=options.remove

    if Verbose_Flag:
        print("ARGV      : {}".format(sys.argv[1:]))
        print("VERBOSE   : {}".format(options.verbose))
        print("REMAINING : {}".format(remainder))
        print("Remove_flag : {}".format(Remove_Flag))

    if (len(remainder) < 1):
        print("Inusffient arguments\n must provide name of directory to process\n")
        sys.exit()

    dir_name=remainder[0]
    if Verbose_Flag:
        print("processing directory {}".format(dir_name))

    null = None
    page_data=dict()
        
    for html_file in pathlib.Path(dir_name).glob('*.html'):
        if Verbose_Flag:
            print("processing {}".format(html_file))
        # do something with each file
        with open(html_file) as input_page_file:
            page = input_page_file.read()
            page_data[os.path.basename(html_file)]=process_page(html_file, page, Remove_Flag)

    output_filename='keywords_and_phrases_'+dir_name[dir_name.rfind("/")+1:]+'.json'
    try:
        with open(output_filename, 'w') as json_file:
            json.dump(page_data, json_file)
    except:
        print("error trying to write to {}".format(output_filename))


if __name__ == "__main__": main()

