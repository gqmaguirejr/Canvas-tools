#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -*- mode: python; python-indent-offset: 4 -*-
#
# extract_terms_from_CSV.py input_csv_file output_txt_file
#
# Reads a 3-column CSV file (subject,predicate,object) and extracts all
# unique subjects and objects into a new text file, one term per line.
#
# Also outputs narrow terms (NT) and broad terms (BT) as separate files.
#
# Example
# ./extract_terms_from_CSV.py /tmp/cleaned_ieee_thesaurus_2023.csv /tmp/ieee_thesaurus_2023_terms.txt
#
# Output
# outputs the number of unique terms, the number of narrow terms, and the number of broad terms
# and outputs files with names of the form:
# base_output_name.txt
# base_output_name + '_narrow.txt'
# base_output_name + '_broad.txt'
#
#
# Note
# One might use this with the CSV file: https://github.com/angelosalatino/ieee-taxonomy-thesaurus-rdf/blob/main/source/cleaned_ieee_thesaurus_2023.csv

import csv
import sys
import os

def main():
    # Check for the correct number of command-line arguments
    if len(sys.argv) != 3:
        print("Usage: python extract_terms.py <input_csv_file> <output_txt_file>")
        sys.exit(1)

    input_csv_file = sys.argv[1]
    output_txt_file = sys.argv[2]

    # Check if the input file exists
    if not os.path.exists(input_csv_file):
        print(f"Error: Input file not found at '{input_csv_file}'")
        sys.exit(1)
        
    terms = set()
    narrow_terms = set()
    broad_terms = set()
    
    print(f"Reading from '{input_csv_file}'...")

    try:
        # Open and read the CSV file
        with open(input_csv_file, mode='r', encoding='utf-8') as infile:
            reader = csv.reader(infile)
            
            # Skip the header row if it exists (optional)
            # next(reader) 
            
            for row in reader:
                # Add subject and object to the appropriate set(s)
                if len(row) >= 3:
                    subject = row[0].strip()
                    predicate=row[1].strip()
                    object_val = row[2].strip()
                    
                    if subject:
                        terms.add(subject)
                    if object_val:
                        terms.add(object_val)
                    if predicate == 'NT':
                        narrow_terms.add(object_val)
                    if predicate == 'BT':
                        broad_terms.add(object_val)
                else:
                    print(f"Skipping malformed row: {row}")

        # Save the elements to the output text file
        sorted_terms = sorted(list(terms))
        sorted_narrow_terms = sorted(list(narrow_terms))
        sorted_broad_terms = sorted(list(broad_terms))
        
        # Use os.path.splitext to safely get the base filename
        base_output_name, extension = os.path.splitext(output_txt_file)

        # Write the main terms file
        with open(output_txt_file, mode='w', encoding='utf-8') as outfile:
            for term in sorted_terms:
                outfile.write(f"{term}\n")
        
        # Write the narrow terms file
        narrow_file_name = base_output_name + '_narrow.txt'
        with open(narrow_file_name, mode='w', encoding='utf-8') as outfile:
            for term in sorted_narrow_terms:
                outfile.write(f"{term}\n")

        # Write the broad terms file
        broad_file_name = base_output_name + '_broad.txt'
        with open(broad_file_name, mode='w', encoding='utf-8') as outfile:
            for term in sorted_broad_terms:
                outfile.write(f"{term}\n")

        print(f"Success! Wrote {len(sorted_terms)} unique terms to '{output_txt_file}'.")
        print(f"Wrote {len(sorted_narrow_terms)} narrow terms to '{narrow_file_name}'.")
        print(f"Wrote {len(sorted_broad_terms)} broad terms to '{broad_file_name}'.")

    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
