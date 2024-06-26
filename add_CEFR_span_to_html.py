#!/usr/bin/python3.11
# -*- coding: utf-8 -*-
# -*- mode: python; python-indent-offset: 4 -*-
#
# ./add_CEFR_span_to_html.py
# 
# Purpose: Add CEFR utilizing as necessary part of speech (POS) to create markup to an HTML string to be able to insert such a marked up page into a Canvas wikipage.
#
# Code is based on a long series of interactions with Google Gemini.
# The code takes the html_content string and outputs styel information, the HTML POS markup for the html_content, and a fotter.
#
# The user has to manually put the output into an html file, such as xxxxx.html and then
# use the cput program to put this into an existing Canvas course room wikipage.
#
# The URL for the page should be taken from the Canvas course room and the file name will be the file portion of the URL
# with the extension ".html" - the ".html" is not part of the argumemt to cput, as cput takes the URL as an argument and
# automatically appends the ".html" to form the filename (note this file must be in the current directory)
# 
# Setting Verbose_flag=True will output more information.
#
# 
# 2024.05.25
#
# G. Q. Maguire Jr.
#
Verbose_flag=False
#Verbose_flag=True

from bs4 import BeautifulSoup
import nltk
from nltk import RegexpParser


import re

import sys
sys.path.append('/z3/maguire/Canvas/Canvas-tools')  # Include the path to module_folder
sys.path.append('/home/maguire/Canvas/Canvas-tools')

#  as common_English_words, common_swedish_words, common_swedish_technical_words
import common_english_and_swedish
import common_acronyms
import miss_spelled_to_correct_spelling
import diva_merged_words
import diva_corrected_abstracts
import AVL_words_with_CEFR

# width to use for outputting numeric values
Numeric_field_width=7

# Define a grammar for basic chunking
grammar = r""" NP: {<DT>?<JJ.*>*<NN.*>+}   # Chunk sequences of DT, JJ, NN
                   {<PRP>}                # Pronouns
                   {<PRP\$><NN.*>+}       # Possessive pronouns followed by nouns
                   {<CD><NN.*>+}          # Cardinal numbers followed by nouns
                   {<NN.*><IN><NN.*>+}    # Nouns followed by a preposition and more nouns
               VP: {<VB.*>+}             # Chunk all verbs together
                   {<MD><VB.*>+}        # Chunk modal verbs with main verbs
                   {<RB.*>?<VB.*>+}     # Allow optional adverbs before verbs
"""

# Create a parser with the grammar
parser = RegexpParser(grammar)



# entries in the dict will have the form: 'acronym': ['expanded form 1', 'expanded form 2',  ... ]
well_known_acronyms=dict()
for e in common_acronyms.well_known_acronyms_list:
    if len(e) >= 1:
        ack=e[0]
        if len(e) >= 2:
            d=e[1]
            current_entry=well_known_acronyms.get(ack, list())
            current_entry.append(d)
            well_known_acronyms[ack]=current_entry

if Verbose_flag:
    print(f'{(len(well_known_acronyms)):>{Numeric_field_width}} unique acronyms in ({len(common_acronyms.well_known_acronyms_list)}) well_known_acronyms')

special_dicts = {
    'common_English_words': common_english_and_swedish.common_English_words,
    'common_swedish_words': common_english_and_swedish.common_swedish_words,
    'common_swedish_technical_words': common_english_and_swedish.common_swedish_technical_words,
    'names_of_persons': common_english_and_swedish.names_of_persons,
    'place_names': common_english_and_swedish.place_names,
    'company_and_product_names': common_english_and_swedish.company_and_product_names,
    'common_programming_languages': common_english_and_swedish.common_programming_languages,
    'well_known_acronyms': well_known_acronyms, # common_english_and_swedish.well_known_acronyms,
    'common_units': common_english_and_swedish.common_units,
    'abbreviations_ending_in_period': common_english_and_swedish.abbreviations_ending_in_period,
    'programming_keywords': common_english_and_swedish.programming_keywords,
    'thousand_most_common_words_in_English_old': common_english_and_swedish.thousand_most_common_words_in_English_old,
    'common_danish_words': common_english_and_swedish.common_danish_words,
    'common_german_words': common_english_and_swedish.common_german_words,
    'common_icelandic_words': common_english_and_swedish.common_icelandic_words,
    'common_latin_words': common_english_and_swedish.common_latin_words,
    'common_portuguese_words': common_english_and_swedish.common_portuguese_words,
    'common_finnish_words': common_english_and_swedish.common_finnish_words,
    'common_spanish_words': common_english_and_swedish.common_spanish_words,
    'common_italian_words': common_english_and_swedish.common_italian_words,
}

