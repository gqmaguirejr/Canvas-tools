#!/usr/bin/python3
# -*- coding: utf-8 -*-
# -*- mode: python; python-indent-offset: 4 -*-
#
# ./assign-random-peer-reviewer-by-section.py course_id new_assignment_id [old_assignment_id ]
#
# This program assigns each user in a course (course_id) with a randomly assigned peer reviewer from within their section for a given assignment (new_assignment).
# Note that this program ignores all sections that do not have a single quote or the word "section" in them.
#
# Note also that there are some permutations that cannot meet the above two conditions and the additional condition of not having a person assigned
# to review two different persons. In this case the program tries with a new starting permutation. It will try up to 99 times before giving
# up doing peer reviewing assignments for this section. I know this is an arbitrary number, but hope that it works in practice.
#
# Example:
#
# ./assign-random-peer-reviewer-by-section.py --testing 28715 159758
# ./assign-random-peer-reviewer-by-section.py 28850 160120
#
# G. Q. Maguire Jr.
#
# 2021.09.16 based on earlier copy-peer-reviewer-assignments.py program
#

import requests, time
from pprint import pprint
import optparse
import sys

import json
import random

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

##############################################################################
## ONLY update the code below if you are experimenting with other API calls ##
##############################################################################

def summarize_assignments(list_of_assignments):
    summary_of_assignments={}
    for assignm in list_of_assignments:
        summary_of_assignments[assignm['id']]=assignm['name']

    print("summary_of_assignments={}".format(summary_of_assignments))

