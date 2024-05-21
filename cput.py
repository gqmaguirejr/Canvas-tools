#!  /usr/bin/env python3
#
# ./cput.py  canvas_course_page_url
# 
# put a given Canvas course page xxxx.html where xxxx is the last part of the URL
#
#
# Example:
#   cput.py https://kth.instructure.com/courses/11/pages/notes-20160716
#
# uploads the file notes-20160716.html into https://kth.instructure.com/courses/11/pages/notes-20160716
#
# G. Q: Maguire Jr.
#
# 2016.07.19
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

# styled based upon https://martin-thoma.com/configuration-files-in-python/
with open('config.json') as json_data_file:
       configuration = json.load(json_data_file)
       canvas = configuration['canvas']
       access_token= canvas["access_token"]
       # access_token=configuration["canvas"]["access_token"]
       #baseUrl = 'https://kth.instructure.com/api/v1/courses/' # changed to KTH domain
       baseUrl = 'https://%s/api/v1/courses/' % canvas.get('host', 'kth.instructure.com')
       header = {'Authorization' : 'Bearer ' + access_token}



#modules_csv = 'modules.csv' # name of file storing module names

# canvas_course_page_url will be of the form: https://kth.instructure.com/courses/11/pages/notes-20160716
def get_course_page(canvas_course_page_url):
       # Use the Canvas API to GET the page
       #GET /api/v1/courses/:course_id/pages/:url

       #extract course_id from URL
       course_id=canvas_course_page_url[canvas_course_page_url.find("courses/")+8:canvas_course_page_url.find("pages/")-1]
       if Verbose_Flag:
              print("course_id: {}".format(course_id))

       #extract the file name portion of the URL
       page_url=canvas_course_page_url[canvas_course_page_url.rfind("/")+1:]
       if Verbose_Flag:
              print("page_url: {}".format(page_url))

       new_file_name=canvas_course_page_url[canvas_course_page_url.rfind("/")+1:]+'.html'
       if Verbose_Flag:
              print("new_file_name: {}".format(new_file_name))


       url = baseUrl + '%s/pages/%s' % (course_id, page_url)
       if Verbose_Flag:
              print(url)
       payload={}
       r = requests.get(url, headers = header, data=payload)
       if Verbose_Flag:
              print("r.status_code: {}".format(r.status_code))
       if r.status_code == requests.codes.ok:
              page_response = r.json()

              # write out body of response as a .html page
              with open(new_file_name, 'wb') as f:
                     encoded_output = bytes(page_response["body"], 'UTF-8')
                     f.write(encoded_output)
              return True

       else:
              print("No such page: {}".format(canvas_course_page_url))
              return False
       return False

# canvas_course_page_url will be of the form: https://kth.instructure.com/courses/11/pages/notes-20160716
def put_course_page(canvas_course_page_url):
       # Use the Canvas API to GET the page
       #GET /api/v1/courses/:course_id/pages/:url

       #extract course_id from URL
       course_id=canvas_course_page_url[canvas_course_page_url.find("courses/")+8:canvas_course_page_url.find("pages/")-1]
       if Verbose_Flag:
              print("course_id: {}".format(course_id))

       #extract the file name portion of the URL
       page_url=canvas_course_page_url[canvas_course_page_url.rfind("/")+1:]
       if Verbose_Flag:
              print("page_url: {}".format(page_url))

       new_file_name=canvas_course_page_url[canvas_course_page_url.rfind("/")+1:]+'.html'
       if Verbose_Flag:
              print("new_file_name: {}".format(new_file_name))

       # read .html page
       with open(new_file_name, 'rb') as f:
              file_input=f.read()
              
       url = baseUrl + '%s/pages/%s' % (course_id, page_url)
       if Verbose_Flag:
              print(url)
       payload={"wiki_page[body]": file_input}
       r = requests.put(url, headers = header, data=payload)
       if Verbose_Flag:
              print("r.status_code: {}".format(r.status_code))
       if r.status_code == requests.codes.ok:
              page_response = r.json()
              pprint(page_response)
              return True
       else:
              print("No such page: {}".format(canvas_course_page_url))
              return False
       return False



def main():
       global Verbose_Flag

       parser = optparse.OptionParser()

       parser.add_option('-v', '--verbose',
                         dest="verbose",
                         default=False,
                         action="store_true",
                         help="Print lots of output to stdout"
       )

       options, remainder = parser.parse_args()

       Verbose_Flag=options.verbose
       if Verbose_Flag:
              print('ARGV      :', sys.argv[1:])
              print('VERBOSE   :', options.verbose)
              print('REMAINING :', remainder)

       if (len(remainder) < 1):
              print("Inusffient arguments\n must provide canvas_course_page_url\n")
       else:
              canvas_course_page_url=remainder[0]

              output=put_course_page(canvas_course_page_url)
              if (output):
                     if Verbose_Flag:
                            pprint(output)


if __name__ == "__main__": main()


