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
sys.setrecursionlimit(10**6)    # increase recusion limit

import json
import re

from datetime import datetime, date, timedelta
import isodate                  # for parsing ISO 8601 dates and times
import pytz                     # for time zones

# Use Python Pandas to create XLSX files
import pandas as pd

# use BeautifulSoup to process the HTML
from bs4 import BeautifulSoup, NavigableString, Tag
import bs4

import nltk
from nltk import RegexpParser
from nltk.tokenize import word_tokenize
# for the following two you will (once) have to do: nltk.download('bcp47')
from nltk.langnames import langname
from nltk.langnames import langcode

#
import spacy_udpipe


import html


sys.path.append('/z3/maguire/Canvas/Canvas-tools')  # Include the path to module_folder
sys.path.append('/home/maguire/Canvas/Canvas-tools')

#  as common_English_words, common_swedish_words, common_swedish_technical_words
import common_english_and_swedish
import common_acronyms
import miss_spelled_to_correct_spelling
import diva_merged_words
import diva_corrected_abstracts
import AVL_words_with_CEFR


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

def create_footer():
    global current_page_url
    return f"""<hr>
<footer>
<p class"CEFRColorCodes">Color codes for CEFR levels: <span class="CEFRA1">A1</span>, <span class="CEFRA2">A2</span> , <span class="CEFRB1">B1</span>,
  <span class="CEFRB2">B2</span>, <span class="CEFRC1">C1</span>, <span class="CEFRC2">C2</span>,
  <span class="CEFRXX">XX</span>, and <span class="CEFRNA">NA</span>.</p>
<p>Automatically generated from the HTML for the page <a href="{current_page_url}">{current_page_url}</a>.
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
    global current_page_url
    
    print(f"processing pages for course {course_id}")

    page_list=list_pages(course_id)

    for p in page_list:
        # skip unpublished pages
        if not p['published']:
            continue

        print(f"processing page: '{p['title']}'")
        if p['title'] ==  'Ethics / Code of Honor and Regulations':
            continue
        if p['title'] ==  'Overview':
            continue
        if p['title'] == 'Course home page':
            continue
        if p['title'] == 'Welcome to II2210':
            continue
        if p['title'] == 'Learning outcomes':
            continue
        if p['title'] == 'Concept of Multiplexing and Demultiplexing':
            continue
        if p['title'] != 'Reference Books and Other Materials':
            continue

        current_page_url=p['url']
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
    words = nltk.regexp_tokenize(text, r"(\w+\-\s?\w+)|(\w+)") # was "\w+|[^\w\s-]"
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

string_field_width=20
def my_partition(s, pat):
    print(f"my_partition('{s:{string_field_width}.{string_field_width}}', '{pat}')")
    if len(s) == 0:
        return '', '', ''
    # look for the Start_of_text_Marker and stop at the End_of_text_Marker
    sm=s.find(Start_of_text_Marker)
    em=s.find(End_of_text_Marker)
    if sm < 0 or em < 0:        #  there is no text here to process
        return s, '', ''
    before_marker=s[0:sm]
    after_marker=s[em:]
    between_markers=s[sm+len(Start_of_text_Marker):em]
    print(f"{len(between_markers)=}")
    if len(between_markers) < len(pat):
        return before_marker, '', after_marker[len(End_of_text_Marker):]
    #
    prefix, w, suffix = between_markers.partition(pat)
    # if not w:
    #     return s, '', ''
    return before_marker+prefix, w, Start_of_text_Marker+suffix+after_marker



def old_process_my_string(s, tagged_words, lang, i):
    global Verbose_Flag
    if Verbose_Flag:
        print(f"process_my_string({s:<20.20}, tagged_words, {lang}, {i=})")
    # if the start marker reaches the end marker, then remove them
    if s.startswith(Start_of_text_Marker+End_of_text_Marker):
        s=s[len(Start_of_text_Marker+End_of_text_Marker):]

    if i >= len(tagged_words):
        return s
    word, tag = tagged_words[i]

    #prefix, word, suffix = s.partition(word)
    prefix, word, suffix = my_partition(s, word)
    #print(f"{prefix=}, {word=}, {suffix=}")
    if word:
        cefr_level, source = get_cefr_level(lang, word, tag, None)
        if cefr_level == 'XX':
            return prefix+f'{html.escape(word)}'+process_my_string(suffix, tagged_words, lang, i+1)
        else:
            return prefix+f'<span class="CEFR{cefr_level}">{html.escape(word)}</span>'+process_my_string(suffix, tagged_words, lang, i+1)
    else:
        return prefix+process_my_string(suffix, tagged_words, lang, i)
    #return s

def process_my_string(s, tagged_words, lang, i):
    # do NOT HTML entities
    #html_content = html.unescape(html_content)
    global Verbose_Flag
    if Verbose_Flag:
        print(f"process_my_string({s:<20.20}, tagged_words, {lang}, {i=})")

    if i >= len(tagged_words):
        return s

    soup = BeautifulSoup(s, 'html.parser')
    def _wrap_words(element):
        # Only process NavigableString elements that have a parent Tag
        if (isinstance(element, NavigableString) and
            element.parent is not None and
            isinstance(element.parent, Tag) and
            element.parent.name not in ['script', 'style'] and
            not any(cls in element.parent.get('class', []) for cls in ['word', 'CEFRA1', 'CEFRA2',  'CEFRB1', 'CEFRB2',  'CEFRC1', 'CEFRC2', 'CEFRXX', 'CEFRNA'] ) # Skip if already wrapped
            #element.parent.get('class') != ['word'] # Skip if already wrapped
            ):
            txt = element.strip()
            if not txt:
                return
            words_and_separators = re.split(r'(\s+|[.,:;!?])', txt)
            #print(f"{words_and_separators=}")
            parent = element.parent  # parent of the original element
            original_siblings = list(element.previous_siblings)
            new_content = []

            # Wrap words and insert, keeping separators as they are

            tagged_index=i
            pos_to_use = 'X'
            for item in words_and_separators:
                #print(f"{item=}")
                if not item:
                    continue
                if item.strip():
                    if False and item in [',', '.']:
                        wrapped_word = soup.new_tag("span", attrs={"class": "word"})
                        wrapped_word.string = item
                        parent.insert_before(wrapped_word)
                    else:
                        # look for the word in tagged_words, starting with entry tagged_index
                        # when you find the word get the pos_tag and update the index for the next word
                        for j in range(tagged_index, len(tagged_words)):
                            word, pos_tag = tagged_words[j]
                            if item.strip() == word:
                                pos_to_use=pos_tag
                                tagged_index=j+1
                            
                        cefr_level, source = get_cefr_level(lang, item, pos_to_use, None)
                        wrapped_word = soup.new_tag("span", attrs={"class": f"CEFR{cefr_level}"})
                        wrapped_word.string = item
                        new_content.append(wrapped_word)
                        #parent.insert_before(wrapped_word)
                else:
                    #print(f"about to insert_before with {item=}")
                    new_content.append(NavigableString(item))
                    #parent.insert_before(NavigableString(item))
            #
            #element.replace_with(NavigableString('')) # Replace element with empty string to prevent further processing
            element.replace_with(*new_content)
        elif isinstance(element, Tag):
            # Process text in this tag first (before recursing)
            if element.string:
                _wrap_words(element.string)
            for child in list(element.children): 
                if child != element.string:  # Avoid processing the same string twice
                    _wrap_words(child)

    _wrap_words(soup)
    return str(soup)




def old_get_text_by_language(html_content, target_lang):
    """
    Extracts text content in a specific language from an HTML string, 
    handling nested elements with different languages.

    Args:
        html_content (str): The HTML content to process.
        target_lang (str): The target language code (e.g., "en", "fr", "es").

    Returns:
        str: The extracted text content in the target language.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    extracted_text = []
    def traverse_and_extract(element, current_lang=None):
        """Recursively traverses the HTML tree to extract text in the target language."""
        #
        if isinstance(element, bs4.element.NavigableString):
            # Find closest parent with 'lang' attribute
            parent = element.find_parent(lambda tag: tag.has_attr('lang'))
            if parent: # Check if parent exists before getting the 'lang' attribute
                current_lang = parent.get('lang') or current_lang
            if current_lang == target_lang:
                #extracted_text.append(element.strip())
                extracted_text.append(element)
        elif isinstance(element, bs4.element.Tag) and element.name != 'script':  # Exclude script tags
            for child in element.children:
                traverse_and_extract(child, current_lang)
    #
    traverse_and_extract(soup)
    #
    return ' '.join(extracted_text)

