#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -*- mode: python; python-indent-offset: 4 -*-
#
# II2210-grades_to_reportv3.py course_id
# Purpose: Compute final grade from the separate quizzes and computed date based on the last quiz to have been passed.
#
# Example:
# ./II2210-grades_to_reportv3.py 11 
#
# The program can walk a gradebook and do computations on the grades. Currently, it is for a course with 4 assigned that each have a certain maximum number of points.
# Note that you have to manually add a short name for each assignment_id number.
#  
# Note that the "Notes" column has to be set to visible in the gradebook before the program will add the date inofmration to the notes column.
#
# Note: This uses the new Canvas_to_LADOK API
#
# 2022-05-17 G. Q. Maguire Jr.
#
# Modified 2021-12-20 - to make the Notes column visible. This avoids creating a new "Notes" column.
#                       This also has a version of list_columns that lists hideen columns.
# This version of the program is for use after 2022-01-01
#
# The dates from Canvas are in ISO 8601 format.
#
# based on II2210-grades_to_reportv2.py
#
# **** this is a work in progress and not yet ready for use ***
#
import re
import sys

import json
# import argparse
from argparse import ArgumentParser
from pathlib import Path

import requests, time
import pprint

import os			# to make OS calls, here to get time zone info
import isodate                  # for parsing ISO 8601 dates and times
import pytz                     # for time zones
from dateutil.tz import tzlocal

# use the canvasapai
import canvasapi

global headers	# the header for all HTML requests

def verbose_print(*args, **kwargs) -> None:
    global verbose
    if verbose:
        print(*args, **kwargs)


def utc_to_local(utc_dt):
    return utc_dt.replace(tzinfo=datetime.timezone.utc).astimezone(tz=None)

def datetime_to_local_string(canvas_time):
    global Use_local_time_for_output_flag
    t1=isodate.parse_datetime(canvas_time)
    if Use_local_time_for_output_flag:
        t2=t1.astimezone()
        return t2.strftime("%Y-%m-%d %H:%M")
    else:
        return t1.strftime("%Y-%m-%d %H:%M")



#############################
###### EDIT THIS STUFF ######
#############################

global t2l_root_url
t2l_root_url='https://app-r.referens.sys.kth.se'


# To use the Instructure Canvas API
global baseUrl	# the base URL used for access to Canvas
global header	# the header for all HTML requests
global payload	# place to store additionally payload when needed for options to HTML requests

