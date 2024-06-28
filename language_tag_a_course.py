#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# ./language_tag_a_course.py course_id lang
#
# Purpose: To go throught a course and add HTML language attribute to relevant elements
#
# Outputs:
# with the option "-v" or "--verbose" you get lots of output - showing in detail the operations of the program
#
# Can also be called with an alternative configuration file:
# ./language_tag_a_course.py --config config-test.json  course_id lang
#
# Example:
# ./language_tag_a_course.py 751 en
#
# ./language_tag_a_course.py 53524 sv
#
# Note that only the 10 most recent entries within a discussion are processed - as this is a limitation of the API call being used to fetch them.
# Note that announcements are considered between 1 year ago today and 70 days from today. Also, announcements and their replies are like discussions,
# hence the limitation to the 10 most recent applies
# 
# G. Q. Maguire Jr.
#
# based on earlier edit_modules_items_in_a_module_in_a_course.py
#
# 2021-09-28
#

import requests, time
import pprint
import optparse
import sys
import json

from datetime import datetime, date, timedelta
import isodate                  # for parsing ISO 8601 dates and times
import pytz                     # for time zones

# Use Python Pandas to create XLSX files
import pandas as pd

# use BeautifulSoup to process the HTML
from bs4 import BeautifulSoup

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
        print(f"Unable to open configuration file named {config_file}")
        print("Please create a suitable configuration file, the default name is config.json")
        sys.exit()

def list_pages(course_id):
    global Verbose_Flag

    list_of_all_pages=[]

    # Use the Canvas API to get the list of pages for this course
    #GET /api/v1/courses/:course_id/pages

    url = f"{baseUrl}/courses/{course_id}/pages"
    payload={
        #'include[]': 'body' # include the body witht he response
    }

    if Verbose_Flag:
        print(f"{url=}")

    r = requests.get(url, headers = header, data=payload)
    if r.status_code == requests.codes.ok:
        page_response=r.json()

        for p_response in page_response:  
            list_of_all_pages.append(p_response)

        while r.links.get('next', False):
            r = requests.get(r.links['next']['url'], headers=header)  
            page_response = r.json()  
            for p_response in page_response:  
                list_of_all_pages.append(p_response)

    if Verbose_Flag:
        for p in list_of_all_pages:
            print(f"{p['title']}")

    if Verbose_Flag:
        print(f"{list_of_all_pages=}")
    return list_of_all_pages


def list_assignments(course_id):
    global Verbose_Flag

    list_of_all_assignments=[]

    # Use the Canvas API to get the list of assignments for this course
    #GET /api/v1/courses/:course_id/assignmenst

    url = f"{baseUrl}/courses/{course_id}/assignments"
    payload={
    }

    if Verbose_Flag:
        print(f"{url=}")

    r = requests.get(url, headers = header, data=payload)
    if r.status_code == requests.codes.ok:
        page_response=r.json()

        for p_response in page_response:  
            list_of_all_assignments.append(p_response)

        while r.links.get('next', False):
            r = requests.get(r.links['next']['url'], headers=header)  
            page_response = r.json()  
            for p_response in page_response:  
                list_of_all_assignments.append(p_response)

    if Verbose_Flag:
        for p in list_of_all_assignments:
            print(f"{p['name']}")

    if Verbose_Flag:
        print(f"{list_of_all_assignments=}")
    return list_of_all_assignments

def list_quizzes(course_id):
    global Verbose_Flag

    list_of_all_quizzes=[]

    # Use the Canvas API to get the list of quizzes for this course
    #GET /api/v1/courses/:course_id/quizzes

    url = f"{baseUrl}/courses/{course_id}/quizzes"
    payload={
    }

    if Verbose_Flag:
        print(f"{url=}")

    r = requests.get(url, headers = header, data=payload)
    if r.status_code == requests.codes.ok:
        page_response=r.json()

        for p_response in page_response:  
            list_of_all_quizzes.append(p_response)

        while r.links.get('next', False):
            r = requests.get(r.links['next']['url'], headers=header)  
            page_response = r.json()  
            for p_response in page_response:  
                list_of_all_quizzes.append(p_response)

    if Verbose_Flag:
        for p in list_of_all_quizzes:
            print(f"{p['title']}")

    return list_of_all_quizzes


