#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -*- mode: python; python-indent-offset: 4 -*-
#
# ./augments-course-stats-with-plots.py  -c course_id
#
# reads in data from 'course-modules-item-stats-'+course_id+'.xlsx'
#
# outputs an updated spreadsheet 'course-modules-item-stats-'+course_id+'-augmented.xlsx'
#
# G. Q. Maguire Jr.
#
# 2021-10-23
#
# based on earlier augment_course_data.py
#

from pprint import pprint
import requests, time
import json
import argparse
import sys
import re
import datetime

# Use Python Pandas to create XLSX files
import pandas as pd

def round_up_to_base(x, base=5):
    return int(x) + (base - int(x)) % base

def xls_col_num_to_letters(colnum):
    a = []
    while colnum:
        colnum, remainder = divmod(colnum - 1, 26)
        a.append(remainder)
    a.reverse()
    return ''.join([chr(n + ord('A')) for n in a])

def df_name_to_col(df, col_name):
    column_names=df.columns
    for index, col in enumerate(column_names):
        #print("col_name={0}, col_name type={1}, index={2}, col={3}, col ltype={4}".format(col_name, type(col_name), index, col, type(col)))
        if col_name == col:
            return xls_col_num_to_letters(index+2)
    # If the column name could be interpreted as an integer, then df.columns returns the integer
    # try matching integers
    for index, col in enumerate(column_names):
        #print("col_name={0}, col_name type={1}, index={2}, col={3}, col type={4}".format(col_name, type(col_name), index, col, type(col)))
        if type(col) is int:
            if col_name ==str (col):
                return xls_col_num_to_letters(index+2)

    print("Unable to convert column name to spreadsheet column")
    return 'A'

def collect_module_names(df):
    module_names=set()
    for index, row in df.iterrows():
        module_name=row.get('module_name', None)
        if module_name:
            module_names.add(module_name)
    return sorted(list(module_names))



