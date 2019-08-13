#!/usr/bin/python3
#
# ./insert-column.py  course_id column_name
# 
# G. Q. Maguire Jr.
#
# 2019.08.13 based on earlier insert-column.py
#

import csv, requests, time
from pprint import pprint
import optparse
import sys

from io import StringIO, BytesIO

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

##############################################################################
## ONLY update the code below if you are experimenting with other API calls ##
##############################################################################

def write_to_log(message):

       with open(log_file, 'a') as log:
              log.write(message + "\n")
              pprint(message)

def insert_column_name(course_id, column_name):
       global Verbose_Flag

       # Use the Canvas API to Create a custom gradebook column
       # POST /api/v1/courses/:course_id/custom_gradebook_columns
       #   Create a custom gradebook column
       # Request Parameters:
       #Parameter		Type	Description
       #column[title]	Required	string	no description
       #column[position]		integer	The position of the column relative to other custom columns
       #column[hidden]		boolean	Hidden columns are not displayed in the gradebook
       # column[teacher_notes]		boolean	 Set this if the column is created by a teacher. The gradebook only supports one teacher_notes column.

       url = "{0}/courses/{1}/custom_gradebook_columns".format(baseUrl,course_id)
       if Verbose_Flag:
              print("url: {}".format(url))
       payload={'column[title]': column_name}
       r = requests.post(url, headers = header, data=payload)
       if r.status_code == requests.codes.ok:
              if Verbose_Flag:
                     print("result of post creating custom column:  {}".format(r.text))
              page_response=r.json()
              print("inserted column")
              return True
       return False

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

       if (len(remainder) < 2):
              print("Inusffient arguments\n must provide course_id custom_column_name\n")
       else:
              output=insert_column_name(remainder[0], remainder[1])
              if (output):
                     print(output)

if __name__ == "__main__": main()