def list_assignments(course_id):
    assignments_found_thus_far=[]

    # Use the Canvas API to get the list of assignments for the course
    #GET /api/v1/courses/:course_id/assignments

    url = "{0}/courses/{1}/assignments".format(baseUrl, course_id)
    if Verbose_Flag:
        print("url: {}".format(url))

    r = requests.get(url, headers = header)
    if Verbose_Flag:
        print("result of getting assignments: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        page_response=r.json()

        for p_response in page_response:  
            assignments_found_thus_far.append(p_response)

        # the following is needed when the reponse has been paginated
        # i.e., when the response is split into pieces - each returning only some of the list of modules
        # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
        while r.links.get('next', False):
            r = requests.get(r.links['next']['url'], headers=header)  
            page_response = r.json()  
            for p_response in page_response:  
                assignments_found_thus_far.append(p_response)

    return assignments_found_thus_far

def list_peer_reviews(course_id, assignment_id):
    reviews_found_thus_far=[]

    # Use the Canvas API to get the list of peer reviwes for the course
    # GET /api/v1/courses/:course_id/assignments/:assignment_id/peer_reviews

    url = "{0}/courses/{1}/assignments/{2}/peer_reviews".format(baseUrl, course_id, assignment_id)
    if Verbose_Flag:
        print("url: {}".format(url))

    r = requests.get(url, headers = header)
    if Verbose_Flag:
        print("result of getting peer reviews: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        page_response=r.json()

        for p_response in page_response:  
            reviews_found_thus_far.append(p_response)

        # the following is needed when the reponse has been paginated
        # i.e., when the response is split into pieces - each returning only some of the list of modules
        # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
        if 'link' in r.headers:
            while r.links.get('next', False):
                r = requests.get(r.links['next']['url'], headers=header)  
                page_response = r.json()  
                for p_response in page_response:  
                    reviews_found_thus_far.append(p_response)

    return reviews_found_thus_far



def submission_for_assignment_by_user(course_id, assignment_id, user_id):
    # return the submission information for a single user's assignment for a specific course as a dict
    #
    # Use the Canvas API to get a user's submission for a course for a specific assignment
    # GET /api/v1/courses/:course_id/assignments/:assignment_id/submissions/:user_id
    url = "{0}/courses/{1}/assignments/{2}/submissions/{3}".format(baseUrl, course_id, assignment_id, user_id)
    if Verbose_Flag:
        print("url: {}".format(url))

    #extra_parameters={'student_ids[]': 'all'}
    #r = requests.get(url, params=extra_parameters, headers = header)
    r = requests.get(url, headers = header)
    if Verbose_Flag:
        print("result of getting submissions: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        page_response=r.json()
        if Verbose_Flag:
            print("page_response: " + str(page_response))
        return page_response
    else:
        return dict()

def assign_peer_reviewer(course_id, assignment_id, user_id, submission_id):
    global Verbose_Flag

    # Use the Canvas API 
    #POST /api/v1/courses/:course_id/assignments/:assignment_id/submissions/:submission_id/peer_reviews
    # Request Parameters:
    #Parameter		Type	Description
    # user_id	Required	integer	 user_id to assign as reviewer on this assignment
    #
    # from https://github.com/matematikk-mooc/frontend/blob/master/src/js/api/api.js
    # createPeerReview: function(courseID, assignmentID, submissionID, userID, callback, error) {
    #       this._post({
    #              "callback": callback,
    #              "error":    error,
    #              "uri":      "/courses/" + courseID + "/assignments/" + assignmentID + "/submissions/" + submissionID + "/peer_reviews",
    #              "params":   { user_id: userID }
    #       });
    #    },
   
    url = "{0}/courses/{1}/assignments/{2}/submissions/{3}/peer_reviews".format(baseUrl, course_id, assignment_id, submission_id)
    if Verbose_Flag:
        print("url: {}".format(url))

    payload={'user_id': user_id}

    r = requests.post(url, headers = header, data=payload)
    if Verbose_Flag:
        print("result of post assigning peer reviwer: {}".format(r.text))
    if r.status_code == requests.codes.ok:
        print("result of post assigning peer reviwer: {}".format(r.text))
    if r.status_code == requests.codes.ok:
        page_response=r.json()
        print("assigned reviewer")
        return True
    return False

def assign_assessor_as_peer_reviewer(course_id, assignment_id, assessor_id, user_id):
    submission=submission_for_assignment_by_user(course_id, assignment_id, user_id)
    if Verbose_Flag:
        print("submission: {}".format(submission))

    if Verbose_Flag:
        print("user_id: {}".format(submission['user_id']))

    if submission['user_id'] == int(user_id):
        if Verbose_Flag:
            print("matching submission: {}".format(submission))
        output=assign_peer_reviewer(course_id, assignment_id, assessor_id, submission['id'])
        return output
    return "no match found"

def copy_assigned_peer_reviewers(course_id, old_assignment_id, new_assignment_id):
    # students=students_in_course(course_id)
    # for student in students:
    old_list=list_peer_reviews(course_id, old_assignment_id)
    if Verbose_Flag:
        print("old_list: {}".format(old_list))

    for previous_peer_assignment in old_list:
        assessor_id=previous_peer_assignment['assessor_id']
        user_id=previous_peer_assignment['user_id']
        if Verbose_Flag:
            print("assessor_id: {}".format(assessor_id))
            print("user_id: {}".format(user_id))

        assign_assessor_as_peer_reviewer(course_id, new_assignment_id, assessor_id, user_id)


        new_list=list_peer_reviews(course_id, new_assignment_id)
        if Verbose_Flag:
            print("new_list: " + str(new_list))

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
        while r.links.get('next', False):
            r = requests.get(r.links['next']['url'], headers=header)  
            page_response = r.json()  
            for p_response in page_response:  
                sections_found_thus_far.append(p_response)

    return sections_found_thus_far

def students_in_course(course_id):
    user_found_thus_far=[]
    # Use the Canvas API to get the list of users enrolled in this course
    #GET /api/v1/courses/:course_id/enrollments

    url = "{0}/courses/{1}/enrollments".format(baseUrl,course_id)
    if Verbose_Flag:
        print("url: {}".format(url))

    extra_parameters={'per_page': '100', 'type[]': ['StudentEnrollment']}
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


def list_groups_in_course(course_id):
    groups_found_thus_far=[]

    # Use the Canvas API to get the list of groups for the course
    # GET /api/v1/courses/:course_id/groups

    url = "{0}/courses/{1}/groups".format(baseUrl, course_id)
    if Verbose_Flag:
        print("url: {}".format(url))

    r = requests.get(url, headers = header)
    if Verbose_Flag:
        print("result of getting groups: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        page_response=r.json()

        for p_response in page_response:  
            groups_found_thus_far.append(p_response)

        # the following is needed when the reponse has been paginated
        # i.e., when the response is split into pieces - each returning only some of the list of modules
        # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
        if 'link' in r.headers:
            while r.links.get('next', False):
                r = requests.get(r.links['next']['url'], headers=header)  
                page_response = r.json()  
                for p_response in page_response:  
                    groups_found_thus_far.append(p_response)

    return groups_found_thus_far

def members_of_groups(group_id):
    members_found_thus_far=[]

    # Use the Canvas API to get the list of members of group
    # GET /api/v1/groups/:group_id/users


    url = "{0}/groups/{1}/users".format(baseUrl, group_id)
    if Verbose_Flag:
        print("url: {}".format(url))

    r = requests.get(url, headers = header)
    if Verbose_Flag:
        print("result of getting memebrs of group: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        page_response=r.json()

        for p_response in page_response:  
            members_found_thus_far.append(p_response)

        # the following is needed when the reponse has been paginated
        # i.e., when the response is split into pieces - each returning only some of the list of modules
        # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
        if 'link' in r.headers:
            while r.links.get('next', False):
                r = requests.get(r.links['next']['url'], headers=header)  
                page_response = r.json()  
                for p_response in page_response:  
                    members_found_thus_far.append(p_response)

    return members_found_thus_far


# remove sections that do not have a quote or the word "section" in them
def clean_up_sections(sections):
    clean_sections=[]
    for i in sections:
        if (i['name'].find("'") >= 0) or (i['name'].find("section") >= 0):
            clean_sections.append(i)
    return clean_sections

def relevant_section_ids(sections):
    section_ids=[]
    for i in sections:
        section_ids.append(i['id'])
    return section_ids

def same_group(s, possible_reviwer, course_groups):
    for g in course_groups:
        if (s in course_groups[g]['member_ids']) and (possible_reviwer in course_groups[g]['member_ids']):
            return True
    return False

def student_name_from_id(id, students_info):
    for s in students_info:
        if s['user']['id'] == id:
            return s['user']['name']
    return ''

def try_to_assignments(student_ids_for_section, course_groups):
    global Verbose_Flag
    assignments={}              # will be of the form  assigned_reviwer student_reviewed
    reviewers=random.sample(student_ids_for_section, k=len(student_ids_for_section))
    print("reviewers={}".format(reviewers))
    for s in student_ids_for_section:
        reviewers=random.sample(student_ids_for_section, k=len(student_ids_for_section))
        if Verbose_Flag:
            print("s={}".format(s))
        if len(reviewers) >= 1:
            possible_reviwer=reviewers.pop()
        else:
            print("empty list of reviewers, s={}".format(s))
            return False

        while (s==possible_reviwer) or same_group(s, possible_reviwer, course_groups) or assignments.get(possible_reviwer, False):
            random.shuffle(reviewers)
            if Verbose_Flag:
                print("reviewers={}".format(reviewers))
            if len(reviewers) >= 1:
                possible_reviwer=reviewers.pop()
            else:
                print("empty list of reviewers #2, s={}".format(s))
                return False
            if Verbose_Flag:
                print("s={0}, possible_reviwer={1}".format(s, possible_reviwer))

        assignments[possible_reviwer]=s
        if Verbose_Flag:
            print("assigned s={0}, possible_reviwer={1}".format(s, possible_reviwer))

    return assignments


def main():
    global Verbose_Flag

    parser = optparse.OptionParser()

    parser.add_option('-v', '--verbose',
                      dest="verbose",
                      default=False,
                      action="store_true",
                      help="Print lots of output to stdout"
                      )

    parser.add_option("--config", dest="config_filename",
                      help="read configuration from FILE", metavar="FILE")

    parser.add_option('-C', '--containers',
                      dest="containers",
                      default=False,
                      action="store_true",
                      help="for the container enviroment in the virtual machine"
                      )

    parser.add_option('-t', '--testing',
                      dest="testing",
                      default=False,
                      action="store_true",
                      help="execute test code"
                      )


    options, remainder = parser.parse_args()

    Verbose_Flag=options.verbose
    if Verbose_Flag:
        print('ARGV      :', sys.argv[1:])
        print('VERBOSE   :', options.verbose)
        print('REMAINING :', remainder)

    initialize(options)

    if (len(remainder) < 2):
        print("Insuffient arguments\n must provide course_id new_assignment_id [old_assignment_id ]")

    if (len(remainder) > 0):
        course_id=remainder[0]
    if (len(remainder) > 1):
        new_assignment_id=remainder[1]
    if (len(remainder) > 3):
        old_assignment_id=remainder[2]

    sections=sections_in_course(course_id)
    sections=clean_up_sections(sections)
    print("sections={}".format(sections))
    s_ids=relevant_section_ids(sections)
    print("s_ids={}".format(s_ids))

    students=students_in_course(course_id)

    students_by_section={}
    for s in students:
        s_id=s['course_section_id']
        if s_id in s_ids:
            current_section_membership=students_by_section.get(s_id, [])
            current_section_membership.append(s)
            students_by_section[s_id]=current_section_membership

    if options.testing and course_id == 28715:
        emils_section=39696
        chips_section=39698
        e_names=[s['user']['name'] for s in students_by_section[emils_section]]
        e_ids=[s['user']['id'] for s in students_by_section[emils_section]]
        print("Emil's section={}".format(e_names))
        print("Emil's section ids={}".format(e_ids))

    groups=list_groups_in_course(course_id)
    print("number of groups={}".format(len(groups)))

    course_groups={}
    for g in groups:
        g_id=g['id']
        g_name=g['name']
        if g['members_count'] > 0:
            members=members_of_groups(g_id)
            member_ids=[x['id'] for x in members]
            course_groups[g_id]={'name': g_name,
                                 'members_count': g['members_count'],
                                 'member_ids': member_ids,
                                 'members': members}

    #print("course_groups={}".format(course_groups))

    student_ids_by_section={}
    assignments={}              # will be of the form  assigned_reviwer student_reviewed
    for section in sections:
        print("working on {}".format(section['name']))

        if section['name'].find('Magnus Boman') >= 0: #  skip Magnus' section
            print("Skipping Magnus Boman's section")
            continue

        if options.testing and course_id == 28715 and section['id'] not in [emils_section, chips_section]:
            continue

        student_ids_for_section=[s['user']['id'] for s in students_by_section[section['id']]]
        assignments_for_section=False
        maximum_permutations_to_try=100
        while (not assignments_for_section):
            maximum_permutations_to_try=maximum_permutations_to_try-1
            if maximum_permutations_to_try == 0:
                print("failed to find a working permutation to asssign reviewers for {}".format(section['name']))
                assignments_for_section=False
                break
            random.shuffle(student_ids_for_section) # shuffle the student's IDs
            assignments_for_section=try_to_assignments(student_ids_for_section, course_groups)
            if not assignments_for_section:
                print("trying again".format(assignments_for_section))

        if assignments_for_section:
            print("assignments_for_section={}".format(assignments_for_section))
            if len(assignments_for_section) != len(student_ids_for_section):
                print("len(assignments_for_section) {0} not equal to len(student_ids_for_section) {1} ".format(len(assignments_for_section), len(student_ids_for_section)))
            for a in assignments_for_section: # copy into the set of assignemnts of reviewers for the course
                assignments[a]=assignments_for_section[a]

    print("assignments={}".format(assignments))
    if options.testing:
        return

    for a in assignments:
        reviewer=a
        reviewee=assignments[reviewer]
        print("{0} is assigned to review: {1}".format(student_name_from_id(reviewer, students), student_name_from_id(reviewee, students)))
        if not options.testing:
            assign_assessor_as_peer_reviewer(course_id, new_assignment_id, reviewer, reviewee)


    return

if __name__ == "__main__": main()
