#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -*- mode: python; python-indent-offset: 4 -*-
#
# ./combine_XLSX:files.py path
# 
# The program walks the path to collect the XLSX files into a single speadsheet.
#
# Example:
# ./combine_XLSX_files.py --dir "./Course_41668/course files/"
#  produces combined_sheets.xlsx in the directory ./Course_41668
#  This is done so that you can run the file repeatedly without needing to delete the file
#  and without any rigk of it being included in the XLX files that will be combined.
#
# 2024..01.11
#
# G. Q. Maguire Jr.
#


import csv, time
from pprint import pprint
import optparse
import sys

import json
import re

import copy  # so that we can make a deep copy

# Use Python Pandas to create XLSX files
import pandas as pd

import os

def main():
    global Verbose_Flag

    parser = optparse.OptionParser()

    parser.add_option('-v', '--verbose',
                      dest="verbose",
                      default=False,
                      action="store_true",
                      help="Print lots of output to stdout"
    )

    parser.add_option('--testing',
                      dest="testing",
                      default=False,
                      action="store_true",
                      help="Run in testing mode"
    )

    parser.add_option("--dir", dest="dir_prefix",
                      default='./',
                      help="directory to start from", metavar="FILE")

    options, remainder = parser.parse_args()

    Verbose_Flag=options.verbose
    if Verbose_Flag:
        print("ARGV      : {}".format(sys.argv[1:]))
        print("VERBOSE   : {}".format(options.verbose))
        print("REMAINING : {}".format(remainder))

    # compute the directory prefix for files to be used for the program's I/O
    # This does not apply to the CEFR spreadsheet files.
    directory_prefix=options.dir_prefix
    if not directory_prefix.endswith('/'):
        directory_prefix=directory_prefix+'/'
    if Verbose_Flag:
        print(f'{directory_prefix=}')

    cumulative_df=pd.DataFrame()
    
    for root, dirs, files in os.walk(directory_prefix, topdown=True):
        for filename in files:
            if Verbose_Flag:
                print(f'file: {filename}')

            # skip locl files
            if filename.startswith('~$'):
                continue

            base_file_name, file_extension = os.path.splitext(os.path.join(root, filename))
            if file_extension== '.xlsx':
                print(f'found XLSX file: {base_file_name} with {file_extension}')
                joined_name=os.path.join(root, filename)
                stats_df = pd.read_excel(open(joined_name, 'rb'), sheet_name='Stats')
                stats_df['joined_name']=joined_name
                cumulative_df = pd.concat([cumulative_df, stats_df])

            #doSomethingWithFile(os.path.join(root, filename))
        for dirname in dirs:
            print(f'directory {dirname}')
            #doSomewthingWithDir(os.path.join(root, dirname))

    # set up the output write
    if directory_prefix.endswith('/'):
        directory_to_use=directory_prefix[:directory_prefix[:-1].rfind('/')]
    else:
        directory_to_use=directory_prefix[:directory_prefix.rfind('/')]
    print(f'using directory: {directory_to_use}')
    new_file_name=f'{directory_to_use}/combined_sheets.xlsx'
    print(f'outputting file: {new_file_name}')
    cumulative_df.rename(columns = {'Unnamed: 0':'orignal_row'}, inplace = True)
    writer = pd.ExcelWriter(new_file_name, engine='xlsxwriter')
    cumulative_df.to_excel(writer, sheet_name='Stats')

    workbook = writer.book
    two_decimals_fmt_dict={'num_format': '0.00'}
    two_decimals_fmt = workbook.add_format(two_decimals_fmt_dict)

    bottom_thick_border_fmt_dict = {'bottom': 5, 'bold': True}
    bottom_thick_border_fmt = workbook.add_format(bottom_thick_border_fmt_dict)

    two_decimals_bottom_thick_border_fmt_dict = {'bottom': 5, 'bold': True, 'num_format': '0.00'}
    two_decimals_bottom_thick_border_fmt = workbook.add_format(two_decimals_bottom_thick_border_fmt_dict)
    
    worksheet = writer.sheets['Stats']
    worksheet.set_column('F:F', 20, two_decimals_fmt)

    worksheet.autofit()
    # Close the Pandas Excel writer and output the Excel file.
    writer.close()


if __name__ == "__main__": main()
