#!/usr/bin/python3
#
# ./add-columns-for-II2202-final-presentation.py  course_id
# 
# creates custom columns in the gradebook to make it easier for each teacher to take notes during the final presentation
# The goal is to avoid the need to have a separate spreadsheet for all of this and then needing to transfer information to the gradebook.
# An additional benefit might be to encourage all of the teachers in the course keep similar notes.
#
# with the option '-C'or '--containers' use HTTP rather than HTTPS for access to Canvas
# with the option "-v" or "--verbose" you get lots of output - showing in detail the operations of the program
#
# Can also be called with an alternative configuration file:
# ./create_fake_users-in-course.py --config config-test.json
#
# Example:
# ./add-columns-for-II2202-final-presentation.py 6434 2019-01-01 2019-02-01
#
# G. Q. Maguire Jr.
#
# 2019.07.01
#

import csv, requests, time
from pprint import pprint
import optparse
import sys

import datetime
import isodate                  # for parsing ISO 8601 dates and times
import pytz                     # for time zones
import os                       # to make OS calls, here to get time zone info
from dateutil.tz import tzlocal

def utc_to_local(utc_dt):
    return utc_dt.replace(tzinfo=datetime.timezone.utc).astimezone(tz=None)

import datetime
import isodate                  # for parsing ISO 8601 dates and times
import pytz                     # for time zones
import os                       # to make OS calls, here to get time zone info
from dateutil.tz import tzlocal

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
        while r.links['current']['url'] != r.links['last']['url']:  
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
        if Verbose_Flag:
            print("inserted column")
        return True
    return False


def list_assignments(course_id):
    global Verbose_Flag
    assignments_found_thus_far=[]

    # Use the Canvas API to get the list of assignments for the course
    #GET /api/v1/courses/:course_id/assignments

    url = "{0}/courses/{1}/assignments".format(baseUrl,course_id)

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
        # i.e., when the response is split into pieces - each returning only some of the list of modules
        # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
        while r.links['current']['url'] != r.links['last']['url']:  
            r = requests.get(r.links['next']['url'], headers=header)  
            page_response = r.json()  
            for p_response in page_response:  
                assignments_found_thus_far.append(p_response)

    return assignments_found_thus_far

def lookup_assignment(assignment_name, list_of_assignment):
    for assignment in list_of_assignment:
        if assignment['name'] == assignment_name: 
            return assignment['id']
    return -1

def list_peer_review_assignments(course_id, assignment_id):
    global Verbose_Flag
    peer_review_assignments_found_thus_far=[]

    # Use the Canvas API to get the list of peer reviewing assignments
    # a given assignment for a course:
    #GET /api/v1/courses/:course_id/assignments/:assignment_id/peer_reviews
    
    url = "{0}/courses/{1}/assignments/{2}/peer_reviews".format(baseUrl,course_id, assignment_id)
    if Verbose_Flag:
        print("url: {}".format(url))

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

def users_in_course(course_id):
    global Verbose_Flag
    user_found_thus_far=[]

    # Use the Canvas API to get the list of users enrolled in this course
    #GET /api/v1/courses/:course_id/enrollments
    
    url = "{0}/courses/{1}/enrollments".format(baseUrl,course_id)
    if Verbose_Flag:
        print("url: {}".format(url))

    extra_parameters={'enrollment_type[]': 'student', 'include[]': 'email'}
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
        if 'link' in r.headers:
            while r.links['current']['url'] != r.links['last']['url']:  
                r = requests.get(r.links['next']['url'], headers=header)  
                page_response = r.json()  
                for p_response in page_response:  
                    user_found_thus_far.append(p_response)
    return user_found_thus_far

def name_of_student(user_id, users):
    for u in users:
        if u['user_id'] == user_id:
            return u['user']['sortable_name']
    return ''

def existing_opponent(user_id, opponents):
    for o in opponents:
        if o['user_id'] == user_id:
            return o['content']
    return False

# https://kth.test.instructure.com:443/api/v1/calendar_events?start_date=2019-01-01&end_date=2019-02-01&all_events=false&context_codes[]=course_6434

