#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# ./get_status-for-users-in-course.py course_id
#
# Create an administrative assignment in the course (if it does not yet exist).
# This assignment does not accept any submission, but is just used to display a "grade" indicating a code for the student's status.
#
# In order to enable students to suggest their status early in the degree project, 
# get the student's status information from their custom data and
# update data in Status assignment in gradebook - but ONLY up to a threshold.
#
# The program also looks at assignments that have been completed and
# administrative actions that have been taken to up0ate the Status assignment's "grade".
#
# Background and underlying idea:
#
#I have done a program: set_status_in_course.py
#It is run using:
#        set_status_in_course.py course_id status_percent
# where the course_id is the Canvas course_id and status_percent is simply a string, which can look like 23.5
# It stores the information in the user's customer date in the name space se.kth.canvas-app.status_course_id
#
# My current idea is that the student can use this program to set their status, while they can view their status in the gradebook via a "Status" assignment (that has no submissions) but shows scores where the scores are the "status_percent" values. A teacher in the course will run a program get_status-for-users-in-course.py that will:
# 1. Get the status information for all the students enrolled in the course. Call this students_status.
# 2. If students_status is lower than a threshold and higher that the student's Status score in the gradebook then update the Status score in the gradebook. The idea is that some of the scores (after some point) should not be set by the the student.
# 3. If the Status score in the course is higher than than the students_status - then update the student's status value. [This operation could be optional.]
# 4. For a set of the assignments, if the assignment is marked Completed - update the Status score in the gradebook.
# 5.Optionally the program could even check the DIVA status and LADOK grade status and update the score based in these.
#
# Output: various diagnotic output
#
# with the option '-C'or '--containers' use HTTP rather than HTTPS for access to Canvas
# with the option -t' or '--testing' testing mode
#
# with the option "-v" or "--verbose" you get lots of output - showing in detail the operations of the program
#
# Can also be called with an alternative configuration file:
# ./custom-data-for-users-in-course.py --config config-test.json
#
# Example:
# ./get_status-for-users-in-course.py 11
#
# ./get_status-for-users-in-course.py --config config-test.json 11
#
# ./get_status-for-users-in-course.py -C 5
#
# G. Q. Maguire Jr.
#
# 2021-04-17
#
# Based on get_status-for-users-in-course.py

import requests, time
import pprint
import optparse
import sys
import json

from bs4 import BeautifulSoup

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

