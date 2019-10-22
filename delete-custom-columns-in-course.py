#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# ./delete-custom-columns-in-course.py course_id
#
# Output: XLSX spreadsheet with custom columns in course
#
# with the option "-a" or "--all" deletes all existing custom columns
# with the option "-v" or "--verbose" you get lots of output - showing in detail the operations of the program
#
# Can also be called with an alternative configuration file:
# ./list_your_courses.py --config config-test.json
#
# Example:
# ./delete-custom-columns-in-course.py 12683
#
# ./delete-custom-columns-in-course.py --config config-test.json 12683 1118
#
# 
# documentation about using xlsxwriter to insert images can be found at:
#   John McNamara, "Example: Inserting images into a worksheet", web page, 10 November 2018, https://xlsxwriter.readthedocs.io/example_images.html
#
# G. Q. Maguire Jr.
#
# based on earlier list-custom-columns.py
#
# 2019.01.07
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

def delete_custom_column_entries(course_id, column_id):
    global Verbose_Flag
    entries_found_thus_far=[]

    # Use the Canvas API to Delete a custom gradebook column
    #DELETE /api/v1/courses/:course_id/custom_gradebook_columns/:id
    
    url = "{0}/courses/{1}/custom_gradebook_columns/{2}".format(baseUrl, course_id, column_id)
    if Verbose_Flag:
        print("url: {}".format(url))

    r = requests.delete(url, headers = header)
    if Verbose_Flag:
        print("result of deleting custom_gradebook_column: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        page_response=r.json()
        return page_response
    return []

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
    
    parser.add_option('-a', '--all',
                      dest="all",
                      default=False,
                      action="store_true",
                      help="Delete all existing custom columns"
    )

    options, remainder = parser.parse_args()

    Verbose_Flag=options.verbose
    if Verbose_Flag:
        print("ARGV      : {}".format(sys.argv[1:]))
        print("VERBOSE   : {}".format(options.verbose))
        print("REMAINING : {}".format(remainder))
        print("Configuration file : {}".format(options.config_filename))

    initialize(options)

    if (len(remainder) < 2):
        print("Insuffient arguments - must provide course_id column_id\n")
    else:
        course_id=remainder[0]
        columns=list_custom_columns(course_id)
        if Verbose_Flag:
            print("columns={}".format(columns))
            
        if (len(remainder) > 1):
            column_id=remainder[1]
            print("column_id={}".format(column_id))
            
            if (columns):
                for c in columns:
                    if Verbose_Flag:
                        print("column is={0} with id={1}".format(c, c['id']))
                    if c['id'] == int(column_id): # note that the column id return in the list is an integer
                        if Verbose_Flag:
                            print("found matching column: {}".format(c))
                        delete_custom_column_entries(course_id, column_id)
        else:
            if (options.all) and columns:
                for c in columns:
                    delete_custom_column_entries(course_id, c['id'])

if __name__ == "__main__": main()

