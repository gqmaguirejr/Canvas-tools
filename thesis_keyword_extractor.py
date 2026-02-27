#!/usr/bin/python3.11
# -*- coding: utf-8 -*-
#
# thesis_keyword_extractor.py PDF_file
#
# Purpose: Thesis Keyword Suggestion Tool
#
# with option '-v' use verbose output
# with option '-s' consider Swedish words
#
# G. Q. Maguire Jr. + help of Gemini 3 Pro
#
# 2025-12-02
#

import warnings
# Suppress specific sklearn UserWarnings using regex matching
warnings.filterwarnings("ignore", category=UserWarning, message=r".*token_pattern.*")
warnings.filterwarnings("ignore", category=UserWarning, message=r".*stop_words.*inconsistent.*")

from sklearn.feature_extraction.text import CountVectorizer
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from collections import Counter, defaultdict

import optparse
import sys
import pymupdf  # PyMuPDF
import re
import nltk
import unicodedata # Added for character normalization
import json
import importlib

# Add path to custom modules
#sys.path.append('/home/maguire/Canvas-tools')
sys.path.append('/z3/maguire/Canvas/Canvas-tools')  # Include the path to module_folder
#sys.path.append('/home/maguire/Canvas/Canvas-tools')

# Attempt to import custom modules
try:
    import common_english
    import common_swedish
    import common_acronyms
    import AVL_words_with_CEFR
    import common_bosnian
    import common_danish
    import common_dutch
    import common_estonian
    import common_finnish
    import common_french
    import common_german
    import common_greek
    import common_icelandic
    import common_italian
    import common_japanese
    import common_latin
    import common_norwegian
    import common_portuguese
    import common_russian
    import common_spanish
    import common_turkish

except ImportError:
    # Fallback to prevent crash if running elsewhere
    common_english = None
    common_swedish = None
    common_acronyms = None
    AVL_words_with_CEFR = None
    common_bosnian = None
    common_danish = None
    common_dutch = None
    common_estonian = None
    common_finnish = None
    common_french = None
    common_german = None
    common_greek = None
    common_icelandic = None
    common_italian = None
    common_japanese = None
    common_latin = None
    common_norwegian = None
    common_portuguese = None
    common_russian = None
    common_spanish = None
    common_turkish = None


# Ensure necessary NLTK data is downloaded
try:
    nltk.data.find('corpora/stopwords')
    nltk.data.find('corpora/wordnet')
    nltk.data.find('tokenizers/punkt')
except LookupError:
    # Only print if we are actually downloading to avoid noise
    # print("Downloading necessary NLTK data...") 
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)
    nltk.download('omw-1.4', quiet=True)
    nltk.download('punkt', quiet=True)

Verbose_Flag = False

# Global variable to store loaded standardized terms
STANDARDIZED_TERMS = {}

# config_file=
def load_standardized_terms(config_file="subject_area_config.json"):
    """
    Loads configuration and standardized term lists from a JSON file.
   
    """
    global STANDARDIZED_TERMS
    global Verbose_Flag

    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
            STANDARDIZED_TERMS = config
            if Verbose_Flag:
                print(f"Loaded configuration for {len(config.get('all_dicts', {}))} term dicts.")
    except FileNotFoundError:
        print(f"WARNING: Configuration file '{config_file}' not found. No standardized terms loaded.")
    except json.JSONDecodeError as e:
        print(f"ERROR: Failed to parse JSON configuration: {e}")


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
   
    # Sort by length descending to ensure matching of longer, more specific subjects first 
    # (e.g., "Civil and Architectural Engineering" before "Civil Engineering" if that were present).
    VALID_SUBJECT_AREAS.sort(key=len, reverse=True)
    
    try:
        doc = pymupdf.open(pdf_path)

        # Search page 1 (index 0) and page 2 (index 1)
        for pageno in range(min(2, doc.page_count)):
            blocks = doc[pageno].get_text("blocks", sort=True)
            
            for (x0, y0, x1, y1, block_text, block_no, block_type) in blocks:
                
                if options.verbose:
                    print(f"GQM: {block_text=}, {block_no=}, {block_type=}")
                # Normalize the block text: replace newlines with spaces and strip
                # Example: "Doctoral Thesis in Mathematics Existence, uniqueness, and regularity theory for local and nonlocal problems"
                text_to_search = block_text.replace('\n', ' ').strip()
                
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


def extract_text_from_pdf(pdf_path):
    """
    Extracts all text from a PDF file using PyMuPDF, returning a list of pages.
    """
    pages = []
    try:
        with pymupdf.open(pdf_path) as doc:
            # Iterate over all pages
            for page in doc:
                page_text = page.get_text()
                if page_text:
                    pages.append(page_text)
    except FileNotFoundError:
        print(f"Error: The file '{pdf_path}' was not found.")
        return []
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return []
    
    return pages

