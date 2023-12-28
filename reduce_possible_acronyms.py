#!/usr/bin/env python3
#
# ./reduce_possible_acronyms.py  course_id [url to acronym page]
# 
# reduce the likely acronyms file for a course (as extraced by compute_unique_words_for_pages_in_course.py
#
# G. Q: Maguire Jr.
#
# 2023.12.28
#
# based on compute_unique_words_for_pages_in_course.py
#
# with the option "-v" or "--verbose" you get lots of output - showing in detail the operations of the program
#
# Can also be called with an alternative configuration file using the option --config config-test.json
#
# Examples:
# ./reduce_possible_acronyms.py 31168
#
# ./reduce_possible_acronyms.py --config config-test.json 31168
#
# The option --dir can be used to specify a directory to be used to get the input tiles and to put the output files in.
# ./reduce_possible_acronyms.py --dir ./Internetworking_course/ 31168
#
# Notes
#
#

import csv, requests, time
from pprint import pprint
import optparse
import sys

import json
import re

from lxml import html

#############################
###### EDIT THIS STUFF ######
#############################

global baseUrl	# the base URL used for access to Canvas
global header	# the header for all HTML requests
global payload	# place to store additionally payload when needed for options to HTML requests

# Based upon the options to the program, initialize the variables used to access Canvas gia HTML requests
def initialize(options):
    global baseUrl, header, payload

    # styled based upon https://martin-thoma.com/configuration-files-in-python/
    if options.config_filename:
        config_file=options.config_filename
    else:
        config_file='config.json'

    try:
        with open(config_file) as json_data_file:
            configuration = json.load(json_data_file)
            access_token=configuration["canvas"]["access_token"]
            baseUrl="https://"+configuration["canvas"]["host"]+"/api/v1"

            header = {'Authorization' : 'Bearer ' + access_token}
            payload = {}
    except:
        print("Unable to open configuration file named {}".format(config_file))
        print("Please create a suitable configuration file, the default name is config.json")
        sys.exit()

def get_existing_acronyms_from__course(course_id, acronym_pages):
    global Verbose_Flag

    list_of_all_pages=[]
    existing_acronyms=set()

    # Use the Canvas API to get the list of pages for this course
    #GET /api/v1/courses/:course_id/pages

    url = "{0}/courses/{1}/pages".format(baseUrl, course_id)
    if Verbose_Flag:
        print("url: " + url)

    r = requests.get(url, headers = header)
    if r.status_code == requests.codes.ok:
        page_response=r.json()
    else:
        print("No pages for course_id: {}".format(course_id))
        return False

    for p_response in page_response:  
        list_of_all_pages.append(p_response)

    # the following is needed when the reponse has been paginated
    # i.e., when the response is split into pieces - each returning only some of the list of modules
    while r.links.get('next', False):
        r = requests.get(r.links['next']['url'], headers=header)  
        page_response = r.json()  
        for p_response in page_response:  
            list_of_all_pages.append(p_response)

    for p in list_of_all_pages:
        # skip page that are not in acronym_pages
        if not p['url'] in acronym_pages:
            if Verbose_Flag:
                print(f"skipping page {p['url']}")
            continue

        if Verbose_Flag:
            print("title is '{0}' with url {1}".format(p['title'], p['url']))

        # Use the Canvas API to GET the page
        #GET /api/v1/courses/:course_id/pages/:url
                
        url = "{0}/courses/{1}/pages/{2}".format(baseUrl, course_id, p["url"])
        if Verbose_Flag:
            print(url)
        payload={}
        r = requests.get(url, headers = header, data=payload)
        if r.status_code == requests.codes.ok:
            page_response = r.json()  
            if Verbose_Flag:
                print("body: {}".format(page_response["body"]))

            body=page_response["body"]
            if isinstance(body, str) and len(body) > 0:
                document = html.document_fromstring(body)
                td_elements=get_text_for_tag(document, 'td')
                for tde in td_elements:
                    existing_acronyms.add(tde)

            else:               # nothing to process
                continue
                
        else:
            print("No pages for course_id: {}".format(course_id))
            return False

    return existing_acronyms

def list_pages(course_id):
    list_of_all_pages=[]

    # Use the Canvas API to get the list of pages for this course
    #GET /api/v1/courses/:course_id/pages
    url = "{0}/courses/{1}/pages".format(baseUrl, course_id)

    if Verbose_Flag:
        print("url: " + url)

    r = requests.get(url, headers = header)
    if r.status_code == requests.codes.ok:
        page_response=r.json()

    for p_response in page_response:  
        list_of_all_pages.append(p_response)

        # the following is needed when the reponse has been paginated
        # i.e., when the response is split into pieces - each returning only some of the list of modules
        while r.links.get('next', False):
            r = requests.get(r.links['next']['url'], headers=header)  
            page_response = r.json()  
            for p_response in page_response:  
                list_of_all_pages.append(p_response)

    for p in list_of_all_pages:
        print("{}".format(p["title"]))

