#!/usr/bin/python3
# -*- coding: utf-8 -*-
# -*- mode: python; python-indent-offset: 4 -*-
#
# ./add_groups_to_gradebook_course.py course_id
#
# updates the gradebook with information about the groups in a course
#
# Example:
#
# ./list_groups_in_course.py 34871
#
# Uses a file with a name of the form: short_group_names-in-ddddd.json where ddddd is the course_id
# that contains a struct of the form:
# {"Chip Maguire's section": {"base_for_group_names": "Chip", "number_of_groups_to_make": 1, "shorted_group_name": "CM"},
#  "Dropped the course": {"base_for_group_names": null, "number_of_groups_to_make": 0, "shorted_group_name": null},
# ...
# }
#
# This information is used to provide the ability to name section names to base names for groups and shorted group names.
# The shortened group names are entered into a custom column in the gradebook. The name of this column is based on the
# group category, i.e., the name of the group set.
#
# G. Q. Maguire Jr.
#
# 2020-10-25 based on list_groups_in_course.py
#

import requests, time
from pprint import pprint
import optparse
import sys
import os.path

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

    if os.path.isfile(config_file):
        if Verbose_Flag:
            print(f"{config_file} exists")
    else:
        print(f"{config_file} does not exist")
        return

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

def section_name_from_section_id(sections_info, section_id): 
    for i in sections_info:
        if i['id'] == section_id:
            return i['name']

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

def students_in_course(course_id):
    user_found_thus_far=[]
    # Use the Canvas API to get the list of users enrolled in this course
    #GET /api/v1/courses/:course_id/enrollments

    url = "{0}/courses/{1}/enrollments".format(baseUrl,course_id)
    if Verbose_Flag:
        print("url: {}".format(url))

    extra_parameters={'per_page': '100', 'type[]': ['StudentEnrollment']}
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
            for p_response in page_response:  
                user_found_thus_far.append(p_response)
    return user_found_thus_far