def clean_text_structural(text):
    """
    Performs structural cleaning (ligatures, hyphens, compounds) 
    BUT preserves case and non-alpha characters for now.
    """
    # --- NEW: Normalization and Accent Fixing ---
    
    # 1. Apply NFC to compose "space + combining" into "spacing modifier"
    # This is critical for inputs like "B \u0301enard" -> "B\u00B4enard" (merges space+accent)
    text = unicodedata.normalize('NFC', text)

    # 2. Fix Legacy/Spacing Accents (e.g. "B´enard" -> "Bénard")
    # Using a callback allows us to handle any letter case dynamically
    def merge_accent(match):
        acc, letter = match.groups()
        # Map spacing accents (often found in LaTeX PDFs) to combining diacritics
        combine_map = {
            '\u00B4': '\u0301', # Acute ´
            '`': '\u0300',      # Grave `
            '¨': '\u0308',      # Diaeresis ¨
            '^': '\u0302',      # Circumflex ^
            '~': '\u0303'       # Tilde ~
        }
        if acc in combine_map:
            # Combine letter + diacritic and normalize to precomposed char (e.g. 'e' + '́' -> 'é')
            return unicodedata.normalize('NFKC', letter + combine_map[acc])
        return match.group(0)

    # Regex matches: spacing accent + optional whitespace + letter
    # \u00B4 is the specific 'acute accent' often distinct from single quote
    text = re.sub(r'([\u00B4`¨^~])\s*([a-zA-Z])', merge_accent, text)

    # 3. Standard Unicode Normalization (NFKC)
    # Run AFTER manual accent fixing to ensure consistency
    text = unicodedata.normalize('NFKC', text)

    # --- End Accent Fixing ---

    # 4. Fix PDF Ligatures using comprehensive table
    ligature_table = {
        '\ufb00': 'ff', # 'ﬀ'
        '\ufb03': 'ffi', # 'ﬃ'
        '\ufb04': 'ffl', # 'ﬄ'
        '\ufb01': 'fi', # 'ﬁ'
        '\ufb02': 'fl', # 'ﬂ'
        '\ua732': 'AA', # 'Ꜳ'
        '\ua733': 'aa', # 'ꜳ'
        '\u00c6': 'AE', # 'Æ'
        '\u00e6': 'ae', # 'æ'
        '\uab31': 'aə', # 'ꬱ'
        '\ua734': 'AO', # 'Ꜵ'
        '\ua735': 'ao', # 'ꜵ'
        '\ua736': 'AU', # 'Ꜷ'
        '\ua737': 'au', # 'ꜷ'
        '\ua738': 'AV', # 'Ꜹ'
        '\ua739': 'av', # 'ꜹ'
        '\ua73a': 'AV', # 'Ꜻ'  - note the bar
        '\ua73b': 'av', # 'ꜻ'  - note the bar
        '\ua73c': 'AY', # 'Ꜽ'
        '\ua76a': 'ET', # 'Ꝫ'
        '\ua76b': 'et', # 'ꝫ'
        '\uab41': 'əø', # 'ꭁ'
        '\u01F6': 'Hv', # 'Ƕ'
        '\u0195': 'hu', # 'ƕ'
        '\u2114': 'lb', # '℔'
        '\u1efa': 'IL', # 'Ỻ'
        '\u0152': 'OE', # 'Œ'
        '\u0153': 'oe', # 'œ'
        '\ua74e': 'OO', # 'Ꝏ'
        '\ua74f': 'oo', # 'ꝏ'
        '\uab62': 'ɔe', # 'ꭢ'
        '\u1e9e': 'SS', # 'ẞ'
        '\u00df': 'ss', # 'ß'
        '\ufb06': 'st', # 'ﬆ'
        '\ufb05': 'ſt', # 'ﬅ'  -- long ST
        '\ua728': 'Tz', # 'Ꜩ'
        '\ua729': 'tz', # 'ꜩ'
        '\u1d6b': 'ue', # 'ᵫ'
        '\uab63': 'uo', # 'ꭣ'
        '\ua760': 'VY', # 'Ꝡ'
        '\ua761': 'vy', # 'ꝡ'
    }
    
    for search, replace in ligature_table.items():
        text = text.replace(search, replace)

    # Expand common abbreviations (titles, months) using abbreviations_map
    text=replace_abbreviations(text)

    # 5. Fix hyphenation at line endings (e.g., "Sen- \n sing" -> "Sensing")
    # \w matches Unicode word characters (letters, numbers, underscore)
    text = re.sub(r'(\w+)-\s+(\w+)', r'\1\2', text)
    
    # 6. Preserve compound words by replacing hyphens with underscores
    # Matches hyphens bounded by Unicode letters (excludes digits and underscores via [^\W\d_])
    text = re.sub(r'(?<=[^\W\d_])-(?=[^\W\d_])', '_', text)
    
    return text

def build_case_frequency_map(pages):
    """
    Scans the original text to build a frequency map of case variations.
    Returns: defaultdict(Counter) where key is lowercase word, 
             value is Counter({'Word': 10, 'word': 5})
    """
    case_map = defaultdict(Counter)
    
    for page in pages:
        # Perform structural cleaning only (keep case, keep punctuation for now)
        text = clean_text_structural(page)
        
        # Remove standalone numbers (keep alphanumeric)
        text = re.sub(r'\b\d+\b', ' ', text)
        
        # Remove non-word characters (punctuation, symbols) but keep whitespace
        # [^\w\s] matches anything that isn't a word char (letter/number/_) or whitespace
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Remove short words (1-2 chars)
        # [^\W\d_] matches any word character that is NOT a digit and NOT an underscore (i.e. letters)
        text = re.sub(r'\b[^\W\d_]{1,2}\b', ' ', text)
        
        # Tokenize by splitting on whitespace
        tokens = text.split()
        
        for token in tokens:
            lower_key = token.lower()
            case_map[lower_key][token] += 1
            
    return case_map

def preprocess_text(text):
    """
    Standard preprocessing for CountVectorizer (lowercase).
    """
    # 1. Structural cleaning (Ligatures, hyphens, underscores)
    text = clean_text_structural(text)

    # 2. Convert to lowercase
    text = text.lower()
    
    # 3. Remove standalone numbers (BUT keep alphanumerics like "Graph2Feat")
    text = re.sub(r'\b\d+\b', ' ', text)
    
    # 4. Remove special characters/punctuation (BUT keep spaces and underscores)
    # [^\w\s] removes anything that isn't a word char (letter/number/_) or whitespace
    # Since we only removed standalone digits in step 3, this effectively keeps alphanumerics and underscores
    text = re.sub(r'[^\w\s]', ' ', text)
    
    # 5. Remove short words (1-2 characters)
    # [^\W\d_] ensures we match only letters (Unicode aware)
    text = re.sub(r'\b[^\W\d_]{1,2}\b', ' ', text)
    
    # 6. Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

