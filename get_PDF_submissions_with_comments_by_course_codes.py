#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# ./get_PDF_submissions_with_comments_by_course_codes.py  course_id assignment_id course_code+
#
# The program assumes that the courses codes are part of the name of a section. It uses this information
# to retrieve the submissions for a given assignment_id for all students in the relevant section or sections.
#
# Outputs a file with a name of the form: 'submission_comments-{course_id}-{section_id}-{assignment_id}.xlsx'
#
# with the option "-v" or "--verbose" you get lots of output - showing in detail the operations of the program
#
# with option "-m" or "--missing" lists the names of students who have made submissions but are not students in the relevant sections (generally this is due to test students)
#
# with option "-" or "--testing" does not fetch the summited files
#
# with option "-d" or "--dir" you can specify the directory to create otherwise it use a constructed anem
# of the form: './Submission-{course_id}-{section_id}-{assignment_id}'
#
# Can also be called with an alternative configuration file:
# ./get_PDF_submissions_with_comments_by_course_codes.py --config config-test.json  section_id course_code+
#
# Example
# ./get_PDF_submissions_with_comments_by_course_codes.py --config config-test.json  33514 179168 DA231X "DA232X VT22"
#
# If there are multiple course codes, then the most specific (i.e., longest) dominate over those that are only 6 characters long
# In this case, the section for DA232X VT22 is included, while all of the sections for DA231X are includes
# ./get_PDF_submissions_with_comments_by_course_codes.py --config config-test.json  33514 179168 DA231X "DA232X VT22"
#
# G. Q. Maguire Jr.
#
# based on earlier get_submissions_with_comments_for_section.py and get_PDF_submission.py
#
# 2023-01-07
#

import requests, time
import pprint
import optparse
import sys
import json

# Use Python Pandas to create XLSX files
import pandas as pd

# to use math.isnan(x) function
import math

import xlsxwriter

# for creating files and directories
from pathlib import Path

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


