#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# ./list_ungraded_submissions_in_your_courses_JSON.py
# Purpose:
#   output a list of ungraded assignments for a user to grade
#
# with the option "-v" or "--verbose" you get lots of output - showing in detail the operations of the program
#
# Can also be called with an alternative configuration file:
# ./list_your_courses.py --config config-test.json
#
# 
# G. Q. Maguire Jr.
#
# 2020.02.04
# based on earlier list_your_courses_JSON.py
#

import requests, time
import pprint
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
                     baseUrl="https://"+configuration["canvas"]["host"]+"/api/v1"

                     header = {'Authorization' : 'Bearer ' + access_token}
                     payload = {}
       except:
              print("Unable to open configuration file named {}".format(config_file))
              print("Please create a suitable configuration file, the default name is config.json")
              sys.exit()

def list_your_courses():
       courses_found_thus_far=[]
       # Use the Canvas API to get the list of all of your courses
       # GET /api/v1/courses

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
              # i.e., when the response is split into pieces - each returning only some of the list of modules
              # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
              while r.links['current']['url'] != r.links['last']['url']:  
                     r = requests.get(r.links['next']['url'], headers=header)  
                     if Verbose_Flag:
                            print("result of getting courses for a paginated response: {}".format(r.text))
                     page_response = r.json()  
                     for p_response in page_response:  
                            courses_found_thus_far.append(p_response)

       return courses_found_thus_far

def your_user_info():
       # Use the Canvas API to get yourown user information
       # GET /api/v1/users/self

       url = "{0}/users/self".format(baseUrl)
       if Verbose_Flag:
              print("url: {}".format(url))

       r = requests.get(url, headers = header)
       if Verbose_Flag:
              print("result of getting your own user information: {}".format(r.text))

       if r.status_code == requests.codes.ok:
              page_response=r.json()
              return page_response
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
              while r.links['current']['url'] != r.links['last']['url']:  
                     r = requests.get(r.links['next']['url'], headers=header)  
                     page_response = r.json()  
                     for p_response in page_response:  
                            sections_found_thus_far.append(p_response)

       return sections_found_thus_far

def enrollments_in_course(course_id):
       enrollments_found_thus_far=[]
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
                     enrollments_found_thus_far.append(p_response)

              # the following is needed when the reponse has been paginated
              # i.e., when the response is split into pieces - each returning only some of the list of modules
              # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
              while r.links['current']['url'] != r.links['last']['url']:  
                     r = requests.get(r.links['next']['url'], headers=header)  
                     page_response = r.json()  
                     for p_response in page_response:  
                            enrollments_found_thus_far.append(p_response)

       return enrollments_found_thus_far

def enrollments_in_section(section_id):
       enrollments_found_thus_far=[]
       # Use the Canvas API to get the list of users enrolled in this course
       #GET /api/v1/sections/:section_id/enrollments

       url = "{0}/sections/{1}/enrollments".format(baseUrl,section_id)
       if Verbose_Flag:
              print("url: {}".format(url))

       extra_parameters={'per_page': '100',
                         'type': ['StudentEnrollment']
       }
       r = requests.get(url, params=extra_parameters, headers = header)
       if Verbose_Flag:
              print("result of getting enrollments in section: {}".format(r.text))

       if r.status_code == requests.codes.ok:
              page_response=r.json()

              for p_response in page_response:  
                     enrollments_found_thus_far.append(p_response)

              # the following is needed when the reponse has been paginated
              # i.e., when the response is split into pieces - each returning only some of the list of modules
              # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
              while r.links['current']['url'] != r.links['last']['url']:  
                     r = requests.get(r.links['next']['url'], headers=header)  
                     page_response = r.json()  
                     for p_response in page_response:  
                            enrollments_found_thus_far.append(p_response)

       return enrollments_found_thus_far


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

def list_ungraded_assignments(course_id):
       assignments_found_thus_far=[]
       # Use the Canvas API to get the list of assignments for the course
       #GET /api/v1/courses/:course_id/assignments

       url = "{0}/courses/{1}/assignments".format(baseUrl, course_id)
       if Verbose_Flag:
              print("url: {}".format(url))

       extra_parameters={'bucket': 'ungraded'
       }
       r = requests.get(url, params=extra_parameters, headers = header)

       if Verbose_Flag:
              print("result of getting ungraded assignments: {}".format(r.text))

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


def submission_for_assignment_by_user(course_id, assignment_id, user_id):
       # return the submission information for a single user's assignment for a specific course as a dict
       #
       # Use the Canvas API to get a user's submission for a course for a specific assignment
       # GET /api/v1/courses/:course_id/assignments/:assignment_id/submissions/:user_id
       url = "{0}/courses/{1}/assignments/{2}/submissions/{3}".format(baseUrl, course_id, assignment_id, user_id)
       if Verbose_Flag:
              print("url: {}".format(url))

       #extra_parameters={'student_ids[]': 'all'}
       #r = requests.get(url, params=extra_parameters, headers = header)
       r = requests.get(url, headers = header)
       if Verbose_Flag:
              print("result of getting submissions: {}".format(r.text))

       if r.status_code == requests.codes.ok:
              page_response=r.json()
              if Verbose_Flag:
                     print("page_response: " + str(page_response))
              return page_response
       else:
              return dict()

