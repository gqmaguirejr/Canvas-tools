#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# ./cefr_tag_a_course.py course_id
#
# Purpose: To go throught a course and add HTML span tags with a CEFR related attribute to relevant elements for each word (or phrase) in the content
#
#
### Input
# With the option "-v" or "--verbose" you get lots of output - showing in detail the operations of the program.
# With the option "-t" or "--testing", the program does not update the strings with the modified HTML.
# 
# Outputs:
# with the option "-v" or "--verbose" you get lots of output - showing in detail the operations of the program
#
# Can also be called with an alternative configuration file:
# ./language_tag_a_course.py --config config-test.json  course_id lang
#
# Example:
# ./cefr_tag_a_course.py 751
#
#
# Notes
# Current the program will only operate on Pages and Syallbus
# 
# G. Q. Maguire Jr.
#
# based on earlier language_tag_a_course.py
#
# 2024-06-29
#

import requests, time
import pprint
import optparse
import sys
import json
import re

from datetime import datetime, date, timedelta
import isodate                  # for parsing ISO 8601 dates and times
import pytz                     # for time zones

# Use Python Pandas to create XLSX files
import pandas as pd

# use BeautifulSoup to process the HTML
from bs4 import BeautifulSoup

import nltk
from nltk import RegexpParser
from nltk.tokenize import word_tokenize
# for the following two you will (once) have to do: nltk.download('bcp47')
from nltk.langnames import langname
from nltk.langnames import langcode

import html


import sys
sys.path.append('/z3/maguire/Canvas/Canvas-tools')  # Include the path to module_folder
sys.path.append('/home/maguire/Canvas/Canvas-tools')

#  as common_English_words, common_swedish_words, common_swedish_technical_words
import common_english_and_swedish
import common_acronyms
import miss_spelled_to_correct_spelling
import diva_merged_words
import diva_corrected_abstracts
import AVL_words_with_CEFR
import common_acronyms

# width to use for outputting numeric values
Numeric_field_width=7

# Define a grammar for basic chunking
grammar = r""" NP: {<DT>?<JJ.*>*<NN.*>+}   # Chunk sequences of DT, JJ, NN
                   {<PRP>}                # Pronouns
                   {<PRP\$><NN.*>+}       # Possessive pronouns followed by nouns
                   {<CD><NN.*>+}          # Cardinal numbers followed by nouns
                   {<NN.*><IN><NN.*>+}    # Nouns followed by a preposition and more nouns
               VP: {<VB.*>+}             # Chunk all verbs together
                   {<MD><VB.*>+}        # Chunk modal verbs with main verbs
                   {<RB.*>?<VB.*>+}     # Allow optional adverbs before verbs
"""

# Create a parser with the grammar
grammar_parser = RegexpParser(grammar)


# entries in the dict will have the form: 'acronym': ['expanded form 1', 'expanded form 2',  ... ]
well_known_acronyms=dict()

def setup_acronyms():
    global well_known_acronyms
    for e in common_acronyms.well_known_acronyms_list:
        if not isinstance(e, list):
            print(f"{e=}")

        if len(e) >= 1:
            ack=e[0]
            if len(e) >= 2:
                d=e[1]
                current_entry=well_known_acronyms.get(ack, list())
                current_entry.append(d)
                well_known_acronyms[ack]=current_entry

special_dicts = {
    'common_English_words': common_english_and_swedish.common_English_words,
    'common_swedish_words': common_english_and_swedish.common_swedish_words,
    'common_swedish_technical_words': common_english_and_swedish.common_swedish_technical_words,
    'names_of_persons': common_english_and_swedish.names_of_persons,
    'place_names': common_english_and_swedish.place_names,
    'company_and_product_names': common_english_and_swedish.company_and_product_names,
    'common_programming_languages': common_english_and_swedish.common_programming_languages,
    'well_known_acronyms': well_known_acronyms, # common_english_and_swedish.well_known_acronyms,
    'common_units': common_english_and_swedish.common_units,
    'abbreviations_ending_in_period': common_english_and_swedish.abbreviations_ending_in_period,
    'programming_keywords': common_english_and_swedish.programming_keywords,
    'thousand_most_common_words_in_English_old': common_english_and_swedish.thousand_most_common_words_in_English_old,
    'common_danish_words': common_english_and_swedish.common_danish_words,
    'common_german_words': common_english_and_swedish.common_german_words,
    'common_icelandic_words': common_english_and_swedish.common_icelandic_words,
    'common_latin_words': common_english_and_swedish.common_latin_words,
    'common_portuguese_words': common_english_and_swedish.common_portuguese_words,
    'common_finnish_words': common_english_and_swedish.common_finnish_words,
    'common_spanish_words': common_english_and_swedish.common_spanish_words,
    'common_italian_words': common_english_and_swedish.common_italian_words,
}

footer="""<hr>
<footer>
<p class"CEFRColorCodes">Color codes for CEFR levels: <span class="CEFRA1">A1</span>, <span class="CEFRA2">A2</span> , <span class="CEFRB1">B1</span>,
  <span class="CEFRB2">B2</span>, <span class="CEFRC1">C1</span>, <span class="CEFRC2">C2</span>,
  <span class="CEFRXX">XX</span>, and <span class="CEFRNA">NA</span>.</p>
<p>Automatically generated from the HTML for the page <a href="https://canvas.kth.se/courses/31168/pages/welcome-to-the-internetworking-course">https://canvas.kth.se/courses/31168/pages/welcome-to-the-internetworking-course</a>.
</footer>
"""
style_info="""<style>
  .CEFRA1{
    background-color: rgba(0, 255, 8,  0.3);
     
  }
  .CEFRA2{
      background-color: rgba(0, 251, 100,  0.8);
  }
  .CEFRB1{
    background-color: rgba(0, 200, 251, 0.3);
  }
  .CEFRB2{
      background-color: rgba(0, 151, 207,  0.8);
  }
  .CEFRC1{
    background-color: rgba(251, 0, 0, 0.3);
  }
  .CEFRC2{
    background-color: rgba(251, 0, 0, 0.8);
  }
  .CEFRXX{
    background-color: #9a9a9a;
  }
  .CEFRNA{
    #background-color: royalblue;
    background-color: transparent;
  }
  .word-CC{
    background-color: rgba(200, 100, 100, 0.3);
  }
  .word-CD{
    background-color: rgba(250, 100, 100, 0.3);
  }
  .word-DT{
    background-color: rgba(200, 000, 200, 0.3);
  }
  .word-EX{
    background-color: rgba(200, 100, 200, 0.3);
  }
  .word-IN{
    background-color: rgba(200, 80, 200, 0.3);
  }
  .word-JJ{
    background-color: rgba(250, 210, 000, 0.8);
  }
  .word-MD{
    background-color: rgba(250, 100, 100, 0.3);
  }
  .word-NN{
    background-color: rgba(251, 0, 0, 0.3);
  }
  .word-NNP{
    background-color: rgba(251, 0, 0, 0.8);
  }
  .word-NNS{
    background-color: rgba(255, 50, 0, 0.8);
  }
  .word-PRP{
    background-color: rgba(100, 100, 8,  0.3);
  }
  .word-PRP§{
    background-color: rgba(120, 120, 88,  0.3);
  }
  .word-RBR{
    background-color: rgba(100, 140, 80,  0.8);
  }
  .word-RB{
    background-color: rgba(100, 140, 8,  0.3);
  }
  .word-TO{
    background-color: rgba(100, 200, 8,  0.3);
  }
  .word-VB{
    background-color: rgba(0, 210, 8,  0.3);
  }
  .word-VBD{
    background-color: rgba(0, 240, 58,  0.8);
  }
  .word-VBG{
    background-color: rgba(0, 235, 80,  0.3);
  }
  .word-VBN{
    background-color: rgba(0, 220, 100,  0.3);
  }
  .word-VBP{
    background-color: rgba(0, 210, 128,  0.3);
  }
  .word-VBZ{
    background-color: rgba(0, 200, 8,  0.3);
  }
  .word-WDT{
    background-color: rgba(0, 200, 251, 0.2);
  } 
  .word-WP{
    background-color: rgba(0, 200, 251, 0.5);
  }
  .word-WRB{
    background-color: rgba(0, 200, 251, 0.8);
  }

</style>
"""


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

