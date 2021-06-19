#!/usr/bin/python3
# -*- coding: utf-8 -*-
# -*- mode: python; python-indent-offset: 4 -*-
#
# ./get_PDF_submission.py -c course_id -a assignment_id -u user_id [-e]
# Purpose:
#   checks that the submission has been graded and has the grade 'complete'
#   and then gets the PDF file submitted for a specified assignment
#   
#
# Ouputs a file with a name of the form: user's name-filename.pdf
#
# with the option "-v" or "--verbose" you get lots of output - showing in detail the operations of the program
# with the option '-C'or '--containers' use HTTP rather than HTTPS for access to Canvas
#
# Can also be called with an alternative configuration file:
#  --config config-test.json
#
# Example:
# ./get_PDF_submission.py -c 25434 -a 150953 -u 746
#
# get file and then call the program to extract the puseudo JSON from it
# ./get_PDF_submission.py -c 25434 -a 150953 -u 746 -e
# 
# G. Q. Maguire Jr.
#
# 2020.06.15
#

import requests, time
import pprint
import argparse
import sys
import json

import os
import subprocess

#############################
###### EDIT THIS STUFF ######
#############################

global baseUrl	# the base URL used for access to Canvas
global header	# the header for all HTML requests
global payload	# place to store additionally payload when needed for options to HTML requests

# Based upon the options to the program, initialize the variables used to access Canvas gia HTML requests
def initialize(args):
    global baseUrl, header, payload

    # styled based upon https://martin-thoma.com/configuration-files-in-python/
    config_file=args["config"]

    try:
        with open(config_file) as json_data_file:
            configuration = json.load(json_data_file)
            access_token=configuration["canvas"]["access_token"]

            if args["containers"]:
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
    
def get_user(user_id):
    #GET /api/v1/users/:user_id
    url = "{0}/users/{1}".format(baseUrl,user_id)
    if Verbose_Flag:
        print("url: {}".format(url))

    r = requests.get(url, headers = header)
    if r.status_code == requests.codes.ok:
        page_response=r.json()

        return page_response

    return []