def get_text_by_language(html_content, target_lang):
    """
    Extracts text content in a specific language from an HTML string, 
    handling nested elements with different languages.

    Args:
        html_content (str): The HTML content to process.
        target_lang (str): The target language code (e.g., "en", "fr", "es").

    Returns:
        str: The extracted text content in the target language.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    extracted_text = []
    def traverse_and_extract(element, current_lang=None):
        """Recursively traverses the HTML tree to extract text in the target language."""
        #
        # We use type and not isinstance since comments, cdata, etc are subclasses that we don't want
        if type(element) == bs4.NavigableString:
            parent_tags = (t for t in element.parents if type(t) == bs4.Tag)
            hidden = False
            for parent_tag in parent_tags:
                # Ignore any text inside a non-displayed tag
                # We also behave is if scripting is enabled (noscript is ignored)
                # The list of non-displayed tags and attributes from the W3C specs:
                if (parent_tag.name in ('area', 'base', 'basefont', 'datalist', 'head', 'link',
                                        'meta', 'noembed', 'noframes', 'param', 'rp', 'script',
                                        'source', 'style', 'template', 'track', 'title', 'noscript') or
                    parent_tag.has_attr('hidden') or
                    (parent_tag.name == 'input' and parent_tag.get('type') == 'hidden')):
                    hidden = True
                    break
            if hidden:
                return

            # Find closest parent with 'lang' attribute
            parent = element.find_parent(lambda tag: tag.has_attr('lang'))
            if parent: # Check if parent exists before getting the 'lang' attribute
                current_lang = parent.get('lang') or current_lang
            if current_lang == target_lang:
                extracted_text.append(element.strip())
        #elif isinstance(element, bs4.element.Tag) and element.name != 'script':  # Exclude script tags
        elif isinstance(element, bs4.element.Tag) and element.name != 'script':  # Exclude script tags
            for child in element.children:
                traverse_and_extract(child, current_lang)
    #
    traverse_and_extract(soup)
    #
    return ' '.join(extracted_text)

# The following two markers will be used to "decorate" the text strings in the soup,
# in this way simple string matching and replacement can be done on these text strings
# without a risk of being confused with instances of the same strings that might occur
# in a anchor title or other places that are not part of the displayed text.
#
# The markers are designed to have a very low probablability of being in any HTML pages
# Start_of_text_Marker=STX + a private use character + DC1 (XON)  + RobotFace
# End_of_text_Marker=RobotFace + DC3 (XOFF) + a private use area (PUA) character + ETX
# Where we have used the following ASCII character:
# STX Start of Text 0x02
# ETX End of Text   0x03
# DC1 (XON)         0x11
# DC3 (XOFF)        0x13
# the RobotFace is U+1F916
# and the private use area character will bx U+E830 (from the PUA U+E830 to U+E88F)
Start_of_text_Marker = chr(0x0002)+chr(0xE830)+chr(0x11)+chr(0x1F916)
End_of_text_Marker = chr(0x1F916)+chr(0x13)+chr(0xE830)+chr(0x03)


def decorate_by_language(html_content, target_lang):
    """
    Decorates text content in a specific language from an HTML string, 
    handling nested elements with different languages.

    The decorations are a special Start_of_text_Marker and End_of_text_Marker

    Args:
        html_content (str): The HTML content to process.
        target_lang (str): The target language code (e.g., "en", "fr", "es").

    Returns:
        str: The decorated string
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    extracted_text = []
    def traverse_and_decorate(element, current_lang=None):
        """Recursively traverses the HTML tree to extract text in the target language."""
        #
        # We use type and not isinstance since comments, cdata, etc are subclasses that we don't want
        if type(element) == bs4.NavigableString:
            parent_tags = (t for t in element.parents if type(t) == bs4.Tag)
            hidden = False
            for parent_tag in parent_tags:
                # Ignore any text inside a non-displayed tag
                # We also behave is if scripting is enabled (noscript is ignored)
                # The list of non-displayed tags and attributes from the W3C specs:
                if (parent_tag.name in ('area', 'base', 'basefont', 'datalist', 'head', 'link',
                                        'meta', 'noembed', 'noframes', 'param', 'rp', 'script',
                                        'source', 'style', 'template', 'track', 'title', 'noscript') or
                    parent_tag.has_attr('hidden') or
                    (parent_tag.name == 'input' and parent_tag.get('type') == 'hidden')):
                    hidden = True
                    break
            if hidden:
                return

            # Find closest parent with 'lang' attribute
            parent = element.find_parent(lambda tag: tag.has_attr('lang'))
            if parent: # Check if parent exists before getting the 'lang' attribute
                current_lang = parent.get('lang') or current_lang
            if current_lang == target_lang:
                element.replace_with(Start_of_text_Marker + element + End_of_text_Marker)
        #elif isinstance(element, bs4.element.Tag) and element.name != 'script':  # Exclude script tags
        elif isinstance(element, bs4.element.Tag) and element.name != 'script':  # Exclude script tags
            for child in element.children:
                traverse_and_decorate(child, current_lang)
    #
    traverse_and_decorate(soup)
    #
    return str(soup)

