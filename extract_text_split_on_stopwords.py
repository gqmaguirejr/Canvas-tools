#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# ./extract_text_split_on_stopwords.py PDF_file
#
# Extract text from PDF file, splitting lines before/after stopwords and punctuation.
#
# G. Q. Maguire Jr.
#
# 2025-10-16
#

import sys
import os
import optparse
import pymupdf # import PyMuPDF
import faulthandler
import re
import pprint
import json

from collections import Counter
from collections import defaultdict

import sys
sys.path.append('/z3/maguire/Canvas/Canvas-tools')  # Include the path to module_folder
sys.path.append('/home/maguire/Canvas/Canvas-tools')

#  as common_English_words, common_swedish_words, common_swedish_technical_words
import common_english
#import common_swedish
import common_acronyms

# List of words that will trigger a line break.
StopWords=[
    u'a', u'à', u'able', u'about', u'above', u'additional', u'additionally', u'after',
    u'against', u'all', u'allows', u'along', u'almost', u'already', u'also', u'also:',
    u'although', u'an', u'and', u'another', u'any', u'anyone', u'are', u'as', u'at',
    u'average', u'be', u'been', u'because', u'before', u'being', u'below', u'between',
    u'both', u'but', u'by', u'can', u'could', u'course', u'currently', u'decrease',
    u'decreasing', u'did', u'do', u'doing', u'does', u'done', u'down', u'due', u'during',
    u'each', u'early', u'earlier', u'easy', u'e.g', u'eigth', u'either', u'else', u'end',
    u'especially', u'etc', u'even', u'every', u'far', u'few', u'five', u'first',
    u'follow', u'following', u'for', u'formerly', u'four', u'from', u'further',
    u'general', u'generally', u'get', u'going', u'good', u'had', u'has', u'have',
    u'having', u'he', u'hence', u'her', u'here', u'hers', u'herself', u'high',
    u'higher', u'him', u'himself', u'his',  u'how', u'however', u'i', u'i.e', u'if',
    u'in', u'include', u'includes', u'including', u'increase', u'increasing', u'into',
    u'is', u'it', u"it's", u'its', u'itself', u'just', u'know', u'known', u'knows',
    u'last', u'later', u'large', u'least', u'like', u'long', u'longer', u'low',
    u'made', u'many', u'make', u'makes', u'me', u'might', u'much', u'more', u'most',
    u'must', u'my', u'myself', u'near', u'need', u'needs', u'needed', u'next', u'new',
    u'no', u'nor', u'not', u'now', u'of', u'off', u'often', u'on', u'once', u'one',
    u'only', u'or', u'other', u'others', u'otherwise', u'our', u'ours', u'ourselves',
    u'out', u'over', u'own', u'pass', u'per', u'pg', u'pp', u'provides', u'rather',
    u'require', u's', u'same', u'see', u'several', u'she', u'should', u'simply',
    u'since', u'six', u'small', u'so', u'some', u'such', u'take', u'takes', u'th',
    u'than', u'that', u'the', u'then', u'their', u'theirs', u'them', u'themselves',
    u'then', u'there', u'therefore', u'these', u'three', u'they', u'this', u'those',
    u'through', u'thus', u'time', u'to', u'too', u'try', u'two', u'under', u'unit',
    u'until', u'up', u'used', u'verison', u'very', u'vs', u'want', u'was', u'we',
    u'were', u'what', u'when', u'where', u'which', u'while', u'who', u'whom', u'why',
    u'wide', u'will', u'with', u'within', u'would', u'you', u'your', u'yourself',
    u'yourselves'
]

# Convert to a set for efficient O(1) lookups
StopWordsSet = set(StopWords)