def users_in_course(course_id):
    user_found_thus_far=[]
    # Use the Canvas API to get the list of users enrolled in this course
    #GET /api/v1/courses/:course_id/enrollments

    url = "{0}/courses/{1}/enrollments".format(baseUrl,course_id)
    if Verbose_Flag:
        print("url: {}".format(url))

    extra_parameters={'per_page': '100'}
    r = requests.get(url, params=extra_parameters, headers = header)
    if Verbose_Flag:
        print("result of getting enrollments: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        page_response=r.json()

        for p_response in page_response:  
            user_found_thus_far.append(p_response)

        # the following is needed when the reponse has been paginated
        # i.e., when the response is split into pieces - each returning only some of the list of modules
        # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
        while r.links.get('next', False):
            r = requests.get(r.links['next']['url'], headers=header)  
            page_response = r.json()  
            if r.status_code == requests.codes.ok:
                for p_response in page_response:  
                    user_found_thus_far.append(p_response)

    return user_found_thus_far

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
        while r.links['current']['url'] != r.links['last']['url']:  
            r = requests.get(r.links['next']['url'], headers=header)  
            if Verbose_Flag:
                print("result of getting assignments for a paginated response: {}".format(r.text))
            page_response = r.json()  
            for p_response in page_response:  
                assignments_found_thus_far.append(p_response)

    return assignments_found_thus_far

def list_ungraded_assignments(course_id):
    assignments_found_thus_far=[]
    # Use the Canvas API to get the list of assignments for the course
    #GET /api/v1/courses/:course_id/assignments

    url = "{0}/courses/{1}/assignments".format(baseUrl, course_id)
    if Verbose_Flag:
        print("url: {}".format(url))

    extra_parameters={'bucket': 'ungraded'
                      }
    r = requests.get(url, params=extra_parameters, headers = header)

    if Verbose_Flag:
        print("result of getting ungraded assignments: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        page_response=r.json()

        for p_response in page_response:  
            assignments_found_thus_far.append(p_response)

        # the following is needed when the reponse has been paginated
        # i.e., when the response is split into pieces - each returning only some of the list of assignments
        # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
        while r.links['current']['url'] != r.links['last']['url']:  
            r = requests.get(r.links['next']['url'], headers=header)  
            if Verbose_Flag:
                print("result of getting assignments for a paginated response: {}".format(r.text))
            page_response = r.json()  
            for p_response in page_response:  
                assignments_found_thus_far.append(p_response)

    return assignments_found_thus_far


def submission_for_assignment_by_user(course_id, assignment_id, user_id):
    # return the submission information for a single user's assignment for a specific course as a dict
    #
    # Use the Canvas API to get a user's submission for a course for a specific assignment
    # GET /api/v1/courses/:course_id/assignments/:assignment_id/submissions/:user_id
    url = "{0}/courses/{1}/assignments/{2}/submissions/{3}".format(baseUrl, course_id, assignment_id, user_id)
    if Verbose_Flag:
        print("url: {}".format(url))

    #extra_parameters={'student_ids[]': 'all'}
    #r = requests.get(url, params=extra_parameters, headers = header)
    r = requests.get(url, headers = header)
    if Verbose_Flag:
        print("result of getting submissions: {}".format(r.text))
        
    if r.status_code == requests.codes.ok:
        page_response=r.json()
        if Verbose_Flag:
            print("page_response: " + str(page_response))
        return page_response
    else:
        return None

def main(argv):
    global Verbose_Flag

    timestamp_regex = r'(2[0-3]|[01][0-9]|[0-9]):([0-5][0-9]|[0-9]):([0-5][0-9]|[0-9])'

    argp = argparse.ArgumentParser(description="get_PDF_submission.py: get PDF file submitted for indicated assignment")

    argp.add_argument('-v', '--verbose', required=False,
                      default=False,
                      action="store_true",
                      help="Print lots of output to stdout")

    argp.add_argument("--config", type=str, default='config.json',
                      help="read configuration from file")

    argp.add_argument("-c", "--canvas_course_id", type=int, required=True,
                      help="canvas course_id")

    argp.add_argument("-a", "--assignment_id", type=int, required=True,
                      help="canvas assignment_id")

    argp.add_argument("-u", "--user_id", type=int, required=True,
                      help="canvas user_id")

    argp.add_argument("-e", "--extract_JSON",
                      default=False,
                      action="store_true",
                      help="flag to cause extraction of JSON")

    argp.add_argument('-C', '--containers', required=False,
                      default=False,
                      action="store_true",
                      help="for the container enviroment in the virtual machine"
    )

    argp.add_argument('-t', '--testing', required=False,
                      default=False,
                      action="store_true",
                      help="execute test code"
    )

    args = vars(argp.parse_args(argv))

    Verbose_Flag=args["verbose"]

    initialize(args)
    if Verbose_Flag:
        print("baseUrl={}".format(baseUrl))

    initialize(args)
    course_id=args["canvas_course_id"]
    assignment_id=args["assignment_id"]
    user_id=args["user_id"]
    if Verbose_Flag:
        print("course_id={0}, assignment_id={1}, user_id={2}".format(course_id, assignment_id, user_id))

    all_assignments=list_assignments(course_id)
    # check that the assignment is in this course
    assignment=False
    for a in all_assignments:
        if a['id'] == assignment_id:
            assignment=a
            break

    if not assignment:
        print("assignment_id={} not found in this course".format(assignment_id))
        print("The assignments are: {}".format(all_assignments))
        return

    user_info=get_user(user_id)
    if Verbose_Flag:
        print("user_info={}".format(user_info))

    submission_info=submission_for_assignment_by_user(course_id, assignment_id, user_id)
    if submission_info is None:
        # check that the user is in the course
        enrollments=users_in_course(course_id)
        # computer a set of user_id for the students in the course
        student_ids=set()
        for e in enrollments:
            if e['type'] == 'StudentEnrollment':
                student_ids.add(e['user_id'])
        if user_id not in student_ids:
            print("user_id={} not found in this course".format(user_id))
        return

    if Verbose_Flag:
        print("{0}: submission_info={1}".format(user_info['sortable_name'], submission_info))
    # submission_info={'id': 12026140,
    #                  'body': None,
    #                  'url': None,
    #                  'grade': None,
    #                  'score': None,
    #                  'submitted_at': '2021-06-12T17:31:30Z',
    #                  'assignment_id': 150953,
    #                  'user_id': 1738,
    #                  'submission_type': 'online_upload',
    #                  'workflow_state': 'submitted',
    #                  'grade_matches_current_submission': True,
    #                  'graded_at': None,
    #                  'grader_id': None,
    #                  'attempt': 1,
    #                  'cached_due_date': None,
    #                  'excused': None,
    #                  'late_policy_status': None,
    #                  'points_deducted': None,
    #                  'grading_period_id': None,
    #                  'extra_attempts': None,
    #                  'posted_at': None,
    #                  'late': False,
    #                  'missing': False,
    #                  'seconds_late': 0,
    #                  'entered_grade': None,
    #                  'entered_score': None,
    #                  'preview_url': 'https://canvas.kth.se/courses/25434/assignments/150953/submissions/1738?preview=1&version=1',
    # 'attachments': [{'id': xxxx, 'uuid': 'xxx',
    #                  'folder_id': xxxx,
    #                  'display_name': 'xxxx.pdf',
    #                  'filename': 'xxxx.pdf',
    #                  'upload_status': 'success',
    #                  'content-type': 'application/pdf',
    #                  'url': 'https://canvas.kth.se/files/xxxx/download?download_frd=1&verifier=xxxx',
    #                  'size': 15619991,
    #                  'created_at': '2021-06-12T17:31:29Z',
    #                  'updated_at': '2021-06-15T15:04:28Z',
    #                  'unlock_at': None, 'locked': False, 'hidden': False, 'lock_at': None, 'hidden_for_user': False, 'thumbnail_url': None, 'modified_at': '2021-06-12T17:31:29Z',
    #                  'mime_class': 'pdf',
    #                  'media_entry_id': None,
    #                  'locked_for_user': False,
    #                  'preview_url': '/api/v1/canvadoc_session?blob=xxxxx'}],
    #  'anonymous_id': 'xxxxxxxx'}
    if  submission_info['workflow_state'] == 'submitted' or submission_info['workflow_state'] == 'graded':
        if submission_info['workflow_state'] != 'graded':
            print("assignment is submitted but not graded yet,  submission_info['workflow_state'] is {} -- update grade book and try again".format(submission_info['workflow_state']))
            return

        if submission_info['entered_grade'] =='incomplete':
            print("entered_grade is {} -- update grade book and try again".format(submission_info['entered_grade']))
            return
        # here submission_info['entered_grade'] =='complete'
        if len(submission_info['attachments']) == 1:
            attachment=submission_info['attachments'][0]
            if attachment and attachment['mime_class'] == 'pdf':
                file_name=attachment['filename']
                file_url=attachment['url']
                r = requests.get(file_url, headers = header)
                if r.status_code == requests.codes.ok:
                    if r.headers['Content-Type'] == 'application/pdf':
                        pdf_file_contents=r.content
                        file_name="{0}-{1}".format(user_info['name'], file_name)
                        with open(file_name, 'wb') as f:
                            f.write(pdf_file_contents)

                    
                        extract_flag=args["extract_JSON"]
                        if extract_flag:
                            print("Extracting JSON information")
                            try:
                                #extract_pseudo_JSON-from_PDF.py --pdf test5.pdf --json event.json
                                json_filename="{0}.json".format(user_info['name'])
                                json_filename=json_filename.replace(' ', '')
                                cmd1 = subprocess.run(['extract_pseudo_JSON-from_PDF.py', '--pdf', file_name, '--json', json_filename], capture_output=True)
                                if Verbose_Flag:
                                    sys.stdout.buffer.write(cmd1.stdout)
                                    sys.stderr.buffer.write(cmd1.stderr)
                                print("json_filename={}".format(json_filename))
                            except:
                                sys.stdout.buffer.write(cmd1.stdout)
                                sys.stderr.buffer.write(cmd1.stderr)
                                sys.exit(cmd1.returncode)


                    else:
                        print("Cntent-Type is not application/pdf, but is {}", r.headers['Content-Type'])
                        return
                else:
                    print("Unable to get url={}".format(file_url))
    else:
        print("Nothing was submitted for this assignment")
    return

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

