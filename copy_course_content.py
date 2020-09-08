#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# ./copy_course_content.py source_course_id destination_course_id
#
# copies course content from source to destination course_id
#
# Output: status updates
#
#
# with the option "-v" or "--verbose" you get lots of output - showing in detail the operations of the program
#
# Can also be called with an alternative configuration file:
# ./list_your_courses.py --config config-test.json
#
# Example:
# ./copy_course_content.py 23939 751
#
# ./copy_course_content.py  --config config-test.json 23939 751
#
# 
# G. Q. Maguire Jr.
#
# based on posting https://community.canvaslms.com/t5/Developers-Group/Use-the-Content-Migration-API-to-copy-courses-but-without-their/m-p/158208#M4203
#
# 2020.09.08
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

def migrateContents(old_course, new_course):
    # Use the Canvas API to get migrate contents
    # POST /api/v1/courses/:course_id/content_migrations
    payload={'migration_type':'course_copy_importer',
	     'settings[source_course_id]': str(old_course),
	     'date_shift_options[remove_dates]':'True',
	     'copy[all_course_settings]':'1',
	     'copy[all_syllabus_body]':'1',
	     'copy[all_context_modules]':'1',
	     'copy[all_assignments]':'1',
	     'copy[all_quizzes]':'1',
	     'copy[all_assessment_question_banks]':'1',
	     'copy[all_discussion_topics]':'1',
	     'copy[all_wiki_pages]':'1',
	     'copy[all_context_external_tools]':'1',
	     'copy[all_rubrics]':'1',
	     'copy[all_attachments]':'1'}
    url = "{0}/courses/{1}/content_migrations".format(baseUrl, new_course)
    r = requests.post(url, params=payload, headers = header)
    data = r.json()
    print("response is {}".format(data))
    progress_url = data[u'progress_url']
    print("Migration URL is: {}".format(progress_url))
    progress = 0
    while progress != 100:
        progress_check = requests.get(progress_url, headers = header)
        progress_result = progress_check.json()
        print("Migration Status is: {0}  | progress: {1}" .format(data[u'workflow_state'], progress_result[u'completion']))
        #print(progress_result)
        progress = progress_result[u'completion']
        time.sleep(2)
        if progress_result[u'completion'] == 100:
            print("------------------------------")
            print("Migration completed.")
            break

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

    if (len(remainder) < 2):
        print("Insuffient arguments\n must provide source_course_id destination_course_id\n")
        return
    
    source_course_id=remainder[0]
    destination_course_id=remainder[1]

    migrateContents(source_course_id, destination_course_id)
    
if __name__ == "__main__": main()
