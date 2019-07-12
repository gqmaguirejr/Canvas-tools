#!/usr/bin/python3
#
# ./insert-group_column_in_gradebook.py  course_id column_name groupset_name [prefix_to_remove]
# 
# Inserts a custom column with the indicated name using the data from from the named groupset
# it will create the column as necessary.
# Note that one can optionally strip a fixed prefix from the group names. For example, if each group name begins with "Project group" followed by space and a number
# then # ./insert-group_column_in_gradebook.py 6433 New_groups "Project Groups" "Project group"
# will simply insert the number with the leading space stripped.
# 
# with the option '-C'or '--containers' use HTTP rather than HTTPS for access to Canvas
# with the option "-v" or "--verbose" you get lots of output - showing in detail the operations of the program
#
# Can also be called with an alternative configuration file:
# ./insert-group_column_in_gradebook.py --config config-test.json
#
# G. Q. Maguire Jr.
#
# examples:
# ./insert-group_column_in_gradebook.py 6433 New_groups "Project Groups"
# ./insert-group_column_in_gradebook.py 6433 New_groups "Project Groups" "Project group"
#
# 2019.07.12
#

import requests, time
import optparse
import sys

import json

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

def students_in_course(course_id):
    students_found_thus_far=[]

    # Use the Canvas API to get the list of students in this course
    # GET /api/v1/courses/:course_id/users
    url = "{0}/courses/{1}/users".format(baseUrl,course_id)
    if Verbose_Flag:
        print("url: " + url)

    # enrollment_type[] should be set to 'student'
    # include[] perhaps include email, enrollments, avatar_url
    extra_parameters={'enrollment_type[]': 'student', 'include[]': 'enrollments'}
    r = requests.get(url, params=extra_parameters, headers = header)
    if Verbose_Flag:
        print("result of getting student enrollments: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        page_response=r.json()

        for p_response in page_response:  
            students_found_thus_far.append(p_response)

        # the following is needed when the reponse has been paginated
        # i.e., when the response is split into pieces - each returning only some of the list of modules
        # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
        if 'link' in r.headers:
            while r.links['current']['url'] != r.links['last']['url']:  
                r = requests.get(r.links['next']['url'], headers=header)  
                page_response = r.json()  
                for p_response in page_response:  
                    students_found_thus_far.append(p_response)
    return students_found_thus_far

def list_groups_in_course(course_id):
    groups_found_thus_far=[]

    # Use the Canvas API to get the list of groups in this course
    #GET /api/v1/courses/:course_id/groups

    url = "{0}/courses/{1}/groups".format(baseUrl,course_id)
    if Verbose_Flag:
        print("url: " + url)

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
        while r.links['current']['url'] != r.links['last']['url']:  
            r = requests.get(r.links['next']['url'], headers=header)  
            page_response = r.json()  
            for p_response in page_response:  
                groups_found_thus_far.append(p_response)

    return groups_found_thus_far


def list_categories_in_course(course_id):
    groups_found_thus_far=[]

    # Use the Canvas API to get the list of group categories in a course 
    # GET /api/v1/courses/:course_id/group_categories

    url = "{0}/courses/{1}/group_categories".format(baseUrl,course_id)
    if Verbose_Flag:
        print("url: " + url)

    r = requests.get(url, headers = header)
    if Verbose_Flag:
        print("result of getting group categories: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        page_response=r.json()

        for p_response in page_response:  
            groups_found_thus_far.append(p_response)

        # the following is needed when the reponse has been paginated
        # i.e., when the response is split into pieces - each returning only some of the list of modules
        # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
        while r.links['current']['url'] != r.links['last']['url']:  
            r = requests.get(r.links['next']['url'], headers=header)  
            page_response = r.json()  
            for p_response in page_response:  
                groups_found_thus_far.append(p_response)

    return groups_found_thus_far

def members_of_group(group_id):
    members_found_thus_far=[]

    # Use the Canvas API to get the list of members of group
    # GET /api/v1/groups/:group_id/users

    url = "{0}/groups/{1}/users".format(baseUrl,group_id)
    if Verbose_Flag:
        print("url: " + url)

    r = requests.get(url, headers = header)
    if Verbose_Flag:
        print("result of getting group categories: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        page_response=r.json()

        for p_response in page_response:  
            members_found_thus_far.append(p_response)

        # the following is needed when the reponse has been paginated
        # i.e., when the response is split into pieces - each returning only some of the list of modules
        # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
        while r.links['current']['url'] != r.links['last']['url']:  
            r = requests.get(r.links['next']['url'], headers=header)  
            page_response = r.json()  
            for p_response in page_response:  
                members_found_thus_far.append(p_response)

    return members_found_thus_far


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

    if (len(remainder) < 3):
        print("Insuffient arguments: must provide course_id column_name groupset_name\n")
        return

    course_id=remainder[0]
    column_name=remainder[1]
    groupset_name=remainder[2]

    prefix_to_remove=False
    if (len(remainder) == 4):
        prefix_to_remove=remainder[3]
        if Verbose_Flag:
            print("Remove the following prefix from the group names: {}".format(prefix_to_remove))

    list_of_columns=list_custom_columns(course_id)
    column_number=add_column_if_necessary(course_id, column_name, list_of_columns)
    if Verbose_Flag:    
        print('column number: ', column_number)

    list_of_columns=list_custom_columns(course_id)
    if Verbose_Flag:
        print(list_of_columns)

    #students=students_in_course(course_id)
    group_categories=list_categories_in_course(course_id)
    if Verbose_Flag:
        print("group_categories are {0}".format(group_categories))

    group_set_id=False
    for gc in group_categories:
        if gc['name'] == groupset_name:
            group_set_id=gc['id']
    
    if group_set_id:
        if Verbose_Flag:
            print("group_set_id is {}".format(group_set_id))

        groups=list_groups_in_course(course_id)
        if Verbose_Flag:
            print("groups are {0}".format(groups))

        for g in groups:
            if g['group_category_id'] == group_set_id:
                for m in members_of_group(g['id']):
                    if Verbose_Flag:
                        print("{0}: user_id is {1} and group name is {2}".format(m['name'], m['id'],  g['name']))
                    if prefix_to_remove:
                        put_custom_column_entries(course_id, column_number, m['id'], g['name'][len(prefix_to_remove):].strip())
                    else:
                        put_custom_column_entries(course_id, column_number, m['id'], g['name'])
    else:
        print("No group set named {}".format(groupset_name))

if __name__ == "__main__": main()

