#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# ./delete_a_module_and_its_items.py course_id 'module_name'
#
# Output: To go throught a specific module and delete the items in the module. If they are pages, then delete the page - unless it is used by anothr module.
#
#
# with the option "-v" or "--verbose" you get lots of output - showing in detail the operations of the program
#
# With the option "-t" or "--testing" it does not actually do the deletes
#
# Can also be called with an alternative configuration file:
# ./list_your_courses.py --config config-test.json
#
# Example:
# ./delete_a_module_and_its_items.py --config config-test.json 11 'Test module for deletion'
#
# ./delete_a_module_and_its_items.py --testing --config config-test.json 11 'Test module for deletion' 
#
# ./delete_a_module_and_its_items.py --config config-test.json 11 'Test module for deletion' 
#
# G. Q. Maguire Jr.
#
# based on earlier edit_modules_items_in_a_module_in_a_course.py and cdel.py
#
# Note that when an existing page is used in a module, it gets a new module item instance in the module ; however, the url points to the original wikipage. For this reason, one can consider deleting the page only if it is not used in another module and in any case you can delete the module item.
#
# 2021-09-30
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

# canvas_course_page_url will be of the form: https://kth.instructure.com/courses/11/pages/notes-20160716
def del_course_page(canvas_course_page_url):
    # Use the Canvas API to get the list of pages for this course
    # DELETE /api/v1/courses/:course_id/pages/:url

    #extract course_id from URL
    course_id=canvas_course_page_url[canvas_course_page_url.find("courses/")+8:canvas_course_page_url.find("pages/")-1]
    if Verbose_Flag:
        print("course_id: {}".format(course_id))

    #extract the file name portion of the URL
    page_url=canvas_course_page_url[canvas_course_page_url.rfind("/")+1:]
    if Verbose_Flag:
        print("page_url: {}".format(page_url))

    new_file_name=canvas_course_page_url[canvas_course_page_url.rfind("/")+1:]+'.html'
    if Verbose_Flag:
        print("new_file_name: {}".format(new_file_name))

    url = "{0}/courses/{1}/pages/{2}".format(baseUrl,course_id, page_url)
    if Verbose_Flag:
        print(url)
    payload={}
    r = requests.delete(url, headers = header, data=payload)
    if Verbose_Flag:
        print("r.status_code: {}".format(r.status_code))
    if r.status_code == requests.codes.ok:
        page_response = r.json()
        print("{} deleted".format(canvas_course_page_url))
        return True
    else:
        print("error when deleteing page: {}".format(canvas_course_page_url))
        return False
    return False

def del_course_pages(course_id, urls):
    # Use the Canvas API to delete pages for this course
    # DELETE /api/v1/courses/:course_id/pages/:url

    if Verbose_Flag:
        print("course_id: {}".format(course_id))

    for page_url in urls:
        if Verbose_Flag:
            print("page_url: {}".format(page_url))

        url = "{0}/courses/{1}/pages/{2}".format(baseUrl,course_id, page_url)
        payload={}
        r = requests.delete(url, headers = header, data=payload)
        if Verbose_Flag:
            print("r.status_code: {}".format(r.status_code))
        if r.status_code == requests.codes.ok:
            page_response = r.json()
            print("{} deleted".format(canvas_course_page_url))
        else:
            print("error when deleteing page: {}".format(page_url))


def delete_module(course_id, module_id):
    # Use the Canvas API to delete this module in this course
    # DELETE /api/v1/courses/:course_id/modules/:id

    if Verbose_Flag:
        print("course_id: {}".format(course_id))

    url = "{0}/courses/{1}/modules/{2}".format(baseUrl,course_id, module_id)
    payload={}
    r = requests.delete(url, headers = header, data=payload)
    if Verbose_Flag:
        print("r.status_code: {}".format(r.status_code))
        if r.status_code == requests.codes.ok:
            page_response = r.json()
            if Verbose_Flag:
                print("module {} deleted".format(module_id))
        else:
            print("error when deleteing module: {}".format(module_id))