footer="""<hr>
<footer>
<p>Color codes for CEFR levels: <span class="CEFRA1">A1</span>, <span class="CEFRA2">A2</span> , <span class="CEFRB1">B1</span>,
  <span class="CEFRB2">B2</span>, <span class="CEFRC1">C1</span>, <span class="CEFRC2">C2</span>,
  <span class="CEFRXX">XX</span>, and <span class="CEFRNA">NA</span>.</p>
<p>Automatically generated from the HTML for the page <a href="https://canvas.kth.se/courses/31168/pages/welcome-to-the-internetworking-course">https://canvas.kth.se/courses/31168/pages/welcome-to-the-internetworking-course</a>.
</footer>
"""
style_info="""<style>
  .CEFRA1{
    background-color: rgba(0, 255, 8,  0.3);
     
  }
  .CEFRA2{
      background-color: rgba(0, 251, 100,  0.8);
  }
  .CEFRB1{
    background-color: rgba(0, 200, 251, 0.3);
  }
  .CEFRB2{
      background-color: rgba(0, 151, 207,  0.8);
  }
  .CEFRC1{
    background-color: rgba(251, 0, 0, 0.3);
  }
  .CEFRC2{
    background-color: rgba(251, 0, 0, 0.8);
  }
  .CEFRXX{
    background-color: #9a9a9a;
  }
  .CEFRNA{
    #background-color: royalblue;
    background-color: transparent;
  }
  .word-CC{
    background-color: rgba(200, 100, 100, 0.3);
  }
  .word-CD{
    background-color: rgba(250, 100, 100, 0.3);
  }
  .word-DT{
    background-color: rgba(200, 000, 200, 0.3);
  }
  .word-EX{
    background-color: rgba(200, 100, 200, 0.3);
  }
  .word-IN{
    background-color: rgba(200, 80, 200, 0.3);
  }
  .word-JJ{
    background-color: rgba(250, 210, 000, 0.8);
  }
  .word-MD{
    background-color: rgba(250, 100, 100, 0.3);
  }
  .word-NN{
    background-color: rgba(251, 0, 0, 0.3);
  }
  .word-NNP{
    background-color: rgba(251, 0, 0, 0.8);
  }
  .word-NNS{
    background-color: rgba(255, 50, 0, 0.8);
  }
  .word-PRP{
    background-color: rgba(100, 100, 8,  0.3);
  }
  .word-PRP§{
    background-color: rgba(120, 120, 88,  0.3);
  }
  .word-RBR{
    background-color: rgba(100, 140, 80,  0.8);
  }
  .word-RB{
    background-color: rgba(100, 140, 8,  0.3);
  }
  .word-TO{
    background-color: rgba(100, 200, 8,  0.3);
  }
  .word-VB{
    background-color: rgba(0, 210, 8,  0.3);
  }
  .word-VBD{
    background-color: rgba(0, 240, 58,  0.8);
  }
  .word-VBG{
    background-color: rgba(0, 235, 80,  0.3);
  }
  .word-VBN{
    background-color: rgba(0, 220, 100,  0.3);
  }
  .word-VBP{
    background-color: rgba(0, 210, 128,  0.3);
  }
  .word-VBZ{
    background-color: rgba(0, 200, 8,  0.3);
  }
  .word-WDT{
    background-color: rgba(0, 200, 251, 0.2);
  } 
  .word-WP{
    background-color: rgba(0, 200, 251, 0.5);
  }
  .word-WRB{
    background-color: rgba(0, 200, 251, 0.8);
  }

</style>
"""

def find_sentences_in_tag(tag):
    if tag.name and Verbose_flag:
        print(f"{tag.name=}")
    if tag.name and tag.name in ['script', 'style']:
        return
    if tag.string:
        if Verbose_flag:
            print(f"{tag.string=}")
        sentences = nltk.sent_tokenize(tag.string)
        for sentence in sentences:
            yield sentence, tag
    else:
        for child in tag.children:
            yield from find_sentences_in_tag(child)
