#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# ./augment_quizzes-and-answers-in-course.py course_id
#
# Input:  XLSX spreadsheet with quizzes in course, with name of the form quizzes-<course_id>.xlsx
# Output: augmented XLSX spreadsheet with quizzes in course, with name of the form quizzes-<course_id>-augmented.xlsx
#
#
# with the option "-v" or "--verbose" you get lots of output - showing in detail the operations of the program
#
# Can also be called with an alternative configuration file:
# ./list_your_courses.py --config config-test.json
#
# Example:
# ./augment_quizzes-and-answers-in-course.py 11
#
# ./augment_quizzes-and-answers-in-course.py --config config-test.json 11
#
# 
# documentation about using xlsxwriter to insert images can be found at:
#   John McNamara, "Example: Inserting images into a worksheet", web page, 10 November 2018, https://xlsxwriter.readthedocs.io/example_images.html
#
# G. Q. Maguire Jr.
#
# based on earlier quizzes-and-answers-in-course.py
#
# 2019.01.05
#

import requests, time
import pprint
import optparse
import sys
import json
import os
from pathlib import Path

# Use Python Pandas to create XLSX files
import pandas as pd

# use lxml to access the HTML content
from lxml import html

# use the request pacek to get the HTML give an URL
import requests

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
    
def make_dir_for_urls(url, target_dir):
    global Verbose_Flag
    # the URLs have the form: https://canvas.kth.se/courses/11/quizzes/39141/history?quiz_submission_id=759552&version=1
    # remove prefix
    prefix="courses/"
    prefix_offset=url.find(prefix)
    if prefix_offset > 0:
        url_tail=url[prefix_offset+len(prefix):]
        parts_of_path=url_tail.split('/')
        if Verbose_Flag:
            print(parts_of_path)
        course_id=parts_of_path[0]
        quiz_id=parts_of_path[2]
        quiz_submission_part=parts_of_path[3].split('=')
        if Verbose_Flag:
            print(quiz_submission_part)
        quiz_submission_id=quiz_submission_part[1].split('&')[0]
        if Verbose_Flag:
            print(quiz_submission_id)
        dir_to_create="{0}/{1}/{2}/{3}".format(target_dir, course_id, quiz_id, quiz_submission_id)
        print("Creating directory: {}".format(dir_to_create))
        Path(dir_to_create).mkdir(parents=True, exist_ok=True)
        return dir_to_create

def dir_name_for_urls(url, target_dir):
    global Verbose_Flag
    # the URLs have the form: https://canvas.kth.se/courses/11/quizzes/39141/history?quiz_submission_id=759552&version=1
    # remove prefix
    prefix="courses/"
    prefix_offset=url.find(prefix)
    if prefix_offset > 0:
        url_tail=url[prefix_offset+len(prefix):]
        parts_of_path=url_tail.split('/')
        if Verbose_Flag:
            print(parts_of_path)
        course_id=parts_of_path[0]
        quiz_id=parts_of_path[2]
        quiz_submission_part=parts_of_path[3].split('=')
        if Verbose_Flag:
            print(quiz_submission_part)
        quiz_submission_id=quiz_submission_part[1].split('&')[0]
        if Verbose_Flag:
            print(quiz_submission_id)
        dir_to_create="{0}/{1}/{2}/{3}".format(target_dir, course_id, quiz_id, quiz_submission_id)
        return dir_to_create



