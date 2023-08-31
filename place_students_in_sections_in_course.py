#!/usr/bin/python3
# -*- coding: utf-8 -*-
# -*- mode: python; python-indent-offset: 4 -*-
#
# ./place_students_in_sections_in_course.py course_id spreadshseet_name name_of_column_with_section_assignments
#
# inputs a spreadsheet of the section in a course as an xlsx file of the form: new_sections-in-189.xlsx
# then processes the column name_of_column_with_section_assignments on the second sheet "Students" (with the list of students):
#  1. collects the list of section names
#  2. if any section name does not yet exist for this course, create it
#  3. assign the student to the indicated section
#
# Note that the section names have to be strings
#
# Extensive use is made of Python Pandas merge operations.
# 
# G. Q. Maguire Jr.
#
# 2017.07.01
#

import csv, requests, time
from pprint import pprint
import optparse
import sys

from io import StringIO, BytesIO

import json

# Use Python Pandas to create XLSX files
import pandas as pd

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

##############################################################################
## ONLY update the code below if you are experimenting with other API calls ##
##############################################################################

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

        if r.status_code == requests.codes.ok:
            page_response=r.json()

            for p_response in page_response:  
                sections_found_thus_far.append(p_response)

    return sections_found_thus_far

def students_in_course(course_id):
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
        # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
        #while r.links['current']['url'] != r.links['last']['url']:  
        while r.links.get('next', False):
            r = requests.get(r.links['next']['url'], headers=header)  
            page_response = r.json()  
            for p_response in page_response:  
                users_found_thus_far.append(p_response)

    return users_found_thus_far

def enroll_student_in_section(course_id, user_id, section_id):
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

    if r.status_code == requests.codes.ok:
        page_response=r.json()
        return page_response

    return None


def main():
    global Verbose_Flag

    parser = optparse.OptionParser(usage="usage: %prog [options] filename")

    parser.add_option('-v', '--verbose',
                      dest="verbose",
                      default=False,
                      action="store_true",
                      help="Print lots of output to stdout"
                  )

    parser.add_option('-t', '--testing',
                      dest="testing",
                      default=False,
                      action="store_true",
                      help="In testing mode do not actually add the students to the target section"
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

    if options.config_filename:
        print("Configuration file : {}".format(options.config_filename))

    initialize(options)

    if (len(remainder) < 2):
        print("Insuffient arguments\n must provide course_id spreadshseet_name name_of_column_with_section_assignments\n")
        return

    course_id=remainder[0]
    spreadshseet_name=remainder[1]
    if (len(remainder) > 2):
        name_of_column_with_section_assignments=remainder[2]
    else:
        name_of_column_with_section_assignments='section_name'
    print("name_of_column_with_section_assignments={}".format(name_of_column_with_section_assignments))

    if Verbose_Flag:
        print("course_id={0}, spreadsheet={1}, column name={2}".format(course_id, spreadshseet_name, name_of_column_with_section_assignments))

    names_of_existing_sections=set()
    existing_sections_in_course=sections_in_course(course_id)
    for i in existing_sections_in_course:
        names_of_existing_sections.add(i['name'])

    if Verbose_Flag:
        print("names_of_existing_sections={}".format(names_of_existing_sections))

    # get list of which sections students are already in, index by user_id
    current_sections=dict()
    students=students_in_course(course_id)
    if Verbose_Flag:
        print("students={0}".format(students))

    if students:
        students_df1=pd.json_normalize(students)
        for  index, row in students_df1.iterrows():
            current_section_id=row['course_section_id']
            user_id=row['user.id']
            current_sections[user_id]=current_section_id

    if Verbose_Flag:
        print("current sections={0}".format(current_sections))

    spread_sheet = pd.ExcelFile(spreadshseet_name)
    sheet_names=spread_sheet.sheet_names
    if Verbose_Flag:
        print("sheet_names={0}".format(sheet_names))

    if 'Students' in sheet_names:
        print("Found sheet named {}".format('Students'))
        student_sheet_name='Students'
    else:
        print("Missing sheet named {}".format('Students'))
        return None
        
    # read the contents of the named sheet into a Panda data frame
    students_df = spread_sheet.parse(student_sheet_name)
    if Verbose_Flag:
        print("student_sheet_name columns={0}".format(students_df.columns.values))


    columns_on_sheet=students_df.columns
    if name_of_column_with_section_assignments in columns_on_sheet:
        if Verbose_Flag:
            print("desired column ({0}) exists".format(name_of_column_with_section_assignments))
        shape=students_df.shape
        if Verbose_Flag:
            print("number of columns is {}".format(shape[1]))
            print("number of rows is {}".format(shape[0]))
    else:
        print("desired column ({0}) does not exist".format(name_of_column_with_section_assignments))
        return None

    # put the student's current section as a value for the student's user ID in the course
    # in the following dict()
    new_sections=dict()

    collected_section_names=set()
    for  index, row in students_df.iterrows():
        section_name=row[name_of_column_with_section_assignments]
        new_section_name=row['section_name']
        # skip section names that represent the basic enrollment
        if "(" in new_section_name and new_section_name.endswith(")"):
            continue

        user_id=row['user.id']
        new_sections[user_id]=new_section_name
        if type(section_name) is str:
            collected_section_names.add(section_name)

    print("collected_section_names: {}".format(collected_section_names))
    print("new_sections: {}".format(new_sections))

    Verbose_Flag=True

    missing_section_names=[]
    for i in collected_section_names:
        if i not in names_of_existing_sections:
            if Verbose_Flag:
                print("missing section: {}".format(i))
            missing_section_names.append(i)

    print("missing sections: {}".format(missing_section_names))

    if len(missing_section_names) > 0:
        create_sections_in_course(course_id, missing_section_names)

    # get the full list of all sections in this course
    # each section has an id and name
    all_sections_in_course=sections_in_course(course_id)

    sections_by_name=dict()
    for s in all_sections_in_course:
        sections_by_name[s['name']]=s['id']


    for  index, row in students_df.iterrows():
        section_name=row[name_of_column_with_section_assignments]
        if type(section_name) is str:
            # the section names inserted for basic membership in the course have the form of: course code (dddd)
            if "(" in section_name and section_name.endswith(")"):
                continue
            # ckeck if student is already in the section
            if sections_by_name[section_name] == current_sections[row['user.id']]:
                if Verbose_Flag:
                    print("user: {0} already in section: {1}".format(row['user.name'], section_name))
                continue
            if Verbose_Flag:
                print("putting user: {0} into section: {1}".format(row['user.name'], section_name))
            if not options.testing:
                enroll_student_in_section(course_id, row['user.id'], sections_by_name[section_name])
    

if __name__ == "__main__": main()
