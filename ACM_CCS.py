# -*- coding: utf-8 -*-
# -*- mode: python; python-indent-offset: 4 -*-
#
# ACM Computing Classification System (CCS)
# https://dl.acm.org/ccs
#
# The terms have been augmented with POS and CEFR information.
#
# 2025-12-09
#
# G. Q. Maguire Jr.
#


ACM_toplevel={
    'General and reference': {'B2': 'Noun Phrase'}, # Academic field grouping
    'Hardware': {'B1 (Specialized)': 'Noun'}, # Foundational technical field
    'Computer systems organization': {'C1 (Specialized)': 'Noun Phrase'}, # Abstract academic field
    'Networks': {'B1 (Specialized)': 'Noun'}, # Foundational technical field
    'Software and its engineering': {'C1 (Specialized)': 'Noun Phrase'}, # Abstract academic field
    'Theory of computation': {'C2 (Specialized)': 'Noun Phrase'}, # Highly abstract and foundational field
    'Mathematics of computing': {'C1 (Specialized)': 'Noun Phrase'}, # Abstract academic field
    'Information systems': {'B2 (Specialized)': 'Noun Phrase'}, # Common academic/business field
    'Security and privacy': {'B2': 'Noun Phrase'}, # Common and widely discussed field
    'Human-centered computing': {'C1 (Specialized)': 'Noun Phrase'}, # Specific academic field (HCI)
    'Computing methodologies': {'C1 (Specialized)': 'Noun Phrase'}, # Abstract academic field
    'Applied computing': {'B2 (Specialized)': 'Noun Phrase'}, # Descriptive academic field
    'Social and professional topics': {'B2': 'Noun Phrase'} # Academic field grouping
}


