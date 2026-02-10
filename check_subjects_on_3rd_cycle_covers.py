#!/usr/bin/python3.11
# -*- coding: utf-8 -*-
#
# check_subjects_on_3rd_cycle_covers.py dir_name
#
# Purpose: Check the subject on the covers of third cycle theses
#
# with option '-v' use verbose output
#
# G. Q. Maguire Jr. + help of Gemini 3 Pro
#
# 2026-02-03
#

import optparse
import sys
import pymupdf  # PyMuPDF
import re
import unicodedata # Added for character normalization
import json
import importlib

from pathlib import Path

# Add path to custom modules
#sys.path.append('/home/maguire/Canvas-tools')
sys.path.append('/z3/maguire/Canvas/Canvas-tools')  # Include the path to module_folder
#sys.path.append('/home/maguire/Canvas/Canvas-tools')

Verbose_Flag = False

third_cycle_subjects={
    'ARKITEKT': {'swe': 'Arkitektur', 'eng': 'Architecture'},
    'BIOLFYS': {'swe': 'Biologisk fysik', 'eng': 'Biological Physics'},
    'BIOTEKN': {'swe': 'Bioteknologi', 'eng': 'Biotechnology'},
    'BYV': {'swe': 'Byggvetenskap', 'eng': 'Civil and Architectural Engineering'},
    'DATALGEM': {'swe': 'Datalogi', 'eng': 'Computer Science'},
    'DATALOGI': {'swe': 'Datalogi', 'eng': 'Computer Science'},
    'ELSYSETS': {'swe': 'Elektro- och systemteknik', 'eng': 'Electrical Engineering'},
    'ELSYSGEM': {'swe': 'Elektro- och systemteknik', 'eng': 'Electrical Engineering'},
    'ELSYTEKN': {'swe': 'Elektro- och systemteknik', 'eng': 'Electrical Engineering'},
    'ENERGIT': {'swe': 'Energiteknik', 'eng': 'Energy Technology'},
    'FARKTE': {'swe': 'Farkostteknik', 'eng': 'Vehicle and Maritime Engineering'},
    'FASTBYGG': {'swe': 'Fastigheter och byggande', 'eng': 'Real Estate and Construction Management'},
    'FIBERPOL': {'swe': 'Fiber- och polymervetenskap', 'eng': 'Fibre and Polymer Science'},
    'FILOSOFI': {'swe': 'Filosofi', 'eng': 'Philosophy'},
    'FLYGRYMD': {'swe': 'Flyg- och rymdteknik', 'eng': 'Aerospace Engineering'},
    'FYSIK': {'swe': 'Fysik', 'eng': 'Physics'},
    'BUSINADM': {'swe': 'Företagsekonomi', 'eng': 'Business Studies'},
    'GEODEINF': {'swe': 'Geodesi och geoinformatik', 'eng': 'Geodesy and Geoinformatics'},
    'ISTTVM': {'swe': 'Historiska studier av teknik, vetenskap och miljö', 'eng': 'History of Science, Technology and Environment'},
    'HALLBST': {'swe': 'Hållbarhetsstudier', 'eng': 'Sustainability studies'},
    'HÅLLF': {'swe': 'Hållfasthetslära', 'eng': 'Solid Mechanics'},
    'INDEKOL': {'swe': 'Industriell ekologi', 'eng': 'Industrial Ecology'},
    'INDEKO': {'swe': 'Industriell ekonomi och organisation', 'eng': 'Industrial Engineering and Management'},
    'INDPROD': {'swe': 'Industriell produktion', 'eng': 'Production Engineering'},
    'INFKTEKN': {'swe': 'Informations- och kommunikationsteknik', 'eng': 'Information and Communication Technology'},
    'INFKTGEM': {'swe': 'Informations- och kommunikationsteknik', 'eng': 'Information and Communication Technology'},
    'KEMI': {'swe': 'Kemi', 'eng': 'Chemistry'},
    'KEMITEKN': {'swe': 'Kemiteknik', 'eng': 'Chemical Engineering'},
    'MASKINKO': {'swe': 'Maskinkonstruktion', 'eng': 'Machine Design'},
    'MATTE': {'swe': 'Matematik', 'eng': 'Mathematics'},
    'MEDICINT': {'swe': 'Medicinsk teknologi', 'eng': 'Medical Technology'},
    'MEDIAT': {'swe': 'Medieteknik', 'eng': 'Media Technology'},
    'MILJOTEK': {'swe': 'Miljöteknik', 'eng': 'Environmental Engineering'},
    'MÄNDATOR': {'swe': 'Människa-datorinteraktion', 'eng': 'Human-computer Interaction'},
    'NATIEKON': {'swe': 'Nationalekonomi', 'eng': 'Economics'},
    'SAMHPLAN': {'swe': 'Samhällsplanering', 'eng': 'Urban and Regional Planning'},
    'TALMUKOM': {'swe': 'Tal- och musikkommunikation', 'eng': 'Speech and Music Communication'},
    'TEKHÄLSA': {'swe': 'Teknik och hälsa', 'eng': 'Technology and Health'},
    'TECLEARN': {'swe': 'Teknik och lärande', 'eng': 'Technology and Learning'},
    'TEVLKOMM': {'swe': 'Teknikvetenskapens lärande och kommunikation', 'eng': 'Education and Communication in the Technological Sciences'},
    'TEMATRVE': {'swe': 'Teknisk materialvetenskap', 'eng': 'Materials Science and Engineering'},
    'TEMEKAN': {'swe': 'Teknisk mekanik', 'eng': 'Engineering Mechanics'},
    'TKEMIBIO': {'swe': 'Teoretisk kemi och biologi', 'eng': 'Theoretical Chemistry and Biology'},
    'TILLFYS': {'swe': 'Tillämpad fysik', 'eng': 'Applied Physics'},
    'TIMABEMA': {'swe': 'Tillämpad matematik och beräkningsmatematik', 'eng': 'Applied and Computational Mathematics'},
    'TRANGEM': {'swe': 'Transportvetenskap', 'eng': 'Transport Science'},
    'TRANSPVP': {'swe': 'Transportvetenskap', 'eng': 'Transport Science'},
    'VATTVTEK': {'swe': 'Vattenvårdsteknik', 'eng': 'Water Resources Engineering'},
    'KTHXXX': {'swe': '*****Okänt ämneområde*****', 'eng': '*****Unknown subject area*****'}, # Fake subject for use in template
}


