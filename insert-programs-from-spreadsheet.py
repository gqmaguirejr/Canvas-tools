#!/usr/bin/python3
# -*- coding: utf-8 -*-
# -*- mode: python; python-indent-offset: 4 -*-
#
#!/usr/bin/python3
#
# ./insert-programs-from-spreadsheet.py  course_id
# 
# Inserts a custom column with the student's program information using the data from several columns of a spreadsheet
# it combines the data from the columns: program_code, program_code_1, and program_code_2
#
# It will create the column as necessary
#
# The spreadsheet is expected to be generate from canvas_ladok3_spreadsheet.py
#
# with the option '-C'or '--containers' use HTTP rather than HTTPS for access to Canvas
# with the option "-v" or "--verbose" you get lots of output - showing in detail the operations of the program
#
# Can also be called with an alternative configuration file:
# ./insert-programs-from-spreadsheet.py  --config config-test.json 25434
#
# G. Q. Maguire Jr.
#
# based upon insert-custom-columns-from-spreadsheet.py
#
# 2021.02.14
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

def lookup_column_number(column_name, list_of_exiting_columns):
    for column in list_of_exiting_columns:
        if Verbose_Flag:
            print('column: ', column)
        if column['title'] == column_name: 
            return column['id']
    return -1
       

def add_column_if_necessary(course_id, new_column_name, list_of_exiting_columns):
    column_number=lookup_column_number(new_column_name, list_of_exiting_columns)
    if column_number > 0:
        return column_number
    # otherwise insert the new column
    insert_column_name(course_id, new_column_name)
    return lookup_column_number(new_column_name, list_custom_columns(course_id))


def put_custom_column_entries(course_id, column_number, user_id, data_to_store):
    entries_found_thus_far=[]

    # Use the Canvas API to get the list of custom column entries for a specific column for the course
    #PUT /api/v1/courses/:course_id/custom_gradebook_columns/:id/data/:user_id

    url = "{0}/courses/{1}/custom_gradebook_columns/{2}/data/{3}".format(baseUrl,course_id, column_number, user_id)
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
    else:
        print("put_custom_column_entries({0}, {1}, {2}, {3}) produced status_code={4}".format(course_id, column_number, user_id, data_to_store,r.status_code))

    return entries_found_thus_far

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
    payload={'column[title]': column_name}
    r = requests.post(url, headers = header, data=payload)
    if r.status_code == requests.codes.ok:
        if Verbose_Flag:
            print("result of post creating custom column:  {}".format(r.text))
            page_response=r.json()
            print("inserted column")
            return True
    return False

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



# [   {'content': 'COPEN|CTFYS|CSDA', 'user_id': 1877},
#     {'content': 'CELTE|TSCRM', 'user_id': 9581},
#     {'content': 'TMAIM', 'user_id': 42912}]
def get_users_existing_program(existing_program_data, user_id):
    for e in existing_program_data:
        if e['user_id'] == user_id:
            return e['content']
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

    if (len(remainder) < 1):
        print("Inusffient arguments: must provide course_id")
        return

    course_id=remainder[0]
    list_of_columns=list_custom_columns(course_id)

    # example of a fillename: users_programs-25434
    input_file_name="users_programs-{0}.xlsx".format(course_id)
    students_df = pd.read_excel(open(input_file_name, 'rb'), sheet_name='users_programs')

    column_name='Program'
    column_number=add_column_if_necessary(course_id, column_name, list_of_columns)
    if Verbose_Flag:
        print('column number: ', column_number)

    if Verbose_Flag:
        list_of_columns=list_custom_columns(course_id)
        print(list_of_columns)

    existing_program_data=list_custom_column_entries(course_id, column_number)
    if Verbose_Flag:
        pp.pprint(existing_program_data)

    enrollments=users_in_course(course_id)
    student_ids=set()
    for e in enrollments:
        students_userid=e['user_id']
        student_ids.add(students_userid)

    columns_from_spreadsheet=['program_code', 'program_code_1', 'program_code_2']

    if Verbose_Flag:
        for c in columns_from_spreadsheet:
            print("{0}: data type {1}".format(c, students_df.dtypes[c]))

    number_of_rows=students_df.canvas_user_id.size
    if Verbose_Flag:
        print("number_of_rows={}".format(number_of_rows))

    if students_df.dtypes[columns_from_spreadsheet[0]] == 'object': # if data values are strings these look like "objects"
        for j in range(0,number_of_rows):
            if options.testing and (j > 2):
                break
            user_id=students_df.canvas_user_id.values[j]
            user_name=students_df.user.values[j]

            # check that the student is enrolled in the course, since the Ladok data can
            # include students who have not yet been added to the Canvas course
            if not user_id in student_ids:
                print("{0} is not enrolled in the course".format(user_name))
                continue

            data_to_store=False
            
            prog0=students_df[columns_from_spreadsheet[0]].values[j]
            if isinstance(prog0, str):
                data_to_store="{0}".format(prog0)

            prog1=students_df[columns_from_spreadsheet[1]].values[j]
            if isinstance(prog1, str) and len(prog1) > 0:
                data_to_store="{0}|{1}".format(prog0, prog1)

            prog2=students_df[columns_from_spreadsheet[2]].values[j]
            if isinstance(prog2, str) and len(prog2) > 0:
                data_to_store="{0}|{1}|{2}".format(prog0, prog1, prog2)

            existing_program=get_users_existing_program(existing_program_data, user_id)
            if data_to_store:
                if not existing_program:
                    status=put_custom_column_entries(course_id, column_number, user_id, data_to_store)
                    if status:
                        print("{0}: {1}".format(user_name, data_to_store))
                    else:
                        print("failed to enter user {0}: {1}".format(user_name, data_to_store))
                else:
                    if data_to_store != existing_program:
                        print("{0}: {1} updated prevous value of {2}".format(user_name, data_to_store, existing_program))
                        status=put_custom_column_entries(course_id, column_number, user_id, data_to_store)
                        if status:
                            print("{0}: {1}".format(user_name, data_to_store))
                        else:
                            print("failed to enter user {0}: {1}".format(user_name, data_to_store))

    else:
        print('unknown data type in column: ', column_name)

if __name__ == "__main__": main()