class LemmaTokenizer:
    """
    Custom tokenizer that uses NLTK's WordNetLemmatizer.
    """
    def __init__(self):
        self.wnl = WordNetLemmatizer()
    def __call__(self, doc):
        return [self.wnl.lemmatize(t) for t in nltk.word_tokenize(doc)]

def restore_case(token, case_map):
    """
    Restores case for a single token based on observed frequencies.
    """
    # Get all observed variations for this lowercase token
    variations = case_map.get(token.lower(), Counter())
    
    # If word wasn't found (unlikely) or only 1 variation exists, return it
    if not variations:
        return token
        
    # Find the single most common variation
    most_common_variant, most_common_count = variations.most_common(1)[0]
    
    # Check User Rule: "Use the most common" 
    # BUT break ties in favor of lowercase (e.g. "The" vs "the", prefer "the")
    
    lower_v = token.lower()
    if lower_v in variations:
        lower_count = variations[lower_v]
        # If lowercase is equally common or more common, use it.
        # This prevents "The" (50) vs "the" (50) -> returning "The" randomly.
        if lower_count >= most_common_count:
            return lower_v
    
    # Otherwise return the clear winner (e.g. "Bénard": 12 vs "bénard": 1 -> "Bénard")
    return most_common_variant

def old_get_top_features(corpus, case_map, ngram_range, top_n=15):
    global options
    """
    Extracts top features and restores case using the frequency map.
    """
    wnl = WordNetLemmatizer()
    
    # Custom stop words list
    base_stop_words = list(stopwords.words('english'))

    academic_noise = [
        'figure', 'table', 'chapter', 'section', 'thesis', 'dissertation',
        'result', 'results', 'conclusion', 'conclusions', 'methodology', 
        'study', 'analysis', 'based', 'using', 'used', 'data', 'research', 
        'model', 'page', 'university', 'abstract', 'introduction',
        'et', 'al', 'pp', 'vol', 'no', 'doi', 'ieee', 'isbn', 'issn',
        'conference', 'proceedings', 'journal', 'http', 'https', 'www',
        'shown', 'show', 'seen', 'see', 'also', 'however', 'therefore',
        'contribution', 'key', 'proposed', 'approach', 'problem', 'performance',
        'value', 'parameter', 'time', 'system', 'case', 'example',
        'sample', 'frequency', 'fig', 'eq', 'equation', 'simulation', 'experiment',
        # Added web artifacts to stop list
        'org', 'com', 'net', 'edu', 'gov',
        # some more to remove
        'preprint', 'arxiv'
    ]
    base_stop_words.extend(academic_noise)
    
    if options.swedish:
        base_stop_words.extend(stopwords.words('swedish'))

    lemmatized_stop_words = [wnl.lemmatize(w) for w in base_stop_words]
    lemmatized_stop_words = list(set(lemmatized_stop_words))

    # Initialize Vectorizer
    vectorizer = CountVectorizer(
        tokenizer=LemmaTokenizer(),
        stop_words=lemmatized_stop_words,
        ngram_range=ngram_range, 
        max_df=0.95,
        min_df=2
    )

    try:
        X = vectorizer.fit_transform(corpus)
        feature_names = vectorizer.get_feature_names_out()
        
        dense = X.todense()
        term_counts = dense.sum(axis=0).tolist()[0]
        
        keyword_counts = list(zip(feature_names, term_counts))
        sorted_keywords = sorted(keyword_counts, key=lambda x: x[1], reverse=True)
        
        final_keywords = []
        for word, count in sorted_keywords:
            clean_word = word.replace('_', '-')
            
            # Split tokens to restore case individually
            # capturing delimiters in split keeps them in the list
            tokens = re.split(r'([-\s])', clean_word)
            restored_tokens = []
            
            for token in tokens:
                # Only attempt restoration on actual words (not delimiters)
                if token.strip() and token.replace('-', '').isalnum():
                    restored_tokens.append(restore_case(token, case_map))
                else:
                    restored_tokens.append(token)
            
            restored_word = "".join(restored_tokens)
            final_keywords.append((restored_word, count))
            
        return final_keywords[:top_n]
    except ValueError:
        return []

# Create a simple word tokenizer as a fallback
def word_tokenizer(text):
    return re.findall(r'\b\w\w+\b', text.lower())

