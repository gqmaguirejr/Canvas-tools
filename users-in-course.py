#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# ./users-in-course.py course_id
#
# Output: XLSX spreadsheet with textual section names and URL to user's avatar
#
#
# with the option "-v" or "--verbose" you get lots of output - showing in detail the operations of the program
#
# Can also be called with an alternative configuration file:
# ./list_your_courses.py --config config-test.json
#
# Example:
# ./users-in-course.py 11
#
# ./users-in-course.py --config config-test.json 6434
#
# ./users-in-course.py --config config-test.json --avatar 6434
# 
# G. Q. Maguire Jr.
#
# based on earlier users-in-course.py that generated CSV files

# 2019.01.04
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
              while r.links['current']['url'] != r.links['last']['url']:  
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
              while r.links['current']['url'] != r.links['last']['url']:  
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
              while r.links['current']['url'] != r.links['last']['url']:  
                     r = requests.get(r.links['next']['url'], headers=header)  
                     if Verbose_Flag:
                            print("result of getting courses for a paginated response: {}".format(r.text))
                     page_response = r.json()  
                     for p_response in page_response:  
                            courses_found_thus_far.append(p_response)

       return courses_found_thus_far

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

       parser.add_option('-a', '--avatar',
                         dest="avatar",
                         default=False,
                         action="store_true",
                         help="include URL to avatar for each user"
       )

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
       else:
              course_id=remainder[0]
              users=users_in_course(course_id)
              if (users):
                     users_df=pd.io.json.json_normalize(users)
                     
                     # below are examples of some columns that might be dropped
                     columns_to_drop=['user.id', 'user.integration_id', 'section_integration_id', 'course_integration_id', 'associated_user_id']
                     users_df.drop(columns_to_drop,inplace=True,axis=1)

                     # the following was inspired by the section "Using XlsxWriter with Pandas" on http://xlsxwriter.readthedocs.io/working_with_pandas.html
                     # set up the output write
                     writer = pd.ExcelWriter('users-'+course_id+'.xlsx', engine='xlsxwriter')
                     #users_df.to_excel(writer, sheet_name='Users')
    
                     sections=sections_in_course(course_id)
                     sections_df=pd.io.json.json_normalize(sections)

                     if options.avatar:
                            users_avatars=dict() # to remember a user's avatar to avoid looking it up again

                     for index, row in  users_df.iterrows():
                            if Verbose_Flag:
                                   print("index: {0}, row[user_id]: {1}".format(index, row['user_id']))

                            user_id=row['user_id']
                            if Verbose_Flag:
                                   print("user_id: {}".format(user_id))

                            section_name=section_name_from_section_id(sections, row['course_section_id'])
                            users_df.at[index, 'Section_name']= section_name

                            if options.avatar:
                                   user_avatar=users_avatars.get(user_id, []) # have we already looked one up
                                   if not user_avatar:
                                          profiles=user_profile_url(user_id)
                                          if Verbose_Flag:
                                                 print("profiles: {}".format(profiles['avatar_url']))
                                          user_avatar=profiles['avatar_url']
                                          users_avatars[user_id]=user_avatar
                                   users_df.at[index, 'avatar_url']=user_avatar

                     users_df.to_excel(writer, sheet_name='Users')
                     sections_df.to_excel(writer, sheet_name='Sections')

                     # Close the Pandas Excel writer and output the Excel file.
                     writer.save()

if __name__ == "__main__": main()

