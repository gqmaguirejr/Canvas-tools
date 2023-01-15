#!/usr/bin/python3
# -*- coding: utf-8 -*-
# -*- mode: python; python-indent-offset: 4 -*-
#
# ./add_course_codes_for_students_in_course.py course_id [admin_assignment_name]
#
# admin_assignment_name = 'Course code' by default
#
# Output: using assignment 'Course code' as the administrative data to do assign course codes as grades
# 	Added the course code (using the Course Code grading scale) based in the SIS section that each student is in
#
# This program uses the fact that the section name starts with the course code, i.e.
#    sis_section_id[5] =='X' and (sis_section_id[2] == '1' or sis_section_id[2] == '2')
#
# with the option "-v" or "--verbose" you get lots of output - showing in detail the operations of the program
#
# Can also be called with an alternative configuration file:
# ./add_course_codes_for_students_in_course.py --config config-test.json 22156
#
# Example:
# ./add_course_codes_for_students_in_course.py 22156
#
# or
#
# ./add_course_codes_for_students_in_course.py 22156 "Kurs Kod"
#
# 
# G. Q. Maguire Jr.
#
# based on earlier add_students_to_examiners_section_in_course.py
#
# 2021.02.14
#
# 2023-01-15 modified to deal with the change in the use of the sis_section_id.
#

import requests, time
import pprint
import optparse
import sys
import json

# Import urlopen() for either Python 2 or 3.
try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen

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

# create the following dict to use as an associate directory about users
selected_user_data={}


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

def user_name_from_user_id(enrollments, id):
    for i in enrollments:
        if i['user_id'] == id:
            return i['user']['name']

def users_sections_from_user_id(enrollments, id):
    section_id=list()
    for i in enrollments:
        if i['user_id'] == id:
            section_id.append(i['course_section_id'])
    return section_id

def section_name_from_section_id(sections_info, section_id): 
    for i in sections_info:
        if i['id'] == section_id:
            return i['name']

def section_id_from_section_name(sections_info, section_name): 
    for i in sections_info:
        if i['name'] == section_name:
            return i['id']
    return False

def sections_in_course(course_id):
    sections_found_thus_far=[]
    # Use the Canvas API to get the list of sections for this course
    #GET /api/v1/courses/:course_id/sections

    url = "{0}/courses/{1}/sections".format(baseUrl,course_id)
    if Verbose_Flag:
        print("url: {}".format(url))

    r = requests.get(url, headers = header)
    if Verbose_Flag:
        print("result of getting sections: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        page_response=r.json()

        for p_response in page_response:  
            sections_found_thus_far.append(p_response)

        # the following is needed when the reponse has been paginated
        # i.e., when the response is split into pieces - each returning only some of the list of modules
        # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
        while r.links.get('next', False):
            r = requests.get(r.links['next']['url'], headers=header)  
            page_response = r.json()  
            for p_response in page_response:  
                sections_found_thus_far.append(p_response)

    return sections_found_thus_far

def assignment_id_from_assignment_name(assignments_info, assignment_name): 
    for i in assignments_info:
        if i['name'] == assignment_name:
            return i['id']
    return False

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

def get_grade_for_assignment(course_id, assignment_id, user_id):
    global Verbose_Flag
    # Use the Canvas API to assign a grade for an assignment
    #GET /api/v1/courses/:course_id/assignments/:assignment_id/submissions/:user_id

    # Request Parameters:
    # include[] string	Associations to include with the group.
    #                   Allowed values: submission_history, submission_comments, rubric_assessment, visibility, course, user

    url = "{0}/courses/{1}/assignments/{2}/submissions/{3}".format(baseUrl, course_id, assignment_id, user_id)

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
                      help="execute test code"
                      )


    options, remainder = parser.parse_args()

    Verbose_Flag=options.verbose
    if Verbose_Flag:
        print("ARGV      : {}".format(sys.argv[1:]))
        print("VERBOSE   : {}".format(options.verbose))
        print("REMAINING : {}".format(remainder))
        print("Configuration file : {}".format(options.config_filename))


    initialize(options)

    pp = pprint.PrettyPrinter(indent=4) # configure prettyprinter

    if (len(remainder) < 1):
        print("Insuffient arguments - must provide course_id\n")
        return

    course_id=remainder[0]

    section_to_course_code_mapping=dict() # of the form {section_id: course_code}

    sections=sections_in_course(course_id)
    if Verbose_Flag:
        pp.pprint(sections)

    course_codes=set()
    for s in sections:
        section_name=s['name'] 
        if section_name and section_name[5] =='X' and (section_name[2] == '1' or section_name[2] == '2'):
            course_code=section_name[0:6]
            course_codes.add(course_code)
            section_to_course_code_mapping[s['id']]=course_code

    if Verbose_Flag:
        pp.pprint(course_codes)

    if Verbose_Flag:
        pp.pprint(section_to_course_code_mapping)

    if (len(remainder) > 1):
        admin_assignment_name=remainder[1]
    else:
        admin_assignment_name="Course code"

    print("Using sections to assign grades in the administrative assignment '{0}'".format(admin_assignment_name))

    # check for assignemnt
    course_assignments=list_assignments(course_id)
    assignment_id=assignment_id_from_assignment_name(course_assignments, admin_assignment_name)
    if not assignment_id:
        print("No assignment named {0}".format(admin_assignment_name))
        return
    
    if Verbose_Flag:
        print("assignment_id={}".format(assignment_id))

    enrollments=users_in_course(course_id)

    number_of_students_processed=0
    # get the "grade" of the administrative assignment
    student_ids=set()
    for e in enrollments:
        if e['type'] == 'StudentEnrollment':
            students_userid=e['user_id']
            student_ids.add(students_userid)
            course_section_id=e['course_section_id']
            if course_section_id:
                number_of_students_processed=number_of_students_processed+1
                if options.testing and number_of_students_processed > 10:
                    break

                students_name=e['user']['sortable_name']

                if Verbose_Flag:
                    print("{0}: {1}".format(students_name, course_section_id))

                course_code=section_to_course_code_mapping.get(course_section_id, False)
                if course_code:
                    # check for existing "grade" i.e., course code
                    grade_info=get_grade_for_assignment(course_id, assignment_id, students_userid)
                    existing_course_code=grade_info.get('grade', False)
                    if not existing_course_code:
                        print("{0}: course code is {1}".format(students_name, course_code))
                        assign_grade_for_assignment(course_id, assignment_id, students_userid, course_code, False)
                        continue

                    if existing_course_code != course_code:
                        # need to change the student's course code
                        assign_grade_for_assignment(course_id, assignment_id, students_userid, course_code, False)
                        print("{0}: changed course code from {1} to {2}".format(students_name, existing_course_code, course_code))
                        

if __name__ == "__main__": main()