def get_top_features(corpus, case_map, ngram_range, top_n=15):
    global options
    wnl = WordNetLemmatizer()
    
    # 1. Expand Noise List with specific ghost fragments found in your output
    # These are fragments typically created by over-lemmatization or OCR errors
    ghost_fragments = ['ho', 'ans', 'ha', 'hu', 'as', 'la', 'le', 'un', 'une']
    
    base_stop_words = list(stopwords.words('english'))
    if options.swedish:
        base_stop_words.extend(stopwords.words('swedish'))
        
    academic_noise = [
        'figure', 'table', 'chapter', 'section', 'thesis', 'dissertation',
        'result', 'results', 'conclusion', 'conclusions', 'methodology', 
        'study', 'analysis', 'based', 'using', 'used', 'data', 'research', 
        'model', 'page', 'university', 'abstract', 'introduction',
        'et', 'al', 'pp', 'vol', 'no', 'doi', 'ieee', 'isbn', 'issn',
        'conference', 'proceedings', 'journal', 'http', 'https', 'www',
        'shown', 'show', 'seen', 'see', 'also', 'however', 'therefore',
        'contribution', 'key', 'proposed', 'approach', 'problem', 'performance',
        'value', 'parameter', 'time', 'system', 'case', 'example',
        'sample', 'frequency', 'fig', 'eq', 'equation', 'simulation', 'experiment',
        'org', 'com', 'net', 'edu', 'gov', 'preprint', 'arxiv',

    ]
    
    base_stop_words.extend(academic_noise)

    if not options.no_lemma:
        base_stop_words.extend(ghost_fragments)
    
    lemmatized_stop_words = list(set([wnl.lemmatize(w.lower()) for w in base_stop_words]))

    if options.no_lemma:
        vectorizer = CountVectorizer(
            tokenizer=word_tokenizer,
            stop_words=base_stop_words,
            ngram_range=ngram_range, 
            max_df=0.95,
            min_df=2
        )
    else:
        vectorizer = CountVectorizer(
            tokenizer=LemmaTokenizer(),
            stop_words=lemmatized_stop_words,
            ngram_range=ngram_range, 
            max_df=0.95,
            min_df=2
        )

    try:
        X = vectorizer.fit_transform(corpus)
        feature_names = vectorizer.get_feature_names_out()
        term_counts = X.todense().sum(axis=0).tolist()[0]
        keyword_counts = list(zip(feature_names, term_counts))
        
        # 2. Refined Filtering
        final_keywords = []
        sorted_keywords = sorted(keyword_counts, key=lambda x: x[1], reverse=True)
        
        # 3. Aggregating "Known" Small Words (The "Shield" set)
        # We combine keys from all three of your dictionaries
        known_small_words = set()
    
        # Dictionary Sources to check
        sources = [
            (common_english, 'common_English_words'),
            (common_english, 'thousand_most_common_words_in_English'),
            (common_swedish, 'common_swedish_words'),
            (common_english, 'common_french_words'),
            (common_bosnian, 'common_bosnian_words'),
            (common_danish, 'common_danish_words'),
            (common_dutch, 'common_dutch_words'),
            (common_estonian, 'common_estonian_words'),
            (common_finnish, 'common_finnish_words'),
            (common_german, 'common_german_words'),
            (common_greek, 'common_greek_words'),
            (common_icelandic, 'common_icelandic_words'),
            (common_italian, 'common_italian_words'),
            (common_japanese, 'common_japanese_words'),
            (common_latin, 'common_latin_words'),
            (common_norwegian, 'common_norwegian_words'),
            (common_portuguese, 'common_portuguese_words'),
            (common_russian, 'common_russian_words'),
            (common_spanish, 'common_spanish_words'),
            (common_turkish, 'common_turkish_words'),
            (common_english, 'common_units'),
            (common_english, 'chemical_elements_symbols'),
            (common_english, 'chemical_elements'),
            (common_english, 'chemical_names_and_formulas'),
            (common_english, 'company_and_product_names'),
            (common_english, 'common_programming_languages'),
        ]
    
        for module, attr in sources:
            # Safely extract keys if the attribute exists
            data = getattr(module, attr, {})
            if isinstance(data, dict):
                known_small_words.update(data.keys())
            elif isinstance(data, (list, set, tuple)):
                known_small_words.update(data)

        for word, count in sorted_keywords:
            clean_word = word.replace('_', '-')
            lower_word = clean_word.lower()

            # REJECTION LOGIC:
            # Reject if it's in our specific ghost list
            if lower_word in ghost_fragments:
                continue
                
            # SPECIAL HANDLING FOR 2-LETTER WORDS:
            if len(clean_word) <= 2:
                # If it's a known symbol/acronym (from your list), KEEP IT
                if clean_word in known_small_words or clean_word.isupper():
                    pass 
                # If it's not known and not an Acronym, it's likely noise
                elif lower_word not in known_small_words:
                    continue

            # Case restoration logic
            tokens = re.split(r'([-\s])', clean_word)
            restored_tokens = [restore_case(t, case_map) if t.strip() and t.replace('-', '').isalnum() else t for t in tokens]
            restored_word = "".join(restored_tokens)
            
            final_keywords.append((restored_word, count))
            
            if len(final_keywords) >= top_n:
                break
                
        return final_keywords
        
    except ValueError:
        return []

