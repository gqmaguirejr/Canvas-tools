#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# ./students-in-my-courses-with-join.py
#
# Output: XLSX spreadsheet with students and the course(s) they are in, one sheet per course
#
#
# with the option "-v" or "--verbose" you get lots of output - showing in detail the operations of the program
#
# Can also be called with an alternative configuration file:
# ./list_your_courses.py --config config-test.json
#
# Example:
# ./students-in-my-courses.py
#
# ./students-in-my-courses.py --config config-test.json
#
# 
# G. Q. Maguire Jr.
#
# based on earlier list-assignments.py
#
# 2019.08.15
#

import requests, time
import pprint
import optparse
import sys
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


def list_my_courses():
    courses_found_thus_far=[]
    # Use the Canvas API to get the list of courses for the user making the query
    #GET /api/v1/courses

    url = "{0}/courses".format(baseUrl)
    if Verbose_Flag:
        print("url: {}".format(url))

    r = requests.get(url, headers = header)
    if Verbose_Flag:
        print("result of getting courses: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        page_response=r.json()

        for p_response in page_response:  
            courses_found_thus_far.append(p_response)

        # the following is needed when the reponse has been paginated
        # i.e., when the response is split into pieces - each returning only some of the list of courses
        # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
        while r.links['current']['url'] != r.links['last']['url']:  
            r = requests.get(r.links['next']['url'], headers=header)  
            if Verbose_Flag:
                print("result of getting courses for a paginated response: {}".format(r.text))
            page_response = r.json()  
            for p_response in page_response:  
                courses_found_thus_far.append(p_response)

    return courses_found_thus_far

def users_in_course(course_id):
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
            while r.links['current']['url'] != r.links['last']['url']:  
                r = requests.get(r.links['next']['url'], headers=header)  
                page_response = r.json()  
                for p_response in page_response:  
                    users_found_thus_far.append(p_response)

    return users_found_thus_far


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

    options, remainder = parser.parse_args()

    Verbose_Flag=options.verbose
    if Verbose_Flag:
        print('ARGV      :', sys.argv[1:])
        print('VERBOSE   :', options.verbose)
        print('REMAINING :', remainder)
        
    if options.config_filename:
        print("Configuration file : {}".format(options.config_filename))

    initialize(options)

    my_courses=list_my_courses()
    print("len(my_courses) are {0}".format(len(my_courses)))

    # set up the output write
    writer = pd.ExcelWriter('users_in_my_courses.xlsx', engine='xlsxwriter')

    list_of_dfs=[]
    course_name_given_number={}
    for c in ['sis_user_id', 'user.login_id', 'user.name', 'user.short_name', 'user.sis_user_id', 'user.sortable_name', 'user_id']:
        course_name_given_number[c]=['none']


    for course in my_courses:
        if course['name'].find('do not use') >= 0:
            print("course id={0}  name={1} -- skipping".format(course['id'], course['name']))
            continue

        # if not (course['id'] in [16039, 17234]): # for testing only look at these courses
        #     continue
        if (course['id'] in [85, # Canvas at KTH
                             4996, # Canvas at KTH 2.0 - New structure
                             5733, # Grunder, resultathantering och attestering för kursledare och examinatorer. (sv/en)
                             8356, # GDPR@KTH
                             17839, # Miljöutbildning
                             18339  # Vårt uppdrag
        ]): # skip the courses over all KTH faculty and staff
            continue
        
        # if not (course['id'] in [189, 190]): # for testing only look at these courses
        #     continue

        print("course id={0}  name={1}".format(course['id'], course['name']))


        users=users_in_course(course['id'])
        if Verbose_Flag:
            print("users are: {0}".format(users))
        if (users):
            users_df=pd.json_normalize(users)
                     
            # below are examples of some columns that might be dropped
            columns_to_drop=[
                'associated_user_id',
                'course_integration_id',
                'course_section_id',
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
                'sis_course_id',
	        'sis_section_id',
	        'start_at',
	        'total_activity_time',
	        'type',
                'updated_at',
                'user.created_at',
	        'user.id',
                'user.integration_id'
            ]
            # keep the following:
            # 'sis_user_id',
	    # 'user.login_id',
	    # 'user.name',
	    # 'user.short_name'
	    # 'user.sis_user_id'
	    # 'user.sortable_name,'
	    # 'user_id'
            
            users_df.drop(columns_to_drop,inplace=True,axis=1)

            # the following was inspired by the section "Using XlsxWriter with Pandas" on http://xlsxwriter.readthedocs.io/working_with_pandas.html
            course_sheet_name="{0}".format(course['name'])
            if (len(course_sheet_name) > 30):
                course_sheet_name=course_sheet_name[0:29]
            course_sheet_name=course_sheet_name.replace(':', '-')
            users_df.to_excel(writer, sheet_name=course_sheet_name)

            new_column_name="{0}".format(course['id'])
            course_name_given_number[new_column_name]=[course['name']]
            users_df.rename(columns={'course_id':new_column_name}, inplace=True)


            list_of_dfs.append(users_df.drop_duplicates().reset_index(drop=True))

    # experiment with join
    #jusers_df=pd.merge(users_df_189, users_df_190, how='outer', on=['user_id'])

    line = pd.DataFrame(course_name_given_number, index=[0]) # insert a row below the column headings
    list_of_dfs.insert(0, line)
    jusers_df=pd.concat(list_of_dfs, sort=True).reset_index(drop = True) 

    # put the columns you want on the left in the order you want below
    inserted_cols = ['user.sortable_name', 'user.login_id', 'sis_user_id', 'user.name','user.short_name',
                     'user.sis_user_id', 'user_id']
    cols = ([col for col in inserted_cols if col in jusers_df]
            + [col for col in jusers_df if col not in inserted_cols])
    jusers_df = jusers_df[cols]

    columns_to_drop=[
        'course_section_id_y','sis_course_id_y','sis_user_id_y','user.login_id_y','user.name_y','user.short_name_y','user.sis_user_id_y','user.sortable_name_y'
    ]
    #    jusers_df.drop(columns_to_drop,inplace=True,axis=1)
    #jusers_df.rename(columns={'course_id_y':'190'}, inplace=True)


    jusers_df.to_excel(writer, sheet_name='concat')

    # Close the Pandas Excel writer and output the Excel file.
    writer.save()

if __name__ == "__main__": main()

