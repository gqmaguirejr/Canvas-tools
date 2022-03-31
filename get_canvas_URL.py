#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# ./get_canvas_URL.py url
#
# Output: file containing URL's contents
#
#
# with the option "-v" or "--verbose" you get lots of output - showing in detail the operations of the program
#
# Can also be called with an alternative configuration file:
# ./list_your_courses.py --config config-test.json
#
# Example:
# ./get_canvas_URL.py https://canvas.kth.se/courses/11/quizzes/39141/history?quiz_submission_id=759552&version=1
#
# ./get_canvas_URL.py --config config-test.json https://canvas.kth.se/courses/11/quizzes/39141/history?quiz_submission_id=759552&version=1
#
# 
# G. Q. Maguire Jr.
#
# based on earlier quizzes-and-answers-in-course.py
#
# 2022-02-25
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

import urllib.request
import urllib.parse

#Subclass of HTTPRedirectHandler. Does not do much, but is very
#verbose. prints out all the redirects. Compaire with what you see
#from looking at your browsers redirects (using live HTTP Headers or similar)
class ShibRedirectHandler (urllib.request.HTTPRedirectHandler):
    def http_error_302(self, req, fp, code, msg, headers):
        print("Request={}".format(req))
        print("URL={}".format(fp.geturl()))
        print("code={}".format(code))
        print("msg={}".format(msg))
        print("headers={}".format(headers))
        #without this return (passing parameters onto baseclass) 
        #redirect following will not happen automatically for you.
        return urllib.request.HTTPRedirectHandler.http_error_302(self,
                                                          req,
                                                          fp,
                                                          code,
                                                          msg,
                                                          headers)


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

