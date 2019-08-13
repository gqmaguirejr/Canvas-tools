#!/usr/bin/python3
#
# ./list-custom-columns.py  course_id
# 
# G. Q. Maguire Jr.
#
# 2019.08.13 based on earlier list-custom-columns.py
#

import csv, requests, time
from pprint import pprint
import optparse
import sys

from io import StringIO, BytesIO

from lxml import html

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

def list_custom_columns(course_id):
       columns_found_thus_far=[]

       # Use the Canvas API to get the list of custom column for this course
       #GET /api/v1/courses/:course_id/custom_gradebook_columns

       url = "{0}/courses/{1}/custom_gradebook_columns".format(baseUrl,course_id)
       if Verbose_Flag:
              print("url: " + url)

       r = requests.get(url, headers = header)

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
              print("Inusffient arguments\n must provide course_id\n")
       else:
              course_id=remainder[0]
              output=list_custom_columns(course_id)
              if (output):
                     print(output)

if __name__ == "__main__": main()

