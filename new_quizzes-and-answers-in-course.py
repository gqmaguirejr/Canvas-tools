#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# ./new_quizzes-and-answers-in-course.py course_id
#
# Output: XLSX spreadsheet with quizzes in course
#
#
# with the option "-v" or "--verbose" you get lots of output - showing in detail the operations of the program
#
# Can also be called with an alternative configuration file:
# ./new_quizzes-and-answers-in-course.py --config config-test.json course_id
#
# Example:
# ./new_quizzes-and-answers-in-course.py 11
#
# ./new_quizzes-and-answers-in-course.py --config config-test.json 11
#
# 
# G. Q. Maguire Jr.
#
# based on earlier quizzes-and-answers-in-course.py and Daniel Bosk's quiz.py
#
# Daniel used the canasapi - https://github.com/ucfopen/canvasapi
#
# Note that his line: quiz.get_submissions(include=["submission_history"])
# "quiz" is really assignment and not a quiz, the quiz object does NOT have a submission history.
# To resolve this for each assignment in the course, I check to see if the assignment is a online_quiz and
# sort the assignment in a dict under the quiz_id from the assignment. Thus one can look up the relevant
# assignment later when you want to get the submissions for a particular assignment.
#
# df_from_api_list and series_from_api_object - adapted from https://raw.githubusercontent.com/IonMich/autocanvas/main/autocanvas/core/conversions.py
# where really useful as getting things from the canvasapi object for use with Python pandas was " not easy to handle and manipulate"
# (quoting the original authors of these two functions - https://github.com/IonMich/autocanvas).
#
# To figure out how to adapte the two functions it was important to look at the canvasapi object,
# see https://github.com/ucfopen/canvasapi/blob/develop/canvasapi/canvas_object.py
# One of the things to be aware of is that in their set_attributes method,
# they create additional attributes X-date when the attribute X  has the form of a datetime ending with a time zone.
# However, the original attribute and value is present and this caused problem when writng the data out to Excel files.
# See the documentation at https://canvasapi.readthedocs.io/en/stable/getting-started.html#installing-canvasapi
#
#
# 2021-05-14
#

from argparse import ArgumentParser
import sys
import re
from pathlib import Path
from collections import defaultdict

# Use Python Pandas to create XLSX files
import pandas as pd

# use lxml to access the HTML content
from lxml import html

# use the request package to get the HTML give an URL
import requests

# 
import canvasapi
import json
import os

from datetime import date

#############################
###### EDIT THIS STUFF ######
#############################

verbose = False # Global flag for verbose prints
DEFAULT_CONFIG_FILE = 'config.json'

TARGET_DIR = './Quiz_Submissions'


def read_config(config_file: str = None) -> dict:
    config_file = config_file or DEFAULT_CONFIG_FILE
    try:
        # styled based upon https://martin-thoma.com/configuration-files-in-python/
        return json.loads(Path(config_file).read_text())
    except json.JSONDecodeError as e:
        print(f'Invalid JSON in {config_file}')
        raise e
    except Exception as e:
        print(f'Unable to open configuration file named {config_file}')
        print(f'Please create a suitable configuration file, the default name is {DEFAULT_CONFIG_FILE}')
        raise e



def dir_name_for_urls(url: str, target_dir: str) -> str:
    # the URLs have the form: https://canvas.kth.se/courses/11/quizzes/39141/history?quiz_submission_id=759552&version=1
    subdir_name = re.sub(r'^.*/courses/(\d+)/quizzes/(\d+)/history\?quiz_submission_id=(\d+)&version=\d+.*$',
                         r'\1/\2/\3',
                         url)
    if subdir_name == url:
        raise ValueError(f'Invalid URL: {url}')
    return f'{target_dir}/{subdir_name}'


def verbose_print(*args, **kwargs) -> None:
    global verbose
    if verbose:
        print(*args, **kwargs)


# df_from_api_list and series_from_api_object - adapted from https://raw.githubusercontent.com/IonMich/autocanvas/main/autocanvas/core/conversions.py
from canvasapi.paginated_list import PaginatedList


def df_from_api_list(api_list, drop_requester=True, drop_created_at=True, 
                    set_index_id=True, bring_to_front="name"):
    """
    Convert list from API (i.e. `list(PaginatedList)` or 
    simply PaginatedList) to pandas by extracting all the 
    attributes of each object 
    
    Note: index might be lost if you perform merging at a later point, 
    so if you want to preserve it, use `set_index_id` to False.
    
    TODO: add the object itself in a column so that the dataframe can 
    still be used directly to extract more info.
    """ 
    if isinstance(api_list, PaginatedList):
        api_list = list(api_list)
    
    row_list = []
    for api_obj in api_list:
        # remove time zones from any datetime type objects
        for e in api_obj.__dict__:
            if isinstance(api_obj.__getattribute__(e), date):
                print("e={0}, type={1}, type_value={2}".format(e, type(e), type(api_obj.__getattribute__(e))))
                d=api_obj.__getattribute__(e)
                #print("d before ={}".format(d))
                d=d.replace(tzinfo=None)
                #print("d after ={}".format(d))
                api_obj.__setattr__(e, d)
        row_list.append(api_obj.__dict__)
    df = pd.DataFrame(row_list)
    df["object"] = api_list
    
    if drop_requester:
        df = df.drop("_requester", errors="ignore", axis=1)
    if drop_created_at:
        df = df.drop("created_at", errors="ignore", axis=1)
    if set_index_id:
        df = df.set_index("id")
    if bring_to_front is not None:
        df = df[ [bring_to_front] + [col for col in df.columns 
                                        if col != bring_to_front] 
               ]
    return df