def get_text_for_tag(document, tag):
    tag_xpath='.//'+tag
    #
    tmp_path=document.xpath(tag_xpath)
    if tmp_path:
        tmp=[item.text for item in tmp_path]
        tmp[:] = [item for item in tmp if item != None and item != "\n"]
    return tmp


testing_existing_acronyms={'UMTS', '3GPP', 'UBR', 'CA', 'PMIPv6', 'SLA', 'PVR', 'SI', 'ESA', 'EU', 'HDLC', 'GMPLS', 'CORBA', 'DES', 'SNUS', 'DVMRP', 'DDNS', 'Euro6IX', 'JBOD', 'bps', 'WAN', 'IDRP', 'AT', 'RADIUS', 'SDP', 'ICANN', 'FBOSS', 'NIST', 'I-BGP', 'SAP', 'MX', 'SATAN', 'TOR', 'DDoS', 'RIP', 'AFS', 'OSI', 'CIX', 'MAC', 'D-ITG', 'IMS', 'OSPF', 'MSDP', 'ISP', 'CoA', 'SA', 'DUAL', 'CWND', 'NMAP', 'X25', 'ARIN', 'PoP', 'gTLD', 'LSA', 'IV', 'KDD', 'HSPA', 'NTP', 'MIB', 'WKS', 'CPIP', 'ENUM', 'USB', 'GRE', 'WebRTC', 'INRIA', 'FIRST', 'MSS', 'RPF', 'SSM', 'GFA', 'XID', 'PGP', 'EGP', 'LAN', 'E-BGP', 'CALEA', 'DLPI', 'FIRE', 'IGMP', 'HVAC', 'NCS', 'WFQ', 'ISO', 'TRILL', 'NIT', 'FA', 'IANA', 'STCP', 'KTH', 'IPX', 'BBN', 'DPT', 'ECN', '(Cisco’s) IOS', 'PCC', 'PIM-DM', 'IMEC', 'DNS', 'CCTLD', 'SPI', 'AVM', 'SITIC', 'RUDE', 'VIF', 'LANL', 'REST', 'ASIC', 'LSAP', 'AFRINIC', 'RTT', 'RSVP', 'ISDN', 'IP', 'IPv4', 'AAA', 'OSPF-TE', 'CN', 'AAAA', 'rwnd', 'MTU', 'ISN', 'VoIP, VOIP', 'IGRP', 'MBONE', 'CRC', 'IPMA', 'IRDA', 'GIX', 'NRL', 'URI', 'ICT', 'USM', 'TLA', 'VAN', 'SOAP', 'VLSM', 'PIM', 'WPAN', 'TCB', 'NAT', 'TCAM', 'QoS', 'IETF', 'SNMP', 'TUT', 'TDP', 'SRV', 'PAWS', 'PDML', 'CODEC', 'PAN', 'IRR', 'TISSEC', 'TFTP', 'DMI', 'T/TCP', 'RPC', 'DTN', 'RMON', 'BT', 'LLC', 'IPMI', 'CAM', 'ICV', 'FQDN', 'IKE', 'IoT', 'UUID', 'RPB', 'CAN', 'ENISA', 'database', 'WLAN', 'pps', 'ACM', 'DWDM', 'RPSL', 'SET', 'CBT', 'DHCP', 'XoJIDM', 'SONET', 'ATM', 'VACM', 'VRF', 'iSCSI', 'CAIDA', 'DAN', 'HTTP', 'SLIP', 'ERA', 'TLS', 'SDH', 'APNIC', 'PDA', 'PEM', 'RTO', 'Diffserv', 'WBEM', 'SIG', 'AES', 'PopC', 'DoS', 'vBNS', 'RIR', 'DiVA', 'MAN', 'SSN', 'SRP', 'BSD', 'RT', 'VLR', 'CMIP', 'XDR', 'VPLS', 'DOE', 'FIX', 'WTO', 'IPv6', 'ANCP', 'SPIT', 'BAN', 'AFSDB', 'MIF', 'TLD', 'B-ISDN', 'GIF', 'SIP', 'ORCHID', 'SMTP', 'ADAE', 'TSN', 'IXP', 'RP', 'JMAPI', 'FTP', 'PMTU', 'TOS', 'LTE', 'MIKEY', 'IEEE', 'NSAP', 'CGA', 'DMZ', 'WWGD', 'UDP', 'CERT®', 'NFS', 'WDM', 'RR', 'FDDI', 'iFCP', 'MN', 'IKEv2', 'PTR', 'SSL', 'ARPANET', 'SRTP', 'GSS-API', 'RH', 'AB', 'AS', 'DVR', 'MPLS', 'VANET', 'ITU-T', 'ARP', 'RIPE', 'EGRP', 'ISAKMP', 'NULL', 'AH', 'MIPMANET', 'CIDR', 'WWAN', 'ESP', 'NAP', 'Euro-IX', 'LBS', 'TTL', 'JSON', 'TCP', 'NMF', 'FRA', 'LANIC', 'MANET', 'CIM', 'MSR', 'NCC', 'ACK', 'NCP', 'ICMP', 'SAN', 'RTCP', 'IPSEC', 'PTMP', 'VCI', 'NXT', 'DTLS', 'SOA', 'BGP', 'RARP', 'SOU', 'MBGP', 'CCNA', 'AADS', 'ITU', 'NS', 'AGP', 'ISOC', 'YANFS', 'ICCC', 'FCIP', 'MANRS', 'BPF', 'HINFO', 'DB', 'PIM-SM', 'WASHMS', 'API', 'VAD', 'E-MBMS', 'TXT', 'NANOG', 'ADSL', 'BSDI', 'LFN', 'NetSCARF', 'RTP', 'UAC', 'pNFS', 'BOOTP', 'RADB', 'S-HTTP', 'RED', 'CIP', 'GSM', 'PSIRP', 'PPP', 'NFV', 'DNSSec', 'FO', 'MIT', 'HLR', 'PX', 'WWW', 'VPN', 'SHA-1', 'XNS', 'HMAC', 'W3C', 'PSTN', 'SCTP', 'RPM', 'DAAD', 'RFC', 'FPGA', 'SUNET', 'AUTH', 'BR', 'SACK'}


