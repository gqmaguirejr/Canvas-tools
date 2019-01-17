#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# ./my-files.py
#
# Output: XLSX spreadsheet of the files for the user running the program
# the file name is: all-my-files.xlsx
#
#
# with the option "-v" or "--verbose" you get lots of output - showing in detail the operations of the program
#
# Can also be called with an alternative configuration file:
# ./list_your_courses.py --config config-test.json
#
# Example:
# ./my-files.py
#
# ./my-files.py --config config-test.json 11
#
# for testing - skips some files:
# ./my-files.py -t 
#
# ./my-files.py -t --config config-test.json
# 
# documentation about using xlsxwriter to insert images can be found at:
#   John McNamara, "Example: Inserting images into a worksheet", web page, 10 November 2018, https://xlsxwriter.readthedocs.io/example_images.html
#
# G. Q. Maguire Jr.
#
# based on earlier my-files.py
#
# 2019.01.17
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

def list_your_courses():
    courses_found_thus_far=[]
    # Use the Canvas API to get the list of all of your courses
    # GET /api/v1/courses

    url = "{0}/courses".format(baseUrl)
    if Verbose_Flag:
        print("url: {}".format(url))

    extra_parameters={'per_page': '100'}
    r = requests.get(url, params=extra_parameters, headers = header)
    if Verbose_Flag:
        print("result of getting courses: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        page_response=r.json()

        for p_response in page_response:  
            courses_found_thus_far.append(p_response)

            # the following is needed when the reponse has been paginated
            # i.e., when the response is split into pieces - each returning only some of the list of courses
            # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
            while r.links['current']['url'] != r.links['last']['url']:  
                r = requests.get(r.links['next']['url'], headers=header)  
                if Verbose_Flag:
                    print("result of getting courses for a paginated response: {}".format(r.text))
                page_response = r.json()  
                for p_response in page_response:  
                    courses_found_thus_far.append(p_response)

    return courses_found_thus_far

def list_files(course_id):
    files_found_thus_far=[]
    # Use the Canvas API to get the list of files for the course
    #GET /api/v1/courses/:course_id/files

    url = "{0}/courses/{1}/files".format(baseUrl, course_id)
    if Verbose_Flag:
        print("url: {}".format(url))

    r = requests.get(url, headers = header)
    if Verbose_Flag:
        print("result of getting files: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        page_response=r.json()

        for p_response in page_response:  
            files_found_thus_far.append(p_response)

            # the following is needed when the reponse has been paginated
            # i.e., when the response is split into pieces - each returning only some of the list of files
            # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
            while r.links['current']['url'] != r.links['last']['url']:  
                r = requests.get(r.links['next']['url'], headers=header)  
                if Verbose_Flag:
                    print("result of getting files for a paginated response: {}".format(r.text))
                page_response = r.json()  
                for p_response in page_response:  
                    files_found_thus_far.append(p_response)

    return files_found_thus_far

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
    parser.add_option("--config", dest="config_filename",
                      help="read configuration from FILE", metavar="FILE")
    
    parser.add_option('-t', '--testing',
                      dest="testing",
                      default=False,
                      action="store_true",
                      help="testing mode for skipping files for some courses"
    )

    options, remainder = parser.parse_args()

    Verbose_Flag=options.verbose
    if Verbose_Flag:
        print("ARGV      : {}".format(sys.argv[1:]))
        print("VERBOSE   : {}".format(options.verbose))
        print("REMAINING : {}".format(remainder))
        print("Configuration file : {}".format(options.config_filename))

    initialize(options)

    courses=list_your_courses()              

    if not courses:
        print("You have no courses")
        sys.exit()

    # the following was inspired by the section "Using XlsxWriter with Pandas" on http://xlsxwriter.readthedocs.io/working_with_pandas.html
    # set up the output write
    writer = pd.ExcelWriter('all-my-files.xlsx', engine='xlsxwriter')

    courses_df=pd.io.json.json_normalize(courses)
    courses_df.to_excel(writer, sheet_name='Courses')

    for c in sorted(courses, key=lambda x: x['id']):
        course_id=int(c['id'])
        if options.testing and course_id in {8, 85, 152, 377, 751}: # skip these courses
            continue
        if course_id >= 1000: # skip files for course_id greater that this
               break
        print("course_id={0} name={1}".format(c['id'], c['name']))
        output=list_files(c['id'])
        print("number of files in course is {}".format(len(output)))
        if (output):
            # create a Panda dataframe from the output
            df=pd.io.json.json_normalize(output)
            # note that it is necessary to drop the thumbnail_urls as many exceed Excel's URL limit for the length of URLs
            columns_to_drop=['thumbnail_url']
            df.drop(columns_to_drop,inplace=True,axis=1)

            # Convert the dataframe to an XlsxWriter Excel object.
            sh_name="{0}".format(course_id)
            df.to_excel(writer, sheet_name=sh_name)
            # Close the Pandas Excel writer and output the Excel file.
    writer.save()

if __name__ == "__main__": main()
