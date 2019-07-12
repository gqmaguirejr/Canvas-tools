#!/usr/bin/python3
#
# ./insert_grades_and_comments.py course_id assignment_id file.csv
#
# G. Q. Maguire Jr.
#
# 2019.09.30
#
# Inserts grades for an assignment into the gradebook for a course.
# The column headings of the gradebook are assumed to have the form (where dddd is a Canvas user_id):
# Student,ID,assignment_name,assignment_name*comment*
# A B Normal (abn),dddd,A,"I wish I had written this report"
# F. Abend (fabend),dddd,E,"Terrible report"
#
# The format is basically that of the exported CSV produced from the gradebook by Canvas,
#  but with the addition of the "*comment*" postfix for an assignment, so that one can also upload comments along with grades.
#
# Note that there can be additional columns between the ID column and the assignment column and after the comment column,
#  as the assignment and comment name matching are done; hence, other columns are ignored.
#
#
# with the option '-C'or '--containers' use HTTP rather than HTTPS for access to Canvas
# with the option "-v" or "--verbose" you get lots of output - showing in detail the operations of the program
#
# Can also be called with an alternative configuration file:
# ./insert_grades_and_comments.py  --config config-test.json course_id assignment_id file.csv
#
# G. Q. Maguire Jr.
#
# based upon 2018.09.30 - Canvas-git/insert_grades_and_comments.py
#
# 2019.07.12
#

import csv, requests, time
from pprint import pprint
import optparse
import sys

from io import StringIO, BytesIO

import json

import datetime
import isodate                  # for parsing ISO 8601 dates and times
import pytz                     # for time zones
import os                       # to make OS calls, here to get time zone info
from dateutil.tz import tzlocal

# Use Python Pandas to create XLSX files
import pandas as pd

# to use math.isnan(x) function
import math
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

def utc_to_local(utc_dt):
    return utc_dt.replace(tzinfo=datetime.timezone.utc).astimezone(tz=None)

##############################################################################
## ONLY update the code below if you are experimenting with other API calls ##
##############################################################################

