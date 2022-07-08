#!/usr/bin/python3
#
# ./export-gradebook-with-score.py course_id
#
# Outputs an xlsx file of the form containing all of the custom columns: gradebook-course_id.xlsx
# The first column of the output will be user_id.
#
# the second sheet "Gradebook_history" will contain all of the gradebook entries made for the course
# 
# One can now selected the lastest grade for each student and for each assignment, to build the equivalent of the gradebook
#
# G. Q. Maguire Jr.
#
# 2017.03.06
# updated 2017.09.06
# updated on 2022-07-08 to deal with next links and change in merge
#

import csv, requests, time
from pprint import pprint
import optparse
import sys

from io import StringIO, BytesIO

from lxml import html

import json

# Use Python Pandas to create XLSX files
import pandas as pd

#############################
###### EDIT THIS STUFF ######
#############################

# styled based upon https://martin-thoma.com/configuration-files-in-python/
with open('config.json') as json_data_file:
       configuration = json.load(json_data_file)
       access_token=configuration["canvas"]["access_token"]
       baseUrl="https://"+configuration["canvas"]["host"]+"/api/v1/courses/"

modules_csv = 'modules.csv' # name of file storing module names
log_file = 'log.txt' # a log file. it will log things
header = {'Authorization' : 'Bearer ' + access_token}
payload = {}


##############################################################################
## ONLY update the code below if you are experimenting with other API calls ##
##############################################################################

def write_to_log(message):

       with open(log_file, 'a') as log:
              log.write(message + "\n")
              pprint(message)


def list_gradebook_history_feed(course_id):
       entries_found_thus_far=[]

       # Use the Canvas API to get the feed of gradebook information
       #GET /api/v1/courses/:course_id/gradebook_history/feed

       url = baseUrl + '%s/gradebook_history/feed' % (course_id)
       if Verbose_Flag:
              print("url: " + url)

       r = requests.get(url, headers = header)
       if Verbose_Flag:
              write_to_log("result of getting gradebook history feed: " + r.text)

       if r.status_code == requests.codes.ok:
              page_response=r.json()

       for p_response in page_response:  
              entries_found_thus_far.append(p_response)

       # the following is needed when the reponse has been paginated
       # i.e., when the response is split into pieces - each returning only some of the list of modules
       # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
       while 'next' in r.links:  
              r = requests.get(r.links['next']['url'], headers=header)  
              page_response = r.json()  
              for p_response in page_response:  
                     entries_found_thus_far.append(p_response)

       return entries_found_thus_far


def sections_in_course(course_id):
       sections_found_thus_far=[]
       # Use the Canvas API to get the list of sections for this course
       #GET /api/v1/courses/:course_id/sections

       url = baseUrl + '%s/sections' % (course_id)
       if Verbose_Flag:
              print("url: " + url)

       r = requests.get(url, headers = header)
       if Verbose_Flag:
              write_to_log("result of getting sections: " + r.text)

       if r.status_code == requests.codes.ok:
              page_response=r.json()

       for p_response in page_response:  
              sections_found_thus_far.append(p_response)

       # the following is needed when the reponse has been paginated
       # i.e., when the response is split into pieces - each returning only some of the list of modules
       # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
       while 'next' in r.links:  
              r = requests.get(r.links['next']['url'], headers=header)  
              page_response = r.json()  
              for p_response in page_response:  
                     sections_found_thus_far.append(p_response)

       return sections_found_thus_far

# create the following dict to use as an associate directory about users
selected_user_data={}

user_found_thus_far=[]

def users_in_course(course_id):
       global user_found_thus_far

       # Use the Canvas API to get the list of users enrolled in this course
       #GET /api/v1/courses/:course_id/enrollments

       url = baseUrl + '%s/enrollments' % (course_id)
       if Verbose_Flag:
              print("url: " + url)

       r = requests.get(url, headers = header)
       if Verbose_Flag:
              write_to_log("result of getting enrollments: " + r.text)

       if r.status_code == requests.codes.ok:
              page_response=r.json()

       for p_response in page_response:  
              user_found_thus_far.append(p_response)

       # the following is needed when the reponse has been paginated
       # i.e., when the response is split into pieces - each returning only some of the list of modules
       # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
       while 'next' in r.links:  
              r = requests.get(r.links['next']['url'], headers=header)  
              page_response = r.json()  
              for p_response in page_response:  
                     user_found_thus_far.append(p_response)
       return user_found_thus_far

