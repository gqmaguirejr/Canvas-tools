#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# ./create_JSON_file_of_sections_in_your_courses.py
#
# with the option "-v" or "--verbose" you get lots of output - showing in detail the operations of the program
#
# Can also be called with an alternative configuration file:
# ./create_JSON_file_of_sections_in_your_courses --config config-test.json
#
# Purpose:
#   Create a JSON file with information about courses where user enrolled as a 'TeacherEnrollment', 'Examiner', or 'TaEnrollment'
#
# The JSON file contains a course_info dict 
#   courses_to_ignore=course_info['courses_to_ignore'] - courses that the user wants to ignore
#   courses_without_specific_sections=course_info['courses_without_specific_sections'] - courses where the user is responsible for all the students
#   courses_with_sections=course_info['courses_with_sections']  - courses where the user has a specific section
#               the specific section's name may be the user's name or some other unique string (such as "Chip's section")
#               Because the name of the relevant section can be arbitrary, this file is necessary to know which section belongs to a given user
# 
# Examples:
#   create file for only exjobb courses:
#      ./create_JSON_file_of_sections_in_your_courses.py -s fee.json -X
#
#   update an existing file (possibly adding new courses)
#      ./create_JSON_file_of_sections_in_your_courses.py -s foo.json -U
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

def students_in_course(course_id):
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

def cleanup_sections(users_name, courses_with_sections):
       # if there is a section with a name == users_name, then eliminate all of the other sections
       for c in courses_with_sections:
              section_for_user=False
              sections=courses_with_sections[c].get('sections', [])
              for s in sections:
                     if courses_with_sections[c]['sections'][s] == users_name:
                            section_for_user=s
              if section_for_user:
                     courses_with_sections[c]['sections']={section_for_user: users_name}

       return courses_with_sections

def remove_courses_to_be_ignored(course_list, courses_to_ignore):
       new_course_list=[]
       for course in course_list:              
              if Verbose_Flag:
                     print("course['id']={}".format(course['id']))
              # note that the course['id'] is an integer in course_list, but a string in courses_to_ignore
              ci=courses_to_ignore.get(str(course['id']), False)
              if ci:
                     print("ignoring course['id']={}".format(course['id']))
              else:
                     new_course_list.append(course)
       return new_course_list
              
def remove_courses_to_be_ignored_dict(course_dict, courses_to_ignore):
       new_course_dict=dict()
       for course in course_dict:
              if Verbose_Flag:
                     print("course['id']={}".format(course['id']))
              ci=courses_to_ignore.get(course, False)
              if ci:
                     print("ignoring course with id={}".format(course))
              else:
                     new_course_dict[course]=course_dict[course]
       return new_course_dict
              
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

       parser.add_option('-U', '--update',
                         dest="update",
                         default=False,
                         action="store_true",
                         help="update existing JSON file"
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

       user_info=your_user_info()
       if user_info:
              if Verbose_Flag:
                     pprint.pprint(user_info, indent=4)
              user_id=user_info['id']
              users_name=user_info['name']
       else:
              print("No user information")
              sys.exit()
       

       course_info=dict()

       if options.course_info_file:
              course_info_file=options.course_info_file
       else:
              course_info_file="sections_in_courses_for_{0}.json".format(users_name)

       if Verbose_Flag:
              print("course_info_file={}".format(course_info_file))

       if options.update:
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

       else:                    # otherwise create empty dictionaries
              courses_to_ignore=dict()
              courses_without_specific_sections=dict()
              courses_with_sections=dict()
       
       course_list=list_your_courses()
       if len(course_list) == 0:
              print("User is not in any courses")
              sys.exit()
       if Verbose_Flag:
              pprint.pprint(course_list, indent=4)

       # remove courses that are to be ignored
       if len(courses_to_ignore) > 0:
              if Verbose_Flag:
                     print("courses_to_ignore={}".format(courses_to_ignore))
              # remove the courses to be ignored from the list of the user's courses
              course_list=remove_courses_to_be_ignored(course_list, courses_to_ignore)
              # also remove courses to be ignored from the courses_with_sections dict
              courses_without_specific_sections=remove_courses_to_be_ignored_dict(courses_without_specific_sections, courses_to_ignore)
              #Note: We do not need removes from courses_with_sections - as they will recomputed from the reduced course_list
              courses_with_sections=remove_courses_to_be_ignored_dict(courses_with_sections, courses_to_ignore)
              
       # if only including degree project courses (course code of the form cc1ddX* or cc2ddX), then skip other courses
       if options.exjobs:
              exjobb_courses=[]
              for course in course_list:
                     if (len(course['course_code']) > 6) and (course['course_code'][5] == 'X') and (course['course_code'][2] == '1'  or (course['course_code'][2] == '2')):
                            exjobb_courses.append(course)

              course_list=exjobb_courses

       if len(course_list) == 0:
              print("No courses to process")
              sys.exit()

       # create a dictionary so one can lookup course details by course id
       course_dict=dict()
       for course in course_list:
              course_dict[course['id']]=course

       list_of_course_ids=[]
       for course in course_list:
              enrolments=course['enrollments']
              for e in enrolments:
                     if e['user_id'] == user_id:
                            if (e['role'] == 'TeacherEnrollment') or (e['role'] == 'Examiner') or (e['role'] == 'TaEnrollment'):
                                   # only put the course into the list once
                                   if not course['id'] in list_of_course_ids:
                                          list_of_course_ids.append(course['id'])

       if len(list_of_course_ids) == 0:
              print("user is not a teacher or examiner in any courses")
              sys.exit()



       if Verbose_Flag:
              print("courses where user is teacher or examiner={}".format(list_of_course_ids))

       for c_id in list_of_course_ids:
              # first check to see if this is a course that should be without specific sections
              c1=courses_without_specific_sections.get(str(c_id), [])
              if c1:
                     print("course {0} indicated as having no specific sections".format(c_id))
                     continue

              # if there is exsiting explicit sections, then do not add additional sections
              c2=courses_with_sections.get(str(c_id), [])
              if c2:
                     s0=courses_with_sections[str(c_id)].get('sections', [])
                     if s0 and type(dict) == 'dict': # s0 will be a dict
                            continue

              # otherwise add the section information
              sections=sections_in_course(c_id)

              if sections:
                     courses_with_sections[c_id]={'name':  course_dict[c_id]['name'],
                                                  'course_code':  course_dict[c_id]['course_code'],
                                                  'sections': dict()}
                     for s in sections:
                            courses_with_sections[c_id]['sections'][s['id']]=s['name']
              else:
                     c3=courses_without_specific_sections.get(c_id, [])
                     if not c3: # if not already in courses_without_specific_sections, then add it
                            courses_without_specific_sections[c_id]={'name':  course_dict[c_id]['name'],
                                                                     'course_code':  course_dict[c_id]['course_code']
                            }


       courses_with_sections=cleanup_sections(users_name, courses_with_sections)

       course_info['courses_to_ignore']=courses_to_ignore
       course_info['courses_without_specific_sections']=courses_without_specific_sections
       course_info['courses_with_sections']=courses_with_sections

       try:
              with open(course_info_file, 'w') as json_data_file:
                     json.dump(course_info, json_data_file)
                     print("created output file {}".format(course_info_file))
       except:
              print("Unable to write JSON file named {}".format(course_info_file))
              sys.exit()

if __name__ == "__main__": main()

