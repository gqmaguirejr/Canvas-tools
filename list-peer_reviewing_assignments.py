#!/usr/bin/python3
#
# ./list-peer_reviewing_assignments.py course_id assignment_id
#
# outputs a summary of peer reviewing assignments as an xlsx file of the form: peer_reviewing_assignments-189.xlsx
#
# This spreadsheet contains information about the peer review assignment, user, and a simplified set of assignments
#
# Extensive use is made of Python Pandas merge operations.
# 
# G. Q. Maguire Jr.
#
# 2019.09.27 based on earlier program of the same name - updated to deal with initialize(options)
#

import csv, requests, time
from pprint import pprint
import optparse
import sys

from io import StringIO, BytesIO

from lxml import html

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

##############################################################################
## ONLY update the code below if you are experimenting with other API calls ##
##############################################################################

## GET /api/v1/sections/:section_id/assignments/:assignment_id/peer_reviews

def list_peer_review_assignments(course_id, assignment_id):
       peer_review_assignments_found_thus_far=[]

       # Use the Canvas API to get the list of peer reviewing assignments
       # a given assignment for a course:
       #GET /api/v1/courses/:course_id/assignments/:assignment_id/peer_reviews
       
       url = "{0}/courses/{1}/assignments/{2}/peer_reviews".format(baseUrl, course_id, assignment_id)
       if Verbose_Flag:
              print("url: " + url)

       payload={'include[]': "submission_comments"}
       r = requests.get(url, headers = header, data=payload)
       #r = requests.get(url, headers = header)
       if Verbose_Flag:
              print("result of getting peer review assignments: {}".format(r.text))

       if r.status_code == requests.codes.ok:
              page_response=r.json()

              for p_response in page_response:  
                     peer_review_assignments_found_thus_far.append(p_response)

              # the following is needed when the reponse has been paginated
              # i.e., when the response is split into pieces - each returning only some of the list of modules
              # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
              if 'link' in r.headers:
                     while r.links['current']['url'] != r.links['last']['url']:  
                            r = requests.get(r.links['next']['url'], headers=header)  
                            page_response = r.json()  
                            for p_response in page_response:  
                                   peer_review_assignments_found_thus_far.append(p_response)

       return peer_review_assignments_found_thus_far

def sections_in_course(course_id):
       sections_found_thus_far=[]
       # Use the Canvas API to get the list of sections for this course
       #GET /api/v1/courses/:course_id/sections

       url = "{0}/courses/{1}/sections".format(baseUrl, course_id)

       if Verbose_Flag:
              print("url: " + url)

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
              while r.links['current']['url'] != r.links['last']['url']:  
                     r = requests.get(r.links['next']['url'], headers=header)  
                     page_response = r.json()  
                     for p_response in page_response:  
                            sections_found_thus_far.append(p_response)

       return sections_found_thus_far



def summarize_assignments(list_of_assignments):
       summary_of_assignments={}
       for assignm in list_of_assignments:
              summary_of_assignments[assignm['id']]=assignm['name']

       print("summary_of_assignments={}".format(summary_of_assignments))

def list_assignments(course_id):
       assignments_found_thus_far=[]

       # Use the Canvas API to get the list of assignments for the course
       #GET /api/v1/courses/:course_id/assignments

       url = "{0}/courses/{1}/assignments".format(baseUrl, course_id)
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


def list_custom_column_entries(course_id, column_number):
       entries_found_thus_far=[]

       # Use the Canvas API to get the list of custom column entries for a specific column for the course
       #GET /api/v1/courses/:course_id/custom_gradebook_columns/:id/data

       url = "{0}/courses/{1}/custom_gradebook_columns/{2}/data".format(baseUrl, course_id, column_number)
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
              while r.links['current']['url'] != r.links['last']['url']:  
                     r = requests.get(r.links['next']['url'], headers=header)  
                     page_response = r.json()  
                     for p_response in page_response:  
                            entries_found_thus_far.append(p_response)

       return entries_found_thus_far

def list_custom_columns(course_id):
       columns_found_thus_far=[]

       # Use the Canvas API to get the list of custom column for this course
       #GET /api/v1/courses/:course_id/custom_gradebook_columns

       url = "{0}/courses/{1}/custom_gradebook_columns".format(baseUrl, course_id)
       if Verbose_Flag:
              print("url: " + url)

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
              while r.links['current']['url'] != r.links['last']['url']:  
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

    url = "{0}/courses/{1}/custom_gradebook_columns".format(baseUrl, course_id)

    if Verbose_Flag:
       print("url: " + url)
    payload={'column[title]': column_name}
    r = requests.post(url, headers = header, data=payload)
    print("result of post creating custom column: {}".format(r.text))
    if r.status_code == requests.codes.ok:
       print("result of inserting the item into the module: {}".format(r.text))
       if r.status_code == requests.codes.ok:
           page_response=r.json()
           print("inserted column")
           return True
    return False

