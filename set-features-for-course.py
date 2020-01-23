#!/usr/bin/python3
#
# ./set-features-for-course.py  course_id feature state
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


def set_features_for_course(course_id, feature, state):
    # PUT /api/v1/courses/:course_id/features/flags/:feature    
    url = "{0}/courses/{1}/features/flags/{2}".format(baseUrl, course_id, feature)
    if Verbose_Flag:
        print("url: {}".format(url))

    payload={'state': state }
    r = requests.put(url, headers = header, json=payload)
    if Verbose_Flag:
        print("result of setting feature: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        page_response=r.json()
        return page_response
    return []

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

    if (len(remainder) < 3):
        print("Insuffient arguments - must provide course_id feature state")
    else:
        course_id=remainder[0]
        feature=remainder[1]
        state=remainder[2]
        existing_features=list_features_for_course(course_id)
        for f in existing_features:
            if f['feature'] == feature:
                if f['feature_flag']['locked']:
                    print("feature {0} is locked".format(feature))
                    return
                # here the feature exists and is unlocked
                if f['feature_flag']['state'] == state:
                    print("feature {0} is already set".format(feature))
                    return
                # check if transition is allowed
                if f['feature_flag']['transitions'][state]['locked'] == False:
                    # here it is time to set the state
                    output=set_features_for_course(course_id, feature, state)
                    if (output):
                        pprint(output)

if __name__ == "__main__": main()

