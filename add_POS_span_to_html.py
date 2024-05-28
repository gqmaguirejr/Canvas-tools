#!/usr/bin/python3.11
# -*- coding: utf-8 -*-
# -*- mode: python; python-indent-offset: 4 -*-
#
# ./add_POS_span_to_html.py
#
# Purpose: Add part of speech (POS) markup to an HTML string to be able to insert such a marked up page into a Canvas wikipage.
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
# Note: This is a very rudimentary program designement primarily as a proof of concept and to explore how to use nltk to generate the markup.
# 
# Note: The program automatically transforms the POS class "PRP$" to "PRP§", as the dollar signed cannot be used in a class name. 
#       W3C specification (https://www.w3.org/TR/CSS21/syndata.html#characters) for identifiers:
#        "In CSS, identifiers (including element names, classes, and IDs in selectors) can contain only the characters [a-z0-9] and ISO 10646 characters U+00A0 and higher, plus the hyphen (-) and the underscore (_); they cannot start with a digit, or a hyphen followed by a digit."
#
#       https://www.compart.com/en/unicode/block/U+0080 was used to see the character in the U+00A0 block that might be a useful substitute for "$".
# although the following classes appeared in the output, they are not included in the styles:
#     class="word-("
#     class="word-)"
#     class="word-,"
#     class="word-."
#     class="word-:"
#     class="word-$"
# After revision of the program, the words for these POS tags are simply output.
# 
# Note: This is not generla purpose, as the list of POS classifications was bmanually extracted from the POS cases
#       that occur for the particular html_content string that is shown.
#       This should be generalized to collect the data on all of the POS classes and automatically generate the style_info.
#
# Future work: Add support for phrases
#
# NP Noun phrase
# VP Verb phrase
# DP Determinative phrase
# AdjP Adjective phrase
# AdvP Adverb phrase
# PP Prepositional phrase
# 
# 2024.05.23
#
# G. Q. Maguire Jr.
#
Verbose_flag=False

# POS tags based on https://stackoverflow.com/questions/15388831/what-are-all-possible-pos-tags-of-nltk
# and https://www.ling.upenn.edu/courses/Fall_2003/ling001/penn_treebank_pos.html
#
# CC: conjunction, coordinating
# CD: numeral, cardinal
# DT: determiner
# EX: existential there
# IN: preposition or conjunction, subordinating
# JJ: adjective or numeral, ordinal
# JJR: adjective, comparative
# JJS: adjective, superlative
# LS: list item marker
# MD: modal auxiliary
# NN: noun, common, singular or mass
# NNP: noun, proper, singular
# NNS: noun, common, plural
# PDT: pre-determiner
# POS: genitive marker
# PRP: pronoun, personal
# PRP$: pronoun, possessive
# RB: adverb
# RBR: adverb, comparative
# RBS: adverb, superlative
# RP: particle
# TO: "to" as preposition or infinitive marker
# UH: interjection
# VB: verb, base form
# VBD: verb, past tense
# VBG: verb, present participle or gerund
# VBN: verb, past participle
# VBP: verb, present tense, not 3rd person singular
# VBZ: verb, present tense, 3rd person singular
# WDT: WH-determiner
# WP: WH-pronoun
# WRB: Wh-adverb
#
# FW	Foreign word
# WP$	Possessive wh-pronoun
# NNPS	Proper noun, plural
# SYM	Symbol
#
# $: dollar
# ``: opening quotation mark
# '': closing quotation mark
# (: opening parenthesis
# ): closing parenthesis
# ,: comma
# --: dash
# .: sentence terminator
# :: colon or ellipsis
#
# to get information about them executre:
# nltk.download('tagsets')
# nltk.help.upenn_tagset()


footer="""<hr>
<footer>
POS color keys:  <span class="word-CC">CC</span>, 
  <span class="word-CD">CD</span>, 
  <span class="word-DT">DT</span>, 
  <span class="word-EX">EX</span>, 
  <span class="word-IN">IN</span>, 
  <span class="word-JJ">JJ</span>, 
  <span class="word-MD">MD</span>, 
  <span class="word-NN">NN</span>, 
  <span class="word-NNP">NNP</span>, 
  <span class="word-NNS">NNS</span>, 
  <span class="word-PRP">PRP</span>, 
  <span class="word-PRP§">PRP$</span> (Note that the class name is PRP§ as the
  dollar signed cannot be used in a class name), 
  <span class="word-RB">RB</span>, 
  <span class="word-RBR">RBR</span>, 
  <span class="word-TO">TO</span>, 
  <span class="word-VB">VB</span>, 
  <span class="word-VBD">VBD</span>, 
  <span class="word-VBG">VBG</span>, 
  <span class="word-VBN">VBN</span>, 
  <span class="word-VBP">VBP</span>, 
  <span class="word-VBZ">VBZ</span>, 
  <span class="word-WDT ">WDT </span>, 
  <span class="word-WP">WP</span>, and
  <span class="word-WRB">WRB</span>.

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

from bs4 import BeautifulSoup, NavigableString
import nltk
from nltk import RegexpParser

# Define a grammar for basic chunking
grammar = r""" NP: {<DT|JJ|NN.*>+} # Chunk sequences of DT, JJ, NN
               VP: {<VB.*>} {<NN.*>*} # Chunk VB (verb) followed by optional NN (noun)
