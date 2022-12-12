#!/usr/bin/python3
# -*- coding: utf-8 -*-
# -*- mode: python; python-indent-offset: 4 -*-
#
# ./users-in-course.py course_id
#
# Output: XLSX spreadsheet with textual section names and URL to user's avatar
#
# --avatar flag include the avatar URLs
# -p or --picture flag include pictures
# -s or --size specification size the pictures (and enable pictures if not separately specified)
#
# with the option "-v" or "--verbose" you get lots of output - showing in detail the operations of the program
#
# Can also be called with an alternative configuration file:
# ./users-in-course.py --config config-test.json 11
#
# Example:
# ./users-in-course.py 11
#
# ./users-in-course.py --config config-test.json 6434
#
# ./users-in-course.py --config config-test.json --avatar 6434
# 
# documentation about using xlsxwriter to insert images can be found at:
#   John McNamara, "Example: Inserting images into a worksheet", web page, 10 November 2018, https://xlsxwriter.readthedocs.io/example_images.html
#
# G. Q. Maguire Jr.
#
# based on earlier users-in-course.py (that generated CSV files) and
#                  users-in-course-improved2.py (that included the images)
#
# 2019.01.04
#

import requests, time
import pprint
import optparse
import sys
import json

# Use Python Pandas to create XLSX files
import pandas as pd

# for dealing with the image bytes
from io import StringIO, BytesIO

# Import urlopen() for either Python 2 or 3.
try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen

from PIL import Image

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
        while r.links.get('next', False):
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

        while r.links.get('next', False):
            r = requests.get(r.links['next']['url'], headers=header)  
            if Verbose_Flag:
                print("result of getting courses for a paginated response: {}".format(r.text))
            page_response = r.json()  
            for p_response in page_response:  
                courses_found_thus_far.append(p_response)

    return courses_found_thus_far

# based upon answer by RoMA on Oct 8 '08 at 10:09 in http://stackoverflow.com/questions/181596/how-to-convert-a-column-number-eg-127-into-an-excel-column-eg-aa
def ColIdxToXlName(idx):
    if idx < 1:
        raise ValueError("Index is too small")
    result = ""
    while True:
        if idx > 26:
            idx, r = divmod(idx - 1, 26)
            result = chr(r + ord('A')) + result
        else:
            return chr(idx + ord('A') - 1) + result


# from KobeJohn on Nov 12 '15 at 15:36 at http://stackoverflow.com/questions/33672833/set-width-and-height-of-an-image-when-inserting-via-worksheet-insert-image