def list_quizzes(course_id):
    quizzes_found_thus_far=[]
    # Use the Canvas API to get the list of quizzes for the course
    #GET /api/v1/courses/:course_id/quizzes

    url = "{0}/courses/{1}/quizzes".format(baseUrl, course_id)
    if Verbose_Flag:
        print("url: {}".format(url))

    r = requests.get(url, headers = header)
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
                r = requests.get(r.links['next']['url'], headers=header)  
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

    r = requests.get(url, headers = header)
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
                r = requests.get(r.links['next']['url'], headers=header)  
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

    extra_parameters={'include[]': 'submission'}

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
                r = requests.get(r.links['next']['url'], headers=header)  
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
        return

    results_url=remainder[0]

    cookieprocessor = urllib.request.HTTPCookieProcessor()
    opener = urllib.request.build_opener(ShibRedirectHandler, cookieprocessor)

    #Edit: should be the URL of the site/page you want to load that is protected with Shibboleth
    x1=opener.open(results_url)
    x2=x1.read().decode('utf-8')

    # x2 is
    # '<!DOCTYPE html>\r\n<html>\r\n    <head>\r\n        <meta charset="utf-8" />\r\n        <meta name="viewport" content="width=device-width,initial-scale=1.0">\r\n        <title>KTH Royal Institute of Technology Web Login Service - Loading Session Information</title>\r\n        <link rel="stylesheet" type="text/css" href="/idp/css/main.css">\r\n        <script>\r\n        <!--\r\n"use strict";\nfunction readLocalStorage(key) {\n    var success;\n    try {\n        var value = localStorage.getItem(key);\n        if (value != null) {\n            document.form1["shib_idp_ls_value." + key].value = value;\n        }\n        success = "true";\n    } catch (e) {\n        success = "false";\n        document.form1["shib_idp_ls_exception." + key].value = e;\n    }\n    document.form1["shib_idp_ls_success." + key].value = success;\n}\n\nfunction isLocalStorageSupported() {\n    try {\n        localStorage.setItem("shib_idp_ls_test", "shib_idp_ls_test");\n        localStorage.removeItem("shib_idp_ls_test");\n        return true;\n    } catch (e) {\n        return false;\n    }\n}\n        // -->\r\n        </script>\r\n    </head>\r\n    <body onload="doLoad()">\r\n        <div class="wrapper">\r\n            <div class="container">\r\n                <header>\r\n                    <h3>KTH Royal Institute of Technology Web Login Service - Loading Session Information</h3>\r\n                </header>\r\n                <div class="content">\r\n                Loading login session information from the browser...\r\n                </div>\r\n                <noscript>\r\n                    <div class="content">\r\n                    Since your browser does not support JavaScript, you must press the Continue button once to proceed.\r\n                    </div>\r\n                </noscript>\r\n<form name="form1" action="/idp/profile/SAML2/Redirect/SSO?execution=e2s1" method="post">\n    <input type="hidden" name="csrf_token" value="_7dd60cac37098ae38c3214b5a5fa2d3335979986" />\n        <input name="shib_idp_ls_exception.shib_idp_session_ss" type="hidden" />\n        <input name="shib_idp_ls_success.shib_idp_session_ss" type="hidden" value="false" />\n        <input name="shib_idp_ls_value.shib_idp_session_ss" type="hidden" />\n        <input name="shib_idp_ls_exception.shib_idp_persistent_ss" type="hidden" />\n        <input name="shib_idp_ls_success.shib_idp_persistent_ss" type="hidden" value="false" />\n        <input name="shib_idp_ls_value.shib_idp_persistent_ss" type="hidden" />\n    <input name="shib_idp_ls_supported" type="hidden" />\n    <input name="_eventId_proceed" type="hidden" />\n    <noscript>\n        <input type="submit" value="Continue" />\n    </noscript>\n</form>\n\n<script>\n<!--\nfunction doLoad() {\n    var localStorageSupported = isLocalStorageSupported();\n    document.form1["shib_idp_ls_supported"].value = localStorageSupported;\n    if (localStorageSupported) {\n        readLocalStorage("shib_idp_session_ss");\n        readLocalStorage("shib_idp_persistent_ss");\n    }\n    document.form1.submit();\n}\n// -->\n</script>            </div>\r\n            <footer>\r\n                <div class="container container-footer">\r\n                    <p class="footer-text">Please contact it-support@kth.se for information about this service.</p>\r\n                </div>\r\n            </footer>\r\n        </div>\r\n    </body>\r\n</html>\r\n'

    # From this the form is:
    # <form name="form1" action="/idp/profile/SAML2/Redirect/SSO?execution=e1s1" method="post">
    #     <input type="hidden" name="csrf_token" value="_083c7d552b9a95b0df44ce4d21efa1f46069432e" />
    #         <input name="shib_idp_ls_exception.shib_idp_session_ss" type="hidden" />
    #         <input name="shib_idp_ls_success.shib_idp_session_ss" type="hidden" value="false" />
    #         <input name="shib_idp_ls_value.shib_idp_session_ss" type="hidden" />
    #         <input name="shib_idp_ls_exception.shib_idp_persistent_ss" type="hidden" />
    #         <input name="shib_idp_ls_success.shib_idp_persistent_ss" type="hidden" value="false" />
    #         <input name="shib_idp_ls_value.shib_idp_persistent_ss" type="hidden" />
    #     <input name="shib_idp_ls_supported" type="hidden" />
    #     <input name="_eventId_proceed" type="hidden" />
    #     <noscript>
    #         <input type="submit" value="Continue" />
    #     </noscript>

    # the full URL for the form is https://saml-5.sys.kth.se/idp/profile/SAML2/Redirect/SSO?execution=e1s1
    form_date={
        "csrf_token": "_083c7d552b9a95b0df44ce4d21efa1f46069432e",
        # "shib_idp_ls_exception.shib_idp_session_ss",
        "shib_idp_ls_success.shib_idp_session_ss": "false",
        #"shib_idp_ls_value.shib_idp_session_ss",
        #"shib_idp_ls_exception.shib_idp_persistent_ss",
        "shib_idp_ls_success.shib_idp_persistent_ss": "false",
        #"shib_idp_ls_value.shib_idp_persistent_ss",
        #"shib_idp_ls_supported",
        #"_eventId_proceed"
    #         <input type="submit" value="Continue" />
    #    
        }
    url='https://saml-5.sys.kth.se/idp/profile/SAML2/Redirect/SSO?execution=e1s1'
    data = parse.urlencode(form_date).encode()
    req = request.Request(url, data=data)
    response = request.urlopen(req)
    print(response.read())
    return

    # https://login.ug.kth.se/adfs/ls/?SAMLRequest=fZLLTsMwEEV%2FxZp94tSQklpNUaFCVOJRkcCCDXLSaWPh2sXj8Ph70hcqLFh75tyZMx6ef64Me0dP2tkcenECDG3t5touc3gsr6IMzkdDUisj1nLchsY%2B4FuLFFjXaEnuXnJovZVOkSZp1QpJhloW49sbKeJErr0LrnYG2JgIfeiiLp2ldoW%2BQP%2Bua3x8uMmhCWFNkvMNMkpj%2BqL4NTQxIdfzNe8gC22Qb2fgG7bgs%2Fui5EVxD2zSTaStCtstDiDjltrG7fKAUfMFcUMc2HSSw0svqxZiLkSiKtVP0tM6GVQqrTDrY5XiIOvKiFqcWgrKhhxEIkSUiEiclb2%2BPBlIkcb9LH0GNtsveKHtTtx%2FNqpdEcnrspxFmxWAPR0O0BXAXrfcpvtjz%2F%2BD1UEujI5V%2FhVJja4qZzA0Q34c9HPlu448ncyc0fUXGxvjPi49qoA5BN8i8NG%2B7%2Fd%2FGH0D&RelayState=e2s1

    #Inspect the page source of the Shibboleth login form; find the input names for the username
    #and password, and edit according to the dictionary keys here to match your input names
    loginData = urllib.parse.urlencode({'UserName':'<your-username>', 'Password':'<your-password>'})
    bLoginData = loginData.encode('ascii')

    #By looking at the source of your Shib login form, find the URL the form action posts back to
    #hard code this URL in the mock URL presented below.
    #Make sure you include the URL, port number and path
    response = opener.open("https://test-idp.server.example", bLoginData)
    #See what you got.
    print (response.read())

    # URL will have the form 'https://canvas.kth.se/courses/:course_id/quizzes/:quiz_id/history?quiz_submission_id=:submission_id&version=:version:number'
    if results_url:
        submitted_quiz = requests.get(results_url)
        status_code=submitted_quiz.status_code
        print("status_code={}".format(status_code))
        submission_html=submitted_quiz.text
        if submission_html and len(submission_html) > 0:
            print("found a submission: {}".format(submission_html))
            document = html.document_fromstring(submission_html)
            link = document.find('.//link')
            print("link={}".format(link))
            for attribute in link.attrib:
                print("attribute {0}={1}".format(attribute, link.attrib[attribute]))
                if link.attrib['href'] == '/idp/css/main.css':
                    print("hi")

if __name__ == "__main__": main()