def students_in_course(course_id, extra_p):
       students_found_thus_far=[]

       # Use the Canvas API to get the list of students in this course
       # GET /api/v1/courses/:course_id/users

       url = baseUrl + '%s/users' % (course_id)
       if Verbose_Flag:
              print("url: " + url)

       # enrollment_type[] should be set to 'student'
       # include[] perhaps include email, enrollments, avatar_url
       if extra_p:
              extra_parameters={'enrollment_type[]': 'student', 'include[]': 'email, enrollments, avatar_url'}
       else:
              extra_parameters={'enrollment_type[]': 'student'}
       r = requests.get(url, params=extra_parameters, headers = header)
       if Verbose_Flag:
              write_to_log("result of getting student enrollments: " + r.text)

       if r.status_code == requests.codes.ok:
              page_response=r.json()

       for p_response in page_response:  
              students_found_thus_far.append(p_response)

       # the following is needed when the reponse has been paginated
       # i.e., when the response is split into pieces - each returning only some of the list of modules
       # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
       if 'link' in r.headers:
              while 'next' in r.links:  
                     r = requests.get(r.links['next']['url'], headers=header)  
                     page_response = r.json()  
                     for p_response in page_response:  
                            students_found_thus_far.append(p_response)
       return students_found_thus_far


def list_custom_column_entries(course_id, column_number):
       entries_found_thus_far=[]

       # Use the Canvas API to get the list of custom column entries for a specific column for the course
       #GET /api/v1/courses/:course_id/custom_gradebook_columns/:id/data

       url = baseUrl + '%s/custom_gradebook_columns/%s/data' % (course_id, column_number)
       if Verbose_Flag:
              print("url: " + url)

       extra_parameters={'per_page': '100'}
       r = requests.get(url, params=extra_parameters, headers = header)
       #r = requests.get(url, headers = header)
       if Verbose_Flag:
              write_to_log("result of getting custom_gradebook_columns: " + r.text)

       if r.status_code == requests.codes.ok:
              page_response=r.json()

       for p_response in page_response:  
              entries_found_thus_far.append(p_response)

       # the following is needed when the reponse has been paginated
       # i.e., when the response is split into pieces - each returning only some of the list of modules
       # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
       while 'next' in r.links:  
              #r = requests.get(r.links['next']['url'], headers=header)  
              r = requests.get(r.links['next']['url'], params=extra_parameters, headers = header)
              page_response = r.json()  
              for p_response in page_response:  
                     entries_found_thus_far.append(p_response)

       return entries_found_thus_far




def list_custom_columns(course_id):
       columns_found_thus_far=[]

       # Use the Canvas API to get the list of custom column for this course
       #GET /api/v1/courses/:course_id/custom_gradebook_columns

       url = baseUrl + '%s/custom_gradebook_columns' % (course_id)
       if Verbose_Flag:
              print("url: " + url)

       r = requests.get(url, headers = header)
       if Verbose_Flag:
              write_to_log("result of getting custom_gradebook_columns: " + r.text)

       if r.status_code == requests.codes.ok:
              page_response=r.json()

       for p_response in page_response:  
              columns_found_thus_far.append(p_response)

       # the following is needed when the reponse has been paginated
       # i.e., when the response is split into pieces - each returning only some of the list of modules
       # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
       while 'next' in r.links:  
              r = requests.get(r.links['next']['url'], headers=header)  
              page_response = r.json()  
              for p_response in page_response:  
                     columns_found_thus_far.append(p_response)

       return columns_found_thus_far



def insert_column_name(course_id, column_name):
    global Verbose_Flag

    # Use the Canvas API to Create a custom gradebook column
    # POST /api/v1/courses/:course_id/custom_gradebook_columns
    #   Create a custom gradebook column
    # Request Parameters:
    #Parameter		Type	Description
    #column[title]	Required	string	no description
    #column[position]		integer	The position of the column relative to other custom columns
    #column[hidden]		boolean	Hidden columns are not displayed in the gradebook
    # column[teacher_notes]		boolean	 Set this if the column is created by a teacher. The gradebook only supports one teacher_notes column.

    url = baseUrl + '%s/custom_gradebook_columns' % (course_id)
    if Verbose_Flag:
       print("url: " + url)
    payload={'column[title]': column_name}
    r = requests.post(url, headers = header, data=payload)
    write_to_log("result of post creating custom column: " + r.text)
    if r.status_code == requests.codes.ok:
       write_to_log("result of inserting the item into the module: " + r.text)
       if r.status_code == requests.codes.ok:
           page_response=r.json()
           print("inserted column")
           return True
    return False

