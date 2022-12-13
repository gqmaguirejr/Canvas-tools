#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# ./get_submissions_with_comments_for_section.py  section_id assignment_id
#
#
# with the option "-v" or "--verbose" you get lots of output - showing in detail the operations of the program
#
# Can also be called with an alternative configuration file:
# ./list_your_courses.py --config config-test.json
#
# G. Q. Maguire Jr.
#
#
# 2022.12.13
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
            if options.containers:
                baseUrl="http://"+configuration["canvas"]["host"]+"/api/v1"
                print("using HTTP for the container environment")
            else:
                baseUrl="https://"+configuration["canvas"]["host"]+"/api/v1"

            header = {'Authorization' : 'Bearer ' + access_token}
            payload = {}
    except:
        print("Unable to open configuration file named {}".format(config_file))
        print("Please create a suitable configuration file, the default name is config.json")
        sys.exit()


def get_submissions_with_comments(section_id, assignment_id):
    courses_found_thus_far=[]
    # Use the Canvas API to get the submissions and comments for an assignment
    # GET /api/v1/sections/:section_id/students/submissions
    url = "{0}/sections/{1}/students/submissions".format(baseUrl, section_id)
    if Verbose_Flag:
        print("url: {}".format(url))

    extra_parameters={'per_page': '100',
                      'student_ids[]': 'all',
                      'assignment_ids[]':  "{0}".format(assignment_id),
                      'grouped	': True,
                      'include[]': "submission_comments"
                      }
    r = requests.get(url, params=extra_parameters, headers = header)
    if Verbose_Flag:
        print("result of getting submissions with comments: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        page_response=r.json()

        for p_response in page_response:  
            courses_found_thus_far.append(p_response)

        # the following is needed when the reponse has been paginated
        # i.e., when the response is split into pieces - each returning only some of the list of courses
        # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
        # while r.links['current']['url'] != r.links['last']['url']:  
        #     r = requests.get(r.links['next']['url'], headers=header)  
        while r.links.get('next', False):
            r = requests.get(r.links['next']['url'], headers=header)
            if Verbose_Flag:
                print("result of getting courses for a paginated response: {}".format(r.text))
            page_response = r.json()  
            for p_response in page_response:  
                courses_found_thus_far.append(p_response)

    return courses_found_thus_far

def users_in_course(course_id):
    users_found_thus_far=[]
    # Use the Canvas API to get the list of users enrolled in this course
    #GET /api/v1/courses/:course_id/enrollments

    url = "{0}/courses/{1}/enrollments".format(baseUrl,course_id)
    if Verbose_Flag:
        print("url: {}".format(url))

    extra_parameters={'per_page': '100',
                      'type': ['StudentEnrollment']
    }
    r = requests.get(url, params=extra_parameters, headers = header)
    if Verbose_Flag:
        print("result of getting enrollments: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        page_response=r.json()

        for p_response in page_response:  
            users_found_thus_far.append(p_response)

        # the following is needed when the reponse has been paginated
        # i.e., when the response is split into pieces - each returning only some of the list of modules
        # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
        #while r.links['current']['url'] != r.links['last']['url']:  
        while r.links.get('next', False):
            r = requests.get(r.links['next']['url'], headers=header)
            page_response = r.json()  
            for p_response in page_response:  
                users_found_thus_far.append(p_response)

    return users_found_thus_far


def main():
    global Verbose_Flag

    parser = optparse.OptionParser()

    parser.add_option('-v', '--verbose',
                      dest="verbose",
                      default=False,
                      action="store_true",
                      help="Print lots of output to stdout"
    )
    parser.add_option('-p', '--print',
                      dest="print",
                      default=False,
                      action="store_true",
                      help="pprint the information"
    )


    parser.add_option("--config", dest="config_filename",
                      help="read configuration from FILE", metavar="FILE")
       
    parser.add_option('-C', '--containers',
                      dest="containers",
                      default=False,
                      action="store_true",
                      help="for the container enviroment in the virtual machine"
    )

    options, remainder = parser.parse_args()

    Verbose_Flag=options.verbose
    if Verbose_Flag:
        print('ARGV      :', sys.argv[1:])
        print('VERBOSE   :', options.verbose)
        print('REMAINING :', remainder)
        
    if options.config_filename:
        print("Configuration file : {}".format(options.config_filename))

    initialize(options)

    if (len(remainder) < 2):
        print("Insuffient arguments - must provide section_id assignment_id\n")
        sys.exit()

    section_id=remainder[0]
    assignment_id=remainder[1]
    comments_info=get_submissions_with_comments(section_id, assignment_id)
    if options.print:
        pprint.pprint(comments_info)

    writer = pd.ExcelWriter(f'comments-{section_id}-{assignment_id}.xlsx', engine='xlsxwriter')
    comments_info_df=pd.json_normalize(comments_info)
    comments_info_df.to_excel(writer, sheet_name='Comments')
    # Close the Pandas Excel writer and output the Excel file.
    writer.close()

if __name__ == "__main__": main()

