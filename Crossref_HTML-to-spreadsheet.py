#!/usr/bin/python3.11
# -*- coding: utf-8 -*-
#
# ./Crossref_HTML-to-spreadsheet.py HTML_file spredsheet_file.xlsx
#
# Process references from the HTML table produced by Crossref's Simple Text Query (https://apps.crossref.org/SimpleTextQuery) to add reference information to a spreadsheet
#
# with option '-v' use verbose output
#
# G. Q. Maguire Jr.
#
# 2026-05-08
#
#

import os
import sys
import optparse
import re
import pandas as pd
from bs4 import BeautifulSoup

def extract_crossref_data(html_file):
    """
    Extracts data by identifying the last <br> as the boundary between 
    the student's citation and the Crossref-injected link.
    """
    base_name = os.path.splitext(os.path.basename(html_file))[0]
    
    with open(html_file, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    table = soup.find('table', class_='resultB')
    if not table:
        return []

    new_data = []
    rows = table.find_all('tr', class_='resultB')

    # Patterns to find IDs in plain text strings
    doi_pattern = re.compile(r'https?://doi\.org/\S+')
    url_pattern = re.compile(r'https?://(?!doi\.org)\S+')

    for row in rows:
        td = row.find('td', class_='resultB')
        if not td:
            continue

        # --- Step 1: Identify the Boundary (Last <br>) ---
        # We look at the children inside the TD cell
        children = list(td.contents)
        last_br_index = -1
        for i, child in enumerate(children):
            if child.name == 'br':
                last_br_index = i

        # --- Step 2: Extract Reference Text ---
        # Everything before the LAST <br> is your citation
        ref_fragments = []
        # If no <br> is found, we take the whole thing as a fallback
        target_children = children[:last_br_index] if last_br_index != -1 else children
        
        for child in target_children:
            if hasattr(child, 'get_text'):
                ref_fragments.append(child.get_text())
            else:
                ref_fragments.append(str(child))
        
        full_student_text = "".join(ref_fragments).strip()
        if len(full_student_text) < 5:
            continue

        # --- Step 3: Extract IDs from the Student's Text ---
        doi_match = doi_pattern.search(full_student_text)
        doi_in_ref = doi_match.group(0) if doi_match else ""
        found_urls = url_pattern.findall(full_student_text)
        
        # --- Step 4: Identify Crossref's DOI ---
        # Crossref appends its result as an <a> tag at the very end
        crossref_doi = ""
        all_links = td.find_all('a', href=True)
        if all_links:
            last_link = all_links[-1]
            if 'doi.org/' in last_link['href']:
                crossref_doi = last_link.get_text(strip=True)

        new_data.append({
            "Source Basename": base_name,
            "Reference Text": full_student_text,
            "URLs": "; ".join(found_urls),
            "DOI in Reference": doi_in_ref,
            "Crossref DOI": crossref_doi
        })
        
    return new_data


def main():
    global Verbose_Flag
    global options

    parser = optparse.OptionParser()
    parser.add_option('-v', '--verbose',
                      dest="verbose",
                      default=False,
                      action="store_true",
                      help="Print lots of output to stdout")

    options, remainder = parser.parse_args()
    Verbose_Flag = options.verbose


    if Verbose_Flag:
        print(f"ARGV      : {sys.argv[1:]}")
        print(f"VERBOSE   : {options.verbose}")
        print(f"REMAINING : {remainder}")

    if len(sys.argv) < 3:
        print("Usage: python update_refs.py <HTML_input_file> <Spreadsheet_output_file>")
        print("Example: python update_refs.py results.html bibliography.xlsx")
        sys.exit(1)

    html_input = sys.argv[1]
    spreadsheet_output = sys.argv[2]
       
    if not os.path.exists(html_input):
        print(f"Error: Input file '{html_input}' not found.")
        sys.exit(1)

    new_entries = extract_crossref_data(html_input)
    if not new_entries:
        print("No data extracted. Exiting.")
        return

    df_new = pd.DataFrame(new_entries)

    # Reorder columns to ensure Crossref DOI is last
    cols = ["Source Basename", "Reference Text", "URLs", "DOI in Reference", "Crossref DOI"]
    df_new = df_new[cols]

    # Handle the spreadsheet (Create or Append)
    if os.path.exists(spreadsheet_output):
        if Verbose_Flag:
            print(f"Updating existing spreadsheet: {spreadsheet_output}")
        # Determine format based on extension
        if spreadsheet_output.endswith('.xlsx'):
            df_old = pd.read_excel(spreadsheet_output)
        else:
            df_old = pd.read_csv(spreadsheet_output)
        
        # Combine old and new data
        df_final = pd.concat([df_old, df_new], ignore_index=True)
    else:
        print(f"Creating new spreadsheet: {spreadsheet_output}")
        df_final = df_new

    # Save the result
    if spreadsheet_output.endswith('.xlsx'):
        # Requires 'openpyxl' installed: pip install openpyxl
        df_final.to_excel(spreadsheet_output, index=False)
    else:
        # Default to CSV if not .xlsx, using utf-8-sig for Excel compatibility
        df_final.to_csv(spreadsheet_output, index=False, encoding='utf-8-sig')

    print(f"Successfully added {len(new_entries)} entries to {spreadsheet_output}")

if __name__ == "__main__":
    main()
