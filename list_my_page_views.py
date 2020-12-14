#!/usr/bin/python3
#
# ./list_my_page_views.py start_date end_date
#
# outputs a spreadsheet of appointments as an xlsx file of the form: page-views-user_id.xlsx
#
# The dates from Canvas are in ISO 8601 format.
# Therefore I have used start_date and end_date in UTC, so that (except for the logging operation) all datetimes are in UTC
# and output in local time format if the Use_local_time_for_output_flag is True (the default).
# 
# Use is made of Python Pandas
#
# Example:
# ./list_my_page_views.py 2020-12-01  2020-12-14
# ./list_my_page_views.py 2020-12-01 
#
# G. Q. Maguire Jr.
#
# 2020-12-14 based on earlier program of 2018.09.30
#

import csv, requests, time
from pprint import pprint
import optparse
import sys

from io import StringIO, BytesIO

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


def get_page_views(user_id, start_date, end_date):
    views_found_thus_far=[]

    # Use the Canvas API
    #GET /api/v1/users/:user_id/page_views
    url = "{0}/users/{1}/page_views".format(baseUrl,user_id)
    if Verbose_Flag:
        print("url: " + url)

    extra_parameters={'start_time': start_date, 'end_time': end_date, 'per_page': 100}
    r = requests.get(url, params=extra_parameters, headers = header)
    if Verbose_Flag:
        write_to_log("result of getting a user's page views: " + r.text)

    if r.status_code == requests.codes.ok:
        page_response=r.json()
        for p_response in page_response:  
            views_found_thus_far.append(p_response)

        # the following is needed when the reponse has been paginated
        # i.e., when the response is split into pieces - each returning only some of the list of modules
        # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
        #while r.links['current']['url'] != r.links['last']['url']:
        if Verbose_Flag:
            print("r.links={}".format(r.links))
        while r.links.get('next', False):
            r = requests.get(r.links['next']['url'], headers=header)  
            page_response = r.json()  
            if Verbose_Flag:
                print("got another page worth of views")
            for p_response in page_response:  
                views_found_thus_far.append(p_response)

    return views_found_thus_far

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

    user_id='self'

    # from amorphic Sep 2 '14 at 23:54 in http://stackoverflow.com/questions/2720319/python-figure-out-local-timezone
    my_tz_name = '/'.join(os.path.realpath('/etc/localtime').split('/')[-2:])
    my_tz = pytz.timezone(my_tz_name)

    if (len(remainder) == 2):
        start_date=datetime.datetime.combine(isodate.parse_date(remainder[0]), datetime.time.min).replace(tzinfo=my_tz)
        end_date=datetime.datetime.combine(isodate.parse_date(remainder[1]), datetime.time.min).replace(tzinfo=my_tz)
        output_file='page_views-'+str(user_id)+'-'+remainder[0]+'-'+remainder[1]+'.xlsx'
    elif (len(remainder) == 1):
        start_date=datetime.datetime.combine(isodate.parse_date(remainder[0]), datetime.time.min).replace(tzinfo=my_tz)
        end_date=datetime.datetime(3000, 1, 1, 0, 0, 0, 0).replace(tzinfo=my_tz)               # use 3000-01-01 as default end date to get "all" appointments
        output_file='page_views-'+str(user_id)+'-'+remainder[0]+'.xlsx'
    else:
        start_date=datetime.datetime(1900, 1, 1, 0, 0, 0, 0).replace(tzinfo=my_tz)             # use 1900-01-01 as default start date to get "all"
        end_date=datetime.datetime(3000, 1, 1, 0, 0, 0, 0).replace(tzinfo=my_tz)               # use 3000-01-01 as default end date to get "all"
        output_file='page_views-'+str(user_id)+'.xlsx'

    if Verbose_Flag:
        print("start date: ", start_date.isoformat())
        print("end date: ", end_date.isoformat())


    page_views=get_page_views(user_id, start_date, end_date)
    if Verbose_Flag:
        print("page_views={0}".format(page_views))

    page_views_df=pd.json_normalize(page_views)

    # the following was inspired by the section "Using XlsxWriter with Pandas" on http://xlsxwriter.readthedocs.io/working_with_pandas.html
    # set up the output write
    writer = pd.ExcelWriter(output_file, engine='xlsxwriter')

    convert_to_local_times(page_views_df, ['created_at', 'updated_at'])

    page_views_df.to_excel(writer, sheet_name='Page_views')

    # Close the Pandas Excel writer and output the Excel file.
    writer.save()

if __name__ == "__main__": main()
