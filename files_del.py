#!/usr/bin/python3
# -*- coding: utf-8 -*-
# -*- mode: python; python-indent-offset: 4 -*-
#
# ./files_del.py  canvas_course_page_url
# 
# delete all files from a Canvas course
#
#
# Example:
# ./files_del.py -v --config config-test.json -c 2139
#
#
# G. Q: Maguire Jr.
#
# 2021.09.07
#

import csv, requests, time
from pprint import pprint
import argparse
import sys

import json

global baseUrl	# the base URL used for access to Canvas
global header	# the header for all HTML requests
global payload	# place to store additionally payload when needed for options to HTML requests

# Based upon the options to the program, initialize the variables used to access Canvas gia HTML requests
def initialize(args):
    global baseUrl, header, payload

    # styled based upon https://martin-thoma.com/configuration-files-in-python/
    config_file=args["config"]

    try:
        with open(config_file) as json_data_file:
            configuration = json.load(json_data_file)
            access_token=configuration["canvas"]["access_token"]

            if args["containers"]:
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


def get_course_files(course_id):
    entries_found_thus_far=[]
    # Use the Canvas API to GET the all the pages
    #GET /api/v1/courses/:course_id/pages

    if Verbose_Flag:
        print("course_id: {}".format(course_id))

    url = "{0}/courses/{1}/files".format(baseUrl,course_id)
    if Verbose_Flag:
        print(url)

    extra_parameters={'per_page': '100'}
    r = requests.get(url, params=extra_parameters, headers = header)

    if r.status_code == requests.codes.ok:
        page_response=r.json()

        for p_response in page_response:  
            entries_found_thus_far.append(p_response)

        # the following is needed when the reponse has been paginated
        # i.e., when the response is split into pieces - each returning only some of the list of modules
        # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
        while r.links.get('next', False):
            r = requests.get(r.links['next']['url'], headers=header)  
            if Verbose_Flag:
                print("result of getting pages for a paginated response: {}".format(r.text))
            page_response = r.json()  
            for p_response in page_response:  
                entries_found_thus_far.append(p_response)

    return entries_found_thus_far

# canvas_course_page_url will be of the form: https://kth.instructure.com/courses/11/pages/notes-20160716
def del_course_file(file_id):
    # Use the Canvas API to get the list of pages for this course
    # DELETE /api/v1/courses/:course_id/pages/:url

    url = "{0}/files/{1}".format(baseUrl, file_id)
    if Verbose_Flag:
        print(url)
    payload={}
    r = requests.delete(url, headers = header, data=payload)
    if Verbose_Flag:
        print("r.status_code: {}".format(r.status_code))
    if r.status_code == requests.codes.ok:
        page_response = r.json()
        print("file with id={} deleted".format(file_id))
        return True
    else:
        print("error when deleteing file with id: {}".format(file_id))
        return False
    return False

def main(argv):
    global Verbose_Flag

    argp = argparse.ArgumentParser(description="II2202-grades_to_report.py: look for students who have passed the 4 assignments and need a grade assigned")
    argp.add_argument('-v', '--verbose', required=False,
                      default=False,
                      action="store_true",
                      help="Print lots of output to stdout")

    argp.add_argument("--config", type=str, default='config.json',
                      help="read configuration from file")

    argp.add_argument('-C', '--containers',
                      default=False,
                      action="store_true",
                      help="for the container enviroment in the virtual machine, uses http and not https")

    argp.add_argument("-c", "--canvas_course_id", type=int, required=True,
                      help="canvas course_id")

    args = vars(argp.parse_args(argv))
    Verbose_Flag=args["verbose"]

    if Verbose_Flag:
        print("args={}".format(args))

    initialize(args)

    course_id=args["canvas_course_id"]
    print("course_id={}".format(course_id))
    files=get_course_files(course_id)
    if Verbose_Flag:
        print("files={}".format(files))
    all_file_ids=[f['id'] for f in files]
    if Verbose_Flag:
        print("all_file_ids={}".format(all_file_ids))
    for f_id in all_file_ids:
        del_course_file(f_id)

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))




