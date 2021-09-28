#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# ./edit_modules_items_in_a_module_in_a_course.py course_id [module_name]
#
# Output: To go throught a specific module or all modules in a course and perform some operations on the content of each page, for example replacing '<p>' with '<p lang="en_us">' to do language tagging.
#
# Note that you have to change the code at "# do the processing here" to do what you want.
#
# with the option "-v" or "--verbose" you get lots of output - showing in detail the operations of the program
#
# Can also be called with an alternative configuration file:
# ./list_your_courses.py --config config-test.json
#
# Example:
# ./edit_modules_items_in_a_module_in_a_course.py 11 'Presenting data (as a Wiki)'
#
# or process all of the modules in the course with:
# ./edit_modules_items_in_a_module_in_a_course.py 11
#
# 
# G. Q. Maguire Jr.
#
# based on earlier modules-items-in-course.py
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

def list_modules(course_id):
    modules_found_thus_far=[]
    # Use the Canvas API to get the list of modules for the course
    #GET /api/v1/courses/:course_id/modules

    url = "{0}/courses/{1}/modules".format(baseUrl, course_id)
    if Verbose_Flag:
        print("url: {}".format(url))

    r = requests.get(url, headers = header)
    if Verbose_Flag:
        print("result of getting modules: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        page_response=r.json()

        for p_response in page_response:  
            modules_found_thus_far.append(p_response)

            # the following is needed when the reponse has been paginated
            # i.e., when the response is split into pieces - each returning only some of the list of modules
            # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
            while r.links.get('next', False):
                r = requests.get(r.links['next']['url'], headers=header)  
                if Verbose_Flag:
                    print("result of getting modules for a paginated response: {}".format(r.text))
                page_response = r.json()  
                for p_response in page_response:  
                    modules_found_thus_far.append(p_response)

    return modules_found_thus_far

def list_module_items(course_id, module_id):
    module_items_found_thus_far=[]
    # Use the Canvas API to get the list of modules for the course
    # GET /api/v1/courses/:course_id/modules/:module_id/items

    url = "{0}/courses/{1}/modules/{2}/items".format(baseUrl, course_id, module_id)
    if Verbose_Flag:
        print("url: {}".format(url))

    r = requests.get(url, headers = header)
    if Verbose_Flag:
        print("result of getting module items: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        page_response=r.json()

        for p_response in page_response:  
            module_items_found_thus_far.append(p_response)

            # the following is needed when the reponse has been paginated
            # i.e., when the response is split into pieces - each returning only some of the list of modules
            # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
            while r.links.get('next', False):
                r = requests.get(r.links['next']['url'], headers=header)  
                if Verbose_Flag:
                    print("result of getting modules for a paginated response: {}".format(r.text))
                page_response = r.json()  
                for p_response in page_response:  
                    module_items_found_thus_far.append(p_response)

    return module_items_found_thus_far

def process_module(course_id, module_id, modules):
    global Verbose_Flag

    module_items=list_module_items(course_id, module_id)
    if Verbose_Flag:
        print("module_items={}".format(module_items))

    number_of_items=len(module_items)
    if Verbose_Flag:
        print("number_of_items={}".format(number_of_items))

    if number_of_items < 1:
        return

    for i in range(1, number_of_items+1):
        process_item(i, module_items)

def process_item(position, module_items):
    print("process_item {}".format(position))
    item_to_process=None
    for item in module_items:
        if item['position'] == position:
            item_to_process=item

    if not item_to_process:
        return

    print("processing item: {}".format(item_to_process['title']))
    if item_to_process['type'] == 'Page':
        url=item_to_process['url']
        payload={}
        r = requests.get(url, headers = header, data=payload)
        if Verbose_Flag:
            print("r.status_code: {}".format(r.status_code))
        if r.status_code == requests.codes.ok:
            page_response = r.json()
            # chec that the response was not None
            pr=page_response["body"]
            if not pr:
                return
            # modified the code to handle empty files
            if len(pr) == 0:
                return
            encoded_output = page_response["body"]

            if Verbose_Flag:
                print("encoded_output before: {}".format(encoded_output))

            # do the processing here
            encoded_output=encoded_output.replace('<h3>Transcript</h3>', '<h2>Transcript</h2>')
            encoded_output=encoded_output.replace('<p>', '<p lang="en_us">')

            if Verbose_Flag:
                print("encoded_output after: {}".format(encoded_output))

            # update the page
            payload={"wiki_page[body]": encoded_output}
            r = requests.put(url, headers = header, data=payload)
            if Verbose_Flag:
                print("r.status_code: {}".format(r.status_code))
            if r.status_code == requests.codes.ok:
                return True
            else:
                return False

    return True
    


def main():
    global Verbose_Flag

    default_picture_size=128

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
        print("Insuffient arguments - must provide course_id")
        return
    
    course_id=remainder[0]

    modules=list_modules(course_id)
    if not modules:
        print("No modules in the course!")

    module_id=None
    if (len(remainder) == 2):
        module_name=remainder[1]
        for m in modules:
            if m['name'] == module_name:
                module_id=m['id']

    if not module_id:
        for m in modules:
            print("processing module: {}".format(m['name']))
            process_module(course_id, m['id'], modules)
    else:
        process_module(course_id, module_id, modules)


if __name__ == "__main__": main()