def sections_in_course(course_id):
    sections_found_thus_far=[]
    # Use the Canvas API to get the list of sections for this course
    #GET /api/v1/courses/:course_id/sections

    url = "{0}/courses/{1}/sections".format(baseUrl,course_id)
    if Verbose_Flag:
        print("url: {}".format(url))

    r = requests.get(url, headers = header)
    if Verbose_Flag:
        print("result of getting sections: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        page_response=r.json()

        for p_response in page_response:  
            sections_found_thus_far.append(p_response)

        # the following is needed when the reponse has been paginated
        # i.e., when the response is split into pieces - each returning only some of the list of modules
        # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
        while r.links.get('next', False):
            r = requests.get(r.links['next']['url'], headers=header)  
            page_response = r.json()  
            for p_response in page_response:  
                sections_found_thus_far.append(p_response)

    return sections_found_thus_far

def get_submissions_with_comments(section_id, assignment_id):
    submissions_found_thus_far=[]
    # Use the Canvas API to get the submissions and comments for an assignment
    # GET /api/v1/sections/:section_id/students/submissions
    url = "{0}/sections/{1}/students/submissions".format(baseUrl, section_id)
    if Verbose_Flag:
        print("url: {}".format(url))

    extra_parameters={'per_page': '100',
                      'student_ids[]': 'all',
                      'assignment_ids[]':  "{0}".format(assignment_id),
                      'grouped	': True,
                      'include[]': "submission_comments"
                      }
    r = requests.get(url, params=extra_parameters, headers = header)
    if Verbose_Flag:
        print("result of getting submissions with comments: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        page_response=r.json()

        for p_response in page_response:  
            submissions_found_thus_far.append(p_response)

        # the following is needed when the reponse has been paginated
        while r.links.get('next', False):
            r = requests.get(r.links['next']['url'], headers=header)
            if Verbose_Flag:
                print("result of getting submissions for a paginated response: {}".format(r.text))
            page_response = r.json()  
            for p_response in page_response:  
                submissions_found_thus_far.append(p_response)

    return submissions_found_thus_far

def students_in_course(course_id):
    users_found_thus_far=[]
    # Use the Canvas API to get the list of users enrolled in this course
    #GET /api/v1/courses/:course_id/enrollments

    url = "{0}/courses/{1}/enrollments".format(baseUrl,course_id)
    if Verbose_Flag:
        print("url: {}".format(url))

    extra_parameters={'per_page': '100',
                      'type': ['StudentEnrollment']
    }
    r = requests.get(url, params=extra_parameters, headers = header)
    if Verbose_Flag:
        print("result of getting enrollments: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        page_response=r.json()

        for p_response in page_response:  
            users_found_thus_far.append(p_response)

        # the following is needed when the reponse has been paginated
        while r.links.get('next', False):
            r = requests.get(r.links['next']['url'], headers=header)
            page_response = r.json()  
            for p_response in page_response:  
                users_found_thus_far.append(p_response)

    return users_found_thus_far

def teachers_in_course(course_id):
    users_found_thus_far=[]
    # Use the Canvas API to get the list of users enrolled in this course
    #GET /api/v1/courses/:course_id/enrollments

    url = "{0}/courses/{1}/enrollments".format(baseUrl,course_id)
    if Verbose_Flag:
        print("url: {}".format(url))

    extra_parameters={'per_page': '100',
                      'type': ['TeacherEnrollment']
    }
    r = requests.get(url, params=extra_parameters, headers = header)
    if Verbose_Flag:
        print("result of getting enrollments: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        page_response=r.json()

        for p_response in page_response:  
            users_found_thus_far.append(p_response)

        # the following is needed when the reponse has been paginated
        while r.links.get('next', False):
            r = requests.get(r.links['next']['url'], headers=header)
            page_response = r.json()  
            for p_response in page_response:  
                users_found_thus_far.append(p_response)

    return users_found_thus_far


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

def column_name_to_excel_letter(df, column_name):
    # The +1 is needed because the first column is an index and has no column heading
    col_no = df.columns.get_loc(column_name) + 1
    return xlsxwriter.utility.xl_col_to_name(col_no)

def main():
    global Verbose_Flag

    parser = optparse.OptionParser()

    parser.add_option('-v', '--verbose',
                      dest="verbose",
                      default=False,
                      action="store_true",
                      help="Print lots of output to stdout"
    )

    parser.add_option('-d', '--dir',
                      dest="target_dir",
                      default=False,
                      action="store",
                      help="Directory name to place submission in",
                      metavar="Target_Directory"
    )


    parser.add_option('-m', '--missing',
                      dest="missing",
                      default=False,
                      action="store_true",
                      help="check for missing students (i.e., submissions by someone who is not a student in the selected sections)"
    )

    parser.add_option('-p', '--print',
                      dest="print",
                      default=False,
                      action="store_true",
                      help="pprint the information"
    )

    parser.add_option('-t', '--testing',
                      dest="testing",
                      default=False,
                      action="store_true",
                      help="flag for testing, do not create submission files)"
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

    if (len(remainder) < 2):
        print("Insuffient arguments - must provide section_id assignment_id\n")
        sys.exit()

    course_id=remainder[0]
    assignment_id=remainder[1]

    list_of_course_codes=[]
    for c in range(2, len(remainder)):
        list_of_course_codes.append(remainder[c])

    print("Course codes to be processed: {}".format(list_of_course_codes))

    sections_info=sections_in_course(course_id)
    relevant_sections=[]
    processed_course_codes=[]
    remaining_course_codes=list_of_course_codes

    for s in sections_info:
        for cc in list_of_course_codes:
            if len(remaining_course_codes) >= 1:
                remaining_course_codes=remaining_course_codes[1:]
            processed_course_codes.append(cc)
            # if the 3rd character is a digit it is probably a KTH course code
            # otherwise check if the section name includes the CC string
            if not cc[2].isdigit() and cc in s['name']:
                relevant_sections.append(s)
            elif len(cc) > 6:
                if s['name'].startswith(cc):
                    relevant_sections.append(s)
            elif len(cc) == 6 and cc[0:5] not in remaining_course_codes:
                if s['name'].startswith(cc):
                    relevant_sections.append(s)
            else:
                print(f'Did not understand cource code {cc}')
                continue
                    
    if Verbose_Flag:
        print(f'{relevant_sections=}')

    comments_info=[]
    relevant_section_ids=[]
    unique_submission_id=set()
    for section in relevant_sections:
        section_id=section['id']
        relevant_section_ids.append(section_id)
        section_name=section['name']
        print(f'processing section {section_name}')

        comments_for_section=get_submissions_with_comments(section_id, assignment_id)
        if options.print:
            pprint.pprint(comments_for_section)
        # Because we get a submission for each section a user is in,
        # we need to only add the submission once.
        # However, the student may have submitted multiple times and
        # we need to keep the last attempt - however, for now we will keep each unique submission
        for s in comments_for_section:
            submission_id=s['id']
            if submission_id not in unique_submission_id:
                comments_info.append(s)
                unique_submission_id.add(submission_id)


    if Verbose_Flag:
        pprint.pprint(comments_info)

    writer = pd.ExcelWriter(f'submission_comments-{course_id}-{section_id}-{assignment_id}.xlsx', engine='xlsxwriter')
    comments_info_df=pd.json_normalize(comments_info)

    columns_to_drop=['assignment_id', 'anonymous_id']
    # look for the turnitin columns and dropt them
    cols=comments_info_df.columns
    for col in cols:
        if col.startswith("turnitin_data."):
            columns_to_drop.append(col)

    comments_info_df.drop(columns_to_drop,inplace=True,axis=1)
    # Note that one cannot drip duplicates as the attachments filed can contain a list
    comments_info_df.to_excel(writer, sheet_name='Comments')

    # collect the teachers in on of the sections that is included
    relevant_teachers=[]
    unique_teacher_ids=set()
    teachers=teachers_in_course(course_id)
    for t in teachers: 
        if t['course_section_id'] in relevant_section_ids:
            user_id=t['user_id']
            if user_id not in unique_teacher_ids:
                relevant_teachers.append(t)
                unique_teacher_ids.add(user_id)

    teachers_df=pd.json_normalize(relevant_teachers)

    cols_to_keep=['user_id', 'user.sortable_name']
    columns_to_drop=[c for c in teachers_df.columns if c not in cols_to_keep]

    teachers_df.drop(columns_to_drop,inplace=True,axis=1)
    teachers_df.drop_duplicates(ignore_index=True, inplace=True, keep='last')
    teachers_df.to_excel(writer, sheet_name='Teachers')

    # Figure out which teachers are relevant as graders based on whether they have graded an assignment or not
    relevant_grader_ids=set()
    for idx, row in comments_info_df.iterrows():
        grader_id=row['grader_id']
        if isinstance(grader_id, float) and not math.isnan(grader_id):
            relevant_grader_ids.add(int(grader_id))

    if Verbose_Flag:
        print(f'{relevant_grader_ids=}')

    graders=[]
    unique_grader_ids=set()
    for t in teachers:
        user_id=t['user_id']
        if user_id in relevant_grader_ids:
            if user_id not in unique_grader_ids:
                graders.append(t)
                unique_grader_ids.add(user_id)

    graders_df=pd.json_normalize(graders)
    
    cols_to_keep=['user_id', 'user.sortable_name']
    columns_to_drop=[c for c in graders_df.columns if c not in cols_to_keep]

    graders_df.drop(columns_to_drop,inplace=True,axis=1)
    graders_df.drop_duplicates(ignore_index=True, inplace=True, keep='last')
    graders_df.to_excel(writer, sheet_name='Graders')

    students=students_in_course(course_id)
    relevant_students=[]
    unique_relevant_student_ids=set()
    for s in students:
        if Verbose_Flag:
            pprint.pprint(s)
        # add the student if they are in any of the relevant sections and not already in the list
        if s['course_section_id'] in relevant_section_ids:
            if s['user_id'] not in unique_relevant_student_ids:
                relevant_students.append(s)


    students_df=pd.json_normalize(relevant_students)
    # keep user_id and 'user.sortable_name', drop the rest
    cols_to_keep=['user_id','user.sortable_name']
    columns_to_drop=[c for c in students_df.columns if c not in cols_to_keep]

    students_df.drop(columns_to_drop,inplace=True,axis=1)
    students_df.drop_duplicates(ignore_index=True, inplace=True, keep='last')
    students_df.to_excel(writer, sheet_name='Students')

    merge_df = pd.merge(comments_info_df, students_df, on='user_id')
    merge_df.to_excel(writer, sheet_name='Submissions')

    if len(graders_df.index) > 0:
        graders_df.rename(columns = {'user_id': 'grader_id', 'user.sortable_name': 'grader.sortable_name'}, inplace = True)
        merge_df2 = pd.merge(merge_df, graders_df, on='grader_id')
        merge_df2.to_excel(writer, sheet_name='Graded')

    # Make a summary
    workbook = writer.book
    summary_worksheet = workbook.add_worksheet('Summary')
    section_names_as_string=','.join(list_of_course_codes) 
    summary_worksheet.write_string(0,    0, f'Some rough statistics for {section_names_as_string}')
    summary_worksheet.write_string(1,    1, 'Submissions with comments')
    summary_worksheet.write_formula(2,   1, f'=COUNTA(Comments!A:A)')
    summary_worksheet.write_string(1,    2, 'Students')
    summary_worksheet.write_formula(2,   2, f'=COUNTA(Students!A:A)')
    summary_worksheet.write_string(1,    3, 'Teachers')
    summary_worksheet.write_formula(2,   3, f'=COUNTA(Teachers!A:A)')
    summary_worksheet.write_string(1,    4, 'Graders')
    summary_worksheet.write_formula(2,   4, f'=COUNTA(Graders!A:A)')

    summary_worksheet.write_string(0,    5, 'workflow_state')
    workflow_state_col=title_eng_column=column_name_to_excel_letter(comments_info_df,  'workflow_state')
    summary_worksheet.write_string(1,    5, 'graded')
    summary_worksheet.write_formula(2,   5, f'=COUNTIF(Comments!{workflow_state_col}:{workflow_state_col}, Summary!F2)')
    summary_worksheet.write_string(1,    6, 'submitted')
    summary_worksheet.write_formula(2,   6, f'=COUNTIF(Comments!{workflow_state_col}:{workflow_state_col}, Summary!G2)')
    summary_worksheet.write_string(1,    7, 'unsubmitted')
    summary_worksheet.write_formula(2,   7, f'=COUNTIF(Comments!{workflow_state_col}:{workflow_state_col}, Summary!H2)')

    # Close the Pandas Excel writer and output the Excel file.
    writer.close()

    if options.missing:
        # look for users_ids that occur in submisisons with comments (i.e., comments_info_df) that are not in Submissions (i.e., merge_df)
        who_submited_with_comments=set()
        who_submitted=set()
        for idx, row in comments_info_df.iterrows():
            who_submited_with_comments.add(row['user_id'])

        for idx, row in merge_df.iterrows():
            who_submitted.add(row['user_id'])

        set_difference=who_submited_with_comments - who_submitted
        print(f'{set_difference=}')

        print("The names of the missing students are:")
        for s in set_difference:
            sp=get_user_profile(s)
            # 'sortable_name': 'Student, Test'
            print(sp['sortable_name'])

    if not options.target_dir:
        target_dir=f'./Submission-{course_id}-{section_id}-{assignment_id}'
    else: 
        target_dir=options.target_dir

    if not options.testing:
        print(f'Creating directory: {target_dir}')
        Path(target_dir).mkdir(parents=True, exist_ok=True)
        for idx, row in merge_df.iterrows():
            output_filename_base=row['user.sortable_name']
            if not output_filename_base or len(output_filename_base) < 1:
                print(f'error in output_filename_base={output_filename_base}, skipping {idx}')
                continue
            if output_filename_base and isinstance(output_filename_base, str):
                output_filename_base=output_filename_base.replace(', ', '__')

            # if the worflow state indicates submitted or graded
            date_submitted=row['submitted_at']
            if row['workflow_state'] in ['submitted', 'graded'] and date_submitted is not None:
                if Verbose_Flag:
                    print("idx={0}, date_submitted={1} type={2}".format(idx, date_submitted, type(date_submitted)))
                attachments=row['attachments']
                # attachments
                # [{'id': 5209764, 'uuid': 'xxxx', 'folder_id': xxxx, 'display_name': 'Individual_plan.pdf', 'filename': 'Individual_plan.pdf', 'upload_status': 'success', 'content-type': 'application/pdf', 'url': 'https://kth.test.instructure.com/files/xxxx/download?download_frd=1&verifier=xxxx', 'size': xxxxx, 'created_at': 'YYYY-MM-DDThh:mm:ssZ', 'updated_at': 'YYYY-MM-DDThh:mm:ssZ', 'unlock_at': None, 'locked': False, 'hidden': False, 'lock_at': None, 'hidden_for_user': False, 'thumbnail_url': None, 'modified_at': 'YYYY-MM-DDThh:mm:ssZ', 'mime_class': 'pdf', 'media_entry_id': None, 'category': 'uncategorized', 'locked_for_user': False, 'preview_url': 'xxxx'}]

                if len(attachments) > 0:
                    for attachment in attachments:
                        if Verbose_Flag:
                            print(f'{attachment=}')
                        created_at=attachment.get('created_at', "")
                        if created_at and isinstance(created_at, str):
                            if created_at.endswith('Z'):
                                created_at=created_at[:-1]
                            created_at=created_at.replace(':', '')
                            created_at=created_at.replace('-', '')

                        a_filename=attachment['filename']
                        if not a_filename or len(a_filename) < 1:
                            print(f'error in attachment filename={a_filename}, skipping {idx}')
                            continue
                        output_filename=f'{target_dir}/{created_at}-{output_filename_base}-{a_filename}'
                        url=attachment['url']
                        if not url or len(url) < 1:
                            print(f'error in url={url}, skipping {idx}')
                            continue
                        content_type=row.get('content-type', None)
                        if content_type and 'application/pdf' not in content_type:
                            print(f'error unexpected ontent-tyep={content_type}, skipping {idx}')
                            continue

                        if Verbose_Flag:
                            print(f'About to fetch url={url}')
                        r = requests.get(url)
                        if r.status_code == requests.codes.ok:
                            print(f'Writing file {output_filename}')
                            with open(output_filename,'wb') as f:
                                f.write(r.content)
if __name__ == "__main__": main()