# Canvas related functions
def list_gradebook_history_feed():
    global Verbose_Flag
    global course_id
    
    entries_found_thus_far=[]

    # Use the Canvas API to get the grade information

    url = "{0}/courses/{1}/gradebook_history/feed".format(baseUrl, course_id)
    if Verbose_Flag:
        print("url: {}".format(url))

    extra_parameters={'per_page': '100'}
    r = requests.get(url, params=extra_parameters, headers = header)

    if Verbose_Flag:
        print("result of getting gradebook feed: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        page_response=r.json()

        for p_response in page_response:  
            entries_found_thus_far.append(p_response)

        # the following is needed when the reponse has been paginated
        # i.e., when the response is split into pieces - each returning only some of the list of modules
        # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
        while r.links.get('next', False):
            r = requests.get(r.links['next']['url'], headers=header)  
            if Verbose_Flag:
                print("result of getting modules for a paginated response: {}".format(r.text))
            page_response = r.json()  
            for p_response in page_response:  
                entries_found_thus_far.append(p_response)

    return entries_found_thus_far


def list_custom_columns():
    # will return a list of custom columns including
    # [{'id': 1684, 'title': 'Notes', 'position': 1, 'teacher_notes': True, 'read_only': False, 'hidden': False}]

    global Verbose_Flag
    global course_id
    entries_found_thus_far=[]

    # Use the Canvas API to get the list of custom column for this course
    #GET /api/v1/courses/:course_id/custom_gradebook_columns
    url = "{0}/courses/{1}/custom_gradebook_columns".format(baseUrl,course_id)
    if Verbose_Flag:
        print("url: {}".format(url))

    payload={'include_hidden': True }

    r = requests.get(url, headers = header, data=payload)
    if Verbose_Flag:
        print("result of getting custom columns: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        page_response=r.json()

        for p_response in page_response:  
            entries_found_thus_far.append(p_response)

        # the following is needed when the reponse has been paginated
        # i.e., when the response is split into pieces - each returning only some of the list of modules
        # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
        while r.links.get('next', False):
            r = requests.get(r.links['next']['url'], headers=header)  
            if Verbose_Flag:
                print("result of getting modules for a paginated response: {}".format(r.text))
            page_response = r.json()  
            for p_response in page_response:  
                entries_found_thus_far.append(p_response)

    return entries_found_thus_far

def list_custom_column_entries(column_number):
    global Verbose_Flag
    global course_id
    entries_found_thus_far=[]

    # Use the Canvas API to get the list of custom column entries for a specific column for the course
    #GET /api/v1/courses/:course_id/custom_gradebook_columns/:id/data

    url = "{0}/courses/{1}/custom_gradebook_columns/{2}/data".format(baseUrl,course_id, column_number)
    if Verbose_Flag:
        print("url: {}".format(url))

    r = requests.get(url, headers = header)
    if Verbose_Flag:
        print("result of getting custom columns: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        page_response=r.json()

        for p_response in page_response:  
            entries_found_thus_far.append(p_response)

        # the following is needed when the reponse has been paginated
        # i.e., when the response is split into pieces - each returning only some of the list of modules
        # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
        while r.links.get('next', False):
            r = requests.get(r.links['next']['url'], headers=header)  
            if Verbose_Flag:
                print("result of getting modules for a paginated response: {}".format(r.text))
            page_response = r.json()  
            for p_response in page_response:  
                entries_found_thus_far.append(p_response)

    return entries_found_thus_far

def assign_grade_for_assignment(assignment_id, user_id, grade, comment):
    global Verbose_Flag
    global course_id
    # Use the Canvas API to assign a grade for an assignment
    #PUT /api/v1/courses/:course_id/assignments/:assignment_id/submissions/:user_id

    # Request Parameters:
    # comment[text_comment]		string	Add a textual comment to the submission.
    # comment[group_comment]		boolean	Whether or not this comment should be sent to the entire group (defaults to false). Ignored if this is not a group assignment or if no text_comment is provided.
    # comment[media_comment_id]		string	Add an audio/video comment to the submission.
    # comment[media_comment_type]		string	The type of media comment being added.
    # comment[file_ids][]		integer	Attach files to this comment that were previously uploaded using the Submission Comment API's files action
    # include[visibility]		string	Whether this assignment is visible to the owner of the submission
    # submission[posted_grade]		string	Assign a score to the submission, updating both the “score” and “grade” fields on the submission record. This parameter can be passed in a few different formats:
    # submission[excuse]		boolean	    Sets the “excused” status of an assignment.
    # submission[late_policy_status]		string	Sets the late policy status to either “late”, “missing”, “none”, or null.
    # submission[seconds_late_override]		integer	Sets the seconds late if late policy status is “late”
    # rubric_assessment		RubricAssessment	Assign a rubric assessment to this assignment submission. The sub-parameters here depend on the rubric for the assignment. The general format is, for each row in the rubric:

    url = "{0}/courses/{1}/assignments/{2}/submissions/{3}".format(baseUrl,course_id, assignment_id, user_id)
    if Verbose_Flag:
        print("url: " + url)

    if comment:
        payload={'submission[posted_grade]': grade,
                 'comment[text_comment]': comment
                 }
    else:
        payload={'submission[posted_grade]': grade,
                 }

    r = requests.put(url, headers = header, data=payload)
    if Verbose_Flag:
        print("result of put assign_grade_for_assignment: {}".format(r.text))
    if r.status_code == requests.codes.ok:
        page_response=r.json()
        if Verbose_Flag:
            print("inserted grade for assignment")
        return True
    return False


# new for v3
def assignment_short_name_given_name(name):
    global assignments
    for a in assignments:
        if a.name == name:
            return a.short_name
    return None

def points_possible(short_name):
    global assignments
    for a in assignments:
        if a.short_name == short_name:
            return a.points_possible
    return None

def assignment_given_short_name(short_name):
    global assignments
    for a in assignments:
        if a.short_name == short_name:
            return a
    return None

def assignment_due_date(short_name):
    global assignments
    for a in assignments:
        if a.short_name == short_name:
            return isodate.parse_datetime(a.due_at)
    return None

def assignment_grading_type(short_name):
    global assignments
    for a in assignments:
        if a.short_name == short_name:
            return a.grading_type
    return None

def grading_type_points(short_name):
    gt=assignment_grading_type(short_name) 
    if gt:
        return gt == 'points'
    return None

def assignment_grading_standard_id(short_name):
    global assignments
    for a in assignments:
        if a.short_name == short_name:
            return a.grading_standard_id
    return None

def grade(short_name, student):
    global gradebook

    assignment=assignment_given_short_name(short_name)
    if not assignment:
        print("No such assignment named {0}".format(shrt_name))
        return None

    if gradebook.get(student, False):
        students_assignments=gradebook[student].get('assignments', False)
        if not students_assignments:
            return None             # student has no assignments

        this_assignment=students_assignments.get(short_name, False)
        if this_assignment:
            return this_assignment.get('grade', None)

    return None


def assign_grade(short_name,user_id, grade, comment):
    print("assign_grade({0},{1}, {2}, {3}".format(short_name,user_id, grade, comment))
    return                      # for testing qqq
    assignment=assignment_given_short_name(short_name)
    if assignment:
        assignment_id=assignment['id']
    else:
        print("No such assignment named {0} unable to store grade".format(shrt_name))
        return None

    assign_grade_for_assignment(assignment_id, user_id, grade, comment)



def submission_date(short_name, student):
    global gradebook

    assignment=assignment_given_short_name(short_name)
    if not assignment:
        print("No such assignment named {0}".format(shrt_name))
        return None

    if gradebook.get(student, False):
        students_assignments=gradebook[student].get('assignments', False)
        if not students_assignments:
            return None             # student has no assignments

        this_assignment=students_assignments.get(short_name, False)
        if this_assignment:
            td=this_assignment.get('submittedAt', None)
            if td:
                return isodate.parse_datetime(td)

    return None

# [{'id': 1684, 'title': 'Notes', 'position': 1, 'teacher_notes': True, 'read_only': False, 'hidden': False}]
def custom_column_id(title):
    global custom_columns
    for c in custom_columns:
        if title == c.title:
            return c.id
    return None

def custom_column_value(user_id, title):
    global custom_column_data
    slice=custom_column_data.get(title, False)
    # slice is of the form: [ {'content': 'xxxx', 'user_id': ddd}, ...]
    if slice:
        for s in slice:
            if s['user_id'] == user_id:
                value=s['content']
                return value
    return None


# for v3
def put_custom_column_entries(custom_columns, title, user_id, data_to_store):
    print("put_custom_column_entries({0},{1},{2},{3}".format(custom_columns, title, user_id, data_to_store))

    for c in custom_columns:
        if c.hidden:     #  skip hidden columns
            continue
        if c.teacher_notes:     #  skip teacher notes columns
            continue
        if c.title == title:
            print("c.id={}".format(c.id))
            print("c.title={}".format(c.title))
            data=c.get_column_entries(include_hidden=True)
            for cdi in data:
                if cdi.user_id == user_id:
                    print("cdi.content={}".format(cdi.content))
                    cdi.update_column_data(column_data={'content': data_to_store})
                    print("cdi.content={} after".format(cdi.content))
                    return
            # if there is no matching data, then you need to add it for the first time
            payload={}
            header=headers
            print("put_custom_column_entries_original")
            put_custom_column_entries_original(c.id, user_id, data_to_store)


def put_custom_column_entries_original(column_id, user_id, data_to_store):
    global baseUrl	# the base URL used for access to Canvas
    global headers
    global course_id
    global verbose
    entries_found_thus_far=[]
    payload={}

    # Use the Canvas API to get the list of custom column entries for a specific column for the course
    #PUT /api/v1/courses/:course_id/custom_gradebook_columns/:id/data/:user_id

    url = "{0}/courses/{1}/custom_gradebook_columns/{2}/data/{3}".format(baseUrl,course_id, column_id, user_id)
    if verbose:
        print("url: " + url)

    payload={'column_data[content]': data_to_store}
    r = requests.put(url, headers = headers, data=payload)

    if verbose:
        print("result of putting data into custom_gradebook_column:  {}".format(r.text))

    if r.status_code == requests.codes.ok:
        page_response=r.json()

        for p_response in page_response:  
            entries_found_thus_far.append(p_response)

    return entries_found_thus_far


def insert_column_name(course_id, column_name):
    global Verbose_Flag

    # Use the Canvas API to Create a custom gradebook column
    # POST /api/v1/courses/:course_id/custom_gradebook_columns
    #   Create a custom gradebook column
    # Request Parameters:
    #Parameter		Type	Description
    #column[title]	Required	string	no description
    #column[position]		integer	The position of the column relative to other custom columns
    #column[hidden]		boolean	Hidden columns are not displayed in the gradebook
    # column[teacher_notes]		boolean	 Set this if the column is created by a teacher. The gradebook only supports one teacher_notes column.

    url = "{0}/courses/{1}/custom_gradebook_columns".format(baseUrl,course_id)
    if Verbose_Flag:
        print("url: {}".format(url))
    payload={'column[title]': column_name,
             'column[hidden]': False
             }
    r = requests.post(url, headers = header, data=payload)
    if r.status_code == requests.codes.ok:
        if Verbose_Flag:
            print("result of post creating custom column:  {}".format(r.text))
            page_response=r.json()
            print("inserted column")
        return True
    return False

def unhide_column_name(course_id, column_name):
    global Verbose_Flag

    # Use the Canvas API to Create a custom gradebook column
    # POST /api/v1/courses/:course_id/custom_gradebook_columns
    #   Create a custom gradebook column
    # Request Parameters:
    #Parameter		Type	Description
    #column[title]	Required	string	no description
    #column[position]		integer	The position of the column relative to other custom columns
    #column[hidden]		boolean	Hidden columns are not displayed in the gradebook
    # column[teacher_notes]		boolean	 Set this if the column is created by a teacher. The gradebook only supports one teacher_notes column.

    url = "{0}/courses/{1}/custom_gradebook_columns".format(baseUrl,course_id)
    if Verbose_Flag:
        print("url: {}".format(url))
    payload={'column[title]': column_name,
             'column[hidden]': False
             }
    r = requests.put(url, headers = header, data=payload)
    if r.status_code == requests.codes.ok:
        if Verbose_Flag:
            print("result of PT updating custom column:  {}".format(r.text))
            page_response=r.json()
            print("inserted column")
        return True
    return False


verbose = False # Global flag for verbose prints
DEFAULT_CONFIG_FILE = 'config.json'

def read_config(config_file: str = None) -> dict:
    config_file = config_file or DEFAULT_CONFIG_FILE
    try:
        # styled based upon https://martin-thoma.com/configuration-files-in-python/
        return json.loads(Path(config_file).read_text())
    except json.JSONDecodeError as e:
        print(f'Invalid JSON in {config_file}')
        raise e
    except Exception as e:
        print(f'Unable to open configuration file named {config_file}')
        print(f'Please create a suitable configuration file, the default name is {DEFAULT_CONFIG_FILE}')
        raise e


# Take out the config variables used to authenticate KTH through SAML login. Used to access Canvas pages directly.
def get_kth_credentials(config: dict) -> tuple:
    try:
        return (config["kth"]["username"], config["kth"]["password"])
    except KeyError as e:
        print('Missing keys in config file')
        raise e

#
# function for use with transfer to LADOK (t2l)
#
def t2l_get_sections(course_id) -> dict:
    global headers
    global t2l_root_url
    #url = f'https://app-referens.sys.kth.se/courses/{course_id}/sections'
    #url = f'https://app-referens.sys.kth.se/transfer-to-ladok/api/courses/{course_id}/sections'
    url = f'{t2l_root_url}/transfer-to-ladok/api/courses/{course_id}/sections'
    payload={}

    response = requests.request("GET", url, headers=headers, data=payload)
    print("response.status_code={}".format(response.status_code))
    if response.status_code == requests.codes.ok:
        print("respose.text={}".format(response.text))
        return response.json()
    else:
        return None

def t2l_gradable_students(course_id, aktivitetstillfalle=None, kurstillfalle=None, utbildningsinstans=None) -> dict:
    global headers
    global verbose
    global t2l_root_url
    url = f'{t2l_root_url}/transfer-to-ladok/api/courses/{course_id}/ladok-grades'
    #       https://app-r.referens.sys.kth.se/transfer-to-ladok/api/courses/11555/ladok-grades?kurstillfalle=eb5505e2-f6ed-11e8-9614-d09e533d4323&utbildningsinstans=7f20dbb6-73d8-11e8-b4e0-063f9afb40e3
    payload={}
    if aktivitetstillfalle:
        payload['aktivitetstillfalle']=aktivitetstillfalle
    if kurstillfalle:
        payload['kurstillfalle']=kurstillfalle
    if utbildningsinstans:
        payload['utbildningsinstans']=utbildningsinstans
    verbose_print(f'{payload=}')
        
    response = requests.request("GET", url, headers=headers, params=payload, data={})
    verbose_print(f'{response.request.url=}')
    verbose_print(f'{response.status_code=}')
    if response.status_code == requests.codes.ok:
        verbose_print(f'{response.text=}')
        print("respose.text={}".format(response.text))
        return response.json()
    else:
        return None
    
def t2l_get_assignments(course_id) -> dict:
    global headers
    global verbose
    global t2l_root_url
    #url = f'https://app-r.referens.sys.kth.se/transfer-to-ladok/api/courses/{course_id}/assignments'
    # End-point change!
    #url = "https://app-r.referens.sys.kth.se/transfer-to-ladok/api/courses/36353/columns"
    url = f'{t2l_root_url}/transfer-to-ladok/api/courses/{course_id}/columns'

    payload={}
    response = requests.request("GET", url, headers=headers, data=payload)
    verbose_print(f'{response.request.url=}')
    verbose_print(f'{response.status_code=}')
    if response.status_code == requests.codes.ok:
        verbose_print(f'{response.text=}')
        return response.json()
    else:
        return None

def t2l_get_grades_for_an_assignment(course_id, assignment_id) -> dict:
    # returns a list with elements of the form:
    # {'student': {'id': 'xxxx', 'sortableName': 'Maguire, Chip'}, 'grade': None, 'gradedAt': None, 'submittedAt': None}
    # where xxxx is an integration id for this student
    global verbose
    global headers
    global t2l_root_url
    url = f'{t2l_root_url}/transfer-to-ladok/api/courses/{course_id}/assignments/{assignment_id}'
    payload={}
    data_payload={}
    response = requests.request("GET", url, headers=headers, params=payload, data=data_payload)
    if verbose:
        print("response.url={}".format(response.url))
        print("response.status_code={}".format(response.status_code))
    if response.status_code == requests.codes.ok:
        if verbose:
            print("respose.text={}".format(response.text))
        return response.json()
    else:
        return None


def t2l_send_grades_for_an_assignment(course_id, assignment_id, results_list, aktivitetstillfalle=None) -> dict:
    global headers
    global t2l_root_url
    url = f'{t2l_root_url}/transfer-to-ladok/api/courses/{course_id}/ladok-grades'
    # payload={
    #     "destination": {
    #         "aktivitetstillfalle": "05b7b9b6-88d9-11ec-bc70-adb799404101"
    #     },
    #     "results": [
    #         {
    #             "id": "df0d839b-b432-11e9-8bbd-25378c5a4e4c",
    #             "draft": {
    #                 "grade": "B",
    #                 "examinationDate": "2022-05-05"
    #             }
    #         },
    #         {
    #             "id": "13bf0c2a-b433-11e9-8bbd-25378c5a4e4c",
    #             "draft": {
    #                 "grade": "F",
    #                 "examinationDate": "2023-05-05"
    #             }
    #         }
    #     ]
    # }
    payload={}
    if aktivitetstillfalle:
        payload['destination']={'aktivitetstillfalle': aktivitetstillfalle}
    payload['results']={'results': results_list}

    response = requests.request("POST", url, headers=headers, data=payload)
    print("response.url={}".format(response.url))
    print("response.status_code={}".format(response.status_code))
    if response.status_code == requests.codes.ok:
        print("respose.text={}".format(response.text))
        return response.json()
    else:
        return None

def main(argv):
    global verbose
    global headers
    global baseUrl	# the base URL used for access to Canvas

    global assignments
    global custom_columns
    global custom_column_data
    global gradebook
    global Use_local_time_for_output_flag
    global course_id

    Use_local_time_for_output_flag=True

    timestamp_regex = r'(2[0-3]|[01][0-9]|[0-9]):([0-5][0-9]|[0-9]):([0-5][0-9]|[0-9])'

    parser = ArgumentParser()
    parser.add_argument('-v', '--verbose',
                        action='store_true',
                        help='Print lots of output to stdout'
    )
    parser.add_argument('-t', '--testing',
                        action='store_true',
                        help='Do not create the directories, only make the XLSX files'
    )
    parser.add_argument('--config', dest='config_filename',
                        help='read configuration from FILE',
                        metavar='FILE'
    )
    parser.add_argument('course_id')

    args = parser.parse_args()
    print("args={}".format(args))

    verbose = args.verbose
    print(f'verbose={verbose}')
    Verbose_Flag=verbose
    course_id = args.course_id
    testing = args.testing

    verbose_print(f'ARGV      : {sys.argv[1:]}')
    verbose_print(f'VERBOSE   : {args.verbose}')
    verbose_print(f'COURSE_ID : {args.course_id}')
    verbose_print(f'Configuration file : {args.config_filename}')

    config = read_config(args.config_filename)

    gradebook=dict()            #  will be used to hold the virtual gradebook
    # form of the gradbook
    #gradebook[student_intrgration_id]={'user_name': e['sortable_name'],
    #                         'canvas_id': e['user_id']
    #                         'assignments': {short_name: grade, short_name2: grade ...}},
    #                         'notes': None
    #                         }

    # Initialize Canvas API
    canvas = canvasapi.Canvas('https://'+config["canvas"]["host"],config["canvas"]["access_token"])

    # set up header for authentication with Canvas token
    access_token=config["canvas"]["access_token"]
    headers = {'Authorization' : 'Bearer ' + access_token}
    #verbose_print(f'{headers=}')

    # Initialize for use with Instructure Canvas API
    baseUrl="https://"+config["canvas"]["host"]+"/api/v1"


    course = canvas.get_course(course_id)
    verbose_print(f'{course=}')

    users = course.get_users(enrollment_type=['student']) # get the list of students in the course

    if verbose:
        print("Information about users")
        for user in users:
            print(user)
            if verbose and testing:
                for attribute, value in user.__dict__.items():
                    print(attribute, '=', value)
    # Each user has the attributes:
    # id
    # name
    # created_at = 2021-05-31T10:51:20+02:00
    # sortable_name
    # short_name
    # sis_user_id
    # integration_id
    # login_id
    # email

    # form of the gradbook
    #gradebook[student_intrgration_id]={'user_name': e['user_name'],
    #                         'canvas_id': e['user_id']
    #                         'assignments': {short_name: {'grade': xx, 'submittedAt': xxx},  ...}},
    #                         'notes': None
    #                         }
    for u in users:
        gradebook[u.integration_id]={'user_name': u.sortable_name,'canvas_id': u.id, 'assignments': dict(), 'notes': None}
                                        
    if verbose:
        print("Initial gradebook")
        for u in users:
            print("gradebook[{0}]={1}".format(u.integration_id, gradebook[u.integration_id]))

    assignments=course.get_assignments()
                                
    verbose_print(f'{assignments=}')
    assignment_summary=[]

    # dump all of the attributes of each assignment
    if testing:
        for a in assignments:
            if not a.published: # skip unpublished assignments
                continue
            print("a={}".format(a))
            for attribute, value in a.__dict__.items():
                print(attribute, '=', value)

    if verbose:
        for a in assignments:
            if not a.published: # skip unpublished assignments
                continue
            print(f"id={a.id}, name={a.name}, points_possible={a.points_possible}, due_at={a.due_at}, grading_type={a.grading_type}, grading_standard_id={a.grading_standard_id}, allowed_attempts={a.allowed_attempts}")

    for a in assignments:
        # Set up the short names for the assignments
        # ***** This is essential as the routines will use the short names to access the relevant assignment and grades
        # You have to look at the assignment id for each assignment and then add a short_name to the assignment
        # You can do this by matching assignment_id numbers or matching the names
        if not a.published: # skip unpublished assignments
            continue
        if a.id == 146887 or a.name == 'Ethical Research (with quiz)' or a.name == 'Ethical Research - quiz':
            a.set_attributes({'short_name': 'ER'})

        if a.id == 146888 or a.name == 'Professionalism and Ethics for ICT students (with quiz)' or a.name == 'Professionalism and Ethics for ICT students - quiz':
            print("found PE")
            a.set_attributes({'short_name': 'PE'})
            print("a.short_name={}".format(a.short_name))

        if a.id == 146885 or a.name == 'Ethical Research: Human Subjects and Computer Issues (with quiz)' or a.name == 'Ethical Research: Human Subjects and Computer Issues - quiz':
            a.set_attributes({'short_name': 'ERH'})

        if a.id == 146886 or a.name == 'Sustainable Development/Hållbar Utveckling (with quiz)' or a.name == 'Sustainable Development/Hållbar Utveckling - quiz':
            a.set_attributes({'short_name': 'SUSD'})

        if a.id == 146889 or a.name == 'LADOK - PRO1 (Onlinequiz)' or a.name == 'LADOK - PRO1 (Onlinequiz)':       # the moment to report to LADOK
            a.set_attributes({'short_name': 'PRO1'})

    if verbose or testing:
        print("Short name")
        for a in assignments:
            print(f'{a.id}: {a.short_name} is {a.name}')

    # sections=course.get_sections()
    # if sections:
    #     for section in sections:
    #         print(f'section={section}')

    if verbose:
        print("calling t2l_get_assignments()")

    ladok_assignments=t2l_get_assignments(course_id)
    if not ladok_assignments:
        print("No assignments for course {0} from transfer to LADOK".format(course_id))
        return

    # for example:
    # {'finalGrades': {'hasLetterGrade': False}, 'assignments': [{'id': '159727', 'name': 'Ethical Research - quiz', 'gradingType': 'points', 'dueAt': '2022-06-07T21:00:00Z', 'unlockAt': None, 'lockAt': None}, {'id': '159728', 'name': 'Professionalism and Ethics for ICT students - quiz', 'gradingType': 'points', 'dueAt': '2022-06-07T21:10:00Z', 'unlockAt': None, 'lockAt': None}, {'id': '159725', 'name': 'Ethical Research: Human Subjects and Computer Issues - quiz', 'gradingType': 'points', 'dueAt': '2022-06-07T21:45:00Z', 'unlockAt': None, 'lockAt': None}, {'id': '159726', 'name': 'Sustainable Development/Hållbar Utveckling - quiz', 'gradingType': 'points', 'dueAt': '2022-06-07T21:59:00Z', 'unlockAt': None, 'lockAt': None}, {'id': '159729', 'name': 'LADOK - PRO1 (Onlinequiz)', 'gradingType': 'letter_grade', 'dueAt': None, 'unlockAt': None, 'lockAt': None}]}
    verbose_print(f'{ladok_assignments=}')
    if verbose:
        print("Assignment id and name")
        for assignment in ladok_assignments['assignments']:
            print(f"{assignment['id']} {assignment['name']}")

    # get the current grades for each of the assignments
    for assignment in ladok_assignments['assignments']:
        print(f"processing assignment: {assignment}")
        current_grades=t2l_get_grades_for_an_assignment(course_id, assignment['id'])
        print(f"{assignment['name']}: {current_grades}")
        assignment_short_name=assignment_short_name_given_name(assignment['name'])
        for g in current_grades:
            student=g['student']
            if verbose:
                print("id={0}".format(student['id']))
                print("sortableName={0}".format(student['sortableName']))
                print("grade={0}".format(g['grade']))
                print("submittedAt={0}".format(g['submittedAt']))
            # check for matching sortable name
            if student['sortableName'] == gradebook[student['id']]['user_name']:
                if g['submittedAt']:
                    gradebook[student['id']]['assignments'][assignment_short_name]={'grade': g['grade'], 'submittedAt': g['submittedAt']}
                elif g['gradedAt']:
                    gradebook[student['id']]['assignments'][assignment_short_name]={'grade': g['grade'], 'submittedAt': g['gradedAt']}
                else:
                    print("error in entry for {} no submittedAt or gradedAt information".format(student['sortableName']))
            else:
                print("error in gradebook entry  {0} names do not match: {1} {2}".format(student['id'], student['sortableName'],  gradebook[student['id']]['user_name']))

    if verbose:
        print("updated gradebook")
        for u in users:
            print("gradebook[{0}]={1}".format(u.integration_id, gradebook[u.integration_id]))

    custom_columns=course.get_custom_columns(include_hidden=True)
    print(f'custom_columns={custom_columns}')
    for c in custom_columns:
        print("printing information about a CustomGradebookColumn")
        if testing:
            for attribute, value in c.__dict__.items():
                print(attribute, '=', value)
        print(f'{c.id} {c.title} at {c.position}')

    # Make sure "Notes" column is visible
    if custom_columns:
        for c in custom_columns:
            if c.title == 'Notes' and c.hidden:
                c.update_custom_column(column={'hidden': 'False'})
    else:
        # if missing, then add "Notes" column
        #insert_column_name(course_id, "Notes")
        course.create_custom_column(column={'title': 'Notes', 'hidden': 'False'})
        custom_columns=course.get_custom_columns()


    print("Printing custom_columns after making Notes not hidden")
    if verbose:
        for c in custom_columns:
            if testing:
                for attribute, value in c.__dict__.items():
                    print(attribute, '=', value)
            print(f'{c.id} {c.title} at {c.position}')

    print("getting custom column data")
    custom_column_data=dict()
    for c in custom_columns:
        if c.hidden:     #  skip hidden columns
            continue
        if c.teacher_notes:     #  skip teacher notes columns
            continue
        print("getting data for column {}".format(c.title))
        data=c.get_column_entries()
        if verbose and testing:
            for attribute, value in data.__dict__.items():
                print(attribute, '=', value)
            # the attributes are:
            # _elements = []
            # _requester = <canvasapi.requester.Requester object at 0x7f6151ea7a60>
            # _content_class = <class 'canvasapi.custom_gradebook_columns.ColumnData'>
            # _first_url = courses/30565/custom_gradebook_columns/1798/data
            # _first_params = {'_kwargs': [], 'per_page': 100}
            # _next_url = courses/30565/custom_gradebook_columns/1798/data
            # _next_params = {'_kwargs': [], 'per_page': 100}
            # _extra_attribs = {'course_id': 30565, 'gradebook_column_id': 1798}
            # _request_method = GET
            # _root = None

        custom_column_data[c.title]=data



    print("custom_column_data={0}".format(custom_column_data))
    custom_column_data_notes=dict()
    if 'Notes' in custom_column_data:
        ccdn=custom_column_data['Notes']
        verbose_print(f'{ccdn=}')
        for cdi in ccdn:
            verbose_print(f'{cdi=}')
            custom_column_data_notes[cdi.user_id]=cdi.content
            if verbose or testing:
                for attribute, value in cdi.__dict__.items():
                    print(attribute, '=', value)
            # This output entries of the form:
            # content = P
            # user_id = xxxxx         <<<< Note that this is a Canvas user_id
            # course_id = 18735
            # gradebook_column_id = 1188

    print("custom_column_data_notes={}".format(custom_column_data_notes))

    # enter Notes data into gradebook dict by matching user_id with canvas_id
    for u in users:
        for cdi in custom_column_data['Notes']:
            if cdi.user_id == u.id:
                gradebook[u.integration_id]['notes']=cdi.content

    if verbose:
        print("Gradebook with notes")
        for u in users:
            print("gradebook[{0}]={1}".format(u.integration_id, gradebook[u.integration_id]))

    if Verbose_Flag:
        pprint.pprint(gradebook, indent=4)
    print("number of users in gradebook={0}".format(len(gradebook)))

    er_due_date=assignment_due_date('ER')
    pe_due_date=assignment_due_date('PE')
    erh_due_date=assignment_due_date('ERH')
    susd_due_date=assignment_due_date('SUSD')

    print(f'er_due_date: {er_due_date}, pe_due_date:{pe_due_date}, erh_due_date: {erh_due_date}, susd_due_date: {susd_due_date}')

    print("grading_type_points('ER')={}".format(grading_type_points('ER')))
    print("grade('ER', 'fb132002-d4e0-11ec-aa2b-20f54c694dd5')={}".format(grade('ER', 'fb132002-d4e0-11ec-aa2b-20f54c694dd5')))

    # look at computing grades for each student s
    for s in gradebook:
        er_grade = pe_grade = erh_grade = susd_grade =False

        # Example of an assignment with points and a passing threshold of all but one point
        #
        # 1. check that the grading type is points and get the grade
        # 2. compare the points gotten with the points threshold for this assignment to pass
        #    If the assignment passes er_grade is set to True
        if grading_type_points('ER'):
            er_points=float(grade('ER', s))
            if er_points:
                er_grade = er_points >= (points_possible('ER') - 1.0)

        if grading_type_points('PE'):
            pe_points=float(grade('PE', s))
            if pe_points:
                pe_grade= pe_points>= (points_possible('PE') - 1.0)

        if grading_type_points('ERH'):
            erh_points = float(grade('ERH', s))
            if erh_points:
                erh_grade= erh_points >= (points_possible('ERH') - 1.0)

        if grading_type_points('SUSD'):
            susd_points=float(grade('SUSD', s))
            if susd_points:
                susd_grade= susd_points >= (points_possible('SUSD') - 1.0)

        print("er_grade={0}, pe_grade={1}, erh_grade={2}, susd_grade={3}".format(er_grade, pe_grade, erh_grade, susd_grade))

        gt=assignment_grading_type('PRO1')
        print("grading type is {0}".format(gt))
        cg=gradebook[s]['assignments']['PRO1']
        print("latest current grade is {}".format(cg))

        # Example of assigning a grade for a student who has passed all for assignments
        if er_grade and pe_grade and erh_grade and susd_grade and gradebook[s]['assignments']['PRO1'] != 'P':
            assign_grade('PRO1', s, 'P', 'test grade assignment')

            # Example of getting a value from a custom column
            s_note=gradebook[s]['notes']
            print("s_note={}".format(s_note))                    
            if True or s_note is None or s_note != 'P':
                # for a studen who has passed all the assignments, compute the data the last one was submitted
                er_submitted=submission_date('ER', s)
                pe_submitted=submission_date('PE', s)
                erh_submitted=submission_date('ERH', s)
                susd_submitted=submission_date('SUSD', s)
                if er_submitted and pe_submitted and erh_submitted and susd_submitted:
                    submission_dates=[er_submitted,
                                      pe_submitted,
                                      erh_submitted,
                                      susd_submitted
                                      ]
                    last_submission_date=max(submission_dates)
                    # Example of storing a value into a custom column named 'Notes' for a student s
                    data_to_store="Data ready for LADOK as of {}".format(last_submission_date)
                    put_custom_column_entries(custom_columns, 'Notes', gradebook[s]['canvas_id'], data_to_store)
                    gradebook[s]['notes']=data_to_store
                    if s == '8e51e001-b973-11eb-b259-d618d1cb4077': # for testing
                        break
                    

        # Example of processing the date of the submssion and checking the assignment's due date
        #
        # if you want to check if the assignment was submitted after the due date
        er_submitted=submission_date('ER', s)
        if  er_submitted:
            if er_submitted > er_due_date:
                print("Late submission of ER by {0}".format(gradebook[s]['user_name']))
            else:
                er_early_submission=submission_date('ER', s) - er_due_date
                print("early submission by {0}".format(er_early_submission))



    return                      # gqmjr for testing - qqq

    if verbose:
        print("calling t2l_get_sections()")
    ladok_sections=t2l_get_sections(course_id)
    if not ladok_sections:
        print("Unable to get section for course {0} from transfer to LADOK".format(course_id))
        return

    # a section might yield:
    # respose.text={"aktivitetstillfalle":[],"kurstillfalle":[{"id":"a8881a52-ac13-11eb-b185-19658d9640e0","utbildningsinstans":"6320c0b1-5cfe-11e9-b67f-a77d6cb34fef","code":"60415","modules":[{"utbildningsinstans":"884b851f-5cfe-11e9-b67f-a77d6cb34fef","code":"PRO1","name":"Onlinequiz"}]}]}
    verbose_print(f'{ladok_sections=}')
    print("type of ladok_sections={}".format(type(ladok_sections)))
    # ladok_sections={'aktivitetstillfalle': [], 'kurstillfalle': [{'id': 'a8881a52-ac13-11eb-b185-19658d9640e0', 'utbildningsinstans': '6320c0b1-5cfe-11e9-b67f-a77d6cb34fef', 'courseCode': 'II2210', 'roundCode': '60415', 'modules': [{'utbildningsinstans': '884b851f-5cfe-11e9-b67f-a77d6cb34fef', 'code': 'PRO1', 'name': 'Onlinequiz'}]}]}
    for e in ladok_sections:
        print("e={0} {1}".format(e, ladok_sections[e]))

    print(f"ladok_sections['aktivitetstillfalle']={ladok_sections['aktivitetstillfalle']}")
    print(f"ladok_sections['kurstillfalle']={ladok_sections['kurstillfalle']}")
    #[   {   'courseCode': 'II2210',
    #        'id': 'a8881a52-ac13-11eb-b185-19658d9640e0',
    #        'modules': [   {   'code': 'PRO1',
    #                           'name': 'Onlinequiz',
    #                          'utbildningsinstans': '884b851f-5cfe-11e9-b67f-a77d6cb34fef'}],
    #    'roundCode': '60415',
    #    'utbildningsinstans': '6320c0b1-5cfe-11e9-b67f-a77d6cb34fef'}]

    print(f"ladok_sections['kurstillfalle'][0]={ladok_sections['kurstillfalle'][0]}")
    print(f"ladok_sections['kurstillfalle'][0]['id']={ladok_sections['kurstillfalle'][0]['id']}")
    print(f"ladok_sections['kurstillfalle'][0]['modules']={ladok_sections['kurstillfalle'][0]['modules']}")
    print(f"ladok_sections['kurstillfalle'][0]['modules'][0]={ladok_sections['kurstillfalle'][0]['modules'][0]}")
    print(f"ladok_sections['kurstillfalle'][0]['modules'][0]['utbildningsinstans']={ladok_sections['kurstillfalle'][0]['modules'][0]['utbildningsinstans']}")
    # ladok_sections['kurstillfalle'] takes the form:
    # [{'id': 'a8881a52-ac13-11eb-b185-19658d9640e0', 'utbildningsinstans': '6320c0b1-5cfe-11e9-b67f-a77d6cb34fef', 'code': '60415', 'modules': [{'utbildningsinstans': '884b851f-5cfe-11e9-b67f-a77d6cb34fef', 'code': 'PRO1', 'name': 'Onlinequiz'}]}]

    print(f"ladok_sections['kurstillfalle'][0]['utbildningsinstans']={ladok_sections['kurstillfalle'][0]['utbildningsinstans']}")

    if verbose:
        print("calling t2l_gradable_students()")
    gradable_students_in_course=t2l_gradable_students(course_id,
                                                      kurstillfalle=ladok_sections['kurstillfalle'][0]['id'],
                                                      utbildningsinstans=ladok_sections['kurstillfalle'][0]['modules'][0]['utbildningsinstans'])
                                                      #utbildningsinstans=ladok_sections['kurstillfalle'][0]['utbildningsinstans'])
    verbose_print(f'{gradable_students_in_course=}')

    print(f'gradable_students_in_course={gradable_students_in_course}')
    return                      # gqmjr for testing
    grade_feed=list_gradebook_history_feed()
    print("length of grade_feed={0}".format(len(grade_feed)))
    if Verbose_Flag:
        print("grade_feed={0}".format(grade_feed))


    for e in grade_feed:
        if Verbose_Flag:
            pprint.pprint(e, indent=4)
            print("{0}, {1}, {2}, {3}, {4}, {5}".format(e['user_id'], e['user_name'], e['assignment_id'], e['attempt'], e['submitted_at'], e['entered_score']))
        gradebook_entry=gradebook.get(e['user_id'], False)
        if not gradebook_entry:
            gradebook_entry={'user_name': e['user_name'],
                             'assignments': {},
                             }

        s_assignments=gradebook_entry.get('assignments', False)
        if not s_assignments:
            s_assignments=dict()
    
        this_assignment=s_assignments.get(e['assignment_id'], False)
        if this_assignment:
            print("previous value for assignment={}".format(this_assignment))
            if Verbose_Flag:
                print("keep previous value for assignment={}".format(this_assignment))
            continue # added by Viggo 2021-05-30


        s_assignments[e['assignment_id']]={'attempt': e['attempt'],
                                           'submitted_at': e['submitted_at'],
                                           'entered_score': e['entered_score']
                                           }

        gradebook[e['user_id']]={'user_name': e['user_name'],
                                 'assignments': s_assignments,
                                 }

        if Verbose_Flag:
            print("gradebook[{0}]={1}".format(e['user_id'], gradebook[e['user_id']]))



if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