def main(argv):
    global Verbose_Flag
    global testing


    argp = argparse.ArgumentParser(description="augments-course-stats-with-plots.py: to add plots to course stats")

    argp.add_argument('-v', '--verbose', required=False,
                      default=False,
                      action="store_true",
                      help="Print lots of output to stdout")

    argp.add_argument('-t', '--testing',
                      default=False,
                      action="store_true",
                      help="execute test code"
                      )

    argp.add_argument("-c", "--canvas_course_id", type=int, required=True,
                      help="canvas course_id")

    argp.add_argument('--unpublished',
                      default=False,
                      action='store_true',
                      help="Include unpublished pages")

    args = vars(argp.parse_args(argv))
    Verbose_Flag=args["verbose"]

    course_id=args["canvas_course_id"]
    print("course_id={}".format(course_id))

    # read in the sheets
    input_file="course-modules-item-stats-{0}.xlsx".format(course_id)
    if args['unpublished']:
        sheet_name='All pages'
    else:
        sheet_name='All published pages'

    all_pages_df = pd.read_excel(open(input_file, 'rb'), sheet_name=sheet_name)
    del all_pages_df['Unnamed: 0']

    module_names=collect_module_names(all_pages_df)
    print("module_names={}".format(module_names))

    module_colors={}
    for index, d in enumerate(module_names):
        if (index%30) == 0:
            c= {'color': 'blue', 'transparency': 50}
        elif (index%30) == 1:
            c= {'color': 'red', 'transparency': 50}
        elif (index%30) == 2:
            c= {'color': 'green', 'transparency': 50}
        elif (index%30) == 3:
            c= {'color': 'magenta', 'transparency': 50}
        elif (index%30) == 4:
            c= {'color': 'cyan', 'transparency': 50}
        elif (index%30) == 5:
            c= {'color': 'lime', 'transparency': 50}
        elif (index%30) == 6:
            c= {'color': 'navy', 'transparency': 50}
        elif (index%30) == 7:
            c= {'color': 'pink', 'transparency': 50}
        elif (index%30) == 8:
            c= {'color': 'gray', 'transparency': 50}
        elif (index%30) == 9:
            c= {'color': 'purple', 'transparency': 50}
        elif (index%30) == 10:
            c= {'color': 'brown', 'transparency': 50}
        elif (index%30) == 11:
            c= {'color': 'red', 'transparency': 70}
        elif (index%30) == 12:
            c= {'color': 'green', 'transparency': 70}
        elif (index%30) == 13:
            c= {'color': 'magenta', 'transparency': 70}
        elif (index%30) == 14:
            c= {'color': 'cyan', 'transparency': 70}
        elif (index%30) == 15:
            c= {'color': 'lime', 'transparency': 70}
        elif (index%30) == 16:
            c= {'color': 'navy', 'transparency': 70}
        elif (index%30) == 17:
            c= {'color': 'pink', 'transparency': 70}
        elif (index%30) == 18:
            c= {'color': 'gray', 'transparency': 70}
        elif (index%30) == 19:
            c= {'color': 'purple', 'transparency': 70}
        elif (index%30) == 20:
            c= {'color': 'brown', 'transparency': 70}
        elif (index%30) == 21:
            c= {'color': 'red', 'transparency': 30}
        elif (index%30) == 22:
            c= {'color': 'green', 'transparency': 30}
        elif (index%30) == 23:
            c= {'color': 'magenta', 'transparency': 30}
        elif (index%30) == 24:
            c= {'color': 'cyan', 'transparency': 30}
        elif (index%30) == 25:
            c= {'color': 'lime', 'transparency': 30}
        elif (index%30) == 26:
            c= {'color': 'navy', 'transparency': 30}
        elif (index%30) == 27:
            c= {'color': 'pink', 'transparency': 30}
        elif (index%30) == 28:
            c= {'color': 'gray', 'transparency': 30}
        elif (index%30) == 29:
            c= {'color': 'purple', 'transparency': 30}
        else:
            c= {'color': 'orange', 'transparency': 50}
        module_colors[d]={'name': d, 'color': c}
    if Verbose_Flag:
        print("module_colors={}".format(module_colors))

    output_file="course-modules-item-stats-{0}-augmented.xlsx".format(course_id)
    writer = pd.ExcelWriter(output_file, engine='xlsxwriter')

    # write out the exiting data for all of the pages
    all_pages_df.to_excel(writer, sheet_name=sheet_name)

    # generate some plots
    # Access the XlsxWriter workbook and worksheet objects from the dataframe.
    #     
    
    workbook = writer.book
    worksheet = writer.sheets[sheet_name]

    max_row = len(all_pages_df)
    print("max_row={}".format(max_row))

    # Configure the series.
    chart1 = workbook.add_chart({'type': 'bar'})
    # Set an Excel chart style.
    #chart1.set_style(11)

    
    score_name='smog_score'
    # for a bar chart the val and cat are reversed from that of a column chart
    cat_col=df_name_to_col(all_pages_df, 'module_name')
    val_col=df_name_to_col(all_pages_df, score_name)
    print("cat_col={0}, val_col={1}".format(cat_col, val_col))
    chart1.add_series({
        'name': "='{0}'!${1}$1".format(sheet_name, val_col),
        'categories': "='{0}'!${1}2:${1}{2}".format(sheet_name, cat_col, max_row+1),
        'values': "='{0}'!${1}2:${1}{2}".format(sheet_name, val_col, max_row+1),
        #'border':    {'color': 'red', 'transparency': 50},
        'border': {'none': True},
        'fill':    {'color': 'red', 'transparency': 50}
    })

    # Add a chart title and some axis labels.
    chart1.set_title ({'name': "SMOG scores for course: {}".format(course_id)})
    # for a bar chart the x and y are reversed from that of a column chart
    chart1.set_y_axis({'name': 'module_name'})
    chart1.set_y_axis({'reverse': True}) # place the first module name at the top

    max_score=all_pages_df[score_name].max()
    x_max=round_up_to_base(max_score, 5)
    print("x_max={}".format(x_max))
    chart1.set_x_axis({'name': 'SMOG score', 'min': 0, 'max': x_max})
    chart1.set_legend({'none': True})

    y_factor=float(int(round_up_to_base(max_row, 50)/50))
    chart1.set_size( {'x_scale': 1.0, 'y_scale': y_factor} )

    # Insert the chart into the worksheet.
    chart_position="{0}{1}".format(xls_col_num_to_letters(len(all_pages_df.columns)+1), 2)
    print("chart_position={}".format(chart_position))
    worksheet.insert_chart(chart_position, chart1)

    workbook.close()
    # Close the Pandas Excel writer and output the Excel file.
    writer.save()

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
