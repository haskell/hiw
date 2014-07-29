#!/usr/bin/python

#
# Compiler for ConferenceFormat2JSON
#
# Author: Alexander Thiemann <mail@agrafix.net>
#
# hacked by JB: introduce function to be called from other modules

import json, sys, re, datetime

# constants
regexp = re.compile("^([^:]*): (.*)$")
timeexp = re.compile("^([0-9]{1,2}):([0-9]{2})$")
invalidAuthor = re.compile("^([^\(]*) \([^\)]*\)$")
dateformat = "%b %d, %Y"


# helpers
def isValidTime(lineNo, timeStr):
    if (timeexp.match(timeStr) == None):
        print >> sys.stderr, "Error on line " + str(lineNo) + ": Invalid time input: " + timeStr
        sys.exit(1)

# data structures
class Session:
    def __init__(self, name):
        self.name = name
        self.chair = ""
        self.start = ""
        self.talks = []

    def addChair(self, chair):
        self.chair = chair

    def addStart(self, start):
        self.start = start

    def addTalk(self, talk):
        self.talks.append(talk)

    def isComplete(self):
        return (self.name != "" and self.start != "")

    def dump(self):
        return {"name": self.name, "chair": self.chair, "start": self.start, "talks": self.talks}

class Talk:
    def __init__(self, name):
        self.name = name
        self.start = ""
        self.authors = []

    def addStart(self, start):
        self.start = start

    def addAuthor(self, author):
        self.authors.append(author)

    def isComplete(self):
        return (self.name != "" and self.start != "")

    def dump(self):
        return {"name": self.name, "start": self.start, "authors": self.authors}

class EventCompiler:
    def __init__(self):
        self.event = {"name": "", "short": "", "date": "", "sessions": []}
        self.currentSession = None
        self.currentTalk = None
        self.endTime = ""

    def calculateDurations(self):

        if (self.endTime == ""):
            print >> sys.stderr, "Error: Missing End-Tag"
            sys.exit(1)
        
        for k in range(0, len(self.event["sessions"])):
            start = self.event["sessions"][k]["start"]
            if (k+1 >= len(self.event["sessions"])):
                end = self.endTime
            else:
                end = self.event["sessions"][k+1]["start"]

            self.event["sessions"][k]["stop"] = end

    def storeSession(self):
        if (self.currentSession != None):
            self.storeTalk()

            if (not self.currentSession.isComplete()):
                print >> sys.stderr, "Error: Session " + self.currentSession.name + " is missing attributes (name and start required)."
                sys.exit(1)
                
            self.event["sessions"].append(self.currentSession.dump())

    def storeTalk(self):
        if (self.currentTalk != None):
            if (not self.currentTalk.isComplete()):
                print >> sys.stderr, "Error: Talk " + self.currentTalk.name + " is missing attributes (name and start required)."
                sys.exit(1)
                
            self.currentSession.addTalk(self.currentTalk.dump())

    def handle(self, line, key, value):
        if key == "Event":
            self.event["name"] = value
            self.event["short"] = value
        elif key == "Short":
            self.event["short"] = value
        elif key == "Date":
            try:
                dt = datetime.datetime.strptime(value, dateformat)
            except ValueError:
                print >> sys.stderr, "Error on line " + str(line) + ": Couldn't parse Event's date: " + value
                sys.exit(1)
                    
            self.event["date"] = value
        elif key == "End":
            isValidTime(line, value)
            
            self.storeSession()
            self.endTime = value
            
        elif key == "Session":
            self.storeSession()
            
            self.currentSession = Session(value)
            self.currentTalk = None
        elif key == "Start":
            isValidTime(line, value)
            
            if (self.currentTalk == None):
                self.currentSession.addStart(value)
            else:
                self.currentTalk.addStart(value)
                
        elif key == "Chair":
            self.currentSession.addChair(value)
        elif key == "Talk":
            self.storeTalk()

            self.currentTalk = Talk(value)

        elif key == "Author":
            if (self.currentTalk != None):

                if (invalidAuthor.match(value) != None):
                    print >> sys.stderr, "Error on line " + str(line) + ": invalid Author. Please use the Affiliation field!"
                    sys.exit(1)
                
                self.currentTalk.addAuthor({"name": value, "affiliation": ""})
            else:
                print >> sys.stderr, "Error on line " + str(line) + ": Unexpected author"
                sys.exit(1)

        elif key == "Affiliation":
            if (self.currentTalk != None):
#                for key in range(0, len(self.currentTalk.authors)):
#                    if self.currentTalk.authors[key]["affiliation"] == "":
#                        self.currentTalk.authors[key]["affiliation"] = value
# This attributes to all authors. I would like control over where affiliation
# appears, from the input txt. Therefore, only last author modified.
                    key = len(self.currentTalk.authors)-1
                    if self.currentTalk.authors[key]["affiliation"] == "":
                        self.currentTalk.authors[key]["affiliation"] = value
                    else:
                        print >> sys.stderr, "Error on line " + str(line) + ": Duplicate Affiliation"

            else:
                print >> sys.stderr, "Error on line " + str(line) + ": Unexpected Affiliation"
                sys.exit(1)

        else:
            print >> sys.stderr, "Error on line " + str(line) + ": Unknown key '" + key + "'"
            sys.exit(1)


# function:: file name -> JSON
def toJSON(file):
    if not file:
        return None
    
    # main function
    comp = EventCompiler()

    print >> sys.stderr, "Reading " + file + " ..."
    fp = open(file)
    ln = fp.readline()
    line = 1;

    while (ln != ""):
        ln = ln.strip()
        
        if (len(ln) >= 2 and ln[0] == "-" and ln[1] == "-"):
            #print "Skip: " + ln
            pass
        elif (len(ln) != 0):
            result = regexp.match(ln)
            if (result == None):
                print >> sys.stderr, "Error on line " + str(line) + ": Parse error! Can't understand: '" + ln + "'"
                sys.exit(1)
            else:
                comp.handle(line, result.group(1), result.group(2))
    
        ln = fp.readline()
        line += 1

    fp.close()

    print >> sys.stderr, "Done."

    print >> sys.stderr, "Calculation finish times ..."
    comp.calculateDurations()
    print >> sys.stderr, "Done."

    return comp.event


# ## Main ###

if '__main__' == __name__:

    # info

    print "Welcome to ConferenceFormat2JSON compiler"
    print "Allowed format per line:"
    print "\t-- this line is ignored"
    print "\tKey: Value"
    print ""

    # config

    if (len(sys.argv) != 2):
        print "Usage: convert.py [filename]"
        sys.exit(1)

    filename = sys.argv[1]

    # call the function...
    event = toJSON(filename)

    if not event:
        print "No result, must have been an error..."
        sys.exit(1)

    filename += ".json"

    print "Writing " + filename + " ..."
    fp = open(filename, "w")
    json = json.dumps(event, sort_keys=True, indent=4)
    fp.write(json)
    fp.close()

    print "Done."