def get_cefr_level(phrase):
    """
    Attempts to retrieve the CEFR level for a phrase from common_english 
    and AVL_words_with_CEFR modules.
    """
    global options
    global name_category_dict
    global exact_name_category_dict
    
    if common_english is None:
        return ""

    phrase_lower = phrase.lower()
    valid_levels = {'A1', 'A2', 'B1', 'B2', 'C1', 'C2'}
    
    if phrase in common_english.ordinals_list:
        return f"B1 Number (ordinal)"

    p_name=cefr_from_exact_match(phrase, exact_name_category_dict)
    if p_name:
        return p_name

    p_name=check_proper_name(phrase, name_category_dict)
    if p_name:
        return p_name

    # List of dictionaries to check in the module
    dicts_to_check = [
        'common_English_words',
        'top_100_English_words',
        'thousand_most_common_words_in_English',
        'chemical_elements_symbols',
        'chemical_names_and_formulas',
        'chemical_elements',
        'KTH_ordbok_English_with_CEFR',
        'common_units',
        'AVL_words_with_CEFR',
    ]

    for dict_name in dicts_to_check:
        vocab = getattr(common_english, dict_name, {})
        
        # Check if attribute is a dictionary
        if not isinstance(vocab, dict):
            continue

        # Check 1: Try exact match (e.g. "Brownian motion")
        entry = vocab.get(phrase)
        if entry and isinstance(entry, dict):
            for key in entry:
                # Use slicing [:2] to match 'C1' from 'C1 (Specialized)'
                if len(key) >= 2 and key[:2] in valid_levels:
                    return key

        # Check 2: Try lowercase match (e.g. "construction")
        entry = vocab.get(phrase_lower)
        if entry and isinstance(entry, dict):
            # Find key that looks like a CEFR level (A1-C2)
            for key in entry:
                # Use slicing [:2] to match 'C1' from 'C1 (Specialized)'
                # This ensures we match 'C1' against the set valid_levels
                if len(key) >= 2 and key[:2] in valid_levels:
                    return key
                    
    dicts_to_check = {
        'common_dutch_words': common_dutch,
        'common_estonian_words': common_estonian,
        'common_french_words': common_french,
        'common_finnish_words': common_finnish,
        'common_german_words': common_german,
        'common_greek_words': common_greek,
        'common_icelandic_words': common_icelandic,
        'common_italian_words': common_italian,
        'common_japanese_words': common_japanese,
        'common_latin_words': common_latin,
        'common_portuguese_words': common_portuguese,
        'common_russian_words': common_russian,
        'common_spanish_words': common_spanish,
        'common_turkish_words': common_turkish,
        'common_danish_words': common_danish,
        'common_bosnian_words': common_bosnian,
        'common_norwegian_words': common_norwegian,
    }

    for dict_name in dicts_to_check:
        vocab = getattr(dicts_to_check[dict_name], dict_name, {})
        
        # Check if attribute is a dictionary
        if not isinstance(vocab, dict):
            continue

        # Check 1: Try exact match (e.g. "Brownian motion")
        entry = vocab.get(phrase)
        if entry and isinstance(entry, dict):
            for key in entry:
                # Use slicing [:2] to match 'C1' from 'C1 (Specialized)'
                if len(key) >= 2 and key[:2] in valid_levels:
                    return key

        # Check 2: Try lowercase match (e.g. "construction")
        entry = vocab.get(phrase_lower)
        if entry and isinstance(entry, dict):
            # Find key that looks like a CEFR level (A1-C2)
            for key in entry:
                # Use slicing [:2] to match 'C1' from 'C1 (Specialized)'
                # This ensures we match 'C1' against the set valid_levels
                if len(key) >= 2 and key[:2] in valid_levels:
                    return key


    if options.swedish or True:
        # List of dictionaries to check in the module
        dicts_to_check = [
            'common_swedish_words',
            'common_swedish_technical_words',
            'KTH_ordbok_Swedish_with_CEFR',
        ]


        for dict_name in dicts_to_check:
            vocab = getattr(common_swedish, dict_name, {})
        
            # Check if attribute is a dictionary
            if not isinstance(vocab, dict):
                continue
        
            # Check 1: Try exact match (e.g. "Brownian motion")
            entry = vocab.get(phrase)
            if entry and isinstance(entry, dict):
                for key in entry:
                    # Use slicing [:2] to match 'C1' from 'C1 (Specialized)'
                    if len(key) >= 2 and key[:2] in valid_levels:
                        return key

            # Check 2: Try lowercase match (e.g. "construction")
            entry = vocab.get(phrase_lower)
            if entry and isinstance(entry, dict):
                # Find key that looks like a CEFR level (A1-C2)
                for key in entry:
                    # Use slicing [:2] to match 'C1' from 'C1 (Specialized)'
                    # This ensures we match 'C1' against the set valid_levels
                    if len(key) >= 2 and key[:2] in valid_levels:
                        return key

    # Check Acronyms (Exact match including case + plurals)
    acronyms_list = getattr(common_acronyms, 'well_known_acronyms_list', [])
    if isinstance(acronyms_list, list):
        for entry in acronyms_list:
            if not entry:
                continue
            acrn = entry[0] # The acronym string
            
            # Check strict exact match
            if phrase == acrn:
                return "Acronym"
            
            # Check plural 's' (e.g. APIs)
            if phrase == acrn + 's':
                return "Acronym"
            
            # Check plural 'es' (e.g. SMSes) - typically if acronym ends in 's'
            if phrase == acrn + 'es':
                return "Acronym"


    # if the word has single right quote mark (such as "l’art"), then replace it with a single quote and try again
    if "’" in phrase:
        phrase=phrase.replace("’", "'")
        return get_cefr_level(phrase)
    return ""

def print_keyword_clusters(all_keywords):
    """
    Groups keywords by common root words to suggest 'Umbrella Terms'.
    Includes CEFR level column aligned.
    """
    groups = defaultdict(list)
    # Extract significant tokens (len > 3) from all phrases
    all_tokens = []
    for phrase, count in all_keywords:
        tokens = phrase.split()
        all_tokens.extend([t.lower() for t in tokens if len(t) > 3])
    
    # Identify common stems (words appearing in more than one phrase)
    common_stems = [word for word, count in Counter(all_tokens).items() if count > 1]
    
    # Assign phrases to groups
    for stem in common_stems:
        for phrase, count in all_keywords:
            if stem in phrase.lower().split():
                groups[stem].append((phrase, count))
    
    # Sort groups by total frequency
    sorted_groups = sorted(groups.items(), key=lambda x: sum(c for p,c in x[1]), reverse=True)
    
    if sorted_groups:
        print(f"\n{'KEYWORD CLUSTERS (Potential Umbrella Terms)':<45} | {'Freq':<6} | {'CEFR'}")
        print("-" * 60)
        
        for root, items in sorted_groups:
            # Only show groups with at least 2 distinct phrases
            unique_phrases = set(p for p, c in items)
            if len(unique_phrases) < 2:
                continue
                
            total_freq = sum(c for p,c in items)
            
            # Check CEFR level for the root/stem
            root_level = get_cefr_level(root)
            
            header_str = f"[{root.upper()}] (Total: {total_freq})"
            print(f"{header_str:<45} | {'':<6} | {root_level}")
            
            # Sort items in group by frequency
            items = sorted(items, key=lambda x: x[1], reverse=True)
            for phrase, count in items:
                level = get_cefr_level(phrase)
                print(f"  - {phrase:<41} | {count:<6} | {level}")
            print()

def get_dictionaries_for_subject_area(subject_area):
    """
    Looks up the required dictionary names (dict_name) for a given subject area
    using the STANDARDIZED_TERMS configuration.
    
    Args:
        subject_area (str): The cleaned degree area (e.g., 'Computer Science').

    Returns:
        list: A list of dictionary names (strings) required for analysis in this area,
              or an empty list if the subject area is not configured.
    """
    return STANDARDIZED_TERMS["degree_areas"].get(subject_area, [])


