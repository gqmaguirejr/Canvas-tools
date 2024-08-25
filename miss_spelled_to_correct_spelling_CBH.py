#-*- coding: utf-8 -*-
# -*- mode: python; python-indent-offset: 4 -*-
#
# Some useful dict()s
#
# 2024-02-20
#
# G. Q. Maguire Jr.
#
# miss_spelled_to_correct_spelling is a dict where the key is the misspelling,
# and the value is a dict having the following possible keys:
#  'c':  a corrected version of the string  [mandatory]
#  's':  information about the source or sources
#          if multiple sources, they are placed in a list
#          Each source is typically of the form: 'diva2:ddddddd''
#  'n':  a note about this entry
#

miss_spelled_to_correct_spelling={
    'boilier': {'c': 'boiler', 's': 'diva2:724099'},
    'devel-opers': {'c': 'developers', 's': 'diva2:1864417'},
    'brow-ser': {'c': 'brow-ser', 's':'diva2:936265'},
    'Conflict-free': {'c': 'conflict-free'},
    'High-level': {'c': 'high-level'},
    'proof-ofconcept': {'c': 'proof-of-concept'},
    "􏰀 chemical modification􏰀": {'c': "chemical modification"},
    "work enviroment": {'c': "work environment"},
    "working enviroment": {'c': "working environment"},

}
