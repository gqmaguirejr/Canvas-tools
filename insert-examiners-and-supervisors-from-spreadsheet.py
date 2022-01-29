#!/usr/bin/python3
# -*- coding: utf-8 -*-
# -*- mode: python; python-indent-offset: 4 -*-
#
#!/usr/bin/python3
#
# ./insert-examiners-and-supervisors-from-spreadsheet.py course_id spreadsheetFile
# 
# The preadhsheet is assumed to have the columns: "first", "last", "e-mail", "Proposal", "Keywords","Examiner", "Supervisor", "Comments"
#
# Program inserts the name of the examiner as a grade based on matching the "e-mail" and the student's in the course gradebook
# It also adds the students to the appropriate section for the examiner and supervisors.
# The names of multiple supervisors are assumed to be separated by either a comma or " and " in the spreadsheet.
# A list of the supervisors (in the same format they are in the spreadsheet) is stored in the gradebook in a custom column 'Supervisors'.
#
# with the option '-C'or '--containers' use HTTP rather than HTTPS for access to Canvas
# with the option "-v" or "--verbose" you get lots of output - showing in detail the operations of the program
#
# Can also be called with an alternative configuration file:
# ./insert-examiners-and-supervisors-from-spreadsheet.py --config config-test.json  33514   "Masters_thesis_proposals-CS-P3-2022.xlsx"
#
# Example:
# ./insert-examiners-and-supervisors-from-spreadsheet.py  33514   "Masters_thesis_proposals-CS-P3-2022.xlsx"
#
# Asditional options:
# --createaliasfile
#       creates a file of aliases in a JSON file name of the form: spreadsheet_aliases-<course_id>.json
#
# Otherwise the examiner and teacher aliases are read from a JSON file name of the form: spreadsheet_aliases-<course_id>.json
#
# The alias file has the format:
#{
#    "examiners": {
#        "Gerald Maguire": "Maguire Jr, Gerald Quentin",
#        "Gerald  Q.  Maguire": "Maguire Jr, Gerald Quentin",
#    },
#    "teachers": {
#        "spreadsheet version of a teacher's name": "Canvas sort order version of teacher's name"
#    }
#}
#
# The reason for the alias file is that the form and values for the names used in the spreadsheet
# do not always match an examiner's or teacher's name in Canvas.
#
# G. Q. Maguire Jr.
#
# based upon insert-programs-from-spreadsheet.py and add_students_to_examiners_section_in_course.py
#
# 2022.01.15
#

import csv, requests, time
import pprint
import optparse
import sys

from io import StringIO, BytesIO

from lxml import html

import json

# Use Python Pandas to work with XLSX files
import pandas as pd

# to use math.isnan(x) function
import math

# to convert strings to python lists
import ast

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

##############################################################################
## ONLY update the code below if you are experimenting with other API calls ##
##############################################################################

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

def students_in_course(course_id):
    global Verbose_Flag
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
        while r.links.get('next', False):
            r = requests.get(r.links['next']['url'], headers=header)
            page_response = r.json()  
            for p_response in page_response:  
                users_found_thus_far.append(p_response)

    return users_found_thus_far