def list_discussion_topics(course_id):
    global Verbose_Flag

    list_of_all_topics=[]

    # Use the Canvas API to get the list of discussion topics
    # GET /api/v1/courses/:course_id/discussion_topics


    url = f"{baseUrl}/courses/{course_id}/discussion_topics"
    payload={
    }

    if Verbose_Flag:
        print(f"{url=}")

    r = requests.get(url, headers = header, data=payload)
    if r.status_code == requests.codes.ok:
        page_response=r.json()

        for p_response in page_response:  
            list_of_all_topics.append(p_response)

        while r.links.get('next', False):
            r = requests.get(r.links['next']['url'], headers=header)  
            page_response = r.json()  
            for p_response in page_response:  
                list_of_all_topics.append(p_response)

    if Verbose_Flag:
        for p in list_of_all_topics:
            print(f"{p['title']}")

    return list_of_all_topics

def list_announcements(course_id):
    global Verbose_Flag

    list_of_all_announcements=[]

    end_date = date.today() + timedelta(days=10*7) # a term into the future
    start_date = date.today().replace(year=end_date.year-1)

    start_date_str=start_date.strftime('%Y-%m-%d')
    end_date_str=end_date.strftime('%Y-%m-%d')

    # Use the Canvas API to get the list of announcements
    # GET /api/v1/announcements
    url = f"{baseUrl}/announcements"

    payload={
        'context_codes[]': f'course_{course_id}',
        'active_only': True,
        'start_date': start_date_str, # yyyy-mm-dd or ISO 8601 YYYY-MM-DDTHH:MM:SSZ.
        'end_date': end_date_str
    }

    if Verbose_Flag:
        print(f"{url=}")

    r = requests.get(url, headers = header, data=payload)
    if r.status_code == requests.codes.ok:
        page_response=r.json()

        for p_response in page_response:  
            list_of_all_announcements.append(p_response)

        while r.links.get('next', False):
            r = requests.get(r.links['next']['url'], headers=header)  
            page_response = r.json()  
            for p_response in page_response:  
                list_of_all_announcements.append(p_response)

    if Verbose_Flag:
        print(f"{list_of_all_announcements}")

    return list_of_all_announcements

def process_pages(course_id, lang):
    global Verbose_Flag
    global testing_mode_flag # if set to True do _not_ write the modified contents

    print(f"processing pages for course {course_id}")

    page_list=list_pages(course_id)

    for p in page_list:
        # skip unpublished pages
        if not p['published']:
            continue

        print(f"processing page: '{p['title']}'")
        if Verbose_Flag:
            print(f"{p['url']=}")

        url = f"{baseUrl}/courses/{course_id}/pages/{p['url']}"

        payload={}
        r = requests.get(url, headers = header, data=payload)
        if Verbose_Flag:
            print(f"{r.status_code=}")
        if r.status_code == requests.codes.ok:
            page_response = r.json()

            # check that the response was not None
            pr=page_response["body"]
            if not pr:
                continue

            # modified the code to handle empty files - there is nothing to do
            if len(pr) == 0:
                continue

            if len(pr) > 0:
                encoded_output = bytes(page_response["body"], 'UTF-8')

            if Verbose_Flag:
                print(f"encoded_output before: {encoded_output}")

            # do the processing here
            transformed_encoded_output, changed=transform_body(encoded_output, lang)

            if testing_mode_flag or not changed: # do not do the update
                continue           

            # update the page
            payload={"wiki_page[body]": transformed_encoded_output}
            r = requests.put(url, headers = header, data=payload)
            if Verbose_Flag:
                print(f"{r.status_code=}")
            if r.status_code != requests.codes.ok:
                print(f"Error when updating page {p['title']} at {p['url']} ")
    
