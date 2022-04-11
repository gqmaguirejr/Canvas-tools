#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# ./quizzes-and-answers-in-course.py course_id
#
# Output: XLSX spreadsheet with quizzes in course
#
#
# with the option "-v" or "--verbose" you get lots of output - showing in detail the operations of the program
#
# Can also be called with an alternative configuration file:
# ./list_your_courses.py --config config-test.json
#
# Example:
# ./quizzes-in-course.py 11
#
# ./quizzes-in-course.py --config config-test.json 11
#
# 
# documentation about using xlsxwriter to insert images can be found at:
#   John McNamara, "Example: Inserting images into a worksheet", web page, 10 November 2018, https://xlsxwriter.readthedocs.io/example_images.html
#
# G. Q. Maguire Jr.
#
# based on earlier list-quizzes.py
#
# 2019.01.05
#

from argparse import ArgumentParser
import sys
import json
import re
from pathlib import Path
from collections import defaultdict

# Use Python Pandas to create XLSX files
import pandas as pd

# use lxml to access the HTML content
from lxml import html

# use the request package to get the HTML give an URL
import requests

# canvas_api.py - handler for Canvas API
from canvas_api import CanvasAPI

# kth_canvas_saml.py - toolkit for KTH Canvas login
import kth_canvas_saml

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


# Take out the config variables used to authenticate KTH through SAML login. Used to access Canvas pages directly.
def get_kth_credentials(config: dict) -> tuple:
    try:
        return (config["kth"]["username"], config["kth"]["password"])
    except KeyError as e:
        print('Missing keys in config file')
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


def main():
    global verbose

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

    # Initialize Canvas API
    canvas_api = CanvasAPI(config, verbose)

    # Initialize Canvas KTH SAML login
    user, password = get_kth_credentials(config)
    canvas_saml_session = kth_canvas_saml.kth_canvas_login_prompt(user, password, verbose=verbose)

    verbose_print(f'{course_id=}')
    course_info = canvas_api.get_course_info(course_id)
    quizzes = canvas_api.list_quizzes(course_id)
    if not quizzes:
        print('No quizzes found')
        return

    # the following was inspired by the section "Using XlsxWriter with Pandas" on http://xlsxwriter.readthedocs.io/working_with_pandas.html
    # set up the output write
    writer = pd.ExcelWriter(f'quizzes-{course_id}.xlsx', engine='xlsxwriter')
    if course_info:
        pd.json_normalize(course_info).to_excel(writer, sheet_name='Course')

    quizzes_df = pd.json_normalize(quizzes)
    # below are examples of some columns that might be dropped
    #columns_to_drop=[]
    #quizzes_df.drop(columns_to_drop,inplace=True,axis=1)
    quizzes_df.to_excel(writer, sheet_name='Quizzes')

    question_type_stats = defaultdict(int) # new keys start counting from 0

    for qid in sorted(q['id'] for q in quizzes):
        qi = canvas_api.list_quiz_questions(course_id, qid)
        pd.json_normalize(qi).to_excel(writer, sheet_name=str(qid))
        for question in qi:
            question_type_stats[question.get('question_type', None)] += 1

        qs = canvas_api.list_quiz_submissions(course_id, qid)
        verbose_print(f'quiz {qid} submissions {qs}')
        pd.json_normalize(qs).to_excel(writer, sheet_name=f's_{qid}')

        for submission in qs:
            results_url = submission.get('result_url', None)
            if not results_url:
                continue
            if not args.testing:
                d = dir_name_for_urls(results_url, TARGET_DIR)
                print(f'Creating directory: {d}')
                Path(d).mkdir(parents=True, exist_ok=True)
            attempt = submission['attempt']
            verbose_print(f'{attempt=}')

            submitted_quiz = canvas_saml_session.get(results_url)
            if submitted_quiz.status_code != requests.codes.ok:
                verbose_print(f'Failed to fetch {results_url}')
                continue

            if not args.testing:
                Path(f'{d}/submission{submission["id"]}_v{attempt}.html').write_text(submitted_quiz.text)

            document = html.document_fromstring(submitted_quiz.text)
            # look for the div with id="questions"
            questions = document.xpath('//*[@id="questions"]')
            for question in questions:
                verbose_print(f'question id={question.attrib["id"]} class={question.attrib["class"]}')
                inputs = question.xpath('.//input')
                for i in inputs:
                    # Example: type="text" name="question_346131" value="redish-green"
                    verbose_print(f'input type={i.type}, name={i.name}, value={i.value}')

    # Close the Pandas Excel writer and output the Excel file.
    writer.save()

    if question_type_stats:
        print(f'{question_type_stats=}')


if __name__ == "__main__": main()