def teachers_in_course(course_id):
    global Verbose_Flag
    users_found_thus_far=[]
    # Use the Canvas API to get the list of teachers enrolled in this course
    #GET /api/v1/courses/:course_id/enrollments

    url = "{0}/courses/{1}/enrollments".format(baseUrl,course_id)
    if Verbose_Flag:
        print("url: {}".format(url))

    extra_parameters={'per_page': '100',
                      'type': ['TeacherEnrollment']
                      }
    r = requests.get(url, params=extra_parameters, headers = header)
    if Verbose_Flag:
        print("result of getting teachers_in_course: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        page_response=r.json()

        for p_response in page_response:  
            users_found_thus_far.append(p_response)

        # the following is needed when the reponse has been paginated
        # i.e., when the response is split into pieces - each returning only some of the list of modules
        while r.links.get('next', False):
            r = requests.get(r.links['next']['url'], headers=header)
            page_response = r.json()  
            for p_response in page_response:  
                users_found_thus_far.append(p_response)

    return users_found_thus_far

def list_custom_columns(course_id):
    columns_found_thus_far=[]
    # Use the Canvas API to get the list of custom column for this course
    #GET /api/v1/courses/:course_id/custom_gradebook_columns

    url = "{0}/courses/{1}/custom_gradebook_columns".format(baseUrl,course_id)
    if Verbose_Flag:
        print("url: {}".format(url))

    r = requests.get(url, headers = header)
    if Verbose_Flag:
        print("result of getting custom_gradebook_columns: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        page_response=r.json()
        
        for p_response in page_response:  
            columns_found_thus_far.append(p_response)

        # the following is needed when the reponse has been paginated
        # i.e., when the response is split into pieces - each returning only some of the list of modules
        # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
        while r.links.get('next', False):
            r = requests.get(r.links['next']['url'], headers=header)  
            page_response = r.json()  
            for p_response in page_response:  
                columns_found_thus_far.append(p_response)

    return columns_found_thus_far

def lookup_column_id(list_of_exiting_columns, column_name):
    global Verbose_Flag

    for column in list_of_exiting_columns:
        if Verbose_Flag:
            print('column: ', column)
        if column['title'] == column_name: 
            return column['id']
    return False

def put_custom_column_entries(course_id, column_id, user_id, data_to_store):
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

# [   {'content': 'COPEN|CTFYS|CSDA', 'user_id': 1877},
#     {'content': 'CELTE|TSCRM', 'user_id': 9581},
#     {'content': 'TMAIM', 'user_id': 42912}]
def get_users_existing_program(existing_program_data, user_id):
    for e in existing_program_data:
        if e['user_id'] == user_id:
            return e['content']
    return False

def list_custom_column_entries(course_id, column_number):
    entries_found_thus_far=[]

    # Use the Canvas API to get the list of custom column entries for a specific column for the course
    #GET /api/v1/courses/:course_id/custom_gradebook_columns/:id/data

    url = "{0}/courses/{1}/custom_gradebook_columns/{2}/data".format(baseUrl,course_id, column_number)
    if Verbose_Flag:
        print("url: " + url)

    r = requests.get(url, headers = header)
    if Verbose_Flag:
        print("result of getting custom_gradebook_columns: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        page_response=r.json()

        for p_response in page_response:  
            entries_found_thus_far.append(p_response)

        # the following is needed when the reponse has been paginated
        # i.e., when the response is split into pieces - each returning only some of the list of modules
        # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
        while r.links.get('next', False):
            r = requests.get(r.links['next']['url'], headers=header)  
            page_response = r.json()  
            for p_response in page_response:  
                entries_found_thus_far.append(p_response)

    return entries_found_thus_far


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


def get_course_info(course_id):
    global Verbose_Flag
    # Use the Canvas API to get a grading standard
    #GET /api/v1/courses/:id
    url = "{0}/courses/{1}".format(baseUrl, course_id)

    if Verbose_Flag:
        print("url: " + url)

    r = requests.get(url, headers = header)
    if r.status_code == requests.codes.ok:
        page_response=r.json()
        return page_response
    return None

def get_grading_standards(id):
    global Verbose_Flag
    # Use the Canvas API to get a grading standard
    # GET /api/v1/courses/:course_id/grading_standards

    # Request Parameters:
    #Parameter		        Type	Description
    url = "{0}/courses/{1}/grading_standards".format(baseUrl, id)

    if Verbose_Flag:
        print("url: " + url)

    r = requests.get(url, headers = header)
    if r.status_code == requests.codes.ok:
        page_response=r.json()
        return page_response
    return None

def get_grading_standard_id_by_name(courss_id, all_course_grading_standards, grading_standard_name):
    for i in all_course_grading_standards:
        if i['id'] == grading_standard_id:
            return i
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

def student_from_students_by_id(canvas_user_id, students):
    for student in students:
        if student['user_id'] == canvas_user_id:
            return student
    return None

def clean_spreadsheetColumns_names(spreadsheetColumns):
    clean_spreadsheetColumns=list()
    for sc in spreadsheetColumns:
        clean_spreadsheetColumns.append(sc.strip())
    return clean_spreadsheetColumns


def check_for_columns_in_spreadsheet(expected_spreadsheet_columns, spreadsheetColumns):
    found_all_expected_columns=True
    for c in expected_spreadsheet_columns:
        if c not in spreadsheetColumns:
            found_all_expected_columns=False
            print("spreadsheet is missing a column with the name: {}".format(c))
    return found_all_expected_columns


def lookup_title_in_gradebook(students_userid, existing_title_data):
    for td in existing_title_data: # data is a list with entries of the form: {'content': 'title', 'user_id': xxxx}
        if students_userid == td['user_id']:
            return td['content']
    return None

def lookup_supervisors_in_gradebook(students_userid, existing_supervisors_data):
    for td in existing_supervisors_data: # data is a list with entries of the form: {'content': 'title', 'user_id': xxxx}
        if students_userid == td['user_id']:
            return td['content']
    return None

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


def create_sections_in_course(course_id, section_names):
    sections_found_thus_far=[]
    
    # Use the Canvas API to create sections for this course
    #POST /api/v1/courses/:course_id/sections

    url = "{0}/courses/{1}/sections".format(baseUrl,course_id)
    if Verbose_Flag:
        print("url: {}".format(url))

    for section_name in section_names:
        #course_section[name]
        payload={'course_section[name]': section_name}
        r = requests.post(url, headers = header, data=payload)

        if Verbose_Flag:
            print("result of creating section: {}".format(r.text))

        if r.status_code == requests.codes.ok:
            page_response=r.json()

            for p_response in page_response:  
                sections_found_thus_far.append(p_response)

    return sections_found_thus_far

def enroll_student_in_section(course_id, user_id, section_id):
    global Verbose_Flag
    # POST /api/v1/courses/:course_id/enrollments
    # enrollment[user_id] = user_id
    # enrollment[type] = StudentEnrollment
    # enrollment[course_section_id] = section_id

    url = "{0}/courses/{1}/enrollments".format(baseUrl,course_id)
    if Verbose_Flag:
        print("url: {}".format(url))

    payload={'enrollment[user_id]': user_id, 
             'enrollment[type]': 'StudentEnrollment',
             'enrollment[course_section_id]': section_id }
    r = requests.post(url, headers = header, data=payload)

    if Verbose_Flag:
        print("result of enrolling student in section: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        page_response=r.json()
        return page_response

    return None

def remove_student_from_section(course_id, user_id, section_id, students):
    global Verbose_Flag
    enrollment_id=None
    for s in students:
        if s['user_id'] == user_id and s['course_section_id'] == section_id:
            enrollment_id=s['id']
            # DELETE /api/v1/courses/:course_id/enrollments/:enrollment_id
            url = "{0}/courses/{1}/enrollments/{2}".format(baseUrl,course_id, enrollment_id)
            if Verbose_Flag:
                print("url: {}".format(url))
            payload={'task': 'delete' } #  delete this specific renollment
            r = requests.delete(url, headers = header, data=payload)

            if Verbose_Flag:
                print("result of deleting enrollment of student with enrollment_id {0}: {1}".format(enrollment_id, r.text))

            if r.status_code == requests.codes.ok:
                page_response=r.json()
                return page_response
            else:
                return None
    return None

# This dict maps the names in the order used in the spread sheet to sortable name order (for use in Canvas)
# This dict contains all of the examiners known to the program
global mapping_spreadsheet_to_sortname_examiner_names
global mapping_spreadsheet_to_sortname_supervisor_names

mapping_spreadsheet_to_sortname_examiner_names={
    'Gerald Maguire': 	'Maguire Jr, Gerald Quentin',
    'Gerald  Q.  Maguire': 	'Maguire Jr, Gerald Quentin',
    # Add new examiners to this mapping.
}

# This dict maps the names in the order used in the spread sheet to sortable name order (for use in Canvas)
# This dict contains all of the teachers (who are not examiners) who are known to the program
mapping_spreadsheet_to_sortname_supervisor_names={
    # Add new teachers to this mapping.
}


def main():
    global Verbose_Flag
    global mapping_spreadsheet_to_sortname_examiner_names
    global mapping_spreadsheet_to_sortname_supervisor_names


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

    parser.add_option('--createaliasfile',
                      dest="createaliasfile",
                      default=False,
                      action="store_true",
                      help="dump examiner and teacher alias to a JSON file"
                      )

    parser.add_option('-t', '--testing',
                      dest="testing",
                      default=False,
                      action="store_true",
                      help="execute test code"
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

    pp = pprint.PrettyPrinter(indent=4) # configure prettyprinter

    if (len(remainder) < 2):
        print("Inusffient arguments: must provide course_id spreadsheetFile")
        return

    course_id=remainder[0]
    spreadsheetFile=remainder[1]

    AliasFile_name="spreadsheet_aliases-{}.json".format(course_id)

    createdAliasFile_Flag=options.createaliasfile
    combined_aliases=None
    if createdAliasFile_Flag:
        combined_aliases={'examiners': mapping_spreadsheet_to_sortname_examiner_names,
                          'teachers': mapping_spreadsheet_to_sortname_supervisor_names
                          }
        try:
            with open(AliasFile_name, 'w') as json_data_file:
                json.dump(combined_aliases, json_data_file, ensure_ascii=False, indent=4)
                print("created alias file {}".format(AliasFile_name))
        except:
            print("Unable to write JSON file named {}".format(course_info_file))
        return


    try:
        with open(AliasFile_name) as json_data_file:
            combined_aliases = json.load(json_data_file)
    except:
        print("Unable to open alias file named {}".format(AliasFile_name))
        print("Please create a suitable alias file")
        sys.exit()

    #  use the alias data from the file
    if combined_aliases:
        mapping_spreadsheet_to_sortname_examiner_names=combined_aliases.get('examiners', dict())
        mapping_spreadsheet_to_sortname_supervisor_names=combined_aliases.get('teachers', dict())
    else:
        print("There was no data in the alias file")

    number_of_examiner_aliases=len(mapping_spreadsheet_to_sortname_examiner_names)
    number_of_teacher_aliases=len(mapping_spreadsheet_to_sortname_supervisor_names)
    if number_of_examiner_aliases == 0 or number_of_teacher_aliases == 0:
        print("Something is likely wrong with the alias file")
    else:
        if Verbose_Flag or True:
            print("Number of aliases examiners={0}, teachers={1}".format(number_of_examiner_aliases, number_of_teacher_aliases))

    projects_df = pd.read_excel(open(spreadsheetFile, 'rb'), sheet_name='Closed')

    # check for column in spreadsheet data
    spreadsheetColumns=projects_df.columns.values.tolist()

    # check that the spreadsheet has the expected columns
    expected_spreadsheet_columns=['e-mail', 'Examiner', 'Supervisor', 'Proposal']
    cleaned_spreadsheetColumns=clean_spreadsheetColumns_names(spreadsheetColumns)
    if not check_for_columns_in_spreadsheet(expected_spreadsheet_columns, cleaned_spreadsheetColumns):
        print("spreadsheet is missing column(s), please correct")
        return

    # The header of the Proposal column seems to have a trailing space
    spreadsheet_proposal_key='Proposal'
    if spreadsheet_proposal_key not in spreadsheetColumns:
        spreadsheet_proposal_key='Proposal '
        if spreadsheet_proposal_key not in spreadsheetColumns:
            spreadsheet_proposal_key=None

    custon_columns_in_course=list_custom_columns(course_id)
    # check for 'Tentative_title' - this corresponds to the spreadsheet column 'Proposal'
    target_column_name='Tenative_title'
    target_column_id=lookup_column_id(custon_columns_in_course, target_column_name)
    if target_column_id:
        if Verbose_Flag:
            print("target_column_name={0} id={1}".format(target_column_name, target_column_id))
    else:
        print("Canvas course is missing a column with the name: {}".format(target_column_name))
        return

    # check for 'Advisors' - this corresponds to the spreadsheet column 'Supervisor'
    target_supervisors_column_name='Supervisors'
    target_supervisors_column_id=lookup_column_id(custon_columns_in_course, target_supervisors_column_name)
    if target_supervisors_column_id:
        if Verbose_Flag:
            print("target_supervisors_column_name={0} id={1}".format(target_supervisors_column_name, target_supervisors_column_id))
    else:
        print("Canvas course is missing a column with the name: {}".format(target_supervisors_column_name))
        return

    if Verbose_Flag:
        print("custon_columns_in_course={}".format(custon_columns_in_course))

    existing_title_data=list_custom_column_entries(course_id, target_column_id)
    existing_supervisors_data=list_custom_column_entries(course_id, target_supervisors_column_id)

    list_of_assignments=list_assignments(course_id)
    if Verbose_Flag:
        print("list_of_assignments={}".format(list_of_assignments))

    # check for 'Examiner' assignment
    target_assignment_name='Examiner'
    assignment_id=assignment_id_from_assignment_name(list_of_assignments, target_assignment_name)
    if assignment_id:
        if Verbose_Flag:
            print("target_assignment_name={0} id={1}".format(target_assignment_name, assignment_id))
    else:
        print("Canvas course is missing an assignment with the name: {}".format(target_assignment_name))
        return

    canvas_grading_standards=dict()
    available_grading_standards=get_grading_standards(course_id)
    if available_grading_standards:
        for s in available_grading_standards:
            old_id=canvas_grading_standards.get(s['title'], None)
            if old_id and s['id'] < old_id: # use only the highest numbered instance of each scale
                continue
            else:
                canvas_grading_standards[s['title']]=s['id']
                if Verbose_Flag:
                    print("title={0} for id={1}".format(s['title'], s['id']))

    if Verbose_Flag:
        print("canvas_grading_standards={}".format(canvas_grading_standards))

    course_info=get_course_info(course_id)
    course_code=course_info.get('course_code', False)
    if not course_code:
        print("No course code found: {}}".format(course_code))
        return
    if Verbose_Flag:
        print("course_code={}".format(course_code))

    examiner_grading_standard_id=canvas_grading_standards.get(course_code+'_Examiners', None)
    if Verbose_Flag:
        print("examiner_grading_standard_id={}".format(examiner_grading_standard_id))

    for i in available_grading_standards:
        if i['id'] == examiner_grading_standard_id:
            examiner_grading_standard=i

    if Verbose_Flag:
        print("There exists a grading standard {0}, with the value={1}".format(examiner_grading_standard_id, examiner_grading_standard))
        examiner_grading_scheme= examiner_grading_standard['grading_scheme']

    if Verbose_Flag:
        pp.pprint(examiner_grading_scheme)

    if Verbose_Flag:
        for c in spreadsheetColumns:
            print("{0}: data type {1}".format(c, projects_df.dtypes[c]))

    students=students_in_course(course_id)
    #pp.pprint(students)


    # get students' e-mail
    students_email=dict()
    for s in students:
        students_id=s['user_id']
        login_id=s['user']['login_id']
        if Verbose_Flag:
            print("login_id={0}, students_id={1}".format(login_id, students_id))
        students_email[login_id]=students_id

    if Verbose_Flag:
        pp.pprint(students_email)

    teachers=teachers_in_course(course_id)

    # compute list of unique teacher sortable names
    teacher_names_sortable=list()
    for t in teachers:
        user_data=t.get('user', False)
        if user_data:
            sortable_name=user_data.get('sortable_name', False)
            if sortable_name:
                if sortable_name in teacher_names_sortable:
                    continue
                else:
                    teacher_names_sortable.append(sortable_name)
    
    if Verbose_Flag:
        print("teacher_names_sortable={0}".format(teacher_names_sortable))

    if len(teacher_names_sortable) == 0:
        print("No teachers in the course, so there is nothing to do")
        return

    teacher_names_sortable_sorted=sorted(teacher_names_sortable)
    if Verbose_Flag:
        print("teacher_names_sortable_sorted={0}".format(teacher_names_sortable_sorted))

    new_sections_needed=list()
    list_of_sections=sections_in_course(course_id)
    
    for t in teacher_names_sortable_sorted:
        section_id=section_id_from_section_name(list_of_sections, t)
        if not section_id:
            new_sections_needed.append(t)

    # if necessary create the missing sections
    if len(new_sections_needed) > 0:
        print("Creating new sections in the course for teachers without sections: {}".format(new_sections_needed))
        create_sections_in_course(course_id, new_sections_needed)

    teacher_to_section_mapping=dict()
    all_teacher_section_ids=set()
    list_of_sections=sections_in_course(course_id)

    for t in teacher_names_sortable_sorted:
        section_id=section_id_from_section_name(list_of_sections, t)
        if not section_id:
            print("Missing section for {0}".format(t))
        else:
            teacher_to_section_mapping[t]=section_id
            all_teacher_section_ids.add(section_id)

    if Verbose_Flag:
        print("teacher_to_section_mapping={}".format(teacher_to_section_mapping))
        print("all_teacher_section_ids={}".format(all_teacher_section_ids))

    number_of_rows=len(projects_df)
    print("number_of_rows in spreadsheet={}".format(number_of_rows))

    # combine the above two alias dicts into mapping_spreadsheet_to_sortname_supervisor_names
    mapping_spreadsheet_to_sortname_supervisor_names.update(mapping_spreadsheet_to_sortname_examiner_names)

    # collect the list of missing students, examiners, and supervisors
    missing_students=set()
    missing_examiners=set()
    missing_supervisors=set()
    missing_sections=set()

    # process each of the rows in the spreadsheet
    for j in range(0,number_of_rows):
        if options.testing and (j > 3):
            break
        if Verbose_Flag:
            row=projects_df.values[j]
            print("row={}".format(row))
        e_mail=projects_df['e-mail'].values[j]
        if isinstance(e_mail, str):
            if Verbose_Flag:
                print("e_mail={}".format(e_mail))
        else:
            continue

        if len(e_mail) > 0:     # Make sure the e-mail address is in lower case, this is the convention in Canvas
            e_mail=e_mail.lower()
        if len(e_mail) > 0 and e_mail.endswith('@kth.se'):
            existing_examiner=None
            students_userid=students_email.get(e_mail, None)
            if not students_userid:
                missing_students.add(e_mail)
                if Verbose_Flag:
                    print("Student with e-mail '{0}' is missing from the course".format(e_mail))
                continue
            student=student_from_students_by_id(students_userid, students)
            if student:
                s_name=student['user']['sortable_name']
                print("processing student {}".format(s_name))
            else:
                print("Could not figure out the sortable_name for {0}".format(students_userid))

            # deal with tentative_title and 'Proposal'
            if spreadsheet_proposal_key:
                data_to_store=projects_df[spreadsheet_proposal_key].values[j]
                if isinstance(data_to_store, str):
                    if Verbose_Flag:
                        print("data_to_store={}".format(data_to_store))
                    tentative_title=lookup_title_in_gradebook(students_userid, existing_title_data)
                    if not tentative_title:
                        if Verbose_Flag:
                            print("Storing tentative tilte for {0} {1} {2}".format(s_name, students_userid, data_to_store))
                        put_custom_column_entries(course_id, target_column_id, students_userid, data_to_store)
                else:
                    if Verbose_Flag:
                        print("no data_to_store")

            # deal with the examiner for this student
            examiner=projects_df['Examiner'].values[j]
            if isinstance(examiner, str):
                examiner=examiner.strip()
                if Verbose_Flag:
                    print("examiner={}".format(examiner))

                # translate from spreadsheet examiner names to exaimners names in sort_name format
                sorted_name=mapping_spreadsheet_to_sortname_examiner_names.get(examiner, False)
                if not sorted_name:
                    print("Could not find sorted name for examiner={}".format(examiner))
                    missing_examiners.add(examiner)
                    continue


                current_grade_info=get_grade_for_assignment(course_id, assignment_id, students_userid)
                if Verbose_Flag:
                    print("current_grade_info={}".format(current_grade_info))
                if current_grade_info:
                    existing_examiner=current_grade_info.get('grade', False)
                    if Verbose_Flag:
                        print("{0}: existing_examiner={1} while sorted_name={2}".format(s_name, existing_examiner, sorted_name))

                    if not existing_examiner:
                        status=assign_grade_for_assignment(course_id, assignment_id, students_userid, sorted_name, False)
                        print("no existing examiner for {0}: assigning examiner {1}".format(s_name, sorted_name))
                        existing_examiner=sorted_name
                    elif existing_examiner and (existing_examiner != sorted_name):
                        # need to change the student's examiner
                        assign_grade_for_assignment(course_id, assignment_id, students_userid, sorted_name, False)
                        print("{0}: changed examiner from {1} to {2}".format(s_name, existing_examiner, sorted_name))
                        # remove the student from the previous examiner's section
                        previous_examiners_section_id=teacher_to_section_mapping[existing_examiner]
                        if previous_examiners_section_id:
                            print("removing previous_examiners_section_id={1} from student={0}".format(s_name, previous_examiners_section_id))
                            remove_student_from_section(course_id, students_userid, previous_examiners_section_id, students)
                        existing_examiner=sorted_name

                    else:
                        if Verbose_Flag:
                            print("Nothing to do as the existing examiner is already as recorded")

                else:
                    print("no current_grade_info {0}: asssigning examiner {1}".format(s_name, sorted_name))
                    assign_grade_for_assignment(course_id, assignment_id, students_userid, sorted_name, False)
                    existing_examiner=sorted_name

                # make sure student is in the examiners's section
                teacher_section_id=teacher_to_section_mapping.get(existing_examiner, False)
                if Verbose_Flag:
                    print("teacher_section_id={}".format(teacher_section_id))

                existing_sections_for_user=users_sections_from_user_id(students, students_userid)
                if Verbose_Flag:
                    print("existing_sections_for_user={0}, teacher_section_id={1}".format(existing_sections_for_user, teacher_section_id))
                if existing_sections_for_user and (teacher_section_id in existing_sections_for_user):
                    if Verbose_Flag:
                        print("Nothing to do - the user is already in the teacher's section")
                else:
                    # add the student to this section
                    if existing_examiner:
                        print("Adding {0} to section for examiner {1}".format(s_name, existing_examiner))
                        enroll_student_in_section(course_id, students_userid, teacher_section_id)
                    else:
                        print("Do not know the examiner for {0}, the examiner's name in the spreadsheet is '{1}'".format(s_name, examiner))

            # Handles supervisors for this student
            # Note that the supervisors (if more than one) can be separate by 'and' or a comma
            supervisors=projects_df['Supervisor'].values[j]
            if isinstance(supervisors, str):
                supervisors=supervisors.strip()
                if Verbose_Flag:
                    print("supervisors={}".format(supervisors))

                if supervisors.find(' and ') >= 0:
                    supervisors_list=supervisors.split(' and ')
                elif supervisors.find(',') >= 0:
                    supervisors_list=supervisors.split(',')
                else:
                    supervisors_list=[supervisors]
                # clean up supervisors (remove preceeding and trailing white space and make a set of them
                new_supervisors=[] # in normal name order for supervisors
                for supervisor in supervisors_list:
                    new_supervisors.append(supervisor.strip())

                if Verbose_Flag:
                    print("new_supervisors={}".format(new_supervisors))

                es=lookup_supervisors_in_gradebook(students_userid, existing_supervisors_data)
                if es:
                    existing_supervisors=ast.literal_eval(es)
                else:
                    existing_supervisors=None

                if Verbose_Flag:
                    print("existing_supervisors={0} of len()={1} and type()={2}".format(existing_supervisors, len(existing_supervisors), type(existing_supervisors)))

                existing_supervisors_sorted_names=set()
                existing_supervisors_section_ids=set()
                map_section_id_to_supervisor=dict()
                if  isinstance(existing_supervisors, list) and existing_supervisors:
                    for supervisor in existing_supervisors:
                        if Verbose_Flag:
                            print("processing supervisor: {0} for {1}".format(supervisor, s_name))
                        # translate from spreadsheet supervisor name to a supervsior's name in sort_name format
                        sorted_name=mapping_spreadsheet_to_sortname_supervisor_names.get(supervisor, False)
                        if not sorted_name:
                            if Verbose_Flag:
                                print("Could not find sorted name for supervisor={}".format(supervisor))
                            missing_supervisors.add(supervisor)
                            continue
                        existing_supervisors_sorted_names.add(sorted_name)

                        teacher_section_id=teacher_to_section_mapping.get(sorted_name, False)
                        if Verbose_Flag:
                            print("teacher_section_id={}".format(teacher_section_id))
                        if not teacher_section_id:
                            if Verbose_Flag:
                                print("Could not find section ID for supervisor={}".format(sorted_name))
                        else:
                            existing_supervisors_section_ids.add(teacher_section_id)
                            map_section_id_to_supervisor[teacher_section_id]=sorted_name
                    else:
                        if Verbose_Flag:
                            print("Error - there seems to be something ('{}') in the supervisor column, but I don't know what to do".format(existing_supervisors))

                new_supervisors_sorted_names=set()
                new_supervisors_section_ids=set()
                if new_supervisors:
                    for supervisor in new_supervisors:
                        # translate from spreadsheet supervisor name to a supervsior's name in sort_name format
                        sorted_name=mapping_spreadsheet_to_sortname_supervisor_names.get(supervisor, False)
                        if not sorted_name:
                            if Verbose_Flag:
                                print("Could not find sorted name for supervisor={}".format(supervisor))
                            missing_supervisors.add(supervisor)
                            continue
                        new_supervisors_sorted_names.add(sorted_name)

                        teacher_section_id=teacher_to_section_mapping.get(sorted_name, False)
                        if Verbose_Flag:
                            print("teacher_section_id={}".format(teacher_section_id))
                        if not teacher_section_id:
                            missing_sections.add(sorted_name)
                            if Verbose_Flag:
                                print("Could not find section ID for supervisor={}".format(sorted_name))
                        else:
                            new_supervisors_section_ids.add(teacher_section_id)
                            map_section_id_to_supervisor[teacher_section_id]=sorted_name

                if Verbose_Flag:
                    print("map_section_id_to_supervisor={}".format(map_section_id_to_supervisor))
                existing_sections_for_user=users_sections_from_user_id(students, students_userid)
                if Verbose_Flag:
                    print("existing_sections_for_user={}".format(existing_sections_for_user))
                # if there is no existing supervisor data or the contents have changed, then update with supervisor names in normal order
                if not existing_supervisors or (existing_supervisors_sorted_names != new_supervisors_sorted_names):
                    if Verbose_Flag:
                        print("Storing supervisor(s) for {0} {1} {2}".format(s_name, students_userid, new_supervisors))
                    new_supervisors_text="{}".format(new_supervisors)
                    put_custom_column_entries(course_id, target_supervisors_column_id, students_userid, new_supervisors_text)

                if existing_supervisors_section_ids:
                    # remove those section IDs that were in the existing set that are not in the new set
                    to_remove=existing_supervisors_section_ids-new_supervisors_section_ids
                    if Verbose_Flag:
                        print("to_remove={}".format(to_remove))
                    for sid in to_remove:
                        if sid in existing_sections_for_user:
                            print("removing {0} from section for supervisor {1}".format(s_name, map_section_id_to_supervisor[sid]))
                            remove_student_from_section(course_id, students_userid, sid, students)
                           
                # add the new section IDs that are not in the user's current set of sections
                if Verbose_Flag:
                    print("Adding {0} to supervisor(s) sections".format(s_name))
                    print("new_supervisors_section_ids={}".format(new_supervisors_section_ids))
                for sid in new_supervisors_section_ids:
                    if sid not in existing_sections_for_user:
                        print("adding {0} to the section for supervisor {1}".format(s_name, map_section_id_to_supervisor[sid]))
                        enroll_student_in_section(course_id, students_userid, sid)

    # list the e-mail address of missing stduents
    if missing_students:
        print("missing_students are students who have an e-mail address in the spreadsheet, but are not in the Canvas course")
        print("missing_students={}".format(missing_students))

    # list the names of missing examiners or supervisors in normal name order
    if missing_supervisors or missing_examiners:
        print("You need to add the missing supervisors or examiners to the mapping table for this program")
    if missing_examiners:
        print("missing_examiners={}".format(missing_examiners))
    if missing_supervisors:
        print("missing_supervisors={}".format(missing_supervisors))

    # the names in the missing sections are in sortable name order
    if missing_sections:
        print("missing_sections={}".format(missing_sections))
    
    missing_teachers=set()
    if missing_sections:
        for ss in missing_sections:
            if ss not in teacher_names_sortable_sorted:
                missing_teachers.add(ss)
    if missing_teachers:
        print("Add the following teachers to the course: {}".format(missing_teachers))
        
if __name__ == "__main__": main()