def process_assignments(course_id, lang):
    global Verbose_Flag
    global testing_mode_flag # if set to True do _not_ write the modified contents

    print(f"processing assignments for course {course_id}")

    assignment_list=list_assignments(course_id)

    for p in assignment_list:
        # skip unpublished assignments
        if not p['published']:
            continue

        print(f"processing assigngement: '{p['name']}'")
        if Verbose_Flag:
            print(f"{p['id']=}")

        # Get individual assignments by ID
        # GET /api/v1/courses/:course_id/assignments/:id
        url = f"{baseUrl}/courses/{course_id}/assignments/{p['id']}"

        payload={}
        r = requests.get(url, headers = header, data=payload)
        if Verbose_Flag:
            print(f"{r.status_code=}")
        if r.status_code == requests.codes.ok:
            page_response = r.json()

            # check that the response was not None
            pr=page_response["description"]
            if not pr:
                continue

            # modified the code to handle empty description - there is nothing to do
            if len(pr) == 0:
                continue

            if len(pr) > 0:
                encoded_output = bytes(page_response["description"], 'UTF-8')

            if Verbose_Flag:
                print(f"encoded_output before: {encoded_output}")

            # do the processing here
            transformed_encoded_output, changed=transform_body(encoded_output, lang)

            if testing_mode_flag or not changed: # do not do the update
                continue           

            # update the assignment's description
            payload={"assignment[description]": transformed_encoded_output}
            r = requests.put(url, headers = header, data=payload)
            if Verbose_Flag:
                print(f"{r.status_code=}")
            if r.status_code != requests.codes.ok:
                print(f"Error when updating assignment {p['name']} with ID: {p['id']} ")
    


def process_syllabus(course_id, lang):
    global Verbose_Flag
    global testing_mode_flag # if set to True do _not_ write the modified contents

    print(f"processing syllabus for course {course_id}")

    url=f"{baseUrl}/courses/{course_id}"
    if Verbose_Flag:
        print(f"{url=}")

    payload={
        'include[]': 'syllabus_body' # include the “syllabus_body” witht he response
    }


    r = requests.get(url, headers = header, data=payload)
    if Verbose_Flag:
        print("r.status_code: {}".format(r.status_code))
    if r.status_code == requests.codes.ok:
        page_response = r.json()
        if Verbose_Flag:
            print(f"{page_response}")
    else:
        print("Error in getting syllabus for course_id: {}".format(course_id))
        return False

    if len(page_response['syllabus_body']) > 0:
        encoded_output = bytes(page_response['syllabus_body'], 'UTF-8')

    if Verbose_Flag:
        print(f"encoded_output before: {encoded_output}")

    # do the processing here
    transformed_encoded_output, changed=transform_body(encoded_output, lang)

    if testing_mode_flag or not changed: # do not do the update
        return

    # update the page
    payload={"course[syllabus_body]": transformed_encoded_output}
    r = requests.put(url, headers = header, data=payload)
    if Verbose_Flag:
        print(f"{r.status_code=}")
        if r.status_code != requests.codes.ok:
            print(f"Error when updating syllabus at {url=} ")

