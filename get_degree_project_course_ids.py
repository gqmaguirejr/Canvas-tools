#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# ./get_degree_project_course_ids.py
#
# Output: XLSX spreadsheet with degree course_id for courses in the accounts I can manage
#
#
# with the option "-v" or "--verbose" you get lots of output - showing in detail the operations of the program
#
# Can also be called with an alternative configuration file:
# ./list_your_courses.py --config config-test.json
#
# Example:
# ./get_degree_project_course_ids
# ./get_degree_project_course_ids --config config-test.json
#
# G. Q. Maguire Jr.
#
# 2022-12-11
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


def get_accounts_relevant_to_me():
    found_thus_far=[]
    # Use the Canvas API to get the list of acocunts I can view or manage
    #GET /api/v1/accounts

    url = "{0}/accounts".format(baseUrl)
    if Verbose_Flag:
        print("url: {}".format(url))

    r = requests.get(url, headers = header)
    if Verbose_Flag:
        print("result of getting accounts: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        page_response=r.json()

        for p_response in page_response:  
            found_thus_far.append(p_response)

            # the following is needed when the reponse has been paginated
            # i.e., when the response is split into pieces - each returning only some of the list of assignments
            # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
            while r.links.get('next', False):
                r = requests.get(r.links['next']['url'], headers=header)
                if Verbose_Flag:
                    print("result of getting accounts for a paginated response: {}".format(r.text))
                page_response = r.json()  
                for p_response in page_response:  
                    found_thus_far.append(p_response)

    return found_thus_far

def get_courses_in_account(account_id):
    found_thus_far=[]
    #List active courses in an accountAccountsController#courses_api
    #GET /api/v1/accounts/:account_id/courses

    url = "{0}/accounts/{1}/courses".format(baseUrl, account_id)
    if Verbose_Flag:
        print("url: {}".format(url))

    r = requests.get(url, headers = header)
    if Verbose_Flag:
        print("result of getting course for account: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        page_response=r.json()

        for p_response in page_response:  
            found_thus_far.append(p_response)

            # the following is needed when the reponse has been paginated
            # i.e., when the response is split into pieces - each returning only some of the list of assignments
            # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
            while r.links.get('next', False):
                r = requests.get(r.links['next']['url'], headers=header)
                if Verbose_Flag:
                    print("result of getting coures in an account a paginated response: {}".format(r.text))
                page_response = r.json()  
                for p_response in page_response:  
                    found_thus_far.append(p_response)

    return found_thus_far


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
    
    options, remainder = parser.parse_args()

    Verbose_Flag=options.verbose
    if Verbose_Flag:
        print("ARGV      : {}".format(sys.argv[1:]))
        print("VERBOSE   : {}".format(options.verbose))
        print("REMAINING : {}".format(remainder))
        print("Configuration file : {}".format(options.config_filename))

    initialize(options)

    # the following was inspired by the section "Using XlsxWriter with Pandas" on http://xlsxwriter.readthedocs.io/working_with_pandas.html
    # set up the output write
    writer = pd.ExcelWriter('accounts_I_can_manage.xlsx', engine='xlsxwriter')

    print("Getting data for all accounts I can view or manage\n")
    relevant_accounts=get_accounts_relevant_to_me()
    relevant_accounts_df=pd.json_normalize(relevant_accounts)
    relevant_accounts_df.to_excel(writer, sheet_name='Accounts')

    possible_degree_project_courses_ids=dict()
    for a in relevant_accounts:
        # skip sandboxes
        if a['name'].find("Sandbox") >= 0:
            continue
        print("Working on courses for account {0}: {1}".format(a['id'], a['name']))
        couses_in_account=get_courses_in_account(a['id'])
        courses_in_account_df=pd.json_normalize(couses_in_account)
        short_name="{}".format(a['id'])
        print("Writing sheet: {0}".format(short_name))
        courses_in_account_df.to_excel(writer, sheet_name=short_name)
        for idx, row in courses_in_account_df.iterrows():
            course_code=row['course_code']
            course_name=row['name']
            if (len(course_code) >= 5 and course_code[5] == 'X') or course_name.find("Degree Project") >= 0 or  course_name.find("Examensarbete") >= 0:
                possible_degree_project_courses_ids[course_code]={'id': row['id'], 'course_code': course_code, 'name': course_name}

    # Close the Pandas Excel writer and output the Excel file.
    writer.close()

    number_degree_project_courses=len(possible_degree_project_courses_ids)
    if  number_degree_project_courses > 0:
        print("There are {} possible degree project course rooms".format(number_degree_project_courses))
        for c in possible_degree_project_courses_ids:
            print("{0}, # {1}".format(possible_degree_project_courses_ids[c]['id'], c))

if __name__ == "__main__": main()