WordsToFilterOut=[
    'KTH',
    # names of parts of document
    'Abstract',
    'Academic Dissertation',
    'Acknowledgments CONTENTS',
    'Background',
    'CONTENTS',
    'Chapter',
    'Conclusions',
    'Equation',
    'FIGURES', 'FIGURES LIST',
    'Figure',  'Figures',
    'Future Work',
    'Future work',
    'Introduction',
    'Licentiate thesis',
    'Listing',
    'LISTINGS List',
    'Related Work',
    'Research Method',
    'Research Methodology',
    'Results',
    'Results and Analysis',
    'Section',
    'Sections',
    'Table',
    'TABLES',
    'TABLES LISTINGS',
    'kth royal institute',
    'Universitetsservice US-AB',
    'abstract',
    'acknowledgments',
    'background',
    'contents',
    'keywords',
    'introduction',
    'references',
    'thesis',
    'work',

    # common words to skip (Egqm)
    'ability',
    'achieve',
    'achieved',
    'achieving',
    'acronyms',
    'adapt',
    'adapting',
    'added',
    'adding',
    'advantage',
    'affect',
    'affected',
    'affecting',
    'affects',
    'aim',
    'algorithm',
    'algorithms',
    'allow',
    'allowed',
    'always',
    'among',
    'amount',
    'analysis',
    'analyzed',
    'analyzes',
    'annotates',
    'announce',
    'announced',
    'announcement',
    'announcements',
    'announces',
    'announcing',
    'answer',
    'append',
    'applied',
    'apply',
    'applying',
    'approach',
    'approached',
    'area',
    'around',
    'art',
    'assessed',
    'assessing',
    'assign',
    'assigned',
    'assigning',
    'assist',
    'associate',
    'assume',
    'assumed',
    'assumption',
    'attack',
    'attacked',
    'attacker',
    'attacks',
    'attempt',
    'attract',
    'attribute',
    'attributed',
    'attributes',
    'augment',
    'augmented',
    'authenticate',
    'authors',
    'available',
    'avoid',
    'avoiding',
    'away',
    'background',
    'backup',
    'backups',
    'base',
    'based',
    'based upon',
    'baseline',
    'bases',
    'become',
    'beforehand',
    'beginning',
    'behavior',
    'believable',
    'belong',
    'beneficial',
    'benefit',
    'benefiting',
    'benefits',
    'best',
    'block',
    'blocked',
    'blocks',
    'breadth',
    'break',
    'build',
    'calculate',
    'calculation',
    'call',
    'called',
    'cannot',
    'cannot benefit',
    'cannot verify',
    'capabilities',
    'capable',
    'capacity',
    'capture',
    'captured',
    'captures',
    'care',
    'carry',
    'case',
    'cases',
    'categories',
    'categorized',
    'category',
    'cause',
    'causes',
    'causing',
    'certain',
    'certain number',
    'challenge',
    'challenges',
    'challenging',
    'change',
    'changes',
    'chapter',
    'chapter answers',
    'chapter explains',
    'chapter presented',
    'chapters',
    'chapter summarizes',
    'characterized',
    'choices',
    'choose',
    'chooses',
    'choosing',
    'chosen',
    'circumstance',
    'circumstances',
    'claiming',
    'classified',
    'clearly',
    'close',
    'closer',
    'closest',
    'code',
    'colleagues',
    'collect',
    'collected',
    'collection',
    'collector',
    'collectors',
    'combination',
    'commercialize',
    'common',
    'commonly',
    'commonly accepted',
    'commonly believed',
    'commonly classified',
    'common practice',
    'common problem',
    'communicate',
    'communicated',
    'communication',
    'compare',
    'compared',
    'comparing',
    'comparison',
    'compiled',
    'completely eliminate',
    'completely invisible',
    'complex',
    'complexity',
    'component',
    'components',
    'compute',
    'computed',
    'computes',
    'computing',
    'conclude',
    'concludes',
    'conclusion',
    'conclusions',
    'conditions',
    'conducted',
    'conducting',
    'configuration',
    'configure',
    'configured',
    'confused',
    'connect',
    'connected',
    'connections',
    'consequently',
    'consider',
    'consideration',
    'considered',
    'considering',
    'considers',
    'continue',
    'continuing',
    'contrary',
    'contrast',
    'data',
    'dataset',
    'defined',
    'defines',
    'definition',
    'definitions',
    'dependency',
    'dependent',
    'depends',
    'depicted',
    'depicts',
    'deploy',
    'deployed',
    'deploying',
    'deployment',
    'describe',
    'described',
    'describes',
    'design',
    'designed',
    'detail',
    'details',
    'difference',
    'differences',
    'different',
    'directly',
    'disadvantage',
    'disclose',
    'disclosed',
    'discover',
    'discoverers',
    'discovering',
    'discovery',
    'discuss',
    'discusses',
    'discussion',
    'distinguish',
    'distinguished',
    'distinguishing',
    'evaluate',
    'example',
    'explains',
    'Finally',
    'Furthermore',
    'impact',
    'implementation',
    'information',
    'Initially',
    'Insights',
    'Instead',
    'Interestingly',
    'Internet',
    'Intuitively',
    'issue',
    'limitations',
    'method',
    'methodology',
    'model',
    'network',
    'networks',
    'paper',
    'part',
    'path',
    'paths',
    'performance',
    'presents',
    'problem',
    'process',
    'results',
    'Secondly',
    'shows',
    'Similar',
    'Similarly',
    'solution',
    'Specifically',
    'study',
    'Subsequently',
    'suggests',
    'Summary',
    'system',
    'systems',
    'techniques',
    'term',
    'test',
    'Third',
    'time',
    'traffic',
    'Unlike',
    'use',
    'uses',
    'Using',
    'value',
    'values',
    'version',
    'way',
    'Line',
    'List',
    'Local',
    'Looking',
    'Measuring',
    'Model',
    'Modeling',
    'Modifying',
    'Moreover',
    'Motivation',
    'Nevertheless',
    'Notable',
    'Notably',
    'Note',
    'Number',
    'Output',
    'Overview',
    'Part',
    'Past work',
    'Path',
    'Paths',
    'Peer',
    'Peers',
    'Percentage',
    'Prefix',
    'Prepend',
    'Printed',
    'Printer',
    'Prior research',
    'Problem',
    'Propagation',
    'Propagators',
    'Protocol',
    'Provider',
    'Providers',
    'Purpose',
    'Realistic',
    'Reality',
    'Recall',
    'Refers',
    'Reflections',
    'Report',
    'Research',
    'Return',
    'Returns',
    'Second',
    'Select',
    'Selection',
    'Shape',
    'Shortest',
    'Standards',
    'Step',
    'Stores',
    'Structure',
    'Taxonomy',
    'Technology',
    'Today',
    'Toy example',
    'Toy example showing',
    'Toy example showing',
    'Traditionally',
    'True',
    'Type',
    'Uncovering',
    'Understanding',
    'Unfortunately',
    'Value',
    'Vendors may',
    'Whether',
    'X-axis',
    'Y-axis',
    'Z-axis',
    'Yet',
    'abbreviations',
    'absence',
    'absent',
    'abstract view',
    'abstraction',
    'abuse',
    'accept',
    'accepted',
    'accordance',
    'according',
    'account',
    'accuracy',
    'accurate',
    'achieve greater impact',
    'accurate prediction',
    'accurate predictions',
    'accurately answer',
    'accurately generate',
    'actually',
    'actually feasible',
    'addition',
    'address',
    'addressed',
    'advertise',
    'advertised',
    'advertisement',
    'advertisements',
    'advertises',
    'advertising',
    'again',
    'agreement',
    'agreements',
    'always export',
    'always generate',
    'always maintained',
    'always perform',
    'always pick',
    'always prefer',
    'always succeed',
    'always supported',
    'always visible',
    'assess whether',
    'available option',
    'become apparent',
    'begins iterating',
    'become visible',
    'becoming visible',
    'candidate',
    'careful handling',
    'careful reader',
    'carefully engineer',
    'carefully engineered',
    'carefully influence',
    'carefully structuring',
    'case shown',
    'chosen set',
    'chosen subset',
    'complex procedure',
    'computational',
    'configures',
    'consist',
    'consistent',
    'consisting',
    'consists',
    'contain',
    'contains',
    'context',
    'continuation',
    'contradiction',
    'control',
    'converge',
    'conversion',
    'correct',
    'correspond',
    'corresponding',
    'corrupt',
    'corrupted',
    'corrupting',
    'cost',
    'counted',
    'counting',
    'country',
    'counts',
    'coverage',
    'covers',
    'craft',
    'crafted',
    'create',
    'created',
    'creating',
    'creation',
    'critical',
    'current',
    'curves',
    'customer',
    'customers',
    'cycle',
    'dangerous',
    'dashed arrow',
    'dashed line',
    'data plane',
    'data-plane',
    'data points',
    'data providers',
    'data sources',
    'databases',
    'datapoints',
    'datasets',
    'day worth',
    "day’s worth",
    'deal',
    'debugging purposes',
    'decades',
    'decide',
    'decided',
    'decides',
    'decision',
    'decisions',
    'decreases',
    'deduced',
    'deflection',
    'degree',
    'deliberately making',
    'delimits',
    'deployment costs',
    'deprioritizing',
    'descending order',
    'description',
    'design choice',
    'design choices',
    'design decision',
    'design goals',
    'despite',
    'destination',
    'destination address',
    'destination prefix',
    'detect',
    'detecting',
    'detection',
    'determined',
    'developed',
    'developing',
    'different percentages',
    'different percentiles',
    'different perspectives',
    'different purpose',
    'different sets',
    'different sources',
    'different types',
    'difficult',
    'difficulties',
    'difficulty',
    'direct consequence',
    'direct neighbor',
    'direct neighbors',
    'directly emerge',
    'directly increases',
    'digitally signs',
    'discovered',
    'discussed',
    'disguise',
    'displayed',
    'disrupt',
    'disrupted',
    'distance',
    'distribution',
    'divided',
    'document',
    'documentation',
    'documented',
    'documented parameters',
    'documents',
    'domain',
    'domains',
    'drop',
    'easier',
    'easily',
    'easily avoid',
    'easily detectable',
    'easily maintain',
    'easily manipulate',
    'effective',
    'effective similar',
    'effectively modify',
    'effectiveness',
    'efficient enough',
    'empirically infer',
    'employ',
    'empty',
    'enable',
    'enables',
    'enabling',
    'encouraged',
    'engineer',
    'engineering',
    'enhance',
    'enhanced',
    'enjoyable',
    'enough',
    'ensure',
    'ensuring',
    'ensuring stability',
    'entire Internet',
    'entire route',
    'entire topology',
    'entries',
    'entry',
    'environment',
    'equal number',
    'equal preference',
    'equally distanced',
    'equally preferred',
    'equidistant',
    'error rate',
    'errors',
    'essential terms',
    'essentially ignoring',
    'establish',
    'established',
    'estimate',
    'estimated influence',
    'estimating',
    'et al',
    'ethical considerations',
    'evaluated',
    'evaluating',
    'examination',
    'examined',
    'examines',
    'example given',
    'example topology',
    'examples',
    'exchange',
    'executed',
    'exempt',
    'exist',
    'existed',
    'existence',
    'existing',
    'existing distribution',
    'existing infrastructure',
    'existing networks',
    'existing number',
    'existing peers',
    'existing problems',
    'existing work',
    'existing works',
    'exists',
    'expand',
    'expected',
    'expected finding',
    'expected length',
    'experiment',
    'experiment consists',
    'experimental design',
    'experiments',
    'explain',
    'explained',
    'explicitly',
    'explicitly',
    'explicitly excluded',
    'exploit',
    'export',
    'exported',
    'exporting',
    'exports',
    'extend',
    'extended',
    'extensions',
    'extent',
    'external method',
    'external networks',
    'extra links',
    'extract',
    'extracted',
    'extracted tables',
    'face',
    'fact',
    'factor',
    'fail',
    'failed',
    'failed attempts',
    'failed simulation',
    'fails',
    'failures',
    'false positives',
    'family',
    'fat finger errors',
    'favor',
    'feasibility',
    'feasible',
    'feasible success',
    'fewer',
    'figure',
    'figure consists',
    'figure illustrates',
    'figure shows',
    'figures',
    'figuring',
    'filled',
    'filter',
    'filtered',
    'filtering',
    'final decision',
    'finally',
    'find',
    'finding',
    'findings',
    'findings indicate',
    'fingerprints',
    'flat',
    'flattening',
    'flatter',
    'flawed',
    'floor',
    'focus',
    'focused',
    'focusing',
    'followed',
    'follows',
    'forbidden',
    'foremost',
    'form',
    'formulate',
    'forward',
    'forwarding',
    'forwards',
    'found',
    'fraction',
    'free',
    'frequency',
    'friends',
    'full',
    'full capabilities',
    'full scale',
    'full topology',
    'full topology',
    'fully dependent',
    'fully utilize',
    'function',
    'function receives',
    'functions',
    'furthest',
    'future',
    'future systems',
    'future tasks',
    'future work',
    'generate',
    'generate costs',
    'generate profit',
    'given',
    'given topology',
    'gives',
    'gives details',
    'glance',
    'global Internet',
    'global Internet topology',
    'global consensus',
    'globally reachable',
    'globe',
    'glues',
    'goal',
    'goals',
    'governments',
    'granularity',
    'gratitude',
    'greater',
    'green line',
    'group',
    'growth',
    'guarantee',
    'guarantee full protection',
    'guaranteed',
    'guaranteeing',
    'guarantees',
    'guidance',
    'hackers',
    'half',
    'hand',
    'handle',
    'happen',
    'happens',
    'hard',
    'harder',
    'hegemony',
    'help',
    'help towards',
    'hereafter',
    'heuristic',
    'hid',
    'hidden',
    'hidden interconnections',
    'hide',
    'hiding',
    'highlights',
    'hijack',
    'hijacked',
    'hijacker',
    'hijackers',
    'hijacking',
    'hijacks',
    'hinder',
    'hold',
    'hop',
    'hop count',
    'hop limit',
    'hop may',
    'hope',
    'hours',
    'huge impact',
    'huge percentage',
    'human errors',
    'ideally',
    'identification',
    'identified',
    'identify',
    'identify whether',
    'identifying',
    'identity',
    'ignore',
    'ignored',
    'illustrate',
    'illustrated',
    'illustrates',
    'immediate environment',
    'impact changes',
    'impactful',
    'impacts',
    'implement',
    'implementations',
    'implemented',
    'implementing',
    'importance',
    'important insights',
    'important services',
    'imposed restriction',
    'impossible',
    'improve',
    'improvement',
    'improvements',
    'improving',
    'inbound filtering',
    'included',
    'inconsistencies',
    'inconsistent',
    'increased',
    'increases',
    'independent',
    'index',
    'indicate',
    'indicated',
    'indicates',
    'indicating',
    'indications',
    'infeasible',
    'infeasible',
    'infer',
    'inference',
    'inferred',
    'inferring',
    'initial results indicated',
    'influence',
    'inform',
    'information based',
    'information provided',
    'information regarding',
    'infrastructure',
    'initialization',
    'initialization phase',
    'initiating',
    'input',
    'insight',
    'inspects',
    'instabilities',
    'install',
    'instead',
    'insufficient',
    'integers',
    'intend',
    'inter-domain links',
    'inter-domain routes',
    'inter-domain routing',
    'inter-domain techniques',
    'intercept',
    'intercepted traffic',
    'intercepting',
    'interception',
    'interceptions',
    'interconnected',
    'interconnections',
    'interesting',
    'interference',
    'intersecting',
    'interval',
    'introduces uncertainty',
    'intuition behind',
    'investigate',
    'investigation',
    'invisible',
    'involved',
    'involves',
    'issues',
    'items',
    'iterating',
    'iteration',
    'iteratively querying',
    'journey',
    'justification',
    'justified',
    'key',
    'key insight',
    'key observations',
    'key question',
    'key results',
    'kinds',
    'knowing',
    'knowledge',
    'labelled',
    'lack',
    'lacks',
    'larger',
    'larger number',
    'larger percentage',
    'latter',
    'lead',
    'lead toward',
    'leading',
    'leads',
    'learn',
    'learned',
    'learning',
    'learns',
    'leave',
    'led',
    'left',
    'left undone',
    'legend label',
    'length',
    'less',
    'less effective',
    'less likely',
    'less preferable',
    'less preferred',
    'less protection',
    'less relevant',
    'less useful',
    'less visible',
    'leveraged',
    'licentiate thesis',
    'lightweight approach',
    'likelihood',
    'likely',
    'likely become',
    'limit',
    'limitation',
    'limitations exist',
    'limitations regarding',
    'limitations suggest',
    'limited',
    'limited amount',
    'limited set',
    'limited visibility',
    'limiting',
    'limits',
    'line',
    'lines',
    'link',
    'link failure',
    'links',
    'list',
    'list goes',
    'listing',
    'literature',
    'literature review',
    'literature study',
    'live',
    'load',
    'local',
    'local dependence',
    'local network',
    'local network operators',
    'local policies',
    'local preference',
    'local preferences',
    'located',
    'location',
    'locations',
    'logged',
    'looking',
    'looking glasses',
    'looks',
    'lookup operation',
    'lookup operations',
    'loop iteration',
    'loops',
    'lot',
    'low-level point',
    'lower',
    'lowest',
    'lucky',
    'main advantage',
    'main incentive',
    'mainly',
    'maintain',
    'maintained',
    'maintaining',
    'majority',
    'making',
    'malicious',
    'manage',
    'manipulation',
    'manually',
    'map',
    'mapping',
    'mark',
    'marked',
    'match',
    'matter',
    'maximize',
    'maximizes',
    'maximizing',
    'maximizing',
    'maximum',
    'may',
    'may affect',
    'may allow',
    'may cause',
    'may happen',
    'may hold true',
    'may lead',
    'may still',
    'may threaten',
    'mean',
    'means',
    'measure',
    'measured',
    'measuring',
    'mechanism',
    'mechanisms',
    'median',
    'median number',
    'member',
    'mentioned',
    'merged',
    'met',
    'methods',
    'metric',
    'metrics',
    'million',
    'mind',
    'minimize',
    'minutes',
    'misconfigure',
    'missing links',
    'mitigation',
    'mitigation techniques',
    'mix',
    'mix together',
    'mixed together',
    'mobile networks',
    'modeled',
    'modeled based',
    'modeling choices',
    'modeling parameter',
    'modeling parameters',
    'modelled',
    'modification',
    'modified',
    'modifies',
    'modify',
    'modifying',
    'module',
    'monetary benefits',
    'monitor',
    'monitoring infrastructure',
    'monitoring infrastructures',
    'monitors',
    'month',
    'more-specific',
    'more/less specific',
    'multiple',
    'multiple insights',
    'multiple locations',
    'multiple options',
    'multiple peers',
    'multiple reports',
    'multiple simulations',
    'multiple solutions',
    'multiple steps',
    'multiple times',
    'multiple years ago',
    'multiplication factor',
    'mutual deployment',
    'naive',
    'naive approach works',
    'naive configuration',
    'nearby networks',
    'nearby routers',
    'necessarily guarantee',
    'necessarily translate',
    'necessity',
    'negative impact',
    'negative values indicate',
    'negatively impacts',
    'negligible',
    'neighbor',
    'neighboring',
    'neighboring domains',
    'neighbors',
    'neither',
    'network connectivity',
    'network dependencies',
    'network operators',
    'network topology',
    'networking devices',
    'networks peer',
    'networks peering',
    'networks use',
    'networks utilizing',
    'networks without',
    'network’s administrator',
    'network’s operator',
    'never announced',
    'never discovered',
    'never reported',
    'node',
    'nodes',
    'non-negligible impact',
    'non-negligible number',
    'non-optimal',
    'non-trivial',
    'none',
    'normal conditions',
    'notable',
    'note',
    'noted',
    'noted',
    'notice',
    'number',
    'number decreases',
    'number equal',
    'number increases',
    'numbers',
    'numerical values',
    'objectives',
    'observability',
    'observable',
    'observations indicate',
    'observe',
    'observed',
    'observing',
    'obtain revenue',
    'obtained',
    'obvious',
    'obvious things',
    'occur outside',
    'occurs',
    'offer',
    'offered',
    'offered',
    'offers',
    'offering',
    'omniscient',
    'on-wards',
    'ongoing',
    'operate',
    'operated',
    'operates',
    'operates',
    'operating',
    'operations',
    'operations specified',
    'operator specifies',
    'operators',
    'optimal',
    'optimal impact',
    'optimally utilize',
    'optimization',
    'optimizations',
    'optimize',
    'optimizing',
    'option',
    'optional',
    'options',
    'oracle',
    'oracle computes',
    'order',
    'ordering',
    'orders',
    'organized',
    'origin',
    'original',
    'originate',
    'originated',
    'originators',
    'other’s set',
    'outbound filtering',
    'outcome',
    'outcomes',
    'outdated',
    'output',
    'output filtering',
    'outside',
    'outside world',
    'overall flattening',
    'overall lower impact',
    'overestimation',
    'override',
    'overview',
    'owns',
    'packet',
    'packet based',
    'page',
    'pairs',
    'papers',
    'paragraphs',
    'parameters',
    'parts',
    'past',
    'past studies',
    'past work',
    'path length',
    'path towards',
    'paths may',
    'paths remaining',
    'paths seems',
    'peer',
    'peer-to-peer',
    'peering',
    'peering agreements',
    'peering link',
    'peering links',
    'peering neighbors',
    'peers',
    'peers propagate',
    'peers receive',
    'percentage',
    'percentage increases',
    'percentages',
    'percentile',
    'percentiles',
    'perfect knowledge',
    'perform',
    'perform different tasks',
    'performance issues',
    'performance optimizations',
    'performed',
    'performed using',
    'performs',
    'permission',
    'perspective',
    'pick',
    'picked',
    'pings',
    'pinpointing',
    'pipeline steps',
    'place',
    'placement',
    'placing',
    'plagued',
    'plane',
    'planes',
    'planned',
    'planning',
    'plus',
    'pointers',
    'poison',
    'poisoned',
    'poisoning',
    'poisons',
    'policies',
    'policies depend',
    'policy violations',
    'portrayed',
    'positions',
    'possible',
    'practice',
    'possibly',
    'possibly generate',
    'posting',
    'potential',
    'potential solution',
    'potentially',
    'potentially affecting',
    'potentially allow',
    'potentially attract',
    'potentially avoid',
    'potentially becoming visible',
    'potentially break',
    'potentially improve',
    'practice',
    'pre-computed',
    'precede',
    'precisely',
    'predefined frequent',
    'predict',
    'predicted',
    'prefer',
    'preferable',
    'preference',
    'preferences',
    'preferred',
    'preferring',
    'prefix',
    'prefixes',
    'prepend',
    'prepended',
    'prepending',
    'present',
    'presentation',
    'presented',
    'preserve',
    'preserved',
    'prevent',
    'previous',
    'previous examples',
    'previous findings',
    'previous node',
    'previous nodes',
    'previous section',
    'previous studies',
    'previous work',
    'previous year',
    'previously',
    'previously noted',
    'previously propagated',
    'prior research',
    'prior work',
    'private interconnections',
    'probes',
    'procedure',
    'proceed',
    'proceeds',
    'process repeats',
    'processes',
    'produce',
    'production use',
    'profit',
    'profit decisions',
    'profits',
    'project',
    'propagate',
    'propagated',
    'propagates',
    'propagating',
    'propagation',
    'propagator',
    'propagators',
    'properly reacting',
    'proportion',
    'proposals',
    'propose',
    'proposed',
    'proposed solutions',
    'protect',
    'protection',
    'protocol',
    'proved',
    'proved',
    'provide',
    'provided',
    'provider',
    'providers',
    'providing',
    'providing feedback',
    'proximity',
    'proximity matrices',
    'proximity matrix',
    'proximity value',
    'proximity values',
    'proxy',
    'public',
    'public access',
    'public defence',
    'public infrastructure',
    'publicly',
    'publicly accessible',
    'publicly disclose',
    'publicly provide',
    'publicly report',
    'publicly reported',
    'purpose',
    'purposes',
    'quantified',
    'quantifies',
    'quantify',
    'quantifying',
    'query',
    'querying',
    'question',
    'questions',
    'quickly',
    'quickly decide',
    'quickly detecting',
    'quickly identifying',
    'raises',
    'random',
    'random heuristic searching',
    'random victim',
    'randomization seed',
    'randomly select',
    'range',
    'rank',
    'rank degree',
    'ranking decisions',
    'rankings',
    'rapidly',
    'reach',
    'reachable',
    'reached',
    'reaching',
    'react',
    'readability',
    'reader',
    'ready',
    'real Internet',
    'real world',
    'real-time',
    'real-world',
    'real-world datasets',
    'realistic',
    'reality',
    'realize',
    'really',
    'reason',
    'reason behind',
    'reasoning behind',
    'reasons',
    'recall',
    'receive',
    'received',
    'receives',
    'receiving domain',
    'recent improvements',
    'recently',
    'recipient',
    'recognizing',
    'recommendations',
    'recomputed',
    'recomputes',
    'recursion',
    'recursive function',
    'red',
    'red line',
    'redirected',
    'rediscovered',
    'reduce',
    'reduced',
    'reduces',
    'reduction',
    'refer',
    'referred',
    'referring',
    'refers',
    'reflections',
    'refrain',
    'regard',
    'regarding',
    'regards',
    'region',
    'regions',
    'rejected',
    'relation',
    'relations',
    'relationships',
    'relevant',
    'reliability',
    'reliable',
    'rely',
    'remain',
    'remain hidden',
    'remain hidden',
    'remain unnoticed',
    'remainder',
    'remained stable',
    'remaining',
    'remaining hidden',
    'remains',
    'remains stable',
    'remove',
    'removing',
    'render',
    'repeat',
    'repeated',
    'replace',
    'reply',
    'replying',
    'report',
    'reported',
    'reporting',
    'reports',
    'representation',
    'represents',
    'requests',
    'required',
    'requirements',
    'requires',
    'rerouted traffic',
    'research',
    'research analysis',
    'research areas',
    'research community',
    'research considers',
    'research dimensions',
    'research led',
    'research methodology',
    'research methodology adopted',
    'research papers',
    'research question',
    'research questions',
    'research seeks',
    'researched',
    'researchers',
    'respect',
    'respectively',
    'responsible',
    'rest',
    'restriction',
    'restrictions',
    'restrictions allow',
    'restrictions meet',
    'restrictions propagated',
    'restrictive',
    'result',
    'resulting',
    'results arrive',
    'results capture',
    'results lead',
    'results regarding',
    'results shown',
    'results suggest',
    'retain',
    'retained',
    'retains',
    'retrieved',
    'return',
    'reverse engineering',
    'returns',
    'reveal',
    'revealing',
    'revenue',
    'reverse discovery',
    'reversed',
    'reviewing',
    'rich ecosystem',
    'rich inter-connectivity',
    'risk becoming visible',
    'risk poisoning',
    'risk propagating',
    'risks',
    'risky',
    'robust',
    'root',
    'root node',
    'roughly',
    'route',
    'route preference',
    'route preferences',
    'routed',
    'router',
    'routers',
    'routes',
    'routes disclosed',
    'routes exchanged',
    'routes received',
    'routes reported',
    'routes towards',
    'routing',
    'routing attack',
    'routing attacks',
    'routing decisions',
    'routing events',
    'routing hijack',
    'routing hijacks',
    'routing instabilities',
    'routing polices',
    'routing preferences',
    'routing protocols',
    'routing table',
    'routing table entries',
    'row contains',
    'rules',
    'runs',
    'safe',
    'safely maintained',
    'safely terminate',
    'safety',
    'said',
    'sample code',
    'samples',
    'say',
    'scale',
    'scaling percentage',
    'scanning',
    'scenario',
    'scenarios occurs',
    'scheduler',
    'scope',
    'scratch',
    'second',
    'second goal',
    'second part',
    'second path',
    'second set',
    'second step',
    'second variable',
    'seconds',
    'section',
    'section considers',
    'section considers scenarios',
    'section discusses',
    'section explains',
    'section investigates',
    'section studies',
    'section summarizes',
    'sections seek',
    'security',
    'security reasons',
    'seek',
    'seem',
    'seems',
    'seen',
    'select',
    'selected',
    'selected best path',
    'selected best paths',
    'selected candidate',
    'selected neighbors',
    'selected peers',
    'selecting',
    'selection mechanism',
    'selection criteria',
    'selection process',
    'selective export',
    'sender',
    'sending',
    'separate prefixes',
    'sequence',
    'serious threat',
    'service',
    'services hosted',
    'session',
    'session using',
    'set',
    'sets',
    'seven',
    'severely limit',
    'shape',
    'shaping',
    'sharper',
    'shorter',
    'shorter path',
    'shorter paths',
    'shortest',
    'shortest path',
    'shortest path length',
    'show',
    'show via simulations',
    'showed',
    'shown',
    'signal',
    'signals',
    'signals',
    'signed',
    'significance',
    'significant',
    'significant percentage',
    'significantly',
    'signing',
    'similar',
    'similar fashion',
    'similar-type',
    'similarly',
    'similations',
    'simple',
    'simplest form',
    'simplicity',
    'simplify',
    'simulate',
    'simulated Internet',
    'simulated Internet environment',
    'simulated Internet topology',
    'simulated pair',
    'simulated topology',
    'simulation',
    'simulation output',
    'simulation printer',
    'simulations',
    'simulations based',
    'simulations commonly',
    'simulations involving',
    'simulations show',
    'simulations show',
    'simulations show',
    'simulations shown',
    'simulations together',
    'simulator',
    'simulator model',
    'simulator’s results',
    'single',
    'single administrative domain',
    'single attack',
    'single datapoint',
    'single iteration',
    'single route',
    'single simulation fails',
    'single path',
    'single route',
    'single transit provider',
    'situations',
    'skip existing steps',
    'skip steps',
    'smaller fraction',
    'smaller percentage',
    'smarter variations',
    'software framework',
    'solutions',
    'solutions rely',
    'solve',
    'something',
    'sometimes exporting',
    'sometimes unavoidable',
    'sophistication',
    'sources',
    'space',
    'sparse set',
    'speaker',
    'special node',
    'specific',
    'specific case',
    'specific mechanisms',
    'specific prefixes',
    'specific type',
    'specifically',
    'specified',
    'split',
    'spread',
    'squatting',
    'stable routes',
    'stable state',
    'standalone',
    'standard',
    'standard rules',
    'standardized',
    'start',
    'state',
    'stated',
    'stated previously',
    'stated previously',
    'states',
    'static routes',
    'stay',
    'stealthier',
    'stealthiness',
    'stealthy',
    'steer',
    'step',
    'steps',
    'steps toward',
    'still',
    'still active',
    'still influence',
    'still maintaining',
    'still present',
    'stop',
    'stopped',
    'stored',
    'straightforward',
    'strategic',
    'strategic locations',
    'strategic placement',
    'strategically choosing',
    'strategically select',
    'strategies',
    'strategy',
    'stress',
    'stressed',
    'stricter',
    'stricter forms',
    'structure',
    'stub',
    'stub networks',
    'studied',
    'studies',
    'studying',
    'sub-figure',
    'submitted',
    'subsections',
    'subsequence',
    'subset',
    'subtracting',
    'succeed',
    'success rate',
    'successful',
    'successfully engineered',
    'successfully reach',
    'sufficient',
    'sufficiently',
    'sufficiently flexible',
    'sufficiently short',
    'suggest',
    'suggested',
    'suggestions',
    'suitable environment',
    'sum',
    'summarised',
    'summarize',
    'summarized',
    'summarizes',
    'summary',
    'supervisor',
    'support',
    'supporting',
    'sure',
    'surgical',
    'surgical use',
    'surgically affect',
    'surprisingly',
    'sustainability issues',
    'systems incur',
    'systems operating',
    'table',
    'tables',
    'tables illustrate',
    'tactically design',
    'tail',
    'taken',
    'target',
    'targeted',
    'tasks',
    'taxonomy',
    'techniques tend',
    'tell',
    'tens',
    'terminal',
    'terminal nodes',
    'terminate',
    'terms',
    'testbeds',
    'thank',
    'thesis addresses',
    'thesis consists',
    'thesis evaluates',
    'thesis examines',
    'thesis explored',
    'thesis focuses',
    'thesis investigates',
    'thesis seeks',
    'third',
    'though',
    'thousands',
    'threat scenarios',
    'threshold',
    'threshold serves',
    'tie-breakers',
    'tier-1 network',
    'tier-1 networks',
    'ties',
    'time-consuming',
    'times',
    'today’s',
    'tools',
    "today’s infrastructure",
    'today’s traffic',
    'tools',
    'top illustrate',
    'topological characteristics',
    'topological datasets',
    'topological information',
    'topological properties',
    'topological-based',
    'topologies',
    'topology',
    'topology contains',
    'topology datasets',
    'topology example',
    'topology modifications',
    'total',
    'towards',
    'toy example',
    'toy topology example',
    'traceroute',
    'traceroutes',
    'trade secret',
    'trade-off',
    'traditional',
    'traditional infrastructure',
    'traditional topology',
    'traditionally deliver',
    'traffic destined',
    'traffic engineering techniques',
    'traffic forwarded',
    'traffic load',
    'traffic redirection',
    'transient events',
    'transit',
    'transit networks',
    'transit provider networks',
    'transits',
    'translates',
    'trend',
    'triggered',
    'true',
    'trust',
    'trust',
    'trusted',
    'trying',
    'turn',
    'tweak',
    'twofold',
    'type',
    'types',
    'typically',
    'typically filtered',
    'unable',
    'unavailable',
    'unaware',
    'uncertain',
    'uncertainty',
    'uncommon',
    'uncover',
    'underlying assumption',
    'underlying security',
    'understand',
    'undesired effect',
    'undetectable',
    'unedited information',
    'unexpectedly deviate',
    'unless',
    'unlike',
    'unluckily select',
    'unlucky',
    'unnecessarily',
    'unobservable',
    'unsolved problem',
    'unstable',
    'update',
    'upper bound',
    'us',
    'use case',
    'use machine learning',
    'use secure protocols',
    'use symbolic labels',
    'useful',
    'user-maintained',
    'using',
    'using techniques',
    'usual',
    'usually',
    'usually considered',
    'usually implemented',
    'usually summarized',
    'utilised',
    'utilize',
    'utilize filters',
    'utilized',
    'utilizing',
    'valid',
    'valid strategy',
    'validate',
    'validity',
    'vantage points',
    'variable',
    'variables',
    'variables specified',
    'various factors',
    'various geographical regions',
    'various insights',
    'various modeling assumptions',
    'various percentiles',
    'vast majority',
    'verification',
    'verified',
    'verify',
    'verifying',
    'vertical line',
    'via',
    'victim',
    'victim commonly',
    'victim’s',
    'view',
    'visibility',
    'visibility',
    'visible',
    'visualizes',
    'vulnerable',
    'ways',
    'well',
    'well observed',
    'well-connected',
    'well-known',
    'well-researched',
    'whatever',
    'wherein',
    'whether',
    'whole Internet',
    'whole community',
    'whole group',
    'whole topology',
    'widely accepted',
    'widely available',
    'widely deployed cases',
    'widely supported',
    'widely utilised',
    'wild',
    'withdrawn',
    'without',
    'without applying',
    'words',
    'work based',
    'work suggests',
    'world',
    'worse',
    'worst',
    'worth noting',
    'worthy',
    'written',
    'year',
    'years',
    'years ago',
    'yet',
    'zero',
    'zero false positives',
    'zero means',
    'zero visibility',
    'zombies',
    '1st',
    'According',
    'Afterwards',
    'Again',
    'Analysis',
    'Announcement',
    'Announcements',
    'Announcing',
    'Archipelago',
    'Autonomous System',
    'Autonomous Systems',
    'Based',
    'Based upon',
    'Based upon looking',
    'Baseline',
    'Capabilities',
    'Choosing',
    'Code showing',
    'Compared',
    'Comparison',
    'Compute',
    'Computing',
    'Conditions',
    'Consider',
    'Conversely',
    'Country',
    'Country hegemony',
    'Current',
    'Degree',
    'Delimitations',
    'Department',
    'Depending',
    'Depending upon',
    'Deploying',
    'Despite',
    'Details',
    'Discovering',
    'Documented parameters',
    'Engineered',
    'Engineering',
    'Evaluation',
    'Forwarding Information Base',
    'Example',
    'Examples',
    'Exceptions',
    'Experimental Design',
    'Factor',
    'Fourth',
    'Given',
    'Global',
    'Goals',
    'IP',
    'IP addresses',
    'IP addresses',
    'IP destination address',
    'IP destination addresses',
    'IP prefix',
    'Identifying',
    'Improving',
    'Indeed',
    'Indeed',
    'Information',
    'Initial space',
    'Inputs',
    'Internal Border Gateway Protocol',
    'Internet Exchange Point',
    'Internet Service Provider',
    'Internet Topology',
    'Internet based',
    'Internet consists',
    'Internet consists',
    'Internet depends upon',
    'Internet ecosystem',
    'Internet layer',
    'Internet simulator',
    'Internet simulators',
    'Internet topologies',
    'Internet topology',
    "Internet’s topology",
    'Iterate',
    'JSON format',
    'Key',
    'Key observations',
    'Less-specific',
    'Licentiate thesis contributes',
    'Licentiate thesis focuses',
    'Licentiate thesis investigated',
    'Limitation example',
    'Limitations',
    'Limitations regarding',
    'Local Preferences',
    'Logical model',
    'Measured metrics',
    'Observing',
    'Obviously',
    'Optionally',
    'Originators',
    'Presence',
    'Python code example',
    'Python dictionaries',
    'Query',
    'Recent improvements',
    'Special case',
    'Strategic Locations',
    'Sustainable Development Goals',
    'Whether realistic',
    'X coordinate',
    'X percent',
    'Y-axis indicate',
    'Yet adding',
    'abnormal networking conditions',
    'accurate decisions',
    'accurate results given',
    'accurately geolocate',
    'achieved wider deployment',
    'action',
    'active probing measurements',
    'actively disclose',
    'actively report',
    'actual code',
    'actual dataset',
    'actual limitations',
    'actual traffic',
    'actually filter',
    'actually receive',
    'actually worse',
    'adversary',
    'affected networks',
    'affected region',
    'affected service',
    'agreements established',
    'allow operators',
    'alternative paths',
    'answer whether',
    'apply advanced filtering practises',
    'approaches usually face',
    'article written',
    'attack based',
    'attack choices',
    'attack outcomes',
    'attack strategies',
    'attack type',
    'attack types',
    'automatically accepted',
    'autonomous networks',
    'available access points',
    'avoid detection',
    'avoid propagating',
    'avoid service disruption',
    'backup paths',
    'best path',
    'best paths',
    'best representation',
    'best route',
    'best route towards',
    'best routes',
    'best routes observed',
    'best routes reported',
    'best-path',
    'better performance',
    'better protection',
    'better quantify',
    'better utilize',
    'beyond imposed restriction',
    'biased observation',
    'biased view',
    'blackhole',
    'blackholed',
    'blackholing',
    'break ties',
    'broad deployment',
    'broken using',
    'buddies',
    'canaries',
    'causing disruption',
    'censor content',
    'change frequently',
    'chapter considers experiments',
    'circumstances may exist',
    'classification involves',
    'clearly effective',
    'closer location',
    'code block',
    'code increases',
    'collaborating network',
    'combining sources',
    'commonly corrupt',
    'commonly corrupt',
    'commonly design',
    'commonly established',
    'commonly implemented',
    'commonly inviable unless',
    'commonly model',
    'commonly observes',
    'commonly outside',
    'commonly poisoned',
    'commonly summarized',
    'commonly visible',
    'communicated via',
    'compact view',
    'comparative research approach',
    'comparison metric',
    'compelling metric',
    'complete knowledge',
    'completely different pattern',
    'completely evade detection',
    'completely secure',
    'complex configurations exist',
    'complex filtering policies',
    'comprehensive description',
    'compromised router',
    'computationally expensive procedure',
    'computationally intensive problem',
    'compute proximity',
    'conflicting goals',
    'congestion',
    'consider thousands',
    'considered inadvisable',
    'consistency reasons',
    'consistent measurement',
    'consistent view',
    'consistently benefit',
    'control plane',
    'core routers',
    'corrupted routes',
    'counter-measures',
    'cross-reference',
    'crucial',
    'crucial service',
    'cryptographic',
    'cryptographic-based',
    'cryptographic-based systems',
    'cryptographically sign',
    'cryptographically verify',
    'current node',
    'current state',
    'current tools',
    'current version',
    'customer cone',
    'customer may',
    'customer networks',
    'customer pays',
    'datapoint value',
    'datapoint values',
    'datasets sources',
    'datasets utilized',
    'decimal strings',
    'decision step',
    'decisions resulted',
    'defend',
    'defense side',
    'define feasible success',
    'defined routing policies',
    'detection systems',
    'determine reachability',
    'developing machine learning methodologies',
    'different categories',
    'different data granularity',
    'different filtering models',
    'different levels',
    'different numbers',
    'different pairs',
    'different path',
    'difficulty lies',
    'digital economy',
    'discovered information',
    'dynamic interconnections',
    'dynamically choosing',
    'dynamically configuring',
    'dynamically selecting',
    'ease',
    'easily corrupt',
    'eavesdropping',
    'economic benefits',
    'economic incentives',
    'enabling autonomy',
    'equal-length paths',
    'equally preferred path',
    'evade detection',
    'evading detection',
    'ever-changing economic relationships',
    'everything remains consistent among',
    'exchange routing information',
    'exchange traffic',
    'exchanged BGP messages',
    'exchanged routing information',
    'expect attacks',
    'experimental topology',
    'export routes',
    'exported route',
    'express',
    'extract fingerprints',
    'false IP addresses',
    'false positive rate',
    'feasible impact',
    'feasibly perform',
    'feasibly utilize',
    'filtering may',
    'filtering mechanisms',
    'filtering operations applied',
    'filtering policies',
    'filtering techniques',
    'filters',
    'filters reduce',
    'final configuration parameters',
    'final paths',
    'final process',
    'fine tune',
    'flatter Internet',
    'focuses',
    'for-profit organizations',
    'for/else',
    'forward traffic',
    'forwarding hop',
    'found ground truth',
    'found sufficient',
    'future Internet topologies',
    'future decryption',
    'heuristic utilized',
    'highest degree',
    'hood',
    'hops',
    'host',
    'hot-potato IGP routing',
    'important',
    'inconsistently updated view',
    'incorrect decisions',
    'independent replica',
    'indicate little',
    'indication',
    'industrial routers',
    'industry started',
    'inference error',
    'infinite restriction',
    'intercontinental networks',
    'interdomain systems',
    'legitimate clients',
    'less preferred route',
    'likely IXP0',
    'limit internal congestion',
    'limited number',
    'limited propagation',
    'lines across',
    'links observed',
    'local-preferences',
    'located somewhere',
    'longest prefix match',
    'loop avoidance algorithm',
    'loop doesn’t break',
    'lower overhead',
    'maintained path',
    'maintained paths',
    'major obvious things',
    'malformed routes',
    'malicious activity',
    'malicious incidents',
    'malicious path',
    'malicious route',
    'malicious routes',
    'malicious routing events',
    'mapping equipment failures',
    'may manipulate',
    'may prepend',
    'may select',
    'may unexpectedly observe',
    'minimum information',
    'mining pools',
    'minutes depending',
    'minutes respectively',
    'modified infrastructure',
    'modified version',
    'more-specific prefixes',
    'more/less specific prefix',
    'motivates',
    'motivation',
    'motivation behind',
    'naive attacker',
    'natural consequence',
    'network represents',
    'networks affect',
    'networks behave',
    'networks destined',
    'networks exchanging routes',
    'networks hosting',
    'networks illustrated',
    'networks implement',
    'networks included',
    'networks rely',
    'nodes discovered',
    'nodes rediscovered',
    'non-stealthy',
    'non-trivial part',
    'normal routing conditions',
    'notable metric',
    'notable parameter',
    'observing changes',
    'offer transit',
    'old best path',
    'old path',
    'originally considered',
    'originally designed',
    'paper published',
    'parameters documented',
    'paramount importance',
    'partial recovery',
    'participating networks',
    'particular example',
    'passively operate',
    'path attribute',
    'path back',
    'paths advertised',
    'paths based',
    'paths disclosed',
    'paths extracted',
    'peering agreements established',
    'peering links established',
    'peering locations',
    'peers based',
    'peers agree',
    'peers choose',
    'peers chosen',
    'peers disclose',
    'peers expressed',
    'peers installs',
    'peers selected',
    'peer† receives',
    'percentages correspond',
    'percentages translate',
    'potential evolution',
    'potential existence',
    'potential future work',
    'potential modifications',
    'potentially invulnerable',
    'potentially missing',
    'prefix changes',
    'prefix propagated',
    'previous best path',
    'previous discovered node',
    'previously discovered adjacent nodes',
    'propagated route',
    'propagating routes',
    'propagation policies',
    'propagation process',
    'propagation rule',
    'propagation speed',
    'proposed operating',
    'protection capabilities',
    'protection defences',
    'proven',
    'provide real-time information',
    'provide topological information',
    'provided public datasets',
    'purposely craft',
    'purposely trigger',
    'python dictionary data-structure using',
    'randomly chosen paths',
    'randomly selected groups',
    'rank representation',
    'ranks dataset',
    'rarely poisoned',
    'rarely propagate',
    'reachability information',
    'real-time monitors',
    'real-time report',
    'real-world misconfiguration',
    'realistic adversary',
    'realistic attacker',
    'realistic future scenarios',
    'received path',
    'received route',
    'recursion termination condition',
    'reflect',
    'relationship dataset',
    'relevant background information',
    'relevant literature',
    'reliable infrastructure',
    'remain stealthy',
    'repeated executions',
    'research reported',
    'respective knowledge',
    'route offered',
    'route servers',
    'route towards',
    'route traffic',
    'router randomly',
    'routers negotiate',
    'routes advertised',
    'routes announced',
    'routing policies',
    'scenarios',
    'second scenario',
    'secretly interfering',
    'secure internet routing',
    'select routes',
    'selected advertising',
    'selection',
    'selection choice',
    'similar tactic',
    'simulated',
    'simulator consists',
    'specific ASN',
    'specific IP prefix',
    'specific IP prefixes',
    'stability',
    'tie- breaking mechanism',
    'tie-breaking mechanisms',
    'topology consisting',
    'topology visible',
    'total routes',
    'tweak',
    'unannounced prefix',
    'understood',
    'undesirable side effect',
    'undesirable updates',
    'visibility constraints',
    'visible across',
    'well-connected networks',
    'Hijack',
    'Hijacker',
    'Hijackers',
    'Internet compared',
    'Internet example shown',
    'Internet-wide simulations',
    'Internet-wide topologies',
    'Internet’s core routers',
    'adjacent neighbors',
    'advanced filters',
    'advanced forms',
    'algorithm consists',
    'algorithms work',
    'allow loops',
    'associative arrays',
    'background information related',
    'bandwidth-consuming',
    'correct combination',
    'dict',
    "domain’s ASN",
    "domain’s administrators",
    'full Internet',
    'full Internet topology',
    'heavily interconnected',
    'DNS servers',
    'Datastructure computed',
    'Domain Name System',
    'Man-in-the- middle',
    'Man-in-the-middle',
    'Multiple papers',
    'Mutually Agreed Norms',
    'Modeling Choices',
    'NP-hard problem',
    'Neighbor',
    'Point',
    'Poisoning',
    'TCP session',
    'Typically',
    'algorithm receives',
    'algorithm starts',
    'bool',
    'communication towards',
    'complex propagation policies',
    'requires knowledge',
    'reroute',




    # typical names
    'Alice',
    'Bob',
    'Eve',

    # things
    'bitcoin',
    'nmap',


    # Companies, countries, and organizations
    'Cisco',
    'Cogent',
    'Hurricane Electric',
    'Level3',
    'North American Network Operators’ Group',
    'Telia',
    'Twitter',
    'United States',
    'United Kingdom',
    'United Nations',
    'UN',


    # days of the week
    'Monday',
    'Tuesday',
    'Wednesday',
    'Thursday',
    'Friday',
    'Saturday',
    'Sunday',

    # names of the months
    'January',
    'February',
    'March',
    'April',
    'May',
    'June',
    'July',
    'August',
    'September',
    'October',
    'November',
    'December',


    # places
    'Electrum',
    'Kistagången',
    'Myanmar',
    'Stockholm',
    'Sweden',


    # Swedish qords (Sgqm)
    'Nyckelord',
]
WordsToFilterOutSet=set(WordsToFilterOut)