def process_quizzes(course_id, lang):
    global Verbose_Flag
    global testing_mode_flag # if set to True do _not_ write the modified contents

    print(f"processing quizzes for course {course_id}")

    quizzes_list=list_quizzes(course_id)

    if Verbose_Flag:
        print(f"{quizzes_list=}")

    for p in quizzes_list:
        # skip unpublished quizzes
        if not p['published']:
            continue

        print(f"processing quiz: '{p['title']}'")
        if Verbose_Flag:
            print(f"{p['id']=}")

        # GET /api/v1/courses/:course_id/quizzes/:id
        url = f"{baseUrl}/courses/{course_id}/quizzes/{p['id']}"

        payload={}
        r = requests.get(url, headers = header, data=payload)
        if Verbose_Flag:
            print(f"{r.status_code=}")
        if r.status_code == requests.codes.ok:
            page_response = r.json()

            # check that the response was not None
            pr=page_response["description"]
            if not pr:
                continue

            # modified the code to handle empty description - there is nothing to do
            if len(pr) == 0:
                continue

            if len(pr) > 0:
                encoded_output = bytes(page_response["description"], 'UTF-8')

            if Verbose_Flag:
                print(f"encoded_output before: {encoded_output}")

            # do the processing here
            transformed_encoded_output, changed=transform_body(encoded_output, lang)

            if not testing_mode_flag and changed: # do not do the update
                # update the page
                payload={"quiz[description]": transformed_encoded_output}
                r = requests.put(url, headers = header, data=payload)
                if Verbose_Flag:
                    print(f"{r.status_code=}")
                if r.status_code != requests.codes.ok:
                    print(f"Error when updating page {p['title']} with ID {p['id']} ")

            # process the questions in this quiz
            list_of_all_questions=[]
            # GET /api/v1/courses/:course_id/quizzes/:quiz_id/questions
            url = f"{baseUrl}/courses/{course_id}/quizzes/{p['id']}/questions"
            payload={}
            if Verbose_Flag:
                print(f"{url=}")

            r = requests.get(url, headers = header, data=payload)
            if r.status_code == requests.codes.ok:
                page_response=r.json()

                for p_response in page_response:  
                    list_of_all_questions.append(p_response)

                while r.links.get('next', False):
                    r = requests.get(r.links['next']['url'], headers=header)  
                    page_response = r.json()  
                    for p_response in page_response:  
                        list_of_all_questions.append(p_response)

            if Verbose_Flag:
                for q in list_of_all_questions:
                    print(f"{q['question_name']}")
                        

            # for each quiz questions get the text fields and update as needed:

            for q in list_of_all_questions:
                payload={}      # initialize payload

                if Verbose_Flag:
                    print(f"{q=}")

                # GET /api/v1/courses/:course_id/quizzes/:quiz_id/questions/:id
                url = f"{baseUrl}/courses/{course_id}/quizzes/{p['id']}/questions/{q['id']}"

                question_text_fields = ['question_text',  'correct_comments_html', 'incorrect_comments_html', 'neutral_comments_html']
                for qtf in question_text_fields:
                    txt=q[qtf]
                    if txt and isinstance(txt, str) and len(txt) > 0:
                        if qtf == 'question_text' and txt[0] != '<': # if the question_txt is not in HTML, the wrap it in a <p> </p>
                            encoded_txt = bytes('<p>'+txt+'</p>', 'UTF-8')
                        else:
                            encoded_txt = bytes(txt, 'UTF-8')

                        if Verbose_Flag:
                            print(f"before: {encoded_txt}")

                        # do the processing here
                        transformed_encoded_output, changed=transform_body(encoded_txt, lang)
                        if changed:
                            payload[f'question[{qtf}]'] = transformed_encoded_output

                # "answers": null
                changed_answer=False
                updated_answers=[]
                for ans in q['answers']:
                    txt=ans.get('html', None)
                    if txt and isinstance(txt, str) and len(txt) > 0:
                        encoded_txt = bytes(txt, 'UTF-8')

                        if Verbose_Flag:
                            print(f"before: {encoded_txt}")

                        # do the processing here
                        transformed_encoded_output, changed=transform_body(encoded_txt, lang)
                        if changed:
                            ans['html']=transformed_encoded_output
                            changed_answer=True
                        updated_answers.append(ans)

                # Note the special format that has to be used to updated the answers - otherwise you get a 500 error.
                # See https://github.com/instructure/canvas-lms/issues/2045
                # and https://community.canvaslms.com/t5/Canvas-Developers-Group/Canvas-API-call-to-update-an-existing-quiz-question-fails-with/m-p/558693
                if changed_answer:
                    for idx, a in enumerate(updated_answers):
                        for prop in a.keys():
                            payload[f'question[answers][{idx}][{prop}]']=a[prop]

                if Verbose_Flag:
                    print(f"{payload=}")

                if not testing_mode_flag and len(payload) > 0: # do the update
                    # update the page
                    r = requests.put(url, headers = header, data=payload)
                    if Verbose_Flag:
                        print(f"{r.status_code=}")
                    if r.status_code != requests.codes.ok:
                        print(f"Error when updating page {q['question_name']} with ID {q['id']} ")