ACM_categories={
    'Document types': {'B1': 'Noun Phrase'}, # Common academic/publishing term
    'Cross-computing tools and techniques': {'C1 (Specialized)': 'Noun Phrase'}, # Abstract academic field
    'Printed circuit boards': {'B1 (Specialized)': 'Noun Phrase'}, # Common engineering/technical item
    'Communication hardware, interfaces and storage': {'B2 (Specialized)': 'Noun Phrase'}, # Compound technical field
    'Integrated circuits': {'B1 (Specialized)': 'Noun Phrase'}, # Foundational electronics component
    'Very large scale integration design': {'C1 (Specialized)': 'Noun Phrase'}, # Specific engineering field (VLSI)
    'Power and energy': {'B1': 'Noun Phrase'}, # Common scientific/engineering term
    'Electronic design automation': {'C1 (Specialized)': 'Noun Phrase'}, # Specific engineering field (EDA)
    'Hardware validation': {'B2 (Specialized)': 'Noun Phrase'}, # Common engineering/systems term
    'Hardware test': {'B2 (Specialized)': 'Noun Phrase'}, # Common engineering/systems term
    'Robustness': {'B2': 'Noun'}, # Common academic/engineering term
    'Emerging technologies': {'B1': 'Noun Phrase'}, # Common business/technical term
    'Architectures': {'B2 (Specialized)': 'Noun (plural)'}, # Common technical/academic term
    'Embedded and cyber-physical systems': {'C1 (Specialized)': 'Noun Phrase'}, # Specific academic field
    'Real-time systems': {'B2 (Specialized)': 'Noun Phrase'}, # Specific academic/technical field
    'Dependable and fault-tolerant systems and networks': {'C1 (Specialized)': 'Noun Phrase'}, # Abstract academic field
    'Network architectures': {'B2 (Specialized)': 'Noun Phrase'}, # Specific academic/technical field
    'Network protocols': {'B1 (Specialized)': 'Noun Phrase'}, # Foundational technical concept
    'Network components': {'B1 (Specialized)': 'Noun Phrase'}, # Common technical term
    'Network algorithms': {'B2 (Specialized)': 'Noun Phrase'}, # Specific academic/technical field
    'Network performance evaluation': {'B2 (Specialized)': 'Noun Phrase'}, # Common technical/academic field
    'Network properties': {'B2 (Specialized)': 'Noun Phrase'}, # Common technical/academic field
    'Network services': {'B1': 'Noun Phrase'}, # Common technical/business term
    'Network types': {'B1': 'Noun Phrase'}, # Common technical term
    'Software organization and properties': {'C1 (Specialized)': 'Noun Phrase'}, # Abstract academic field
    'Software notations and tools': {'B2 (Specialized)': 'Noun Phrase'}, # Common academic/technical field
    'Software creation and management': {'B2 (Specialized)': 'Noun Phrase'}, # Descriptive academic field
    'Models of computation': {'C2 (Specialized)': 'Noun Phrase'}, # Highly abstract and foundational field
    'Formal languages and automata theory': {'C1 (Specialized)': 'Noun Phrase'}, # Specific academic field
    'Computational complexity and cryptography': {'C1 (Specialized)': 'Noun Phrase'}, # Specific academic field
    'Logic': {'C1 (Specialized)': 'Noun'}, # Specific academic field (Formal Logic)
    'Design and analysis of algorithms': {'C1 (Specialized)': 'Noun Phrase'}, # Specific academic field
    'Randomness, geometry and discrete structures': {'C1 (Specialized)': 'Noun Phrase'}, # Compound mathematical field
    'Theory and algorithms for application domains': {'C1 (Specialized)': 'Noun Phrase'}, # Abstract academic field
    'Semantics and reasoning': {'C1 (Specialized)': 'Noun Phrase'}, # Abstract academic field
    'Discrete mathematics': {'B2 (Specialized)': 'Noun Phrase'}, # Foundational academic field
    'Probability and statistics': {'B2': 'Noun Phrase'}, # Common academic field
    'Mathematical software': {'B2 (Specialized)': 'Noun Phrase'}, # Common technical field
    'Information theory': {'C1 (Specialized)': 'Noun Phrase'}, # Specific academic field
    'Mathematical analysis': {'C1 (Specialized)': 'Noun Phrase'}, # Specific academic field
    'Continuous mathematics': {'C1 (Specialized)': 'Noun Phrase'}, # Specific academic field
    'Data management systems': {'B2 (Specialized)': 'Noun Phrase'}, # Common academic/technical field
    'Information storage systems': {'B1 (Specialized)': 'Noun Phrase'}, # Common technical term
    'Information systems applications': {'B2 (Specialized)': 'Noun Phrase'}, # Common academic/business field
    'World Wide Web': {'A2 (Proper Noun)': 'Noun Phrase'}, # Common general term
    'Information retrieval': {'B2 (Specialized)': 'Noun Phrase'}, # Specific academic/technical field
    'Cryptography': {'B2 (Specialized)': 'Noun'}, # Specific academic/technical field
    'Formal methods and theory of security': {'C2 (Specialized)': 'Noun Phrase'}, # Highly abstract field
    'Security services': {'B2': 'Noun Phrase'}, # Common business/technical term
    'Intrusion/anomaly detection and malware mitigation': {'C1 (Specialized)': 'Noun Phrase'}, # Compound security field
    'Security in hardware': {'B2 (Specialized)': 'Noun Phrase'}, # Common academic/technical field
    'Systems security': {'B2 (Specialized)': 'Noun Phrase'}, # Common academic/technical field
    'Network security': {'B2 (Specialized)': 'Noun Phrase'}, # Common academic/technical field
    'Database and storage security': {'B2 (Specialized)': 'Noun Phrase'}, # Common academic/technical field
    'Software and application security': {'B2 (Specialized)': 'Noun Phrase'}, # Common academic/technical field
    'Human and societal aspects of security and privacy': {'C1 (Specialized)': 'Noun Phrase'}, # Compound academic field
    'Human computer interaction (HCI)': {'B2 (Proper Noun)': 'Noun Phrase'}, # Specific academic field
    'Interaction design': {'B2': 'Noun Phrase'}, # Specific academic/professional field
    'Collaborative and social computing': {'C1 (Specialized)': 'Noun Phrase'}, # Specific academic field
    'Ubiquitous and mobile computing': {'C1 (Specialized)': 'Noun Phrase'}, # Specific academic field
    'Visualization': {'B2': 'Noun'}, # Common academic/technical term
    'Accessibility': {'B1': 'Noun'}, # Common general/technical term
    'Symbolic and algebraic manipulation': {'C1 (Specialized)': 'Noun Phrase'}, # Specific mathematical field
    'Parallel computing methodologies': {'C1 (Specialized)': 'Noun Phrase'}, # Specific academic field
    'Artificial intelligence': {'B2 (Specialized)': 'Noun Phrase'}, # Foundational academic field
    'Machine learning': {'B2 (Specialized)': 'Noun Phrase'}, # Foundational academic field
    'Modeling and simulation': {'B2 (Specialized)': 'Noun Phrase'}, # Common scientific/engineering field
    'Computer graphics': {'B2 (Specialized)': 'Noun Phrase'}, # Specific academic/technical field
    'Distributed computing methodologies': {'C1 (Specialized)': 'Noun Phrase'}, # Specific academic field
    'Concurrent computing methodologies': {'C1 (Specialized)': 'Noun Phrase'}, # Specific academic field
    'Electronic commerce': {'B1': 'Noun Phrase'}, # Common business/economic term
    'Enterprise computing': {'B2 (Specialized)': 'Noun Phrase'}, # Specific business/technical field
    'Physical sciences and engineering': {'B2': 'Noun Phrase'}, # Academic field grouping
    'Life and medical sciences': {'B2': 'Noun Phrase'}, # Academic field grouping
    'Law, social and behavioral sciences': {'B2': 'Noun Phrase'}, # Academic field grouping
    'Computer forensics': {'C1 (Specialized)': 'Noun Phrase'}, # Specific academic/technical field
    'Arts and humanities': {'A2': 'Noun Phrase'}, # Common academic field
    'Computers in other domains': {'B1': 'Noun Phrase'}, # Descriptive academic field
    'Operations research': {'C1 (Specialized)': 'Noun Phrase'}, # Specific academic/technical field
    'Education': {'A2': 'Noun'}, # Common academic/social term
    'Document management and text processing': {'B2 (Specialized)': 'Noun Phrase'}, # Common technical field
    'Professional topics': {'B1': 'Noun Phrase'}, # Common academic/general term
    'Computing / technology policy': {'B2': 'Noun Phrase'}, # Common academic/political field
    'User characteristics': {'B1': 'Noun Phrase'} # Common academic/technical field
}


