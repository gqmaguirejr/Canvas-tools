#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# ./extract_anchor_elements_from_rawHTML_files.py  course_id
# 
# The content is taken from the wikipages in the specified course have been saved in a file and
# the pages are separated with lines, such as:
# ⌘⏩routing-table-search-classless⏪
# where the page URL is between the markers. This makes it easy to look at the source material, for example when tryign to locate misspellings.
# The idea is to read in this material and extract information about all of the anchor elements.
#
# Example:
# ./extract_anchor_elements_from_rawHTML_files.py  --dir Course_41668 41668
#
# G. Q: Maguire Jr.
#
# 2024.01.12
#
# with the option "-v" or "--verbose" you get lots of output - showing in detail the operations of the program
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

start_marker='\n⌘⏩'
end_marker='⏪\n'

def main():
    global Verbose_Flag

    parser = optparse.OptionParser()

    parser.add_option('-v', '--verbose',
                      dest="verbose",
                      default=False,
                      action="store_true",
                      help="Print lots of output to stdout"
    )

    parser.add_option("--dir", dest="dir_prefix",
                      default='./',
                      help="read configuration from FILE", metavar="FILE")


    options, remainder = parser.parse_args()
    Verbose_Flag=options.verbose
    if Verbose_Flag:
        print("ARGV      : {}".format(sys.argv[1:]))
        print("VERBOSE   : {}".format(options.verbose))
        print("REMAINING : {}".format(remainder))
        print("Configuration file : {}".format(options.config_filename))

    # compute the directory prefix for files to be used for the program's I/O
    directory_prefix=options.dir_prefix
    if not directory_prefix.endswith('/'):
        directory_prefix=directory_prefix+'/'
    if Verbose_Flag:
        print(f'{directory_prefix=}')

    if len(remainder) < 1:
        print("Insuffient arguments\n must provide course_id")
        return

    course_id=remainder[0]

    # save all the raw HTML
    new_file_name=f'{directory_prefix}unique_words-for-course-raw_HTML-{course_id}.txt'
    with open(new_file_name, 'r') as f:
        total_raw_HTML=f.read()

    if Verbose_Flag:
        print(f'{len(total_raw_HTML)}')

    html_pages=dict()
    
    parts=total_raw_HTML.split(start_marker)
    if Verbose_Flag:
        print(f'number of parts: {len(parts)}')
    #print(f'last of parts: {parts[len(parts)-1]}')
    for p in parts:
        split_part=p.split(end_marker)
        if len(split_part) == 2:
            front=split_part[0]
            back=split_part[1]
            if Verbose_Flag:
                print(f'{front=}')
            html_pages[front]=back

    html_anchors=dict()

    for indx, p in enumerate(html_pages):
        if Verbose_Flag:
            print(f'{indx=} {p=} {len(html_pages[p])=}')
        body=html_pages[p]
        document = html.document_fromstring(body)
        
        entries=list()
        for anchor in document.xpath("*//a"):
            if Verbose_Flag:
                print(f'{anchor.attrib=}')
            entry=dict()
            for at in anchor.attrib:
                if at not in ['target', 'data-canvas-previewable', 'style']:
                    if at == 'class':
                        short_at_value=anchor.attrib.get(at)
                        short_at_value=short_at_value.replace('inline_disabled', '').strip()
                        short_at_value=short_at_value.replace('instructure_scribd_file', '').strip()
                        if len(short_at_value) > 0:
                            entry[at]=short_at_value
                    else:
                        entry[at]=anchor.attrib.get(at)
            entries.append(entry)
        html_anchors[p]=entries

    if Verbose_Flag:
        print(f'{html_anchors=}')
    new_file_name=f'{directory_prefix}anchors-{course_id}.json'
    with open(new_file_name, 'w') as f:
        f.write(json.dumps(html_anchors, ensure_ascii=False))
    print(f'output {new_file_name}')

if __name__ == "__main__": main()
