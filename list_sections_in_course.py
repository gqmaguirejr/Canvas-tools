#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# ./list_sections_in_course.py course_id
#
# Output:
#    outputs a spreadsheet of the section in a course as an xlsx file of the form: sections-in-189.xlsx
#     the second sheet "Students" lists students
#
# with the option "-v" or "--verbose" you get lots of output - showing in detail the operations of the program
#
# Extensive use is made of Python Pandas merge operations.
# Can also be called with an alternative configuration file:
# ./list_sections_in_course.py --config config-test.json
#
# Example:
# ./list_sections_in_course.py  11
#
# ./list_sections_in_course.py --config config-test.json 12683
#
# 
# G. Q. Maguire Jr.
#
# 2020.02.04
# based on earlier list_sections_in_course.py
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
              #while r.links['current']['url'] != r.links['last']['url']:  
              while r.links.get('next', False):
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
              #while r.links['current']['url'] != r.links['last']['url']:  
              while r.links.get('next', False):
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

       if (len(remainder) < 1):
              print("Insuffient arguments\n must provide course_id\n")
              return

       course_id=remainder[0]

       sections=sections_in_course(course_id)
       if Verbose_Flag:
              print("sections={0}".format(sections))
       sections_df=pd.json_normalize(sections)
       sections_df.rename(columns = {'id':'course_section_id', 'name':'section_name'}, inplace = True)
       columns_to_drop=['course_id', 'end_at', 'integration_id', 'nonxlist_course_id', 'sis_course_id', 'sis_section_id', 'start_at']
       sections_df.drop(columns_to_drop,inplace=True,axis=1)
       headers = sections_df.columns.tolist()
       if Verbose_Flag:
              print('sections_df columns: ', headers)
              
       students=students_in_course(course_id)
       if Verbose_Flag:
              print("students={0}".format(students))

       if students:
              students_df1=pd.json_normalize(students)
              headers = sections_df.columns.tolist()
              if Verbose_Flag:
                     print('sections_df columns: ', headers)

              if sections:      # if there are no sections, there is nothing to merge!
                     students_df = pd.merge(sections_df, students_df1, on='course_section_id')
              else:
                     students_df = students_df1

              columns_to_drop=['associated_user_id', 'course_integration_id', 'grades.current_grade', 'grades.current_score', 'grades.final_grade',
                               'grades.final_score', 'grades.html_url', 'html_url', 'start_at', 'user.integration_id' ]
              students_df.drop(columns_to_drop,inplace=True,axis=1)


       # the following was inspired by the section "Using XlsxWriter with Pandas" on http://xlsxwriter.readthedocs.io/working_with_pandas.html
       # set up the output write
       writer = pd.ExcelWriter('sections-in-'+str(course_id)+'.xlsx', engine='xlsxwriter')
       if sections:
              sections_df.to_excel(writer, sheet_name='Sections')
       if students:
              students_df.to_excel(writer, sheet_name='Students')

       # Close the Pandas Excel writer and output the Excel file.
       writer.save()

if __name__ == "__main__": main()