def process_discussions(course_id, lang):
    global Verbose_Flag
    global testing_mode_flag # if set to True do _not_ write the modified contents

    print(f"processing discussions for course {course_id}")

    discussion_list=list_discussion_topics(course_id)

    if Verbose_Flag:
        print(f"{discussion_list=}")

    for p in discussion_list:
        # skip unpublished discussions
        if not p['published']:
            continue

        print(f"processing discussion topic: '{p['title']}'")
        if Verbose_Flag:
            print(f"{p['id']=}")

        # GET /api/v1/courses/:course_id/discussion_topics/:id
        url = f"{baseUrl}/courses/{course_id}/discussion_topics/{p['id']}"

        payload={}
        r = requests.get(url, headers = header, data=payload)
        if Verbose_Flag:
            print(f"{r.status_code=}")
        if r.status_code == requests.codes.ok:
            page_response = r.json()

            # check that the response was not None
            pr=page_response["message"]
            if not pr:
                continue

            # modified the code to handle empty message - there is nothing to do
            if len(pr) == 0:
                continue

            if len(pr) > 0:
                encoded_output = bytes(page_response["message"], 'UTF-8')

            if Verbose_Flag:
                print(f"encoded_output before: {encoded_output}")

            # do the processing here
            transformed_encoded_output, changed=transform_body(encoded_output, lang)

            if not testing_mode_flag and changed: # do not do the update
                # update the page
                payload={"message": transformed_encoded_output}
                r = requests.put(url, headers = header, data=payload)
                if Verbose_Flag:
                    print(f"{r.status_code=}")
                if r.status_code != requests.codes.ok:
                    print(f"Error when updating page {p['title']} with ID {p['id']} ")

            # process the entires under this discussion topic
            list_of_all_entries=[]
            # GET /api/v1/courses/:course_id/discussion_topics/:topic_id/entries
            url = f"{baseUrl}/courses/{course_id}/discussion_topics/{p['id']}/entries"
            payload={}
            if Verbose_Flag:
                print(f"URL for entries {url=}")

            r = requests.get(url, headers = header, data=payload)
            if r.status_code == requests.codes.ok:
                page_response=r.json()

                for p_response in page_response:  
                    list_of_all_entries.append(p_response)

                while r.links.get('next', False):
                    r = requests.get(r.links['next']['url'], headers=header)  
                    page_response = r.json()  
                    for p_response in page_response:  
                        list_of_all_entries.append(p_response)

            if Verbose_Flag:
                print(f"{list_of_all_entries=}")
                        

            # for each entry get the message and update as needed:
            recent_replies=[]
            for q in list_of_all_entries:
                payload={}      # initialize payload

                if Verbose_Flag:
                    print(f"{q=}")
                if q.get('recent_replies', None):
                    for rep in q['recent_replies']:
                        recent_replies.append(rep)

                txt=q['message']
                if txt and isinstance(txt, str) and len(txt) > 0:
                    encoded_txt = bytes(txt, 'UTF-8')

                    if Verbose_Flag:
                        print(f"before: {encoded_txt}")

                    # do the processing here
                    transformed_encoded_output, changed=transform_body(encoded_txt, lang)
                    if changed:
                        payload['message'] = transformed_encoded_output

                if Verbose_Flag:
                    print(f"{payload=}")

                if not testing_mode_flag and len(payload) > 0: # do the update
                    # update the entry
                    url = f"{baseUrl}/courses/{course_id}/discussion_topics/{p['id']}/entries/{q['id']}"
                    r = requests.put(url, headers = header, data=payload)
                    if Verbose_Flag:
                        print(f"{r.status_code=}")
                    if r.status_code != requests.codes.ok:
                        print(f"Error when updating entry {q['message']} with ID {q['id']} ")

            for q in recent_replies:
                payload={}      # initialize payload

                if Verbose_Flag:
                    print(f"{q=}")

                txt=q['message']
                if txt and isinstance(txt, str) and len(txt) > 0:
                    encoded_txt = bytes(txt, 'UTF-8')

                    if Verbose_Flag:
                        print(f"before: {encoded_txt}")

                    # do the processing here
                    transformed_encoded_output, changed=transform_body(encoded_txt, lang)
                    if changed:
                        payload['message'] = transformed_encoded_output

                if Verbose_Flag:
                    print(f"{payload=}")

                if not testing_mode_flag and len(payload) > 0: # do the update
                    # update the entry
                    url = f"{baseUrl}/courses/{course_id}/discussion_topics/{p['id']}/entries/{q['id']}"
                    r = requests.put(url, headers = header, data=payload)
                    if Verbose_Flag:
                        print(f"{r.status_code=}")
                    if r.status_code != requests.codes.ok:
                        print(f"Error when updating entry {q['message']} with ID {q['id']} ")

