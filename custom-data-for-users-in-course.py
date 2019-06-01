#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# ./custom-data-for-users-in-course.py course_id
#
# Output: none
#
# with the option '-C'or '--containers' use HTTP rather than HTTPS for access to Canvas
# with the option -t' or '--testing' testing mode
#
# with the option "-v" or "--verbose" you get lots of output - showing in detail the operations of the program
#
# Can also be called with an alternative configuration file:
# ./custom-data-for-users-in-course.py --config config-test.json
#
# Example:
# ./custom-data-for-users-in-course.py 4
#
# ./custom-data-for-users-in-course.py --config config-test.json 4
#
# ./custom-data-for-users-in-course.py -C 5
#
# G. Q. Maguire Jr.
#
# 2019.02.02
#

import requests, time
import pprint
import optparse
import sys
import json

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

# create the following dict to use as an associate directory about users
selected_user_data={}


def users_in_course(course_id):
    user_found_thus_far=[]
    # Use the Canvas API to get the list of users enrolled in this course
    #GET /api/v1/courses/:course_id/enrollments

    url = "{0}/courses/{1}/enrollments".format(baseUrl,course_id)
    if Verbose_Flag:
        print("url: {}".format(url))

    extra_parameters={'per_page': '100'}
    r = requests.get(url, params=extra_parameters, headers = header)
    if Verbose_Flag:
        print("result of getting enrollments: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        page_response=r.json()
        
        for p_response in page_response:  
            user_found_thus_far.append(p_response)

            # the following is needed when the reponse has been paginated
            # i.e., when the response is split into pieces - each returning only some of the list of modules
            # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
            while r.links['current']['url'] != r.links['last']['url']:  
                r = requests.get(r.links['next']['url'], headers=header)  
                page_response = r.json()  
                for p_response in page_response:  
                    user_found_thus_far.append(p_response)
    return user_found_thus_far

def user_profile_url(user_id):
    # Use the Canvas API to get the profile of a user
    #GET /api/v1/users/:user_id/profile
    url = "{0}/users/{1}/profile".format(baseUrl, user_id)
    if Verbose_Flag:
        print("user url: {}".format(url))

    r = requests.get(url, headers = header)
    if Verbose_Flag:
        print("result of getting profile: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        page_response=r.json()
        return page_response
    return []

#curl 'https://kth.test.instructure.com/api/v1/users/self/custom_data/program_of_study' \
#  -H 'Content-Type: application/json' \
#  -X PUT \
#  -d '{
#        "ns": "se.kth.canvas-app.program_of_study",
#        "data": {
#      "programs": [{"code": "TIVNM-DASC", "name": "ICT Innovation, (TIVNM), Data Science (DASC) Program", "start": 2016}]
#        }
#      }'
def put_user_custom_data_by_sis_id(user_id, name_space, scope, data):
    # Use the Canvas API to set a user's custom data
    # PUT /api/v1/users/:user_id/custom_data(/*scope)
    url = "{0}/users/sis_user_id:{1}/custom_data/{2}".format(baseUrl, user_id, scope)
    if Verbose_Flag:
        print("url: {}".format(url))

    payload={'ns': name_space,
             'data': data
    }
    r = requests.put(url, headers = header, json=payload)
    if Verbose_Flag:
        print("result of setting custom data: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        page_response=r.json()
        return page_response
    return []

def put_user_custom_data_by_user_id(user_id, name_space, scope, data):
    # Use the Canvas API to set a user's custom data
    # PUT /api/v1/users/:user_id/custom_data(/*scope)
    url = "{0}/users/{1}/custom_data/{2}".format(baseUrl, user_id, scope)
    if Verbose_Flag:
        print("url: {}".format(url))

    payload={'ns': name_space,
             'data': data
    }
    r = requests.put(url, headers = header, json=payload)
    if Verbose_Flag:
        print("result of setting custom data: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        page_response=r.json()
        return page_response
    return []

def get_user_custom_data_by_sis_id(user_id, name_space, scope):
    # Use the Canvas API to get a user's custom data
    # GET /api/v1/users/:user_id/custom_data(/*scope)
    url = "{0}/users/sis_user_id:{1}/custom_data/{2}".format(baseUrl, user_id, scope)
    if Verbose_Flag:
        print("url: {}".format(url))

    payload={'ns': name_space }

    r = requests.get(url, headers = header, json=payload)
    if Verbose_Flag:
        print("result of getting custom data: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        page_response=r.json()
        return page_response
    return []

def get_user_custom_data_by_user_id(user_id, name_space, scope):
    # Use the Canvas API to get a user's custom data
    # GET /api/v1/users/:user_id/custom_data(/*scope)
    url = "{0}/users/{1}/custom_data/{2}".format(baseUrl, user_id, scope)
    if Verbose_Flag:
        print("url: {}".format(url))

    payload={'ns': name_space }

    r = requests.get(url, headers = header, json=payload)
    if Verbose_Flag:
        print("result of getting custom data: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        page_response=r.json()
        return page_response
    return []



def section_name_from_section_id(sections_info, section_id): 
    for i in sections_info:
        if i['id'] == section_id:
            return i['name']

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
            while r.links['current']['url'] != r.links['last']['url']:  
                r = requests.get(r.links['next']['url'], headers=header)  
                page_response = r.json()  
                for p_response in page_response:  
                    sections_found_thus_far.append(p_response)

    return sections_found_thus_far

def list_your_courses():
    courses_found_thus_far=[]
    # Use the Canvas API to get the list of all of your courses
    # GET /api/v1/courses

    url = baseUrl+'courses'
    if Verbose_Flag:
        print("url: {}".format(url))

    r = requests.get(url, headers = header)
    if Verbose_Flag:
        print("result of getting courses: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        page_response=r.json()

        for p_response in page_response:  
            courses_found_thus_far.append(p_response)

            # the following is needed when the reponse has been paginated
            # i.e., when the response is split into pieces - each returning only some of the list of modules
            # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
            while r.links['current']['url'] != r.links['last']['url']:  
                r = requests.get(r.links['next']['url'], headers=header)  
                if Verbose_Flag:
                    print("result of getting courses for a paginated response: {}".format(r.text))
                page_response = r.json()  
                for p_response in page_response:  
                    courses_found_thus_far.append(p_response)

    return courses_found_thus_far

def users_in_account(account_id):
    user_found_thus_far=[]
    # Use the Canvas API to get the list of users known to the system
    # GET /api/v1/accounts/:account_id/users

    url = "{0}/accounts/{1}/users".format(baseUrl, account_id)
    if Verbose_Flag:
        print("url: {}".format(url))

    extra_parameters={'per_page': '100'}
    r = requests.get(url, params=extra_parameters, headers = header)
    if Verbose_Flag:
        print("result of getting users for account: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        page_response=r.json()
        
        for p_response in page_response:  
            user_found_thus_far.append(p_response)

            # the following is needed when the reponse has been paginated
            # i.e., when the response is split into pieces - each returning only some of the list of modules
            # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
            while r.links['current']['url'] != r.links['last']['url']:  
                r = requests.get(r.links['next']['url'], headers=header)  
                page_response = r.json()  
                for p_response in page_response:  
                    user_found_thus_far.append(p_response)
    return user_found_thus_far

def create_user(account_id, user_name, short_name, sortable_name, time_zone, locale, birthdate, unique_id, password, sis_user_id, email_address):
    # Create a user
    # POST /api/v1/accounts/:account_id/users
    # Create and return a new user and pseudonym for an account.

    # If you don't have the “Modify login details for users” permission, but self-registration is enabled on the account, you can still use this endpoint to register new users. Certain fields will be required, and others will be ignored (see below).

    url = "{0}/accounts/{1}/users".format(baseUrl, account_id)
    if Verbose_Flag:
        print("url: {}".format(url))

    # Request Parameters:
    # Parameter		Type	Description
    # user[name]		string	
    # The full name of the user. This name will be used by teacher for grading. Required if this is a self-registration.
    #
    # user[short_name]		string	
    # User's name as it will be displayed in discussions, messages, and comments.
    #
    # user[sortable_name]		string	
    # User's name as used to sort alphabetically in lists.
    #
    # user[time_zone]		string	
    # The time zone for the user. Allowed time zones are IANA time zones or friendlier Ruby on Rails time zones.
    #
    # user[locale]		string	
    # The user's preferred language, from the list of languages Canvas supports. This is in RFC-5646 format.
    #
    # user[birthdate]		Date	-- note that this is in ISO8601 format
    # The user's birth date.
    #
    # user[terms_of_use]		boolean	
    # Whether the user accepts the terms of use. Required if this is a self-registration and this canvas instance requires users to accept the terms (on by default).
    #
    # If this is true, it will mark the user as having accepted the terms of use.
    #
    # user[skip_registration]		boolean	
    # Automatically mark the user as registered.
    #
    # If this is true, it is recommended to set "pseudonym[send_confirmation]" to true as well. Otherwise, the user will not receive any messages about their account creation.
    #
    # The users communication channel confirmation can be skipped by setting "communication_channel[skip_confirmation]" to true as well.
    #
    # pseudonym[unique_id]	Required	string	
    # User's login ID. If this is a self-registration, it must be a valid email address.
    #
    # pseudonym[password]		string	
    # User's password. Cannot be set during self-registration.
    #
    # pseudonym[sis_user_id]		string	
    # SIS ID for the user's account. To set this parameter, the caller must be able to manage SIS permissions.
    #
    # pseudonym[integration_id]		string	
    # Integration ID for the login. To set this parameter, the caller must be able to manage SIS permissions. The Integration ID is a secondary identifier useful for more complex SIS integrations.
    #
    # pseudonym[send_confirmation]		boolean	
    # Send user notification of account creation if true. Automatically set to true during self-registration.
    #
    # pseudonym[force_self_registration]		boolean	
    # Send user a self-registration style email if true. Setting it means the users will get a notification asking them to “complete the registration process” by clicking it, setting a password, and letting them in. Will only be executed on if the user does not need admin approval. Defaults to false unless explicitly provided.
    #
    # pseudonym[authentication_provider_id]		string	
    # The authentication provider this login is associated with. Logins associated with a specific provider can only be used with that provider. Legacy providers (LDAP, CAS, SAML) will search for logins associated with them, or unassociated logins. New providers will only search for logins explicitly associated with them. This can be the integer ID of the provider, or the type of the provider (in which case, it will find the first matching provider).
    #
    # communication_channel[type]		string	
    # The communication channel type, e.g. 'email' or 'sms'.
    #
    # communication_channel[address]		string	
    # The communication channel address, e.g. the user's email address.
    #
    # communication_channel[confirmation_url]		boolean	
    # Only valid for account admins. If true, returns the new user account confirmation URL in the response.
    #
    # communication_channel[skip_confirmation]		boolean	
    # Only valid for site admins and account admins making requests; If true, the channel is automatically validated and no confirmation email or SMS is sent. Otherwise, the user must respond to a confirmation message to confirm the channel.
    #
    # If this is true, it is recommended to set "pseudonym[send_confirmation]" to true as well. Otherwise, the user will not receive any messages about their account creation.
    #
    # force_validations		boolean	
    # If true, validations are performed on the newly created user (and their associated pseudonym) even if the request is made by a privileged user like an admin. When set to false, or not included in the request parameters, any newly created users are subject to validations unless the request is made by a user with a 'manage_user_logins' right. In which case, certain validations such as 'require_acceptance_of_terms' and 'require_presence_of_name' are not enforced. Use this parameter to return helpful json errors while building users with an admin request.
    #
    # enable_sis_reactivation		boolean	
    # When true, will first try to re-activate a deleted user with matching sis_user_id if possible. This is commonly done with user and communication_channel so that the default communication_channel is also restored.
    #
    # destination		URL	
    # If you're setting the password for the newly created user, you can provide this param with a valid URL pointing into this Canvas installation, and the response will include a destination field that's a URL that you can redirect a browser to and have the newly created user automatically logged in. The URL is only valid for a short time, and must match the domain this request is directed to, and be for a well-formed path that Canvas can recognize.
    #
    # Returns a User
    #
    payload={'user[name]': user_name,
             'user[short_name]': short_name,
             'user[sortable_name]': sortable_name,
             'user[time_zone]': time_zone,
             'user[locale]': locale,
             'user[birthdate]': birthdate,
             'user[terms_of_use]': 'true', # indicate that user has accepted terms of use
             'user[skip_registration]': 'true', # indicate that user need not register
             'pseudonym[unique_id]': unique_id,
             'pseudonym[password]': password,
             'pseudonym[sis_user_id]': sis_user_id,
             'pseudonym[send_confirmation]': 'true',
             'communication_channel[type]': 'email',
             'communication_channel[address]': email_address,
             'communication_channel[skip_confirmation]': 'true',
             'force_validations': 'false',
             'enable_sis_reactivation': 'false',
    }
    r = requests.post(url, headers = header, data=payload)
    if Verbose_Flag:
        print("status code: {0}, result of creating a user: {1}".format(r.status_code, r.text))

    if r.status_code == requests.codes.ok:
        page_response=r.json()

    return page_response

def enrollments_in_course(course_id):
    global Verbose_Flag
    users_found_thus_far=[]

    # Use the Canvas API to get the list of users enrolled in this course
    #GET /api/v1/courses/:course_id/enrollments

    url = "{0}/courses/{1}/enrollments".format(baseUrl,course_id)
    if Verbose_Flag:
        print("url: {}".format(url))

    extra_parameters={'per_page': '100'}
    r = requests.get(url, params=extra_parameters, headers = header)
    if Verbose_Flag:
        print("result of getting enrollments: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        page_response=r.json()
        
        for p_response in page_response:  
            user_found_thus_far.append(p_response)

            # the following is needed when the reponse has been paginated
            # i.e., when the response is split into pieces - each returning only some of the list of modules
            # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
            while r.links['current']['url'] != r.links['last']['url']:  
                r = requests.get(r.links['next']['url'], headers=header)  
                page_response = r.json()  
                for p_response in page_response:  
                    user_found_thus_far.append(p_response)
    return user_found_thus_far

# Enroll a user 
# return the user's Canvas user_id
def enroll_user_with_sis_id(course_id, sis_id, role, section_id):
    global Verbose_Flag
    # Request Parameters:
    #Parameter		Type	Description
    # enrollment[user_id]	Required	string	The ID of the user to be enrolled in the course.
    # enrollment[type]	Required	string	Enroll the user as a student, teacher, TA, observer, or designer. If no value is given, the type will be inferred by enrollment if supplied, otherwise 'StudentEnrollment' will be used.
    #                                           Allowed values:
    #                                            StudentEnrollment, TeacherEnrollment, TaEnrollment, ObserverEnrollment, DesignerEnrollment
    # enrollment[enrollment_state]		string	If set to 'active,' student will be immediately enrolled in the course. Otherwise they will be required to accept a course invitation. Default is 'invited.'.
    # If set to 'inactive', student will be listed in the course roster for teachers, but will not be able to participate in the course until their enrollment is activated.
    #                                           Allowed values: active, invited, inactive
    # enrollment[notify]		boolean	If true, a notification will be sent to the enrolled user. Notifications are not sent by default.


    # Use the Canvas API to create an enrollment
    # POST /api/v1/courses/:course_id/enrollments

    url = "{0}/courses/{1}/enrollments".format(baseUrl, course_id)
    if Verbose_Flag:
        print("url: {}".format(url))

    payload={'enrollment[user_id]': 'sis_user_id:'+sis_id,
             'enrollment[type]': role,
             'enrollment[enrollment_state]': 'active' # make the person automatically active in the course
    }
    
    if section_id:              # if there is a section_id then add the users to section
        payload['enrollment[course_section_id]']=section_id

    r = requests.post(url, headers = header, data=payload)
    if Verbose_Flag:
        print("result of posting an enrollment: {}".format(r.text))
    if r.status_code == requests.codes.ok:
        page_response=r.json()
        if Verbose_Flag:
            print("inserted person into course")
        return page_response['user_id']
    else:
        if r.status_code == 404: # "404 Not Found"
            message="student {0} not in Canvas - status code {1} ".format(kthid, r.status_code)
            print(message)
        else:
            message="unable to enroll student {0} in Canvas course {1}, status code {2} ".format(kthid, course_id, r.status_code)
            print(message)
    return None

def existing_user_by_sis_id(all_users, sis_user_id):
    # if there are no users, then by definition the user does not yet exist
    if not all_users:
        return False

    for user in all_users:
        if user['sis_user_id'] == sis_user_id:
            return True
    return False

def existing_user_in_course_by_sis_id(all_users_in_course, sis_user_id):
    # if there are no users in the course, then by definition the user does not yet exist in this course
    if not all_users_in_course:
        return False

    for user in all_users_in_course:
        if user['sis_user_id'] == sis_user_id:
            return True
    return False

KOPPSbaseUrl = 'https://www.kth.se'
def v1_get_programmes():
    global Verbose_Flag
    #
    # Use the KOPPS API to get the data
    # note that this returns XML
    url = "{0}/api/kopps/v1/programme".format(KOPPSbaseUrl)
    if Verbose_Flag:
        print("url: " + url)
    #
    r = requests.get(url)
    if Verbose_Flag:
        print("result of getting v1 programme: {}".format(r.text))
    #
    if r.status_code == requests.codes.ok:
        return r.text           # simply return the XML
    #
    return None

def programs_and_owner_and_titles():
    programs=v1_get_programmes()
    xml=BeautifulSoup(programs, "lxml")
    program_and_owner_titles=dict()
    for prog in xml.findAll('programme'):
        if prog.attrs['cancelled'] == 'false':
            owner=prog.owner.string
            titles=prog.findAll('title')
            title_en=''
            title_sv=''
            for t in titles:
                if t.attrs['xml:lang'] == 'en':
                    title_en=t.string
                if t.attrs['xml:lang'] == 'sv':
                    title_sv=t.string
            program_and_owner_titles[prog.attrs['code']]={'owner': owner, 'title_en': title_en, 'title_sv': title_sv}
    #
    return program_and_owner_titles

def main():
    global Verbose_Flag

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

    parser.add_option('-t', '--testing',
                      dest="testing",
                      default=False,
                      action="store_true",
                      help="execute test code"
    )

    parser.add_option('-C', '--containers',
                      dest="containers",
                      default=False,
                      action="store_true",
                      help="for the container enviroment in the virtual machine"
    )


    
    options, remainder = parser.parse_args()

    Verbose_Flag=options.verbose
    if Verbose_Flag:
        print("ARGV      : {}".format(sys.argv[1:]))
        print("VERBOSE   : {}".format(options.verbose))
        print("REMAINING : {}".format(remainder))
        print("Configuration file : {}".format(options.config_filename))

    initialize(options)

    if (len(remainder) < 1):
        print("Insuffient arguments - must provide account_id course_id\n")
        sys.exit()
              
    course_id=remainder[0]
    all_users_in_course=users_in_course(course_id)
    if all_users_in_course:
        if Verbose_Flag:
    	    print(all_users_in_course)

    if not all_users_in_course:
        sys.exit()

    if options.testing:
        print("testing for course_id={}".format(course_id))
        data={"programs": [{"code": 'FakeFake', "name": 'Fake program', "start": 1600}]
        }
        result=put_user_custom_data_by_sis_id('z0', 'se.kth.canvas-app.program_of_study', 'program_of_study', data)
        if Verbose_Flag:
            print("result of setting custom data for user z0 is {0}".format(result))

        sys.exit()

    all_sis_ids=set()

    for user in all_users_in_course:
        name=user['user'].get('name', 'no name')
        sis_user_id=user.get('sis_user_id', [])
        
        if sis_user_id not in all_sis_ids:
            print("user name={0} with id={1} and sis_id={2}".format(name, user['id'], sis_user_id))
            if sis_user_id:
                result2=get_user_custom_data_by_sis_id(user['sis_user_id'], 'se.kth.canvas-app.program_of_study', 'program_of_study')
                print("result of getting custom data for user {0} is {1}".format(name, result2))
                all_sis_ids.add(sis_user_id)

    #result_for_self=get_user_custom_data_by_user_id('self', 'se.kth.canvas-app.program_of_study', 'program_of_study')
    #print("result of getting custom data for user self is {0}".format(result_for_self))

if __name__ == "__main__": main()

