#!/usr/bin/python3
# -*- coding: utf-8 -*-
# -*- mode: python; python-indent-offset: 4 -*-
#
#!/usr/bin/python3
#
# ./insert-examiners-from-spreadsheet.py  course_id spreadsheetFile [column_name]
# 
# The preadhsheet is assumed to have the columns: "PROPOSAL TITLE", "LINK TO PROPOSAL IN KTH BOX", "EXAMINER", "SUPERVISOR", "Notes"
#
# Program inserts the name of the examiner as a grade based on mathicng the "PROPOSAL TITLE" with the "Tentative_tile" in the course gradebook
#
# with the option '-C'or '--containers' use HTTP rather than HTTPS for access to Canvas
# with the option "-v" or "--verbose" you get lots of output - showing in detail the operations of the program
#
# Can also be called with an alternative configuration file:
# ./insert-examiners-from-spreadsheet.py   --config config-test.json 25434   "/z3/maguire/Exjobs-2020/Master's thesis proposals P3 2021-20210220.xlsx"
# ./insert-examiners-from-spreadsheet.py -v 25434   "/z3/maguire/Exjobs-2020/Master's thesis proposals P3 2021-20210220.xlsx"
#
# G. Q. Maguire Jr.
#
# based upon insert-programs-from-spreadsheet.py and add_students_to_examiners_section_in_course.py
#
# 2021.02.20
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
    projects_df = pd.read_excel(open(spreadsheetFile, 'rb'))

    if (len(remainder) >= 3):
        column_name=remainder[2]
    else:
        column_name='EXAMINER'

    # check for column in spreadsheet data
    spreadsheetColumns=projects_df.columns.values.tolist()

    if column_name in spreadsheetColumns:
        print("spreadsheetColumns={}".format(spreadsheetColumns))
    else:
        print("spreadsheet is missing a column with the name: {}".format(column_name))
        return

    custon_columns_in_course=list_custom_columns(course_id)
    if Verbose_Flag:
        print("custon_columns_in_course={}".format(custon_columns_in_course))

    # check for 'Tentative_tile'
    target_column_name='Tentative_title'
    target_column_id=lookup_column_id(custon_columns_in_course, target_column_name)
    if target_column_id:
        print("target_column_name={0} id={1}".format(target_column_name, target_column_id))
    else:
        print("Canvas course is missing a column with the name: {}".format(target_column))
        return

    existing_title_data=list_custom_column_entries(course_id, target_column_id)
    # data is a list with entries of the form: {'content': 'title', 'user_id': xxxx}
    if Verbose_Flag:
        print("existing_title_data={}".format(existing_title_data))

    list_of_assignments=list_assignments(course_id)
    if Verbose_Flag:
        print("list_of_assignments={}".format(list_of_assignments))

    # check for 'Examiner' assignment
    target_assignment_name='Examiner'
    assignment_id=assignment_id_from_assignment_name(list_of_assignments, target_assignment_name)
    if assignment_id:
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

    #if Verbose_Flag:
    print("canvas_grading_standards={}".format(canvas_grading_standards))

    course_info=get_course_info(course_id)
    course_code=course_info.get('course_code', False)
    if not course_code:
        print("No course code found: {}}".format(course_code))
        return
    if Verbose_Flag:
        print("course_code={}".format(course_code))

    examiner_grading_standard_id=canvas_grading_standards.get(course_code+'_Examiners', None)
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

    student_ids=set()
    for td in existing_title_data: # data is a list with entries of the form: {'content': 'title', 'user_id': xxxx}
        students_userid=td['user_id']
        student_ids.add(students_userid)

    print("number of students with tentative titles is {}".format(len(student_ids)))

    enrollments=users_in_course(course_id)

    # get students' names
    students_name=dict()
    for e in enrollments:
        if e['type'] == 'StudentEnrollment':
            students_name[e['user_id']]=e['user']['sortable_name']

    if Verbose_Flag:
        pp.pprint(students_name)


    number_of_rows=len(projects_df)
    print("number_of_rows in spreadsheet={}".format(number_of_rows))

    mapping_spreadsheet_to_sortname_examiner_names={
        'Aris Gionis':         'Gionis, Aristides',
        'Aristides Gionis':    'Gionis, Aristides',
        'Arvind Kumar':        'Kumar, Arvind',
        'Benoit Baudry':       'Baudry, Benoit',
        'Carlo Fischione':     'Fischione, Carlo',
        'Cyrille Artho':       'Artho, Cyrille',
        'Danica Kragic':       'Kragic Jensfelt, Danica',
        'Danica Kragic Jensfelt': 'Kragic Jensfelt, Danica',
        'Dejan Kostic':		'Kostic, Dejan Manojlo',
        'Elena Troubitsyna':	'Troubitsyna, Elena',
        'Erik Fransén':		'Fransén, Erik',
        'Gerald Maguire': 	'Maguire Jr, Gerald Quentin',
        'Gerald  Q.  Maguire': 	'Maguire Jr, Gerald Quentin',
        'György Dán':		'Dán, György',
        'joakim gustafson':	'Gustafsson, Joakim',
        'Joakim Gustafsson':	'Gustafsson, Joakim',
        'Johan Håstad':		'Håstad, Johan',
        'Jonas Beskow':		'Beskow, Jonas',
        'Kristina Höök':	'Höök, Kristina',
        'Mads Dam':		'Dam, Mads',
        'Magnus Boman':		'Boman, Magnus',
        'Marco Chiesa':		'Chiesa, Marco',
        'Mario Romero Vega':	'Romero Vega, Mario',
        'Mårten Björkman':	'Björkman, Mårten',
        'Martin Monperrus':	'Monperrus, Martin',
        'Mathias Ekstedt':	'Ekstedt, Mathias',
        'Olof Bälter':		'Bälter, Olof',
        'Olov Engwall':		'Engwall, Olov',
        'Panos Papadimitratos':	'Papadimitratos, Panagiotis',
        'Patric Jensfelt':	'Jensfelt, Patric',
        'Pawel Herman':		'Herman, Pawel',
        'Robert Lagerström':	'Lagerström, Robert',
        'Roberto Guanciale':	'Guanciale, Roberto',
        'Stefano Markidis':	'Markidis, Stefano',
        'Tino Weinkauf':	'Weinkauf, Tino',
        'Viggo Kann':		'Kann, Viggo',
        'Viktoria Fodor':	'Fodor, Viktoria'
        }


    for j in range(0,number_of_rows):
        if options.testing and (j > 2):
            break
        proposal_title_column='PROPOSAL TITLE'
        title=projects_df[proposal_title_column].values[j]
        if isinstance(title, str):
            if Verbose_Flag:
                print("title={}".format(title))

            students_userid=False
            for td in existing_title_data: # data is a list with entries of the form: {'content': 'title', 'user_id': xxxx}
                if td['content'] == title:
                    students_userid=td['user_id']
                    break
            
            if students_userid:
                s_name=students_name.get(students_userid, False)
                if not s_name:
                    print("Student with title matching '{0}' missing name for id: {1}".format(title, students_userid))
                    continue

                if Verbose_Flag:
                    print("Student with title matching '{0}' is named: {1}".format(title, s_name))

                examiner=projects_df[column_name].values[j]
                if isinstance(examiner, str):
                    examiner=examiner.strip()
                    if Verbose_Flag:
                        print("examiner={}".format(examiner))

                    # translate from spreadhseet examiner names to exaimners names in sort_name format
                    sorted_name=mapping_spreadsheet_to_sortname_examiner_names.get(examiner, False)
                    if not sorted_name:
                        print("Could not find sorted name for examiner={}".format(examiner))
                        continue

                    current_grade_info=get_grade_for_assignment(course_id, assignment_id, students_userid)
                    if current_grade_info:
                        existing_examiner=current_grade_info.get('grade', False)
                        print("{0}: existing_examiner={1}".format(s_name, existing_examiner))
                        if existing_examiner and (existing_examiner != sorted_name):
                            # need to change the student's examiner
                            assign_grade_for_assignment(course_id, assignment_id, students_userid, sorted_name, False)
                            print("{0}: changed examiner from {1} to {2}".format(s_name, existing_examiner, sorted_name))
                        else:
                            print("{0}: examiner is {1}".format(s_name, sorted_name))
                            assign_grade_for_assignment(course_id, assignment_id, students_userid, sorted_name, False)

                    else:
                        print("no current_grade_info {0}: examiner is {1}".format(s_name, sorted_name))
                        assign_grade_for_assignment(course_id, assignment_id, students_userid, sorted_name, False)

if __name__ == "__main__": main()

