# -*- coding: utf-8 -*-
# -*- mode: python; python-indent-offset: 4 -*-
#
# Some acronyms from courses and theses in EECS
#
# on 2024-04-26 the merged words and corrected abstracts were separated out into their own files
#
# on 2024-06-23 put the acronyms into this file
#
# 2024-06-23
#
# G. Q. Maguire Jr.
#
# well_known_acronyms_list is a list of acronym_:entries
#   The list structure has been used becuase there can be many different
#   means for a given acronym.
#
# Each acronym_:entry is a list and has the form:
#  acronym, expanded_form, extras_dict
#
#  Note that the optional extras_dict can contain the following keys and values:
#   's': list of sources
#           each source is s string, typeically of the form: 'diva2:ddddddd'
#   'cefr': string containing a CEFR level, such as 'B2'
#

# consider adding support for these
well_known_acronyms_list=[
    # the following are from CBH
    ['R,L,C', 'Resistor, Inductor, and Capacitor'],
    ['EVs', 'electric vehicles'],
    ['TATO', 'triazine-trione', {'s': 'diva2:1361820'}],
    ['TEC', 'thiol-ene coupling', {'s': 'diva2:1361820'}],
    ['TYC', 'thiol-yne coupling', {'s': 'diva2:1361820'}],
    ['TEC/TYC', 'thiol-ene coupling/thiol-yne coupling', {'s': 'diva2:1361820'}],
    ['DPMS', 'dolicholphosphate mannosesynthase', {'s': 'diva2:1219274'}],
    ['ISTD', 'Intern standard', {'s': 'diva2:1859260'}],
    ['mMSCs', 'mouse mesenchymal stem cells', {'s': 'diva2:1266796'}],
    ['MSCs', 'Mesenchymal stromal cells', {'s': 'diva2:1454998'}],
    ['OC', 'Object Controllers', {'s': 'diva2:1562805'}],
    ['AC', 'activated Carbon', {'s': 'diva2:827212'}],
    ['CT', 'Computed tomography'],
    ['TBI', 'Traumatic brain injury'],
    ['TBP', 'True Boiling Point)'],
    ['THUMS', 'Total HUman Model for Safety'],
    ['ADRD', 'Alzheimer’s disease and related dementias'],
    ['Arthro-CT', 'Arthrogram Computed Tomography'],
    ['ATAC-seq', 'Assay for transposase-accessible chromatin with sequencing'],
    ['AR', 'Augmented Reality'],
    ['BIM', 'Building Information Modeling'],
    ['CCS', 'Carbon capture and storage'],
    ['cMRF', 'Cardiac Magnetic Resonance Fingerprinting'],
    ['CMR', 'Cardiac Magnetic Resonance Imaging'],
    ['CMR', 'Cardiovascular Magnetic Resonance Imaging'],
    ['CSD', 'Cardiac State Diagram'],
    ['CNF', 'Cellulose nanofibrils'],
    ['ChIP-seq', 'chromatin immunoprecipitation'],
    ['CFUs', 'Colony Forming Units'],
    ['CT', 'computed tomography'],
    ['CBP', 'Consolidated Bioprocessing'],
    ['CNR', 'Contrast-to-noise ratio'],
    ['CNN', 'Convolutional Neural Network'],


]