def is_integer(s):
    """
    Returns True if the string s can be converted to an integer, False otherwise.
    """
    try:
        int(s)
        return True
    except ValueError:
        return False

# both 10% and 10th
def is_percentage(s):
    if len(s) > 1 and s[-1] == '%' and is_integer(s[:-1]):
        return True
    if len(s) > 2 and s[-2:] == 'th' and is_integer(s[:-2]):
        return True
    return False


ligrature_table= {'\ufb00': 'ff', # 'ﬀ'
                  '\ufb03': 'f‌f‌i', # 'ﬃ'
                  '\ufb04': 'ffl', # 'ﬄ'
                  '\ufb01': 'fi', # 'ﬁ'
                  '\ufb02': 'fl', # 'ﬂ'
                  '\ua732': 'AA', # 'Ꜳ'
                  '\ua733': 'aa', # 'ꜳ'
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
                  '\u1e9e': 'SS', # 'ẞ' -- rather than 'fs' replace with 'SS'
                  '\u00df': 'ss', # 'ß' -- rather than 'fz', replace with 'ss'
                  '\ufb06': 'st', # 'ﬆ'
                  '\ufb05': 'ſt', # 'ﬅ'  -- long ST
                  '\ua728': 'Tz', # 'Ꜩ'
                  '\ua729': 'tz', # 'ꜩ'
                  '\u1d6b': 'ue', # 'ᵫ'
                  '\uab63': 'uo', # 'ꭣ'
                  #'\u0057': 'UU', # 'W'
                  #'\u0077': 'uu', # 'w'
                  '\ua760': 'VY', # 'Ꝡ'
                  '\ua761': 'vy', # 'ꝡ'
                  # 
                  # '\u0238': 'db', # 'ȸ'
                  # '\u02a3': 'dz', # 'ʣ'
                  # '\u1b66': 'dʐ', # 'ꭦ'
                  # '\u02a5': 'dʑ', # 'ʥ'
                  # '\u02a4': 'dʒ', # 'ʤ'
                  # '\u02a9': 'fŋ', # 'ʩ'
                  # '\u02aa': 'ls', # 'ʪ'
                  # '\u02ab': 'lz', # 'ʫ'
                  # '\u026e': 'lʒ', # 'ɮ'
                  # '\u0239': 'qp', # 'ȹ'
                  # '\u02a8': 'tɕ', # 'ʨ'
                  # '\u02a6': 'ts', # 'ʦ'
                  # '\uab67': 'tʂ', # 'ꭧ'
                  # '\u02a7': 'tʃ', # 'ʧ'
                  # '\uab50': 'ui', # 'ꭐ'
                  # '\uab51': 'ui', # 'ꭑ' -- turned ui
                  # '\u026f': 'uu', # 'ɯ'
                  # # digraphs with single code points
                  # '\u01f1': 'DZ', # 'Ǳ'
                  # '\u01f2': 'Dz', # 'ǲ'
                  # '\u01f3': 'dz', # 'ǳ'
                  # '\u01c4': 'DŽ', # 'Ǆ'
                  # '\u01c5': 'Dž', # 'ǅ'
                  # '\u01c6': 'dž', # 'ǆ'
                  # '\u0132': 'IJ', # 'Ĳ'
                  # '\u0133': 'ij', # 'ĳ'
                  # '\u01c7': 'LJ', # 'Ǉ'
                  # '\u01c8': 'Lj', # 'ǈ'
                  # '\u01c9': 'lj', # 'ǉ'
                  # '\u01ca': 'NJ', # 'Ǌ'
                  # '\u01cb': 'Nj', # 'ǋ'
                  # '\u01cc': 'nj', # 'ǌ'
                  # '\u1d7a': 'th', # 'ᵺ'
                  }

