#!/usr/bin/env python3
#-*- coding: utf-8 -*-
# -*- mode: python; python-indent-offset: 4 -*-
#
# ./check_color.py
#
# The program creats three cells in a spreadsheet and then the
# heck_red_substring() function was used to check for a red substrin gin the cell.
#
#
# 2025-03-14
#
# G. Q. Maguire Jr.
#
import csv, time
from pprint import pprint
import optparse
import sys

from openpyxl import Workbook
from openpyxl import load_workbook
from openpyxl.styles import Color, Font
from openpyxl.cell.rich_text import Text
from openpyxl.cell.text import InlineFont
from openpyxl.cell.rich_text import TextBlock, CellRichText


def check_red_substring(cell):
    """Checks if any substring within a cell is red (RGB: FFFF0000)."""
    if cell.value is None:
        return False

    if cell.font and cell.font.color and cell.font.color.rgb == 'FFFF0000':
        return True # if the entire cell is red

    if type(cell.value) == CellRichText                  :
        for element in cell.value:
            if isinstance(element, TextBlock):
                if element.font and element.font.color and element.font.color.rgb == 'FFFF0000':
                    return True

    return False

# Example usage (assuming you have a workbook and sheet loaded)
# Create a test workbook and sheet for demonstration.

def main():
    global Verbose_Flag
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
    wb = Workbook()
    sheet = wb.active

    # Cell one, all black
    sheet['A1'] = "abc"

    # Cell two, all red
    red_font = Font(color=Color(rgb='FFFF0000'))
    sheet['B1'] = "def"
    sheet['B1'].font = red_font

    # Cell three, partial red

    # Cell three, partial red

    sheet['C1'].value = CellRichText(
        "q",
        TextBlock(InlineFont(color=Color(rgb='FFFF0000')),'w'),
        "e"
    )


    # Test the function
    cell_one = sheet['A1']
    cell_two = sheet['B1']
    cell_three = sheet['C1']

    print(f"Cell A1 (abc) has red substring: {check_red_substring(cell_one)}")
    print(f"Cell B1 (def) has red substring: {check_red_substring(cell_two)}")
    print(f"Cell C1 (qwe) has red substring: {check_red_substring(cell_three)}")

    wb.save('temp1.xlsx')


#
if __name__ == "__main__": main()
