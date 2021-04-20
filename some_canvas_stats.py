#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -*- mode: python; python-indent-offset: 4 -*-
#
# some_canvas_stats.py
#
# Example:
# ./some_canvas_stats.py
#
# The program get the list of accounts that this user can get data about, then for each of them gets the number of users and calculates the distinct users (i.e., the number of distinct users)
# The program also get he list of course in each account and for each course gets the name of the course, the number of students in the course, the number of enrollments in the course, and the number of sections in the course - also the min, max, and median number of sections a student is in
# For each course it also reports on the number of assignments
#  
# The information is output as sheets in a a spreadsheet: Accounts, Per Account, Per Course
#
# 2021-04-19 G. Q. Maguire Jr.
#
import re
import sys

import json
import argparse
import os			# to make OS calls, here to get time zone info

import requests, time

# Use Python Pandas to create XLSX files
import pandas as pd

import pprint

import isodate                  # for parsing ISO 8601 dates and times
import pytz                     # for time zones
from dateutil.tz import tzlocal

def utc_to_local(utc_dt):
    return utc_dt.replace(tzinfo=datetime.timezone.utc).astimezone(tz=None)

def datetime_to_local_string(canvas_time):
    global Use_local_time_for_output_flag
    t1=isodate.parse_datetime(canvas_time)
    if Use_local_time_for_output_flag:
        t2=t1.astimezone()
        return t2.strftime("%Y-%m-%d %H:%M")
    else:
        return t1.strftime("%Y-%m-%d %H:%M")



#############################
###### EDIT THIS STUFF ######
#############################

global baseUrl	# the base URL used for access to Canvas
global header	# the header for all HTML requests
global payload	# place to store additionally payload when needed for options to HTML requests

# Based upon the options to the program, initialize the variables used to access Canvas gia HTML requests
def initialize(args):
    global baseUrl, header, payload

    # styled based upon https://martin-thoma.com/configuration-files-in-python/
    config_file=args["config"]

    try:
        with open(config_file) as json_data_file:
            configuration = json.load(json_data_file)
            access_token=configuration["canvas"]["access_token"]

            if args["containers"]:
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