#
# Custom formatter function for prettify()
def custom_formatter(indent_level, text, is_inline_element):
    if not is_inline_element:  # Add newline for block-level elements
        return f"\n{' ' * indent_level}{text}"
    else:
        return text
#

def choose_lowest_cefr_level(wl):
    level_order=['A1', 'A2', 'B1', 'B2', 'C1', 'C2', 'xx']
    for l in level_order:
        if l in wl:
            return l
    # otherwise
    if Verbose_flag:
        print(f'Error in choose_lowest_cefr_level({wl})')
    return False
def cefr_level_index(wl):
    level_order=['A1', 'A2', 'B1', 'B2', 'C1', 'C2', 'xx']
    for l in level_order:
        if l in wl:
            return l
    # otherwise
    if Verbose_flag:
        print(f'error in cefr_level_index({w1})')

def choose_lowest_cefr_level_from_two(w1, w2):
    level_order=['A1', 'A2', 'B1', 'B2', 'C1', 'C2', 'xx']
    if cefr_level_index(w1) < cefr_level_index(w2):
        return w1
    else:
        return w2

    # otherwise
    if Verbose_flag:
        print(f'Error in choose_lowest_cefr_level_from_two({w1}, {w2})')
    return False

def cefr_level_to_index(li):
    level_order=['A1', 'A2', 'B1', 'B2', 'C1', 'C2', 'xx']
    for indx, l in enumerate(level_order):
        if li == l:
            return indx
    return False

def compare_cefr_levels(l1, l2):
    level_order=['A1', 'A2', 'B1', 'B2', 'C1', 'C2', 'xx']
    l1i=cefr_level_to_index(l1)
    l2i=cefr_level_to_index(l2)
    if isinstance(l1i, int) and isinstance(l2i, int):
        return l2i - l1i
    # otherwise
    if Verbose_flag:
        print(f'Error in compare_cefr_level({l1}, {l2})')
    return False

# each entry in the lex is of the form {'word': word, 'pos': pos, 'cefr_level': key_max}
def compute_lowest_CEFR_level(lex, lex_name):
    global Verbose_Flag

    level_words=dict()
    for w in lex:
        word=w['word']
        new_level=w['cefr_level']
            
        current_level=level_words.get(word, False)
        if current_level:
            lowest=choose_lowest_cefr_level_from_two(current_level, new_level)
        else:
            lowest=new_level
        level_words[word]=lowest

    if Verbose_Flag:
        print(f'loest levels for {lex_name}={level_words=}')

    return level_words

def is_academic_term(s):
    if len(s) == 6 and s[1] == 'T' and (s[0] == 'V' or s[0] == 'H') and s[2:].isdigit():
        return True
    else:
        return False

def is_float(string):
    try:
        float(string)
        return True
    except ValueError:
        return False
    
def is_number(string):
    # deal with the fact that LaTeX can set a minus sign
    if len(string) > 1 and string[0] == '\u2212':
        string = '-' + string[1:]
    if len(string) > 1 and string[0] == '~':
        string = '-' + string[1:]
    #
    if len(string) > 0:
        if not (string[0] == '-' or string[0] == '+'):
            if not string[0].isdigit():
                return False
    rr = re.findall("[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?", string)
    if rr and len(rr) == 1:
        if is_float(rr[0]):
            return True
    # otherwise
    return False

def is_integer_range_or_ISSN(string):
    if string.count('-') == 1:
        string=string.replace('-', "")
        return string.isdigit()
    elif string.count('–') == 1:
        string=string.replace('–', "")
        return string.isdigit()
    # otherwise
    return False
    

level_order=['A1', 'A2', 'B1', 'B2', 'C1', 'C2', 'xx', 'NA']