def put_user_custom_data_by_user_id(user_id, name_space, scope, data):
    # Use the Canvas API to set a user's custom data
    # PUT /api/v1/users/:user_id/custom_data(/*scope)
    if scope:
        url = "{0}/users/{1}/custom_data/{2}".format(baseUrl, user_id, scope)
    else:
        url = "{0}/users/{1}/custom_data".format(baseUrl, user_id)
    if Verbose_Flag:
        print("url: {}".format(url))

    payload={'ns': name_space,
             'data': data
    }
    r = requests.put(url, headers = header, json=payload)
    if Verbose_Flag:
        print("result of setting custom data: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        page_response=r.json()
        return page_response
    return []

def get_user_custom_data_by_user_id(user_id, name_space, scope):
    # Use the Canvas API to get a user's custom data
    # GET /api/v1/users/:user_id/custom_data(/*scope)
    if scope:
        url = "{0}/users/{1}/custom_data/{2}".format(baseUrl, user_id, scope)
    else:
        url = "{0}/users/{1}/custom_data".format(baseUrl, user_id)
    if Verbose_Flag:
        print("url: {}".format(url))

    payload={'ns': name_space }

    r = requests.get(url, headers = header, json=payload)
    if Verbose_Flag:
        print("result of getting custom data: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        page_response=r.json()
        return page_response
    return []


# Note that the students will be shown enrolled in EACH section they are enrolled in.
def students_in_course(course_id):
    user_found_thus_far=[]
    # Use the Canvas API to get the list of users enrolled in this course
    #GET /api/v1/courses/:course_id/enrollments

    url = "{0}/courses/{1}/enrollments".format(baseUrl,course_id)
    if Verbose_Flag:
        print("url: {}".format(url))

    extra_parameters={'per_page': '100',
                      'type[]': 'StudentEnrollment',
                      }
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

def user_profile_url(user_id):
    # Use the Canvas API to get the profile of a user
    #GET /api/v1/users/:user_id/profile
    url = "{0}/users/{1}/profile".format(baseUrl, user_id)
    if Verbose_Flag:
        print("user url: {}".format(url))

    r = requests.get(url, headers = header)
    if Verbose_Flag:
        print("result of getting profile: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        page_response=r.json()
        return page_response
    return []

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

def list_your_courses():
    courses_found_thus_far=[]
    # Use the Canvas API to get the list of all of your courses
    # GET /api/v1/courses

    url = baseUrl+'courses'
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
            # i.e., when the response is split into pieces - each returning only some of the list of modules
            # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
            while r.links.get('next', False):
                r = requests.get(r.links['next']['url'], headers=header)  
                if Verbose_Flag:
                    print("result of getting courses for a paginated response: {}".format(r.text))
                page_response = r.json()  
                for p_response in page_response:  
                    courses_found_thus_far.append(p_response)

    return courses_found_thus_far

def enrollments_in_course(course_id):
    global Verbose_Flag
    users_found_thus_far=[]

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

def list_assignments(course_id):
    global Verbose_Flag
    entries_found_thus_far=[]

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
            entries_found_thus_far.append(p_response)

        # the following is needed when the reponse has been paginated
        # i.e., when the response is split into pieces - each returning only some of the list of modules
        # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
        while r.links.get('next', False):
            r = requests.get(r.links['next']['url'], headers=header)  
            if Verbose_Flag:
                print("result of getting modules for a paginated response: {}".format(r.text))
            page_response = r.json()  
            for p_response in page_response:  
                entries_found_thus_far.append(p_response)

    return entries_found_thus_far

def assign_grade_for_assignment(course_id,assignment_id, user_id, grade, comment):
    global Verbose_Flag
    # Use the Canvas API to assign a grade for an assignment
    #PUT /api/v1/courses/:course_id/assignments/:assignment_id/submissions/:user_id

    # Request Parameters:
    # comment[text_comment]		string	Add a textual comment to the submission.
    # comment[group_comment]		boolean	Whether or not this comment should be sent to the entire group (defaults to false). Ignored if this is not a group assignment or if no text_comment is provided.
    # comment[media_comment_id]		string	Add an audio/video comment to the submission.
    # comment[media_comment_type]		string	The type of media comment being added.
    # comment[file_ids][]		integer	Attach files to this comment that were previously uploaded using the Submission Comment API's files action
    # include[visibility]		string	Whether this assignment is visible to the owner of the submission
    # submission[posted_grade]		string	Assign a score to the submission, updating both the “score” and “grade” fields on the submission record. This parameter can be passed in a few different formats:
    # submission[excuse]		boolean	    Sets the “excused” status of an assignment.
    # submission[late_policy_status]		string	Sets the late policy status to either “late”, “missing”, “none”, or null.
    # submission[seconds_late_override]		integer	Sets the seconds late if late policy status is “late”
    # rubric_assessment		RubricAssessment	Assign a rubric assessment to this assignment submission. The sub-parameters here depend on the rubric for the assignment. The general format is, for each row in the rubric:

    url = "{0}/courses/{1}/assignments/{2}/submissions/{3}".format(baseUrl,course_id, assignment_id, user_id)
    if Verbose_Flag:
        print("url: " + url)

    if comment:
        payload={'submission[posted_grade]': grade,
                 'comment[text_comment]': comment
                 }
    else:
        payload={'submission[posted_grade]': grade,
                 }

    r = requests.put(url, headers = header, data=payload)
    if Verbose_Flag:
        print("result of put assign_grade_for_assignment: {}".format(r.text))
    if r.status_code == requests.codes.ok:
        page_response=r.json()
        if Verbose_Flag:
            print("inserted grade for assignment")
        return True
    return False


def get_assignment_grade_by_id(course_id, user_id, assignment_id):
    global Verbose_Flag

    entries_found_thus_far=[]

    # Use the Canvas API to get the grade information
    # GET /api/v1/courses/:course_id/gradebook_history/feed

    url = "{0}/courses/{1}/gradebook_history/feed".format(baseUrl, course_id)
    if Verbose_Flag:
        print("url: {}".format(url))

    extra_parameters={'per_page': '100',
             'assignment_id': assignment_id,
             'user_id':  user_id
             }
    
    r = requests.get(url, params=extra_parameters, headers = header)

    if Verbose_Flag:
        print("result of getting a grade from gradebook: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        page_response=r.json()

        for p_response in page_response:  
            entries_found_thus_far.append(p_response)

        # the following is needed when the reponse has been paginated
        # i.e., when the response is split into pieces - each returning only some of the list of modules
        # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
        while r.links.get('next', False):
            r = requests.get(r.links['next']['url'], headers=header)  
            if Verbose_Flag:
                print("result of getting modules for a paginated response: {}".format(r.text))
            page_response = r.json()  
            for p_response in page_response:  
                entries_found_thus_far.append(p_response)

    return entries_found_thus_far

def get_a_grade(grades):
    global Verbose_Flag
    if grades and len(grades) > 1:
        return grades[0]['grade']             # by default the latest grade is first
    return None

def get_asssignment_grade(course_id, user_id, short_name):
    global Verbose_Flag

    assignment=assignment_given_short_name(short_name)
    if assignment:
        assignment_id=assignment['id']
    else:
        print("No such assignment named {0}".format(shrt_name))
        return None

    return get_assignment_grade_by_id(user_id, assignment_id)

def points_possible(short_name):
    global assignments
    for a in assignments:
        if a['short_name'] == short_name:
            return a['points_possible']
    return None

def assignment_given_short_name(short_name):
    global assignments
    for a in assignments:
        if a['short_name'] == short_name:
            return a
    return None

def assignment_due_date(short_name):
    global assignments
    for a in assignments:
        if a['short_name'] == short_name:
            return isodate.parse_datetime(a['due_at'])
    return None

def assignment_grading_type(short_name):
    global assignments
    for a in assignments:
        if a['short_name'] == short_name:
            return a['grading_type']
    return None

def grading_type_points(short_name):
    gt=assignment_grading_type(short_name) 
    if gt:
        return gt == 'points'
    return None

def assignment_grading_standard_id(short_name):
    global assignments
    for a in assignments:
        if a['short_name'] == short_name:
            return a['grading_standard_id']
    return None

def create_assignment(course_id, name, max_points, grading_type, description):
    # Use the Canvas API to create an assignment
    # POST /api/v1/courses/:course_id/assignments

    # Request Parameters:
    #Parameter		Type	Description
    # assignment[name]	string	The assignment name.
    # assignment[position]		integer	The position of this assignment in the group when displaying assignment lists.
    # assignment[submission_types][]		string	List of supported submission types for the assignment. Unless the assignment is allowing online submissions, the array should only have one element.
    # assignment[peer_reviews]	boolean	If submission_types does not include external_tool,discussion_topic, online_quiz, or on_paper, determines whether or not peer reviews will be turned on for the assignment.
    # assignment[notify_of_update] boolean     If true, Canvas will send a notification to students in the class notifying them that the content has changed.
    # assignment[grade_group_students_individually]		integer	 If this is a group assignment, teachers have the options to grade students individually. If false, Canvas will apply the assignment's score to each member of the group. If true, the teacher can manually assign scores to each member of the group.
    # assignment[points_possible]		number	 The maximum points possible on the assignment.
    # assignment[grading_type]		string	The strategy used for grading the assignment. The assignment defaults to “points” if this field is omitted.
    # assignment[description]		string	The assignment's description, supports HTML.
    # assignment[grading_standard_id]		integer	The grading standard id to set for the course. If no value is provided for this argument the current grading_standard will be un-set from this course. This will update the grading_type for the course to 'letter_grade' unless it is already 'gpa_scale'.
    # assignment[published]		boolean	Whether this assignment is published. (Only useful if 'draft state' account setting is on) Unpublished assignments are not visible to students.

    url = "{0}/courses/{1}/assignments".format(baseUrl, course_id)
    if Verbose_Flag:
        print("url: {}".format(url))

    payload={'assignment[name]': name,
             'assignment[submission_types][]': ["none"],
             'assignment[peer_reviews]': 'false',
             'assignment[notify_of_update]': 'false',
             'assignment[grade_group_students_individually]': 'true',
             'assignment[peer_reviews]': 'false',
             'assignment[points_possible]': max_points,
             'assignment[grading_type]': grading_type,
             'assignment[description]': description,
             'assignment[published]': 'true' # if not published it will not be in the gradebook
    }

    r = requests.post(url, headers = header, data=payload)
    if Verbose_Flag:
        print("result of post making an assignment: {}".format(r.text))
        print("r.status_code={}".format(r.status_code))
    if r.status_code == requests.codes.created:
        page_response=r.json()
        print("inserted assignment")
        return page_response['id']
    return False

def main():
    global Verbose_Flag
    global assignments
    
    default_picture_size=128

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

    # create the following list to keep track of users already processed
    already_processed_students=[]

    if (len(remainder) < 1):
        print("Insuffient arguments - must provide account_id course_id\n")
        sys.exit()
              
    course_id=remainder[0]

    assignments=list_assignments(course_id)
    # check for Status assignment
    status_assignment_id=None
    status_assignment_name='Status'
    status_assignment_description="This assigment is used to keep track of the status of the degree project. Students can suggest progress levels with set_status_in_course.py course_id status_percent; while teachers can update the status in the gradebook and with this program."
    for a in assignments:
        if a['name'] == status_assignment_name:
            status_assignment_id=a['id']

    if not status_assignment_id:
        status_assignment_id=create_assignment(course_id, status_assignment_name, 1, 'percent', status_assignment_description)
        print("Created Status assignment with assignment_id={0}".format(status_assignment_id))

    if options.testing:
        return
    
    all_student_enrollments_in_course=students_in_course(course_id)
    if all_student_enrollments_in_course:
        if Verbose_Flag:
    	    print(all_student_enrollments_in_course)

    maximum_for_student_update=0.200 # percent as a float

    for user in all_student_enrollments_in_course:
        user_id=user['user_id']

        if user_id not in already_processed_students:
            if user_id:
                # for example if a users's "grade": "10%", and the maximum points is 1, then their "score": 0.1
                students_grade=get_a_grade(get_assignment_grade_by_id(course_id, user_id, status_assignment_id))
                users_name=user['user']['sortable_name']
                print("{0}: students_grade={1}".format(users_name, students_grade))
                if students_grade:
                    print("{0}: students_grade={1}".format(users_name, students_grade))
                    if students_grade[-1:] == '%':
                        students_grade_float=float(students_grade[:-1])/100.0
                    else:
                        students_grade_float=float(students_grade)/100.0

                students_status=get_user_custom_data_by_user_id(user_id, 'se.kth.canvas-app.status_'+course_id,[])
                print("Existing custom data for user for course {0} is {1}".format(course_id, students_status))

                if students_status:
                    students_status=students_status.get('data', None)
                    if students_status[-1:] == '%':
                        students_status_float=float(students_status[:-1])/100.0
                    else:
                        students_status_float=float(students_status)/100.0

                    print("students_status_float={0}".format(students_status_float))
                    if (students_status_float < maximum_for_student_update):
                        if students_grade is None:
                            comment=None
                            assign_grade_for_assignment(course_id,status_assignment_id, user_id, students_status_float, comment)
                            continue
                        
                        if students_grade and (students_status_float > students_grade_float ):
                            comment=None
                            assign_grade_for_assignment(course_id,status_assignment_id, user_id, students_status_float, comment)

                #result2=put_user_custom_data_by_user_id(user_id, 'se.kth.canvas-app.status_'+course_id, [], status_percent)
                #print("Result of setting custom data for user for course {0} is {1}".format(course_id, result2))

                already_processed_students.append(user_id)

if __name__ == "__main__": main()
