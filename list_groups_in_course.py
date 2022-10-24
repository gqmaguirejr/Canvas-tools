#!/usr/bin/python3
# -*- coding: utf-8 -*-
# -*- mode: python; python-indent-offset: 4 -*-
#
# ./list_groups_in_course.py course_id
#
# output spreadsheet of groups in a course
#
# Example:
#
# ./list_groups_in_course.py 34871
#
# G. Q. Maguire Jr.
#
# 2020-10-24 based on earlier assign-random-peer-reviewer-by-section.py
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

    groups=list_groups_in_course(course_id)
    print("number of groups={}".format(len(groups)))
    if Verbose_Flag:
        print(f'{groups=}')

    course_groups={}
    groups_per_student=dict()   # per student list of group names
 
    for g in groups:
        g_id=g['id']
        g_name=g['name']
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

    if Verbose_Flag:
        print("course_groups={}".format(course_groups))
        print(f'{groups_per_student=}')

    if (students):
        students_df=pd.json_normalize(students)
        
        for index, row in  students_df.iterrows():
            userid=row['user_id']
            glist=groups_per_student.get(userid, None)
            if glist:
                for i in range(0, len(glist)):
                    gindex=f'group{i}'
                    students_df.at[index, gindex]=glist[i]
            csid=row['course_section_id']
            students_df.at[index, 'Section_name']=section_name_from_section_id(sections, csid)

        # below are examples of some columns that might be dropped
        columns_to_drop=[
            'associated_user_id',
            'course_integration_id',
            'created_at',
	    'end_at',
	    'enrollment_state',
	    'grades.current_grade',
	    'grades.current_score',
	    'grades.final_grade',
	    'grades.final_score',
	    'grades.html_url',
	    'grades.unposted_current_grade',
	    'grades.unposted_current_score',
	    'grades.unposted_final_grade',
	    'grades.unposted_final_score',
            'html_url',
	    'id',
            'last_activity_at',
            'last_attended_at',
	    'limit_privileges_to_course_section',
            'role',
	    'role_id',
            'root_account_id',
            'section_integration_id',
            'sis_account_id',
	    'sis_section_id',
	    'start_at',
	    'total_activity_time',
	    'type',
            'updated_at',
            'user.created_at',
	    'user.id',
            'user.integration_id',
            'sis_course_id'
        ]
        # keep the following:
        # 'sis_user_id',
	# 'user.login_id',
	# 'user.name',
	# 'user.short_name'
	# 'user.sis_user_id'
	# 'user.sortable_name,'
	# 'user_id'
        
        students_df.drop(columns_to_drop,inplace=True,axis=1)
        students_df.drop_duplicates(subset=None, keep='first', inplace=True)

        students_df.sort_values(['Section_name', 'user.sortable_name'],
               axis = 0, ascending = True,
               inplace = True,
               na_position = "first")

        # shift the position of the 'Section_name' column
        students_df.insert(2, 'Section_name', students_df.pop('Section_name'))
    # the following was inspired by the section "Using XlsxWriter with Pandas" on http://xlsxwriter.readthedocs.io/working_with_pandas.html
    # set up the output write
    writer = pd.ExcelWriter(f'groups-in-{course_id}.xlsx', engine='xlsxwriter')
    students_df.to_excel(writer, sheet_name="Students")
        
    # Close the Pandas Excel writer and output the Excel file.
    writer.close()

    return

if __name__ == "__main__": main()