def compute_assignments_with_scores(list_of_assignments):
       d_of_assignments=dict()
       for assignm in list_of_assignments:
              # if the assignment has more than 0 points, then add a fake assignment to use to report the score
              if assignm['points_possible'] and (int(assignm['points_possible']) > 0):
                     d_of_assignments[assignm['name']+'_score'] = int(assignm['points_possible'])
       return d_of_assignments

def compute_list_of_assignments(list_of_assignments):
       assignments_list=list()
       for assignm in list_of_assignments:
              assignments_list.append(assignm['name'])
              # if the assignment has more than 0 points, then add a fake assignment to use to report the score
              if assignm['points_possible'] and (int(assignm['points_possible']) > 0):
                     assignments_list.append(assignm['name']+'_score')
       return assignments_list

def summarize_assignments(list_of_assignments):
       summary_of_assignments={}
       for assignm in list_of_assignments:
              summary_of_assignments[assignm['id']]=assignm['name']

       print("summary_of_assignments={}".format(summary_of_assignments))

def list_assignments(course_id):
       assignments_found_thus_far=[]

       # Use the Canvas API to get the list of assignments for the course
       #GET /api/v1/courses/:course_id/assignments

       url = baseUrl + '%s/assignments' % (course_id)
       if Verbose_Flag:
              print("url: " + url)

       r = requests.get(url, headers = header)
       if Verbose_Flag:
              write_to_log("result of getting assignments: " + r.text)

       if r.status_code == requests.codes.ok:
              page_response=r.json()

       for p_response in page_response:  
              assignments_found_thus_far.append(p_response)

       # the following is needed when the reponse has been paginated
       # i.e., when the response is split into pieces - each returning only some of the list of modules
       # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
       while 'next' in r.links:  
              r = requests.get(r.links['next']['url'], headers=header)  
              page_response = r.json()  
              for p_response in page_response:  
                     assignments_found_thus_far.append(p_response)

       return assignments_found_thus_far


def find_students_row(c_student, g_df):
       for i, row in  g_df.iterrows():
              if (row['user_id'] == c_student):
                     return i
       return -1
       