def get_relevant_terms_from_dicts(terms_to_search, loaded_dicts_map):
    """
    Searches a list of unigrams and phrases (terms_to_search) across multiple 
    loaded subject dictionaries using case-insensitive and basic singular/plural matching.
    
    The function builds a map: {normalized_key: (original_key, dict_name, dictionary_object)}
    This ensures the correct source dictionary is captured during the lookup phase.
    
    Args:
        terms_to_search (list): A list of strings (unigrams or phrases) extracted from the thesis text.
        loaded_dicts_map (dict): A map where keys are dict_name strings and values 
                                 are the actual loaded Python dictionary objects.

    Returns:
        list: A list of result dictionaries, where each result is:
              {'term': str, 'dict_name': str, 'classification': dict}
    """
    relevant_terms = []
    
    # Normalize input terms once (lowercase for initial key lookup)
    normalized_input_terms = set(term.lower() for term in terms_to_search)
    
    # Structure to hold mappings: {normalized_form: (original_key, dict_name, dictionary_object)}
    normalized_to_original_map = {}
    
    # 1. Pre-process all dictionary keys for faster, case/plural-insensitive lookup
    for dict_name, dictionary in loaded_dicts_map.items():
        if dictionary is None:
            continue
            
        for original_key in dictionary.keys():
            normalized_key = original_key.lower()
            
            # Map normalized key to original key, dict_name, and dictionary object
            if normalized_key not in normalized_to_original_map:
                 normalized_to_original_map[normalized_key] = (original_key, dict_name, dictionary)
                 
            # Basic singular/plural check for keys ending in 's'
            if normalized_key.endswith('s'):
                singular_key = normalized_key[:-1]
                if singular_key not in normalized_to_original_map:
                    # Map normalized singular key to original plural key
                    normalized_to_original_map[singular_key] = (original_key, dict_name, dictionary)

    # 2. Search all normalized input terms against the prepared map
    matched_keys = set() # Track unique dictionary keys found to avoid duplicates
    
    for input_term_lower in normalized_input_terms:
        
        # Check for exact match (case-insensitive)
        if input_term_lower in normalized_to_original_map:
            original_dict_key, dict_name, dictionary = normalized_to_original_map[input_term_lower]
            if original_dict_key not in matched_keys:
                relevant_terms.append({
                    'term': original_dict_key,
                    'dict_name': dict_name,
                    'classification': dictionary[original_dict_key]
                })
                matched_keys.add(original_dict_key)
                
        # Check for singular/plural match on input terms (input is plural, map holds singular)
        if input_term_lower.endswith('s'):
            singular_input_term = input_term_lower[:-1]
            if singular_input_term in normalized_to_original_map:
                original_dict_key, dict_name, dictionary = normalized_to_original_map[singular_input_term]
                if original_dict_key not in matched_keys:
                    relevant_terms.append({
                        'term': original_dict_key,
                        'dict_name': dict_name,
                        'classification': dictionary[original_dict_key]
                    })
                    matched_keys.add(original_dict_key)

    return relevant_terms

def get_dict_import_info(relevant_dict_names):
    """
    Looks up the source file and dict name for a list of required dictionary names
    by checking against the 'all_dicts' configuration list.

    Args:
        relevant_dict_names (list): A list of 'dict_name' strings obtained 
                                    from the subject area lookup.

    Returns:
        list: A list of dictionaries, where each inner dictionary contains 
              'source_file', 'dict_name', and 'display_name' for the required dicts.
    """
    required_dicts = []
    
    # Create a set for fast lookup of required names
    required_names_set = set(relevant_dict_names)
    
    # Iterate through all configured dictionaries and check if their dict_name is required
    for d_info in STANDARDIZED_TERMS["all_dicts"]:
        if d_info["dict_name"] in required_names_set:
            required_dicts.append(d_info)
            
    return required_dicts

def get_relevant_terms_from_dicts(terms_to_search, loaded_dicts_map):
    """
    Searches a list of unigrams and phrases (terms_to_search) across multiple 
    loaded subject dictionaries using case-insensitive and basic singular/plural matching.
    
    The function builds a map: {normalized_key: (original_key, dict_name, dictionary_object)}
    This ensures the correct source dictionary is captured during the lookup phase.
    
    Args:
        terms_to_search (list): A list of strings (unigrams or phrases) extracted from the thesis text.
        loaded_dicts_map (dict): A map where keys are dict_name strings and values 
                                 are the actual loaded Python dictionary objects.

    Returns:
        list: A list of result dictionaries, where each result is:
              {'term': str, 'dict_name': str, 'classification': dict}
    """
    relevant_terms = []
    
    # Normalize input terms once (lowercase for initial key lookup)
    normalized_input_terms = set(term.lower() for term in terms_to_search)
    
    # Structure to hold mappings: {normalized_form: (original_key, dict_name, dictionary_object)}
    normalized_to_original_map = {}
    
    # 1. Pre-process all dictionary keys for faster, case/plural-insensitive lookup
    for dict_name, dictionary in loaded_dicts_map.items():
        if dictionary is None:
            continue
            
        for original_key in dictionary.keys():
            normalized_key = original_key.lower()
            
            # Map normalized key to original key, dict_name, and dictionary object
            if normalized_key not in normalized_to_original_map:
                 normalized_to_original_map[normalized_key] = (original_key, dict_name, dictionary)
                 
            # Basic singular/plural check for keys ending in 's'
            if normalized_key.endswith('s'):
                singular_key = normalized_key[:-1]
                if singular_key not in normalized_to_original_map:
                    # Map normalized singular key to original plural key
                    normalized_to_original_map[singular_key] = (original_key, dict_name, dictionary)

    # 2. Search all normalized input terms against the prepared map
    matched_keys = set() # Track unique dictionary keys found to avoid duplicates
    
    for input_term_lower in normalized_input_terms:
        
        # Check for exact match (case-insensitive)
        if input_term_lower in normalized_to_original_map:
            original_dict_key, dict_name, dictionary = normalized_to_original_map[input_term_lower]
            if original_dict_key not in matched_keys:
                relevant_terms.append({
                    'term': original_dict_key,
                    'dict_name': dict_name,
                    'classification': dictionary[original_dict_key]
                })
                matched_keys.add(original_dict_key)
                
        # Check for singular/plural match on input terms (input is plural, map holds singular)
        if input_term_lower.endswith('s'):
            singular_input_term = input_term_lower[:-1]
            if singular_input_term in normalized_to_original_map:
                original_dict_key, dict_name, dictionary = normalized_to_original_map[singular_input_term]
                if original_dict_key not in matched_keys:
                    relevant_terms.append({
                        'term': original_dict_key,
                        'dict_name': dict_name,
                        'classification': dictionary[original_dict_key]
                    })
                    matched_keys.add(original_dict_key)

    return relevant_terms