# Canvas API related functions
def list_of_accounts():
    global Verbose_Flag
    global course_id
    
    entries_found_thus_far=[]

    # Use the Canvas API to get the list of accounts this user can see
    # GET /api/v1/accounts
    url = "{0}/accounts".format(baseUrl)
    if Verbose_Flag:
        print("url: {}".format(url))

    extra_parameters={'per_page': '100'}
    r = requests.get(url, params=extra_parameters, headers = header)

    if Verbose_Flag:
        print("result of getting accounts: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        page_response=r.json()

        for p_response in page_response:  
            entries_found_thus_far.append(p_response)

        # the following is needed when the reponse has been paginated
        # i.e., when the response is split into pieces - each returning only some of the list of modules
        # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
        while r.links.get('next', False):
            r = requests.get(r.links['next']['url'], headers=header)  
            if Verbose_Flag:
                print("result of getting accounts for a paginated response: {}".format(r.text))
            page_response = r.json()  
            for p_response in page_response:  
                entries_found_thus_far.append(p_response)

    return entries_found_thus_far

def list_of_subaccounts(account_id):
    global Verbose_Flag
    global course_id
    
    entries_found_thus_far=[]

    #Get the sub-accounts of an accountAccountsController#sub_accounts
    #GET /api/v1/accounts/:account_id/sub_accounts
    url = "{0}/accounts/{1}//sub_accounts".format(baseUrl, account_id)
    if Verbose_Flag:
        print("url: {}".format(url))

    extra_parameters={'per_page': '100'}
    r = requests.get(url, params=extra_parameters, headers = header)

    if Verbose_Flag:
        print("result of getting accounts: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        page_response=r.json()

        for p_response in page_response:  
            entries_found_thus_far.append(p_response)

        # the following is needed when the reponse has been paginated
        # i.e., when the response is split into pieces - each returning only some of the list of modules
        # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
        while r.links.get('next', False):
            r = requests.get(r.links['next']['url'], headers=header)  
            if Verbose_Flag:
                print("result of getting accounts for a paginated response: {}".format(r.text))
            page_response = r.json()  
            for p_response in page_response:  
                entries_found_thus_far.append(p_response)

    return entries_found_thus_far


def users_in_account(account_id):
    global Verbose_Flag
    global course_id
    
    entries_found_thus_far=[]

    # Use the Canvas API to get the list of users known to the system
    # GET /api/v1/accounts/:account_id/users
    url = "{0}/accounts/{1}/users".format(baseUrl, account_id)
    if Verbose_Flag:
        print("url: {}".format(url))

    extra_parameters={'per_page': '100'}
    r = requests.get(url, params=extra_parameters, headers = header)

    if Verbose_Flag:
        print("result of getting gradebook feed: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        page_response=r.json()

        for p_response in page_response:  
            entries_found_thus_far.append(p_response)

        # the following is needed when the reponse has been paginated
        # i.e., when the response is split into pieces - each returning only some of the list of modules
        # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
        while r.links.get('next', False):
            r = requests.get(r.links['next']['url'], headers=header)  
            if Verbose_Flag:
                print("result of getting useers in an account for a paginated response: {}".format(r.text))
            page_response = r.json()  
            for p_response in page_response:  
                entries_found_thus_far.append(p_response)

    return entries_found_thus_far

def main(argv):
    global Verbose_Flag
    global Use_local_time_for_output_flag

    Use_local_time_for_output_flag=True

    timestamp_regex = r'(2[0-3]|[01][0-9]|[0-9]):([0-5][0-9]|[0-9]):([0-5][0-9]|[0-9])'

    argp = argparse.ArgumentParser(description="II2202-grades_to_report.py: look for students who have passed the 4 assignments and need a grade assigned")

    argp.add_argument('-v', '--verbose', required=False,
                      default=False,
                      action="store_true",
                      help="Print lots of output to stdout")

    argp.add_argument("--config", type=str, default='config.json',
                      help="read configuration from file")

    argp.add_argument('-C', '--containers',
                      default=False,
                      action="store_true",
                      help="for the container enviroment in the virtual machine, uses http and not https")

    args = vars(argp.parse_args(argv))

    Verbose_Flag=args["verbose"]

    initialize(args)
    if Verbose_Flag:
        print("baseUrl={}".format(baseUrl))

    # the following was inspired by the section "Using XlsxWriter with Pandas" on http://xlsxwriter.readthedocs.io/working_with_pandas.html
    # set up the output write
    writer = pd.ExcelWriter('canvas_stats.xlsx', engine='xlsxwriter')

    accounts=list_of_accounts()
    if Verbose_Flag:
        print("accounts={0}".format(accounts))

    accounts_df=pd.json_normalize(accounts)
    accounts_df.to_excel(writer, sheet_name='accounts')

    all_subaccounts=[]
    for a in accounts:
        subaccount_info=list_of_subaccounts(a['id'])
        if subaccount_info:
            all_subaccounts.append()

    if Verbose_Flag:
        print("all_subaccounts={0}".format(all_subaccounts))
    
    if len(all_subaccounts) > 0:
        all_subaccounts_df=pd.json_normalize(all_subaccounts)
        all_subaccounts_df.to_excel(writer, sheet_name='subaccounts')
    else:
        print("No subaccounts")

    users_per_account=dict()
    count_users_per_account=[]
    unique_users=set()
    for a in accounts:
        users_per_account[a['id']]=users_in_account(a['id'])
        count_users_per_account.append(
            {
                'account_id': a['id'],
                'account_name': a['name'],
                'count':      len(users_per_account[a['id']])
            }
        )
        for u in users_per_account:
            for u1 in users_per_account[u]:
               unique_users.add(u1['id'])
        
    print("len unique_users={0}".format(len(unique_users)))

    
    count_users_per_account_df=pd.json_normalize(count_users_per_account)
    count_users_per_account_df.to_excel(writer, sheet_name='per account')


    #print("course_id={}".format(course_id))

    #assignments=list_assignments()
    #if Verbose_Flag:
    #    print("assignments={0}".format(assignments))

    # Close the Pandas Excel writer and output the Excel file.
    writer.save()


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