def process_announcements(course_id, lang):
    global Verbose_Flag
    global testing_mode_flag # if set to True do _not_ write the modified contents

    print(f"processing announcements for course {course_id}")

    announcement_list=list_announcements(course_id)

    if Verbose_Flag:
        print(f"{announcement_list=}")

    for p in announcement_list:
        if not isinstance(p, dict): # check that it is a dict, as I found one instance where this was a string!
            continue

        print(f"processing announcement: '{p['title']}'")
        # skip unpublished announcements
        if not p.get('published', None):
            print(f"no published field for {p}")
            continue

        if Verbose_Flag:
            print(f"{p['id']=}")

        # GET /api/v1/courses/:course_id/discussion_topics/:id
        url = f"{baseUrl}/courses/{course_id}/discussion_topics/{p['id']}"

        payload={}
        r = requests.get(url, headers = header, data=payload)
        if Verbose_Flag:
            print(f"{r.status_code=}")
        if r.status_code == requests.codes.ok:
            page_response = r.json()

            # check that the response was not None
            pr=page_response["message"]
            if not pr:
                continue

            # modified the code to handle empty message - there is nothing to do
            if len(pr) == 0:
                continue

            if len(pr) > 0:
                encoded_output = bytes(page_response["message"], 'UTF-8')

            if Verbose_Flag:
                print(f"encoded_output before: {encoded_output}")

            # do the processing here
            transformed_encoded_output, changed=transform_body(encoded_output, lang)

            if not testing_mode_flag and changed: # do not do the update
                # update the page
                payload={"message": transformed_encoded_output}
                r = requests.put(url, headers = header, data=payload)
                if Verbose_Flag:
                    print(f"{r.status_code=}")
                if r.status_code != requests.codes.ok:
                    print(f"Error when updating page {p['title']} with ID {p['id']} ")


            # process the entires under this announcement as if it were a discussion topic
            list_of_all_entries=[]
            # GET /api/v1/courses/:course_id/discussion_topics/:topic_id/entries
            url = f"{baseUrl}/courses/{course_id}/discussion_topics/{p['id']}/entries"
            payload={}
            if Verbose_Flag:
                print(f"URL for entries {url=}")

            r = requests.get(url, headers = header, data=payload)
            if r.status_code == requests.codes.ok:
                page_response=r.json()

                for p_response in page_response:  
                    list_of_all_entries.append(p_response)

                while r.links.get('next', False):
                    r = requests.get(r.links['next']['url'], headers=header)  
                    page_response = r.json()  
                    for p_response in page_response:  
                        list_of_all_entries.append(p_response)

            if Verbose_Flag:
                print(f"{list_of_all_entries=}")
                        

            # for each entry get the message and update as needed:
            recent_replies=[]
            for q in list_of_all_entries:
                payload={}      # initialize payload

                if Verbose_Flag:
                    print(f"{q=}")

                for rep in q.get('recent_replies', None):
                    recent_replies.append(rep)

                txt=q['message']
                if txt and isinstance(txt, str) and len(txt) > 0:
                    encoded_txt = bytes(txt, 'UTF-8')

                    if Verbose_Flag:
                        print(f"before: {encoded_txt}")

                    # do the processing here
                    transformed_encoded_output, changed=transform_body(encoded_txt, lang)
                    if changed:
                        payload['message'] = transformed_encoded_output

                if Verbose_Flag:
                    print(f"{payload=}")

                if not testing_mode_flag and len(payload) > 0: # do the update
                    # update the entry
                    url = f"{baseUrl}/courses/{course_id}/discussion_topics/{p['id']}/entries/{q['id']}"
                    r = requests.put(url, headers = header, data=payload)
                    if Verbose_Flag:
                        print(f"{r.status_code=}")
                    if r.status_code != requests.codes.ok:
                        print(f"Error when updating entry {q['message']} with ID {q['id']} ")

            for q in recent_replies:
                payload={}      # initialize payload

                if Verbose_Flag:
                    print(f"{q=}")

                txt=q['message']
                if txt and isinstance(txt, str) and len(txt) > 0:
                    encoded_txt = bytes(txt, 'UTF-8')

                    if Verbose_Flag:
                        print(f"before: {encoded_txt}")

                    # do the processing here
                    transformed_encoded_output, changed=transform_body(encoded_txt, lang)
                    if changed:
                        payload['message'] = transformed_encoded_output

                if Verbose_Flag:
                    print(f"{payload=}")

                if not testing_mode_flag and len(payload) > 0: # do the update
                    # update the entry
                    url = f"{baseUrl}/courses/{course_id}/discussion_topics/{p['id']}/entries/{q['id']}"
                    r = requests.put(url, headers = header, data=payload)
                    if Verbose_Flag:
                        print(f"{r.status_code=}")
                    if r.status_code != requests.codes.ok:
                        print(f"Error when updating entry {q['message']} with ID {q['id']} ")