def get_subject_area(pdf_path):
    """
    Attempts to read the subject area (e.g., 'Information and Communication Technology')
    from the cover/title page of the PDF, robustly handling multi-line subjects using
    the PyMuPDF 'blocks' extraction method for better structural awareness.
    
    The function uses an explicit list of valid subject areas to reliably match 
    and extract the correct field of study, discarding the specific thesis title.
    """
    global options
    global VALID_SUBJECT_AREAS
    global VALID_SUBJECT_AREAS_English
    global VALID_SUBJECT_AREAS_Swedish
    subject = "Unknown"
    doc = None
    
    # Matches common leading thesis title text (Doctoral Thesis in, Master's Thesis in, etc.)
    thesis_title_pattern = re.compile(r'(?:Doctoral|Licentiate|Master\'s)\s+Thesis\s+in\s*', re.IGNORECASE)
    swedish_thesis_title_pattern = re.compile(r'(?:Doktorsavhandling|Licentiatuppsats|Licentiatavhandling|Magisteravhandling|Masteruppsats)\s+inom\s*', re.IGNORECASE)
    
    try:
        doc = pymupdf.open(pdf_path)

        # Search page 1 (index 0) and page 2 (index 1)
        for pageno in range(min(1, doc.page_count)):
            blocks = doc[pageno].get_text("blocks", sort=True)
            
            for (x0, y0, x1, y1, block_text, block_no, block_type) in blocks:
                
                if options.verbose:
                    print(f"GQM: {block_text=}, {block_no=}, {block_type=}")
                # Normalize the block text: replace newlines with spaces and strip
                # Example: "Doctoral Thesis in Mathematics Existence, uniqueness, and regularity theory for local and nonlocal problems"
                text_to_search = block_text.replace('\n', ' ').strip()
                
                
                #if re.search(r'Thesis\s+in', text_to_search, re.IGNORECASE):
                first_match=thesis_title_pattern.search(text_to_search)
                if first_match:
                    #print(f"{first_match.group(0)=}")
                    # 1. Clean the text to remove "Doctoral Thesis in " boilerplate
                    # subject_raw: "Mathematics Existence, uniqueness, and regularity theory for local and nonlocal problems"
                    subject_raw = thesis_title_pattern.split(text_to_search)[-1].strip()
                    if options.verbose:
                        print(f"{subject_raw=}")
                    
                    if subject_raw:
                        # 2. Check the cleaned raw text against the list of known subjects
                        for valid_subject in sorted(VALID_SUBJECT_AREAS_English, key=len, reverse=True):
                            
                            # Create a regex pattern to match the valid subject at the start of the string,
                            # followed by a word boundary (space or end of string), ensuring we don't match 
                            # 'Computer Science' when the subject is 'Computer Science and Engineering'.
                            # The check is case-insensitive.
                            # match_pattern = re.compile(re.escape(valid_subject) + r'(\s|$)', re.IGNORECASE)
                            
                            # if match_pattern.search(subject_raw):
                            #     # Found a match! Return the correctly capitalized/formatted version from the list.
                            #     return valid_subject
                            offset=subject_raw.find(valid_subject)
                            if offset < 0:
                                continue
                            if offset == 0:
                                return valid_subject
                    else:
                        print(f"No valid subject found for {pdf_path}")
                else:
                    second_match=swedish_thesis_title_pattern.search(text_to_search)
                    if second_match:
                        print(f"{second_match.group(0)=}")
                        # 1. Clean the text to remove "Doctoral Thesis in " boilerplate
                        # subject_raw: "Mathematics Existence, uniqueness, and regularity theory for local and nonlocal problems"
                        subject_raw = thesis_title_pattern.split(text_to_search)[-1].strip()
                        if options.verbose:
                            print(f"{subject_raw=}")
                        
                        if subject_raw:
                            # 2. Check the cleaned raw text against the list of known subjects
                            for valid_subject in sorted(VALID_SUBJECT_AREAS_Swedish, key=len, reverse=True):
                                # Create a regex pattern to match the valid subject at the start of the string,
                                # followed by a word boundary (space or end of string), ensuring we don't match 
                                # 'Computer Science' when the subject is 'Computer Science and Engineering'.
                                # The check is case-insensitive.
                                match_pattern = re.compile(re.escape(valid_subject) + r'(\s|$)', re.IGNORECASE)
                            
                                if match_pattern.search(subject_raw):
                                    # Found a match! Return the correctly capitalized/formatted version from the list.
                                    return valid_subject
                        else:
                            print(f"No valid subject found for {pdf_path}")
                    

        else:
            print(f"No thesis heading found found for {pdf_path}")

    except Exception as e:
        # In a real environment, you might log this error.
        print(f"Error reading subject area: {e}")
        pass
    finally:
        # doc is mocked, so we just check for its existence in a real application context
        if doc: doc.close()
    
    return subject


