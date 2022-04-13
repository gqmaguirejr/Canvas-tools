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

import requests, time
import pprint
import optparse
import sys
import json

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



def get_course_info(course_id):
    # Use the Canvas API to get the course info
    #GET /api/v1/courses/:id

    url = "{0}/courses/{1}".format(baseUrl, course_id)
    if Verbose_Flag:
        print("in course info url: {}".format(url))

    r = requests.get(url, headers = header)
    if Verbose_Flag:
        print("result of getting course info: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        page_response=r.json()

    return page_response



def list_quizzes(course_id):
    quizzes_found_thus_far=[]
    # Use the Canvas API to get the list of quizzes for the course
    #GET /api/v1/courses/:course_id/quizzes

    url = "{0}/courses/{1}/quizzes".format(baseUrl, course_id)
    if Verbose_Flag:
        print("in list_quizzes url: {}".format(url))

    extra_parameters={'per_page': '100'}
    r = requests.get(url, headers = header, params=extra_parameters)
    if Verbose_Flag:
        print("result of getting quizzes: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        page_response=r.json()

        for p_response in page_response:  
            quizzes_found_thus_far.append(p_response)

            # the following is needed when the reponse has been paginated
            # i.e., when the response is split into pieces - each returning only some of the list
            # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
            while r.links.get('next', False):
                r = requests.get(r.links['next']['url'], headers=header, params=extra_parameters)  
                if Verbose_Flag:
                    print("result of getting quizzes for a paginated response: {}".format(r.text))
                page_response = r.json()  
                for p_response in page_response:  
                    quizzes_found_thus_far.append(p_response)

    return quizzes_found_thus_far

def list_quiz_questions(course_id, quiz_id):
    questions_found_thus_far=[]
    # Use the Canvas API to get the list of questions for a quiz in the course
    # GET /api/v1/courses/:course_id/quizzes/:quiz_id/questions

    url = "{0}/courses/{1}/quizzes/{2}/questions".format(baseUrl, course_id, quiz_id)
    if Verbose_Flag:
        print("url: {}".format(url))

    extra_parameters={'per_page': '100'}
    r = requests.get(url, headers = header, params=extra_parameters)
    if Verbose_Flag:
        print("result of getting questions: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        page_response=r.json()

        for p_response in page_response:  
            questions_found_thus_far.append(p_response)

            # the following is needed when the reponse has been paginated
            # i.e., when the response is split into pieces - each returning only some of the list of modules
            # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
            while r.links.get('next', False):
                r = requests.get(r.links['next']['url'], headers=header, params=extra_parameters)
                if Verbose_Flag:
                    print("result of getting questions for a paginated response: {}".format(r.text))
                page_response = r.json()  
                for p_response in page_response:  
                    questions_found_thus_far.append(p_response)

    return questions_found_thus_far


def list_quiz_submissions(course_id, quiz_id):
    submissions_found_thus_far=[]
    # Get all quiz submissions
    # GET /api/v1/courses/:course_id/quizzes/:quiz_id/submissions
    #Parameter		Type	Description
    #include[]		string	
    #Associations to include with the quiz submission.
    # Allowed values: submission, quiz, user

    url = "{0}/courses/{1}/quizzes/{2}/submissions".format(baseUrl, course_id, quiz_id)
    if Verbose_Flag:
        print("url: {}".format(url))

    extra_parameters={'include[]': 'submission',
                      'per_page': '100'}

    r = requests.get(url, params=extra_parameters, headers = header)
    if Verbose_Flag:
        print("result of getting submissions: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        page_response=r.json()

        qs=page_response.get('quiz_submissions', [])
        for p_response in qs:  
            submissions_found_thus_far.append(p_response)

            # the following is needed when the reponse has been paginated
            # i.e., when the response is split into pieces - each returning only some of the list of modules
            # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
            while r.links.get('next', False):
                r = requests.get(r.links['next']['url'], headers=header, params=extra_parameters)  
                if Verbose_Flag:
                    print("result of getting submissions for a paginated response: {}".format(r.text))
                page_response = r.json()  
                qs=page_response.get('quiz_submissions', [])
                for p_response in qs:  
                    submissions_found_thus_far.append(p_response)

    return submissions_found_thus_far


def update_question_type_stats(question):
    global question_type_stats

    qt=question.get('question_type', None)
    qt_number=question_type_stats.get(qt, 0)
    if qt_number == 0:
        question_type_stats[qt]=1
    else:
        question_type_stats[qt]=qt_number+1
    
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

    parser.add_option('-t', '--testing',
                      dest="testing",
                      default=False,
                      action="store_true",
                      help="Do not create the directories only make the XLSX files"
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
        return
    else:
        course_id=remainder[0]
        if Verbose_Flag:
            print("course_id={0}, type={1}".format(course_id, type(course_id)))

        course_info=get_course_info(course_id)
        quizzes=list_quizzes(course_id)
        question_type_stats=dict()

        target_dir="./Quiz_Submissions"
        if options.testing:
            target_dir="./Quiz_Submissions-testing"

        if course_info:
            course_info_df=pd.json_normalize(course_info)
        if (quizzes):
            quizzes_df=pd.json_normalize(quizzes)
                     
            # below are examples of some columns that might be dropped
            #columns_to_drop=[]
            #quizzes_df.drop(columns_to_drop,inplace=True,axis=1)

            # the following was inspired by the section "Using XlsxWriter with Pandas" on http://xlsxwriter.readthedocs.io/working_with_pandas.html
            # set up the output write
            writer = pd.ExcelWriter('quizzes-'+course_id+'.xlsx', engine='xlsxwriter')
            if course_info:
                course_info_df.to_excel(writer, sheet_name='Course')

            quizzes_df.to_excel(writer, sheet_name='Quizzes')

            for q in sorted(quizzes, key=lambda x: x['id']):
                qi=list_quiz_questions(course_id, q['id'])
                qi_df=pd.json_normalize(qi)
                qi_df.to_excel(writer, sheet_name=str(q['id']))

                for question in qi:
                    update_question_type_stats(question)

                #Verbose_Flag=True
                qs=list_quiz_submissions(course_id, q['id'])
                #Verbose_Flag=False
                if Verbose_Flag:
                    print("quiz submission {0} {1}".format(q['id'], qs))
                qs_df=pd.json_normalize(qs)
                qs_df.to_excel(writer, sheet_name='s_'+str(q['id']))
                for submission in qs:
                    results_url=submission.get('result_url', None)
                    if results_url and not options.testing:
                        make_dir_for_urls(results_url, target_dir)


                # At this point I want to fetch all of the version of each quiz submission and save the results to files
                # converting the URLs of the form 'https://canvas.kth.se/courses/:course_id/quizzes/:quiz_id/history?quiz_submission_id=:submission_id&version=:version:number'
                # into file names of the form: :course_id_:quiz_id_quiz_submission_id=:submission_id_version_:version:number

                #
                # for submission in qs:
                #     results_url=submission.get('result_url', None)
                #     if results_url:
                #         attempt=submission['attempt']
                #         print("attempt={}".format(attempt))

                #         submitted_quiz = requests.get(results_url)
                #         submission_html=submitted_quiz.text
                #         if submission_html and len(submission_html) > 0:
                #             print("found a submission: {}".format(submission_html))
                #             # look for the div with id="questions"
                #             document = html.document_fromstring(submission_html)
                #             # questions = document.xpath('//*[@id="questions"]/div/*[@class="display_question"]')
                #             questions = document.xpath('//*[@id="questions"]')
                #             for a_question in questions:
                #                 a_question_id=a_question.attrib['id']
                #                 a_question_class=a_question.attrib['class']
                #                 print("question id={0} class={1}".format(a_question_id, a_question_class))
                #                 input=a_question.find('input')
                #                 if input:
                #                     # type="text" name="question_346131" value="redish-green"
                #                     input_type=input.attrib['type']
                #                     input_name=input.attrib['name']
                #                     input_value=input.attrib['value']
                #                     print("input type={0], name={1}, value={2}".format(input_type, input_name, input_value))


            # Close the Pandas Excel writer and output the Excel file.
            writer.save()

        if len(question_type_stats) > 0:
            print("question_type_stats={}".format(question_type_stats))
        

if __name__ == "__main__": main()

