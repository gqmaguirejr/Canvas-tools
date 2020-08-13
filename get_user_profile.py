#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# ./get_user_profile.py user_id
#
# outputs user̈́s profile in JSON
#
# with the option "-v" or "--verbose" you get lots of output - showing in detail the operations of the program
#
# Can also be called with an alternative configuration file:
# ./list_your_courses.py --config config-test.json
#
# Example:
# ./get_user_profile.py 29
#
# ./get_user_profile.py --config config-test.json 29
#
# G. Q. Maguire Jr.
#
# based on earlier my-files.py
#
# 2020.08.13
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


def get_user_profile(user_id):
    # Use the Canvas API to get the user's profile
    #GET /api/v1/users/:user_id/profile

    url = "{0}/users/{1}/profile".format(baseUrl, user_id)
    if Verbose_Flag:
        print("url: {}".format(url))

    r = requests.get(url, headers = header)
    if Verbose_Flag:
        print("result of getting user profile: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        page_response=r.json()
        return page_response

    return None


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

    if (len(remainder) < 1):
        print("Insuffient arguments\n must provide user_id\n")
        return
    
    user_id=remainder[0]

    output=get_user_profile(user_id)

    if output and len(output) > 0:
        print("user's profile is:\n")
        pprint.pprint(output, indent=4)

if __name__ == "__main__": main()