def process_pages(course_id):
    global Verbose_Flag
    global testing_mode_flag # if set to True do _not_ write the modified contents

    print(f"processing pages for course {course_id}")

    page_list=list_pages(course_id)

    for p in page_list:
        # skip unpublished pages
        if not p['published']:
            continue

        print(f"processing page: '{p['title']}'")
        if p['title'] == 'Reference Books and Other Materials': # skip this page for now
            continue
        if p['title'] ==  'Ethics / Code of Honor and Regulations':
            continue
        if p['title'] ==  'Overview':
            continue
        if p['title'] == 'Course home page':
            continue
        if p['title'] != 'Welcome to II2210':
            continue
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
                #encoded_output = bytes(page_response["body"], 'UTF-8')
                encoded_output = page_response["body"]

            if Verbose_Flag:
                print(f"encoded_output before: {encoded_output}")

            # do the processing here
            transformed_encoded_output, changed=transform_body(encoded_output)

            if testing_mode_flag or not changed: # do not do the update
                continue           

            # update the page
            payload={"wiki_page[body]": transformed_encoded_output}
            r = requests.put(url, headers = header, data=payload)
            if Verbose_Flag:
                print(f"{r.status_code=}")
            if r.status_code != requests.codes.ok:
                print(f"Error when updating page {p['title']} at {p['url']} ")
    
def process_assignments(course_id):
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
            transformed_encoded_output, changed=transform_body(encoded_output)

            if testing_mode_flag or not changed: # do not do the update
                continue           

            # update the assignment's description
            payload={"assignment[description]": transformed_encoded_output}
            r = requests.put(url, headers = header, data=payload)
            if Verbose_Flag:
                print(f"{r.status_code=}")
            if r.status_code != requests.codes.ok:
                print(f"Error when updating assignment {p['name']} with ID: {p['id']} ")
    


def process_syllabus(course_id):
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
    transformed_encoded_output, changed=transform_body(encoded_output)

    if testing_mode_flag or not changed: # do not do the update
        return

    # update the page
    payload={"course[syllabus_body]": transformed_encoded_output}
    r = requests.put(url, headers = header, data=payload)
    if Verbose_Flag:
        print(f"{r.status_code=}")
        if r.status_code != requests.codes.ok:
            print(f"Error when updating syllabus at {url=} ")

def process_quizzes(course_id):
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
            transformed_encoded_output, changed=transform_body(encoded_output)

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
                        transformed_encoded_output, changed=transform_body(encoded_txt)
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
                        transformed_encoded_output, changed=transform_body(encoded_txt)
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

def process_discussions(course_id):
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
            transformed_encoded_output, changed=transform_body(encoded_output)

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
                    transformed_encoded_output, changed=transform_body(encoded_txt)
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
                    transformed_encoded_output, changed=transform_body(encoded_txt)
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

def process_announcements(course_id):
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
            transformed_encoded_output, changed=transform_body(encoded_output)

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
                    transformed_encoded_output, changed=transform_body(encoded_txt)
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
                    transformed_encoded_output, changed=transform_body(encoded_txt)
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



def process_course(course_id):
    global Verbose_Flag
    global testing_mode_flag
    # for the different type of resources, call the relevant processing function 

    # start by processing Pages
    process_pages(course_id)

    # process the syllabus
    #process_syllabus(course_id)

    # Process the assignments
    #process_assignments(course_id)

    # Process (classic) qquizzes
    #process_quizzes(course_id)

    # Process Discussions
    #process_discussions(course_id)

    # Process Announcements
    #process_announcements(course_id)

CEFR_labels=['CEFRA1', 'CEFRA2', 'CEFRB1', 'CEFRB2', 'CEFRC1', 'CEFRC2', 'CEFRXX', 'CEFRNA']
def remove_existing_CEFR_markup(s):
    elems=s.find_all('style')
    for p in elems:
        p.decompose()
    
    for cl in CEFR_labels:
        elems=s.find_all('span', attrs={'class' : cl})
        for p in elems:
            p.unwrap()
    return s


# The following function was developed on 2024-06-30 in interaction with Google Gemin Advanced
# It is based on my suggestion to compute the POS for words and then back substitute the tagged
# version into the text of the html_content - rather that struggling with BeautifulSoup
def pos_tag_html_with_context(html_content):
    """
    POS tags HTML content, considering context by grouping text within elements.
    Preserves all HTML markup and avoids incorrect spacing.

    Args:
        html_content (str): The HTML content to be tagged.

    Returns:
        str: The HTML content with POS tags inserted around words.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    text = soup.get_text()  # Extract text from HTML
    # Tokenize and POS tag words in the extracted text
    # using regular expression tokenizer
    words = nltk.regexp_tokenize(text, r"\w+|[^\w\s]")
    tagged_words = nltk.pos_tag(words)
    # Remove the period from the list of words
    try:
        period_index = words.index(".")
        del words[period_index]
        del tagged_words[period_index]
    except ValueError:
        pass
    #
    # Zip the original and tagged words together
    tagged_word_list = list(zip(words, tagged_words))
    #
    # Create a regular expression to match the words in order
    pattern = re.compile(r"|".join(map(re.escape, words)))
    # Function to replace words with their tagged versions
    def replace_with_tags(match, count=[0]):
        # count the number of time tag_words has been called
        # count is a list to be used as a mutable default argument so it will retain its value after every function call
        word = match.group(0)
        if count[0] < len(tagged_word_list):
            _, (tagged_word, tag) = tagged_word_list[count[0]]
            if tagged_word == word:
                # Only return a tagged word if it is the next tagged word in tagged_word_list
                count[0] += 1
                return f"<{tag}>{html.escape(word)}</{tag}>"
        return word  # Return the original word if no tag was found (e.g., punctuation)
    #
    # Replace words in the original HTML content with their tagged versions
    tagged_html = pattern.sub(replace_with_tags, html_content)
    #
    return html.unescape(tagged_html) # Decode the html before returning the string

def get_unique_languages(html_content):
    """
    Extracts all unique language codes used in lang attributes from an HTML string.

    Args:
        html_content (str): The HTML content to process.

    Returns:
        set: A set of unique language codes found in the HTML.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    #
    # Find all elements with a 'lang' attribute
    lang_elements = soup.find_all(lambda tag: tag.has_attr('lang'))
    #    
    # Collect all unique language values from these elements 
    languages = {tag['lang'] for tag in lang_elements}
    #
    return languages