def main():
       global Verbose_Flag

       parser = optparse.OptionParser()

       parser.add_option('-v', '--verbose',
                         dest="verbose",
                         default=False,
                         action="store_true",
                         help="Print lots of output to stdout"
       )

       options, remainder = parser.parse_args()

       Verbose_Flag=options.verbose
       if Verbose_Flag:
              print('ARGV      :', sys.argv[1:])
              print('VERBOSE   :', options.verbose)
              print('REMAINING :', remainder)

       # add time stamp to log file
       log_time = str(time.asctime(time.localtime(time.time())))
       write_to_log(log_time)   

       if (len(remainder) < 1):
              print("Insuffient arguments\n must provide course_id\n")
              return

       course_id=remainder[0]
       students=students_in_course(course_id, False)
       students_df=pd.json_normalize(students)
       students_df.rename(columns = {'id': 'user_id'}, inplace = True)

       gradebook_history=list_gradebook_history_feed(course_id)
       if len(gradebook_history) == 0:
              print("No gradebook history - probably be cause you do not have access to the course.")
              return
       gradebook_history_df=pd.json_normalize(gradebook_history)
       
       list_of_assignments=list_assignments(course_id)
       l_of_assignments = compute_list_of_assignments(list_of_assignments)
       if Verbose_Flag:
              print('set of assignments ', l_of_assignments)

       list_of_columns=list_custom_columns(course_id)              

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
                     df=pd.json_normalize(output)
                     df.rename(columns = {'content': column_name}, inplace = True)
                     index=index+1
                     
                     if index == 1:
                            if Verbose_Flag:
                                   print('index: ', index)
                            merge_df = df
                     else:
                            if Verbose_Flag:
                                   print('else index: ', index)
                            # Note that one has to do an outer join in case one of the columns does not have a matching entry.
                            # This works because the outer join uses the union of the keys from both inputs.
                            new_merge_df = pd.merge(merge_df, df, on='user_id', how='outer')
                            merge_df=new_merge_df


       # If there were custom columns then fix them and put them in the gradebook_df, else just put the student_df in the gradebook_df
       if len(list_of_columns) > 0:
              #  based upon contribution by Ed Chum on Aug 4 '14 at 15:30 at http://stackoverflow.com/questions/25122099/move-column-by-name-to-front-of-table-in-pandas
              # get a list of columns
              cols = list(merge_df)
              # move the column to head of list using index, pop and insert
              cols.insert(0, cols.pop(cols.index('user_id')))
              # use ix to reorder
              merge_df = merge_df[cols]

              # This works because the outer join uses the union of the keys from both inputs.
              gradebook_df = pd.merge(students_df, merge_df, on='user_id', how='outer')
       else:
              gradebook_df = students_df.copy(deep=True)

       for x in l_of_assignments:
              gradebook_df[x]=''

       for index, row in  gradebook_history_df.iterrows():
              if Verbose_Flag:
                     print('index: ', index, 'row[assignment_name]: ', row['assignment_name'])
              current_assignment_name=row['assignment_name']
              current_student=row['user_id']
              current_student_row_index=find_students_row(current_student, gradebook_df)
              if Verbose_Flag:
                     print('index: ', index, 'row[assignment_name]: ', row['assignment_name'], 'current_student_row_index=', current_student_row_index, 'current_assignment_name=', current_assignment_name, 'grade=', row['current_grade'])
              if (row['current_graded_at'] == row['graded_at']):
                     if (row['excused'] == True):
                            gradebook_df.loc[current_student_row_index, current_assignment_name] = 'Excused'
                            if Verbose_Flag:
                                   print('excused: index: ', index)
                     else:
                            gradebook_df.loc[current_student_row_index, current_assignment_name] = row['current_grade']
                            current_assignment_name_score = current_assignment_name+'_score'
                            if current_assignment_name_score in gradebook_df.columns:
                                   gradebook_df.loc[current_student_row_index, current_assignment_name_score] = row['score']
                            if Verbose_Flag:
                                   print('current grade: index: ', index)
              else:
                     if Verbose_Flag:
                            print('current: ', row['current_graded_at'], 'graded_at: ', row['graded_at'])

       # add a row with the maximum number of points for the different scores
       assignments_with_scores=compute_assignments_with_scores(list_of_assignments)
       assignments_with_scores['user_id'] = -2
       assignments_with_scores['login_id'] = 'MAXIMUM'
       assignments_with_scores['name'] = 'aaaMAXIMUM'
       assignments_with_scores['short_name'] = 'aaaMAXIMUM'
       assignments_with_scores['sortable_name'] = 'aaaMAXIMUM'
       assignments_with_scores['Notes'] = 'dummy entry with maximum points per assignment'
       print('assignments_with_scores=', assignments_with_scores)

       for key, value in assignments_with_scores.items():
              gradebook_df.loc[-2, key] = value

       if Verbose_Flag:
              print('gradebook_df', gradebook_df)

       # the following was inspired by the section "Using XlsxWriter with Pandas" on http://xlsxwriter.readthedocs.io/working_with_pandas.html
       # set up the output write
       writer = pd.ExcelWriter('gradebook-'+str(course_id)+'.xlsx', engine='xlsxwriter')
       # Convert the dataframe to an XlsxWriter Excel object.

       gradebook_df.to_excel(writer, sheet_name='Gradebook')

       students_df.to_excel(writer, sheet_name='Students')

       # only output custom columns sheet if there were custom columns
       if len(list_of_columns) > 0:
              merge_df.to_excel(writer, sheet_name='Custom_Columns')

       gradebook_history_df.to_excel(writer, sheet_name='Gradebook_history')

       # Close the Pandas Excel writer and output the Excel file.
       writer.save()


       # add time stamp to log file
       log_time = str(time.asctime(time.localtime(time.time())))
       write_to_log(log_time)   
       write_to_log("\n--DONE--\n\n")

if __name__ == "__main__": main()