def main():
    global Verbose_Flag
    global options
    global VALID_SUBJECT_AREAS
    global VALID_SUBJECT_AREAS_English
    global VALID_SUBJECT_AREAS_Swedish

    parser = optparse.OptionParser()
    parser.add_option('-v', '--verbose',
                      dest="verbose",
                      default=False,
                      action="store_true",
                      help="Print lots of output to stdout")

    parser.add_option('-t', '--testing',
                      dest="testing",
                      default=False,
                      action="store_true",
                      help="A mode for testing")

    options, remainder = parser.parse_args()
    Verbose_Flag = options.verbose

    if len(remainder) != 1:
        print("Usage: ./check_subjects_on_3rd_cycle_covers.py [-v] <dir>")
        sys.exit(1)

    directory_path = remainder[0]
    
    # --- VALID SUBJECT AREAS (provided by user for precise matching) ---
    VALID_SUBJECT_AREAS=[]
    VALID_SUBJECT_AREAS_English=[]
    VALID_SUBJECT_AREAS_Swedish=[]

    for c in third_cycle_subjects:
        if c == 'KTHXXX': # skip the fake entry
            continue
        VALID_SUBJECT_AREAS.append(third_cycle_subjects[c]['swe'])
        VALID_SUBJECT_AREAS_Swedish.append(third_cycle_subjects[c]['swe'])

        VALID_SUBJECT_AREAS.append(third_cycle_subjects[c]['eng'])
        VALID_SUBJECT_AREAS_English.append(third_cycle_subjects[c]['eng'])

    # Sort by length descending to ensure matching of longer, more specific subjects first 
    # (e.g., "Civil and Architectural Engineering" before "Civil Engineering" if that were present).
    VALID_SUBJECT_AREAS.sort(key=len, reverse=True)
    
    print(f"{VALID_SUBJECT_AREAS=}")

    # Convert the string path to a Path object
    path = Path(directory_path)
    
    file_count=0
    # Use .glob() to find all files ending in .pdf
    # Use r'**/*.pdf' if you want to search subdirectories recursively
    for pdf_file in path.glob('*.pdf'):
        file_count=file_count+1
        print(f"Processing: {pdf_file.name}")
        
        # Access properties easily:
        # pdf_file.name (filename with extension)
        # pdf_file.stem (filename without extension)
        # pdf_file.absolute() (full path)
        
        # Your processing logic goes here
        # with open(pdf_file, 'rb') as f:
        #     ...
        subject_area=get_subject_area(pdf_file.absolute())
        print(f"{subject_area=}")
    
if __name__ == "__main__":
    main()
