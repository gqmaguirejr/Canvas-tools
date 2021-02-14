#!/usr/bin/python3
# -*- coding: utf-8 -*-
# -*- mode: python; python-indent-offset: 4 -*-
#
# ./insert_course_code_grading_standard.py course_id
#
# Generate a "grading standard" scale with the course codes as the "grades".
# Note that if the grading scale is already present, it does nothing unless the "-f" (force) flag is set.
# In the latter case it adds the grading scale.
#
# You can manually manage grading scales via the GUI: https://XXXX/courses/COURSE_ID/grading_standards
#
# Note that this only creates a COURSE LEVEL grading scale. 
# Also note that the name of the grading scale is 'Course_code'
#
# **** Note****
#  If you have assigned grades previously using another grading scale - adding a new one can render all previoous grades incorrect - as the process of assigning scores to teacher is not stable if there is a change in the number or list of course codes.
#
# G. Q. Maguire Jr.
#
# 2021.02.14
#
# Test with
#  ./insert_course_code_grading_standard.py -v 11 
#  ./insert_course_code_grading_standard.py -v --config config-test.json 11
#
# based on earlier program insert_teachers_grading_standards.py
#

import csv, requests, time
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


##############################################################################
## ONLY update the code below if you are experimenting with other API calls ##
##############################################################################


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


def get_course_info(course_id):
    global Verbose_Flag
    # Use the Canvas API to get a grading standard
    #GET /api/v1/courses/:id
    url = "{0}/courses/{1}".format(baseUrl, course_id)

    if Verbose_Flag:
        print("url: " + url)

    r = requests.get(url, headers = header)
    if r.status_code == requests.codes.ok:
        page_response=r.json()
        return page_response
    return None

def create_grading_standard(id, name, scale):
    global Verbose_Flag
    # Use the Canvas API to create an grading standard
    # POST /api/v1/courses/:course_id/grading_standards

    # Request Parameters:
    #Parameter		        Type	Description
    # title	Required	string	 The title for the Grading Standard.
    # grading_scheme_entry[][name]	Required	string	The name for an entry value within a GradingStandard that describes the range of the value e.g. A-
    # grading_scheme_entry[][value]	Required	integer	 -The value for the name of the entry within a GradingStandard. The entry represents the lower bound of the range for the entry. This range includes the value up to the next entry in the GradingStandard, or 100 if there is no upper bound. The lowest value will have a lower bound range of 0. e.g. 93

    url = "{0}/courses/{1}/grading_standards".format(baseUrl, id)

    if Verbose_Flag:
        print("url: {}".format(url))

    payload={'title': name,
             'grading_scheme_entry': scale
            }
    
    if Verbose_Flag:
        print("payload={0}".format(payload))

    r = requests.post(url, headers = header, json=payload)
    if r.status_code == requests.codes.ok:
        page_response=r.json()
        print("inserted grading standard")
        return True
    print("r.status_code={0}".format(r.status_code))
    print("r.reason={0}".format(r.reason))
    print("r.text={0}".format(r.text))
    return False

def get_grading_standards(id):
    global Verbose_Flag
    # Use the Canvas API to get a grading standard
    # GET /api/v1/courses/:course_id/grading_standards

    # Request Parameters:
    #Parameter		        Type	Description
    url = "{0}/courses/{1}/grading_standards".format(baseUrl, id)

    if Verbose_Flag:
        print("url: " + url)

    r = requests.get(url, headers = header)
    if r.status_code == requests.codes.ok:
        page_response=r.json()
        return page_response
    return None

def get_grading_standard_by_id(courss_id, grading_standard_id):
    all_course_grading_standards=get_grading_standards(courss_id)
    for i in all_course_grading_standards:
        if i['id'] == grading_standard_id:
            return i
    return None

