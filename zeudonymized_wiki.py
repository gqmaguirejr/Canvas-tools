#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -*- mode: python; python-indent-offset: 4 -*-
#
# zeudonymized_wiki.py -c course_id --transcript zoom_chat_file
#
# Example:
# ./zeudonymized_wiki.py -c 11 --transcript /z3/maguire/meeting_saved_chat-20210304.txt
# ./zeudonymized_wiki.py -v -c 11 --transcript /z3/maguire/meeting_saved_chat-2020-12-10.txt
#
# based on by zeudonymize.py Daniel Bosk <dbosk@kth.se> - https://github.com/dbosk/recordy.git
# His program took in a Zoom chant and pseudo anonymized it.
# It can optionally take a file to map names - for example to preserve the teacher's name
#
# Example: ./zeudonymize.py --transcript /z3/maguire/meeting_saved_chat-20210304.txt
# Where the transcript is:
# 14:16:01	 From  KTH, Anna-Karin Högfeldt : https://docs.google.com/document/d/1418Kq39ESLC58HlKBmhq2ZIPWzm8NZmlHkUg6fSXe5E/edit#
# 14:35:19	 From  Sofia Jonsson - Stockholms universitet : https://www.wonder.me/
# 14:35:32	 From  Daniel Bosk, KTH : An alternative is https://gather.town
# 14:41:00	 From  Daniel Bosk, KTH : @Chip: I wrote a short script to pseudonymize Zoom chat transcripts.
# 14:41:48	 From  Gerald Q Maguire Jr  to  Daniel Bosk, KTH(Direct Message) : Great - send me a pointer to it.
# 14:42:15	 From  Daniel Bosk, KTH  to  Gerald Q Maguire Jr(Direct Message) : https://github.com/dbosk/recordy/tree/master/zeudonymize
# 14:43:27	 From  Mats Olsson LiU : I  have used padlet and flinga.fi. in lessons. 
# 14:48:35	 From  Brittney Nicole Arthur Cabrera : https://www.psychologicalscience.org/observer/nasa-exercise
#
# will generate:
#  meeting_saved_chat-20210304-pseudonymized.txt
#  meeting_saved_chat-20210304.nyms
# The later will contain:
# {
#   " KTH, Anna-Karin H\u00f6gfeldt": "Student 1",
#   " Sofia Jonsson - Stockholms universitet": "Student 2",
#   " Daniel Bosk, KTH": "Student 3",
#   " Gerald Q Maguire Jr ": "Student 4",
#   " Daniel Bosk, KTH ": "Student 5",
#   " Gerald Q Maguire Jr": "Student 6",
#   " Mats Olsson LiU": "Student 7",
#   " Brittney Nicole Arthur Cabrera": "Student 8"
# }
#
# Changing the pseudonym file to meeting_saved_chat-20210304-teacher.nyms
# {
#   " KTH, Anna-Karin H\u00f6gfeldt": "Student 1",
#   " Sofia Jonsson - Stockholms universitet": "Student 2",
#   " Daniel Bosk, KTH": "Teacher",
#   " Gerald Q Maguire Jr ": "Student 4",
#   " Daniel Bosk, KTH ": "Student 5",
#   " Gerald Q Maguire Jr": "Student 6",
#   " Mats Olsson LiU": "Student 7",
#   " Brittney Nicole Arthur Cabrera": "Student 8"
# }
# and running with
#  --nymfile /z3/maguire/meeting_saved_chat-20210304-teacher.nyms
# will apply the pseudonym for Daniel as "Teacher"
#
# on 2021-03-04 G. Q. Maguire Jr. extended this to use information from a Canvas course room to be able to
# make a wikipage from a chat transcript.
# Also as can be seen from the above, the names should have strip applied to them to remove the starting and trailng white space.
#
# With the option "-N" it does not use pseudonyms, but rather the real user's names
#
import re
import sys

