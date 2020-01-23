#!/usr/bin/python3
#
# ./list-features-for-course.py  course_id
# 
# outputs a list of features for the given course_id
#
# with the option '-C'or '--containers' use HTTP rather than HTTPS for access to Canvas
# with the option "-v" or "--verbose" you get lots of output - showing in detail the operations of the program
#
# Can also be called with an alternative configuration file:
# ./create_fake_users-in-course.py --config config-test.json
#
# Example:
# ./list-features-for-course.py 4
#
# ./list-features-for-course.py --config config-test.json 4
#
# ./list-features-for-course.py -C 5
#
#
# G. Q. Maguire Jr.
#
# 2020.01.23 based on the earlier list-external-tools-for-course.py
#

import csv, requests, time
from pprint import pprint
import optparse
import sys

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


#modules_csv = 'modules.csv' # name of file storing module names
log_file = 'log.txt' # a log file. it will log things


def details_of_external_tools_for_course(course_id, external_tool_id):
    # Use the Canvas API to GET the tool's detailed information
    # GET /api/v1/courses/:course_id/external_tools/:external_tool_id
    # GET /api/v1/accounts/:account_id/external_tools/:external_tool_id

    url = "{0}/courses/{1}/external_tools/{2}".format(baseUrl, course_id, external_tool_id)
    if Verbose_Flag:
        print(url)
    payload={}
    r = requests.get(url, headers = header, data=payload)
    if r.status_code == requests.codes.ok:
        tool_response = r.json()  
        pprint(tool_response)
        return tool_response
    else:
        print("No details for tool_id {1} for course_id: {2}".format(external_tool_id, course_id))
        return False

def list_external_tools_for_course(course_id):
    list_of_all_tools=[]
    # Use the Canvas API to get the list of external tools for this course
    # GET /api/v1/courses/:course_id/external_tools
    # GET /api/v1/accounts/:account_id/external_tools
    # GET /api/v1/groups/:group_id/external_tools

    url = "{0}/courses/{1}/external_tools".format(baseUrl, course_id)
    if Verbose_Flag:
        print("url: " + url)

    r = requests.get(url, headers = header)
    if Verbose_Flag:
        print("result of getting list of external tools: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        tool_response=r.json()
    else:
        print("No external tools for course_id: {}".format(course_id))
        return False


    for t_response in tool_response:  
        list_of_all_tools.append(t_response)

        # the following is needed when the reponse has been paginated
        # i.e., when the response is split into pieces - each returning only some of the list of modules
        # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
        while r.links['current']['url'] != r.links['last']['url']:  
            r = requests.get(r.links['next']['url'], headers=header)  
            tool_response = r.json()  
            for t_response in tool_response:  
                list_of_all_tools.append(t_response)

    return list_of_all_tools

def list_features_for_course(course_id):
    list_of_all_features=[]
    # Use the Canvas API to get the list of external tools for this course
    # GET /api/v1/courses/:course_id/features
    url = "{0}/courses/{1}/features".format(baseUrl, course_id)
    if Verbose_Flag:
        print("url: " + url)

    r = requests.get(url, headers = header)
    if Verbose_Flag:
        print("result of getting list of features: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        tool_response=r.json()
    else:
        print("No features for course_id: {}".format(course_id))
        return False


    for t_response in tool_response:  
        list_of_all_features.append(t_response)

        # the following is needed when the reponse has been paginated
        # i.e., when the response is split into pieces - each returning only some of the list of modules
        # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
        while r.links['current']['url'] != r.links['last']['url']:  
            r = requests.get(r.links['next']['url'], headers=header)  
            response = r.json()  
            for f_response in response:  
                list_of_all_features.append(f_response)

    return list_of_all_features



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

    parser.add_option('-t', '--testing',
                      dest="testing",
                      default=False,
                      action="store_true",
                      help="execute test code"
    )

    parser.add_option('-C', '--containers',
                      dest="containers",
                      default=False,
                      action="store_true",
                      help="for the container enviroment in the virtual machine"
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
        print("Insuffient arguments - must provide course_id")
    else:
        course_id=remainder[0]
        output=list_features_for_course(course_id)
        if (output):
            pprint(output)

if __name__ == "__main__": main()

