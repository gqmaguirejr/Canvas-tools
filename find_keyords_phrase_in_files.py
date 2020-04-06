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

    # remove span class="inline-ref">
    if remove:
        for bad in document.xpath("//span[contains(@class, 'inline-ref')]"):
            bad.getparent().remove(bad)

    # remove span class="dont-index">
    if remove:
        for bad in document.xpath("//span[contains(@class, 'dont-index')]"):
            bad.getparent().remove(bad)


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

