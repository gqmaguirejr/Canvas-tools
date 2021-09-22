#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -*- mode: python; python-indent-offset: 4 -*-
#
# II2210-grades_to_report.py -c course_id
#
# Example:
# ./II2210-grades_to_report.py    -c 11 
#
# The program can walk a gradebook and do computations on the grades. Currently, it is for a course with 4 assigned that each have a certain maximum number of points.
# Note that you have to manually add a short name for each assignment_id number.
#  
# Note that the "Notes" column has to be set to visible in the gradebook before the program will add the date inofmration to the notes column.
#
# 2021.04.12 G. Q. Maguire Jr.
#
#
# The dates from Canvas are in ISO 8601 format.
#
import re
import sys

import json
import argparse
import os			# to make OS calls, here to get time zone info

import requests, time
import pprint

import isodate                  # for parsing ISO 8601 dates and times
import pytz                     # for time zones
from dateutil.tz import tzlocal

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

def list_assignments():
    global Verbose_Flag
    global course_id
    entries_found_thus_far=[]

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


def points_possible(short_name):
    global assignments
    for a in assignments:
        if a['short_name'] == short_name:
            return a['points_possible']
    return None

def assignment_given_short_name(short_name):
    global assignments
    for a in assignments:
        if a['short_name'] == short_name:
            return a
    return None

def assignment_due_date(short_name):
    global assignments
    for a in assignments:
        if a['short_name'] == short_name:
            return isodate.parse_datetime(a['due_at'])
    return None

def assignment_grading_type(short_name):
    global assignments
    for a in assignments:
        if a['short_name'] == short_name:
            return a['grading_type']
    return None

def grading_type_points(short_name):
    gt=assignment_grading_type(short_name) 
    if gt:
        return gt == 'points'
    return None

def assignment_grading_standard_id(short_name):
    global assignments
    for a in assignments:
        if a['short_name'] == short_name:
            return a['grading_standard_id']
    return None

def get_a_grade(user_id, short_name):
    global Verbose_Flag
    g=get_asssignment_grade(user_id, short_name)
    if g and len(g) > 1:
        return g[0]['grade']             # by default the latest grade is first
    return None

def get_asssignment_grade(user_id, short_name):
    global Verbose_Flag
    global course_id
    
    assignment=assignment_given_short_name(short_name)
    if assignment:
        assignment_id=assignment['id']
    else:
        print("No such assignment named {0}".format(shrt_name))
        return None

    entries_found_thus_far=[]

    # Use the Canvas API to get the grade information
    # GET /api/v1/courses/:course_id/gradebook_history/feed

    url = "{0}/courses/{1}/gradebook_history/feed".format(baseUrl, course_id)
    if Verbose_Flag:
        print("url: {}".format(url))

    extra_parameters={'per_page': '100',
             'assignment_id': assignment_id,
             'user_id':  user_id
             }
    
    r = requests.get(url, params=extra_parameters, headers = header)

    if Verbose_Flag:
        print("result of getting a grade from gradebook: {}".format(r.text))

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

def grade(short_name, student):
    global gradebook

    assignment=assignment_given_short_name(short_name)
    if assignment:
        assignment_id=assignment['id']
    else:
        print("No such assignment named {0}".format(shrt_name))
        return None

    if gradebook.get(student, False):
        students_assignments=gradebook[student].get('assignments', False)
        if not students_assignments:
            return None             # student has no assignments

        this_assignment=students_assignments.get(assignment_id, False)
        if this_assignment:
            return this_assignment.get('entered_score', None)

    return None


def assign_grade(short_name,user_id, grade, comment):
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
    if assignment:
        assignment_id=assignment['id']
    else:
        print("No such assignment named {0}".format(shrt_name))
        return None

    if gradebook.get(student, False):
        students_assignments=gradebook[student].get('assignments', False)
        if not students_assignments:
            return None             # student has no assignments

        this_assignment=students_assignments.get(assignment_id, False)
        if this_assignment:
            td=this_assignment.get('submitted_at', None)
            if td:
                return isodate.parse_datetime(td)

    return None

# [{'id': 1684, 'title': 'Notes', 'position': 1, 'teacher_notes': True, 'read_only': False, 'hidden': False}]
def custom_column_id(title):
    global custom_columns
    for c in custom_columns:
        if title == c['title']:
            return c['id']
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

def put_custom_column_entries(column_id, user_id, data_to_store):
    global course_id
    entries_found_thus_far=[]

    # Use the Canvas API to get the list of custom column entries for a specific column for the course
    #PUT /api/v1/courses/:course_id/custom_gradebook_columns/:id/data/:user_id

    url = "{0}/courses/{1}/custom_gradebook_columns/{2}/data/{3}".format(baseUrl,course_id, column_id, user_id)
    if Verbose_Flag:
        print("url: " + url)

    payload={'column_data[content]': data_to_store}
    r = requests.put(url, headers = header, data=payload)

    if Verbose_Flag:
        print("result of putting data into custom_gradebook_column:  {}".format(r.text))

    if r.status_code == requests.codes.ok:
        page_response=r.json()

        for p_response in page_response:  
            entries_found_thus_far.append(p_response)

    return entries_found_thus_far