def process_my_string(s, tagged_words, lang, i):
    global Verbose_Flag
    if Verbose_Flag:
        print(f"process_my_string({s}, tagged_words, {lang}, {i=})")
    if i >= len(tagged_words):
        return s
    word, tag = tagged_words[i]

    prefix, word, suffix = s.partition(word)
    if word:
        cefr_level, source = get_cefr_level(lang, word, tag, None)
        if cefr_level == 'XX':
            return prefix+f'{html.escape(word)}'+process_my_string(suffix, tagged_words, lang, i+1)
        else:
            return prefix+f'<span class="CEFR{cefr_level}">{html.escape(word)}</span>'+process_my_string(suffix, tagged_words, lang, i+1)
    else:
        return s

def get_text_by_language(html_content, target_lang):
    """
    Extracts text content in a specific language from an HTML string.

    Args:
        html_content (str): The HTML content to process.
        target_lang (str): The target language code (e.g., "en", "fr", "es").

    Returns:
        str: The extracted text content in the target language.
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find all elements with the 'lang' attribute matching the target language
    elements = soup.find_all(lang=target_lang)

    # Extract and combine the text content from those elements
    text = ' '.join(element.get_text(separator=' ', strip=True) for element in elements)

    return text

# NLTK uses ISO 639 code for languages
# more specifically the ISO 639-3 three letter codes
# while we assume the content is language tagged according to RFC 5646
# RFC 5646 states in its list of rules for the primary language subtag:
#    1. Two-character primary language subtags were defined in the IANA
#       registry according to the assignments found in the standard "ISO
#       639-1:2002, Codes for the representation of names of languages --
#       Part 1: Alpha-2 code" [ISO639-1], or using assignments
#       subsequently made by the ISO 639-1 registration authority (RA) or
#       governing standardization bodies.
def convert_to_ISO_639_code(lang):
    return langcode(langname(lang), typ=3 )

def tokenize_and_CEFR_tag_html_sentences(html_content):
    global Verbose_Flag
    """
    Based on POS and CEFR information for words tag HTML content, considering context by grouping text within elements.
    Preserves all HTML markup and avoids incorrect spacing.

    Args:
        html_content (str): The HTML content to be tagged.

    Returns:
        str: The HTML content with span tags with CEFR attribute inserted around words.
    """
    languages_in_content=get_unique_languages(html_content)

    tagged_html=html_content
    for lang in languages_in_content:
        #soup = BeautifulSoup(html_content, 'html.parser')
        #text = soup.get_text()  # Extract text from HTML
        text=get_text_by_language(tagged_html, lang)
        if Verbose_Flag:
            print(f"{lang=} {text=}")
        # Tokenize and POS tag words in the extracted text
        # using regular expression tokenizer
        words = nltk.regexp_tokenize(text, r"\w+|[^\w\s]")
        tagged_words = nltk.pos_tag(words, lang=convert_to_ISO_639_code(lang))
        if Verbose_Flag:
            print(f"{words=} {tagged_words=}")
        # Remove the punctuation from the list of words
        for w in words:
            for ci in [ ',', '.', ':', '$', '--', "``", "''", '(', ')', '[', ']', '{', '}', '<', '>', '-' ]:
                try:
                    period_index = words.index(ci)
                    del words[period_index]
                    del tagged_words[period_index]
                except ValueError:
                    pass
        if Verbose_Flag:
            print(f"after cleaning {tagged_words=}")
        #
        # Zip the original and tagged words together
        tagged_word_list = list(zip(words, tagged_words))
        if Verbose_Flag:
            print(f"{tagged_word_list=}")
            #
        tagged_html=process_my_string(tagged_html, tagged_words, lang, 0)
        if Verbose_Flag:
            print(f"before cleaning {tagged_html=}")


    tagged_html=clean_tagged_html(tagged_html)
    if Verbose_Flag:
        print(f"{tagged_html=}")
    return html.unescape(tagged_html) # Decode the html before returning the string

# replace "<span class="CEFRA1">i</span>.<span class="CEFRXX">e</span>."
# with "<span lang="latin" class="CEFRA1">i.e.</span>"

def simplify_cefr_span_of_float(html_text):
    """
    Simplifies HTML spans with CEFR level and number into a single span.

    Replace floats such as
         <span class="CEFRXX">1</span>.<span class="CEFRXX">5</span>
    with <span class="CEFRA2">1.5</span>

    Args:
        html_text: The HTML string to modify.

    Returns:
        The modified HTML string with simplified CEFR spans.
    """
    pattern = r'<span class="CEFR\w+">(\d+)</span>\.<span class="CEFR\w+">(\d+)</span>'
    replacement = r'<span class="CEFRA2">\1.\2</span>'  
    # Use re.sub with the count=0 argument to replace all occurrences
    # 
    modified_text = re.sub(pattern, replacement, html_text, count=0)
    return modified_text

#
# Define the mapping of abbreviations to CEFR levels and language
abbreviation_levels = {
    'e.g.': {'cefr': 'B2', 'lang': 'la'},
    'etc.': {'cefr': 'B1', 'lang': 'la'},
    'i.a.': {'cefr': 'C1', 'lang': 'la'},
    'i.e.': {'cefr': 'B2', 'lang': 'la'},
    'i.g.': {'cefr': 'C2', 'lang': 'la'},
    'w.r.t.': {'cefr': 'C1', 'lang': 'en'},
    'M.Sc.': {'cefr': 'B2', 'lang': 'en', 'note': 'Master of Science (academic context)'},
    'M.S.E.E.': {'cefr': 'C1', 'lang': 'en', 'note': 'Master of Science in Electrical Engineering (highly specialized academic context)'},
    'Mr.': {'cefr': 'A1', 'lang': 'en', 'note': 'Mister (title of respect for men)'},
    'Mrs.': {'cefr': 'A1', 'lang': 'en', 'note': 'Missus (title of respect for married women('},
    'Ms.': {'cefr': 'A1', 'lang': 'en', 'note': 'Miss (title of respect for women, marital status unknown)'},
    'N.J.': {'cefr': 'B2', 'lang': 'en', 'note': 'New Jersey, US state'},
    'Ph.': {'cefr': 'C1', 'lang': 'en', 'note': 'Physics (academic/scientific context)'},
    'Ph.D.': {'cefr': 'B2', 'lang': 'en', 'note': 'Doctor of Philosophy (academic context)'},
    'Phys.': {'cefr': 'C1', 'lang': 'en', 'note': 'Physics (academic/scientific context)'},
    'Prof.': {'cefr': 'B2', 'lang': 'en', 'note': 'Professor (academic title)'},
    'prof.': {'cefr': 'B2', 'lang': 'en', 'note': 'Professor (academic title)'}, # informal abbreviation
    'Q.E.D.': {'cefr': 'C2', 'lang': 'la', 'note': 'quod erat demonstrandum'},  # used in formal proofs
    'S.A.': {'cefr': 'B2', 'lang': 'fr', 'note': 'Société Anonyme '}, # (French), or limited company.
    'S.A.S.': {'cefr': 'B2', 'lang': 'fr', 'note': 'Société par Actions Simplifiée'}, # simplified joint-stock company.
    'Tekn.': {'cefr': 'C1', 'lang': 'sv', 'note': 'Teknologie (academic title)'},
    'U.K.': {'cefr': 'A2', 'lang': 'en', 'note': 'United Kingdom'},
    'U.S.': {'cefr': 'A2', 'lang': 'en', 'note': 'United States'},
    'U.S.A.': {'cefr': 'A2', 'lang': 'en', 'note': 'United States of America'},
    'U.S.C.': {'cefr': 'C1', 'lang': 'en', 'note': 'United States Code (law), or University of Southern California (higher education)'},

    'A.I.': {'cefr': 'B1', 'lang': 'en', 'note': 'Artificial Intelligence'}, 
    'Assoc.': {'cefr': 'B2', 'lang': 'en', 'note': 'Associate'}, 
    'B.A.': {'cefr': 'B2', 'lang': 'en', 'note': 'Bachelor of Arts'},
    'B.S.': {'cefr': 'B2', 'lang': 'en', 'note': 'Bachelor of Science'},
    'Corp.': {'cefr': 'B2', 'lang': 'en', 'note': 'Corporation'},
    'D.A.': {'cefr': 'C1', 'lang': 'en', 'note': 'District Attorney (legal context)'},
    'D.C.': {'cefr': 'B2', 'lang': 'en', 'note': 'Washington D.C.'},
    'Dr.': {'cefr': 'A2', 'lang': 'en', 'note': 'Doctor (title)'},
    'E.U.': {'cefr': 'B1', 'lang': 'en', 'note': 'European Union'},
    'G.Q.': {'cefr': 'C1', 'lang': 'en', 'note': "Gentlemen's Quarterly (magazine) or initials"}, 
    'I.T.': {'cefr': 'B1', 'lang': 'en', 'note': 'Information Technology'},
    'Inc.': {'cefr': 'B2', 'lang': 'en', 'note': 'Incorporated (business)'},
    'Jr.': {'cefr': 'A2', 'lang': 'en', 'note': 'Junior (suffix for names)'},
    'Ltd.': {'cefr': 'B2', 'lang': 'en', 'note': 'Limited (company)'},
    'M.A.': {'cefr': 'B2', 'lang': 'en', 'note': 'Master of Arts'},
    'M.I.T.': {'cefr': 'B2', 'lang': 'en', 'note': 'Massachusetts Institute of Technology'},
    'a.k.a.': {'cefr': 'B2', 'lang': 'en', 'note': 'Also known as'},
    'al.': {'cefr': 'C1', 'lang': 'la', 'note': 'alii'}, # "and others"
    'e.g.': {'cefr': 'B2', 'lang': 'la', 'note': 'exempli gratia'},  # meaning "for example"
    'etc.': {'cefr': 'B1', 'lang': 'la', 'note': 'et cetera'},  # meaning "and so on"
    'i.a.': {'cefr': 'C1', 'lang': 'la', 'note': 'inter alia'},  #meaning "among other things"
    'i.e.': {'cefr': 'B2', 'lang': 'ls', 'note': 'id est'},  # meaning "that is"
    'i.g.': {'cefr': 'C2', 'lang': 'ls', 'note': 'igitur'},  # meaning "therefore"
    'i.i.d.': {'cefr': 'C2', 'lang': 'en', 'note': 'independent and identically distributed'}, # Statistics term
    'a.m.': {'cefr': 'A2', 'lang': 'la', 'note': 'Ante Meridiem (time)'},
    'p.m.': {'cefr': 'A2', 'lang': 'la', 'note': 'Post Meridiem (time)'},
    'v.s.': {'cefr': 'B2', 'lang': 'en', 'note': 'Versus '},
    'vs.': {'cefr': 'B2', 'lang': 'en', 'note': 'Versus '},
    'n.d.': {'cefr': 'B2' , 'lang': 'en', 'note': 'No date'},
    'd.o.f.': {'cefr': 'C1', 'lang': 'en', 'note': 'Degrees of freedom (statistics)'},
    'sq.': {'cefr': 'B1', 'lang': 'en', 'note': 'Square'},


    't.ex./t.ex': {'cefr': 'A2', 'lang': 'sv', 'note': 'Till exempel'},
    't.ex./t.ex': {'cefr': 'A2', 'lang': 'sv', 'note': 'Till exempel'},
    's.k.': {'cefr': 'B1', 'lang': 'sv', 'note': 'Så kallad'},   #  "so-called"
    'p.g.a.': {'cefr': 'A2', 'lang': 'sv', 'note': 'På grund av'},  #  "due to" or "because of"
    'o.k.s.': {'cefr': 'A2', 'lang': 'sv', 'note': 'Och liknande'},  #  "and the like"
    'o.s.v.': {'cefr': 'A2', 'lang': 'sv', 'note': 'Och så vidare'},  # "and so on"
    'm.a.o.': {'cefr': 'B2', 'lang': 'sv', 'note': 'Med andra ord'},  # "in other words"
    'm.fl.': {'cefr': 'B2', 'lang': 'sv', 'note': 'Med flera'},  #  "with several" or "among others"
    'm.m.': {'cefr': 'A2', 'lang': 'sv', 'note': 'Med mera'},  # "and more"
    'V.S.B.': {'cefr': 'C2', 'lang': 'sv', 'note': 'Vilket skulle bevisas'},  # "which was to be proven"
    'v.s.b.': {'cefr': 'C2', 'lang': 'sv', 'note': 'Vilket skulle bevisas'},  # "which was to be proven"
    'v.s.v.': {'cefr': 'C2', 'lang': 'sv', 'note': 'Vilket skulle visas'},  #  "which was to be shown"
    'ö.h.t.': {'cefr': 'B1', 'lang': 'sv', 'note': 'Överhuvudtaget'},  # "at all" or "in general"
    'm.h.a.': {'cefr': 'B2', 'lang': 'sv', 'note': 'Med hjälp av'},  # "with the help of"
    'eng.': {'cefr': 'B1', 'lang': 'sv', 'note': 'engelska '}, # Short for English
    'm.a.p.': {'cefr': 'C1', 'lang': 'sv', 'note': 'Med avseende på'}, # "with respect to"
    'P.S.S.': {'cefr': 'B2', 'lang': 'sv', 'note': 'På samma sätt'},  # "in the same way"
    'p.s.s.': {'cefr': 'B2', 'lang': 'sv', 'note': 'På samma sätt'},  # "in the same way"
    'D.v.s.': {'cefr': 'A2', 'lang': 'sv', 'note': 'Det vill säga'},  # "that is" or "in other words"
    'd.v.s.': {'cefr': 'A2', 'lang': 'sv', 'note': 'Det vill säga'},  # "that is" or "in other words"
    'i.a.f.': {'cefr': 'A2', 'lang': 'sv', 'note': 'I alla fall'},  # "in any case" or "at least"
    'i.o.m.': {'cefr': 'B2', 'lang': 'sv', 'note': 'I och med'},  # "with" or "as a result of"
    't.o.m.': {'cefr': 'A2', 'lang': 'sv', 'note': 'Till och med'},  # "even" or "up to and including"
    'u.å.': {'cefr': 'B2', 'lang': 'sv', 'note': 'Under årens lopp'},  # "Over the years"
    'p.u.': {'cefr': 'B2', 'lang': 'sv', 'note': 'Per undantag'},  # "By exception" or "As an exception"



}

def simplify_abbreviations(html_text, abbreviation_levels):
    global Verbose_Flag
    """
    Simplifies HTML spans for multiple abbreviations with specified CEFR levels and languages.

    Args:
        html_text (str): The HTML string to modify.
        abbreviation_levels (dict): A dictionary mapping abbreviations to their CEFR levels and languages.

    Returns:
        The modified HTML string with simplified and tagged spans.
    """
    for abbreviation, info in abbreviation_levels.items():
        cefr_level = info["cefr"]
        lang = info["lang"]
        # Use a more robust pattern that handles any number of periods
        if abbreviation.count('.') < 1:
            continue
        pattern=""
        parts=abbreviation.split('.')
        for i in range(0, len(parts)-1):
            pattern = pattern+fr"""<span class="CEFR\w+">{parts[i]}</span>\."""
        if Verbose_Flag:
            print(f"pattern: {pattern}")
        # Replacement string with escaped abbreviation
        replacement = (
            fr'<span lang="{lang}" class="CEFR{cefr_level}">{abbreviation}</span>'
        )
        # Replace the pattern in the HTML text
        html_text = re.sub(pattern, replacement, html_text, count=0)
    #
    return html_text

def clean_tagged_html(tagged_html):
    tagged_html=simplify_cefr_span_of_float(tagged_html)
    tagged_html=simplify_abbreviations(tagged_html, abbreviation_levels)
    return tagged_html

def transform_body(html_content):
    global Verbose_Flag
    if Verbose_Flag:
        print(f"{html_content=}")

    changed_flag=True

    soup = BeautifulSoup(html_content, 'html.parser')
    print(f"{soup=}")


    # Remove existing CEFR markup
    soup=remove_existing_CEFR_markup(soup)

    modified_HTML=tokenize_and_CEFR_tag_html_sentences(str(soup))

    new_html_content = style_info+modified_HTML
    if Verbose_Flag:
        print(f"transformed {new_html_content=}")

    return new_html_content, changed_flag

def find_sentences_in_tag(tag):
    global Verbose_Flag
    if tag.name and Verbose_Flag:
        print(f"{tag.name=}")
    if tag.name and tag.name in ['script', 'style']:
        return
    if tag.string:
        if Verbose_Flag:
            print(f"{tag.string=}")
        sentences = nltk.sent_tokenize(tag.string)
        for sentence in sentences:
            yield sentence, tag
    else:
        for child in tag.children:
            yield from find_sentences_in_tag(child)

def choose_lowest_cefr_level(wl):
    global Verbose_Flag
    level_order=['A1', 'A2', 'B1', 'B2', 'C1', 'C2', 'xx']
    for l in level_order:
        if l in wl:
            return l
    # otherwise
    if Verbose_Flag:
        print(f'Error in choose_lowest_cefr_level({wl})')
    return False
def cefr_level_index(wl):
    level_order=['A1', 'A2', 'B1', 'B2', 'C1', 'C2', 'xx']
    for l in level_order:
        if l in wl:
            return l
    # otherwise
    if Verbose_Flag:
        print(f'error in cefr_level_index({w1})')

def choose_lowest_cefr_level_from_two(w1, w2):
    global Verbose_Flag
    level_order=['A1', 'A2', 'B1', 'B2', 'C1', 'C2', 'xx']
    if cefr_level_index(w1) < cefr_level_index(w2):
        return w1
    else:
        return w2

    # otherwise
    if Verbose_Flag:
        print(f'Error in choose_lowest_cefr_level_from_two({w1}, {w2})')
    return False

def cefr_level_to_index(li):
    level_order=['A1', 'A2', 'B1', 'B2', 'C1', 'C2', 'xx']
    for indx, l in enumerate(level_order):
        if li == l:
            return indx
    return False

def compare_cefr_levels(l1, l2):
    global Verbose_Flag
    level_order=['A1', 'A2', 'B1', 'B2', 'C1', 'C2', 'xx']
    l1i=cefr_level_to_index(l1)
    l2i=cefr_level_to_index(l2)
    if isinstance(l1i, int) and isinstance(l2i, int):
        return l2i - l1i
    # otherwise
    if Verbose_Flag:
        print(f'Error in compare_cefr_level({l1}, {l2})')
    return False

# each entry in the lex is of the form {'word': word, 'pos': pos, 'cefr_level': key_max}
def compute_lowest_CEFR_level(lex, lex_name):
    global Verbose_Flag

    level_words=dict()
    for w in lex:
        word=w['word']
        new_level=w['cefr_level']
            
        current_level=level_words.get(word, False)
        if current_level:
            lowest=choose_lowest_cefr_level_from_two(current_level, new_level)
        else:
            lowest=new_level
        level_words[word]=lowest

    if Verbose_Flag:
        print(f'loest levels for {lex_name}={level_words=}')

    return level_words

def is_academic_term(s):
    if len(s) == 6 and s[1] == 'T' and (s[0] == 'V' or s[0] == 'H') and s[2:].isdigit():
        return True
    else:
        return False

def is_float(string):
    try:
        float(string)
        return True
    except ValueError:
        return False
    
def is_number(string):
    # deal with the fact that LaTeX can set a minus sign
    if len(string) > 1 and string[0] == '\u2212':
        string = '-' + string[1:]
    if len(string) > 1 and string[0] == '~':
        string = '-' + string[1:]
    #
    if len(string) > 0:
        if not (string[0] == '-' or string[0] == '+'):
            if not string[0].isdigit():
                return False
    rr = re.findall("[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?", string)
    if rr and len(rr) == 1:
        if is_float(rr[0]):
            return True
    # otherwise
    return False

def is_integer_range_or_ISSN(string):
    if string.count('-') == 1:
        string=string.replace('-', "")
        return string.isdigit()
    elif string.count('–') == 1:
        string=string.replace('–', "")
        return string.isdigit()
    # otherwise
    return False
    

level_order=['A1', 'A2', 'B1', 'B2', 'C1', 'C2', 'xx', 'NA']

def check_cefr_levels_for_POS(cefl_levels, pos, context):
    global Verbose_Flag
    if Verbose_Flag:
        print(f"check_cefr_levels_for_POS({cefl_levels}, {pos}, {context}")

    # check to see if there is a CEFR level for the given POS
    if isinstance(cefr_levels, str):
        return True

    #GQMz
    # if not, then return False
    return False

def get_cefr_level(language, word, pos, context):
    celf_levels=False
    src=None
    # handle punctuation
    if word in ['.', ',', '?', '!', "’"]:
        return 'A1', 'punctuation'
    if word in [';', ':', '-', '(', ')', '[', ']', '{', '}']:
        return 'B1', 'punctuation'
    if word in ['-',]: # add ellipses
        return 'C1', 'punctuation'

    # Note if the word is not found with a relevant POS in a given source, we check the next source
    if language == 'en':
        src='top_100_English_words'
        celf_levels=common_english_and_swedish.top_100_English_words.get(word, False)
        if celf_levels:
            cfl, src=get_specific_cefr_level(language, word, pos, context, src, celf_levels)
            if cfl:
                return cfl, src

        celf_levels=common_english_and_swedish.top_100_English_words.get(word.lower(), False)
        if celf_levels:
            cfl, src=get_specific_cefr_level(language, word, pos, context, src, celf_levels)
            if cfl:
                return cfl, src

        # note that the entries in thousand_most_common_words_in_English are all in lower case
        src='thousand_most_common_words_in_English'
        celf_levels=common_english_and_swedish.thousand_most_common_words_in_English.get(word.lower(), False)
        if celf_levels:
            cfl, src=get_specific_cefr_level(language, word, pos, context, src, celf_levels)
            if cfl:
                return cfl, src

        src='AVL'
        celf_levels=AVL_words_with_CEFR.avl_words.get(word, False)
        if celf_levels:
            cfl, src=get_specific_cefr_level(language, word, pos, context, src, celf_levels)
            if cfl:
                return cfl, src

        celf_levels=AVL_words_with_CEFR.avl_words.get(word.lower(), False)
        if celf_levels:
            cfl, src=get_specific_cefr_level(language, word, pos, context, src, celf_levels)
            if cfl:
                return cfl, src

        src='common_English_words'
        celf_levels=common_english_and_swedish.common_English_words.get(word, False)
        if celf_levels:
            cfl, src=get_specific_cefr_level(language, word, pos, context, src, celf_levels)
            if cfl:
                return cfl, src

        #
        celf_levels=common_english_and_swedish.common_English_words.get(word.lower(), False)
        if celf_levels:
            cfl, src=get_specific_cefr_level(language, word, pos, context, src, celf_levels)
            if cfl:
                return cfl, src

        src='KTH_ordbok_English_with_CEFR'
        celf_levels=common_english_and_swedish.KTH_ordbok_English_with_CEFR.get(word, False)
        if celf_levels:
            cfl, src=get_specific_cefr_level(language, word, pos, context, src, celf_levels)
            if cfl:
                return cfl, src

        src='KTH_ordbok_English_with_CEFR'
        celf_levels=common_english_and_swedish.KTH_ordbok_English_with_CEFR.get(word.lower(), False)
        if celf_levels:
            cfl, src=get_specific_cefr_level(language, word, pos, context, src, celf_levels)
            if cfl:
                return cfl, src



    if language == 'sv':
        src='common_swedish_words'
        celf_levels=common_english_and_swedish.common_swedish_words.get(word, False)
        if celf_levels:
            cfl, src=get_specific_cefr_level(language, word, pos, context, src, celf_levels)
            if cfl:
                return cfl, src

        #
        src='common_swedish_words'
        celf_levels=common_english_and_swedish.common_swedish_words.get(word.lower(), False)
        if celf_levels:
            cfl, src=get_specific_cefr_level(language, word, pos, context, src, celf_levels)
            if cfl:
                return cfl, src

        #
        src='common_swedish_technical_words'
        celf_levels=common_english_and_swedish.common_swedish_technical_words.get(word, False)
        if celf_levels:
            cfl, src=get_specific_cefr_level(language, word, pos, context, src, celf_levels)
            if cfl:
                return cfl, src

        #
        src='common_swedish_technical_words'
        celf_levels=common_english_and_swedish.common_swedish_technical_words.get(word.lower(), False)
        if celf_levels:
            cfl, src=get_specific_cefr_level(language, word, pos, context, src, celf_levels)
            if cfl:
                return cfl, src

        #
        src='KTH_ordbok_Swedish_with_CEFR'
        celf_levels=common_english_and_swedish.KTH_ordbok_Swedish_with_CEFR.get(word, False)
        if celf_levels:
            cfl, src=get_specific_cefr_level(language, word, pos, context, src, celf_levels)
            if cfl:
                return cfl, src
        #
        src='KTH_ordbok_Swedish_with_CEFR'
        celf_levels=common_english_and_swedish.KTH_ordbok_Swedish_with_CEFR.get(word.lower(), False)
        if celf_levels:
            cfl, src=get_specific_cefr_level(language, word, pos, context, src, celf_levels)
            if cfl:
                return cfl, src

    # all languages
    if word in common_english_and_swedish.common_units:
        return 'A1', 'common_units'
    #
    if word in common_english_and_swedish.chemical_names_and_formulas:
        return 'B2', 'chemical_names_and_formulas'
    #
    if word in common_english_and_swedish.common_urls:
        return 'B2', 'common_urls'
    #
    if word in common_english_and_swedish.java_paths:
        return 'B2', 'java_paths'
    #
    if word in common_english_and_swedish.misc_words_to_ignore:
        return 'XX', 'misc_words_to_ignore'
    #
    if word in common_english_and_swedish.place_names:
        return 'A1', 'place_names'
    #
    if word in common_english_and_swedish.company_and_product_names:
        return 'B2', 'company_and_product_names'
    #
    if word in common_english_and_swedish.common_programming_languages:
        return 'B2', 'common_programming_languages'
    #
    if word in common_english_and_swedish.names_of_persons:
        return 'B2', 'names_of_persons'

    #
    # look in all the sources for the lowest level without an specific POS
    cfl, src=get_cefr_level_without_POS(language, word, context)
    if cfl:
        return cfl, src

    return 'XX', 'unknown'


def get_lowest_cefr_level(language, word, context, src, cefr_levels):
    global Verbose_Flag
    if Verbose_Flag:
        print(f"get_lowest_cefr_level({language}, {word}, {context}, {src}, {cefr_levels})")

    level_order=['A1', 'A2', 'B1', 'B2', 'C1', 'C2', 'xx']

    if language == 'en' and word == "'s":
        return 'B1', 'genative marker'

    if word in well_known_acronyms:  # Perhaps  used the 'cefr' property of the entry
        cefr_levels = get_acronym_cefr_levels(word)
        print(f"'{word}' {cefr_levels=}")
        if len(cefr_levels) == 0:
            return 'C2', 'well_known_acronyms'
        elif len(cefr_levels) == 1:
            return cefr_levels[0], 'well_known_acronyms'
        else:
            for l in level_order:
                if l in cefr_levels:
                    return l, 'well_known_acronyms'

    if not cefr_levels:
        if is_number(word):
            return 'A1', 'number'
        if is_integer_range_or_ISSN(word):
            return 'A1', 'integer_range_or_ISSN'
        if is_academic_term(word):
            return 'A1', 'academic_term'
        return False, src

    if isinstance(cefr_levels, str):
        return cefr_levels, src

    for wl in level_order:
        level=cefr_levels.get(wl, False)
        if level:
            return wl, src

    print(f"no result for get_lowest_cefr_level({language}, {word}, {context}, {src}, {cefr_levels})")
    return False, src


def get_cefr_level_without_POS(language, word, context):
    global Verbose_Flag
    if Verbose_Flag:
        print(f"get_cefr_level_without_POS({language}, {word}, {context})")
    celf_levels=False
    src=None
    # handle punctuation
    if word in ['.', ',', '?', '!', "’"]:
        return 'A1', 'punctuation'
    if word in [';', ':', '-', '(', ')', '[', ']', '{', '}']:
        return 'B1', 'punctuation'
    if word in ['-',]: # add ellipses
        return 'C1', 'punctuation'

    # Note if the word is not found with a relevant POS in a given source, we check the next source
    if language == 'en':
        src='top_100_English_words'
        celf_levels=common_english_and_swedish.top_100_English_words.get(word, False)
        if celf_levels:
            cfl, src=get_lowest_cefr_level(language, word, context, src, celf_levels)
            if cfl:
                return cfl, src

        celf_levels=common_english_and_swedish.top_100_English_words.get(word.lower(), False)
        if celf_levels:
            cfl, src=get_lowest_cefr_level(language, word, context, src, celf_levels)
            if cfl:
                return cfl, src

        src='thousand_most_common_words_in_English'
        celf_levels=common_english_and_swedish.thousand_most_common_words_in_English.get(word.lower(), False)
        if celf_levels:
            cfl, src=get_lowest_cefr_level(language, word, context, src, celf_levels)
            if cfl:
                return cfl, src

        src='AVL'
        celf_levels=AVL_words_with_CEFR.avl_words.get(word, False)
        if celf_levels:
            cfl, src=get_lowest_cefr_level(language, word, context, src, celf_levels)
            if cfl:
                return cfl, src

        celf_levels=AVL_words_with_CEFR.avl_words.get(word.lower(), False)
        if celf_levels:
            cfl, src=get_lowest_cefr_level(language, word, context, src, celf_levels)
            if cfl:
                return cfl, src

        src='common_English_words'
        celf_levels=common_english_and_swedish.common_English_words.get(word, False)
        if celf_levels:
            cfl, src=get_lowest_cefr_level(language, word, context, src, celf_levels)
            if cfl:
                return cfl, src

        #
        celf_levels=common_english_and_swedish.common_English_words.get(word.lower(), False)
        if celf_levels:
            cfl, src=get_lowest_cefr_level(language, word, context, src, celf_levels)
            if cfl:
                return cfl, src

        src='KTH_ordbok_English_with_CEFR'
        celf_levels=common_english_and_swedish.KTH_ordbok_English_with_CEFR.get(word.lower(), False)
        if celf_levels:
            cfl, src=get_lowest_cefr_level(language, word, context, src, celf_levels)
            if cfl:
                return cfl, src



    if language == 'sv':
        src='common_swedish_words'
        celf_levels=common_english_and_swedish.common_swedish_words.get(word, False)
        if celf_levels:
            cfl, src=get_lowest_cefr_level(language, word, context, src, celf_levels)
            if cfl:
                return cfl, src

        #
        src='common_swedish_technical_words'
        celf_levels=common_english_and_swedish.common_swedish_technical_words.get(word, False)
        if celf_levels:
            cfl, src=get_lowest_cefr_level(language, word, context, src, celf_levels)
            if cfl:
                return cfl, src

        #
        src='KTH_ordbok_Swedish_with_CEFR'
        celf_levels=common_english_and_swedish.KTH_ordbok_Swedish_with_CEFR.get(word, False)
        if celf_levels:
            cfl, src=get_lowest_cefr_level(language, word, context, src, celf_levels)
            if cfl:
                return cfl, src

    # all languages
    if word in common_english_and_swedish.common_units:
        return 'A1', 'common_units'
    #
    if word in common_english_and_swedish.chemical_names_and_formulas:
        return 'B2', 'chemical_names_and_formulas'
    #
    if word in common_english_and_swedish.common_urls:
        return 'B2', 'common_urls'
    #
    if word in common_english_and_swedish.java_paths:
        return 'B2', 'java_paths'
    #
    if word in common_english_and_swedish.misc_words_to_ignore:
        return 'XX', 'misc_words_to_ignore'
    #
    if word in common_english_and_swedish.place_names:
        return 'A1', 'place_names'
    #
    if word in common_english_and_swedish.company_and_product_names:
        return 'B2', 'company_and_product_names'
    #
    if word in common_english_and_swedish.common_programming_languages:
        return 'B2', 'common_programming_languages'
    #
    if word in common_english_and_swedish.names_of_persons:
        return 'B2', 'names_of_persons'

    if word in well_known_acronyms:
        return get_lowest_cefr_level('en', word, None, 'well_known_acronyms', get_acronym_cefr_levels(word))
    #
    return 'XX', 'unknown'

def get_acronym_cefr_levels(w):
    cefr_levels=[]
    for e in common_acronyms.well_known_acronyms_list:
        if not isinstance(e, list):
            print(f"{e=}")

        if len(e) >= 1 and  w == e[0]:
            if len(e) >= 2:
                d=e[1]
            if len(e) >= 3:
                if isinstance(e[2], dict):
                    cefr_level=e[2].get('cefr', None)
                    print(f"{w} {cefr_level=}")
                    if cefr_level:
                        cefr_levels.append(cefr_level)
    return cefr_levels


def get_specific_cefr_level(language, word, pos, context, src, cerf_levels_from_src):
    global Verbose_Flag
    if Verbose_Flag:
        print(f"get_specific_cefr_level('{language}', '{word}', '{pos}', {context}, {src})")

    level_order=['A1', 'A2', 'B1', 'B2', 'C1', 'C2', 'xx']

    # check if there is a need to correct the POS
    pos = corrected_pos_for_word(word, pos)

    celf_levels=False

    if language == 'en' and word == "'s" and pos == 'POS':
        return 'B1', 'genative marker'

    if pos == 'CD': # numeral, cardinal
        return 'A1', 'fixed'

    if pos == 'LS': # list item marker
        return 'A1', 'fixed'

    if pos == 'SYM': # Symbol
        return 'A1', 'fixed'

    if pos == 'FW': # Foreign word
        return 'XX', 'foreign word'

    if word in well_known_acronyms:  # Perhaps  used the 'cefr' property of the entry
        cefr_levels = get_acronym_cefr_levels(word)
        if Verbose_Flag:
            print(f"'{word}' {cefr_levels=}")
        if len(cefr_levels) == 0:
            return 'C2', 'well_known_acronyms'
        elif len(cefr_levels) == 1:
            return cefr_levels[0], 'well_known_acronyms'
        else:
            for l in level_order:
                if l in cefr_levels:
                    return l, 'well_known_acronyms'

    cefr_levels=cerf_levels_from_src
    if Verbose_Flag:
        print(f"{cefr_levels=}")
    if not cefr_levels:
        if is_number(word):
            return 'A1', 'number'
        if is_integer_range_or_ISSN(word):
            return 'A1', 'integer_range_or_ISSN'
        if is_academic_term(word):
            return 'A1', 'academic_term'
        return False, src

    if isinstance(cefr_levels, str):
        return cefr_levels, src

    for wl in level_order:
        pos_in_level=cefr_levels.get(wl, False)
        if not pos_in_level:
            continue
        if Verbose_Flag:
            print(f"'{word}' {pos=} {wl=} {type(pos_in_level)=} {pos_in_level}")
        if pos_in_level:
            pos_in_level=pos_in_level.lower().split(',')
            pos_in_level=[p.strip() for p in pos_in_level]
            # note that pos_in_levels now a list 
            if Verbose_Flag:
                print(f"second print: '{word}' {pos=} {wl=} {pos_in_level}")

            # handle wild card of POS
            if 'et al.' in pos_in_level:
                return wl, src

            if pos in ['RB', 'RBR', 'RBS']:
                if 'adverb' in pos_in_level:
                    return wl, src

            if pos in ['WRB']:
                if 'interrogative adverb' in pos_in_level:
                    return wl, src
                if 'adverb' in pos_in_level:
                    return wl, src

            if pos in ['VBD']:
                if 'verb past tense' in pos_in_level:
                    return wl, src

            if pos in ['VBN']:
                if 'past participle' in pos_in_level:
                    return wl, src
                if 'verb past participle' in pos_in_level:
                    return wl, src
                if 'verb (past participle)' in pos_in_level:
                    return wl, src
                if 'verb' in pos_in_level:
                    return wl, src

            if pos in ['VBG']:
                if 'verb gerund or present participle' in pos_in_level:
                    return wl, src
                if 'verb (present participle)' in pos_in_level:
                    return wl, src
                if 'verb' in pos_in_level:
                    return wl, src
                if 'verb' in pos_in_level:
                    return wl, src

            if pos in ['VBZ']:
                if 'verb 3rd person present' in pos_in_level:
                    return wl, src

            if pos in ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']:
                if 'verb' in pos_in_level:
                    return wl, src

            if pos in ['PRP§']:
                if 'possessive pronoun' in pos_in_level:
                    return wl, src
                if 'pronoun' in pos_in_level:
                    return wl, src

            if pos in ['PRP', 'WP', 'WP§']:
                if 'pronoun' in pos_in_level:
                    return wl, src

            if pos in ['NNP', 'NNPS']:
                if 'proper noun' in pos_in_level:
                    return wl, src
                if 'noun' in pos_in_level:
                    return wl, src

            if pos in ['NN']:
                if 'noun' in pos_in_level:
                    return wl, src
                if 'acronym' in pos_in_level:
                    return wl, src
                if 'verb' in pos_in_level: # a fall back
                    return wl, src


            if pos in ['NNS']:
                if 'noun (plural)' in pos_in_level:
                    return wl, src
                if 'noun' in pos_in_level:
                    return wl, src


            if pos in ['NN', 'NNP', 'NNS', 'NNPS']:
                if 'noun' in pos_in_level:
                    return wl, src
                if 'proper noun' in pos_in_level:
                    return wl, src

            if pos in ['JJ', 'JJR', 'JJS']:
                if 'adjective' in pos_in_level:
                    return wl, src

            if pos in ['TO']:
                if 'preposition' in pos_in_level:
                    return wl, src
                if 'infinitive' in pos_in_level:
                    return wl, src

            if pos in ['IN']:
                if 'preposition' in pos_in_level:
                    return wl, src
                if 'conjunction' in pos_in_level:
                    return wl, src

            if pos in ['CC']:
                if 'conjunction' in pos_in_level:
                    return wl, src
                if 'coordinator' in pos_in_level:
                    return wl, src

            if pos in ['DT', 'PDT', 'WDT']:
                if 'determiner' in pos_in_level:
                    return wl, src
                if 'article' in pos_in_level:
                    return wl, src


            if pos in ['UH']:
                if 'interjection' in pos_in_level:
                    return wl, src

            if pos in ['RP']:
                if 'particle' in pos_in_level:
                    return wl, src

            if pos in ['EX']:
                if 'existential' in pos_in_level:
                    return wl, src

            if pos in ['MD']:
                if 'modal verb' in pos_in_level:
                    return wl, src
                if 'verb (modal)' in pos_in_level:
                    return wl, src
                if 'verb' in pos_in_level:
                    return wl, src

            if pos in ['POS']:
                if 'genitive' in pos_in_level:
                    return wl, src
    print(f"no result for get_specific_cefr_level({language}, {word}, {pos}, {context}, {src})")
    return False, src

corrected_pos_info=[
    ['fun', 'VBN', 'JJR'],
    ['Join', 'NNP', 'VB'],
]

def corrected_pos_for_word(word, pos):
    for e in corrected_pos_info:
        if e[0] == word and e[1] == pos:
            return e[2]
    return pos

encountered_POS_list=set()
# Find sentences in the HTML
def find_sentences_in_tag(tag, parent=None):
    if tag.name and tag.name in ['script', 'style']:
        return []
        
    # If it's a string, tokenize it and yield sentence and parent
    if isinstance(tag, NavigableString):
        text = tag.string.strip()
        if text:
            sentences = nltk.sent_tokenize(text)
            for sentence in sentences:
                yield sentence, tag  

        # If it's a tag, process children recursively
    elif tag.name:
        for child in tag.children:
            yield from find_sentences_in_tag(child, tag)  

def tokenize_paragraph(soup, e):
    words = nltk.word_tokenize(e.text, language='english')
    print("GQM")
    pos_tags = nltk.pos_tag(words)
    print(f"at start of paragraph {words=} {pos_tags=}")

    # chunk the pos tagged tokens
    # chunked_sentence = grammar_parser.parse(pos_tags)
    # # print the chunked sentence structure (tree)
    # print(f"{chunked_sentence=}")
    # if False and Verbose_Flag:
    #     chunked_sentence.draw()

    # create new spans for words and pos tags
    new_spans = []
    last_word='' 
    for word, pos in pos_tags:
        if Verbose_Flag:
            print(F"in loop: {word=} {pos=}")
        encountered_POS_list.add(pos) # keep track of the pos encounterd
        # correct the pos tag, as the  dollar character cannot be in a class name
        if pos == "PRP$":
            pos="PRP§"
        if pos == "WP$":
            pos="WP§"

        cefr_level, source = get_cefr_level('en', word, pos, None)
        print(f"magic: {cefr_level} '{word}'")
        if Verbose_Flag:
            print(f"word: '{word}', pos: '{pos}', cefr level: {cefr_level}, source: {source}")
        span = soup.new_tag('span', attrs={'class': f'CEFR{cefr_level}'})
        span.string = word
        # add space between word spans, except before punctuation
        if Verbose_Flag:
                print(f"{word=} - {new_spans=}")
        # if len(new_spans) == 0:
        #     new_spans.append(soup.new_string(' '))
        if len(new_spans) > 0 and last_word not in ["’"] and word not in [',', '.', '?', ':', "’"]:
            new_spans.append(soup.new_string(' '))
        last_word=word

        new_spans.append(span)

        if Verbose_Flag:
            print(f"after adding possible spaces {new_spans=}")

    return new_spans

def tokenize_and_pos_tag_html_sentences(soup):
    for paragraph in soup.find_all(recursive=False):
        print(f"new paragraph {paragraph.name=}")
        if paragraph.name == 'p':
            new_spans=tokenize_paragraph(soup, paragraph)
            # replace the original text with the new spans
            #paragraph.replace_with(*new_spans)
            paragraph.clear()
            for ns in new_spans:
                paragraph.append(ns)
        elif paragraph.name == 'ul':
            children = paragraph.findChildren(recursive=False)
            for child in children:
                new_spans=tokenize_paragraph(soup, child)
                # replace the original text with the new spans
                #child.replace_with(*new_spans)
                child.clear()
                for ns in new_spans:
                    child.append(ns)
        else:
            print(f"Not handled {paragraph.name=}")
            continue
    return soup

def is_float(string):
    try:
        float(string)
        return True
    except ValueError:
        return False
    
def is_number(string):
    # deal with the fact that LaTeX can set a minus sign
    if len(string) > 1 and string[0] == '\u2212':
        string = '-' + string[1:]
    #
    if len(string) > 0:
        if not (string[0] == '-' or string[0] == '+'):
            if not string[0].isdigit():
                return False
    rr = re.findall("[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?", string)
    if rr and len(rr) == 1:
        if is_float(rr[0]):
            return True
    # otherwise
    return False

hex_digits='0123456789abcdefABCDEF'

def is_hex_number(string):
    if string.startswith('0x'):
        for c in string[2:]:
            if c not in hex_digits:
                return False
        return True
    else:
        return False


def main():
    global Verbose_Flag
    global testing_mode_flag # if set to true do _not_ write the modified contents
    global well_known_acronyms


    parser = optparse.OptionParser()

    parser.add_option('-v', '--verbose',
                      dest="verbose",
                      default=False,
                      action="store_true",
                      help="print lots of output to stdout"
    )

    parser.add_option('-t', '--testing',
                      dest="testing",
                      default=False,
                      action="store_true",
                      help="set test mode"
    )

    parser.add_option("--config", dest="config_filename",
                      help="read configuration from file", metavar="file")
    
    options, remainder = parser.parse_args()

    Verbose_Flag=options.verbose
    if Verbose_Flag:
        print("argv      : {}".format(sys.argv[1:]))
        print("verbose   : {}".format(options.verbose))
        print("remaining : {}".format(remainder))
        print("configuration file : {}".format(options.config_filename))

    testing_mode_flag=options.testing

    initialize(options)

    if (len(remainder) < 1):
        print("insuffient arguments - must provide course_id")
        return
    
    course_id=remainder[0]

    setup_acronyms()
    x1=get_acronym_cefr_levels('ECTS')
    print(f"get_acronym_cefr_levels: {x1}")
    x=get_lowest_cefr_level('en', 'ECTS', None, 'bogus', get_acronym_cefr_levels('ECTS'))
    print(f"is ECTS in ancronyms? {x}")
    
    if Verbose_Flag:
        print(f'{(len(well_known_acronyms)):>{Numeric_field_width}} unique acronyms in ({len(common_acronyms.well_known_acronyms_list)}) well_known_acronyms')

    process_course(course_id)


if __name__ == "__main__": main()
