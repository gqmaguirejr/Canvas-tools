#!/usr/bin/python3.11
# -*- coding: utf-8 -*-
#
# ./compare_dois.py spreadsheet_file.xlsx
#
# Compares the 'DOI in Reference' and 'Crossref DOI' columns from the output
# of Crossref_HTML-to-spreadsheet.py to evaluate matching performance.
#
# G. Q. Maguire Jr. style extension
#
# 2026-05-14
#

import os
import sys
import optparse
import pandas as pd

def clean_doi(val):
    """
    Cleans a DOI string by removing NaN values, stripping whitespaces,
    removing the 'https://doi.org' prefix, and converting to lowercase.
    """
    if pd.isna(val):
        return ""
    
    s = str(val).strip()
    
    if s.startswith('https://doi.org/https://doi.org/'):
        s = s[len("https://doi.org/https://doi.org"):]

    if s.startswith("https://doi.org"):
        s = s[len("https://doi.org"):]

    if s.startswith("/"):
        s = s[1:]
        
    return s.lower()

def semi_clean_doi(val):
    """
    Cleans a DOI string by removing NaN values, stripping whitespaces,
    removing the 'https://doi.org' prefix, and converting to lowercase.
    """
    if pd.isna(val):
        return ""
    
    s = str(val).strip()
    
    if s.startswith('https://doi.org/https://doi.org/'):
        s = s[len("https://doi.org/https://doi.org"):]

    if s.startswith("https://doi.org"):
        s = s[len("https://doi.org"):]

    if s.startswith("/"):
        s = s[1:]

    if s.endswith("."):
        s = s[:-1]
        
    return s



def evaluate_doi_match(row):
    """
    Applies the verification logic scoring rules based on DOI content.
    """
    ref_doi = clean_doi(row.get('DOI in Reference', ''))
    cross_doi = clean_doi(row.get('Crossref DOI', ''))
    
    if ref_doi == "" and cross_doi == "":
        return 0
    if ref_doi != "" and cross_doi == "":
        return 1
    if ref_doi == "" and cross_doi != "":
        return 2
    if ref_doi == cross_doi:
        return 3
    
    return 4

def remove_terminal_period(val):
    """
    Removes a trailing period if the string starts with the standard prefix.
    """
    if pd.isna(val):
        return val
    s = str(val).strip()
    if s.startswith("https://doi.org") and s.endswith("."):
        return s[:-1]
    if s.startswith("10.") and s.endswith("."):
        return s[:-1]
    return val