def main(argv):
    global Verbose_Flag
    global assignments
    global custom_columns
    global custom_column_data
    global gradebook
    global Use_local_time_for_output_flag
    global course_id

    Use_local_time_for_output_flag=True

    timestamp_regex = r'(2[0-3]|[01][0-9]|[0-9]):([0-5][0-9]|[0-9]):([0-5][0-9]|[0-9])'

    argp = argparse.ArgumentParser(description="II2202-grades_to_report.py: look for students who have passed the 4 assignments and need a grade assigned")

    argp.add_argument('-v', '--verbose', required=False,
                      default=False,
                      action="store_true",
                      help="Print lots of output to stdout")

    argp.add_argument("--config", type=str, default='config.json',
                      help="read configuration from file")

    argp.add_argument("-c", "--canvas_course_id", type=int, required=True,
                      help="canvas course_id")
    
    argp.add_argument('-C', '--containers',
                      default=False,
                      action="store_true",
                      help="for the container enviroment in the virtual machine, uses http and not https")

    args = vars(argp.parse_args(argv))

    Verbose_Flag=args["verbose"]

    initialize(args)
    if Verbose_Flag:
        print("baseUrl={}".format(baseUrl))

    course_id=args["canvas_course_id"]
    print("course_id={}".format(course_id))

    assignments=list_assignments()
    if Verbose_Flag:
        print("assignments={0}".format(assignments))

    assignment_summary=[]

    for a in assignments:
        print("id={0}, name={1}, points_possible={2}, due_at={3}, grading_type={4}, grading_standard_id={5}, allowed_attempts={6}".format(a['id'], a['name'], a['points_possible'], a['due_at'], a['grading_type'], a['grading_standard_id'], a['allowed_attempts']))

        # Set up the short names for the assignments
        # ***** This is essential as the routines will use the short names to access the relevant assignment and grades
        # You have to look at the assignment id for each assignment and then add a short_name to the assignment
        # You can do this by matching assignment_id numbers or matching the names
        if a['id'] == 146887 or a['name'] == 'Ethical Research (with quiz)':
            a['short_name']= 'ER'

        if a['id'] == 146888 or a['name'] == 'Professionalism and Ethics for ICT students (with quiz)':
            a['short_name']= 'PE'

        if a['id'] == 146885 or a['name'] == 'Ethical Research: Human Subjects and Computer Issues (with quiz)':
            a['short_name']= 'ERH'

        if a['id'] == 146886 or a['name'] == 'Sustainable Development/Hållbar Utveckling (with quiz)':
            a['short_name']= 'SUSD'

        if a['id'] == 146889 or a['name'] == 'LADOK - PRO1 (Onlinequiz)':       # the moment to report to LADOK
            a['short_name']= 'PRO1'

        if Verbose_Flag:
            print("assignments={0}".format(assignments))

    custom_columns=list_custom_columns()
    print("custom_columns={}".format(custom_columns))

    custom_column_data=dict()
    for c in custom_columns:
        custom_column_data[c['title']]=list_custom_column_entries(c['id'])



    grade_feed=list_gradebook_history_feed()
    print("length of grade_feed={0}".format(len(grade_feed)))
    if Verbose_Flag:
        print("grade_feed={0}".format(grade_feed))
    gradebook=dict()

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

    pprint.pprint(gradebook, indent=4)
    print("number of users in gradebook={0}".format(len(gradebook)))


    er_due_date=assignment_due_date('ER')
    pe_due_date=assignment_due_date('PE')
    erh_due_date=assignment_due_date('ERH')
    susd_due_date=assignment_due_date('SUSD')

    # look at computing grades for each student s
    for s in gradebook:
        er_grade = pe_grade = erh_grade = susd_grade =False

        # Example of an assignment with points and a passing threshold of all but one point
        #
        # 1. check that the grading type is points and get the grade
        # 2. compare the points gotten with the points threshold for this assignment to pass
        #    If the assignment passes er_grade is set to True
        er_points=grading_type_points('ER') and grade('ER', s)
        if er_points:
            er_grade = er_points >= (points_possible('ER') - 1.0)

        pe_points=grading_type_points('PE') and grade('PE', s)
        if pe_points:
            pe_grade= pe_points>= (points_possible('PE') - 1.0)

        erh_points = grading_type_points('ERH') and grade('ERH', s)
        if erh_points:
            erh_grade= erh_points >= (points_possible('ERH') - 1.0)

        susd_points=grading_type_points('SUSD') and grade('SUSD', s)
        if susd_points:
            susd_grade= susd_points >= (points_possible('SUSD') - 1.0)

        print("er_grade={0}, pe_grade={1}, erh_grade={2}, susd_grade={3}".format(er_grade, pe_grade, erh_grade, susd_grade))

        g1=grade('PRO1', s)
        print("grade is currently {}".format(g1))
        gt=assignment_grading_type('PRO1')
        print("grading type is {0}".format(gt))
        cg=get_a_grade(s, 'PRO1')
        print("latest current grade is {}".format(cg))

        # Example of assigning a grade for a student who has passed all for assignments
        if er_grade and pe_grade and erh_grade and susd_grade and get_a_grade(s, 'PRO1') != 'P':
            assign_grade('PRO1', s, 'P', 'test grade assignment')

            # Example of getting a value from a custom column
            s_note=custom_column_value(s, 'Notes')
            print("s_note={}".format(s_note))                    
            if s_note is None or s_note != 'P':
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
                    put_custom_column_entries(custom_column_id('Notes'), s, data_to_store)

                # refresh the copy of the custom column data after changing it.
                custom_column_data['Notes']=list_custom_column_entries(custom_column_id('Notes'))
                s_note=custom_column_value(s, 'Notes')
                if s_note:
                    print("s_note={0}, len of string={1}".format(s_note, len(s_note)))


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


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