def replace_ligature(s):
    """
    Replaces all ligatures in a string with their expanded equivalents in a single pass.
    """
    if not s:
        return s

    # 1. Create a regex pattern by joining all ligature keys with the OR operator '|'
    # The keys are escaped to handle any special regex characters.
    ligature_keys = sorted(ligrature_table.keys(), key=len, reverse=True)
    pattern = re.compile("|".join(re.escape(key) for key in ligature_keys))

    # 2. Define a lookup function for re.sub()
    def lookup(match):
        return ligrature_table[match.group(0)]

    # 3. Use re.sub with the lookup function to perform all replacements
    return pattern.sub(lookup, s)

abbreviations_map = {
    'i.e.': 'id est',
    'e.g.': 'for example',
    'et al.': 'et alii', # 'and others'
    'etc.': 'et cetera',
    'vs.': 'versus',
    'Dr.': 'Doctor',
    'Prof.': 'Professor',
    'prof.': 'professor',
    'Mr.': 'Mister',
    'Mrs.': 'Missus',
    'Ms.': 'Miss',
    'U.S.': 'United States',
    'U.K.': 'United Kingdom',
    'Inc.': 'Incorporated',
    'Ltd.': 'Limited',
    'M.Sc.': 'Master of Science', # Must come before M.S.
    'M.S.': 'Master of Science',
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

def remove_suffixes(wl):
    # Sort suffixes by length (longest first) to fix the bug.
    # This ensures '<=' is checked before '='.
    suffixes = sorted(['-', '–', '>', '≤', '=', '<=', '*', '**', '†', '††', '‡', '‡‡', '§', '§§', '¶', '¶¶', '∥', '∥∥'], key=len, reverse=True)
    
    new_wl = []
    
    # 1. Loop through the word list (wl) ONCE.
    for w in wl:
        found_suffix = False
        
        # 2. For each word, check all suffixes.
        for s in suffixes:
            if w.endswith(s):
                # 3. If a match is found, strip it and break the inner loop.
                new_wl.append(w[:-len(s)].strip())
                found_suffix = True
                break # Suffix found, move to the next word
                
        # 4. If no suffix was found for this word, append the original word.
        if not found_suffix:
            new_wl.append(w)
            
    return new_wl

def remove_prefixes(wl):
    # Sort prefixes by length (longest first) to fix the bug.
    # This ensures '††' is checked before '†'
    prefixes = sorted(['*', '**', '†', '††', '‡', '‡‡', '§', '§§', '¶', '¶¶', '∥', '∥∥'], key=len, reverse=True)
    
    new_wl = []
    
    # 1. Loop through the word list (wl) ONCE.
    for w in wl:
        found_prefix = False
        
        # 2. For each word, check all prefixes.
        for s in prefixes:
            if w.startswith(s):
                # 3. If a match is found, strip it and break the inner loop.
                new_wl.append(w[len(s):].strip())
                found_prefix = True
                break # prefix found, move to the next word
                
        # 4. If no prefix was found for this word, append the original word.
        if not found_prefix:
            new_wl.append(w)
            
    return new_wl


def compute_column_positions(current_page_words):
    global Verbose_Flag
    global header_bottom
    all_x0_values = []

    for idx, b in enumerate(current_page_words):
        x0, y0, x1, y1, word, block_no, line_no, word_no=b
        if y1 < header_bottom + 0.01:
            continue
        all_x0_values.append(round(x0))

    # Count the frequency of each x0 value.
    x0_counts = Counter(all_x0_values)
    
    # Get the two most common x0 values and their counts.
    # .most_common(2) returns a list of [ (value, count), (value, count) ]
    most_common_x0 = x0_counts.most_common(2)

    if len(most_common_x0) < 2:
        print("Could not find two distinct column positions.")
        return None, None
    
    # Extract just the x0 values from the result.
    column1_x0 = most_common_x0[0][0]
    column2_x0 = most_common_x0[1][0]
    
    # Ensure column1 is always the leftmost one.
    if column1_x0 < column2_x0:
        return column1_x0, column2_x0
    else:
        return column2_x0, column1_x0

def collect_acronyms_from_page(pageno, page):
    global Verbose_Flag
    global acronyms_dict
    global header_bottom

    potential_key = ""
    potential_value = ""
    last_line_number=0
    last_block_no=0
    current_page_words=page.get_text("words", sort=True) # get plain text encoded as UTF-8
    column1, column2 = compute_column_positions(current_page_words)
    print(f"{column1=}, {column2=}")

    for idx, b in enumerate(current_page_words):
        x0, y0, x1, y1, word, block_no, line_no, word_no=b
        if y1 < header_bottom + 0.01:
            continue
        if Verbose_Flag:
            print(f"acronyms {idx} {b}")


        if x0 < (column2 - 1):
            if block_no > last_block_no or line_no > last_line_number:
                last_block_no = block_no
                # if this is a new line number, then it is a new key - save old key and value
                last_line_number = line_no
                potential_key = potential_key.strip()
                potential_value = potential_value.strip()
                if len(potential_key) > 0 and len(potential_value) > 0:
                    # filter out heading on first page of the list of acronyms and abbreviations
                    if potential_key.lower() != 'list of acronyms':
                        acronyms_dict[potential_key] = potential_value
                        if Verbose_Flag:
                            print(f"{potential_key.strip()} = {potential_value.strip()}")
                    potential_key = ""
                    potential_value = ""
                    
            potential_key += word + ' '

        if x0 > (column2 - 1):
            potential_value += word + ' '

    # save last key and value
    if len(potential_key.strip()) > 0 and len(potential_value.strip()) > 0:
        acronyms_dict[potential_key.strip()] = potential_value.strip()
        if Verbose_Flag:
            print(f"{potential_key.strip()} = {potential_value.strip()}")



def extract_text_from_pdf(pdf_path):
    """
    Extracts text from a PDF file, splits it by stopwords and punctuation,
    and saves it to a text file.
    """
    global Verbose_Flag
    global acronyms_found
    global acronyms_text
    global header_bottom

    try:
        doc = pymupdf.open(pdf_path)
        print(f"Successfully opened '{pdf_path}'...")

        full_text = ""
        # Extract text from all pages
        # for page in doc:
        #     full_text += page.get_text()

        acronyms_text = ""

        acronyms_found=False
        first_page_found=False
        references_found=False
        header_bottom=0
        for pageno, page in enumerate(doc): # iterate the document pages
            if Verbose_Flag:
                print(f"{pageno=}")
            current_page=page.get_text("blocks", sort=True) # get plain text encoded as UTF-8

            for idx, b in enumerate(current_page):
                if Verbose_Flag:
                    print(f"**** {idx=} {type(b)}****")
                x0, y0, x1, y1, lines_in_the_block, block_no, block_type=b
                if Verbose_Flag:
                    print(f"{x0=}, {y0=}, {x1=}, {y1=}, {lines_in_the_block=}, {block_no=}, {block_type=}")

                # look for the first abstract page and use the bottom of its bounding box as the bottom of the header
                if header_bottom == 0 and lines_in_the_block.startswith('Abstract |'):
                    header_bottom = y1
                    print(f"found header_bottom {header_bottom}")
                    continue
                
                # We assume that the lis tof acronyms is before the first page of the main matter
                # and has the expected header.
                # look for acronyms
                if header_bottom > 0 and not acronyms_found and (lines_in_the_block.startswith('List of Acronyms and abbreviations | ') or lines_in_the_block.startswith('List of acronyms and abbreviations | ')):
                    acronyms_found=True
                    print(f"found acronyms {pageno}")

                # collect acronyms
                if acronyms_found and not first_page_found:
                    if y1 > header_bottom and not lines_in_the_block.lower() == 'list of acronyms and abbreviations\n':
                        acronyms_text += lines_in_the_block
                        collect_acronyms_from_page(pageno, page)
                        break # go to the next page

                # look for first page of the main matter
                if header_bottom > 0 and not first_page_found and lines_in_the_block.endswith(' | 1\n'):
                    first_page_found = True
                    print(f"found first page {pageno}")

                # look for first of the references
                if header_bottom > 0 and first_page_found and not references_found and lines_in_the_block.lower().startswith('references | '):
                    references_found=True
                    print(f"found references page {pageno}")

                # if we are in the main matter and before the start of the references
                if y1 > header_bottom and first_page_found and not references_found:
                    full_text += lines_in_the_block
                else:
                    continue

        full_text=replace_ligature(full_text)
        full_text=replace_abbreviations(full_text)
        #print(f"****{full_text=}****")

        # --- NEW LOGIC TO SPLIT TEXT ---
        
        # 1. Define a regex pattern for splitting.
        # This splits the text by any whitespace or by the desired punctuation marks.
        # The parentheses () ensure the delimiters (spaces and punctuation) are kept.
        #splitter_pattern = re.compile(r'(\s+|[.,?!:;()#"“”])')
        # The new, corrected pattern with escaped brackets and braces:
        splitter_pattern = re.compile(r'(\s+|[.,?!:;()#"“”\[\]\{\}\+\∗×•∗])')
        
        tokens = splitter_pattern.split(full_text)

        # 2. Reconstruct the text, creating newlines around delimiters.
        output_lines = []
        current_phrase = ""
        for token in tokens:
            # Ignore empty strings or tokens that are only whitespace
            if not token or token.isspace():
                continue

            cleaned_token = token.strip().lower()
            is_stopword = cleaned_token in StopWordsSet
            # A simple check if the token itself is one of the punctuation marks
            is_punctuation = cleaned_token in {'.', ',', '?', '!', ':', ';', '(', ')', '"', '“', '”', '|', '#', '[', ']', '{', '}', '×', '*', '•', '∗', '+'}

            if is_stopword or is_punctuation or is_integer(token) or is_percentage(token):
                # If we were building a phrase, add it to the output first.
                if current_phrase:
                    output_lines.append(current_phrase.strip())
                    current_phrase = ""
                # Add the delimiter (stopword/punctuation) as its own line.
                if not options.stop:
                    output_lines.append(token)
            else: # It's a normal word
                # Append the word to the current phrase, adding a space if needed.
                if not current_phrase:
                    current_phrase = token
                else:
                    current_phrase += " " + token
        
        # Add any leftover phrase at the end of the text
        if current_phrase:
            output_lines.append(current_phrase.strip())

        # remove the start of some lines
        output_lines = [l[2:] if l.startswith('% ') else l for l in output_lines]
        output_lines = [l[2:] if l.startswith('= ') else l for l in output_lines]

        output_lines = [l for l in output_lines if l not in WordsToFilterOutSet]

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if 'doc' in locals() and doc:
            doc.close()

    return output_lines


def group_by_prefix(phrase_list, min_group_size=2):
    """
    Groups phrases by their first word (prefix).
    """
    prefix_groups = defaultdict(list)
    
    for phrase in phrase_list:
        words = phrase.split()
        if len(words) > 1:
            prefix = words[0].strip()
            # Ignore groups based on a stopword
            if prefix.lower() not in StopWords:
                prefix_groups[prefix].append(phrase)
    
    # Filter out groups that are too small to be meaningful
    return {
        prefix: members for prefix, members in prefix_groups.items()
        if len(members) >= min_group_size
    }

def group_by_suffix(phrase_list, min_group_size=2):
    """
    Groups phrases by their last word (suffix).
    """
    suffix_groups = defaultdict(list)
    
    for phrase in phrase_list:
        words = phrase.split()
        if len(words) > 1:
            suffix = words[-1].strip()
            # Ignore groups based on a stopword
            if suffix.lower() not in StopWords:
                suffix_groups[suffix].append(phrase)
    
    # Filter out groups that are too small to be meaningful
    return {
        suffix: members for suffix, members in suffix_groups.items()
        if len(members) >= min_group_size
    }



def remove_known_words(output_lines, well_known_acronyms):
    remove_list=[]
    for w in output_lines:
        if w in common_english.top_100_English_words:
            remove_list.append(w)
            continue

        if w in common_english.thousand_most_common_words_in_English:
            remove_list.append(w)
            continue

        if w in common_english.common_English_words:
            remove_list.append(w)
            continue

        if w in common_english.chemical_elements_symbols:
            remove_list.append(w)
            continue

        if w in common_english.chemical_elements:
            remove_list.append(w)
            continue

        if w in common_english.programming_keywords:
            remove_list.append(w)
            continue

        if w in common_english.language_tags:
            remove_list.append(w)
            continue

        if w in common_english.KTH_ordbok_English_with_CEFR:
            remove_list.append(w)
            continue

        if w in common_english.common_units:
            remove_list.append(w)
            continue

        if w in common_english.amino_acids:
            remove_list.append(w)
            continue

        if w in common_english.binary_prefixes:
            remove_list.append(w)
            continue

        if w in common_english.decimal_prefixes:
            remove_list.append(w)
            continue

        if w in common_english.place_names:
            remove_list.append(w)
            continue

        if w in well_known_acronyms:
            remove_list.append(w)
            continue

        if w in common_english.chemical_names_and_formulas:
            remove_list.append(w)
            continue

        if w in common_english.common_urls:
            remove_list.append(w)
            continue

        if w in common_english.java_paths:
            remove_list.append(w)
            continue

        if w in common_english.company_and_product_names:
            remove_list.append(w)
            continue

        if w in common_english.common_programming_languages:
            remove_list.append(w)
            continue

        if w in common_english.names_of_persons:
            remove_list.append(w)
            continue

        if w in common_english.mathematical_words_to_ignore:
            remove_list.append(w)
            continue

        if w in common_english.miss_spelled_words:
            remove_list.append(w)
            continue

        if w in common_english.common_latin_words:
            remove_list.append(w)
            continue

        # consider lower case version
        if w.lower() in common_english.top_100_English_words:
            remove_list.append(w.lower())
            continue

        if w.lower() in common_english.thousand_most_common_words_in_English:
            remove_list.append(w.lower())
            continue

        if w.lower() in common_english.common_English_words:
            remove_list.append(w.lower())
            continue

        if w.lower() in common_english.chemical_elements_symbols:
            remove_list.append(w.lower())
            continue

        if w.lower() in common_english.chemical_elements:
            remove_list.append(w.lower())
            continue

        if w.lower() in common_english.programming_keywords:
            remove_list.append(w.lower())
            continue

        if w.lower() in common_english.language_tags:
            remove_list.append(w.lower())
            continue

        if w.lower() in common_english.KTH_ordbok_English_with_CEFR:
            remove_list.append(w.lower())
            continue

        if w.lower() in common_english.common_units:
            remove_list.append(w.lower())
            continue

        if w.lower() in common_english.amino_acids:
            remove_list.append(w.lower())
            continue

        if w.lower() in common_english.binary_prefixes:
            remove_list.append(w.lower())
            continue

        if w.lower() in common_english.decimal_prefixes:
            remove_list.append(w.lower())
            continue

        if w.lower() in common_english.place_names:
            remove_list.append(w.lower())
            continue

        if w.lower() in well_known_acronyms:
            remove_list.append(w.lower())
            continue

        if w.lower() in common_english.chemical_names_and_formulas:
            remove_list.append(w.lower())
            continue

        if w.lower() in common_english.common_urls:
            remove_list.append(w.lower())
            continue

        if w.lower() in common_english.java_paths:
            remove_list.append(w.lower())
            continue

        if w.lower() in common_english.company_and_product_names:
            remove_list.append(w.lower())
            continue

        if w.lower() in common_english.common_programming_languages:
            remove_list.append(w.lower())
            continue

        if w.lower() in common_english.names_of_persons:
            remove_list.append(w.lower())
            continue

        if w.lower() in common_english.mathematical_words_to_ignore:
            remove_list.append(w.lower())
            continue

        if w.lower() in common_english.miss_spelled_words:
            remove_list.append(w.lower())
            continue
        
        if w in common_english.common_latin_words:
            remove_list.append(w.lower())
            continue

        else:
            print(f"'{w}' not in common_English_words")

    return remove_list


def main():
    global Verbose_Flag
    global options
    global acronyms_found
    global acronyms_text
    global acronyms_dict


    parser = optparse.OptionParser()
    parser.add_option('-v', '--verbose',
                      dest="verbose",
                      default=False,
                      action="store_true",
                      help="Print lots of output to stdout")

    parser.add_option('-s', '--stop',
                      dest="stop",
                      default=False,
                      action="store_true",
                      help="remove stopwords and pubctuation from output")


    options, remainder = parser.parse_args()
    Verbose_Flag = options.verbose


    if Verbose_Flag:
        print(f"ARGV      : {sys.argv[1:]}")
        print(f"VERBOSE   : {options.verbose}")
        print(f"REMAINING : {remainder}")

    if len(remainder) != 1:
        print("Usage: ./extract_text_from_PDF.py [-v] <PDF_file>")
        sys.exit(1)

    input_file = remainder[0]

    if not os.path.exists(input_file):
        # Corrected bug: was using 'input_pdf' which was not defined
        print(f"Error: The file '{input_file}' was not found.")
        sys.exit(1)
        
    output_txt = os.path.splitext(input_file)[0] + ".txt"
    
    acronyms_dict=dict()

    output_lines = extract_text_from_pdf(input_file)

    if acronyms_found:
        #print(f"{acronyms_text}")
        pprint.pprint(f"{acronyms_dict}")

        #output_lines = [l for l in output_lines if l not in acronyms_dict.keys()]
        # Create a new, combined set for filtering
        acronym_filter_set = set()
        # Loop through your dictionary keys ONCE to build the set
        for key in acronyms_dict.keys():
            acronym_filter_set.add(key)  # Add the base acronym (e.g., "cdf")
    
            # Use your smart pluralization rule on the lowercase key
            if key.endswith('s') or key.endswith('S'):
                acronym_filter_set.add(key + 'es')  # e.g., "manrses"
            else:
                acronym_filter_set.add(key + 's')   # e.g., "cdfs"

        # Now, your list comprehension is simple, clean, and case-insensitive
        output_lines = [l for l in output_lines if l not in acronym_filter_set]

        output_lines = [l for l in output_lines if l not in acronyms_dict.values()]

    # remove unnecessary capitals
    output_lines = [l for l in output_lines if l.lower() not in output_lines]

    author_et_al = [l for l in output_lines if l.endswith(' et alii')]
    authors = [l[:-6] for l in output_lines if l.endswith(' et alii')]
    output_lines = [l for l in output_lines if l not in author_et_al]

    # drop strings with unerscores, as these are not words, but probably variables
    output_lines = [l for l in output_lines if '_' not in l]

    # drop strings with '==', as these are not words, but probably an equation
    output_lines = [l for l in output_lines if '==' not in l]



    # remove suffixes and prefixes
    output_lines = remove_suffixes(output_lines)
    output_lines = remove_prefixes(output_lines)




    well_known_acronyms = [a[0] for a in common_acronyms.well_known_acronyms_list]


    remove_list = remove_known_words(output_lines, well_known_acronyms)

    #output_lines = [l for l in output_lines if l not in remove_list]

    processed_text = "\n".join(output_lines)

    # Write the processed text to the output file
    with open(output_txt, "w", encoding="utf-8") as out_file:
        out_file.write(processed_text)
        
    print(f"Successfully extracted and processed text to '{output_txt}'.")

    prefix_results = group_by_prefix(output_lines)
    suffix_results = group_by_suffix(output_lines)

    print("--- PREFIX GROUPS (Central Concepts) ---")
    # remove_list = remove_known_words(prefix_results, well_known_acronyms)
    # new_prefix_results=[]
    # for w in prefix_results:
    #     if w not in remove_list:
    #         new_prefix_results[w]=prefix_results[w]
            
    # prefix_results=new_prefix_results

    print(f"{len(prefix_results)=}")
    for idx, w in enumerate(prefix_results):
        print(f"prefix: {idx} {w} {len(prefix_results[w])}")

    print(json.dumps(prefix_results, indent=2))

    print("\n--- SUFFIX GROUPS (Concept Variants) ---")
    print(f"{len(suffix_results)=}")
    for idx, w in enumerate(suffix_results):
        print(f"suffix: {idx} {w} {len(suffix_results[w])}")
    print(json.dumps(suffix_results, indent=2))

if __name__ == "__main__":
    main()
