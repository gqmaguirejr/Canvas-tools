#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# ./modules-items-in-course-json.py course_id
#
# Output: json file with modules and module items in course
#         it also get the front page, it it exists and is published and visible to students
#
#
# with the option "-v" or "--verbose" you get lots of output - showing in detail the operations of the program
#
# Can also be called with an alternative configuration file:
# ./list_your_courses.py --config config-test.json
#
# Example:
# ./modules-items-in-course.py 11
#
# ./modules-items-in-course.py --config config-test.json 11
#
# 
# documentation about using xlsxwriter to insert images can be found at:
#   John McNamara, "Example: Inserting images into a worksheet", web page, 10 November 2018, https://xlsxwriter.readthedocs.io/example_images.html
#
# G. Q. Maguire Jr.
#
# 2020.03.27
# based on earlier (2019.01.05) modules-items-in-course.py
# 
#

import requests, time
import pprint
import optparse
import sys
import json

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

def list_quizzes(course_id):
    quizzes_found_thus_far=[]
    # Use the Canvas API to get the list of quizzes for the course
    #GET /api/v1/courses/:course_id/quizzes

    url = "{0}/courses/{1}/quizzes".format(baseUrl, course_id)
    if Verbose_Flag:
        print("url: {}".format(url))

    r = requests.get(url, headers = header)
    if Verbose_Flag:
        print("result of getting quizzes: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        page_response=r.json()

        for p_response in page_response:  
            quizzes_found_thus_far.append(p_response)

            # the following is needed when the reponse has been paginated
            # i.e., when the response is split into pieces - each returning only some of the list
            # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
            while r.links['current']['url'] != r.links['last']['url']:  
                r = requests.get(r.links['next']['url'], headers=header)  
                if Verbose_Flag:
                    print("result of getting quizzes for a paginated response: {}".format(r.text))
                page_response = r.json()  
                for p_response in page_response:  
                    quizzes_found_thus_far.append(p_response)

    return quizzes_found_thus_far

def get_front_page(course_id):
    front_page=[]
    # Use the Canvas API to get the front page it it exists
    #GET /api/v1/courses/:course_id/GET /v1/courses/{course_id}/front_page

    url = "{0}/courses/{1}/front_page".format(baseUrl, course_id)
    if Verbose_Flag:
        print("url: {}".format(url))

    r = requests.get(url, headers = header)
    if Verbose_Flag:
        print("result of getting modules: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        front_page=r.json()

    return front_page

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
            while r.links['current']['url'] != r.links['last']['url']:  
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
            while r.links['current']['url'] != r.links['last']['url']:  
                r = requests.get(r.links['next']['url'], headers=header)  
                if Verbose_Flag:
                    print("result of getting modules for a paginated response: {}".format(r.text))
                page_response = r.json()  
                for p_response in page_response:  
                    module_items_found_thus_far.append(p_response)

    return module_items_found_thus_far

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
        print("Insuffient arguments - must provide course_id\n")
    else:
        course_info=dict()

        course_id=remainder[0]
        course_info_file="modules-in-course-{}.json".format(course_id)
        # place information into the course_info under 'modules', 'front_page', and 'quizzes'
        course_info['modules']=dict()

        modules=list_modules(course_id)
        if (modules):
            for m in sorted(modules, key=lambda x: x['id']):
                module_items=dict()
                mi=list_module_items(course_id, m['id'])
                for item in sorted(mi, key=lambda x: x['id']):
                    module_items[item['title']]=item

                m['module_items']=module_items
                course_info['modules'][m['name']]=m

        front_page=get_front_page(course_id)
        if front_page:
            # check that it is a front_page, published, and visible to students
            if front_page['front_page'] and front_page['published'] and not front_page['hide_from_students']:
                course_info['front_page']=front_page

        quizzes=list_quizzes(course_id)
        if quizzes:
            course_info['quizzes']=quizzes

        if Verbose_Flag:
            print("course_info={}".format(course_info))

        try:
            with open(course_info_file, 'w') as json_data_file:
                json.dump(course_info, json_data_file)
                print("created output file {}".format(course_info_file))
        except:
            print("Unable to write JSON file named {}".format(course_info_file))
            sys.exit()


if __name__ == "__main__": main()