def users_in_course(course_id):
       user_found_thus_far=[]

       # Use the Canvas API to get the list of users enrolled in this course
       #GET /api/v1/courses/:course_id/enrollments

       url = "{0}/courses/{1}/enrollments".format(baseUrl, course_id)
       if Verbose_Flag:
              print("url: " + url)

       r = requests.get(url, headers = header)
       if Verbose_Flag:
              print("result of getting enrollments: {}".format(r.text))

       if r.status_code == requests.codes.ok:
              page_response=r.json()

              for p_response in page_response:  
                     user_found_thus_far.append(p_response)

              # the following is needed when the reponse has been paginated
              # i.e., when the response is split into pieces - each returning only some of the list of modules
              # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
              while r.links['current']['url'] != r.links['last']['url']:  
                     r = requests.get(r.links['next']['url'], headers=header)  
                     page_response = r.json()  
                     for p_response in page_response:  
                            user_found_thus_far.append(p_response)
       return user_found_thus_far

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

       initialize(options)

       if (len(remainder) < 2):
              print("Insuffient arguments\n must provide course_id assignment_id\n")
       else:
              course_id=remainder[0]
              assignment_id=remainder[1]

              users=users_in_course(course_id)
              users_df1=pd.json_normalize(users)
              sections_df=pd.json_normalize(sections_in_course(course_id))
              sections_df.rename(columns = {'id':'course_section_id'}, inplace = True)
              columns_to_drop=['course_id', 'end_at', 'integration_id', 'nonxlist_course_id', 'sis_course_id', 'sis_section_id', 'start_at']
              sections_df.drop(columns_to_drop,inplace=True,axis=1)


              output=list_peer_review_assignments(course_id, assignment_id)
              if (output):
                     if Verbose_Flag:
                            print(output)
                     # the following was inspired by the section "Using XlsxWriter with Pandas" on http://xlsxwriter.readthedocs.io/working_with_pandas.html
                     # set up the output write
                     writer = pd.ExcelWriter('peer_reviewing_assignments-'+str(course_id)+'-assignment-'+str(assignment_id)+'.xlsx', engine='xlsxwriter')

                     sections_df.to_excel(writer, sheet_name='Sections')

                     # the following was inspired by pbreach's answer on Jan 21 '14 at 18:17 in http://stackoverflow.com/questions/21104592/json-to-pandas-dataframe
                     # create a Panda dataframe from the output
                     df=pd.json_normalize(output)
                     # Convert the dataframe to an XlsxWriter Excel object.
                     df.to_excel(writer, sheet_name='PeerAssignment')

                     users_df = pd.merge(sections_df, users_df1, on='course_section_id')
                     users_df.to_excel(writer, sheet_name='Users')

                     merge_df = pd.merge(df, users_df, on='user_id')
                     merge_df.to_excel(writer, sheet_name='Merged')

                     # change the user_id into an assessor_id and do another merge
                     assessors_df=users_df.copy(deep=True)
                     columns_to_drop=['course_section_id']
                     assessors_df.drop(columns_to_drop,inplace=True,axis=1)

                     assessors_df.rename(columns = {'user_id':'assessor_id'}, inplace = True)
                     merge2_df = pd.merge(merge_df, assessors_df, on='assessor_id')
                     columns_to_drop=['id', 'created_at_y', 'name_y']
                     #merge2_df.drop(columns_to_drop,inplace=True,axis=1)

                     #merge2_df.drop_duplicates(inplace=True)
                     merge2_df.to_excel(writer, sheet_name='Merged2')
                     
                     columns_to_drop=['asset_id', 'asset_type', 'id_x',
                                      'associated_user_id_x',
                                      'course_integration_id_x',
                                      'created_at_x',
                                      'end_at_x',
                                      'enrollment_state_x',
                                      'grades.current_grade_x',
                                      'grades.current_score_x',
                                      'grades.final_grade_x',
                                      'grades.final_score_x',
                                      'grades.html_url_x', 'html_url_x',
                                      'id_y', 'last_activity_at_x',
                                      'limit_privileges_to_course_section_x',
                                      'role_x', 'role_id_x',
                                      'root_account_id_x',
                                      'section_integration_id_x',
                                      'sis_account_id_x', 'sis_course_id_x',
                                      'sis_account_id_x', 'sis_course_id_x',
                                      'sis_section_id_x', 'sis_user_id_x',
                                      'start_at_x', 'total_activity_time_x',
                                      'type_x', 'updated_at_x', 'user.id_x',
                                      'associated_user_id_y', 'course_id_y',
                                      'course_integration_id_y',
                                      'end_at_y', 'enrollment_state_y',
                                      'grades.current_grade_y',
                                      'grades.current_score_y',
                                      'grades.final_grade_y',
                                      'grades.final_score_y',
                                      'grades.html_url_y', 'html_url_y',
                                      'last_activity_at_y',
                                      'limit_privileges_to_course_section_y',
                                      'role_y', 'role_id_y',
                                      'root_account_id_y',
                                      'section_integration_id_y',
                                      'sis_account_id_y', 'sis_course_id_y',
                                      'sis_section_id_y', 'sis_user_id_y',
                                      'start_at_y', 'total_activity_time_y',
                                      'type_y', 'updated_at_y',
                                      'user.short_name_x', 'user.sortable_name_x',
                                      'user.short_name_y', 'user.sortable_name_y'

                     ]
                     #merge2_df.drop(columns_to_drop,inplace=True,axis=1)
                     
                     old_names = ['course_id_x_x', 'name_x'] 
                     new_names = ['course_id', 'section_name'] 
                     #merge2_df.rename(columns=dict(zip(old_names, new_names)), inplace=True)


                     old_names = ['user.id_y', 'user.login_id_y', 'user.name_y'] 
                     new_names = ['user.id_assessor', 'user.login_id_assessor', 'user.name_assessor'] 
                     #merge2_df.rename(columns=dict(zip(old_names, new_names)), inplace=True)
                     merge2_df.to_excel(writer, sheet_name='Reviewers')

                     # Close the Pandas Excel writer and output the Excel file.
                     writer.save()

if __name__ == "__main__": main()

