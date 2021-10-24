#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# ./compute_stats_for_course.py course_id
#
# Textatistic is used to compute some statistics about module items that are Pages.
# For details of the metrics, see https://www.erinhengel.com/software/textatistic/
# and the code at https://github.com/erinhengel/Textatistic/blob/master/textatistic/textatistic.py
#
#       HTML elements that contain non-English sentences are filtered or cause an exception for Textatistic.
#             By default, only published pages are processed (use option -u or --unpublished to include them).
#
#      The pages (either on 'All pages' or 'All published pages') are sorted by the module's position and the postion of the page within this module. This is to make it easy to look at the statistics for pages within a module and across modules.
#
#       Note: The filtering is a work in progress - the filters should be expanded.
#
# Output: XLSX spreadsheet with modules in course
#
#
#
# with the option "-v" or "--verbose" you get lots of output - showing in detail the operations of the program
#
# Can also be called with an alternative configuration file:
# ./list_your_courses.py --config config-test.json
#
# Options '-t'and '--testing' are for testing
#
# Options '-u' '--unpublished' cause unpublished pages to also be processed.
#
# Example:
# ./compute_stats_for_course.py 11
#
# ./compute_stats_for_course.py --config config-test.json 11
#
# 
# documentation about using xlsxwriter to insert images can be found at:
#   John McNamara, "Example: Inserting images into a worksheet", web page, 10 November 2018, https://xlsxwriter.readthedocs.io/example_images.html
#
# G. Q. Maguire Jr.
#
# based on earlier list-modules.py
#
# 2021.10.22
#

import requests, time
import pprint
import optparse
import sys
import json

# Use Python Pandas to create XLSX files
import pandas as pd

from lxml import html
import lxml.etree as et

from textatistic import Textatistic

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

