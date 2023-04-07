#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# ./get_students_submissions_with_comments.py course_:d assignment_id user_id
#
#
# with the option "-v" or "--verbose" you get lots of output - showing in detail the operations of the program
#
# Can also be called with an alternative configuration file:
# ./list_your_courses.py --config config-test.json
#
# Example getting your own submission:
# ./get_students_submissions_with_comments.py 34870 200752 self
#
# G. Q. Maguire Jr.
#
# 2023-04-07
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


def get_student_submissions_with_comments(course_id, assignment_id, student_id):
    submissions_found_thus_far=[]
    # GET /api/v1/courses/:course_id/assignments/:assignment_id/submissions/:user_id

    url = "{0}/courses/{1}/assignments/{2}/submissions/{3}".format(baseUrl, course_id, assignment_id, student_id)
    if Verbose_Flag:
        print("url: {}".format(url))

    extra_parameters={'per_page': '100',
                      'include[]': "submission_comments"
                      }
    r = requests.get(url, params=extra_parameters, headers = header)
    if Verbose_Flag:
        print("result of getting submissions with comments: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        page_response=r.json()

        submissions_found_thus_far.append(page_response)

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
            submissions_found_thus_far.append(page_response)

    return submissions_found_thus_far



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
        print("Insuffient arguments - must provide course_id assignment_id\n")
        sys.exit()

    course_id=remainder[0]
    assignment_id=remainder[1]
    if (len(remainder) > 2):
        student_id=remainder[2]
    else:
        student_id="self"


    comments_info=get_student_submissions_with_comments(course_id, assignment_id, student_id)
    if options.print:
        pprint.pprint(comments_info)
    for s in comments_info:
        attachments=s['attachments']
        for a in attachments:
            print("filename: {0}, type={1}, date={2}, size={3}".format(a['filename'], a['mime_class'], a['created_at'], a['size']))

if __name__ == "__main__": main()
