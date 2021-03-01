#!/usr/bin/python3
# -*- coding: utf-8 -*-
# -*- mode: python; python-indent-offset: 4 -*-
#
# ./create-assignment-with-textual-submission.py course_id [name_of_assignment]
# Purpose:
#	Create an assignment with a textual submission
#
# with the option "-v" or "--verbose" you get lots of output - showing in detail the operations of the program
# with the option '-C'or '--containers' use HTTP rather than HTTPS for access to Canvas
#
# Can also be called with an alternative configuration file:
#  --config config-test.json
#
# Example:
# ./create-assignment-with-textual-submission.py 7 "Second assignment"
# 
# G. Q. Maguire Jr.
#
# 2020.03.01
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

def list_assignments(course_id):
    assignments_found_thus_far=[]
    # Use the Canvas API to get the list of assignments for the course
    #GET /api/v1/courses/:course_id/assignments

    url = "{0}/courses/{1}/assignments".format(baseUrl, course_id)
    if Verbose_Flag:
        print("url: {}".format(url))

    r = requests.get(url, headers = header)
    if Verbose_Flag:
        print("result of getting assignments: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        page_response=r.json()

        for p_response in page_response:  
            assignments_found_thus_far.append(p_response)

            # the following is needed when the reponse has been paginated
            # i.e., when the response is split into pieces - each returning only some of the list of assignments
            # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
            while r.links.get('next', False):
                r = requests.get(r.links['next']['url'], headers=header)  
                if Verbose_Flag:
                    print("result of getting assignments for a paginated response: {}".format(r.text))
                page_response = r.json()  
                for p_response in page_response:  
                    assignments_found_thus_far.append(p_response)

    return assignments_found_thus_far

def create_assignment_with_textual_submission(course_id, name, max_points, grading_type, description, assignment_group_id):
    if Verbose_Flag:
        print("in create_assignment_with_textual_submission assignment_group_id={}".format(assignment_group_id))
    # Use the Canvas API to create an assignment
    # POST /api/v1/courses/:course_id/assignments

    url = "{0}/courses/{1}/assignments".format(baseUrl, course_id)
    if Verbose_Flag:
        print("url: {}".format(url))

    payload={'assignment[name]': name,
             'assignment[submission_types][]': ['online_text_entry', 'online_upload'], # add online upload
             'assignment[peer_reviews]': 'false',
             'assignment[notify_of_update]': 'false',
             'assignment[grade_group_students_individually]': 'true',
             'assignment[peer_reviews]': 'false',
             'assignment[points_possible]': max_points,
             'assignment[grading_type]': grading_type,
             'assignment[description]': description,
             'assignment[published]': 'true' # if not published it will not be in the gradebook
    }
    if assignment_group_id:
        payload['assignment[assignment_group_id]']=assignment_group_id



    r = requests.post(url, headers = header, data=payload)
    if Verbose_Flag:
        print("result of post making an assignment: {}".format(r.text))
        print("r.status_code={}".format(r.status_code))
    if r.status_code == requests.codes.created:
        page_response=r.json()
        print("inserted assignment")
        return page_response['id']
    return False


def main():
    global Verbose_Flag

    parser = optparse.OptionParser()

    parser.add_option('-v', '--verbose',
                      dest="verbose",
                      default=False,
                      action="store_true",
                      help="Print lots of output to stdout"
    )

    parser.add_option('-C', '--containers',
                      dest="containers",
                      default=False,
                      action="store_true",
                      help="for the container enviroment in the virtual machine"
    )


    parser.add_option('-t', '--testing',
                      dest="testing",
                      default=False,
                      action="store_true",
                      help="execute test code"
    )

    parser.add_option('-s', '--submit',
                      dest="submit",
                      default=False,
                      action="store_true",
                      help="submit resulting DOCX file as the student"
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
        sys.exit()
    else:
        course_id=remainder[0]

    if (len(remainder) == 2):
        assignment_name=remainder[1]
    else:
        assignment_name='Test assignment with textual submission'

    # create the assignment

    assignment_description='''
<p><span lang="en">Assignment with a textual answer - fill in your answer below:</span></p>
'''
    target_group=False
    assignment_id=create_assignment_with_textual_submission(course_id, assignment_name, '0.50', 'pass_fail', assignment_description, target_group)
    print("assignment_id={}".format(assignment_id))

    all_assignments=list_assignments(course_id)
    print("all_assignments={}".format(all_assignments))

if __name__ == "__main__": main()
