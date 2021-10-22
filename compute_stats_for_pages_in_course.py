#!/usr/bin/python3
#
# ./compute_stats_for_pages_in_course.py  course_id
# 
# it outputs a XLSX file with the name statistics_for_course_xx.xlsx
# where xx is the course_id
#
# G. Q: Maguire Jr.
#
# 2020.03.27
# based on compute_stats_for_pages_in_course.py  from 2016.07.15
#
# with the option "-v" or "--verbose" you get lots of output - showing in detail the operations of the program
#
# Can also be called with an alternative configuration file:
# ./compute_stats_for_pages_in_course.py --config config-test.json
#
# Examples:
# ./compute_stats_for_pages_in_course.py 11
#
# ./compute_stats_for_pages_in_course.py --config config-test.json 11
#


import csv, requests, time
from pprint import pprint
import optparse
import sys

import json

from lxml import html

# Use Python Pandas to create XLSX files
import pandas as pd

from textatistic import Textatistic
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

def compute_stats_for_pages_in_course(course_id):
    list_of_all_pages=[]
    page_stats=[]

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
                continue

            if Verbose_Flag:
                print("raw_text: {}".format(raw_text))
                
        else:
            print("No pages for course_id: {}".format(course_id))
            return False

        # see http://www.erinhengel.com/software/textatistic/
        try:
            fixed_title=page_response["title"].replace(',', '_comma_')
            fixed_title=fixed_title.replace('"', '_doublequote_')
            fixed_title=fixed_title.replace("'", '_singlequote_')
            page_entry={"url": url, "page_name": fixed_title, "Textatistic.statistics": Textatistic(raw_text).dict()}
        except ZeroDivisionError:
            # if there are zero sentences, then some of the scores cannot be computed
            if Verbose_Flag:
                print("no sentences in page {}".format(url))
            continue
        except ValueError:
            # if there is code on the page, for example a json structure, then the hyphenation package cannot handle this
            if Verbose_Flag:
                print("there is likely code on page {}".format(url))
            continue

        if page_entry: 
            page_stats.append(page_entry)

    return page_stats

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


def main():
    global Verbose_Flag

    parser = optparse.OptionParser()

    parser.add_option('-v', '--verbose',
                      dest="verbose",
                      default=False,
                      action="store_true",
                      help="Print lots of output to stdout"
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

    initialize(options)

    if (len(remainder) < 1):
        print("Inusffient arguments\n must provide course_id\n")
    else:
        course_id=remainder[0]
        output=compute_stats_for_pages_in_course(course_id)
        if (output):
            if Verbose_Flag:
                print(output)
            stats_df=pd.json_normalize(output)

            # set up the output write
            writer = pd.ExcelWriter('statistics-for-course-'+str(course_id)+'.xlsx', engine='xlsxwriter')
            stats_df.to_excel(writer, sheet_name='Stats')
            # Close the Pandas Excel writer and output the Excel file.
            writer.save()


if __name__ == "__main__": main()