def main():
    global Verbose_Flag
    global Use_local_time_for_output_flag
    global Force_appointment_flag

    Use_local_time_for_output_flag=True
    Other_value=0.01

    parser = optparse.OptionParser()

    parser.add_option('-v', '--verbose',
                      dest="verbose",
                      default=False,
                      action="store_true",
                      help="Print lots of output to stdout"
                    )


    parser.add_option('-f', '--force',
                      dest="force",
                      default=False,
                      action="store_true",
                      help="Replace existing grading scheme"
                      )

    parser.add_option('-t', '--testing',
                      dest="testing",
                      default=False,
                      action="store_true",
                      help="execute test code"
                      )

    parser.add_option("--config", dest="config_filename",
                      help="read configuration from FILE", metavar="FILE")



    options, remainder = parser.parse_args()

    Verbose_Flag=options.verbose
    Force_Flag=options.force

    if Verbose_Flag:
        print('ARGV      :', sys.argv[1:])
        print('VERBOSE   :', options.verbose)
        print('REMAINING :', remainder)
        print("Configuration file : {}".format(options.config_filename))

    if (len(remainder) < 1):
        print("Insuffient arguments - must provide course_id\n")
        return

    initialize(options)

    pp = pprint.PrettyPrinter(indent=4) # configure prettyprinter

    course_id=remainder[0]

    sections=sections_in_course(course_id)
    if Verbose_Flag:
        pp.pprint(sections)

    course_codes=set()
    for s in sections:
        sis_section_id=s['sis_section_id'] 
        if sis_section_id and sis_section_id[5] =='X':
            course_codes.add(sis_section_id[0:6])

    pp.pprint(course_codes)


    course_codes_sorted=list()
    if len(course_codes) > 0:
        course_codes_sorted=sorted(course_codes)
        print("course_codes_sorted={0}".format(course_codes_sorted))

    if len(course_codes_sorted)  < 1:
        print("No course codes, nothing to do")
        return

    canvas_grading_standards=dict()
    available_grading_standards=get_grading_standards(course_id)
    if available_grading_standards:
        for s in available_grading_standards:
            old_id=canvas_grading_standards.get(s['title'], None)
            if old_id and s['id'] < old_id: # use only the highest numbered instance of each scale
                continue
            else:
                canvas_grading_standards[s['title']]=s['id']
                if Verbose_Flag:
                    print("title={0} for id={1}".format(s['title'], s['id']))

    if Verbose_Flag:
        print("canvas_grading_standards={}".format(canvas_grading_standards))

    new_course_codes=list()
    
    name='Course_code'
    potential_grading_standard_id=canvas_grading_standards.get(name, None)

    if (not potential_grading_standard_id):
        scale=[]
        number_of_course_codes=len(course_codes_sorted)
        print("number_of_course_codes={}".format(number_of_course_codes))
        index=0
        for e in course_codes_sorted:
            i=number_of_course_codes-index
            d=dict()
            d['name']=e
            # save values above 80% for additions of additional course codes - so as not to disturbe existing lower assignments
            # note that this will require manually assigning the new course codes.
            new_value=((float(i)/float(number_of_course_codes))*80.0) + 2*(Other_value*100.0)
            if number_of_course_codes < 25:
                d['value'] = round(new_value, 0) #  round to integers - if there are few course codes
            else:
                d['value'] = round(new_value, 2) #  round to hundredths

            scale.append(d)
            index=index+1

        # testing shows that this was the smallest value other than zero that could be inserted as a value
        scale.append({'name': 'other - see comments', 'value': Other_value})

        scale.append({'name': 'none assigned', 'value': 0.0})
        if Verbose_Flag:
            print("scale={}".format(scale))

        status=create_grading_standard(course_id, name, scale)
        print("status={0}".format(status))
        if Verbose_Flag and status:
            print("Created new grading scale: {}".format(name))

    elif Force_Flag and potential_grading_standard_id: #  there is an existing grading standard and force is applied
        if potential_grading_standard_id:
            existing_grading_standard=get_grading_standard_by_id(course_id, potential_grading_standard_id)
            print("There exists a grading standard {0}, with the value={1}".format(potential_grading_standard_id, existing_grading_standard))

            course_codes_in_existing_grading_standard=list()
            highest_value_in_existing_grading_standard = -1.0
            existing_grading_scheme= existing_grading_standard['grading_scheme']
            for e in existing_grading_scheme:
                e_value=e['value']*100.0
                e['value']=round(e_value,2) # store back scaled value - round to hundreths
                if e_value > highest_value_in_existing_grading_standard:
                    highest_value_in_existing_grading_standard=e_value

                e_name=e['name']
                course_codes_in_existing_grading_standard.append(e_name)

            # figure out if there are new course codes to add
            for t in course_codes_sorted:
                if not t in course_codes_in_existing_grading_standard:
                    new_course_codes.append(t)

            scale=existing_grading_scheme # initialize with existing grading scheme
            number_in_existing_scale=len(scale)

            print("number_in_existing_scale={}".format(number_in_existing_scale))

            #new_course_codes.append('Test5')

            new_value=highest_value_in_existing_grading_standard
            print("inserting starting above value={0}".format(new_value))
            if (len(new_course_codes) > 0):
                print("Adding {0} new course codes to top of grading_standard".format(len(new_course_codes)))
                for nt in new_course_codes:
                    new_value=new_value+Other_value
                    scale.insert(0, {'name': nt, 'value': new_value})

                print("proposed scale {0} is={1}".format(name, scale))
                status=create_grading_standard(course_id, name, scale)
                print("status={0}".format(status))
                if Verbose_Flag and status:
                    print("Created new grading scale: {}".format(name))
            else:
                print("There were no new course codes to add, so no need to add a new grading scale")
    else:
        print("Could not figure out what you want to do")
        
if __name__ == "__main__": main()