def calendar_events_in_course(course_id, start_date, end_date):
    global Verbose_Flag
    events_found_thus_far=[]

    # Use the Canvas API to get the list of users enrolled in this course
    #GET /api/v1/calendar_events
    
    url = "{0}/calendar_events".format(baseUrl)
    if Verbose_Flag:
        print("url: {}".format(url))

    extra_parameters={'start_date': start_date,
                      'end_date':   end_date,
                      'all_events': 'false',
                      'context_codes[]': 'course_'+course_id}
    r = requests.get(url, params=extra_parameters, headers = header)
    if Verbose_Flag:
        print("result of getting calendar events: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        page_response=r.json()

        for p_response in page_response:  
            events_found_thus_far.append(p_response)

        # the following is needed when the reponse has been paginated
        # i.e., when the response is split into pieces - each returning only some of the list of modules
        # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
        if 'link' in r.headers:
            while r.links['current']['url'] != r.links['last']['url']:  
                r = requests.get(r.links['next']['url'], headers=header)  
                page_response = r.json()  
                for p_response in page_response:  
                    events_found_thus_far.append(p_response)
    return events_found_thus_far

def list_groups_in_course(course_id):
    global Verbose_Flag
    groups_found_thus_far=[]

    # Use the Canvas API to get the list of groups in this course
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
            while r.links['current']['url'] != r.links['last']['url']:  
                r = requests.get(r.links['next']['url'], headers=header)  
                page_response = r.json()  
                for p_response in page_response:  
                    groups_found_thus_far.append(p_response)
    return groups_found_thus_far

def members_of_groups(group_id):
    global Verbose_Flag
    members_found_thus_far=[]

    # Use the Canvas API to get the list of members of group
    # GET /api/v1/groups/:group_id/users

    url = "{0}/groups/{1}/users".format(baseUrl, group_id)
    if Verbose_Flag:
        print("url: {}".format(url))

    r = requests.get(url, headers = header)
    if Verbose_Flag:
        print("result of getting group info: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        page_response=r.json()

        for p_response in page_response:  
            members_found_thus_far.append(p_response['id'])

        # the following is needed when the reponse has been paginated
        # i.e., when the response is split into pieces - each returning only some of the list of modules
        # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
        if 'link' in r.headers:
            while r.links['current']['url'] != r.links['last']['url']:  
                r = requests.get(r.links['next']['url'], headers=header)  
                page_response = r.json()  
                for p_response in page_response:  
                    members_found_thus_far.append(p_response['id'])
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

    parser.add_option('-t', '--testing',
                      dest="testing",
                      default=False,
                      action="store_true",
                      help="execute test code"
    )

    parser.add_option('-C', '--containers',
                      dest="containers",
                      default=False,
                      action="store_true",
                      help="for the container enviroment in the virtual machine"
    )

    options, remainder = parser.parse_args()

    Verbose_Flag=options.verbose
    if Verbose_Flag:
        print("ARGV      : {}".format(sys.argv[1:]))
        print("VERBOSE   : {}".format(options.verbose))
        print("REMAINING : {}".format(remainder))
        print("Configuration file : {}".format(options.config_filename))

    initialize(options)

    if (len(remainder) < 3):
        print("Insuffient arguments - must provide course_id start_date end_date")
    else:
        course_id=remainder[0]
        start_date=remainder[1]
        end_date=remainder[2]

        # create the following additional custom columns
        # if you change the names of these columns, be sure to change the strings later in the code
        columns_to_add=["Oral presentation date/time",
                        "title",
                        "Opponent",
	                "Written opposition (by opponents)",
	                "Questions from opponent",
                        "Notes on presentation",
                        "presentation grade",
                        "Grade for written opposition",
	                "Final report grade",
	                "Overall final grade"]

        # identify which assignment to use to get the information about the opponent(s)
        # for P1
        opposition_assignment_name="Opposition before final seminar"
        # for P1P2
        #opposition_assignment_name="Opposition before final seminar - with peer review"


        list_of_columns=list_custom_columns(course_id)
        for column_name in columns_to_add:
            column_number=add_column_if_necessary(course_id, column_name, list_of_columns)
            if Verbose_Flag:
                print('column_name: "{0}" at column number: {1}'.format(column_name, column_number))

        assignments=list_assignments(course_id)
        if Verbose_Flag:
            print('{0} assignments is {1}'.format(len(assignments), assignments))

        opposition_assignment=lookup_assignment(opposition_assignment_name, assignments)
        if Verbose_Flag:
            print('opposition assignment is {0}'.format(opposition_assignment))

        peer_review_assignments=list_peer_review_assignments(course_id, opposition_assignment)
        if Verbose_Flag:
            print('{0} peer reviewing assignments is {1}'.format(len(peer_review_assignments), peer_review_assignments))
        # user_id is the student being reviewed, assessor_id is the peer reviewer

        list_of_columns=list_custom_columns(course_id)
        if Verbose_Flag:
            print('final list of columns is {}'.format(list_of_columns))

        # Add names of peer reviewer(s) to the opponent column
        opponent_column_number=lookup_column_number("Opponent", list_of_columns)

        opponents=list_custom_column_entries(course_id, opponent_column_number)
        if Verbose_Flag:
            print('{0} opponents is {1}'.format(len(opponents), opponents))

        users=users_in_course(course_id)
        if Verbose_Flag:
            print('{0} users is {1}'.format(len(users), users))

        for pa in peer_review_assignments:
            user_id=pa['user_id']
            assessor_id=pa['assessor_id']
            assessor_name=name_of_student(assessor_id, users)
            opponent=existing_opponent(user_id, opponents)

            if not opponent:
                put_custom_column_entries(course_id, opponent_column_number, user_id, assessor_name)
                if Verbose_Flag:
                    print("{0} is reviewed by {1} named {2}".format(user_id, assessor_id, assessor_name))
            else:
                #if opponent != assessor_name:
                if opponent.find(assessor_name) < 0:
                    put_custom_column_entries(course_id, opponent_column_number, user_id, opponent + ';' + assessor_name)
                    if Verbose_Flag:
                        print("{0} is reviewed by multiple {1}".format(user_id, opponent + ';' + assessor_name))

        # get group information
        groups=list_groups_in_course(course_id)
        if Verbose_Flag:
            print("{0} groups are {1}".format(len(groups), groups))
        group_members_by_group=dict()
        group_by_member=dict()
        for g in groups:
            group_id=g['id']
            m=members_of_groups(group_id)
            if Verbose_Flag:
                print("members of group {0} {1} are {2}".format(group_id, g['name'], m))
            group_members_by_group[group_id]=m
            for m1 in m:
                group_by_member[m1]=group_id

        # calendar events
        events=calendar_events_in_course(course_id, start_date, end_date)
        if Verbose_Flag:
            print("{0} events are {1}".format(len(events), events))
        date_time_column_number=lookup_column_number("Oral presentation date/time", list_of_columns)

        user_prefix="user_"
        group_prefix="group_"
        for e in events:
            for child_events in e['child_events']:
                timestamp=child_events['start_at']
                t1=isodate.parse_datetime(timestamp)
                t2=t1.astimezone()
                time_stamp_local=t2.strftime("%Y-%m-%d %H:%M")
                if Verbose_Flag:
                    print("local time {0} Z time {1}".format(time_stamp_local, timestamp))

                cc=child_events['context_code']
                if cc.startswith(user_prefix): # process the event for the user who booked it
                    user_id=int(cc[len(user_prefix):])
                    if Verbose_Flag:
                        print("context_code {0} for user_id {1} named {2}".format(cc, user_id, name_of_student(user_id, users)))
                    group_id=group_by_member[user_id]
                    for m in group_members_by_group[group_id]: # add timestamp for all group members
                        put_custom_column_entries(course_id, date_time_column_number, m, time_stamp_local)
                else:
                    if cc.startswith(group_prefix): # process the event for the group who booked it
                        group_id=int(cc[len(group_prefix):])
                        for m in group_members_by_group[group_id]: # add timestamp for all group members
                            put_custom_column_entries(course_id, date_time_column_number, m, time_stamp_local)

if __name__ == "__main__": main()

