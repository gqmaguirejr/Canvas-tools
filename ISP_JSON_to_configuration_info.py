#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -*- mode: python; python-indent-offset: 4 -*-
#
# ./ISP_JSON_to_configuration_info.py xxx.json [course_id]
#
# The course_id has to be a course where the supervisor is enrolled (as student, teacher, ... )
#
#
# Output: supervisor information for LaTeX thesis temlate
#
# with the option "-v" or "--verbose" you get lots of output - showing in detail the operations of the program
#
# Can also be called with an alternative configuration file:
# ./ISP_JSON_to_configuration_info.py --config config-test.json 11
#
# Example:
# ./ISP_JSON_to_configuration_info.py /tmp/example.json 11
#
# ./ISP_JSON_to_configuration_info.py --config config-test.json /tmp/example.json 6434
#
# based on earlier whoami_for_latex.py
#
# G. Q. Maguire Jr.
#
# 2025-10-14
#

import requests, time
import pprint
import optparse
import sys
import json

#############################
###### EDIT THIS STUFF ######
#############################

global baseUrl	# the base URL used for access to Canvas
global header	# the header for all HTML requests
global payload	# place to store additionally payload when needed for options to HTML requests

global kth_header	# the header for all HTML requests
global kth_host


# Based upon the options to the program, initialize the variables used to access Canvas gia HTML requests
def initialize(options):
    global baseUrl, header, payload
    global kth_header, kth_host

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
            kth_api_info=configuration.get("KTH_API")
            if kth_api_info:
                kth_key=kth_api_info["key"]
                kth_host=kth_api_info["host"]
                kth_header = {'api_key': kth_key, 'Content-Type': 'application/json', 'Accept': 'application/json' }
            else:
                kth_key=None
                kth_host=None
                kth_header = None

    except:
        print(f"Unable to open configuration file named {config_file}")
        print("Please create a suitable configuration file, the default name is config.json")
        sys.exit()