def process_course(course_id, lang):
    global Verbose_Flag
    global testing_mode_flag
    # for the different type of resources, call the relevant processing function 

    if not testing_mode_flag:
        # start by processing Pages
        process_pages(course_id, lang)

        # process the syllabus
        process_syllabus(course_id, lang)

        # Process the assignments
        process_assignments(course_id, lang)

        # Process (classic) qquizzes
        process_quizzes(course_id, lang)

        # Process Discussions
        process_discussions(course_id, lang)

        # Process Announcements
        process_announcements(course_id, lang)

def transform_body(html_content, lang):
    global Verbose_Flag
    if Verbose_Flag:
        print(f"{html_content=}")

    changed_flag=False

    soup = BeautifulSoup(html_content, 'html.parser')

    # Find all top level elements _without_ a lang attribute
    top_level_elements=soup.find_all(attrs={'lang':None}, recursive=False)
    if len(top_level_elements) >= 1:
        if Verbose_Flag:
            print(f"{len(top_level_elements)=}")

        changed_flag=True
        for node in top_level_elements:
            node.attrs['lang']=lang

        html_content = str(soup)
        if Verbose_Flag:
            print(f"transformed {html_content=}")

    return html_content, changed_flag



def main():
    global Verbose_Flag
    global testing_mode_flag # if set to True do _not_ write the modified contents

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
                      help="Set test mode"
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

    testing_mode_flag=options.testing

    initialize(options)

    if (len(remainder) < 2):
        print("Insuffient arguments - must provide course_id language")
        return
    
    course_id=remainder[0]

    lang=None
    if (len(remainder) == 2):
        lang=remainder[1]
    else:
        print("You must specify a language code - see RFC 5646 https://datatracker.ietf.org/doc/html/rfc5646")
        return

    process_course(course_id, lang)


if __name__ == "__main__": main()
