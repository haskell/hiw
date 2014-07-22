#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Author: Jost Berthold <berthold@diku.dk>
#

import sys

from string import replace

def encode(str):
    """Escape html-relevant characters in a string.  Most of this is
    unnecessary when the right encoding is used..."""

    # this one first, otherwise results may vary
    str = str.replace("&", "&amp;")

    translations \
      = {    "<":"&lt;", ">":"&gt;"
           , "#":"&#35;", "'":"&#39;", '"':"&#34;"
        }
    for a,b in translations.iteritems():
        str = str.replace(a,b)

    return str

# talk: start -- name
#                author (affiliation)
def talkRender(dict):
    """ Render a talk entry, as time TAB title NL TAB author list(comma-sep)
    talk ::= start name author*
    author ::= name affiliation?"""

    if not dict:
        return "%% no talks\n"

    out  ='   <td>%s<td colspan="2" class="ttitle">%s\n' \
              % (dict["start"], encode(dict["name"]))
    
    def authorRender(d):
        au = "%s " % encode(d["name"])
        if d["affiliation"]:
            au += "(%s)" % encode(d["affiliation"])
        return au
    if dict["authors"]:
        out += '   <div class="authors">\n'
        out += ', '.join( map(authorRender, dict["authors"]) )

        out += '</div>\n'
    return out

# session: start-stop -- session title, then go over talks
def sessionRender(dict):
    """Produce an entry for a session. In a tabular environment, first the
    timing, then (tabbed) the title, then "("chair")", if any, then a rule,
    then all talks (if any, otherwise also no rule), still in tabular.
    session ::= chair? name start stop talk* """

    if not dict:
        return "<!-- empty session-->\n"

    # assume valid, process
    dict["name"] = encode(dict["name"])
    if dict["talks"]:
        out = '  <tr class="hastalks">\n'
    else:
        out = '  <tr>\n'
    out += '    <td class="times"> %(start)s - %(stop)s' % dict
    out += '    <td class="stitle"> %(name)s' % dict

    if dict["chair"]:
        out += '<td id="schair"> Chair: %s' % encode(dict["chair"])

    out += "<tr>".join( ["\n"] + map(talkRender, dict["talks"]) )
    return out

# event: page header, date outside, title in the middle. Then print sessions
def eventRender(dict):
    """Produce a html page with the date and title of the event,
    then render all sessions.
    event ::= date name session* """

    if not dict:
        return "<!-- empty event dictionary-->\n"

    # assume valid event, process it
    dict["name"] = encode(dict["name"])
    out = """<html>
<!-- generated from %(name)s -->
 <head>
  <title>%(name)s - %(date)s</title>
  <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/> 
  <link type="text/css" rel="stylesheet" href="acm-icfp2012.css"></link>
  <link type="text/css" rel="stylesheet" href="program.css"></link>
  <script src="icfphook.js" type="text/javascript"></script>
 </head>
 <body>
 <div id="content">
  <h1 id="eventh1">%(name)s </h1>
  <h3 id="dateh3">%(date)s </h3>
  <table id="sessions">
""" % dict #(n, dict["date"], n, n)

    out += '\n   <tr class="spacer"><td>\n   '.join( \
                  map(sessionRender, dict["sessions"]) )

    out += "\n  </table>\n </div>\n </body>\n</html>\n"
    return out