def get_cefr_levels(language, word):
    celf_levels=False
    src=None
    if language == 'en':
        celf_levels=common_english_and_swedish.top_100_English_words.get(word.lower(), False)
        if celf_levels:
            return celf_levels, 'top_100_English_words'
        celf_levels=common_english_and_swedish.thousand_most_common_words_in_English.get(word.lower(), False)
        if celf_levels:
            return celf_levels, 'thousand_most_common_words_in_English'
        #
        celf_levels=AVL_words_with_CEFR.avl_words.get(word, False)
        if celf_levels:
            return celf_levels, 'AVL'

        celf_levels=AVL_words_with_CEFR.avl_words.get(word.lower(), False)
        if celf_levels:
            return celf_levels, 'AVL'

        celf_levels=common_english_and_swedish.common_English_words.get(word, False)
        if celf_levels:
            return celf_levels, 'common_English_words'
        #
        celf_levels=common_english_and_swedish.common_English_words.get(word.lower(), False)
        if celf_levels:
            return celf_levels, 'common_English_words'
        #
        celf_levels=common_english_and_swedish.common_English_words.get(word.lower(), False)
        if celf_levels:
            return celf_levels, 'common_English_words'

        celf_levels=common_english_and_swedish.KTH_ordbok_English_with_CEFR.get(word.lower(), False)
        if celf_levels:
            return celf_levels, 'KTH_ordbok_English_with_CEFR'


    if language == 'sv':
        celf_levels=common_english_and_swedish.common_swedish_words.get(word, False)
        if celf_levels:
            return celf_levels, 'common_swedish_words'
        #
        celf_levels=common_english_and_swedish.common_swedish_technical_words.get(word, False)
        if celf_levels:
            return celf_levels, 'common_swedish_technical_words'
        #
        celf_levels=common_english_and_swedish.KTH_ordbok_Swedish_with_CEFR.get(word, False)
        if celf_levels:
            return celf_levels, 'KTH_ordbok_Swedish_with_CEFR'


    # all languages
    if word in common_english_and_swedish.common_units:
        return 'A1', 'common_units'
    #
    if word in common_english_and_swedish.chemical_names_and_formulas:
        return 'B2', 'chemical_names_and_formulas'
    #
    if word in common_english_and_swedish.common_urls:
        return 'B2', 'common_urls'
    #
    if word in common_english_and_swedish.java_paths:
        return 'B2', 'java_paths'
    #
    if word in common_english_and_swedish.misc_words_to_ignore:
        return 'XX', 'misc_words_to_ignore'
    #
    if word in common_english_and_swedish.place_names:
        return 'A1', 'place_names'
    #
    if word in common_english_and_swedish.company_and_product_names:
        return 'B2', 'company_and_product_names'
    #
    if word in common_english_and_swedish.common_programming_languages:
        return 'B2', 'common_programming_languages'
    #
    if word in common_english_and_swedish.names_of_persons:
        return 'B2', 'names_of_persons'

    #
    return celf_levels, src