def main():
       global Verbose_Flag

       parser = optparse.OptionParser()

       parser.add_option('-v', '--verbose',
                         dest="verbose",
                         default=False,
                         action="store_true",
                         help="Print lots of output to stdout"
       )

       parser.add_option('-s', '--sectionnames',
                         dest="course_info_file",
                         help="use JSON FILE giving section names for a user in each course",
                         metavar="FILE"
       )

       parser.add_option('-t', '--testing',
                         dest="testing",
                         default=False,
                         action="store_true",
                         help="execute test code"
       )

       parser.add_option('-X', '--exjobs',
                         dest="exjobs",
                         default=False,
                         action="store_true",
                         help="only include degree project courses"
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

       # get user's info
       user_info=your_user_info()
       if user_info:
              if Verbose_Flag:
                     pprint.pprint(user_info, indent=4)
              user_id=user_info['id']
              users_name=user_info['name']
       else:
              print("No user information")
              sys.exit()

       if options.course_info_file:
              course_info_file=options.course_info_file
       else:
              course_info_file="sections_in_courses_for_{0}.json".format(users_name)

       if Verbose_Flag:
              print("course_info_file={}".format(course_info_file))

       try:
              with open(course_info_file) as json_data_file:
                     try:
                            course_info = json.load(json_data_file)
                            if Verbose_Flag:                                   
                                   print("course_info={}".format(course_info))
                            courses_to_ignore=course_info.get('courses_to_ignore',{})
                            courses_without_specific_sections=course_info.get('courses_without_specific_sections', {})
                            courses_with_sections=course_info.get('courses_with_sections', {})

                     except json.JSONDecodeError as e:
                            print("Unable to load JSON file named {}".format(course_info_file))
                            sys.exit()

       except OSError as e:
              print(e.message)
              print("Unable to open JSON file named {}".format(course_info_file))
              sys.exit()

       # get list of user's courses
       course_list=list_your_courses()
       if len(course_list) == 0:
              print("User is not in any courses")
              sys.exit()

       # create a dictionary so one can lookup course details by course id
       course_dict=dict()
       for course in course_list:
              c_id=course['id']
              if courses_with_sections.get(str(c_id), []):
                     course_dict[c_id]=course
                     continue
              if courses_without_specific_sections.get(str(c_id), []):
                     course_dict[c_id]=course

       if Verbose_Flag:
              pprint.pprint(course_dict, indent=4)

       if not course_dict:
              print("User has no courses")
              sys.exit()

       # if only including degree project courses (course code of the form cc1ddX* or cc2ddX), then remove other courses
       if options.exjobs:
              for course in course_dict:
                     if not (len(course['course_code']) > 6) and (course['course_code'][5] == 'X') and (course['course_code'][2] == '1'  or (course['course_code'][2] == '2')):
                            course_dict.pop(course)

       if Verbose_Flag:
              print("courses to be considered={}".format(course_dict))

       # check if the there are multiple sections in the course
                    
       for c_id in course_dict:
              if Verbose_Flag:
                     print("course_dict[{0}]['workflow_state']={1}".format(c_id, course_dict[c_id]['workflow_state']))

              if course_dict[c_id]['workflow_state'] == 'unpublished': # no need to process unpublished courses
                     continue

              if options.testing:
                     if c_id not in [1585, 19885, 19871]:
                            continue

              if Verbose_Flag:
                     print("processing course_id={0}".format(c_id))
              relevant_enrollments=[]
              # check that the course is in the list of courses with sections
              c_sections=courses_with_sections.get(str(c_id), [])
              if c_sections:
                     sections=courses_with_sections[str(c_id)].get('sections', [])
                     if sections:
                            for s in sections:
                                   print("getting students in course {0} for section {1} for {2}".format(c_id, s, sections[s]))
                                   enrollments=enrollments_in_section(int(s))
                                   relevant_enrollments.extend(enrollments)
              else:             #  for courses_without_specific_section
                     relevant_enrollments=enrollments_in_course(c_id)

              if not relevant_enrollments: # if no relevant_enrollments, there is nothing to do
                     continue

              assignments=list_ungraded_assignments(c_id)
              if Verbose_Flag:
                     print("ungraded assignments={0}".format(assignments))

              for assignment in assignments:
                     assignment_id=assignment['id']
                     for enrollment in relevant_enrollments:
                            if Verbose_Flag:
                                   print("enrollment={0}".format(enrollment))
                            if Verbose_Flag:
                                   print("checking for ungraded assignment for student {0} on assignment {1} in course {2}".format(enrollment['user']['name'], assignment['name'], course_dict[c_id]['name']))

                            student_submission=submission_for_assignment_by_user(c_id, assignment_id, enrollment['user_id'])

                            # if the grader_id is NULL then the submission has not been graded
                            if student_submission:
                                   # ignore unsubmitted assignments and ignore assignments that are not relevant for a student
                                   if (student_submission['workflow_state'] == 'unsubmitted') or (student_submission['workflow_state'] is None) or (student_submission['workflow_state'] == 'deleted'):
                                          continue

                                   # if not graded and not excused, then report as ungraded
                                   if (student_submission['grader_id'] is None) and not (student_submission['excused'] == True):
                                          print("ungraded assignment for student: {0} on assignment: {1} in course: {2} ({3})".format(enrollment['user']['name'], assignment['name'], course_dict[c_id]['name'], c_id))
                                          print("student_submission={}".format(student_submission))

       
if __name__ == "__main__": main()

