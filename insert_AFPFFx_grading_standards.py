#!/usr/bin/python3
#
# ./insert_AFPFFx_grading_standards.py -a account_id
# ./insert_AFPFFx_grading_standards.py    course_id
#
# Currently this is hard wired to generate and insert the two grading standard scales.
# Note that if the grading scale is already present, it does nothing unless the "-f" (force) flag is set.
# In the latter case it adds the grading scale.
#
# G. Q. Maguire Jr.
#
# 2019.02.04, based on earlier insert_UGS_grading_standards.py
#
# Test with
#  ./insert_AFPFFx_grading_standards.py -v 11
# ./insert_AFPFFx_grading_standards.py -v --config config-test.json 11
# 
#

import csv, requests, time
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


##############################################################################
## ONLY update the code below if you are experimenting with other API calls ##
##############################################################################

def create_grading_standard(course_or_account, id, name, scale):

    # Use the Canvas API to create an grading standard
    # POST /api/v1/accounts/:account_id/grading_standards
    # or
    # POST /api/v1/courses/:course_id/grading_standards

    # Request Parameters:
    #Parameter		        Type	Description
    # title	Required	string	 The title for the Grading Standard.
    # grading_scheme_entry[][name]	Required	string	The name for an entry value within a GradingStandard that describes the range of the value e.g. A-
    # grading_scheme_entry[][value]	Required	integer	 -The value for the name of the entry within a GradingStandard. The entry represents the lower bound of the range for the entry. This range includes the value up to the next entry in the GradingStandard, or 100 if there is no upper bound. The lowest value will have a lower bound range of 0. e.g. 93

    if course_or_account:
        url = "{0}/courses/{1}/grading_standards".format(baseUrl, id)
    else:
        url = "{0}/accounts/{1}/grading_standards".format(baseUrl, id)

    if Verbose_Flag:
       print("url: {}".format(url))

    payload={'title': name,
             'grading_scheme_entry': scale
    }
         
    if Verbose_Flag:
        print("payload={0}".format(payload))

    r = requests.post(url, headers = header, json=payload)
    if r.status_code == requests.codes.ok:
        page_response=r.json()
        print("inserted grading standard")
        return True
    return False

def get_grading_standards(course_or_account, id):
    global Verbose_Flag
    # Use the Canvas API to get a grading standard
    # GET /api/v1/accounts/:account_id/grading_standards
    # or
    # GET /api/v1/courses/:course_id/grading_standards

    # Request Parameters:
    #Parameter		        Type	Description

    if course_or_account:
        url = "{0}/courses/{1}/grading_standards".format(baseUrl, id)
    else:
        url = "{0}/accounts/{1}/grading_standards".format(baseUrl, id)

    if Verbose_Flag:
       print("url: " + url)

    r = requests.get(url, headers = header)
    if r.status_code == requests.codes.ok:
        page_response=r.json()
        return page_response
    return None


def main():
    global Verbose_Flag
    global Use_local_time_for_output_flag
    global Force_appointment_flag

    Use_local_time_for_output_flag=True

    parser = optparse.OptionParser()

    parser.add_option('-v', '--verbose',
                      dest="verbose",
                      default=False,
                      action="store_true",
                      help="Print lots of output to stdout"
    )

    parser.add_option('-a', '--account',
                      dest="account",
                      default=False,
                      action="store_true",
                      help="Apply grading scheme to indicated account"
    )

    parser.add_option('-f', '--force',
                      dest="force",
                      default=False,
                      action="store_true",
                      help="Replace existing grading scheme"
    )

    parser.add_option("--config", dest="config_filename",
                      help="read configuration from FILE", metavar="FILE")



    options, remainder = parser.parse_args()

    Verbose_Flag=options.verbose
    Force_Flag=options.force

    if Verbose_Flag:
        print('ARGV      :', sys.argv[1:])
        print('VERBOSE   :', options.verbose)
        print('REMAINING :', remainder)
        print("Configuration file : {}".format(options.config_filename))

    course_or_account=True
    if options.account:
        course_or_account=False
    else:
        course_or_account=True

    if Verbose_Flag:
        print("Course or account {0}: course_or_account = {1}".format(options.account,
                                                                      course_or_account))

    if (len(remainder) < 1):
        print("Insuffient arguments must provide a course_id or account_id\n")
        return

    initialize(options)

    canvas_course_id=remainder[0]
    if Verbose_Flag:
        if course_or_account:
            print("course_id={0}".format(canvas_course_id))
        else:
            print("account_id={0}".format(canvas_course_id))

    canvas_grading_standards=dict()
    available_grading_standards=get_grading_standards(True, canvas_course_id)
    if available_grading_standards:
        for s in available_grading_standards:
            old_id=canvas_grading_standards.get(s['title'], None)
            if old_id and s['id'] < old_id: # use only the highest numbered instance of each scale
                continue
            else: 
                canvas_grading_standards[s['title']]=s['id']
                if Verbose_Flag:
                    print("title={0} for id={1}".format(s['title'], s['id']))

    if Verbose_Flag:
        print("canvas_grading_standards={}".format(canvas_grading_standards))

    potential_grading_standard_id=canvas_grading_standards.get('AFFx', None)
    if Force_Flag or (not potential_grading_standard_id):
        name='AFFx'
        scale=[
            {
                "name": "A",
                "value": 90
            },
            {
                "name": "B",
                "value": 80
            },
            {
                "name": "C",
                "value": 70
            },
            {
                "name": "D",
                "value": 60
            },
            {
                "name": "E",
                "value": 50
            },
            {
                "name": "Fx",
                "value": 10
            },
            {
                "name": "F",
                "value": 0
            },
        ]
        status=create_grading_standard(course_or_account, canvas_course_id, name, scale)
        if Verbose_Flag and status:
            print("Create new AFFx grading scale")

    potential_grading_standard_id=canvas_grading_standards.get('P/FFx', None)
    if Force_Flag or (not potential_grading_standard_id):
        name='P/FFx'
        scale=[
            {
                "name": "P",
                "value": 1
            },
            {
                "name": "Fx",
                "value": 0.1
            },
            {
                "name": "F",
                "value": 0
            },
        ]
        status=create_grading_standard(course_or_account, canvas_course_id, name, scale)
        if Verbose_Flag and status:
            print("Create new P/FFx grading scale")


if __name__ == "__main__": main()