def get_cefr_level(language, word, pos, context):
    global Verbose_flag
    if Verbose_flag:
        print(f"get_cefr_level('{language}', '{word}', '{pos}', {context})")

    # check if there is a need to correct the POS
    pos = corrected_pos_for_word(word, pos)

    celf_levels=False
    src=None

    if word == "'s" and pos == 'POS':
        return 'B1', 'genative marker'

    if pos == 'CD': # numeral, cardinal
        return 'A1', 'fixed'

    if pos == 'LS': # list item marker
        return 'A1', 'fixed'

    if pos == 'SYM': # Symbol
        return 'A1', 'fixed'

    if pos == 'FW': # Foreign word
        return 'XX', 'foreign word'

    if word in well_known_acronyms:
        return 'NA', 'well_known_acronyms'
        
    cefr_levels, src=get_cefr_levels(language, word)
    if Verbose_flag:
        print(f"{cefr_levels=}")
    if not cefr_levels:
        if is_number(word):
            return 'A1', 'number'
        if is_integer_range_or_ISSN(word):
            return 'A1', 'integer_range_or_ISSN'
        if is_academic_term(word):
            return 'A1', 'academic_term'
        return 'XX', 'unknown'

    if isinstance(cefr_levels, str):
        return cefr_levels, src

    for wl in level_order:
        pos_in_level=cefr_levels.get(wl, 'False')
        if Verbose_flag:
            print(f"{wl=} {pos_in_level}")
        if pos_in_level:
            pos_in_level=pos_in_level.lower().split(',')
            pos_in_level=[p.strip() for p in pos_in_level]

            print(f"second print: {wl=} {pos_in_level}")

            # handle wild card of POS
            if 'et al.' in pos_in_level:
                return wl, src

            if pos in ['RB', 'RBR', 'RBS']:
                if 'adverb' in pos_in_level:
                    return wl, src

            if pos in ['WRB']:
                if 'interrogative adverb' in pos_in_level:
                    return wl, src
                if 'adverb' in pos_in_level:
                    return wl, src

            if pos in ['VBD']:
                if 'verb past tense' in pos_in_level:
                    return wl, src

            if pos in ['VBN']:
                if 'past participle' in pos_in_level:
                    return wl, src
                if 'verb past participle' in pos_in_level:
                    return wl, src
                if 'verb (past participle)' in pos_in_level:
                    return wl, src
                if 'verb' in pos_in_level:
                    return wl, src

            if pos in ['VBG']:
                if 'verb gerund or present participle' in pos_in_level:
                    return wl, src
                if 'verb (present participle)' in pos_in_level:
                    return wl, src
                if 'verb' in pos_in_level:
                    return wl, src
                if 'verb' in pos_in_level:
                    return wl, src

            if pos in ['VBZ']:
                if 'verb 3rd person present' in pos_in_level:
                    return wl, src

            if pos in ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']:
                if 'verb' in pos_in_level:
                    return wl, src

            if pos in ['PRP§']:
                if 'possessive pronoun' in pos_in_level:
                    return wl, src
                if 'pronoun' in pos_in_level:
                    return wl, src

            if pos in ['PRP', 'WP', 'WP§']:
                if 'pronoun' in pos_in_level:
                    return wl, src

            if pos in ['NNP', 'NNPS']:
                if 'proper noun' in pos_in_level:
                    return wl, src
                if 'noun' in pos_in_level:
                    return wl, src

            if pos in ['NN']:
                if 'acronym' in pos_in_level:
                    return wl, src

            if pos in ['NNS']:
                if 'noun (plural)' in pos_in_level:
                    return wl, src
                if 'noun' in pos_in_level:
                    return wl, src


            if pos in ['NN', 'NNP', 'NNS', 'NNPS']:
                if 'noun' in pos_in_level:
                    return wl, src
                if 'proper noun' in pos_in_level:
                    return wl, src

            if pos in ['JJ', 'JJR', 'JJS']:
                if 'adjective' in pos_in_level:
                    return wl, src

            if pos in ['TO']:
                if 'preposition' in pos_in_level:
                    return wl, src
                if 'infinitive' in pos_in_level:
                    return wl, src

            if pos in ['IN']:
                if 'preposition' in pos_in_level:
                    return wl, src
                if 'conjunction' in pos_in_level:
                    return wl, src

            if pos in ['CC']:
                if 'conjunction' in pos_in_level:
                    return wl, src
                if 'coordinator' in pos_in_level:
                    return wl, src

            if pos in ['DT', 'PDT', 'WDT']:
                if 'determiner' in pos_in_level:
                    return wl, src
                if 'article' in pos_in_level:
                    return wl, src


            if pos in ['UH']:
                if 'interjection' in pos_in_level:
                    return wl, src

            if pos in ['RP']:
                if 'particle' in pos_in_level:
                    return wl, src

            if pos in ['EX']:
                if 'existential' in pos_in_level:
                    return wl, src

            if pos in ['MD']:
                if 'modal verb' in pos_in_level:
                    return wl, src
                if 'verb' in pos_in_level:
                    return wl, src

            if pos in ['POS']:
                if 'genitive' in pos_in_level:
                    return wl, src

    return 'XX', src


corrected_pos_info=[
    ['fun', 'VBN', 'JJR'],
    ['that', 'IN', 'DT'],
    ['anytime', 'NN', 'RB'],
    ['Join', 'NNP', 'VB'],
    ['Meeting', 'VBG', 'NNP'],
    ['written', 'VBN', 'JJ'],
]

def corrected_pos_for_word(word, pos):
    for e in corrected_pos_info:
        if e[0] == word and e[1] == pos:
            return e[2]
    return pos

encountered_POS_list=set()

