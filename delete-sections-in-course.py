#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# ./delete-sections-in-course.py course_id [section_name]  [section_name]  [section_name] ...
#
# Output: none
#
# with the option "-v" or "--verbose" you get lots of output - showing in detail the operations of the program
#
# Can also be called with an alternative configuration file:
# ./create_sections_in_course.py --config config-test.json
#
# Example:
#
# ./delete-sections-in-course.py --config config-test.json 12683  16404
#
#
# G. Q. Maguire Jr.
#
# based on earlier create-sections-in-course.py
#
# 2019.01.08
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
                     print("status code: {0}, result of creating section: {1}".format(r.status_code, r.text))

              if r.status_code == requests.codes.ok:
                     page_response=r.json()

                     for p_response in page_response:  
                            sections_found_thus_far.append(p_response)

       return sections_found_thus_far

def delete_sections_by_id(section_id):
       sections_found_thus_far=[]
       # Use the Canvas API to create sections for this course
       #POST /api/v1/courses/:course_id/sections

       url = "{0}/sections/{1}".format(baseUrl, section_id)
       if Verbose_Flag:
              print("url: {}".format(url))

       r = requests.delete(url, headers = header)
       if Verbose_Flag:
              print("status code: {0}, result of deleting a section: {1}".format(r.status_code, r.text))

       if r.status_code == requests.codes.ok:
              page_response=r.json()

              for p_response in page_response:  
                     sections_found_thus_far.append(p_response)

       return sections_found_thus_far


def main():
       global Verbose_Flag

       default_picture_size=128

       parser = optparse.OptionParser()

       parser.add_option('-v', '--verbose',
                         dest="verbose",
                         default=False,
                         action="store_true",
                         help="Print lots of output to stdout"
       )

       parser.add_option('-a', '--all',
                         dest="all",
                         default=False,
                         action="store_true",
                         help="Delete all sections in the course"
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

       if (len(remainder) < 1) and options.all:
              print("Insuffient arguments - must provide course_id\n")
       else:
              print("Insuffient arguments - must provide course_id and at least one section name\n")

       course_id=remainder[0]

       # existing sections
       sections=sections_in_course(course_id)

       if options.all:
              for s in sections:
                     section_id=s['id']
                     section_name=s['name']
                     print("deleting section id={0} with name={1}".format(section_id, section_name))
                     delete_sections_by_id(section_id)
       else:
              for i in range(1, len(remainder)):
                     section_id=int(remainder[i])
                     for s in sections:
                            if s['id'] == section_id:
                                   section_name=s['name']
                                   print("deleting section id={0} with name={1}".format(section_id, section_name))
                                   delete_sections_by_id(section_id)

if __name__ == "__main__": main()

