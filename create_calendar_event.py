#!/usr/bin/python3
#
# ./create_calendar_event.py user_id date title description
#
# The dates from Canvas are in ISO 8601 format.
# Therefore I have used start_date and end_date in UTC, so that (except for the logging operation)
# all datetimes are in UTC
# and output in local time format if the Use_local_time_for_output_flag is True (the default).
# 
# with the option '-C'or '--containers' use HTTP rather than HTTPS for access to Canvas
# with the option "-v" or "--verbose" you get lots of output - showing in detail the operations of the program
#
# Can also be called with an alternative configuration file:
# ./create_fake_users-in-course.py --config config-test.json
#
#
# G. Q. Maguire Jr.
#
# Based on the 2017 version of list_my_calendar_events.py
#
# 2019.03.05
#

import csv, requests, time
from pprint import pprint
import optparse
import sys

from io import StringIO, BytesIO

#from lxml import html

import json

# Use Python Pandas to create XLSX files
import pandas as pd

import datetime
import isodate                  # for parsing ISO 8601 dates and times
import pytz                     # for time zones
import os                       # to make OS calls, here to get time zone info
from dateutil.tz import tzlocal

def utc_to_local(utc_dt):
    return utc_dt.replace(tzinfo=datetime.timezone.utc).astimezone(tz=None)

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

def convert_to_local_times(input_df, list_of_columns_to_convert):
    global Use_local_time_for_output_flag

    for c in list_of_columns_to_convert:
        working_list=[]
        for row in input_df[c]:
            if row is None:
                working_list.append("")
            else:
                t1=isodate.parse_datetime(row)
                if Use_local_time_for_output_flag:
                    t2=t1.astimezone()
                    working_list.append(t2.strftime("%Y-%m-%d %H:%M"))
                else:
                    working_list.append(t1.strftime("%Y-%m-%d %H:%M"))
        input_df['local_'+c]=working_list

def create_calendar_event(user_id, cal_date, title, description):
    # Use the Canvas API to get the calendar event
    # POST /api/v1/calendar_events
    url = "{0}/calendar_events".format(baseUrl)
    if Verbose_Flag:
        print("url: " + url)

    context_code="user_{}".format(user_id)
    #context_code="course_{}".format(user_id)
    print("context_code={}".format(context_code))
    date_time_start=datetime.datetime.strptime(cal_date, "%Y-%m-%d")
    date_time_end=date_time_start
    print("date_time_start is {}".format(date_time_start))

    payload={'calendar_event[context_code]': context_code,
             'calendar_event[title]': title,
             'calendar_event[description]': description,
             'calendar_event[start_at]': date_time_start,
             'calendar_event[end_at]':   date_time_end
    }
    r = requests.post(url, headers = header, data=payload)
    if Verbose_Flag:
        print("result of creating a calendar event: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        page_response=r.json()
        return page_response
    else:
        print("status code={}".format(r.status_code))
    return None
    
def get_calendar_event(calendar_event_id):
       # Use the Canvas API to get the calendar event
       #GET /api/v1/calendar_events/:id
       url = "{0}/calendar_events/{1}".format(baseUrl, calendar_event_id)
       if Verbose_Flag:
              print("url: " + url)

       r = requests.get(url, headers = header)
       if Verbose_Flag:
              print("result of getting a single calendar event: {}".format(r.text))

       if r.status_code == requests.codes.ok:
              page_response=r.json()
              return page_response

       return None


def get_calendar_events_for_user(user_id):
    appointments_found_thus_far=[]
    # Use the Canvas API to get the user's calendar event
    # GET /api/v1/users/:user_id/calendar_events
    url = "{0}/users/{1}".format(baseUrl, user_id)
    url =  url + '/calendar_events'
    if Verbose_Flag:
        print("url: " + url)

    r = requests.get(url, headers = header)
    if Verbose_Flag:
        print("result of getting a user's calendar events: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        page_response=r.json()
    else:
        return appointments_found_thus_far

    for p_response in page_response:  
        if p_response['start_at'] is not None:
            if (isodate.parse_datetime(p_response['start_at']) >= start_date) and (isodate.parse_datetime(p_response['start_at']) <= end_date):
                appointments_found_thus_far.append(p_response)
        else:
            appointments_found_thus_far.append(p_response)

    # the following is needed when the reponse has been paginated
    # i.e., when the response is split into pieces - each returning only some of the list of modules
    # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
    if 'link' in r.headers:
        while r.links['current']['url'] != r.links['last']['url']:  
            r = requests.get(r.links['next']['url'], headers=header)  
            page_response = r.json()  
            for p_response in page_response:  
                if p_response['start_at'] is not None:
                    if (isodate.parse_datetime(p_response['start_at']) >= start_date) and (isodate.parse_datetime(p_response['end_at']) <= end_date):
                        appointments_found_thus_far.append(p_response)
                else:
                    appointments_found_thus_far.append(p_response)

        return appointments_found_thus_far

    return None

def main():
    global Verbose_Flag
    global Use_local_time_for_output_flag

    Use_local_time_for_output_flag=True

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

    if (len(remainder) >= 4):
        user_id = remainder[0]
        date = remainder[1]
        title = remainder[2]
        description = remainder[3]
    else:
        user_id = "self"

    create_calendar_event(user_id, date, title, description)

if __name__ == "__main__": main()