def main():
    global Verbose_Flag
    global question_type_stats

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

    if (len(remainder) < 1):
        print("Insuffient arguments - must provide course_id\n")
    else:
        course_id=remainder[0]
        if not course_id:
            return

    target_dir="./Quiz_Submissions"
    question_id_prefix="question_"


    input_file="quizzes-{}.xlsx".format(course_id)
    quizzes_df = pd.read_excel(open(input_file, 'rb'), sheet_name='Quizzes')

    quiz_info=dict()
    quiz_list=[]
    for index, row in  quizzes_df.iterrows():
        quiz_info[row['id']]=row['title']

    print("quiz_info={}".format(quiz_info))

    incorrect_answers=dict()    # values student as a list under the question_id

    quiz_submissions_all=dict()
    for quiz in quiz_info:
        sheet_name="s_{}".format(quiz)
        quiz_submissions_all[quiz] = pd.read_excel(open(input_file, 'rb'), sheet_name=sheet_name)

        # add an empty column to remeber the questions that were ask
        quiz_submissions_all[quiz]['questions_asked']=''

        for index, row in  quiz_submissions_all[quiz].iterrows():
            # make a directory for the submissions from result_url
            # the URLs have the form: https://canvas.kth.se/courses/11/quizzes/39141/history?quiz_submission_id=759552&version=1
            url=row['result_url']
            questions_asked=dict()
            dir_name=dir_name_for_urls(url, target_dir)
            for file in os.listdir(dir_name):
                if file.endswith(".html"):
                    file_name=os.path.join(dir_name, file)
                    html_string=''
                    try:
                        with open(file_name) as html_file:
                            html_string = html_file.read()
                    except:
                        print("Unable to open file named {}".format(file_name))

                    print("\nProcessing file: {}".format(file_name))
                    version_prefix='_v'
                    version_offset=file_name.rindex(version_prefix)+2
                    if version_offset:
                        version_string=file_name[version_offset:-5]
                        print("version_string={}".format(version_string))

                    document = html.document_fromstring(html_string)
                    display_questions = document.xpath('//*[contains(@class, "display_question")]')
                    # Can have a correct answer:
                    # question id=question_274025 class=display_question question multiple_answers_question  correct   
                    # question id=question_274030 class=display_question question true_false_question  correct   
                    # question id=question_274031 class=display_question question multiple_answers_question  correct   
                    # question id=question_274032 class=display_question question short_answer_question  correct   

                    # Can have partially correct answer:
                    # question id=question_274033 class=display_question question multiple_answers_question     partial_credit
                    #
                    # Can have an incorrect answer:
                    # question id=question_274222 class=display_question question short_answer_question   incorrect  
                    # 
                    # Remember the questions ask in this attempt
                    question_asked_this_attempt=list()
                    for a_question in display_questions:
                        a_question_id=a_question.attrib['id']
                        a_question_class=a_question.attrib['class']
                        if Verbose_Flag:
                            print("question id={0} class={1}".format(a_question_id, a_question_class))
                        question_id=int(a_question_id[len(question_id_prefix):])
                        question_asked_this_attempt.append(question_id)
                    questions_asked[version_string]=question_asked_this_attempt

                    inputs = document.xpath('//*[@class="question_input"]')
                    #<input type="text" name="question_274239" value="effective" class="question_input" autocomplete="off" readonly="&quot;readonly&quot;" aria-label="Fill in the blank answer" aria-describedby="user_answer_NaN_arrow" style="width: 85.5px;">
                    for input in inputs:
                        input_id=input.attrib.get('id', None)
                        input_type=input.attrib.get('type', None)
                        input_name=input.attrib.get('name', None)
                        input_value=input.attrib.get('value', None)
                        input_describedby=input.attrib.get('aria-describedby', None)
                        if input_describedby == 'user_answer_NaN_arrow':
                            question_id=int(input_name[len(question_id_prefix):])                            
                            current_incorrect_answers=incorrect_answers.get(question_id, None)
                            if current_incorrect_answers:
                                incorrect_answers[question_id]=current_incorrect_answers.append(input_value)
                            else:
                                incorrect_answers[question_id]=[input_value]
                        print("input_id={0}, input_type={1},input_name={2},input_value={3},input_describedby={4}".format(input_id, input_type, input_name, input_value, input_describedby))

            if questions_asked:
                print("questions_asked={}".format(questions_asked))
                quiz_submissions_all[quiz].at[index, 'questions_asked']=questions_asked

    # the following was inspired by the section "Using XlsxWriter with Pandas" on http://xlsxwriter.readthedocs.io/working_with_pandas.html
    # set up the output write
    writer = pd.ExcelWriter('quizzes-'+course_id+'-augmented.xlsx', engine='xlsxwriter')
    quizzes_df.to_excel(writer, sheet_name='Quizzes')

    for quiz in quiz_info:
        # copy over the quiz data
        sheet_name="{}".format(quiz)
        print("copying quiz={}".format(sheet_name))
        quiz_instance = pd.read_excel(open(input_file, 'rb'), sheet_name=sheet_name)
        quiz_instance.to_excel(writer, sheet_name=sheet_name)

        # save the aumented quiz submission information
        sheet_name="s_{}".format(quiz)
        print("saving quiz submissions={}".format(sheet_name))
        quiz_submissions_all[quiz].to_excel(writer, sheet_name=sheet_name)

    # Close the Pandas Excel writer and output the Excel file.
    writer.save()

    for q in incorrect_answers:
        print("Incorrect answers for {0}: {1}".format(q, incorrect_answers[q]))


if __name__ == "__main__": main()