def check_proper_name(phrase, category_dict):
    global options

    if not phrase:
        return None

    # Step 1: Global Exact Match
    # Check all categories for the phrase exactly as it is.
    for category, names_set in category_dict.items():
        if phrase in names_set:
            return f"B2 (Proper Name: {category})"

    # Step 2: Swedish Genitive Check (The 's' rule)
    if options.swedish and phrase.endswith('s') and len(phrase) > 2:
        root = phrase[:-1]
        # Only strip if the root doesn't end in s, x, or z
        if not root.lower().endswith(('s', 'x', 'z')):
            # We prioritize checking People and Swedish Places for possessives
            for cat in ['names_of_persons', 'swedish_place_names', 'proper_names']:
                if root in category_dict.get(cat, set()):
                    return f"B2 (Proper Name: {cat} possessive)"

    # Step 3: Compound Name Logic
    parts = phrase.split()
    if len(parts) > 1:
        match_count = 0
        for part in parts:
            found = False
            # Check if this specific word exists in any list or is a possessive
            for cat, names_set in category_dict.items():
                if part in names_set:
                    found = True
                    break
                # Inner possessive check for compound parts like "Sigurd Curmans"
                if options.swedish and part.endswith('s'):
                    p_root = part[:-1]
                    if not p_root.lower().endswith(('s', 'x', 'z')) and p_root in names_set:
                        found = True
                        break
            if found:
                match_count += 1
        
        if match_count == len(parts):
            return "B2 (Proper Name: Compound Match)"

    return None

def cefr_from_exact_match(phrase, category_dict):
    if not phrase:
        return None

    # Step 1: Global Exact Match
    # Check all categories for the phrase exactly as it is.
    for category, names_set in category_dict.items():
        if phrase in names_set:
            return f"B2 (Proper Name: {category})"

    return None

abbreviations_map = {
    '⎧⎨⎩': '{', # a large left curly brace
    'i.e.': 'id est',
    'e.g.': 'for example',
    'et al.': 'et alii', # 'and others'
    'etc.': 'et cetera',
    'vs.': 'versus',
    'Dr.': 'Doctor',
    'Prof.': 'Professor',
    'prof.': 'professor',
    'Asst.': 'assistant',
    'Assoc.': 'asso0ciate',
    'Mr.': 'Mister',
    'Mrs.': 'Missus',
    'Ms.': 'Miss',
    'U.S.': 'United States',
    'U.K.': 'United Kingdom',
    'Inc.': 'Incorporated',
    'Ltd.': 'Limited',
    'M.Sc.': 'Master of Science', # Must come before M.S.
    'M.S.': 'Master of Science',

    # abbreviations for months
    'Jan.': 'January',
    'Feb.': 'February',
    'Mar.': 'March',
    'Apr.': 'April',
    # May
    'Jun.': 'June',
    'Jul.': 'July',
    'Aug.': 'August',
    'Sep.': 'September',
    'Sept.': 'September',
    'Oct.': 'October',
    'Nov.': 'November',
    'Dec.': 'December',

    # Add the rest of your month/other abbreviations here
}

def replace_abbreviations(text):
    """
    Replaces abbreviations in a string with their full-text equivalents.
    """
    if not text:
        return text

    # Sort keys by length (descending) to replace longer matches first
    sorted_keys = sorted(abbreviations_map.keys(), key=len, reverse=True)

    for abbr in sorted_keys:
        escaped_abbr = re.escape(abbr)
        
        # Start with a word boundary to prevent matching "see.g."
        start_boundary = r'\b'
        
        # --- THE FIX ---
        # Only add a word boundary at the end if the abbreviation
        # itself ends with a word character (a-z, 0-9, _).
        if abbr[-1].isalnum():
             end_boundary = r'\b'
        else:
             # If it ends with '.', don't add a boundary, as the '.'
             # already acts as the boundary.
             end_boundary = r''
        # --- END FIX ---

        # Build the final pattern
        pattern = start_boundary + escaped_abbr + end_boundary
        
        # Use a lambda function to handle case-insensitivity in the replacement
        # This makes sure "E.G." is replaced with "FOR EXAMPLE"
        def get_replacement(match):
            replacement = abbreviations_map[abbr]
            if match.group(0).isupper():
                return replacement.upper()
            elif match.group(0).istitle():
                return replacement.title()
            else:
                return replacement

        text = re.sub(pattern, get_replacement, text, flags=re.IGNORECASE)
        
    return text