def undecorate_by_language(html_content, target_lang):
    """
    Decorates text content in a specific language from an HTML string, 
    handling nested elements with different languages.

    The decorations are a special Start_of_text_Marker and End_of_text_Marker

    Args:
        html_content (str): The HTML content to process.
        target_lang (str): The target language code (e.g., "en", "fr", "es").

    Returns:
        str: The decorated string
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    extracted_text = []
    def traverse_and_undecorate(element, current_lang=None):
        """Recursively traverses the HTML tree to extract text in the target language."""
        #
        # We use type and not isinstance since comments, cdata, etc are subclasses that we don't want
        if type(element) == bs4.NavigableString:
            parent_tags = (t for t in element.parents if type(t) == bs4.Tag)
            hidden = False
            for parent_tag in parent_tags:
                # Ignore any text inside a non-displayed tag
                # We also behave is if scripting is enabled (noscript is ignored)
                # The list of non-displayed tags and attributes from the W3C specs:
                if (parent_tag.name in ('area', 'base', 'basefont', 'datalist', 'head', 'link',
                                        'meta', 'noembed', 'noframes', 'param', 'rp', 'script',
                                        'source', 'style', 'template', 'track', 'title', 'noscript') or
                    parent_tag.has_attr('hidden') or
                    (parent_tag.name == 'input' and parent_tag.get('type') == 'hidden')):
                    hidden = True
                    break
            if hidden:
                return

            # Find closest parent with 'lang' attribute
            parent = element.find_parent(lambda tag: tag.has_attr('lang'))
            if parent: # Check if parent exists before getting the 'lang' attribute
                current_lang = parent.get('lang') or current_lang
            if current_lang == target_lang and element.startswith(Start_of_text_Marker) and element.endswith(End_of_text_Marker):
                element.replace_with(element[len(Start_of_text_Marker): -len(End_of_text_Marker)]) # Slice the string between the markers
        elif isinstance(element, bs4.element.Tag) and element.name != 'script':  # Exclude script tags
            for child in element.children:
                traverse_and_undecorate(child, current_lang)
    #
    traverse_and_undecorate(soup)
    #
    return str(soup)



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

def extract_iso_code(bcp_identifier):
    if bcp_identifier.count('-') == 0:
        return bcp_identifier
    language, _ = bcp_identifier.split('-', 1)
    if 2 <= len(language) <=3:
        # this is a valid ISO-639 code or is grandfathered
        return language
    else:
        # handle non-ISO codes
        raise ValueError(bcp_identifier)
    
def words_and_pos_info(txt, lang):
    global nlp
    wrds=[]
    wrds_pos=[]

    lang=extract_iso_code(lang)

    if not nlp.get(lang, False):
        print(f'*** add spacy_udpipe.download("{lang}) to main()')
        return

    doc = nlp[lang](txt)
    for token in doc:
        print(token.text, token.lemma_, token.pos_, token.dep_)
        wrds.append(token.text)
        wrds_pos.append( [token.text, token.pos_])
    return   wrds, wrds_pos

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
        #words = nltk.regexp_tokenize(text, r"[\w-\s]+|[^\w\s-]")
        #tagged_words = nltk.pos_tag(words, lang=convert_to_ISO_639_code(lang))
        words, tagged_words = words_and_pos_info(text, lang)
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
        #tagged_html=decorate_by_language(tagged_html, lang)
        tagged_html=process_my_string(tagged_html, tagged_words, lang, 0)
        #tagged_html=undecorate_by_language(tagged_html, lang)
        if Verbose_Flag:
            print(f"before cleaning {tagged_html=}")

        if lang in ['en', 'en-US']:
            tagged_html=combine_English_words_in_html(tagged_html)

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
    pattern = r'<span class="CEFR\w+">(\d+)</span><span class="CEFRA1">.</span><span class="CEFR\w+">(\d+)</span>'
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
    # Months
    'Jan.': {'cefr': 'A2', 'lang': 'en', 'note': 'January'},
    'Feb.': {'cefr': 'A2', 'lang': 'en', 'note': 'February'},
    'Mar.': {'cefr': 'A2', 'lang': 'en', 'note': 'March'},
    'Apr.': {'cefr': 'A2', 'lang': 'en', 'note': 'April'},
    'June.': {'cefr': 'A2', 'lang': 'en', 'note': 'June'},
    'Jul.': {'cefr': 'A2', 'lang': 'en', 'note': 'July'},
    'Aug.': {'cefr': 'A2', 'lang': 'en', 'note': 'August'},
    'Sep.': {'cefr': 'A2', 'lang': 'en', 'note': 'September'},
    'Sept.': {'cefr': 'A2', 'lang': 'en', 'note': 'September'},
    'Oct.': {'cefr': 'A2', 'lang': 'en', 'note': 'October'},
    'Nov.': {'cefr': 'A2', 'lang': 'en', 'note': 'November'},
    'Dec.': {'cefr': 'A2', 'lang': 'en', 'note': 'December'},

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
            pattern = pattern+fr"""<span class="CEFR\w+">{parts[i]}</span><span class="CEFRA1">.</span>"""
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

def my_search_replace(pattern, transform_function, S, offset=0):
    """
    Search for a pattern and then apply the transform_function to the match
    Note: Unlike re.sub() this function will continue the search with the next character from where the search started
          when there was not a match. In contrast, re.sub() continues with the next character after the pattern.
          As a result this function can support "overlapping" patterns.

    Args:
        pattern: a regex pattern
        transform_function: a function that will be called with the result of the match with the pattern
        S: string to modify.
        offset: a starting offset for the search

    Returns:
        The modified string S
    """
    #print(f"my_search_replace({pattern}, transform_function, '{S}', {offset=})")
    compiled_pattern = re.compile(pattern)
    match = compiled_pattern.search(S, offset)
    if match:
        prefix=S[:match.start()]
        replacement=transform_function(match)
        suffix=S[match.end():]
        #print(f"'{prefix=}', '{replacement=}', '{suffix=}'")
        # Note that the search continue on the replacement + suffix
        return prefix+my_search_replace(pattern, transform_function, replacement+suffix, 1)
    else:
        if (offset < len(S)) and (len(S) > 1):
            return my_search_replace(pattern, transform_function, S, offset+1)
        else:
            return S

def combine_names_in_html(html_text):
    """
    Combines consecutive name spans in HTML

    Args:
        html_text: The HTML string to modify.

    Returns:
        The modified HTML string with combined name spans.
    """
    # Regular expression patterns for name combinations
    pattern_place_comma_place='<span class="CEFR\\w+">([\\w-]+\\s*[\\w-]*)</span><span class="CEFRA1">,</span>\\s*<span class="CEFR\\w+">([\\w-]+)</span>'
    #
    pattern_KTH = r'<span class="CEFR\w+">KTH</span>\s*<span class="CEFR\w+">Royal</span>\s*<span class="CEFR\w+">Institute</span>\s*<span class="CEFR\w+">of</span>\s*<span class="CEFR\w+">Technology</span>'
    pattern_firstname_space_lastname = r'<span class="CEFR\w+">([\w-]+)</span>\s*<span class="CEFR\w+">([\w-]+)</span>'
    pattern_with_initial = r'<span class="CEFR\w+">([\w-]+)</span>\s*<span class="CEFR\w+">([\w-])</span><span class="CEFRA1">.</span>\s*<span class="CEFR\w+">([\w-]+)</span>'
    pattern_with_first_initial = r'<span class="CEFR\w+">([\w-])</span><span class="CEFRA1">.</span>\s<span class="CEFR\w+">([\w-]+)</span>\s*<span class="CEFR\w+">([\w-]+)</span>'
    pattern_with_three_names = r'<span class="CEFR\w+">([\w-]+)</span>\s*<span class="CEFR\w+">([\w-]+)</span>\s*<span class="CEFR\w+">([\w-]+)</span>'



    pattern_with_hyphen = r'<span class="CEFR\w+">([\w-]+)</span>-(\w*)\s*<span class="CEFR\w+">([\w-]+)</span>'
    pattern_with_hyphen_post_middle = r'<span class="CEFR\w+">([\w-]+)</span>\s*(\w*)-<span class="CEFR\w+">([\w-]+)</span>'
    pattern =              r'<span class="CEFR\w+">([\w-]+\s*[\w-]*)</span>\s*<span class="CEFR\w+">([\w-]+)</span>'

    # There is a problem with </span><span><span class ...
    pattern_span_span_without_preceeding_space = r'</span><span><span class='
    # Similarly for </span><span class="dont-index"><span class="CEFRA1">
    pattern_spanplus_span_without_preceeding_space = r'</span><span\s*([\w"=-]*)><span class='
    #
    def replace_name_with_initials(match):
        """Helper function to replace the name with the correct tag."""
        first_name, initial, last_name = match.groups()
        first_name=first_name.strip()
        initial=initial.strip()
        last_name=last_name.strip()
        print(f"{first_name=} {initial=}. {last_name=}")
        #
        # Check if we have an initial
        if initial:
            combined_name = f"{first_name} {initial}. {last_name}"
            if (first_name in common_english_and_swedish.names_of_persons) and (last_name in common_english_and_swedish.names_of_persons):
                return f'<span class="CEFRA1">{combined_name}</span>'
        return match.group(0) # Return original if not a name
    def replace_name_with_first_initial(match):
        """Helper function to replace the name with the correct tag."""
        initial,  middle_name, last_name = match.groups()
        initial=initial.strip()
        middle_name=middle_name.strip()
        last_name=last_name.strip()
        print(f"{initial=} {middle_name=} {last_name=}")
        #
        # Check if we have an initial
        if initial:
            combined_name = f"{initial}. {middle_name} {last_name}"
            if (middle_name in common_english_and_swedish.names_of_persons) and (last_name in common_english_and_swedish.names_of_persons):
                # need to ensure there is a space before the span
                return f' <span class="CEFRA1">{combined_name}</span>'
        return match.group(0) # Return original if not a name
    def replace_hyphenated_name(match):
        """Helper function to replace the name with the correct tag."""
        first_name,  middle_name, last_name = match.groups()
        first_name=first_name.strip()
        middle_name=middle_name.strip()
        last_name=last_name.strip()
        print(f"replace_hyphenated_name: {first_name=}-{middle_name=} {last_name=}")
        #
        # Check if we have an initial
        if middle_name:
            combined_name = f"{first_name}-{middle_name} {last_name}"
            if (first_name in common_english_and_swedish.names_of_persons) and (middle_name in common_english_and_swedish.names_of_persons) and (last_name in common_english_and_swedish.names_of_persons):
                return f'<span class="CEFRA1">{combined_name}</span>'
        else:
            combined_name = f"{first_name}-{last_name}"
            if (first_name in common_english_and_swedish.names_of_persons) and (last_name in common_english_and_swedish.names_of_persons):
                return f'<span class="CEFRA1">{combined_name}</span>'
            if combined_name in common_english_and_swedish.company_and_product_names:
                return f'<span class="CEFRA1">{combined_name}</span>'

        return match.group(0) # Return original if not a name
    def replace_hyphenated_post_middle_name(match):
        """Helper function to replace the name with the correct tag."""
        first_name,  middle_name, last_name = match.groups()
        first_name=first_name.strip()
        middle_name=middle_name.strip()
        last_name=last_name.strip()
        print(f"replace_hyphenated_post_middle_name: {first_name=} {middle_name=}-{last_name=}")
        #
        # Check if we have a first, middle, and last name
        if middle_name:
            if (first_name in common_english_and_swedish.names_of_persons) and (middle_name in common_english_and_swedish.names_of_persons) and (last_name in common_english_and_swedish.names_of_persons):
                combined_name = f"{first_name} {middle_name}-{last_name}"
                return f'<span class="CEFRA1">{combined_name}</span>'
        return match.group(0) # Return original if not a name

    def replace_name(match):
        """Helper function to replace the name with the correct tag."""
        first_name, last_name = match.groups()
        first_name=first_name.strip()
        last_name=last_name.strip()
        print(f"replace_name: {first_name=}  {last_name=}")
        #
        combined_name = f"{first_name} {last_name}"
        print(f"replace_name: {combined_name=}")
        #
        print(f"{(first_name in common_english_and_swedish.names_of_persons)=} {(last_name in common_english_and_swedish.names_of_persons)=} {combined_name=}")
        if (first_name in common_english_and_swedish.names_of_persons) and (last_name in common_english_and_swedish.names_of_persons):
            return f'<span class="CEFRA1">{combined_name}</span>'
        if combined_name in common_english_and_swedish.place_names:
            return f'<span class="CEFRA1">{combined_name}</span>'
        if combined_name in common_english_and_swedish.company_and_product_names:
            return f'<span class="CEFRA1">{combined_name}</span>'
        return match.group(0) # Return original if not a name
    def replace_place_comma_place(match):
        first_name, last_name = match.groups()
        first_name=first_name.strip()
        last_name=last_name.strip()
        print(f"replace_place_comma_place: {first_name=}  {last_name=}")
        #
        combined_name = f"{first_name}, {last_name}"
        print(f"replace_place_comma_place: {combined_name=}")
        #
        print(f"{(first_name in common_english_and_swedish.place_names)=} {(last_name in common_english_and_swedish.place_names)=} {combined_name=}")
        if (first_name in common_english_and_swedish.place_names) and (last_name in common_english_and_swedish.place_names):
            return f'<span class="CEFRA1">{combined_name}</span>'
        if combined_name in common_english_and_swedish.place_names:
            return f'<span class="CEFRA1">{combined_name}</span>'
        return match.group(0) # Return original if not a name
    def replace_spanplus_span_without_preceeding_space(match):
        """Helper function to add a space before spans without preceeding space(s)."""
        print(f"{match.groups()=}")
        if len(match.groups()) == 0:
            return f'</span> <span><span class='
        span_attrs = match.group(1)
        print(f"{span_attrs=}")
        #
        if not span_attrs:
            return f'</span> <span><span class='
        if span_attrs in ['class="dont-index']:
            return f'</span> <span {span_attrs}><span class='
        return match.group(0) # Return original
    def replace_three_names(match):
        """Helper function to replace the name with the correct tag."""
        first_name,  middle_name, last_name = match.groups()
        first_name=first_name.strip()
        middle_name=middle_name.strip()
        last_name=last_name.strip()
        print(f"replace_three_names: {first_name=} {middle_name=} {last_name=}")
        #
        # Check if we have a first, middle, and last name
        if middle_name:
            if (first_name in common_english_and_swedish.names_of_persons) and (middle_name in common_english_and_swedish.names_of_persons) and (last_name in common_english_and_swedish.names_of_persons):
                combined_name = f"{first_name} {middle_name} {last_name}"
                return f'<span class="CEFRA1">{combined_name}</span>'
        return match.group(0) # Return original if not a name

    #
    # Apply replacements

    html_text = re.sub(pattern_KTH, '<span class="CEFRA2">KTH Royal Institute of Technology</span>', html_text)
    html_text = my_search_replace(pattern_with_three_names, replace_three_names, html_text)
    html_text = my_search_replace(pattern_with_initial, replace_name_with_initials, html_text)
    html_text = my_search_replace(pattern_with_first_initial, replace_name_with_first_initial, html_text)
    html_text = my_search_replace(pattern_firstname_space_lastname, replace_name, html_text)
    html_text = my_search_replace(pattern_place_comma_place, replace_place_comma_place, html_text )
    html_text = my_search_replace(pattern_span_span_without_preceeding_space, replace_spanplus_span_without_preceeding_space, html_text)


    # html_text = my_search_replace(pattern_with_hyphen, replace_hyphenated_name, html_text)
    # html_text = my_search_replace(pattern_with_hyphen_post_middle, replace_hyphenated_post_middle_name, html_text)
    # html_text = my_search_replace(pattern, replace_name, html_text )
    # html_text = my_search_replace(pattern, replace_name, html_text)
    return html_text

def combine_English_words_in_html(html_text):
    """
    Combines consecutive spans in HTML based on these phrases appearing in common_english_words.common_English_words

    Args:
        html_text: The HTML string to modify.

    Returns:
        The modified HTML string with combined spans.
    """
    # Regular expression patterns for name combinations
    pattern_words_pairs = r'<span class="CEFR\w+">([\w-]+)</span>\s*<span class="CEFR\w+">([\w-]+)</span>'
    #
    def replace_word_pair(match):
        """Helper function to replace the name with the correct tag."""
        first_word, second_word = match.groups()
        first_word=first_word.strip()
        second_word=second_word.strip()
        combined_words = f"{first_word} {second_word}"
        #
        if combined_words in common_english_and_swedish.common_English_words:
            print(f"replace_word_pair: {first_word=}  {second_word=} with {combined_words=}")
            cefr_level, source = get_cefr_level_without_POS('en', combined_words, None)
            print(f"{cefr_level}, {source}")
            if cefr_level != 'XX':
                return f'<span class="CEFR{cefr_level}">{html.escape(combined_words)}</span>'
        return match.group(0) # Return original
    #
    # Apply replacements
    html_text = my_search_replace(pattern_words_pairs, replace_word_pair, html_text)
    return html_text

def clean_tagged_html(tagged_html):
    tagged_html=simplify_cefr_span_of_float(tagged_html)
    tagged_html=simplify_abbreviations(tagged_html, abbreviation_levels)
    tagged_html=combine_names_in_html(tagged_html)
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

    new_html_content = style_info+modified_HTML+create_footer()
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
    language=extract_iso_code(language)
    celf_levels=False
    src=None
    # handle punctuation
    if word in ['.', ',', '?', '!', "’"]:
        return 'A1', 'punctuation'
    if word in [';', ':', '-', '(', ')', '[', ']', '{', '}']:
        return 'B1', 'punctuation'
    if word in ['-',]: # add ellipses
        return 'C1', 'punctuation'
    # consider single letters A1
    if len(word) == 1:
        return 'A1', 'single letter'

    if is_number(word):
        return 'A1', 'number'

    # an approximate number
    if word.startswith('~') and len(word) >= 2 and is_number(word[1:]):
        return 'B1', 'number'

    if is_integer_range_or_ISSN(word):
        return 'A1', 'numeric range or ISSN'

    if word.startswith('(') and len(word) >= 2:
        word=word[1:]
    if word.endswith(')') and len(word) >= 2:
        word=word[:-1]
    if word.startswith('[') and len(word) >= 2:
        word=word[1:]
    if word.endswith(']') and len(word) >= 2:
        word=word[:-1]
    if word.startswith("‘") and len(word) >= 2: # lieft single quotation mark
        word=word[1:]
    if word.endswith("’") and len(word) >= 2: # right single quotation mark
        word=word[:-1]


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

        src='common_swedish_words'
        celf_levels=common_english_and_swedish.common_swedish_words.get(word.lower(), False)
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
        src='common_swedish_technical_words'
        celf_levels=common_english_and_swedish.common_swedish_technical_words.get(word.lower(), False)
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
        celf_levels=common_english_and_swedish.KTH_ordbok_Swedish_with_CEFR.get(word.lower(), False)
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
    # If the word starts with a '-', remove the dash and look again
    if word.startswith('-'):
        return get_cefr_level_without_POS(language, word[1:], context)

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
        print(f"get_specific_cefr_level('{language}', '{word}', '{pos}', {context}, {src}, {cerf_levels_from_src})")

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
                if 'verb (gerund)' in pos_in_level:
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

            # for handling POS tagging from spaCy + UDPipe
            if pos in ['ADJ']:  # adjective
                if 'adjective' in pos_in_level:
                    return wl, src

            if pos in ['ADP']: # adposition
                if 'preposition' in pos_in_level:
                    return wl, src

            if pos in ['ADV']: # adverb
                if 'adverb' in pos_in_level:
                    return wl, src

            if pos in ['AUX']: # auxiliary
                if 'verb (modal)' in pos_in_level:
                    return wl, src
                if 'modal verb' in pos_in_level:
                    return wl, src
                if 'verb' in pos_in_level:
                    return wl, src

            if pos in ['CCONJ']: # conjunction
                if 'conjunction' in pos_in_level:
                    return wl, src

            if pos in ['CCONJ']: # coordinating conjunction
                if 'conjunction' in pos_in_level:
                    return wl, src

            if pos in ['DET']: # determiner
                if 'determiner' in pos_in_level:
                    return wl, src
                if 'article' in pos_in_level:
                    return wl, src

            if pos in ['INTJ']: # interjection
                if 'interjection' in pos_in_level:
                    return wl, src

            if pos in ['NOUN']: # Noun
                if 'noun' in pos_in_level:
                    return wl, src

            if pos in ['NUM']: # numeral
                if 'cardinal number' in pos_in_level:
                    return wl, src
                if 'numeral' in pos_in_level:
                    return wl, src

            if pos in ['PART']: # particle
                if 'particle' in pos_in_level:
                    return wl, src

            if pos in ['PRON']: # pronoun
                if 'possessive pronoun' in pos_in_level:
                    return wl, src
                if 'pronoun' in pos_in_level:
                    return wl, src

            if pos in ['PROPN']: # # proper noun
                if 'proper noun' in pos_in_level:
                    return wl, src
                if 'noun' in pos_in_level:
                    return wl, src
                if word in common_english_and_swedish.names_of_persons:
                    return 'A1', 'names_of_persons'

            if pos in ['PUNCT']: # punctuation
                if 'punctuation' in pos_in_level:
                    return wl, src

            if pos in ['SCONJ']: # subordinating conjunction
                if 'subordinating conjunction' in pos_in_level:
                    return wl, src

            if pos == 'SYM': # Symbol
                return 'A1', 'fixed'

            if pos in ['VERB']: # verb
                if 'verb gerund or present participle' in pos_in_level:
                    return wl, src
                if 'verb (present participle)' in pos_in_level:
                    return wl, src
                if 'verb' in pos_in_level:
                    return wl, src

            if pos in ['X']: # other
                if 'other' in pos_in_level:
                    return wl, src

            # there is also SPACE as a POS, which is just a space

            # If no POS above matches, check if it is an acronym
            if 'acronym' in pos_in_level:
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
        elif paragraph.name == 'div':
            children = paragraph.findChildren(recursive=False) # changed from False
            for child in children:
                new_spans=tokenize_paragraph(soup, child)
                # replace the original text with the new spans
                #child.replace_with(*new_spans)
                child.clear()
                for ns in new_spans:
                    child.append(ns)
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
    global nlp # dict of spaCy + UDPipe pipelines

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

    if testing_mode_flag:
        x1=get_acronym_cefr_levels('ECTS')
        print(f"get_acronym_cefr_levels: {x1}")
        x=get_lowest_cefr_level('en', 'ECTS', None, 'bogus', get_acronym_cefr_levels('ECTS'))
        print(f"is ECTS in ancronyms? {x}")
    
    if Verbose_Flag:
        print(f'{(len(well_known_acronyms)):>{Numeric_field_width}} unique acronyms in ({len(common_acronyms.well_known_acronyms_list)}) well_known_acronyms')

    nlp=dict()
    spacy_udpipe.download("en") # download English model
    spacy_udpipe.download("sv") # download Swedish model
    # set up two spaCy + UDPipe pipelines
    nlp['en'] = spacy_udpipe.load("en")
    nlp['sv'] = spacy_udpipe.load("sv")


    process_course(course_id)


if __name__ == "__main__": main()