def generate_match_comment(row):
    """
    Generates targeted diagnostic messages for entries where DOI matches is 4.
    Uses exact string matching except for the duplicate prefix structural rule.
    """
    if row.get('DOI matches') != 4:
        return ""

    # Fetch original uncleaned string values for strict exact matching, then clean
    ref_val = str(row.get('DOI in Reference', '')).strip()
    cross_val = str(row.get('Crossref DOI', '')).strip()

    # 1. Structural Prefix Rule (The only non-exact match allowed)
    if ref_val.startswith('https://doi.org/https://doi.org/'):
        return "Reference DOI has an unnecessary duplicate 'https://doi.org'"

    # 2. Strict Exact Mapping Dictionary
    exact_cases = {
        "10.1177/1070496516658753/ASSET/IMAGES/LARGE/10.1177_1070496516658753-FIG4.JPEG": "'/ASSET/IMAGES/LARGE/10.1177_1070496516658753-FIG4.JPEG' invalid in reference DOI",
        "10.3389/FENVS.2021.691523/BIBTEX": "'/BIBTEX' is invalid in the reference DOI",
        "10.3389/FENVS.2022.820125/BIBTEX": "'/BIBTEX' is invalid in the reference DOI",
        "10.1007/S10584-017-2027-8/FIGURES/4": "'/FIGURES/4' is invalid in the reference DOI",
        "10.1007/S12667-020-00420-W/FIGURES/9": "'/FIGURES/9' is invalid in the reference DOI",
        "10.1109/AERO58975.2024.10521434": "Crossref DOI is incorrect (incomplete)",
        "10.1007/BF00992698": "Crossref found the Technical Note: Q-Learning by the same authors",
        "10.3390/ma17081713": "DOI in reference is correct, the Crossref DOI is for the preprint",
        "10.26668/INDEXLAWJOURNALS/2358-1352/2021.V30I11.8422": "Reference DOI has a 'I' and not an '1' before the '11'",
        "10.1115/1.4040245/422743": "reference DOI is invalid, there is no '/422743' in the real DOI",
        "10.1126/science.aba525": "reference DOI is missing a trailing '7'",
        "10.1115/GT2011-4506": "reference DOI is missing a trailing '7'",
        "10.1177/146978740404046": "reference DOI missing a terminal '3'",
        "10.1073/pnas.12112861": "reference is missing a trailing '09'",
        "10.1007/1-4020-5742-3_": "reference DOI is missing trailing '8'",
        "10.1109/RO-MAN570194": "reference DOI is invalid, missing the later part of the Crossref DOI (which is correct)",
        "10.1007/978-3-030-47291-0": "reference DOI is invalid, while the Crossref DOI is correct",
        "10.1080/13583_883.2016.12142_86": "there are two spaces that have been inserted in the thesis reference",
        "10.1063/5.0009297/1017497": "reference DOI is invalid, Crossref DOI is correct",
        "10.3390/EN14133916/S1": "the 'S1' makes the reference DOI invalid",
        "10.2307/24987406": "reference DOI is invalid, Crossref DOI is correct, but the authors are in the opposite order from that given in the reference",
        "10.1111/j.1468-2451.2003.05502003.x": "reference DOI is correct, Crossref DOI is incorrect",
        "10.1108/MEQ-07-2021-0170/FULL/XML": "'/FULL/XML' makes the DOI invalid",
        "10.1002/pip":	"reference DOI is incomplete, Crossref DOI is correct",
        "10.1007/978-3-030-38490-6_7": "removing the curly braces and escape for the underscore in the reference DOI produces the correct DOI, Crossref DOI is for something else",
        "10.1007/978-1-4471-5451-8_116": "removing the curly braces and escape for the underscore in the reference DOI produces the correct DOI, Crossref DOI is for something else",
        "10.1007/978-3-031-34906-5_7": "removing the curly braces and escape for the underscore in the reference DOI produces the correct DOI, Crossref DOI is for something else",
        "10.1016/j.forpol.2015.10.012": "reference DOI is correct, Crossref DOI is incorrect",
        "10.3316/informit.609093216085752": "reference DOI is invalid, Crossref DOI is correct",
        "10.1604/9780080455730": "reference DOI is invalid, this should be the book with ISBN: 978-0-12-566251-2 with https://doi.org/10.1016/B978-0-12-566251-2.X5000-X; the Crossref DOI is to a review of the book",
        "10.1145/1240866": "reference DOI refers to all of the extended abstracts, Crossref DOI is to the specific abstract being cited",
        "10.1007/978-1-4615-4201-8": "reference DOI is for the whole book, while the Crossref DOI is for the chapter with the indicated title",
        "10.1007/978-3-030-29384-0": "reference DOI refers to the whole book, while the Crossref DOI refers to the specific chapter cited.",
        "10.1145/3532106": "reference DOI refers to the whole proceedings, while the Crossref DOI refers to the specific paper cited.",
        "10.2307/1251307": "reference DOI redirects to the same landing page as the Crossref DOI",
        "10.2307/1251126": "reference DOI redirects to the same landing page as the Crossref DOI",
        "10.2307/1249496": "reference DOI redirects to the same landing page as the Crossref DOI",
        "10.2307/1251983":  "reference DOI redirects to the same landing page as the Crossref DOI",
        "10.1016/j.ijpe.2023.108120": "reference DOI is invalid, Crossref DOI is correct",
        "10.1016/j.trip.2020.100165": "reference DOI is invalid, missing training '5'",
        "DOI:10.1111/jir.12097": "reference DOI has an unnecessary 'DOI:' in the URL",
        "doi:10.1136/bmj-2022-071531": "reference DOI has an unnecessary 'doi:' in the URL",
        "doi:10.18549/PharmPract.2020.2.1927": "reference DOI has an unnecessary 'doi:' in the URL",
        "10.1007/978-3-030-77641-1_4": "reference DOI is to the preprint, while Crossref DOI is to the published paper",
        "10.1177/0306312717709363/SUPPL_FILE/SUPPLEMENTARY_MATERIAL.PDF": "'/SUPPL_FILE/SUPPLEMENTARY_MATERIAL.PDF' in the reference DOI makes it invalid",
        "10.18653/v1/2023.emnlp-main.568": "reference DOI is to the preprint, while Crossref DOI is to the published paper",
        "http://doi.org/10.1615/JWomenMinorScienEng.2022041001": "reference DOI uses 'http:*' rather than 'https:*'",
        "10.1016/0368-2048(88)80012-6": "reference DOI is invalid, Crossref DOI is correct, i.e., trailing '80012-6' should be '85010-2'",
        "10.1002/anie.201104268": "reference DOI is invalid, Crossref DOI is correct, i.e., trailing '4268' should be '3616'",
        "10.48550/arXiv.2411.17616": "reference DOI is correct, Crossref DOI is incorrect",
        "10.1023/A:1022864513654/METRICS": "'/METRICS' in the reference DOI makes it invalid",
        "10.1002/smj.863": "reference DOI invalid, missing trailing '.863'",
        "10.1007/BF02766777": "reference DOI in incorrect, Crossref DOI is correct",
        "10.1002/smj.2247": "reference DOI invalid, missing trailing '.2247'",
        "10.1002/smj.2000":  "reference DOI invalid, missing trailing '.2000'",
        "10.1002/hrdq.20063": "reference DOI invalid, missing trailing '.20063'",
        "10.1002/smj.2078": "reference DOI invalid, missing trailing '.2078'",
        "10.5465/amj.2007.24160882": "reference DOI is incorrect, Crossref DOI is correct",
        "10.1002/smj.640": "reference DOI invalid, missing trailing '.640'",
        "10.1002/(SICI)1097-0266(199708)18:7<509::AID-SMJ882>3.0.CO;2-Z": "reference DOI is to a reprint in Essays in Technology Management and Policy, pp. 77-120 (2003), while the Crossref DOI is the original publication - and the journal, volume, issues, and pages used in the reference",
        "10.1177/014920630102700607": "reference DOI and Crossref DOI take you to the same landing page https://journals.sagepub.com/doi/10.1177/014920630102700607",
        "info:doi/10.14512/gaia.23.S1.4": "reference DOI has an unnecessary 'info:doi' in it",
        "10.1016/S0140-6736(19)32989-7": "references [3] and [4] are duplicates but [4] is more complete",
        "10.7208/chicago/9780226226767.001.0001": "reference DOI is invalid, Crossref DOI is correct",
        "10.1136/ bmjgh-2018-000895": "reference DOI as a space in it, making it invalid (the URL link in the document only has 'https://doi.org/10.1136/'",
        "10.1016/C2023-0-013942": "reference DOI is invalid, Crossref is correct",
        "10.1089=apc.2009.0050": "reference DOI has an '=' that should be a '/'",
        "10.1007/978-3-030-70924-2{\_}12":  "removing the curly braces and escape for the underscore in the reference DOI produces the correct DOI, Crossref DOI is for something else",
        "10.1051/0004-6361/202554494": "reference DOI is the preprint, Crossref DOI is the published paper",
        "10.1007/s12369-020-00683-1": "reference DOI is invalid, Crossref DOI is correct",
        "10.1007/S10704-009-93641/METRICS": "reference DOI is invalid, Crossref DOI is correct",
        "10.12759/hsr.37.2012.4.64-75": "reference DOI is correct, Crossref DOI is for something else",
        "10.23943/9781400844623": "reference DOI is invalid, Crossref DOI is correct",
        "10.1109/ICCV48922.2021.00986": "reference DOI is the preprint, Crossref DOI is the published paper",
        "10.1109/CVPR.2019.00712": "reference DOI is the preprint, Crossref DOI is the published paper",
        "10.1109/LRA.2025.1234567": "reference DOI is invalid and seems like a place holder, Crossref DOI is to an unrelated publication in volume 10 number 10 of journal",
        "10.1109/SCCC.2007.4": "reference DOI is to the 'Forword' of the conference proceedings, the paper is actually at the Crossref DOI, i.e., 10.1109/SCCC.2007.12",
        "10.5281/zenodo.10796440": "reference DOI is correctly for the artifact, while the Crossref DOI is for the paper and not the artifact (which this reference is about)",
        "10.33774/coe-2025-lj1mm": "reference DOI is correct, Crossref DOI resolves to the SSRN version of the same publication",
        "10.1002/(SICI)1099-1727(199623)12:3<183::AID-SDR103>3.0.CO;2-4": "while the reference DOI would seem to be escaped version of the Crossref DOI; the escaped version in invalid is because of Percent-Encoding Over-correction (or double-encoding) within the URL string",
        "10.1007/978-1-4471-7475-2": "reference DOI is to the 2020 edition of the book, while the Crossref DOI is for the 2009 edition -- the reference is for the year 2009, so the reference DOI is incorrect, while the Crossref DOI is the correct DOI for this reference",
        "10.1007/978-3-319-73374-610": "reference DOI is invalid (as is the link in the PDF file), Crossre DOI is correct",
        "10.1007/978-3-030-62219-0_5": "reference DOI is to the whole book, while the Crossref DOI is to the correct chapter that is being referenced",
        "10.1016/0277-5395(83)90035-3": "referenced DOI is missing the trailing '3'",
        "10.1177/001872679404700602": "referenced DOI is missing the trailing '02' that is in the PDF link and is correctly in the Crossref DOI",
        "doi:10.18261/ISSN1890-2146-2006-01-03": "referenced DOI has an unnecessary 'doi:' in it",
        "10.31399/asm.hb.v10.a0001763": "reference DOI invalid as it is missing the periods that are in the Crossref DOI",
        "10.1140/epjh/e2016-70031-7": "reference DOI is invalid, Crossref DOI is correct",
        "10.1021/jp101387c": "reference DOI is invalid, Crossref DOI is correct",
        "10.1021/jp100476g": "reference DOI is invalid, Crossref DOI is correct",
        "10.1016/S0921-5093(99)00486-0": "reference DOI is invalid, Crossref DOI is correct",
        "10.1007/s13412-020-00669-1": "reference DOI is invalid, Crossref DOI is correct",
        "10.1046/j.1475-1313.2001.00606.x": "reference DOI is correct, Crossref DOI is for a version of the same publication in Wiley Online Library",
        "10.48550/arXiv.1910.04209": "reference DOI is the preprint, Crossref DOI is the published paper",
        "10.1007/1-4020-5742-3_8": "reference DOI is missing the trailing '_8'",
        "10.5281/zenodo.14956750": "reference DOI is correct, the 10.1088/2515-7620/adc65a is the published paper",
        "10.1088/2515-7620/adc65a": "reference DOI is correct, the 10.1088/2515-7620/adc65a is the published paper",
        "10.1177/1468794112468475": "reference DOI is invalid, it is missing the trailing '75'",
        "10.59670/ml.v14i2.326": "reference DOI is invalid as is the Crossref DOI",
        "10.1023/A:1024409931608": "reference DOI is invalid, Crossref DOI is valid, but for a different title than the reference",
        
    }

    # semi_clean the DOIs, i.e., do not convert to lower-case
    ref_val = semi_clean_doi(ref_val)
    cross_val = semi_clean_doi(cross_val)

    if ref_val in exact_cases:
        return exact_cases[ref_val]
        
    if cross_val in exact_cases:
        return exact_cases[cross_val]

    return "DOI conflict detected (mismatch type 4)"

