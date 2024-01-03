#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -*- mode: python; python-indent-offset: 4 -*-

# ./getall-files.py  course_id destination_directory
# 
# get all of the files of a Canvas for a given course_id
#
# with the option '-C'or '--containers' use HTTP rather than HTTPS for access to Canvas
# with the option "-v" or "--verbose" you get lots of output - showing in detail the operations of the program
#
# Can also be called with an alternative configuration file:
# ./getall-files.py --config config-test.json  11  Course_11
#
# Example:
#   getall-files.py 11  Course_11
#
# Note:
# Does not do anything to handle files with different file IDs that have the same name, the last one to be copied will overwrite an earlier copy.
#
# G. Q. Maguire Jr.
#
# 2024.01.03
# based on cgetall.py
#

import csv, requests, time
from pprint import pprint
import optparse
import sys

import json

import pathlib

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


#modules_csv = 'modules.csv' # name of file storing module names

def list_files(course_id):
    files_found_thus_far=[]
    # Use the Canvas API to get the list of files for the course
    #GET /api/v1/courses/:course_id/files

    url = "{0}/courses/{1}/files".format(baseUrl, course_id)
    if Verbose_Flag:
        print("url: {}".format(url))

    r = requests.get(url, headers = header)
    if Verbose_Flag:
        print("result of getting files: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        page_response=r.json()

        for p_response in page_response:  
            files_found_thus_far.append(p_response)

            # the following is needed when the reponse has been paginated
            # i.e., when the response is split into pieces - each returning only some of the list of files
            # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
            while r.links['current']['url'] != r.links['last']['url']:  
                r = requests.get(r.links['next']['url'], headers=header)  
                if Verbose_Flag:
                    print("result of getting files for a paginated response: {}".format(r.text))
                page_response = r.json()  
                for p_response in page_response:  
                    files_found_thus_far.append(p_response)

    return files_found_thus_far


def list_folders(course_id):
    folders_found_thus_far=[]
    # Use the Canvas API to get the list of folders for the course
    #GET /api/v1/courses/:course_id/folders

    url = "{0}/courses/{1}/folders".format(baseUrl, course_id)
    if Verbose_Flag:
        print("url: {}".format(url))

    r = requests.get(url, headers = header)
    if Verbose_Flag:
        print("result of getting folders: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        page_response=r.json()

        for p_response in page_response:  
            folders_found_thus_far.append(p_response)

            # the following is needed when the reponse has been paginated
            # i.e., when the response is split into pieces - each returning only some of the list of folders
            # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
            while r.links['current']['url'] != r.links['last']['url']:  
                r = requests.get(r.links['next']['url'], headers=header)  
                if Verbose_Flag:
                    print("result of getting folders for a paginated response: {}".format(r.text))
                page_response = r.json()  
                for p_response in page_response:  
                    folders_found_thus_far.append(p_response)

    return folders_found_thus_far


def list_pages(course_id):
    list_of_all_pages=[]

    # Use the Canvas API to get the list of pages for this course
    #GET /api/v1/courses/:course_id/pages

    url = "{0}/courses/{1}/pages".format(baseUrl, course_id)
    if Verbose_Flag:
        print("url: {}".format(url))

    r = requests.get(url, headers = header)
    if r.status_code == requests.codes.ok:
        page_response=r.json()

        for p_response in page_response:  
            list_of_all_pages.append(p_response)

            # the following is needed when the reponse has been paginated
            # i.e., when the response is split into pieces - each returning only some of the list of modules
            # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
            while r.links['current']['url'] != r.links['last']['url']:  
                r = requests.get(r.links['next']['url'], headers=header)  
                page_response = r.json()  
                for p_response in page_response:  
                    list_of_all_pages.append(p_response)

            if Verbose_Flag:
                for p in list_of_all_pages:
                    print("{}".format(p["title"]))

    return list_of_all_pages

def getall_course_pages(course_id, destination_directory):
    for p in list_pages(course_id):
        url = "{0}/courses/{1}/pages/{2}".format(baseUrl, course_id, p["url"])
        if Verbose_Flag:
            print(url)
        payload={}
        r = requests.get(url, headers = header, data=payload)
        if Verbose_Flag:
            print("r.status_code: {}".format(r.status_code))
        if r.status_code == requests.codes.ok:
            page_response = r.json()

            new_file_name=p["url"][p["url"].rfind("/")+1:]+'.html'
            if len(destination_directory) > 0:
                new_file_name=destination_directory+'/'+new_file_name
            if Verbose_Flag:
                print("new_file_name: {}".format(new_file_name))

            # write out body of response as a .html page
            with open(new_file_name, 'wb') as f:
                # modified the code to handle empty files
                if page_response["body"] is None:
                    continue
                if len(page_response["body"]) > 0:
                    encoded_output = bytes(page_response["body"], 'UTF-8')
                else:
                    encoded_output = bytes("", 'UTF-8')

                f.write(encoded_output)

                continue
        else:
            print("No such page: {}".format(canvas_course_page_url))
            continue
    return True
   
def getfile_to_dest(url, destination_directory, filename):
    payload={}
    r = requests.get(url, headers = header, data=payload)
    if Verbose_Flag:
        print("r.status_code: {}".format(r.status_code))
    if r.status_code == requests.codes.ok:
        page_response = r.content
    else:
        return False

    new_file_name=f'{destination_directory}/{filename}'
    if Verbose_Flag:
        print("new_file_name: {}".format(new_file_name))

    # write out the response as a file
    with open(new_file_name, 'wb') as f:
        # # modified the code to handle empty files
        # if len(page_response) > 0:
        #     encoded_output = bytes(page_response, 'UTF-8')
        # else:
        #     encoded_output = bytes("", 'UTF-8')

        # f.write(encoded_output)
        f.write(page_response)

    return True
   

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
        print("ARGV      :{}".format(sys.argv[1:]))
        print("VERBOSE   :{}".format(options.verbose))
        print("REMAINING :{}".format(remainder))

    initialize(options)

    print("remainder is {}".format(remainder))
    if (len(remainder) < 2):
        print("Inusffient arguments\n must course_id and destiation_directory\n")
        return
    course_id=remainder[0]
    if Verbose_Flag:
        print("course_id is {}".format(course_id))
    destination_directory=remainder[1]
    if destination_directory.endswith('/'):
        destination_directory=destination_directory[:-1]
    print("outputing files to {}".format(destination_directory))

    # list of folder_id that we will care about
    relevant_folders=[]
    # get the list of folders
    folders=list_folders(course_id)

    folder_id_to_name_mapping=dict()

    for f in folders:
        # skip hidden folders
        if f['hidden']:
            continue
        dir_to_make=destination_directory+'/'+f['full_name']
        if Verbose_Flag:
            print("dir_to_make={}".format(dir_to_make))
        pathlib.Path(dir_to_make).mkdir(parents=True, exist_ok=True) 
        relevant_folders.append(f['id'])
        folder_id_to_name_mapping[f['id']]=dir_to_make

    print("relevant_folders={}".format(relevant_folders))
    print(f'{folder_id_to_name_mapping=}')

    files=list_files(course_id)
    for f in files:
        if not f['hidden'] and f['folder_id'] in relevant_folders:
            print(f"should copy file {f['filename']} of size {f['size']} from {f['url']}")
            getfile_to_dest(f['url'], folder_id_to_name_mapping[ f['folder_id']], f['filename'])

if __name__ == "__main__": main()