def list_group_categories_in_course(course_id):
    group_categories_found_thus_far=[]

    # Use the Canvas API to get the list of groups for the course
    #List group categories for a contextGroupCategoriesController#index
    #GET /api/v1/courses/:course_id/group_categories

    url = "{0}/courses/{1}/group_categories".format(baseUrl, course_id)
    if Verbose_Flag:
        print("url: {}".format(url))

    r = requests.get(url, headers = header)
    if Verbose_Flag:
        print("result of getting groups: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        page_response=r.json()

        for p_response in page_response:  
            group_categories_found_thus_far.append(p_response)

        # the following is needed when the reponse has been paginated
        # i.e., when the response is split into pieces - each returning only some of the list of modules
        # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
        if 'link' in r.headers:
            while r.links.get('next', False):
                r = requests.get(r.links['next']['url'], headers=header)  
                page_response = r.json()  
                for p_response in page_response:  
                    group_categories_found_thus_far.append(p_response)

    return group_categories_found_thus_far

def list_groups_in_course(course_id):
    groups_found_thus_far=[]

    # Use the Canvas API to get the list of groups for the course
    # GET /api/v1/courses/:course_id/groups

    url = "{0}/courses/{1}/groups".format(baseUrl, course_id)
    if Verbose_Flag:
        print("url: {}".format(url))

    r = requests.get(url, headers = header)
    if Verbose_Flag:
        print("result of getting groups: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        page_response=r.json()

        for p_response in page_response:  
            groups_found_thus_far.append(p_response)

        # the following is needed when the reponse has been paginated
        # i.e., when the response is split into pieces - each returning only some of the list of modules
        # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
        if 'link' in r.headers:
            while r.links.get('next', False):
                r = requests.get(r.links['next']['url'], headers=header)  
                page_response = r.json()  
                for p_response in page_response:  
                    groups_found_thus_far.append(p_response)

    return groups_found_thus_far

def members_of_groups(group_id):
    members_found_thus_far=[]

    # Use the Canvas API to get the list of members of group
    # GET /api/v1/groups/:group_id/users

    url = "{0}/groups/{1}/users".format(baseUrl, group_id)
    if Verbose_Flag:
        print("url: {}".format(url))

    r = requests.get(url, headers = header)
    if Verbose_Flag:
        print("result of getting memebrs of group: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        page_response=r.json()

        for p_response in page_response:  
            members_found_thus_far.append(p_response)

        # the following is needed when the reponse has been paginated
        # i.e., when the response is split into pieces - each returning only some of the list of modules
        # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
        if 'link' in r.headers:
            while r.links.get('next', False):
                r = requests.get(r.links['next']['url'], headers=header)  
                page_response = r.json()  
                for p_response in page_response:  
                    members_found_thus_far.append(p_response)

    return members_found_thus_far

def relevant_section_ids(sections):
    section_ids=[]
    for i in sections:
        section_ids.append(i['id'])
    return section_ids

def same_group(s, possible_reviwer, course_groups):
    for g in course_groups:
        if (s in course_groups[g]['member_ids']) and (possible_reviwer in course_groups[g]['member_ids']):
            return True
    return False

def student_name_from_id(id, students_info):
    for s in students_info:
        if s['user']['id'] == id:
            return s['user']['name']
    return ''

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
    global Verbose_Flag
    entries_found_thus_far=[]

    # Use the Canvas API to get the list of custom column entries for a specific column for the course
    #PUT /api/v1/courses/:course_id/custom_gradebook_columns/:id/data/:user_id

    url = "{0}/courses/{1}/custom_gradebook_columns/{2}/data/{3}".format(baseUrl,course_id, column_number, user_id)
    if Verbose_Flag:
        print("url: {}".format(url))

    payload={'column_data[content]': data_to_store}
    r = requests.put(url, headers = header, data=payload)

    if Verbose_Flag:
        print("result of putting data into custom_gradebook_column:  {}".format(r.text))

    if r.status_code == requests.codes.ok:
        page_response=r.json()

        for p_response in page_response:  
            entries_found_thus_far.append(p_response)

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
    global Verbose_Flag
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
        if Verbose_Flag:
            print("inserted column")
        return True
    return False


def extract_acronym(s):
    # add first letter
    acronym = s[0]
    # iterate over input string
    for i in range(1, len(s)):
        if s[i-1] == ' ':
            # add letter after a space to the acronym
            acronym += s[i]
    #
    # uppercase acronym
    return  acronym.upper()

def trim_to_apostrophe(s):
    if "'" in s:
        offset=s.find("'")
        return s[:offset]
    else:
        return s
    
def shorten_section_name(s):
    return extract_acronym(trim_to_apostrophe(s))

def first_name_from_section_name(s):
    if ' ' in s:
        sname=s.split(' ')
        return sname[0]
    else:
        return s

def shorted_group_name_from_base(b, short_group_names):
    for sn in short_group_names:
        if short_group_names[sn].get('base_for_group_names') == b:
            ssn=short_group_names[sn].get('shorted_group_name')
            if ssn:
                return ssn
            else:
                return b
    # If there are no matches
    return None

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

    parser.add_option('-s', '--short',
                      dest="short",
                      default=False,
                      action="store_true",
                      help="use short names for groups"
                      )


    options, remainder = parser.parse_args()

    Verbose_Flag=options.verbose
    if Verbose_Flag:
        print('ARGV      :', sys.argv[1:])
        print('VERBOSE   :', options.verbose)
        print('REMAINING :', remainder)

    initialize(options)

    if (len(remainder) < 1):
        print("Insuffient arguments\n must provide course_id")

    if (len(remainder) > 0):
        course_id=remainder[0]

    sections=sections_in_course(course_id)
    if Verbose_Flag:
        print("sections={}".format(sections))

    students=students_in_course(course_id)
    if Verbose_Flag:
        print(f"{students=}")

    group_categories=list_group_categories_in_course(course_id)
    if Verbose_Flag:
        print(f"{group_categories=}")
    group_categories_names_by_id=dict()

    columns_to_add=[]
    for gc in group_categories:
        group_categories_names_by_id[gc['id']]=gc['name']
        columns_to_add.append(gc['name'])
    if Verbose_Flag:
        print(f"{columns_to_add=}")

    list_of_columns=list_custom_columns(course_id)
    for column_name in columns_to_add:
        if not options.testing:
            column_number=add_column_if_necessary(course_id, column_name, list_of_columns)
            if Verbose_Flag:
                print('added column_name: "{0}" at column number: {1}'.format(column_name, column_number))

    groups=list_groups_in_course(course_id)
    if Verbose_Flag:
        print(f'{groups=}')
    if Verbose_Flag:
        print("number of groups={}".format(len(groups)))

    short_group_names=dict()
    if options.short:
        short_names_file=f'short_group_names-in-{course_id}.json'
        if os.path.isfile(short_names_file):
            if Verbose_Flag:
                print(f"{short_names_file} exists")
            try:
                with open(short_names_file, encoding='utf8') as short_file:
                    short_group_names = json.load(short_file)
            except:
                print("Error when openning short names name file named {}".format(short_names_file))
                sys.exit()
        else:
            print(f"{short_names_file} does not exist, creating one")
            for s in sections:
                s_name=s['name']
                if ("'" in s_name) and ("section" in s_name):
                    short_group_names[s_name]={
                        'base_for_group_names': first_name_from_section_name(s_name),
                        'number_of_groups_to_make': 1,
                        'shorted_group_name': shorten_section_name(s_name)
                    }
                else:
                    short_group_names[s_name]={
                        'base_for_group_names': None,
                        'number_of_groups_to_make': 0,
                        'shorted_group_name': None
                    }
            try:
                with open(short_names_file, 'w', encoding='utf8') as short_file:
                    json.dump(short_group_names, short_file, ensure_ascii=False)
            except:
                print("Error when writing an initial short names name file named {}".format(short_names_file))
                sys.exit()

        print(f'{short_group_names=}')

    course_groups={}
    groups_per_student=dict()   # per student list of group names
 
    for g in groups:
        g_id=g['id']
        g_name=g['name']
        g_category=g['group_category_id']
        g_category_name=group_categories_names_by_id.get(g_category)
        if g['members_count'] > 0:
            members=members_of_groups(g_id)
            member_ids=[x['id'] for x in members]
            course_groups[g_id]={'name': g_name,
                                 'members_count': g['members_count'],
                                 'member_ids': member_ids,
                                 'members': members}
            for m_id in member_ids:
                cgroups=groups_per_student.get(m_id, None)
                if cgroups:
                    groups_per_student[m_id]=cgroups.append(g_name)
                else:
                    groups_per_student[m_id]=[g_name]
                if g_category_name:
                    column_number=lookup_column_number(g_category_name, list_of_columns)
                    if short_group_names:
                        # computer short name for group
                        sg_name=g_name.split(' group ')
                        short_group_name=shorted_group_name_from_base(sg_name[0], short_group_names)
                        if short_group_name:
                            new_short_group_name=f'{short_group_name}{sg_name[1]}'
                            put_custom_column_entries(course_id, column_number, m_id, new_short_group_name)
                        else:
                            put_custom_column_entries(course_id, column_number, m_id, g_name)
                    else:
                        put_custom_column_entries(course_id, column_number, m_id, g_name)

                    if Verbose_Flag:
                        print(f"Put {column_number} {m_id} {g_name} {members}")
    return

if __name__ == "__main__": main()