"""

grammar = r"""   NP: {<DT|PP\$>?<JJ>*<NN>}   # chunk determiner/possessive, adjectives and nouns
      {<NNP>+}                # chunk sequences of proper nouns
"""

# Create a parser with the grammar
parser = RegexpParser(grammar)

# Custom formatter function for prettify()
def custom_formatter(text):
    text = text.replace('\n', '')
    text = text.replace('  ', ' ')
    return text

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
            if text_node.parent is not None:  # Ensure the tag is still in the tree
                #tokenizer = nltk.RegexpTokenizer(r"\w+['-]\w+|\w+|[^\w\s]")
                #words = tokenizer.tokenize(text_node)
                words = nltk.word_tokenize(text_node, language='english')
                pos_tags = nltk.pos_tag(words)

                # Chunk the POS tagged tokens
                chunked_sentence = parser.parse(pos_tags)
                # Print the chunked sentence structure (tree)
                print(f"{chunked_sentence=}")

                # Create new spans for words and POS tags
                new_spans = []
                for word, pos in pos_tags:
                    encountered_POS_list.add(pos) # keep track of the POS encounterd
                    # correct the POS tag, as the  dollar character cannot be in a class name
                    if pos == "PRP$":
                        pos="PRP§"
                    if pos == "WP$":
                        pos="WP§"

                    # pos tags of words that shuold simply be inserted _without_ placing them in a span
                    if pos in ['(', ')', ',', '.', ':', '$', '--', "``", "''"]:
                        # prepend a space in some cases
                        if pos in  ['(', '$', '--', "``" ]:
                            new_spans.append(soup.new_string(' '))
                        new_spans.append(soup.new_string(word))
                        # postpend a space in some cases
                        if pos in  [')', ',', '.', ':', '$', '--', "''"]:
                            new_spans.append(soup.new_string(' '))
                        continue

                    span = soup.new_tag('span', attrs={'class': f'word-{pos}'})
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

# Example usage
html_content = """<p lang="en-US">Welcome to IK1552: Internetworking. The course should be fun. If you find topics that interest you, you will find that you are more motivated to actively learn. (For some motivation of why other students wanted to take the course and what they wanted to get out of it - see the first ~10 minutes of the first video from the first week - from <a title="Videos 2019" href="https://canvas.kth.se/courses/31168/modules/60503" data-api-endpoint="https://canvas.kth.se/api/v1/courses/31168/modules/60503" data-api-returntype="Module">Videos 2019</a>.)</p>
<p lang="en-US">During the course, we will dig deeper into the TCP/IP protocols and protocols built upon them. Much of the focus is going to be on <strong>Why?</strong> and <strong>How?</strong>, rather than just <strong>What?.&nbsp;</strong></p>
<p lang="en-US">Information about the course is available from the Canvas course room. (There are also a link to the course room from my homepage -&nbsp; <a href="https://people.kth.se/~maguire/">https://people.kth.se/~maguire/</a>)</p>
<p lang="en-US">Key buttons to use on the lefthand menu in this Canvas course room are:</p>
<p lang="en-US"><a title="Syllabus" href="https://canvas.kth.se/courses/31168/assignments/syllabus"><strong>Syllabus</strong></a> - This will show the assignments and their due dates (you can also see information about the assignments at <strong>Assignments</strong>)</p>
<p lang="en-US"><a title="Modules" href="https://canvas.kth.se/courses/31168/modules" data-api-endpoint="https://canvas.kth.se/api/v1/courses/31168/modules" data-api-returntype="[Module]"><strong>Modules</strong></a> - This will show all of the various modules of pages available for the course. You should start with <a title="Spring 2022: lecture notes, Zoom session recordings , and other material" href="https://canvas.kth.se/courses/31168/modules/70911" data-api-endpoint="https://canvas.kth.se/api/v1/courses/31168/modules/70911" data-api-returntype="Module">Spring 2022: lecture notes, Zoom session recordings , and other material</a>. You will also find videos from the 2019 year's course at <a title="Videos 2019" href="https://canvas.kth.se/courses/31168/modules/60503" data-api-endpoint="https://canvas.kth.se/api/v1/courses/31168/modules/60503" data-api-returntype="Module">Videos 2019</a> and a video from 2018 at <a title="Videos 2018" href="https://canvas.kth.se/courses/31168/modules/60504" data-api-endpoint="https://canvas.kth.se/api/v1/courses/31168/modules/60504" data-api-returntype="Module">Videos 2018. </a> Additional modules may be added over time.&nbsp;</p>
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
modified_soup = tokenize_and_pos_tag_html_sentences(html_content)
if Verbose_flag:
    print(modified_soup.prettify(formatter=custom_formatter))
#
print(f"parts of speech codes that wre encountered: {sorted(encountered_POS_list)}")
print("----------------------------------------------------------------------")

print(style_info)
print(modified_soup)
print(footer)