def tokenize_and_pos_tag_html_sentences(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find sentences in the HTML
    def find_sentences_in_tag(tag, parent=None):
        if tag.name and tag.name in ['script', 'style']:
            return []
        
        # If it's a string, tokenize it and yield sentence and parent
        if isinstance(tag, NavigableString):
            text = tag.string.strip()
            if text:
                sentences = nltk.sent_tokenize(text)
                for sentence in sentences:
                    yield sentence, tag  

        # If it's a tag, process children recursively
        elif tag.name:
            for child in tag.children:
                yield from find_sentences_in_tag(child, tag)  

    for paragraph in soup.find_all('p'):
        text_nodes = list(paragraph.find_all(string=True, recursive=True))  # Get all text nodes (recursive)
        for text_node in text_nodes:
            if text_node.parent.name == 'a':
                if Verbose_flag:
                    print(f"parent is a link: {text_node.parent=} -  text: {text_node.string}")
                # if the text is simply a URL, just keep it and do not do CEFR processing
                tokenizer = nltk.RegexpTokenizer(r"http\S+|\w+['-]\w+|\w+|[^\w\s]")
                words = tokenizer.tokenize(text_node)
                if Verbose_flag:
                    print(f"{words=}")
                if len(words) == 1 and words[0].find('http') == 0:
                    continue

            if text_node.parent.name == 'strong':
                if Verbose_flag:
                    print(f"parent is a strong: {text_node.parent=} -  text: {text_node.string}")
            if text_node.parent is not None:  # Ensure the tag is still in the tree
                #tokenizer = nltk.RegexpTokenizer(r"\w+['-]\w+|\w+|[^\w\s]")
                #words = tokenizer.tokenize(text_node)
                words = nltk.word_tokenize(text_node, language='english')
                pos_tags = nltk.pos_tag(words)

                # Chunk the POS tagged tokens
                chunked_sentence = parser.parse(pos_tags)
                # Print the chunked sentence structure (tree)
                print(f"{chunked_sentence=}")
                if Verbose_flag:
                    chunked_sentence.draw()

                # Create new spans for words and POS tags
                new_spans = []
                if text_node.parent.name in ['i', 's', 'strong', 'em', 'span', 'a', 'b'] and len(pos_tags) >= 1 and pos_tags[0][1] not in ['(', ')', ',', '.', '$',  "``", "''"]:
                    if Verbose_flag:
                        print(f"parent is a {pos_tags[0][1]}: {text_node.parent=} -  text: {text_node.string}")
                    new_spans.append(soup.new_string(' '))

                if Verbose_flag:
                    print(f"before loop - parent is a {pos_tags}: {text_node.parent=} -  text: {text_node.string}")


                for word, pos in pos_tags:
                    if Verbose_flag:
                        print(f"in loop: {text_node.parent.name=} {word=} {pos=}")
                    encountered_POS_list.add(pos) # keep track of the POS encounterd
                    # correct the POS tag, as the  dollar character cannot be in a class name
                    if pos == "PRP$":
                        pos="PRP§"
                    if pos == "WP$":
                        pos="WP§"

                    
                    # pos tags of words that should simply be inserted _without_ placing them in a span
                    if pos in ['(', ')', ',', '.', ':', '$', '--', "``", "''"]:
                        # prepend a space in some cases
                        if pos in  ['(', '$', '--', "``", ':' ]:
                            new_spans.append(soup.new_string(' '))
                        new_spans.append(soup.new_string(word))
                        # postpend a space in some cases
                        if pos in  [')', ',', '.', ':', '$', '--', "''"]:
                            new_spans.append(soup.new_string(' '))
                        continue

                    cefr_level, source = get_cefr_level('en', word, pos, None)
                    if Verbose_flag:
                        print(f"Word: '{word}', POS: '{pos}', CEFR Level: {cefr_level}, Source: {source}")
                    span = soup.new_tag('span', attrs={'class': f'CEFR{cefr_level}'})
                    span.string = word
                    # Add space between word spans, except before punctuation
                    if Verbose_flag:
                        print(f"{word=} - {new_spans=}")
                    # if len(new_spans) == 0:
                    #     new_spans.append(soup.new_string(' '))
                    if len(new_spans) > 0:
                        new_spans.append(soup.new_string(' '))

                    new_spans.append(span)

                    if Verbose_flag:
                        print(f"after adding possible spaces {new_spans=}")

                # Replace the original text with the new spans
                text_node.replace_with(*new_spans)

    return soup
# Custom formatter function for prettify()
def custom_formatter(indent_level, text, is_inline_element):
    if not is_inline_element:  # Add newline for block-level elements
        return f"\n{' ' * indent_level}{text}"
    else:
        return text
#
html_content="""<p lang="en-US">Welcome to IK1552: Internetworking. The course should be fun. If you find topics that interest you, you will find that you are more motivated to actively learn. (For some motivation of why other students wanted to take the course and what they wanted to get out of it - see the first ~10 minutes of the first video from the first week - from <a title="Videos 2019" href="https://canvas.kth.se/courses/31168/modules/60503" data-api-endpoint="https://canvas.kth.se/api/v1/courses/31168/modules/60503" data-api-returntype="Module">Videos 2019</a>.)</p>
<p lang="en-US">During the course, we will dig deeper into the TCP/IP protocols and protocols built upon them. Much of the focus is going to be on <strong>Why?</strong> and <strong>How?</strong>, rather than just <strong>What?.&nbsp;</strong></p>
<p lang="en-US">Information about the course is available from the Canvas course room. (There are also a link to the course room from my homepage -&nbsp; <a href="https://people.kth.se/~maguire/">https://people.kth.se/~maguire/</a>)</p>
<p lang="en-US">Key buttons to use on the lefthand menu in this Canvas course room are:</p>
<p lang="en-US"><a title="Syllabus" href="https://canvas.kth.se/courses/31168/assignments/syllabus"><strong>Syllabus</strong></a> - This will show the assignments and their due dates (you can also see information about the assignments at <strong>Assignments</strong>)</p>
<p lang="en-US"><a title="Modules" href="https://canvas.kth.se/courses/31168/modules" data-api-endpoint="https://canvas.kth.se/api/v1/courses/31168/modules" data-api-returntype="[Module]"><strong>Modules</strong></a> - This will show all of the various modules of pages available for the course. You should start with <a title="Spring 2022: lecture notes, Zoom session recordings , and other material" href="https://canvas.kth.se/courses/31168/modules/70911" data-api-endpoint="https://canvas.kth.se/api/v1/courses/31168/modules/70911" data-api-returntype="Module">Spring 2022: lecture notes, Zoom session recordings , and other material</a>. You will also find videos from the 2019 year's course at <a title="Videos 2019" href="https://canvas.kth.se/courses/31168/modules/60503" data-api-endpoint="https://canvas.kth.se/api/v1/courses/31168/modules/60503" data-api-returntype="Module">Videos 2019</a> and a video from 2018 at <a title="Videos 2018" href="https://canvas.kth.se/courses/31168/modules/60504" data-api-endpoint="https://canvas.kth.se/api/v1/courses/31168/modules/60504" data-api-returntype="Module">Videos 2018.</a>  Additional modules may be added over time.&nbsp;</p>
<p lang="en-US"><a title="Announcements" href="https://canvas.kth.se/courses/31168/announcements"><strong>Announcements</strong></a> - This will show all of the announcements that have been made in the course.</p>
<p lang="en-US"><a title="Discussions" href="https://canvas.kth.se/courses/31168/discussion_topics" data-api-endpoint="https://canvas.kth.se/api/v1/courses/31168/discussion_topics" data-api-returntype="[Discussion]"><strong>Discussions</strong></a> - This is a place to create and participate in discussions for the course. For example, if you are looking for a study partner or a partner to work on the final report for the course - use a discussion (there are two discussions created for these purposes).</p>
<p lang="en-US"><a title="Collaborations" href="https://canvas.kth.se/courses/31168/collaborations"><strong>Collaborations</strong> </a>- web tools to enable groups of students to collaborate</p>
<p lang="en-US"><a title="Grades" href="https://canvas.kth.se/courses/31168/grades"><strong>Grades</strong></a> - gives you information about which assignments you have completed</p>
<p lang="en-US">We will use a flipped- classroom model for the course - after the first lecture (Monday 21 March 2022) via Zoom:</p>
<p style="margin-left: 10%; margin-right: 10%;">Topic: IK1552 VT2022<br />Time: This is a recurring meeting Meet anytime</p>
<p style="margin-left: 10%; margin-right: 10%;">Join Zoom Meeting <br /><a href="https://kth-se.zoom.us/j/65739701259" target="_blank" rel="noopener">https://kth-se.zoom.us/j/65739701259</a>&nbsp;</p>
<p style="margin-left: 10%; margin-right: 10%;">Meeting ID: 657 3970 1259</p>
<p lang="en-US">The course consists of 1 hour of lecture (during the first
class), ~23 hours of videos, 14 hours of discussions, and 40-100 hours of written assignments.</p>
"""

modified_soup=tokenize_and_pos_tag_html_sentences(html_content)
if Verbose_flag:
    print(modified_soup.prettify(formatter=custom_formatter))
#
print(f"parts of speech codes that wre encountered: {sorted(encountered_POS_list)}")
print("----------------------------------------------------------------------")

print(style_info)
print(modified_soup)
print(footer)
#
