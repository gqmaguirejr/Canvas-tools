#!/usr/bin/python3
# -*- coding: utf-8 -*-
# -*- mode: python; python-indent-offset: 4 -*-
#
# ./list_acounts_and_courses.py [school_code]
#
# Output:
#    outputs a spreadsheet of accounts and courses (potentially those with a given school_code)
#
# with the option "-v" or "--verbose" you get lots of output - showing in detail the operations of the program
#
# Extensive use is made of Python Pandas merge operations.
# Can also be called with an alternative configuration file:
#
# Example:
# ./list_acounts_and_courses.py
#
# ./list_acounts_and_courses.py EECS
#
# ./list_acounts_and_courses.py --config config-test.json 
#
# 
# G. Q. Maguire Jr.
#
# 2024-08-12
#

import csv, requests, time
from pprint import pprint
import optparse
import sys

from io import StringIO, BytesIO

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



##############################################################################
## ONLY update the code below if you are experimenting with other API calls ##
##############################################################################


def list_accounts():
    accounts_found_thus_far=[]
    # Use the Canvas API to get the list of accounts - I can access
    #GET /api/v1/accounts

    url = f"{baseUrl}/accounts"
    if Verbose_Flag:
       print("url: {}".format(url))

    extra_parameters={'per_page': '100',
                      'recursive': True,
                      'include[]': 'sub_account_count'
    }
    r = requests.get(url, params=extra_parameters, headers = header)
    if Verbose_Flag:
       print("result of getting acounts: {}".format(r.text))

    if r.status_code == requests.codes.ok:
       page_response=r.json()

       for p_response in page_response:  
           accounts_found_thus_far.append(p_response)

           # the following is needed when the reponse has been paginated
           # i.e., when the response is split into pieces - each returning only some of the list of modules
           # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
           #while r.links['current']['url'] != r.links['last']['url']:  
           while r.links.get('next', False):
              r = requests.get(r.links['next']['url'], headers=header)  
              page_response = r.json()  
              for p_response in page_response:  
                  accounts_found_thus_far.append(p_response)

    return accounts_found_thus_far


def list_accounts_recusively(account_id):
    accounts_found_thus_far=[]
    #List sub-accounts recursively
    #GET /v1/accounts/{account_id}/sub_accounts

    url = f"{baseUrl}/accounts/{account_id}/sub_accounts"
    if Verbose_Flag:
       print("url: {}".format(url))

    extra_parameters={'per_page': '100',
                      'recursive': True,
                      'include[]': 'course_count, sub_account_count'
    }
    r = requests.get(url, params=extra_parameters, headers = header)
    if Verbose_Flag:
       print("result of getting acounts recursively: {}".format(r.text))

    if r.status_code == requests.codes.ok:
       page_response=r.json()

       for p_response in page_response:  
           accounts_found_thus_far.append(p_response)

           # the following is needed when the reponse has been paginated
           # i.e., when the response is split into pieces - each returning only some of the list of modules
           # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
           #while r.links['current']['url'] != r.links['last']['url']:  
           while r.links.get('next', False):
              r = requests.get(r.links['next']['url'], headers=header)  
              page_response = r.json()  
              for p_response in page_response:  
                  accounts_found_thus_far.append(p_response)

    return accounts_found_thus_far


def list_courses_in_account(account_id):
    courses_found_thus_far=[]
    # Use the Canvas API to get the list of active courses in an account
    # GET /api/v1/accounts/:account_id/courses

    url = f"{baseUrl}/accounts/{account_id}/courses"
    if Verbose_Flag:
       print("url: {}".format(url))

    extra_parameters={'per_page': '100',
    }
    r = requests.get(url, params=extra_parameters, headers = header)
    if Verbose_Flag:
       print("result of getting acounts: {}".format(r.text))

    if r.status_code == requests.codes.ok:
       page_response=r.json()

       for p_response in page_response:  
           courses_found_thus_far.append(p_response)

           # the following is needed when the reponse has been paginated
           # i.e., when the response is split into pieces - each returning only some of the list of modules
           # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
           #while r.links['current']['url'] != r.links['last']['url']:  
           while r.links.get('next', False):
              r = requests.get(r.links['next']['url'], headers=header)  
              page_response = r.json()  
              for p_response in page_response:  
                  courses_found_thus_far.append(p_response)

    return courses_found_thus_far


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

    if (len(remainder) >= 1):
       school_code=remainder[0]
    else:
       school_code=False

    accounts=list_accounts()
    if Verbose_Flag:
       print(f"{accounts=}")

    for account in accounts:
       print(f'{account=}')
       if account['sub_account_count'] > 0:
           print(f"Getting information for subaccount of {account['id']}")
           sub_ccounts=list_accounts_recusively(account['id'])
           accounts.extend(sub_ccounts)

    accounts_df=pd.json_normalize(accounts)
    #sections_df.rename(columns = {'id':'course_section_id', 'name':'section_name'}, inplace = True)
    #columns_to_drop=['course_id', 'end_at', 'integration_id', 'nonxlist_course_id', 'sis_course_id', 'sis_section_id', 'start_at']
    #sections_df.drop(columns_to_drop,inplace=True,axis=1)

    headers = accounts_df.columns.tolist()
    if Verbose_Flag:
       print(f'{headers=}')
              
    # the following was inspired by the section "Using XlsxWriter with Pandas" on http://xlsxwriter.readthedocs.io/working_with_pandas.html
    # set up the output write
    if school_code:
       filename=f'accounts-me-{school_code}.xlsx'
    else:
       filename='accounts-me.xlsx'
    writer = pd.ExcelWriter(filename, engine='xlsxwriter')
    if accounts:
        accounts_df.to_excel(writer, sheet_name='Accounts')

    for account in accounts:
       if school_code:
           if not account['name'].startswith(school_code):
              continue
       print(f'getting courses for {account=}')
       courses=list_courses_in_account(account['id'])
       courses_df=pd.json_normalize(courses)
       s_name=f"{account['name']}"
       # Sheet names can be a maximum of 31 chaaracters, so truncate them to 30
       if len(s_name) > 30:
           s_name=s_name[0:29]
       courses_df.to_excel(writer, sheet_name=s_name)

    # Close the Pandas Excel writer and output the Excel file.
    writer.close()


if __name__ == "__main__": main()