def calculate_scale(im_size, bound_size):
    original_width, original_height = im_size

    # calculate the resize factor, keeping original aspect and staying within boundary
    bound_width, bound_height = bound_size
    ratios = (float(bound_width) / original_width, float(bound_height) / original_height)
    return min(ratios)

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

    parser.add_option('-a', '--avatar',
                      dest="avatar",
                      default=False,
                      action="store_true",
                      help="include URL to avatar for each user"
                      )

    parser.add_option('-p', '--pictures',
                      dest="pictures",
                      default=False,
                      action="store_true",
                      help="Include pictures from user's avatars"
                      )

    parser.add_option("-s", "--size",
                      action="store",
                      dest="picture_size",
                      default=default_picture_size,
                      help="size of picture in pixels")

    parser.add_option('-t', '--testing',
                      dest="testing",
                      default=False,
                      action="store_true",
                      help="For testing only get the list of users"
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

    Picture_Flag=options.pictures
    Picture_size=int(options.picture_size)
    # if a size is specified, but the picture option is not set, then set it automatically
    if Picture_Flag and Picture_size > 1:
        Picture_Flag=True
    else:
        Picture_Flag=False

    if Picture_Flag:         # you need to have the avatar URLs in order to make pictures, so enable them
        options.avatar=True

    initialize(options)

    if (len(remainder) < 1):
        print("Insuffient arguments - must provide course_id\n")
    else:
        course_id=remainder[0]
        users=users_in_course(course_id)
        if options.testing:     # if testing only get the list of users and then return
            return
        
        if (users):
            users_df=pd.json_normalize(users)
                     
            # below are examples of some columns that might be dropped
            columns_to_drop=['user.id', 'user.integration_id', 'section_integration_id', 'course_integration_id', 'associated_user_id']
            users_df.drop(columns_to_drop,inplace=True,axis=1)

            # the following was inspired by the section "Using XlsxWriter with Pandas" on http://xlsxwriter.readthedocs.io/working_with_pandas.html
            # set up the output write
            writer = pd.ExcelWriter('users-'+course_id+'.xlsx', engine='xlsxwriter')
            #users_df.to_excel(writer, sheet_name='Users')

            # Get the xlsxwriter workbook and worksheet objects.
    
            sections=sections_in_course(course_id)
            sections_df=pd.json_normalize(sections)
            
            if options.avatar:
                users_avatars=dict() # to remember a user's avatar to avoid looking it up again

            for index, row in  users_df.iterrows():
                if Verbose_Flag:
                    print("index: {0}, row[user_id]: {1}".format(index, row['user_id']))

                user_id=row['user_id']
                if Verbose_Flag:
                    print("user_id: {}".format(user_id))

                section_name=section_name_from_section_id(sections, row['course_section_id'])
                users_df.at[index, 'Section_name']= section_name

                if options.avatar:
                    user_avatar=users_avatars.get(user_id, []) # have we already looked one up
                    if not user_avatar:
                        profiles=user_profile_url(user_id)
                        if Verbose_Flag:
                            print("profiles: {}".format(profiles['avatar_url']))
                        user_avatar=profiles['avatar_url']
                        users_avatars[user_id]=user_avatar
                        users_df.at[index, 'avatar_url']=user_avatar

                if Picture_Flag: # if necessary add a picture column
                    users_df['pictures']=''
                    headers = users_df.columns.tolist()
                    if Verbose_Flag:
                        print("users_df columns: {}".format(headers))
                    column_for_pictures_of_users=ColIdxToXlName(len(headers) + 1)

            users_df.to_excel(writer, sheet_name='Users')

            # for adding pictures
            workbook = writer.book
            worksheet = writer.sheets['Users']
                                          
            if Picture_Flag: # add pictures
                # Widen the picture column to hold the images
                worksheet.set_column(column_for_pictures_of_users+':'+column_for_pictures_of_users, 25)


                # set the row slightly larger than the pictures
                maxsize = (Picture_size, Picture_size)
                worksheet.set_default_row(Picture_size+2)
                # set the heading row to be only 25 units high
                worksheet.set_row(0, 20)

                for index, row in  users_df.iterrows():
                    avatar_url=row['avatar_url']
                    if Verbose_Flag:
                        print("index: {0}, avatar_url: {1}".format(index, avatar_url))

                    if isinstance(avatar_url, str) and len(avatar_url) > 0:
                        http_reponse=urlopen(avatar_url)
                        if Verbose_Flag:
                            print("http_reponse: {0}".format(http_reponse.info()))
                        im = Image.open(http_reponse)
                        image_width, image_height = im.size
                        if (image_width <= 1) or (image_height <= 1): # if either dimension is <1, this is a degenerate image
                            print("degenerate image encountered (for user_id={0}) that is one pixel of less in height or width, URL={1}".format(row['user_id'],avatar_url))
                            continue
                        if Verbose_Flag:
                            print("im: {0}".format(im.size))
                        resize_scale=calculate_scale(im.size, maxsize)
                        if Verbose_Flag:
                            print("resize_scale: {0}".format(resize_scale))

                        image_data = BytesIO(urlopen(avatar_url).read())
                        if Verbose_Flag:
                            print("image_data: {}".format(image_data))
                        # im.thumbnail(maxsize, Image.ANTIALIAS)
                        # need to increase the index because the first user is in the row indexed by 0, but this has to be in the second row of the Excel spreadhsheet
                        if Verbose_Flag:
                            print("column_for_pictures_of_users+str(index+2): {}".format(column_for_pictures_of_users+str(index+2)))
                        worksheet.insert_image(column_for_pictures_of_users+str(index+2),
                                               avatar_url,
                                               {'image_data': image_data, 'x_scale': resize_scale, 'y_scale': resize_scale}
                                               )

            sections_df.to_excel(writer, sheet_name='Sections')

            # Close the Pandas Excel writer and output the Excel file.
            writer.close()

if __name__ == "__main__": main()