def series_from_api_object(api_object, 
                           add_object=True,
                           drop_requester=True, 
                           drop_created_at=True):
    """
    Convert object retrieved from API (i.e. to pandas by extracting all its
    attributes
    
    TODO: add the object itself in a row so that the dataframe can 
    still be used directly to extract more info.
    """ 

    # remove time zones from any datetime type objects
    for e in api_object.__dict__:
        if isinstance(api_object.__getattribute__(e), date):
            print("e={0}, type={1}, type_value={2}".format(e, type(e), type(api_object.__getattribute__(e))))
            d=api_object.__getattribute__(e)
            #print("d before ={}".format(d))
            d=d.replace(tzinfo=None)
            #print("d after ={}".format(d))
            api_object.__setattr__(e, d)

    series = pd.Series(api_object.__dict__)
    if add_object:
        series["object"] = api_object
    if drop_requester:
            series = series.drop("_requester", errors="ignore")
    if drop_created_at:
        series = series.drop("created_at", errors="ignore")
    return series

def main():
    global verbose
    global canvas

    parser = ArgumentParser()
    parser.add_argument('-v', '--verbose',
                        action='store_true',
                        help='Print lots of output to stdout'
    )
    parser.add_argument('-t', '--testing',
                        action='store_true',
                        help='Do not create the directories, only make the XLSX files'
    )
    parser.add_argument('--config', dest='config_filename',
                        help='read configuration from FILE',
                        metavar='FILE'
    )
    parser.add_argument('course_id')
    args = parser.parse_args()

    verbose_print(f'ARGV      : {sys.argv[1:]}')
    verbose_print(f'VERBOSE   : {args.verbose}')
    verbose_print(f'COURSE_ID : {args.course_id}')
    verbose_print(f'Configuration file : {args.config_filename}')

    verbose = args.verbose
    course_id = args.course_id
    config = read_config(args.config_filename)

    f'course_id={course_id}'

    # Initialize Canvas API
    canvas = canvasapi.Canvas('https://'+config["canvas"]["host"],config["canvas"]["access_token"])

    course = canvas.get_course(course_id)
    verbose_print(f'{course=}')
    course_info=series_from_api_object(course, add_object=False)
    verbose_print(f'{course_info=}')
    frame = { course_id: course_info}
  
    # use the transpose to convert rows to columns
    course_info_df = pd.DataFrame(frame).transpose()
    verbose_print(f'{course_info_df=}')
    
    quizzes = course.get_quizzes()
    if not quizzes:
        print('No quizzes found')
        return
    verbose_print(f'{quizzes=}')
    for quiz in quizzes:
        verbose_print(f'{quiz.title=}')

    # the following was inspired by the section "Using XlsxWriter with Pandas" on http://xlsxwriter.readthedocs.io/working_with_pandas.html
    # set up the output write
    writer = pd.ExcelWriter(f'quizzes-{course_id}.xlsx', engine='xlsxwriter')
    course_info_df.to_excel(writer, sheet_name='Course')

    #quizzes_df = pd.json_normalize(quizzes)
    quizzes_df = df_from_api_list(quizzes, drop_requester=True, drop_created_at=True,  set_index_id=False, bring_to_front=None)
    # below are examples of some columns that might be dropped
    columns_to_drop=[]
    quizzes_df.drop(columns_to_drop,inplace=True,axis=1)
    verbose_print(f'{quizzes_df.columns=}')    
    quizzes_df.sort_values(by=['id'],inplace=True)
    quizzes_df.to_excel(writer, sheet_name='Quizzes')

    question_type_stats = defaultdict(int) # new keys start counting from 0

    quizzes_by_id=dict()
    for q in quizzes:
        verbose_print(f'{q=}')
        qid=int(q.id)
        quizzes_by_id[qid]=q
    verbose_print(f'{quizzes_by_id=}')

    assignment_by_qid=dict()
    assignments=course.get_assignments()
    verbose_print(f'{assignments=}')
    for assignment in course.get_assignments():
        verbose_print(f'{assignment=}')
        if 'online_quiz' in assignment.submission_types:
            assignment_by_qid[assignment.quiz_id]=assignment
    verbose_print(f'{assignment_by_qid=}')

    for qid, quiz in sorted(quizzes_by_id.items()):
        quiz_qustions=quiz.get_questions()
        verbose_print(f'{quiz_qustions=}')

        quiz_questions_df = df_from_api_list(quiz_qustions, drop_requester=True, drop_created_at=True,  set_index_id=False, bring_to_front=None)
        #qi = canvas_api.list_quiz_questions(course_id, qid)
        quiz_questions_df.to_excel(writer, sheet_name=str(qid))

        for question in quiz_qustions:
            question_type_stats[question.question_type] += 1

        print("\n# Quiz submission questions\n")
        for quiz_submission in quiz.get_submissions():
            for subm_question in quiz_submission.get_submission_questions():
                #print(subm_question.__dict__.keys())
                #print(subm_question)
                print(f"{subm_question.id} "
                      f"{subm_question.question_name}:\n"
                      f"{subm_question.question_text}")
                try:
                    print(f"Alternatives: {subm_question.answers}")
                    print(f"Correct: {subm_question.correct}")
                except AttributeError:
                    pass
                print()

        print("\n# Quiz submission answers\n")
        quiz_assignment=assignment_by_qid.get(qid, None)
        submissions_for_this_quiz=[]
        if quiz_assignment:
            for submission in quiz_assignment.get_submissions(include=["submission_history"]):
                for subm in submission.submission_history:
                    submissions_for_this_quiz.append(subm)
                    print(subm)
                    try:
                        for data in subm["submission_data"]:
                            print(json.dumps(data, indent=2))
                    except KeyError:
                        pass

        
        submissions_for_this_quiz_df = pd.json_normalize(submissions_for_this_quiz)
        submissions_for_this_quiz_df.to_excel(writer, sheet_name=f'sh_{qid}')

        qs = quiz.get_submissions()
        # qs = canvas_api.list_quiz_submissions(course_id, qid)
        verbose_print(f'quiz {qid} submissions {qs}')
        quiz_sumbissions_df = df_from_api_list(qs, drop_requester=True, drop_created_at=True,  set_index_id=False, bring_to_front=None)
        quiz_sumbissions_df.to_excel(writer, sheet_name=f's_{qid}')



        # for submission in qs:
        #     results_url = submission.get('result_url', None)
        #     if not results_url:
        #         results_url = submission.get('html_url', None)
        #         workflow_state=submission.get('workflow_state', None)
        #         # it is possible that the student started to take a quiz, but did not complete it
        #         # in thas case the workflow_state will not be 'complete', check for the 'untaken' state
        #         # If so, then look at the previous attempt
        #         if workflow_state == 'untaken':
        #             attempt = int(submission['attempt']) - 1
        #             # we have to convert the html_url to an results_url
        #             # html_url    https://canvas.kth.se/courses/30565/quizzes/28318/submissions/777998
        #             # results_url https://canvas.kth.se/courses/30565/quizzes/28318/history?quiz_submission_id=777998&version=1
        #             s1=results_url.split('/submissions/')
        #             results_url="{0}/history?quiz_submission_id={1}&version={2}".format(s1[0], s1[1], attempt)
        #             print("new results_url is {0}".format(results_url))
        #         else:
        #             continue
        #     if not args.testing:
        #         d = dir_name_for_urls(results_url, TARGET_DIR)
        #         print(f'Creating directory: {d}')
        #         Path(d).mkdir(parents=True, exist_ok=True)
        #     attempt = submission['attempt']
        #     verbose_print(f'{attempt=}')

        #     # split to get the version and a base to which one can added new versions
        #     base_html_splt=results_url.split('version=')

        #     if base_html_splt and len(base_html_splt) == 2:
        #         latest_version=int(base_html_splt[1])

        #     for version in range(1, latest_version+1):
        #         print("getting version {0} of {1}".format(version, latest_version))
        #         target_url="{0}version={1}".format(base_html_splt[0], version)
        #         submitted_quiz = canvas_saml_session.get(target_url)
        #         if submitted_quiz.status_code != requests.codes.ok:
        #             verbose_print(f'Failed to fetch {results_url}')
        #             print("Error in getting page (0): {1}".format(target_url, submitted_quiz.status_code))
        #             continue

        #         if not args.testing:
        #             #Path(f'{d}/submission{submission["id"]}_v{attempt}.html').write_text(submitted_quiz.text)
        #             Path(f'{d}/submission{submission["id"]}_v{version}.html').write_text(submitted_quiz.text)

        #         document = html.document_fromstring(submitted_quiz.text)
        #         # look for the div with id="questions"
        #         questions = document.xpath('//*[@id="questions"]')
        #         for question in questions:
        #             verbose_print(f'question id={question.attrib["id"]} class={question.attrib["class"]}')
        #             inputs = question.xpath('.//input')
        #             for i in inputs:
        #                 # Example: type="text" name="question_346131" value="redish-green"
        #                 verbose_print(f'input type={i.type}, name={i.name}, value={i.value}')

    # Close the Pandas Excel writer and output the Excel file.
    writer.save()

    if question_type_stats:
        print(f'{question_type_stats=}')


if __name__ == "__main__": main()