def enrollments_in_course(course_id):
    global Verbose_Flag
    users_found_thus_far=[]

    # Use the Canvas API to get the list of users enrolled in this course
    #GET /api/v1/courses/:course_id/enrollments

    url = "{0}/courses/{1}/enrollments".format(baseUrl,course_id)

    if Verbose_Flag:
        print("url: " + url)

    r = requests.get(url, headers = header)
    if Verbose_Flag:
        print("result of getting enrollments: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        page_response=r.json()

        for p_response in page_response:  
            users_found_thus_far.append(p_response)

        # the following is needed when the reponse has been paginated
        # i.e., when the response is split into pieces - each returning only some of the list of modules
        # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
        while r.links['current']['url'] != r.links['last']['url']:  
            r = requests.get(r.links['next']['url'], headers=header)  
            page_response = r.json()  
            for p_response in page_response:  
                users_found_thus_far.append(p_response)

    return users_found_thus_far

def list_assignments(course_id):
    global Verbose_Flag
    assignments_found_thus_far=[]

    # Use the Canvas API to get the list of assignments for the course
    #GET /api/v1/courses/:course_id/assignments

    url = "{0}/courses/{1}/assignments".format(baseUrl,course_id)

    if Verbose_Flag:
        print("url: " + url)

    r = requests.get(url, headers = header)
    if Verbose_Flag:
        print("result of getting assignments: {}".format(r.text))
    if r.status_code == requests.codes.ok:
        page_response=r.json()

        for p_response in page_response:  
            assignments_found_thus_far.append(p_response)

        # the following is needed when the reponse has been paginated
        # i.e., when the response is split into pieces - each returning only some of the list of modules
        # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
        while r.links['current']['url'] != r.links['last']['url']:  
            r = requests.get(r.links['next']['url'], headers=header)  
            page_response = r.json()  
            for p_response in page_response:  
                assignments_found_thus_far.append(p_response)

    return assignments_found_thus_far


def get_assignment_details(course_id, assignment_id):
    global Verbose_Flag
    # Use the Canvas API to get a specific assignments for the course
    #GET /api/v1/courses/:course_id/assignments/:id

    url = "{0}/courses/{1}/assignments/{2}".format(baseUrl, course_id,  assignment_id)
    if Verbose_Flag:
        print("url: " + url)

    r = requests.get(url, headers = header)
    if Verbose_Flag:
        print("result of getting assignment: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        page_response=r.json()
        return  page_response
    else:
        return None


def get_grade_for_assignment(course_id, assignment_id, user_id):
    global Verbose_Flag
    # Use the Canvas API to assign a grade for an assignment
    #GET /api/v1/courses/:course_id/assignments/:assignment_id/submissions/:user_id

    # Request Parameters:
    # include[] string	Associations to include with the group.
    #                   Allowed values: submission_history, submission_comments, rubric_assessment, visibility, course, user

    url = "{0}/courses/{1}/assignments/{2}/submissions/{3}".format(baseUrl,course_id, assignment_id, user_id)

    if Verbose_Flag:
       print("url: " + url)

    payload={'include[]': 'submission_comments'}

    r = requests.get(url, headers = header, data=payload)
    if Verbose_Flag:
        print("result of getting assignment: {}".format(r.text))
    if r.status_code == requests.codes.ok:
        page_response=r.json()
        return page_response
    return None

def assign_grade_for_assignment(course_id, assignment_id, user_id, grade, comment):
    global Verbose_Flag
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

def main():
    global Verbose_Flag
    global Use_Local_Time_For_Output_Flag

    # same data used in the program
    Use_Local_Time_For_Output_Flag=True
    Number_of_students_enrolled=0


    parser = optparse.OptionParser()

    parser.add_option('-v', '--verbose',
                      dest="verbose",
                      default=False,
                      action="store_true",
                      help="Print lots of output to stdout"
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


    if (len(remainder) < 3):
        print("Insuffient arguments must provide course_id assignment_id file_name.csv\n")
        return

    course_id=remainder[0]
    assignment_id=int(remainder[1])
    csv_file=remainder[2]
   
    print("course_id={0}, assignment_id={1}, file_name='{2}'".format(course_id, assignment_id, csv_file))

    # read in the CSV entries (assumed to have been exported from the gradebook)
    gradebook_df=pd.read_csv(csv_file, sep=',')
    if Verbose_Flag:
        print("gradebook_df={}".format(gradebook_df))

    # get a list of the assignments in the courses
    assignments=list_assignments(course_id)
    if Verbose_Flag:
        print("assignments={}".format(assignments))

    # get a list of those enrolled in the course
    enrollments=enrollments_in_course(course_id) # students in the Canvas course
    if Verbose_Flag:
        print("Number of enrollments_in_course={}".format(len(enrollments)))

    for a in assignments:
        if Verbose_Flag:
            print("assignment id={0} name={1}".format(a['id'], a['name']))
        if a['id'] == assignment_id:
            assignment_name=a['name']
            if Verbose_Flag:
                print("assignment_name={}".format(assignment_name))

    if not assignment_id:
        print("No assignment with ID: {}", assignment_id)
        return
    
    grade_header=''
    comments_header=''
    match_count=0
    headers=list(gradebook_df)
    for h in headers:
        if h.find(assignment_name) >= 0:
            match_count=match_count+1
            print("h={}".format(h))
            if match_count==1:
                grade_header=h
            if h.find('*comment*') >= 0:
                comments_header=h

    if len(grade_header) and len(comments_header) > 0:
        print("grade_header={0}, comments_header={1}".format(grade_header, comments_header))

        for index, row in gradebook_df.iterrows():
            name=row['Student']
            user_id=row['ID']
            new_grade=row[grade_header]
            comment=row[comments_header]
        
            #if Verbose_Flag:
            print("user_id={0}, name={1}, new_grade={2}, comment={3}".format(user_id, name, new_grade, comment))
            grade=get_grade_for_assignment(course_id, assignment_id, user_id)
            print("existing_grade={}".format(grade))

            Verbose_Flag=True
            ag=assign_grade_for_assignment(course_id, assignment_id, user_id, new_grade,comment)
            print("ag is {0}".format(ag))

            final_grade=get_grade_for_assignment(course_id, assignment_id, user_id)
            print("final_grade={}".format(final_grade))



if __name__ == "__main__": main()
