#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# ./language_tag_a_course.py course_id lang
#
# Output: To go throught a course and add HTML language attribute to relevant elements
#
#
# with the option "-v" or "--verbose" you get lots of output - showing in detail the operations of the program
#
# Can also be called with an alternative configuration file:
# ./language_tag_a_course.py --config config-test.json  course_id lang
#
# Example:
# ./language_tag_a_course.py 751 en
#
# ./language_tag_a_course.py 53524 sv
#
# 
# G. Q. Maguire Jr.
#
# based on earlier edit_modules_items_in_a_module_in_a_course.py
#
# 2021-09-28
#

import requests, time
import pprint
import optparse
import sys
import json

# Use Python Pandas to create XLSX files
import pandas as pd

# use BeautifulSoup to process the HTML
from bs4 import BeautifulSoup

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
        print(f"Unable to open configuration file named {config_file}")
        print("Please create a suitable configuration file, the default name is config.json")
        sys.exit()

def list_pages(course_id):
    global Verbose_Flag

    list_of_all_pages=[]

    # Use the Canvas API to get the list of pages for this course
    #GET /api/v1/courses/:course_id/pages

    url = f"{baseUrl}/courses/{course_id}/pages"
    payload={
        #'include[]': 'body' # include the body witht he response
    }

    if Verbose_Flag:
        print(f"{url=}")

    r = requests.get(url, headers = header, data=payload)
    if r.status_code == requests.codes.ok:
        page_response=r.json()

        for p_response in page_response:  
            list_of_all_pages.append(p_response)

            while r.links['current']['url'] != r.links['last']['url']:  
                r = requests.get(r.links['next']['url'], headers=header)  
                page_response = r.json()  
                for p_response in page_response:  
                    list_of_all_pages.append(p_response)

    if Verbose_Flag:
        for p in list_of_all_pages:
            print(f"{p['title']}")

    if Verbose_Flag:
        print(f"{list_of_all_pages=}")
    return list_of_all_pages


def process_course(course_id, lang):
    global Verbose_Flag
    # for the different type of resources, call the relevant processing function 

    # start by processing Pages
    process_pages(course_id, lang)


def process_pages(course_id, lang):
    global Verbose_Flag
    global testing_mode_flag # if set to True do _not_ write the modified contents

    print(f"processing pages for course {course_id}")

    page_list=list_pages(course_id)

    for p in page_list:
        # skip unpublished pages
        if not p['published']:
            continue

        print(f"processing '{p['title']}'")
        if Verbose_Flag:
            print(f"{p['url']=}")

        url = f"{baseUrl}/courses/{course_id}/pages/{p['url']}"

        payload={}
        r = requests.get(url, headers = header, data=payload)
        if Verbose_Flag:
            print(f"{r.status_code=}")
        if r.status_code == requests.codes.ok:
            page_response = r.json()

            # check that the response was not None
            pr=page_response["body"]
            if not pr:
                continue

            # modified the code to handle empty files - there is nothing to do
            if len(pr) == 0:
                continue

            if len(pr) > 0:
                encoded_output = bytes(page_response["body"], 'UTF-8')

            if Verbose_Flag:
                print(f"encoded_output before: {encoded_output}")

            # do the processing here
            transformed_encoded_output, changed=transform_body(encoded_output, lang)

            if testing_mode_flag or not changed: # do not do the update
                continue           

            # update the page
            payload={"wiki_page[body]": transformed_encoded_output}
            r = requests.put(url, headers = header, data=payload)
            if Verbose_Flag:
                print(f"{r.status_code=}")
            if r.status_code != requests.codes.ok:
                print(f"Error when updating page {p['title']} at {p['url']} ")
    

def transform_body(html_content, lang):
    global Verbose_Flag
    if Verbose_Flag:
        print(f"{html_content=}")

    changed_flag=False

    soup = BeautifulSoup(html_content, 'html.parser')

    # Find all top level elements _without_ a lang attribute
    top_level_elements=soup.find_all(attrs={'lang':None}, recursive=False)
    if len(top_level_elements) >= 1:
        if Verbose_Flag:
            print(f"{len(top_level_elements)=}")

        changed_flag=True
        for node in top_level_elements:
            node.attrs['lang']=lang

        html_content = str(soup)
        print(f"transformed {html_content=}")

    return html_content, changed_flag

def main():
    global Verbose_Flag
    global testing_mode_flag # if set to True do _not_ write the modified contents

    default_picture_size=128

    parser = optparse.OptionParser()

    parser.add_option('-v', '--verbose',
                      dest="verbose",
                      default=False,
                      action="store_true",
                      help="Print lots of output to stdout"
    )

    parser.add_option('-t', '--testing',
                      dest="testing",
                      default=False,
                      action="store_true",
                      help="Set test mode"
    )

    parser.add_option("--config", dest="config_filename",
                      help="read configuration from FILE", metavar="FILE")
    
    options, remainder = parser.parse_args()

    Verbose_Flag=options.verbose
    if Verbose_Flag:
        print("ARGV      : {}".format(sys.argv[1:]))
        print("VERBOSE   : {}".format(options.verbose))
        print("REMAINING : {}".format(remainder))
        print("Configuration file : {}".format(options.config_filename))

    testing_mode_flag=options.testing

    initialize(options)

    if (len(remainder) < 2):
        print("Insuffient arguments - must provide course_id language")
        return
    
    course_id=remainder[0]

    lang=None
    if (len(remainder) == 2):
        lang=remainder[1]
    else:
        print("You must specify a language code - see RFC 5646 https://datatracker.ietf.org/doc/html/rfc5646")
        return

    process_course(course_id, lang)


if __name__ == "__main__": main()