def main():
    parser = optparse.OptionParser()
    parser.add_option('-v', '--verbose',
                      dest="verbose",
                      default=False,
                      action="store_true",
                      help="Print execution details to stdout")

    options, remainder = parser.parse_args()
    verbose_flag = options.verbose

    if len(remainder) < 1:
        print("Usage: python compare_dois.py <Spreadsheet_input_file>")
        sys.exit(1)

    input_file = remainder[0]
    
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found.")
        sys.exit(1)

    if input_file.endswith('.xlsx'):
        df = pd.read_excel(input_file)
    else:
        df = pd.read_csv(input_file)

    required_columns = ["DOI in Reference", "Crossref DOI"]
    for col in required_columns:
        if col not in df.columns:
            print(f"Error: Required column '{col}' is missing.")
            sys.exit(1)

    if verbose_flag:
        print(f"Analyzing {len(df)} entries from '{input_file}'...")

    # 1. Clean trailing periods
    df['DOI in Reference'] = df['DOI in Reference'].apply(remove_terminal_period)

    # 2. Evaluate base codes (0-4)
    df['DOI matches'] = df.apply(evaluate_doi_match, axis=1)

    # 3. Apply custom comments block for mismatch type 4
    df['match comments'] = df.apply(generate_match_comment, axis=1)

    # Construct output filename
    base_name, ext = os.path.splitext(input_file)
    output_file = f"{base_name}-matched{ext}"

    if output_file.endswith('.xlsx'):
        df.to_excel(output_file, index=False)
    else:
        df.to_csv(output_file, index=False, encoding='utf-8-sig')

    print(f"Successfully processed entries and saved to: {output_file}")

if __name__ == "__main__":
    main()