import json
import argparse
import os

#############################
###### EDIT THIS STUFF ######
#############################

global baseUrl	# the base URL used for access to Canvas
global header	# the header for all HTML requests
global payload	# place to store additionally payload when needed for options to HTML requests

# Based upon the options to the program, initialize the variables used to access Canvas gia HTML requests
def initialize(args):
  global baseUrl, header, payload

  # styled based upon https://martin-thoma.com/configuration-files-in-python/
  config_file=args["config"]

  try:
    with open(config_file) as json_data_file:
      configuration = json.load(json_data_file)
      access_token=configuration["canvas"]["access_token"]
      if args["containers"]:
        baseUrl="http://"+configuration["canvas"]["host"]+"/api/v1"
        print("using HTTP for the container environment")
      else:
        baseUrl="https://"+configuration["canvas"]["host"]+"/api/v1"

      header = {'Authorization' : 'Bearer ' + access_token}
      payload = {}
  except:
    print("Unable to open configuration file named {}".format(config_file))
    print("Please create a suitable configuration file, the default name is config.json")
    sys.exit()

class PseudonymFactory:
  def __init__(self, prefix, nym_map):
    self.__prefix = prefix
    self.__num = 0
    pattern = re.compile(f"{prefix} (\\d+)")
    for _, pseudonym in nym_map.items():
      match = pattern.match(pseudonym)
      if match:
        self.__num = max(self.__num, int(match.group(1)))

  def __str__(self):
    return f"{self.__prefix} {self.__num}"

  def next(self):
    self.__num += 1
    return str(self)

  def __next__(self):
    return self.next()

def pseudonymize(lines, nym_map, prefix="Student"):
  pseudonym = PseudonymFactory(prefix, nym_map)
  for line in lines:
    sender, recipient = parties(line)

    if sender not in nym_map:
      nym_map[sender] = pseudonym.next()
    line = substitute(line, sender, nym_map[sender])

    if recipient:
      if recipient not in nym_map:
        nym_map[recipient] = pseudonym.next()
      line = substitute(line, recipient, nym_map[recipient])

    yield line

def substitute(string, frm, to):
  pattern = re.compile(frm)
  return pattern.sub(to, string)

def parties(line):
  to_kw = "[Tt]o"
  from_kw = "[Ff]rom"
  private_kw = "(Privately|Direct Message)"

  line = re.sub(f"{to_kw} Everyone", "", line)

  recipient = re.compile(f"{to_kw} *(.*(?=\({private_kw}\)))").search(line)
  sender = re.compile(f"{from_kw} *([^:]*(?= {to_kw} ))").search(line) \
    if recipient \
    else re.compile(f"{from_kw} ([^:]*) :").search(line)

  try:
    if recipient:
      print("sender='{0}' and recipient='{1}'".format(sender.group(1).strip(), recipient.group(1).strip()))
      return sender.group(1).strip(), recipient.group(1).strip()
    else:
      print("sender='{0}'".format(sender.group(1).strip()))
      return sender.group(1).strip(), None
  except AttributeError:
    raise ValueError(f"malformed: {line}")

