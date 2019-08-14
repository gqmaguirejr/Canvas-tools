#!/usr/bin/python3
#
# ./list-all-custom-column-entries.py course_id
#
# Outputs an xlsx file of the form containing all of the custom columns: custom-column-entries-course_id-column-column_all.xlsx
# The first column of the output will be user_id.
#
# with the option '-C'or '--containers' use HTTP rather than HTTPS for access to Canvas
# with the option "-v" or "--verbose" you get lots of output - showing in detail the operations of the program
#
# Can also be called with an alternative configuration file:
# ./create_fake_users-in-course.py --config config-test.json
#
# G. Q. Maguire Jr.
#
# based on 2016.11.29 version of Canvas-git/list-all-custom-column-entries.py
#
# 2019.02.19
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

def list_custom_column_entries(course_id, column_number):
       entries_found_thus_far=[]

       # Use the Canvas API to get the list of custom column entries for a specific column for the course
       #GET /api/v1/courses/:course_id/custom_gradebook_columns/:id/data

       url = "{0}/courses/{1}/custom_gradebook_columns/{2}/data".format(baseUrl,course_id, column_number)
       if Verbose_Flag:
              print("url: " + url)

       r = requests.get(url, headers = header)
       if Verbose_Flag:
              print("result of getting custom_gradebook_columns: {}".format(r.text))

       if r.status_code == requests.codes.ok:
              page_response=r.json()

       for p_response in page_response:  
              entries_found_thus_far.append(p_response)

       # the following is needed when the reponse has been paginated
       # i.e., when the response is split into pieces - each returning only some of the list of modules
       # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
       while r.links['current']['url'] != r.links['last']['url']:  
              r = requests.get(r.links['next']['url'], headers=header)  
              page_response = r.json()  
              for p_response in page_response:  
                     entries_found_thus_far.append(p_response)

       return entries_found_thus_far

def list_custom_columns(course_id):
       columns_found_thus_far=[]
       # Use the Canvas API to get the list of custom column for this course
       #GET /api/v1/courses/:course_id/custom_gradebook_columns

       url = "{0}/courses/{1}/custom_gradebook_columns".format(baseUrl,course_id)
       if Verbose_Flag:
              print("url: {}".format(url))

       r = requests.get(url, headers = header)
       if Verbose_Flag:
              print("result of getting custom_gradebook_columns: {}".format(r.text))

       if r.status_code == requests.codes.ok:
              page_response=r.json()

              for p_response in page_response:  
                     columns_found_thus_far.append(p_response)

              # the following is needed when the reponse has been paginated
              # i.e., when the response is split into pieces - each returning only some of the list of modules
              # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
              while r.links['current']['url'] != r.links['last']['url']:  
                     r = requests.get(r.links['next']['url'], headers=header)  
                     page_response = r.json()  
                     for p_response in page_response:  
                            columns_found_thus_far.append(p_response)

       return columns_found_thus_far



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

       if (len(remainder) < 1):
              print("Insuffient arguments\n must provide course_id\n")
              return

       course_id=remainder[0]
       list_of_columns=list_custom_columns(course_id)              
       if Verbose_Flag:
           print('list_of_columns: ', list_of_columns)

       custom_columns_present=False
       index=0
       for column in list_of_columns:
              column_name=column['title']
              column_number=column['id']

              if Verbose_Flag:
                     print('column_name: ', column_name, '; column_number: ', column_number)

              output=list_custom_column_entries(course_id, column_number)
              if (output):
                     if Verbose_Flag:
                            print(output)

                     # the following was inspired by pbreach's answer on Jan 21 '14 at 18:17 in http://stackoverflow.com/questions/21104592/json-to-pandas-dataframe
                     # create a Panda dataframe from the output
                     df=pd.io.json.json_normalize(output)
                     df.rename(columns = {'content': column_name}, inplace = True)
                     index=index+1
                     
                     if index == 1:
                            if Verbose_Flag:
                                   print('index: ', index)
                            merge_df = df
                            custom_columns_present=True
                     else:
                            if Verbose_Flag:
                                   print('else index: ', index)
                            # Note that one has to do an outer join in case on of the columns does not have a matching entry.
                            # This works because the outer join uses the union of the keys from both inputs.
                            new_merge_df = pd.merge(merge_df, df, on='user_id', how='outer')
                            merge_df=new_merge_df


       #  based upon contribution by Ed Chum on Aug 4 '14 at 15:30 at http://stackoverflow.com/questions/25122099/move-column-by-name-to-front-of-table-in-pandas
       # get a list of columns
       #cols = list(merge_df)
       if custom_columns_present:
              cols = list(merge_df)
              # move the column to head of list using index, pop and insert
              cols.insert(0, cols.pop(cols.index('user_id')))
              # use ix to reorder
              merge_df = merge_df.ix[:, cols]

              # the following was inspired by the section "Using XlsxWriter with Pandas" on http://xlsxwriter.readthedocs.io/working_with_pandas.html
              # set up the output write
              writer = pd.ExcelWriter('custom-column-entries-'+str(course_id)+'-column-all.xlsx', engine='xlsxwriter')
              # Convert the dataframe to an XlsxWriter Excel object.
              merge_df.to_excel(writer, sheet_name='Custom_Columns')
              # Close the Pandas Excel writer and output the Excel file.
              writer.save()
       else:
              print("There were no custom columns")
if __name__ == "__main__": main()

