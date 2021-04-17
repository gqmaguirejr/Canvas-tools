#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# ./set_status_in_course.py course_id status_percent
#
# note the status_percent is simply treated as a string
#
# with the option '-C'or '--containers' use HTTP rather than HTTPS for access to Canvas
# with the option -t' or '--testing' testing mode
#
# with the option "-v" or "--verbose" you get lots of output - showing in detail the operations of the program
#
# Can also be called with an alternative configuration file:
# ./custom-data-for-users-in-course.py --config config-test.json
#
# Example:
# ./set_status_in_course.py 11 22
#
# ./set_status_in_course.py --config config-test.json 11 23.5
# example output:
# Existing custom data for user for course 11 is {'data': '21.5'}
# Result of setting custom data for user for course 11 is {'data': '23.5'}
#
#
# ./set_status_in_course.py -C 5 11 23.7
#
# G. Q. Maguire Jr.
#
# 2021-04-17
# based on earlier custom-data-for-users-in-course.py
#

import requests, time
import pprint
import optparse
import sys
import json

from bs4 import BeautifulSoup

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

def put_user_custom_data_by_user_id(user_id, name_space, scope, data):
    # Use the Canvas API to set a user's custom data
    # PUT /api/v1/users/:user_id/custom_data(/*scope)
    if scope:
        url = "{0}/users/{1}/custom_data/{2}".format(baseUrl, user_id, scope)
    else:
        url = "{0}/users/{1}/custom_data".format(baseUrl, user_id)
    if Verbose_Flag:
        print("url: {}".format(url))

    payload={'ns': name_space,
             'data': data
    }
    r = requests.put(url, headers = header, json=payload)
    if Verbose_Flag:
        print("result of setting custom data: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        page_response=r.json()
        return page_response
    return []

def get_user_custom_data_by_user_id(user_id, name_space, scope):
    # Use the Canvas API to get a user's custom data
    # GET /api/v1/users/:user_id/custom_data(/*scope)
    if scope:
        url = "{0}/users/{1}/custom_data/{2}".format(baseUrl, user_id, scope)
    else:
        url = "{0}/users/{1}/custom_data".format(baseUrl, user_id)
    if Verbose_Flag:
        print("url: {}".format(url))

    payload={'ns': name_space }

    r = requests.get(url, headers = header, json=payload)
    if Verbose_Flag:
        print("result of getting custom data: {}".format(r.text))

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
        print("Insuffient arguments - must provide account_id course_id status_percent\n")
        sys.exit()
              
    course_id=remainder[0]
    status_percent=remainder[1]

    user_id='self'
        
    result1=get_user_custom_data_by_user_id(user_id, 'se.kth.canvas-app.status_'+course_id,[])
    print("Existing custom data for user for course {0} is {1}".format(course_id, result1))

    result2=put_user_custom_data_by_user_id(user_id, 'se.kth.canvas-app.status_'+course_id, [], status_percent)
    print("Result of setting custom data for user for course {0} is {1}".format(course_id, result2))


if __name__ == "__main__": main()

