#!/usr/bin/python3
#
# ./cgetall.py  canvas_course_page_url|course_id [destination_directory]
# 
# get all of the Canvas course pages with a given base URL or for a given course_id
#
# with the option '-C'or '--containers' use HTTP rather than HTTPS for access to Canvas
# with the option "-v" or "--verbose" you get lots of output - showing in detail the operations of the program
#
# Can also be called with an alternative configuration file:
# ./cgetall.py --config config-test.json  11
#
# Example:
#   cgetall.py https://kth.instructure.com/courses/11/pages/test-3
# or
#   cgetall.py 11
#
#  both get all of the course pages for course 11
#
# G. Q. Maguire Jr.
#
# 2020.03.27
# based on the earlier cgetall.py of 2016.07.25
#

import csv, requests, time
from pprint import pprint
import optparse
import sys

import json
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
log_file = 'log.txt' # a log file. it will log things

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
                encoded_output = bytes(page_response["body"], 'UTF-8')

                f.write(encoded_output)
                continue
        else:
            print("No such page: {}".format(canvas_course_page_url))
            continue
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

    if (len(remainder) < 1):
        print("Inusffient arguments\n must provide url or course_id\n")
    else:
        canvas_course_page_url=remainder[0]

    if (len(remainder) >= 1):
        destination_directory=remainder[1]
        print("outputing files to {}".format(destination_directory))
    else:
        destination_directory=""

    if canvas_course_page_url.find("http") >= 0:
        #extract course_id from URL
        course_id=canvas_course_page_url[canvas_course_page_url.find("courses/")+8:canvas_course_page_url.find("pages/")-1]
    else:
        course_id=remainder[0]
              
    if Verbose_Flag:
        print("course_id: {}".format(course_id))

    output=getall_course_pages(course_id, destination_directory)
    if (output):
        if Verbose_Flag:
            pprint(output)

if __name__ == "__main__": main()
