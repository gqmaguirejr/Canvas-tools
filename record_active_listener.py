#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# ./record_active_listener.py course_id inputfile student_presenting_email
#
#
# Purpose: To help report student's active participation in a Canvas course room for a degree project
#
# the text file has the form:
# student name <xxx.kth.se>
# student name <xxx.kth.se>
# student name <xxx.kth.se>
# ...
#
# for each student look up their active listening assignments
# choose the first that does not have a grade and record a grade
# Perhaps one should check if there is a submission and if it matches the presentation being done
# If OK, then record a grade with a note of the exmainer and date
#
#
# Output: nothing specific
#
#
# with the option "-v" or "--verbose" you get lots of output - showing in detail the operations of the program
# with the option "--testing" it does not actually report a grade
#
# Example:
# ./record_active_listener.py 11 foo.txt
# ./record_active_listener.py  /z3/maguire/Exjobs-2022/xxxx/active_listeners.txt  xxxx@kth.se
#
# Can also be called with an alternative configuration file:
# ./record_active_listener.py --config config-test.json 33514 /z3/maguire/Exjobs-2022/xxxx/active_listeners.txt  xxxx@kth.se --testing
#
# G. Q. Maguire Jr.
#
# based on earlier quizzes-and-answers-in-course.py
#
# 2022-05-16
#

from argparse import ArgumentParser
import sys
import json
import re
from pathlib import Path
from collections import defaultdict

# Use Python Pandas to create XLSX files
import pandas as pd

# use lxml to access the HTML content
from lxml import html

# use the request package to get the HTML give an URL
import requests

# use the canvasapai
import canvasapi

#############################
###### EDIT THIS STUFF ######
#############################

verbose = False # Global flag for verbose prints
DEFAULT_CONFIG_FILE = 'config.json'

TARGET_DIR = './Quiz_Submissions'


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


def dir_name_for_urls(url: str, target_dir: str) -> str:
    # the URLs have the form: https://canvas.kth.se/courses/11/quizzes/39141/history?quiz_submission_id=759552&version=1
    subdir_name = re.sub(r'^.*/courses/(\d+)/quizzes/(\d+)/history\?quiz_submission_id=(\d+)&version=\d+.*$',
                         r'\1/\2/\3',
                         url)
    if subdir_name == url:
        raise ValueError(f'Invalid URL: {url}')
    return f'{target_dir}/{subdir_name}'


def verbose_print(*args, **kwargs) -> None:
    global verbose
    if verbose:
        print(*args, **kwargs)


def main():
    global verbose

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
    parser.add_argument('inputfile')
    parser.add_argument('student_presenting_email')

    args = parser.parse_args()

    verbose_print(f'ARGV      : {sys.argv[1:]}')
    verbose_print(f'VERBOSE   : {args.verbose}')
    verbose_print(f'COURSE_ID : {args.course_id}')
    verbose_print(f'Configuration file : {args.config_filename}')

    verbose = args.verbose
    testing = args.testing
    course_id = args.course_id
    inputfile = args.inputfile
    student_presenting_email=args.student_presenting_email
    
    config = read_config(args.config_filename)

    print(f'course_id={course_id}')

    # Initialize Canvas API
    canvas = canvasapi.Canvas('https://'+config["canvas"]["host"],config["canvas"]["access_token"])

    course = canvas.get_course(course_id)
    verbose_print(f'{course=}')

    active_listening_assignments=dict()
    assignments=course.get_assignments()
    for assignment in assignments:
        if assignment.name.find('Active listening') >= 0:
            print(f'{assignment.name} is {assignment.id}')
            active_listening_assignments[assignment.name]=assignment

    #verbose_print(f'{active_listening_assignments=}')

    if student_presenting_email:
        print(f'student_presenting_email={student_presenting_email}')
        try:
            student_presenting=canvas.get_user(student_presenting_email, 'sis_login_id')
        except:
            print("Could not look up user by their e-mail address")
            student_presenting=None
    else:
        student_presenting=None
    print(f'student_presenting={student_presenting}')

    try:
        with open(inputfile) as in_file:
            students = in_file.readlines()
    except:
        print("Unable to open file named {}".format(inputfile))
        sys.exit()

    students_with_grade_entered=set()

    for line in students:
        start_marker='<'
        end_marker='>'
        grade_recorded=False

        if start_marker in line and end_marker in line:
            start_offset=line.find(start_marker)+1
            end_offset=line.find(end_marker, start_offset)
            if start_offset >= 0 and end_offset > start_offset:
                email_address=line[start_offset:end_offset]
                if email_address in students_with_grade_entered:
                    print(f'already entered a grade for {email_address} - nothing to do')
                    continue
                if verbose:
                    print(f'email_address={email_address}')
                try:
                    user = canvas.get_user(email_address, 'sis_login_id')
                except:
                    print(f'user with {email_address} not found')
                    break

                print(f'{user.sortable_name}')
                for al_instance, assignment in active_listening_assignments.items():
                    verbose_print(f'{al_instance=}')                    
                    print(f'assignment.name={assignment.name}')
                    try:
                        subm=assignment.get_submission(user)
                    except:
                        print(f'user {user.sortable_name} is not enrolled in the course {course_id}')
                        break
                    verbose_print(f'{subm=}')
                    if subm.workflow_state == 'graded' and subm.entered_grade: #  already a grade submission for this assignment
                        grader=canvas.get_user(subm.grader_id)
                        print(f'{subm.entered_grade} on {subm.graded_at} by {grader.short_name} body={subm.body}')
                        continue
                    elif subm.workflow_state == 'submitted': #  student submitted something, check if it is for the current presentation
                        submitted_at=subm.submitted_at
                        print(f'submitted {submitted_at} body={subm.body}')
                        # process it
                        user_response = input("Is the submission for the student who is presenting (Y/N):?")
                        if user_response in ['Y', 'y']:
                            if not grade_recorded:
                                if student_presenting:
                                    comment=f'Active listener for {student_presenting.short_name}'
                                    if not testing: # when testing do not actually report a grade
                                        subm.edit(submission={'posted_grade': 'complete', 'comment[text_comment]': comment})
                                    else:
                                        print('If not testing, would have reported a grade')
                                else:
                                    if not testing:
                                        subm.edit(submission={'posted_grade': 'complete'})
                                    else:
                                        print('If not testing, would have reported a grade')

                                grade_recorded=True
                                if not testing:
                                    subm_after=assignment.get_submission(user)
                                    verbose_print(f'{subm_after=}')
                                break
                    elif subm.workflow_state == 'unsubmitted' or not subm.entered_grade: #  student did not submit anything or they have a grade of None
                        if not grade_recorded:
                            if student_presenting:
                                comment=f'Active listener for {student_presenting.short_name}'
                                if not testing: # when testing do not actually report a grade
                                    subm.edit(submission={'posted_grade': 'complete', 'comment[text_comment]': comment})
                                else:
                                    print('If not testing, would have reported a grade')
                            else:
                                if not testing:
                                    subm.edit(submission={'posted_grade': 'complete'})
                                else:
                                    print('If not testing, would have reported a grade')

                            grade_recorded=True
                            if not testing:
                                subm_after=assignment.get_submission(user)
                                verbose_print(f'{subm_after=}')
                            break
                    else:
                        print(f'else case - unhandled case submissions={sumb}')

                if grade_recorded:
                    students_with_grade_entered.add(email_address)
    return

if __name__ == "__main__": main()

