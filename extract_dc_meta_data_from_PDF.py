#!/usr/bin/env python3
#-*- coding: utf-8 -*-
# -*- mode: python; python-indent-offset: 4 -*-
#
# ./extract_dc_meta_data_from_PDF.py pdf_filename
#
# The program opens the file and extracts the Dublin Core metadata
#
# Examples:
# ./extract_dc_meta_data_from_PDF.py /tmp/KTH_new_cover_experiment_with_configuration_with_Arial.pdf
#
# 2025-01-27
#
# G. Q. Maguire Jr.
#
import csv, time
from pprint import pprint
import optparse
import sys


from pypdf import PdfReader
from xml.etree import ElementTree

def extract_dc_metadata(pdf_path):
    """
    Extracts Dublin Core metadata from a PDF file.

    Args:
        pdf_path (str): The path to the PDF file.

    Returns:
        dict: A dictionary containing Dublin Core metadata or None if not found.
    """
    global Verbose_Flag
    
    try:
        with open(pdf_path, 'rb') as f:
            reader = PdfReader(f)
            if Verbose_Flag:
                print(f'Opened file "{pdf_path}"')

            if reader.metadata:
                if Verbose_Flag:
                    print(f'{reader.metadata=}')

            if reader.xmp_metadata:
                if Verbose_Flag:
                    print(f'{reader.xmp_metadata=}')
                root = reader.xmp_metadata.rdf_root

                #### for the moment just print as opoosed to returin g a dict
                print(type(root))
                print(root.toxml())
                return None

    except FileNotFoundError:
        print(f"Error: File not found at {pdf_path}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def main():
    global Verbose_Flag
    global directory_prefix
    #
    directory_prefix='/tmp/'
    #
    parser = optparse.OptionParser()
    #
    parser.add_option('-v', '--verbose',
                      dest="verbose",
                      default=False,
                      action="store_true",
                      help="Print lots of output to stdout"
    )
    #
    options, remainder = parser.parse_args()
    #
    Verbose_Flag=options.verbose
    if Verbose_Flag:
        print("ARGV      : {}".format(sys.argv[1:]))
        print("VERBOSE   : {}".format(options.verbose))
        print("REMAINING : {}".format(remainder))
    #
    if (len(remainder) < 1):
        print("Insuffient arguments\n must provide file_name\n")
        return
    #
    input_file_name=remainder[0]
    dc_data = extract_dc_metadata(input_file_name)

    if dc_data:
        print("Dublin Core Metadata:")
        for key, value in dc_data.items():
            print(f"  {key}: {value}")
    else:
        print("No Dublin Core metadata found in this PDF or an error occurred.")



#
if __name__ == "__main__": main()

