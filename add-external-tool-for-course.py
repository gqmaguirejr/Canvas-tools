#!/usr/bin/python3
#
# ./add-external-tool-for-course.py  course_id tool_id 'navigation_text'
# 
# outputs a list of external tools for the given course_id
#
# with the option '-C'or '--containers' use HTTP rather than HTTPS for access to Canvas
# with the option "-v" or "--verbose" you get lots of output - showing in detail the operations of the program
#
# Can also be called with an alternative configuration file:
# ./create_fake_users-in-course.py --config config-test.json
#
# Example:
# ./add-external-tool-for-course.py 4 2 'TestTool'
#
# ./add-external-tool-for-course.py --config config-test.json 4 2 'TestTool'
#
# ./add-external-tool-for-course.py -C 5 2 'TestTool'
#
# G. Q. Maguire Jr.
#
# 2019.02.15
#

import csv, requests, time
from pprint import pprint
import optparse
import sys

from lxml import html

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


def details_of_external_tools_for_course(course_id, external_tool_id):
    # Use the Canvas API to GET the tool's detailed information
    # GET /api/v1/courses/:course_id/external_tools/:external_tool_id
    # GET /api/v1/accounts/:account_id/external_tools/:external_tool_id

    url = "{0}/courses/{1}/external_tools/{2}".format(baseUrl, course_id, external_tool_id)
    if Verbose_Flag:
        print(url)
    payload={}
    r = requests.get(url, headers = header, data=payload)
    if r.status_code == requests.codes.ok:
        tool_response = r.json()  
        pprint(tool_response)
        return tool_response
    else:
        print("No details for tool_id {1} for course_id: {2}".format(external_tool_id, course_id))
        return False