def list_modules(course_id):
    modules_found_thus_far=[]
    # Use the Canvas API to get the list of modules for the course
    #GET /api/v1/courses/:course_id/modules

    url = "{0}/courses/{1}/modules".format(baseUrl, course_id)
    if Verbose_Flag:
        print("url: {}".format(url))

    r = requests.get(url, headers = header)
    if Verbose_Flag:
        print("result of getting modules: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        page_response=r.json()

        for p_response in page_response:  
            modules_found_thus_far.append(p_response)

            # the following is needed when the reponse has been paginated
            # i.e., when the response is split into pieces - each returning only some of the list of modules
            # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
            while r.links.get('next', False):
                r = requests.get(r.links['next']['url'], headers=header)  
                if Verbose_Flag:
                    print("result of getting modules for a paginated response: {}".format(r.text))
                page_response = r.json()  
                for p_response in page_response:  
                    modules_found_thus_far.append(p_response)

    return modules_found_thus_far

def list_module_items(course_id, module_id):
    module_items_found_thus_far=[]
    # Use the Canvas API to get the list of modules for the course
    # GET /api/v1/courses/:course_id/modules/:module_id/items

    url = "{0}/courses/{1}/modules/{2}/items".format(baseUrl, course_id, module_id)
    if Verbose_Flag:
        print("url: {}".format(url))

    r = requests.get(url, headers = header)
    if Verbose_Flag:
        print("result of getting module items: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        page_response=r.json()

        for p_response in page_response:  
            module_items_found_thus_far.append(p_response)

            # the following is needed when the reponse has been paginated
            # i.e., when the response is split into pieces - each returning only some of the list of modules
            # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
            while r.links.get('next', False):
                r = requests.get(r.links['next']['url'], headers=header)  
                if Verbose_Flag:
                    print("result of getting modules for a paginated response: {}".format(r.text))
                page_response = r.json()  
                for p_response in page_response:  
                    module_items_found_thus_far.append(p_response)

    return module_items_found_thus_far

def augment_entries(course_id, moduleItems, module_name, module_position, options):
    newModuleitems=[]
    for mi in moduleItems:
        mn={'module_name': module_name, 'module_position': module_position}
        mn.update(mi)
        mi=mn
        publishedP=mi['published']
        if not options.unpublished and not publishedP:      # If not published do not process it further, but add it to the list to return
            newModuleitems.append(mi)
            continue
        mi_type=mi['type']
        if mi_type == 'Page':
            url=mi['url']
            if Verbose_Flag:
                print(url)
            page_entry=None
            payload={}
            r = requests.get(url, headers = header, data=payload)
            if r.status_code == requests.codes.ok:
                page_response = r.json()  
                if Verbose_Flag:
                    print("body: {}".format(page_response["body"]))
                if page_response:
                    body=page_response.get("body", None)
                if body and isinstance(body, str) and len(body) > 0:
                    document = html.document_fromstring(body)

                    elements_to_remove=['img', 'code', 'pre']
                    for el in elements_to_remove:
                        el_path="//{}".format(el)
                        for bad in document.xpath(el_path):
                            bad.getparent().remove(bad)

                    #  remove anything in one of the following languages
                    languages_to_remove=['sv', 'sv-SE', 'fr', 'fr-FR', 'de', 'de-DE', 'nb-NO', 'nn-NO', 'da-DK', 'zh-Hans', 'es', 'es-ES', 'nl', 'nl-NL', 'it', 'it-IT', 'X-NONE', 'x-western']
                    for l in languages_to_remove:
                        lang_path="//*[@lang=\'{0}\']".format(l)
                        for bad in document.xpath(lang_path):
                            bad.getparent().remove(bad)

                    expected_languages=['en', 'en-US', 'en-GB', 'en-UK']
                    for el in document.xpath('//*[@lang]'):
                        lang=el.get('lang')
                        if lang not in expected_languages:
                            print("Unexpected language={0}, url={1}".format(lang, url))

                    raw_text = document.text_content()
                    if Verbose_Flag:
                        print("raw_text: {}".format(raw_text))

                    if len(raw_text) > 0:
                        # see http://www.erinhengel.com/software/textatistic/
                        try:
                            page_entry=Textatistic(raw_text).dict()
                        except ZeroDivisionError:
                            # if there are zero sentences, then some of the scores cannot be computed
                            if Verbose_Flag:
                                print("no sentences in page {0}, raw_text={1}".format(url, raw_text))
                            page_entry={'text_stats_note': 'no sentences on page'}
                        except ValueError:
                            # if there is code on the page, for example a json structure, then the hyphenation package cannot handle this
                            if Verbose_Flag:
                                print("there is likely code on page {0}, raw_text={1}".format(url, raw_text))
                            page_entry={'text_stats_note': 'likely there is code on the page'}
                    else:
                        page_entry={'text_stats_note': 'no text left after filtering on the page'}

            # augment the module item if there were statistics
            if page_entry: 
                mi.update(page_entry)
            else:
                page_entry={'text_stats_note': 'No results for Textatistic on this page'}
                mi.update(page_entry)

        # add module item to list to return all module items
        newModuleitems.append(mi)

    return newModuleitems

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
                      help="conditional for testing"
    )

    parser.add_option('-u', '--unpublished',
                      dest="unpublished",
                      default=False,
                      action="store_true",
                      help="Include unpublished pages"
    )

    options, remainder = parser.parse_args()

    Verbose_Flag=options.verbose
    if Verbose_Flag:
        print("ARGV      : {}".format(sys.argv[1:]))
        print("VERBOSE   : {}".format(options.verbose))
        print("REMAINING : {}".format(remainder))
        print("Configuration file : {}".format(options.config_filename))

    initialize(options)

    if (len(remainder) < 1):
        print("Insuffient arguments - must provide course_id\n")
    else:
        course_id=remainder[0]
        modules=list_modules(course_id)
        if (modules):
            modules_df=pd.json_normalize(modules)
                     
            # below are examples of some columns that might be dropped
            #columns_to_drop=[]
            #modules_df.drop(columns_to_drop,inplace=True,axis=1)

            if Verbose_Flag:
                cols=modules_df.columns.values.tolist()
                print("cols={}".format(cols))

            modules_df.sort_values(by='position',inplace=True)

            # the following was inspired by the section "Using XlsxWriter with Pandas" on http://xlsxwriter.readthedocs.io/working_with_pandas.html
            # set up the output write
            writer = pd.ExcelWriter('course-modules-item-stats-'+course_id+'.xlsx', engine='xlsxwriter')
            modules_df.to_excel(writer, sheet_name='Modules')

            allModuleItems=[]
            for m in sorted(modules, key=lambda x: x['id']):
                m_id=int(m['id'])
                if options.testing: # only process specific modules, a list of module ids
                    if m_id not in (12, 13, 25, 26, 50, 51):
                        continue
                mi=list_module_items(course_id, m['id'])
                mi=augment_entries(course_id, mi, m['name'], m['position'], options)
                mi_df=pd.json_normalize(mi)
                mi_df.sort_values(by='position',inplace=True)
                mi_df.to_excel(writer, sheet_name=str(m['id']))
                allModuleItems.extend(mi) # save the latest module items to the whole set of them

            allModuleItems_df=pd.json_normalize(allModuleItems)
            allModuleItems_df.sort_values(by=['module_position', 'position'],inplace=True)
            allModuleItems_df = allModuleItems_df[allModuleItems_df.type == 'Page'] #  remove non-pages
            if options.unpublished:
                allModuleItems_df.to_excel(writer, sheet_name='All pages')
            else:
                allModuleItems_df = allModuleItems_df[allModuleItems_df.published == True] # remove unpublished pages
                allModuleItems_df.to_excel(writer, sheet_name='All published pages')

            # Close the Pandas Excel writer and output the Excel file.
            writer.save()

if __name__ == "__main__": main()