def main():
    global Verbose_Flag


    parser = optparse.OptionParser()

    parser.add_option('-v', '--verbose',
                      dest="verbose",
                      default=False,
                      action="store_true",
                      help="Print lots of output to stdout"
    )

    parser.add_option("--config", dest="config_filename",
                      help="read configuration from FILE", metavar="FILE")
    
    parser.add_option("--dir", dest="dir_prefix",
                      default='./',
                      help="read configuration from FILE", metavar="FILE")

    parser.add_option('-t', '--testing',
                      dest="testing",
                      default=False,
                      action="store_true",
                      help="enable testing mode"
    )


    options, remainder = parser.parse_args()

    Verbose_Flag=options.verbose
    if Verbose_Flag:
        print("ARGV      : {}".format(sys.argv[1:]))
        print("VERBOSE   : {}".format(options.verbose))
        print("REMAINING : {}".format(remainder))
        print("Configuration file : {}".format(options.config_filename))

    initialize(options)


    acronym_urls=[] # a list of URLs
    
    # compute the directory prefix for files to be used for the program's I/O
    directory_prefix=options.dir_prefix
    if not directory_prefix.endswith('/'):
        directory_prefix=directory_prefix+'/'
    if Verbose_Flag:
        print(f'{directory_prefix=}')

    if (len(remainder) < 1):
        print("Insuffient arguments\n must provide course_id\n")
        return

    if (len(remainder) >= 1):
        course_id=remainder[0]
        if Verbose_Flag:
            print(f'{course_id=}')
            
    if (len(remainder) == 1):
        if int(course_id) == 31168:
            acronym_urls=['acronyms-and-abbreviations']
        else:
            acronym_urls=[]

    if (len(remainder) >= 2):
        acronym_urls.append(remainder[1])

    if acronym_urls:
        print(f'processing existing acronyms from {acronym_urls}')

    # get collected acronyms
    new_file_name=f'{directory_prefix}unique_words-for-course-likely-acronyms-{course_id}.txt'        
    with open(new_file_name, 'r') as f:
        likely_acronyms_list=f.readlines()

    likely_acronyms=set()
    for la in likely_acronyms_list:
        likely_acronyms.add(la.strip())
    print(f'{len(likely_acronyms)} likely acronyms')

    if Verbose_Flag:
        print(f'{likely_acronyms=}')

    if options.testing:
        existing_acronyms=testing_existing_acronyms
    else:
        if acronym_urls and len(acronym_urls) > 0:
            existing_acronyms=get_existing_acronyms_from__course(course_id, acronym_urls)

    if Verbose_Flag:
        print(f'existing_acronyms={sorted(existing_acronyms)}')
    print(f'{len(existing_acronyms)} existing acronyms in the Canvas course room')

    # print(f'common acronyms = {existing_acronyms.union(likely_acronyms)}')
    missing_acronyms = likely_acronyms.difference(existing_acronyms)
    print(f'{len(missing_acronyms)} missing acronyms')
    print(f'missing acronyms = {sorted(missing_acronyms)}')


    # output likely acronyms
    new_file_name=f'{directory_prefix}unique_words-for-course-missing-acronyms-{course_id}.txt'        
    with open(new_file_name, 'w') as f:
        for word in sorted(missing_acronyms):
            f.write(f"{word}\n")


if __name__ == "__main__": main()