def main(argv):
  global Verbose_Flag
  
  timestamp_regex = r'(2[0-3]|[01][0-9]|[0-9]):([0-5][0-9]|[0-9]):([0-5][0-9]|[0-9])'

  argp = argparse.ArgumentParser(description="zeudonymize: Pseudonymizing Zoom chats")

  argp.add_argument("-t", "--transcript", required=True,
                    help="Filename of the chat transcript")
  argp.add_argument("-p", "--prefix", type=str, default="Student",
                    help="Pseudonym prefix for new pseudonyms")
  argp.add_argument("-n", "--nymfile", type=str,
                    help="Filename of the nym map")

  argp.add_argument('-v', '--verbose', required=False,
                    default=False,
                    action="store_true",
                    help="Print lots of output to stdout")
  argp.add_argument('-C', '--containers',
                    default=False,
                    action="store_true",
                    help="for the container enviroment in the virtual machine")
  argp.add_argument("--config", type=str, default='config.json',
                    help="read configuration from file")

  argp.add_argument("-c", "--canvas_course_id", type=int, required=True,
                    help="canvas course_id")

  argp.add_argument('-N', '--nonanonymous', required=False,
                    default=False,
                    action="store_true",
                    help="use the real names and not the pseudonyms")

  args = vars(argp.parse_args(argv))

  Verbose_Flag=args["verbose"]

  initialize(args)
  if Verbose_Flag:
    print("baseUrl={}".format(baseUrl))

  course_id=args["canvas_course_id"]
  print("course_id={}".format(course_id))

  in_filename = args["transcript"]
  prefix = args["prefix"]
  if args["nymfile"]:
    with open(args["nymfile"], "r") as nym_file:
      nym_map = json.loads(nym_file.read())
  else:
    nym_map = {}

  out_base, out_ext = os.path.splitext(in_filename)
  out_filename = out_base + "-pseudonymized" + out_ext
  out_pseudonyms = out_base + ".nyms"

  pseudonym = PseudonymFactory(prefix, nym_map) # initialize the factory to make pseudonyms
  from_kw = "[Ff]rom"
  privateMsg="Privately"
  directMsg="(Direct Message)"
  
  list_of_chat_items=[]

  chat_item=dict()              # empty chat item to use
  
  if Verbose_Flag:
    print("About to start processing the transcript")
  
  try:
    with open(in_filename, "r") as in_file, open(out_filename, "w") as out_file:
      inputLines=in_file.readlines()
      for line in inputLines:
        # check for the start of a chat item
        # these have the form: dd:dd:dd\t From  <sender> : msg
        # or                   dd:dd:dd\t From  <nsender> to <recipient> (Direct Message) : msg
          m0=re.match(timestamp_regex,line)
          if m0:
            if m0.start() == 0:
              timestamp=m0.group()
              if Verbose_Flag:
                print("timestamp={0}, line={1}".format(timestamp, line))
              remainder_of_line=line[m0.end():].strip()

              chat_item=dict()              # empty chat item to use
              chat_item['timestamp']=timestamp

              # check for From keyword
              fromMatch=re.match(from_kw, remainder_of_line)
              if not fromMatch:
                print("From keyword not found in line=".format(remainder_of_line))
                continue

              # there must always be a sender
              senderMatch = re.match(f"{from_kw} *([^:]*)", remainder_of_line)
              if not senderMatch:              
                print("sender not found in line=".format(remainder_of_line))
                continue

              possibleSender=senderMatch.group(1).strip()
              # here sender can include a "to xxxx" portion
              # now look a possible recipient
              # print("looking for recipient in sender={0}".format(sender))

              # look for "[Tt]o" keyword
              toKeywordFound=False

              toIndex1=possibleSender.find(" to ")
              toIndex2=possibleSender.find(" TO ")
              if toIndex1 > 0:
                sender=possibleSender[0:toIndex1].strip()
                possibeRecipient=possibleSender[toIndex1+5:].strip()
                toKeywordFound=True
              elif toIndex2 > 0:
                sender=possibleSender[0:toIndex2].strip()
                possibeRecipient=possibleSender[toIndex2+5:].strip()
                toKeywordFound=True
              else:
                sender=possibleSender
                possibeRecipient=None

              if Verbose_Flag:
                print("toKeywordFound={0} sender={1} possibeRecipient={2}".format(toKeywordFound, sender, possibeRecipient))

              if sender not in nym_map: # if the sender is not know, add a pseudonym for them
                if Verbose_Flag:
                  print("sender '{0}' not in nym_map".format(sender))
                nym_map[sender] = pseudonym.next()

              if not toKeywordFound: #  there is just a sender
                sender_offset=remainder_of_line.find(sender)
                remainder_of_line = remainder_of_line[(sender_offset+len(sender)):].strip()
                if remainder_of_line[0] == ':':
                  remainder_of_line = remainder_of_line[1:].strip()
                output_line="{0}\t{1}:\t:{2}".format(timestamp, nym_map[sender], remainder_of_line)

                if args["nonanonymous"]:
                  chat_item['sender']=sender
                else:
                  chat_item['sender']=nym_map[sender]

                chat_item['msg']=remainder_of_line
                list_of_chat_items.append(chat_item)

                print(output_line, file=out_file)
                continue

              # now look for recipient
              directIndex=possibeRecipient.endswith(directMsg)
              recipient=possibeRecipient[:len(directMsg)]
              if Verbose_Flag:
                print("recipient={}".format(recipient))

              directIndex2=remainder_of_line.find(directMsg)
              if directIndex2 > 0:
                remainder_of_line = remainder_of_line[(directIndex2+len(directMsg)):].strip()
                if remainder_of_line[0] == ':':
                  remainder_of_line = remainder_of_line[1:].strip()
                  msg=remainder_of_line.strip()
              else:
                msg=""

              if recipient not in nym_map:
                if Verbose_Flag:
                  print("recipient '{0}' not in nym_map".format(recipient))
                nym_map[recipient] = pseudonym.next()

              output_line="{0}\t{1}:{2}:{3}".format(timestamp, nym_map[sender], nym_map[recipient], msg)
              if args["nonanonymous"]:
                chat_item['sender']=sender
              else:
                chat_item['sender']=nym_map[sender]

              if args["nonanonymous"]:
                chat_item['recipient']=recipient
              else:
                chat_item['recipient']=nym_map[recipient]

              chat_item['msg']=remainder_of_line
              list_of_chat_items.append(chat_item)

              print(output_line, file=out_file)
              continue

            else:               # timestamp not starting in column 0
              output_line="\t\t\t{0}".format(line.strip())
              existing_msg=chat_item.get('msg', "")
              chat_item['msg']=existing_msg+'\n'+output_line
              print(output_line, file=out_file)

          else:                 # just output lines that do not start with a timestamp
            output_line="\t\t\t{0}".format(line.strip())
            existing_msg=chat_item.get('msg', "")
            chat_item['msg']=existing_msg+'\n'+output_line

            print(output_line, file=out_file)

  except FileNotFoundError as err:
    print(f"file not found: {err}", file=sys.stderr)
    return -1

  with open(out_pseudonyms, "w") as nym_file:
    print(json.dumps(nym_map, indent=2), file=nym_file)

  if Verbose_Flag:
    print("number of chat_items={}".format(len(list_of_chat_items)))


  new_file_name="{1}-chat_for_course-{0}.html".format(course_id, out_base)

  page='<h2><a id="Chat">{0}</h3>'.format(out_base)
  page=page+'<table style="width:100%">\n<tr><th  width=10%>Timestamp</th><th width=15%>Sender</th><th width=15%>[Recipient]</th><th>Message</th></tr>'

  for i in list_of_chat_items:
    print("item={}".format(i))
    timestamp=i['timestamp']
    sender=i['sender']
    recipient=i.get('recipient', False)
    msg=i['msg']

    if recipient:
      new_item="<tr><td>{0}</td><td>{1}</td><td>{2}</td><td>{3}</td></tr>".format(timestamp, sender, recipient, msg)
    else:
      new_item="<tr><td>{0}</td><td>{1}</td><td></td><td>{2}</td></tr>".format(timestamp, sender, msg)
    page=page+new_item

  page=page+'</table>'
  # write out body of response as a .html page

  with open(new_file_name, 'wb') as f:
    encoded_output = bytes(page, 'UTF-8')
    f.write(encoded_output)

if __name__ == '__main__':
  sys.exit(main(sys.argv[1:]))