def delete_module_item(course_id, module_id, item_id):
    # Use the Canvas API to delete this module item in this module in this course
    # DELETE /api/v1/courses/:course_id/modules/:module_id/items/:di

    if Verbose_Flag:
        print("course_id: {}".format(course_id))

    url = "{0}/courses/{1}/modules/{2}/items/{3}".format(baseUrl, course_id, module_id, item_id)
    payload={}
    r = requests.delete(url, headers = header, data=payload)
    if Verbose_Flag:
        print("r.status_code: {}".format(r.status_code))
        if r.status_code == requests.codes.ok:
            page_response = r.json()
            if Verbose_Flag:
                print("module item {} deleted".format(item_id))
        else:
            print("error when deleteing module item: {}".format(item_id))

def look_for_use_elsewhere(course_id, url, module_id, modules_info):
    global Testing_Flag    
    if Testing_Flag:
        print("looking for url={}".format(url))
    for m in modules_info:
        if m == module_id:      # skip the module you are currently looking at
            continue
        for item in modules_info[m]:
            item_url=item.get('url', None)
            if not item_url:    #  item has no URL
                continue
            if item_url == url: # it the URL is used, then return True
                if Testing_Flag:
                    print("found url in module_id={}".format(m))
                return True
    # if the url is not in use in another of the modules return False
    return False

def process_module(course_id, module_id, modules, modules_info):
    global Verbose_Flag
    global Testing_Flag

    module_items=list_module_items(course_id, module_id)
    if Verbose_Flag:
        print("module_items={}".format(module_items))

    number_of_items=len(module_items)
    if Verbose_Flag:
        print("number_of_items={}".format(number_of_items))

    if number_of_items < 1:
        return

    for i in range(1, number_of_items+1):
        process_item(course_id, i, module_items, module_id, modules_info)
    # now that the items have been taken care of, delte the module
    if not Testing_Flag:
        delete_module(course_id, module_id)
    else:
        print("If not testing, module_id={} would be deleted".format(module_id))

def process_item(course_id, position, module_items, module_id, modules_info):
    print("process_item {}".format(position))
    item_to_process=None
    for item in module_items:
        if item['position'] == position:
            item_to_process=item

    if not item_to_process:
        return

    print("processing item: {}".format(item_to_process['title']))

    if not Testing_Flag:
        delete_module_item(course_id, module_id, item_to_process['id'])
    else:
        print("If not testing, item_id={} would be deleted".format(item_to_process['id']))

    # the types of th module items are: 'File', 'Page', 'Discussion', 'Assignment', 'Quiz',
    # 'SubHeader', 'ExternalUrl', 'ExternalTool'
    # delete the module item from this module
    if item_to_process['type'] == 'Page':
        url=item_to_process['url']
        # skip deletion of pages that are in use in another module
        if not look_for_use_elsewhere(course_id, url, module_id, modules_info):
            if not Testing_Flag:
                #print("deleting course page {}".format(url))
                del_course_pages(course_id, [url])
            else:
                print("If not testing, url={} would be deleted".format(url))

    return True

def main():
    global Verbose_Flag
    global Testing_Flag

    parser = optparse.OptionParser()

    parser.add_option('-v', '--verbose',
                      dest="verbose",
                      default=False,
                      action="store_true",
                      help="Print lots of output to stdout"
    )

    parser.add_option("--config", dest="config_filename",
                      help="read configuration from FILE", metavar="FILE")
    
    parser.add_option('-t', '--testing',
                      dest="testing",
                      default=False,
                      action="store_true",
                      help="Enable testing mode"
    )

    options, remainder = parser.parse_args()

    Verbose_Flag=options.verbose
    if Verbose_Flag:
        print("ARGV      : {}".format(sys.argv[1:]))
        print("VERBOSE   : {}".format(options.verbose))
        print("REMAINING : {}".format(remainder))
        print("Configuration file : {}".format(options.config_filename))

    Testing_Flag=options.testing
    if Testing_Flag:
        print("In testing mode")

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

    modules_info=dict()
    for m in modules:
        modules_info[m['id']]=list_module_items(course_id, m['id'])

    if Testing_Flag:
        print("modules_info={}".format(modules_info))

    process_module(course_id, module_id, modules, modules_info)


if __name__ == "__main__": main()
