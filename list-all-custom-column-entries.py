#!/usr/bin/python3
#
# ./list-all-custom-column-entries.py course_id
#
# Outputs an xlsx file of the form containing all of the custom columns: custom-column-entries-course_id-column-column_all.xlsx
# The first column of the output will be user_id.
#
# with the option '-C'or '--containers' use HTTP rather than HTTPS for access to Canvas
# with the option "-v" or "--verbose" you get lots of output - showing in detail the operations of the program
#
# Can also be called with an alternative configuration file:
# ./create_fake_users-in-course.py --config config-test.json
#
# G. Q. Maguire Jr.
#
# based on 2016.11.29 version of Canvas-git/list-all-custom-column-entries.py
#
# 2019.02.19
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
        while r.links.get('next', False):
            r = requests.get(r.links['next']['url'], headers=header)
            page_response = r.json()  
            for p_response in page_response:  
                users_found_thus_far.append(p_response)

    return users_found_thus_far

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

    if (len(remainder) < 1):
        print("Insuffient arguments\n must provide course_id\n")
        return

    course_id=remainder[0]
    users=users_in_course(course_id)
    if Verbose_Flag:
        print("users are: {0}".format(users))
    if (users):
        users_df=pd.json_normalize(users)
        
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
            'user.integration_id'
        ]
        # keep the following:
        # 'sis_course_id',
        # 'sis_user_id',
	# 'user.login_id',
	# 'user.name',
	# 'user.short_name'
	# 'user.sis_user_id'
	# 'user.sortable_name,'
	# 'user_id'
        
        users_df.drop(columns_to_drop,inplace=True,axis=1)
        users_df.drop_duplicates(subset=None, keep='first', inplace=True)

    # get section info
    sections=sections_in_course(course_id)
    sections_df=pd.json_normalize(sections)

    # augment the users-df with section names
    for index, row in  users_df.iterrows():
        if Verbose_Flag:
            print("index: {0}, row[user_id]: {1}".format(index, row['user_id']))

        user_id=row['user_id']
        if Verbose_Flag:
            print("user_id: {}".format(user_id))

        section_name=section_name_from_section_id(sections, row['course_section_id'])
        users_df.at[index, 'Section_name']= section_name


    list_of_columns=list_custom_columns(course_id)              
    if Verbose_Flag:
        print('list_of_columns: ', list_of_columns)

    custom_columns_present=False
    index=0
    for column in list_of_columns:
        column_name=column['title']
        column_number=column['id']
        
        if Verbose_Flag:
            print('column_name: ', column_name, '; column_number: ', column_number)

        output=list_custom_column_entries(course_id, column_number)
        if (output):
            if Verbose_Flag:
                print(output)

            # the following was inspired by pbreach's answer on Jan 21 '14 at 18:17 in http://stackoverflow.com/questions/21104592/json-to-pandas-dataframe
            # create a Panda dataframe from the output
            df=pd.json_normalize(output)
            df.rename(columns = {'content': column_name}, inplace = True)
            index=index+1
            
            if index == 1:
                if Verbose_Flag:
                    print('index: ', index)
                merge_df = df
                custom_columns_present=True
            else:
                if Verbose_Flag:
                    print('else index: ', index)
                # Note that one has to do an outer join in case on of the columns does not have a matching entry.
                # This works because the outer join uses the union of the keys from both inputs.
                new_merge_df = pd.merge(merge_df, df, on='user_id', how='outer')
                merge_df=new_merge_df


    #  based upon contribution by Ed Chum on Aug 4 '14 at 15:30 at http://stackoverflow.com/questions/25122099/move-column-by-name-to-front-of-table-in-pandas
    # get a list of columns
    #cols = list(merge_df)
    if custom_columns_present:
        cols = list(merge_df)
        # move the column to head of list using index, pop and insert
        cols.insert(0, cols.pop(cols.index('user_id')))
        # use ix to reorder
        #merge_df = merge_df.ix[:, cols]
        merge_df = merge_df.loc[:, cols]

        # the following was inspired by the section "Using XlsxWriter with Pandas" on http://xlsxwriter.readthedocs.io/working_with_pandas.html
        # set up the output write
        writer = pd.ExcelWriter('custom-column-entries-'+str(course_id)+'-column-all.xlsx', engine='xlsxwriter')

        users_df.to_excel(writer, sheet_name="Students")
        sections_df.to_excel(writer, sheet_name='Sections')

        # Convert the dataframe to an XlsxWriter Excel object.
        merge_df.to_excel(writer, sheet_name='Custom_Columns')

        new_merge_df = pd.merge(merge_df, users_df, on='user_id', how='outer')

        # below are examples of some columns that might be dropped
        columns_to_drop=[
            'course_id',
            'sis_course_id',
        ]
        
        new_merge_df.drop(columns_to_drop,inplace=True,axis=1)
        new_merge_df.to_excel(writer, sheet_name='Custom_Columns_with_name')

        # Close the Pandas Excel writer and output the Excel file.
        writer.close()
    else:
        print("There were no custom columns")

if __name__ == "__main__": main()