# search for user in account by e-mail address
# https://canvas.kth.se/accounts/59/users?search_term=verardo@kth.se
def user_via_search_in_account(email_address, account_id):
    user_found_thus_far=[]
    url = f"{baseUrl}/accounts/{account_id}/users?search_term={email_address}"
    if Verbose_Flag:
        print("url: {}".format(url))

    extra_parameters={'per_page': '100'}
    r = requests.get(url, params=extra_parameters, headers = header)
    if Verbose_Flag:
        print("result of search for user: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        page_response=r.json()

        for u in page_response:
            u_name=u['sortable_name'].split(',')
            lastname=u_name[0].strip()
            firstname=u_name[1].strip()
            kthid=u['sis_user_id']
            return lastname, firstname, kthid

    return None, None, None

def users_in_course(course_id):
    global Verbose_Flag
    user_found_thus_far=[]
    # Use the Canvas API to get the list of users enrolled in this course
    #GET /api/v1/courses/:course_id/enrollments

    url = f"{baseUrl}/courses/{course_id}/enrollments"
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
        while r.links.get('next', False):
            r = requests.get(r.links['next']['url'], headers=header)  
            page_response = r.json()  
            for p_response in page_response:  
                user_found_thus_far.append(p_response)
    return user_found_thus_far

def user_profile_url(user_id):
    global Verbose_Flag
    # Use the Canvas API to get the profile of a user
    #GET /api/v1/users/:user_id/profile

    url = f"{baseUrl}/users/{user_id}/profile"
    if Verbose_Flag:
        print("user url: {}".format(url))

    r = requests.get(url, headers = header)
    if Verbose_Flag:
        print("result of getting profile: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        page_response=r.json()
        return page_response
    return None

def get_user_by_kthid(kthid):
    global Verbose_Flag
    # Use the KTH API to get the user information give an orcid
    #"#{$kth_api_host}/profile/v1/kthId/#{kthid}"

    if kth_host is None:
        return None
    
    url = f"{kth_host}/profile/v1/kthId/{kthid}"
    if Verbose_Flag:
        print("url: {}".format(url))

    r = requests.get(url, headers = kth_header)
    if Verbose_Flag:
        print("result of getting profile: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        page_response=r.json()
        return page_response
    return None


def get_user_name_and_kthid(email_address, users):
    global Verbose_Flag
    for u in users:
        login_id=u['user']['login_id']
        if login_id == email_address:
            u_name=u['user']['sortable_name'].split(',')
            lastname=u_name[0].strip()
            firstname=u_name[1].strip()
            kthid=u['user']['sis_user_id']
            return lastname, firstname, kthid
    return None, None, None

def get_user_info(email, users):
    global Verbose_Flag
    if users:
        lastname, firstname, kthid = get_user_name_and_kthid(email, users)
        if not kthid:
            print(f"Unable to determine KTHID for {email}")
            return None
    else:
        account_id=59
        lastname, firstname, kthid = user_via_search_in_account(email, account_id)
        if not kthid:
            print(f"Unable to determine KTHID for {email}")
            return None

    if Verbose_Flag:
        print(f"{lastname=}, {firstname=}, {kthid=}")

    user_info=get_user_by_kthid(kthid)
    if user_info and Verbose_Flag:
        pprint.pprint(user_info)
    return user_info

def get_school_acronym_and_department(user_info):
    school_acronym = None
    department = None

    for wi in user_info['worksFor'].get('items'):
        wi_key=wi['key']
        if wi_key.count('.') == 3:
            wi_name_swe=wi['name'].strip()
            wi_name_eng=wi['nameEn'].strip()
            wi_key_parts=wi_key.split('.')
            if wi_key_parts[2] == 'j' or wi_key_parts[2] == 'J':
                school_acronym='EECS'
            elif wi_key_parts[2] == 'a' or wi_key_parts[2] == 'A':
                school_acronym='ABE'
            elif wi_key_parts[2] == 'c' or wi_key_parts[2] == 'C':
                school_acronym='CBH'
            elif wi_key_parts[2] == 'm' or wi_key_parts[2] == 'M':
                school_acronym='ITM'
            elif wi_key_parts[2] == 's' or wi_key_parts[2] == 'S':
                school_acronym='SCI'
            else:
                print(f"Unknown organization path: {wi_key_parts[2]}")
                school_acronym='unknown'

    # set the name in title case
    if wi_name_eng:
        wi_name_eng=wi_name_eng.title()

        # clean up department names to just have the name
        if wi_name_eng.find('Department Of') == 0:
            department=wi_name_eng.replace('Department Of', '').strip()

    return school_acronym, department

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
                      help="For testing only get the list of users"
                      )

    options, remainder = parser.parse_args()

    Verbose_Flag=options.verbose
    if Verbose_Flag:
        print("ARGV      : {}".format(sys.argv[1:]))
        print("VERBOSE   : {}".format(options.verbose))
        print("REMAINING : {}".format(remainder))
        print("Configuration file : {}".format(options.config_filename))

    initialize(options)

    orcid = None

    if (len(remainder) < 1):
        print("Insuffient arguments - must provide file_name [course_id]\n")
    else:
        file_name=remainder[0]

    if (len(remainder) > 1):
        course_id=remainder[1]
    else:
        course_id=None

    isp_info=None

    users = None

    # if a course_id is specified get the information for all users
    if course_id:
        users=users_in_course(course_id)
        if not users:
            print(f"Could not find any users in course {course_id}")

        if (users):
            if Verbose_Flag:
                print(f"{users}")
        else:
            print("No user information in course")
            return

    try:
        with open(file_name) as file_ptr:
            isp_info = json.load(file_ptr)
            if not isp_info:
                print("Unable to get isP_info")
                sys.exit()
    except:
        print(f"Unable to open json file named {file_name}")
        sys.exit()

        
    if Verbose_Flag:
        print(f"{isp_info=}")
          
    # get author information
    email=isp_info['student_email']
    if not email:
        print(f"student_email address not found")
        return

    user_info=get_user_info(email, users)
    if not user_info:
        print(f"Cound not get user_info for {email}")
        return

    lastname=user_info['lastName']
    firstname=user_info['firstName']
    kthid=user_info['kthId']
    if user_info.get('researcher') and user_info['researcher'].get('orcid'):
        orcid = user_info['researcher'].get('orcid')
    
    school_acronym, department = get_school_acronym_and_department(user_info)
    if Verbose_Flag:
        print(f"{school_acronym=}, {department=}")

    print("% --- Author Information ---")
    print(f"\\authorsLastname"+"{"+f"{lastname}"+"}")
    print(f"\\authorsFirstname"+"{"+f"{firstname}"+"}")
    print(f"\\email"+"{"+f"{email}"+"}")
    print(f"\\kthid"+"{"+f"{kthid}"+"}")
    print(f"\\authorsSchool"+"{\\schoolAcronym{"+f"{school_acronym}"+"}}")
    if orcid:
        print(f"\\orcid"+"{"+f"{orcid}"+"}")
    print(f"\\authorsDepartment"+"{"+f"{department}"+"}")

    for supervisor_index in ['A', 'B', 'C', 'D', 'E']:
        # get supervisor information
        if supervisor_index == 'A':
            email=isp_info['main_supervisor']
            if not email:
                print(f"Supervisor{supervisor_index}'s email address not found")
                continue

        else:
            idx=f"supervisor{supervisor_index}_email"
            email=isp_info.get(idx)
            if not email:
                break

        user_info=get_user_info(email, users)
        if not user_info:
            print(f"Cound not get user_info for {email}")
            
            #print(f"\\supervisor{supervisor_index}sLastname"+"{"+f"{lastname}"+"}")
            #print(f"\\supervisor{supervisor_index}sFirstname"+"{"+f"{firstname}"+"}")
            #print(f"\\supervisor{supervisor_index}sEmail"+"{"+f"{email}"+"}")

            continue

        lastname=user_info['lastName']
        firstname=user_info['firstName']
        kthid=user_info['kthId']
        email=user_info['emailAddress']
        school_acronym, department = get_school_acronym_and_department(user_info)
            
        print(f"% -- supervisor{supervisor_index}")
        print(f"\\supervisor{supervisor_index}sLastname"+"{"+f"{lastname}"+"}")
        print(f"\\supervisor{supervisor_index}sFirstname"+"{"+f"{firstname}"+"}")
        print(f"\\supervisor{supervisor_index}sEmail"+"{"+f"{email}"+"}")
        if kthid:
            print(f"\\supervisor{supervisor_index}sKTHID"+"{"+f"{kthid}"+"}")
            print(f"\\supervisor{supervisor_index}sSchool"+"{\\schoolAcronym{"+f"{school_acronym}"+"}}")
            print(f"\\supervisor{supervisor_index}sDepartment"+"{"+f"{department}"+"}")
    



if __name__ == "__main__": main()






