#!/usr/bin/python3
# -*- coding: utf-8 -*-
# -*- mode: python; python-indent-offset: 4 -*-
#
# ./add_students_to_examiners_section_in_course.py course_id [admin_assignment_name]
#
# Output: using assignment 'Examiner' as the administrative data to do the assignment into sections
# 	Added XXXX to section for Maguire Jr, Gerald Quentin
#
# with the option "-v" or "--verbose" you get lots of output - showing in detail the operations of the program
#
# Can also be called with an alternative configuration file:
# ./add_students_to_examiners_section_in_course.py --config config-test.json 22156
#
# Example:
# ./add_students_to_examiners_section_in_course.py 22156
#
# or
#
# ./add_students_to_examiners_section_in_course.py 22156 "Supervisor"
#
# 
# G. Q. Maguire Jr.
#
# based on earlier teachers_in_coursse.py
#
# 2021.01.24
#

import requests, time
import pprint
import optparse
import sys
import json

# Import urlopen() for either Python 2 or 3.
try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen

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

# create the following dict to use as an associate directory about users
selected_user_data={}


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
            for p_response in page_response:  
                user_found_thus_far.append(p_response)
    return user_found_thus_far

def user_name_from_user_id(enrollments, id):
    for i in enrollments:
        if i['user_id'] == id:
            return i['user']['name']

def users_sections_from_user_id(enrollments, id):
    section_id=list()
    for i in enrollments:
        if i['user_id'] == id:
            section_id.append(i['course_section_id'])
    return section_id

def section_name_from_section_id(sections_info, section_id): 
    for i in sections_info:
        if i['id'] == section_id:
            return i['name']

def section_id_from_section_name(sections_info, section_name): 
    for i in sections_info:
        if i['name'] == section_name:
            return i['id']
    return False

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

        if Verbose_Flag:
            print("result of creating section: {}".format(r.text))

        if r.status_code == requests.codes.ok:
            page_response=r.json()

            for p_response in page_response:  
                sections_found_thus_far.append(p_response)

    return sections_found_thus_far

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

def enroll_student_in_section(course_id, user_id, section_id):
    global Verbose_Flag
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

    if Verbose_Flag:
        print("result of enrolling student in section: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        page_response=r.json()
        return page_response

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

    options, remainder = parser.parse_args()

    Verbose_Flag=options.verbose
    if Verbose_Flag:
        print("ARGV      : {}".format(sys.argv[1:]))
        print("VERBOSE   : {}".format(options.verbose))
        print("REMAINING : {}".format(remainder))
        print("Configuration file : {}".format(options.config_filename))


    initialize(options)

    if (len(remainder) < 1):
        print("Insuffient arguments - must provide course_id\n")
        return

    course_id=remainder[0]
    enrollments=users_in_course(course_id)

    teachers=list()
    for e in enrollments:
        if e['type'] == 'TeacherEnrollment':
            teachers.append(e)

    teacher_names_sortable=list()
    for e in teachers:
        user_data=e.get('user', False)
        if user_data:
            sortable_name=user_data.get('sortable_name', False)
            if sortable_name:
                if sortable_name in teacher_names_sortable:
                    continue
                else:
                    teacher_names_sortable.append(sortable_name)
    
    if Verbose_Flag:
        print("teacher_names_sortable={0}".format(teacher_names_sortable))

    if len(teacher_names_sortable) == 0:
        print("No teacher in the course, so there is nothing to do")

    teacher_names_sortable_sorted=sorted(teacher_names_sortable)
    if Verbose_Flag:
        print("teacher_names_sortable_sorted={0}".format(teacher_names_sortable_sorted))

    new_sections_needed=list()
    list_of_section=sections_in_course(course_id)
    
    for t in teacher_names_sortable_sorted:
        section_id=section_id_from_section_name(list_of_section, t)
        if not section_id:
            new_sections_needed.append(t)

    # if necessary create the missing sections
    if len(new_sections_needed) > 0:
        create_sections_in_course(course_id, new_sections_needed)

    teacher_to_section_mapping=dict()
    list_of_section=sections_in_course(course_id)
    
    for t in teacher_names_sortable_sorted:
        section_id=section_id_from_section_name(list_of_section, t)
        if not section_id:
            print("Missing section for {0}".format(t))
        else:
            teacher_to_section_mapping[t]=section_id

    if Verbose_Flag:
        print("teacher_to_section_mapping={}".format(teacher_to_section_mapping))

    if (len(remainder) > 1):
        admin_assignment_name=remainder[1]
    else:
        admin_assignment_name="Examiner"

    print("using assignment '{0}' as the administrative data to do the assignment into sections".format(admin_assignment_name))

    # check for assignemnt
    course_assignments=list_assignments(course_id)
    assignment_id=assignment_id_from_assignment_name(course_assignments, admin_assignment_name)
    if not assignment_id:
        print("No assignment named {0}".format(admin_assignment_name))
        return
    
    if Verbose_Flag:
        print("assignment_id={}".format(assignment_id))

    # get the "grade" of the administrative assignment and use this to get the teacher's name and then lookup the section based on this name
    student_ids=set()
    for e in enrollments:
        if e['type'] == 'StudentEnrollment':
            student_ids.add(e['user_id'])

    for s in student_ids:
        grade_info=get_grade_for_assignment(course_id, assignment_id, s)
        grade=grade_info.get('grade', False)
        if grade:
            user_name=user_name_from_user_id(enrollments, s)

            teacher_section_id=teacher_to_section_mapping.get(grade, False)
            if Verbose_Flag:
                print("teacher_section_id={}".format(teacher_section_id))

            existing_sections_for_user=users_sections_from_user_id(enrollments, s)
            if existing_sections_for_user and (teacher_section_id in existing_sections_for_user):
                if Verbose_Flag:
                    print("Nothing to do - the user is already in the teacher's section")
            else:
                # add the student to this section
                enroll_student_in_section(course_id, s, teacher_section_id)
                print("Added {0} to section for {1}".format(user_name, grade))

if __name__ == "__main__": main()