def main():
    global Verbose_Flag
    global options
    global STANDARDIZED_TERMS
    global name_category_dict
    global exact_name_category_dict
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

    parser.add_option('-s', '--swedish',
                      dest="swedish",
                      default=False,
                      action="store_true",
                      help="When processing a thesis in Swedish")

    parser.add_option('-n', '--nolemitization',
                      dest="no_lemma",
                      default=False,
                      action="store_true",
                      help="Diable lemmitization")

    options, remainder = parser.parse_args()
    Verbose_Flag = options.verbose

    if len(remainder) != 1:
        print("Usage: ./thesis_keyword_extractor.py [-v] <PDF_file>")
        sys.exit(1)

    pdf_path = remainder[0]
    pdf_path = pdf_path.replace('"', '').replace("'", "")
    
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
    
    if Verbose_Flag:
        print(f"{VALID_SUBJECT_AREAS=}")

    # get subject from the conver or title page
    potential_subject=get_subject_area(pdf_path)
    print(f"{pdf_path=}\t{potential_subject=}")
    if options.testing:
        return
    
    # Initialize the dictionary using sets for O(1) lookup speed
    name_category_dict = {
        'names_of_persons': set(common_english.names_of_persons),
        'proper_names': set(common_english.proper_names),
        'place_names': set(common_english.place_names),
        'swedish_place_names': set(common_swedish.swedish_place_names),
        'swedish_names_for_foreign_places': set(common_swedish.swedish_names_for_foreign_places)
    }

    exact_name_category_dict = {
        'company_and_product_names': set(common_english.company_and_product_names),
        'common_programming_languages': set(common_english.common_programming_languages),
        'mathematical_words_to_ignore': set(common_english.mathematical_words_to_ignore),
        'common_units': set(common_english.common_units),
    }


    print("\nExtracting text...")
    pages = extract_text_from_pdf(pdf_path)
    
    if pages:
        print(f"Successfully extracted {len(pages)} pages.")
        
        # 1. Build Case Frequency Map (Data-Driven Case Restoration)
        print("Analyzing text case usage...")
        case_map = build_case_frequency_map(pages)
        
        # 2. Preprocess for Analysis
        corpus = [preprocess_text(page) for page in pages]
        corpus = [page for page in corpus if page.strip()]
        
        if not corpus:
            print("Error: No text found after preprocessing.")
            return

        print("Identifying keywords...\n")
        
        # 1. Get Top Unigrams (Single Words)
        unigrams = get_top_features(corpus, case_map, ngram_range=(1, 1), top_n=1000)
        
        # 2. Get Top Bigrams/Trigrams (Phrases)
        phrases = get_top_features(corpus, case_map, ngram_range=(2, 3), top_n=100) 
        
        print(f"{'TOP SINGLE KEYWORDS':<35} | {'Freq':<6} | {'CEFR'}")
        print("-" * 60)
        for word, count in unigrams:
            level = get_cefr_level(word)
            print(f"{word:<35} | {count:<6} | {level}")
            
        print("\n" + "=" * 60 + "\n")
        
        print(f"{'TOP KEY PHRASES':<35} | {'Freq':<6} | {'CEFR'}")
        print("-" * 60)
        for phrase, count in phrases:
            level = get_cefr_level(phrase)
            print(f"{phrase:<35} | {count:<6} | {level}")

        # 3. Print Cluster Analysis
        all_keywords = unigrams + phrases
        print_keyword_clusters(all_keywords)

        print("\nSuggestion: Key phrases often make better thesis keywords than single words.")
        
    else:
        print("Failed to process the PDF.")


    print(f"'alii' has CEFR level: {get_cefr_level('alii')}")


    # do the processing of the subject area dicts
    already_loaded=[]
    full_dicts=dict()

    if potential_subject == "Unknown":
        return                  # return as there is nothing more that can be done

    print(f"\nChecking for standard keywords for the subject: {potential_subject}")

    load_standardized_terms()
    if Verbose_Flag:
        print(f"{STANDARDIZED_TERMS=}")
    relevant_dicts = get_dictionaries_for_subject_area(potential_subject)
    if Verbose_Flag:
        print(f"{relevant_dicts=}")

    if relevant_dicts:
        dicts_to_import=get_dict_import_info(relevant_dicts)
        if Verbose_Flag:
            print(f"{dicts_to_import=}")

        # [{'source_file': 'IEEE_thesaurus.py', 'dict_name': 'IEEE_thesaurus_2023_broad_terms', 'display_name': 'IEEE Thesaurus 2023 (Broad Terms)'}, {'source_file': 'IEEE_thesaurus.py', 'dict_name': 'IEEE_thesaurus_2023_narrow_terms', 'display_name': 'IEEE Thesaurus 2023 (Narrow Terms)'}, {'source_file': 'ACM_CCS.py', 'dict_name': 'ACM_categories', 'display_name': 'ACM Computing Classification System (Full Categories)'}, {'source_file': 'ACM_CCS.py', 'dict_name': 'ACM_toplevel', 'display_name': 'ACM Computing Classification System (Top Level)'}]
        for d in dicts_to_import:
            print(f"Importing {d['display_name']}")
            try:
                if d['source_file'].endswith('.py'):
                    file_to_import=d['source_file'][:-3]
                    if file_to_import not in already_loaded:
                        new_module=importlib.import_module(file_to_import)
                        already_loaded.append(file_to_import)
                        for name, value in new_module.__dict__.items():
                            if not name.startswith("__"):
                                globals()[name] = value
                                full_dicts[name]=value

            except Exception as e:
                print(f"Error importing {d['source_file']}: {e}")
                return []
                
        # print(f"{full_dicts=}")
        # for d in full_dicts:
        #     print(f"{d} {len(full_dicts[d])}")

        what_to_search_for=[]
        for word, count in all_keywords:
            what_to_search_for.append(word)

        results=get_relevant_terms_from_dicts(what_to_search_for, full_dicts)
        for result in results:
            print(f"Match: Term='{result['term']}', Dict='{result['dict_name']}', Class='{result['classification']}'")


if __name__ == "__main__":
    main()
