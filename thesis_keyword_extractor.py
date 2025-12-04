#!/usr/bin/python3.11
# -*- coding: utf-8 -*-
#
# thesis_keyword_extractor.py PDF_file
#
# Purpose: Thesis Keyword Suggestion Tool
#
# with option '-v' use verbose output
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

# Add path to custom modules
sys.path.append('/home/maguire/Canvas-tools')
# sys.path.append('/z3/maguire/Canvas/Canvas-tools')  # Include the path to module_folder
# sys.path.append('/home/maguire/Canvas/Canvas-tools')

# Attempt to import custom modules
try:
    import common_english
    import common_acronyms
    import AVL_words_with_CEFR
except ImportError:
    # Fallback to prevent crash if running elsewhere
    common_english = None
    common_acronyms = None
    AVL_words_with_CEFR = None

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
    # 0. Fix PDF Ligatures using comprehensive table
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

    # 1. Fix hyphenation at line endings (e.g., "Sen- \n sing" -> "Sensing")
    # \w matches Unicode word characters (letters, numbers, underscore)
    text = re.sub(r'(\w+)-\s+(\w+)', r'\1\2', text)
    
    # 2. Preserve compound words by replacing hyphens with underscores
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
    if len(variations) == 1:
        return variations.most_common(1)[0][0]
    
    # Check User Rule: "If there is a title-caps version and a lower case version, 
    # then you use the lower case version."
    # Examples: "Computer" (Title) vs "computer" (Lower) -> Use "computer"
    # Note: "GHz" is NOT Title case (it's mixed). "Ghz" IS Title case.
    
    lower_v = token.lower()
    # Check if a true Title Case variant exists (e.g. "Word")
    # We iterate keys to find one that is title case
    has_title = any(v.istitle() for v in variations.keys())
    has_lower = lower_v in variations
    
    if has_title and has_lower:
        return lower_v
        
    # User Rule: "Otherwise... use the most common"
    # This handles "GHz" (100) vs "Ghz" (1) -> uses "GHz"
    return variations.most_common(1)[0][0]

def get_top_features(corpus, case_map, ngram_range, top_n=15):
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

def get_cefr_level(phrase):
    """
    Attempts to retrieve the CEFR level for a phrase from common_english 
    and AVL_words_with_CEFR modules.
    """
    if common_english is None:
        return ""

    phrase_lower = phrase.lower()
    valid_levels = {'A1', 'A2', 'B1', 'B2', 'C1', 'C2'}
    
    # 0. Check names of persons (Exact match required)
    # Uses names_of_persons list if it exists in common_english
    names_list = getattr(common_english, 'names_of_persons', [])
    if isinstance(names_list, (list, set, tuple)):
        # Check 1: Exact phrase match
        if phrase in names_list:
            return "B2 (Proper Name)"
        
        # Check 2: Compound names (e.g. "John Smith")
        # Split phrase by spaces and check if ALL parts are in the list
        parts = phrase.split()
        if len(parts) > 1:
            if all(part in names_list for part in parts):
                return "B2 (Proper Name)"


    # List of dictionaries to check in the module
    dicts_to_check = [
        'common_English_words',
        'top_100_English_words',
        'thousand_most_common_words_in_English',
        'chemical_elements_symbols',
        'chemical_elements',
        'KTH_ordbok_English_with_CEFR',
        'common_units',
        'AVL_words_with_CEFR'
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

    if len(remainder) != 1:
        print("Usage: ./thesis_keyword_extractor.py [-v] <PDF_file>")
        sys.exit(1)

    pdf_path = remainder[0]
    pdf_path = pdf_path.replace('"', '').replace("'", "")
    
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
        unigrams = get_top_features(corpus, case_map, ngram_range=(1, 1), top_n=10)
        
        # 2. Get Top Bigrams/Trigrams (Phrases)
        phrases = get_top_features(corpus, case_map, ngram_range=(2, 3), top_n=20) 
        
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

if __name__ == "__main__":
    main()