def list_external_tools_for_course(course_id):
    list_of_all_tools=[]
    # Use the Canvas API to get the list of external tools for this course
    # GET /api/v1/courses/:course_id/external_tools
    # GET /api/v1/accounts/:account_id/external_tools
    # GET /api/v1/groups/:group_id/external_tools

    url = "{0}/courses/{1}/external_tools".format(baseUrl, course_id)
    if Verbose_Flag:
        print("url: " + url)

    r = requests.get(url, headers = header)
    if Verbose_Flag:
        print("result of getting list of external tools: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        tool_response=r.json()
    else:
        print("No external tools for course_id: {}".format(course_id))
        return False


    for t_response in tool_response:  
        list_of_all_tools.append(t_response)

        # the following is needed when the reponse has been paginated
        # i.e., when the response is split into pieces - each returning only some of the list of modules
        # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
        while r.links['current']['url'] != r.links['last']['url']:  
            r = requests.get(r.links['next']['url'], headers=header)  
            tool_response = r.json()  
            for t_response in tool_response:  
                list_of_all_tools.append(t_response)

def add_course_navigation_url(course_id, external_tool_id, navigation_text, navigation_icon_url):
    tool_response = []          # default value
    # course_home_sub_navigation[url]		string The url of the external tool for right-side course home navigation menu
    # course_home_sub_navigation[enabled]	boolean Set this to enable this feature
    # course_home_sub_navigation[text]		string	The text that will show on the right-side course home navigation menu
    # course_home_sub_navigation[icon_url]	string	The url of the icon to show in the right-side course home navigation menu
    # course_navigation[enabled]	boolean	Set this to enable this feature
    # course_navigation[text]		string	The text that will show on the left-tab in the course navigation
    # course_navigation[visibility]	string	Who will see the navigation tab. “admins” for course admins, “members” for students, null for everyone (Allowed values: admins, members)
    # course_navigation[windowTarget]	string	Determines how the navigation tab will be opened. “_blank” Launches the external tool in a new window or tab. “_self” (Default) Launches the external tool in an iframe inside of Canvas. (Allowed values: _blank, _self)
    # course_navigation[default]	boolean	Whether the navigation option will show in the course by default or whether the teacher will have to explicitly enable it
    # course_navigation[display_type] string The layout type to use when launching the tool. Must be “full_width”, “full_width_in_context”, “borderless”, or “default”

    url = "{0}/courses/{1}/external_tools/{2}".format(baseUrl, course_id, external_tool_id)
    if Verbose_Flag:
        print(url)
    payload={}
    # get the existing tool information
    r = requests.get(url, headers = header, data=payload)
    if Verbose_Flag:
        print("r.status_code={}".format(r.status_code))

    if r.status_code == requests.codes.ok:
        tool_response = r.json()  
        print("Existing tool information for tool_id={}".format(external_tool_id))
        pprint(tool_response)
    else:
        print("No details for tool_id {0} for course_id: {1}".format(external_tool_id, course_id))
        return False

    # set editor button url to be the same as that of the tool
    tool_url=tool_response["url"]
              
    # added the message type to make the button do a ContentItemSelectionRequest
    payload={#'course_home_sub_navigation[url]': tool_url,
             #'course_home_sub_navigation[enabled]': 'enabled',
             #'course_home_sub_navigation[icon_url]': navigation_icon_url,
             #'course_home_sub_navigation[]': navigation_text, 
        'course_navigation[url]': tool_url,
        'course_navigation[default]': 'enabled',
        'course_navigation[enabled]': 'true',
        'course_navigation[text]': navigation_text+'Left',
        'course_navigation[visibility]': 'admins',
        'course_navigation[windowTarget]': '_blank',
        'course_navigation[display_type]': 'full_width'
    }

    # set the tool information
    r = requests.put(url, headers = header, data=payload)
    if r.status_code == requests.codes.ok:
        tool_response = r.json()  
        pprint(tool_response)
        return tool_response
    else:
        print("Unable to add course navagation (status code={0}) for tool_id {1} for course_id: {2}".format(r.status_code, external_tool_id, course_id))
        return False

    payload={}
    # get the updated tool information
    r = requests.get(url, headers = header, data=payload)
    if r.status_code == requests.codes.ok:
        tool_response = r.json()  
        print("Existing tool information for tool_id {}".format(external_tool_id))
        pprint(tool_response)
    return tool_response

def add_user_navigation_url(account_id, external_tool_id, navigation_text):
    tool_response = []          # default value
    # user_navigation[url]	string	The url of the external tool for user navigation
    # user_navigation[enabled]	boolean	Set this to enable this feature
    # user_navigation[text]	string	The text that will show on the left-tab in the user navigation
    # user_navigation[visibility]	string	Who will see the navigation tab. “admins” for admins, “public” or “members” for everyone

    url = "{0}/account/{1}/external_tools/{2}".format(baseUrl, accound_id, external_tool_id)
    if Verbose_Flag:
        print(url)
    payload={}
    # get the existing tool information
    r = requests.get(url, headers = header, data=payload)
    if Verbose_Flag:
        print("r.status_code={}".format(r.status_code))

    if r.status_code == requests.codes.ok:
        tool_response = r.json()  
        print("Existing tool information for tool_id={}".format(external_tool_id))
        pprint(tool_response)
    else:
        print("No details for tool_id {0} for course_id: {1}".format(external_tool_id, course_id))
        return False

    # set editor button url to be the same as that of the tool
    tool_url=tool_response["url"]
              
    # added the message type to make the button do a ContentItemSelectionRequest
    payload={
        'user_navigation[url]': tool_url,
        'user_navigation[enabled]': 'true',
        'user_navigation[text]': navigation_text+'User',
        'user_navigation[visibility]': 'admins',
        'user_navigation[windowTarget]': '_blank',
        'user_navigation[display_type]': 'full_width'
    }

    # set the tool information
    r = requests.put(url, headers = header, data=payload)
    if r.status_code == requests.codes.ok:
        tool_response = r.json()  
        pprint(tool_response)
        return tool_response
    else:
        print("Unable to add course navagation (status code={0}) for tool_id {1} for course_id: {2}".format(r.status_code, external_tool_id, course_id))
        return False

    payload={}
    # get the updated tool information
    r = requests.get(url, headers = header, data=payload)
    if r.status_code == requests.codes.ok:
        tool_response = r.json()  
        print("Existing tool information for tool_id {}".format(external_tool_id))
        pprint(tool_response)
    return tool_response


def add_editor_icon_url(course_id, external_tool_id, icon_url):
    tool_response = []          # default value
    # editor_button[url]		string	The url of the external tool
    # editor_button[enabled]		boolean	 Set this to enable this feature
    # editor_button[icon_url]		string	The url of the icon to show in the WYSIWYG editor
    # editor_button[selection_width]		string	The width of the dialog the tool is launched in
    # editor_button[selection_height]		string	The height of the dialog the tool is launched in

    url = "{0}/courses/{1}/external_tools/{2}".format(baseUrl, course_id, external_tool_id)
    if Verbose_Flag:
        print(url)
    payload={}
    # get the existing tool information
    r = requests.get(url, headers = header, data=payload)
    if Verbose_Flag:
        print("r.status_code=%d".format(r.status_code))

    if r.status_code == requests.codes.ok:
        tool_response = r.json()  
        print("Existing tool information for tool_id %s".format(external_tool_id))
        pprint(tool_response)
    else:
        print("No details for tool_id %s for course_id: %s" % (external_tool_id, course_id))
        return False

    # set editor button url to be the same as that of the tool
    tool_url=tool_response["url"]
              
    # added the message type to make the button do a ContentItemSelectionRequest
    payload={'editor_button[url]': tool_url,
             'editor_button[enabled]': True,
             'editor_button[icon_url]': icon_url,
             'editor_button[selection_width]': 500,
             'editor_button[selection_height]': 500,
             'editor_button[message_type]': "basic-lti-launch-request"
             #'editor_button[message_type]': "ContentItemSelectionRequest"
    }

    # set the tool information
    r = requests.put(url, headers = header, data=payload)
    if r.status_code == requests.codes.ok:
        tool_response = r.json()  
        pprint(tool_response)
        return tool_response
    else:
        print("Unable to add icon_url to tool_id %s for course_id: %s" % (external_tool_id, course_id))
        return False

    payload={}
    # get the updated tool information
    r = requests.get(url, headers = header, data=payload)
    if r.status_code == requests.codes.ok:
        tool_response = r.json()  
        print("Existing tool information for tool_id %s" % (external_tool_id))
        pprint(tool_response)
    return tool_response

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

    parser.add_option('-u', '--user',
                      dest="user",
                      default=False,
                      action="store_true",
                      help="insert user_navigation"
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

    if (len(remainder) < 3):
        print("Insuffient arguments - must provide course_id external_tool_id navigation_text [navigation_icon_url]")
    else:
        course_id=remainder[0]
        external_tool_id=remainder[1]
        navigation_text=remainder[2]
        if (len(remainder) == 4):
            navigation_icon_url=remainder[3]
        else:
            navigation_icon_url=''
        
        output=add_course_navigation_url(course_id, external_tool_id, navigation_text, navigation_icon_url)
        if (output):
            pprint(output)

if __name__ == "__main__": main()

