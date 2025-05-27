#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -*- mode: python; python-indent-offset: 4 -*-
#
# ./whoami_for_latex.py email course_id [supervisor_index]
#
# The course_id has to be a course where the supervisor is enrolled (as student, teacher, ... )
#
# If supervisor_index not specified, it defaults to "A"
#
# Output: supervisor information for LaTeX thesis temlate
#
# with the option "-v" or "--verbose" you get lots of output - showing in detail the operations of the program
#
# Can also be called with an alternative configuration file:
# ./users-in-course.py --config config-test.json 11
#
# Example:
# ./whoami_for_latex.py maguire@kth.se 11
#
# ./whoami_for_latex.py --config config-test.json  maguire@kth.se 6434
#
# for the 2nd supervisor
# ./whoami_for_latex.py maguire@kth.se 11 B
#
# G. Q. Maguire Jr.
#
# 2025-05-26
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
            kth_key=configuration["KTH_API"]["key"]
            kth_host=configuration["KTH_API"]["host"]
            kth_header = {'api_key': kth_key, 'Content-Type': 'application/json', 'Accept': 'application/json' }

    except:
        print(f"Unable to open configuration file named {config_file}")
        print("Please create a suitable configuration file, the default name is config.json")
        sys.exit()

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
    return []

def get_user_by_kthid(kthid):
    global Verbose_Flag
    # Use the KTH API to get the user information give an orcid
    #"#{$kth_api_host}/profile/v1/kthId/#{kthid}"

    url = f"{kth_host}/profile/v1/kthId/{kthid}"
    if Verbose_Flag:
        print("url: {}".format(url))

    r = requests.get(url, headers = kth_header)
    if Verbose_Flag:
        print("result of getting profile: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        page_response=r.json()
        return page_response
    return []




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

    if (len(remainder) < 2):
        print("Insuffient arguments - must provide email_address course_id\n")
    else:
        email_address=remainder[0]
        course_id=remainder[1]
        if (len(remainder) >= 3):
            supervisor_index=remainder[2]
        else:
            supervisor_index='A'

        users=users_in_course(course_id)
        if options.testing:     # if testing only get the list of users and then return
            return
        
        if not users:
            print(f"Could not find any users in course {course_id}")

        if (users):
            if Verbose_Flag:
                print(f"{users}")


            for u in users:
                login_id=u['user']['login_id']
                if login_id == email_address:
                    u_name=u['user']['sortable_name'].split(',')
                    lastname=u_name[0].strip()
                    firstname=u_name[1].strip()
                    kthid=u['user']['sis_user_id']
                    kth_user_info=get_user_by_kthid(kthid)
                    if Verbose_Flag:
                        pprint.pprint(kth_user_info)
                    if kth_user_info:
                        for wi in kth_user_info['worksFor'].get('items'):
                            wi_key=wi['key']
                            if wi_key.count('.') == 3:
                                wi_name_swe=wi['name'].strip()
                                wi_name_eng=wi['nameEn'].strip()
                                org_path=wi['path']
                                if org_path[0] == 'a':
                                    school_acronym='ABE'
                                elif org_path[0] == 'c':
                                    school_acronym='CBH'
                                elif org_path[0] == 'j':
                                    school_acronym='EECS'
                                elif org_path[0] == 'm':
                                    school_acronym='ITM'
                                elif org_path[0] == 's':
                                    school_acronym='SCI'
                                else:
                                    print(f"Unknown organization path: {org_path}")
                                    school_acronym='unknown'

                        # set the name in title case
                        wi_name_eng=wi_name_eng.title()

                        # clean up department names to just have the name
                        if wi_name_eng.find('Department Of') == 0:
                            wi_name_eng=wi_name_eng.replace('Department Of', '').strip()

                        if supervisor_index == 'A':
                            print(f"%If not the first supervisor,")
                            print(f"% then replace supervisorAs with supervisorBs or")
                            print(f"% supervisorCAs as appropriate")
                        print(f"\\supervisor{supervisor_index}sLastname"+"{"+f"{lastname}"+"}")
                        print(f"\\supervisor{supervisor_index}sFirstname"+"{"+f"{firstname}"+"}")
                        print(f"\\supervisor{supervisor_index}sEmail"+"{"+f"{email_address}"+"}")
                        print(f"% If the supervisor is from within KTH")
                        print(f"% add their KTHID, School and Department info")
                        print(f"\\supervisor{supervisor_index}sKTHID"+"{"+f"{kthid}"+"}")
                        print(f"%\\supervisor{supervisor_index}sSchool"+"{\\schoolAcronym{"+f"{school_acronym}"+"}")
                        print(f"%\\supervisor{supervisor_index}sDepartment"+"{"+f"{wi_name_eng}"+"}")
                        return
                    else:
                        print(f"%If not the first supervisor,")
                        print(f"% then replace supervisorAs with supervisorBs or")
                        print(f"% supervisorCAs as appropriate")
                        print("\\supervisorAsLastname{"+f"{lastname}"+"}")
                        print("\\supervisorAsFirstname{"+f"{firstname}"+"}")
                        print("\\supervisorAsEmail{"+f"{email_address}"+"}")
                        return
            else:
                print(f"Could not find user with e-mail address {email_address} in course {course_id}")

if __name__ == "__main__": main()

