#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Author: Jost Berthold <berthold@diku.dk>
#

import sys

from convert import toJSON
from string import replace

def texify(str):
    """ escape tex-relevant characters in a string"""
    # this one first...
    str = replace(str, "\\", "\\textbackslash")

    translations \
       = { "#":"\\#", "%%":"\\%%", "$":"\\$"
           , "&":"\&"
           , "ü":"\\\"u", "ö":"\\\"o", "ä":"\\\"a"
           , "Ü":"\\\"U", "Ö":"\\\"O", "Ä":"\\\"A", "ß":"\\ss{}"
           , "õ":"\\~{o}", "ñ":"\\~{n}"
           , "á":"\\'a", "é":"\\'e", "í":"\\'i", "ó":"\\'o", "ú":"\\'u"
           , "à":"\\`a", "è":"\\`e", "ì":"\\`i", "ò":"\\`o", "ù":"\\`u"
           , "ø":"\\o{}", "æ":"\\ae{}", "å":"\\aa{}"
           , "Ø":"\\O{}", "Æ":"\\AE{}", "Å":"\\AA{}"
           }
    # ...
    for a,b in translations.iteritems():
        str = str.replace(a,b)

    return str

# talk: start -- name
#                author (affiliation)
def talkRender(dict):
    """ Render a talk entry, as time TAB title NL TAB author list(comma-sep)
    talk ::= start name author+
    author ::= name affiliation?"""

    if not dict:
        return "%% no talks\n"

    out = "%s & \\multicolumn{3}{p{\\talkwidth}}{ %s}" % \
            (dict["start"], texify(dict["name"]))
    
    def authorRender(d):
        au = "%s" % texify(d["name"])
        if d["affiliation"]:
            au += " (%s)" % texify(d["affiliation"])
        return au
    if dict["authors"]:
        out += """\\\\
    & \\multicolumn{3}{r}{
\\begin{minipage}{\\talkwidth}
{\\small \\raggedright \it %% \\raggedleft 
"""
        out +=  ", ".join( map(authorRender, dict["authors"]) )

        out += """\\\\}
\end{minipage}}
"""
    return out

# session: start-stop -- session title, then go over talks
def sessionRender(dict):
    """Produce an entry for a session. In a tabular environment, first the
    timing, then (tabbed) the title, then "("chair")", if any, then a rule,
    then all talks (if any, otherwise also no rule), still in tabular.
    session ::= chair? name start stop talk* """

    if not dict:
        return "%% empty session\n"

    # assume valid, process
    dict["name"] = texify(dict["name"])
    out = "%(start)s & -- %(stop)s & {\\bf %(name)s} &\n" % dict

    if dict["chair"]:
        out += "Chair: %s\\\\\n" % texify(dict["chair"])
    elif dict["talks"]:
        out += "\\\\\n"

    if dict["talks"]:
        out = "\\rowcolor[gray]{0.9}\n" + out
        out += "\\\\\n".join( map(talkRender, dict["talks"]) )
    return out

# event: page header, date outside, title in the middle. Then print sessions
def eventRender(dict):
    """Produce a page header with the date on the side and title 
    in the middle as a title, then render all sessions (if any).
    event ::= date name session* """

    if not dict:
        return "%% empty event dictionary\n"
    
    # assume valid event, process it
    dict["name"] = texify(dict["name"])
    out = """
%% %(name)s
\\fancyhead[RE,LO]{{\\large \\bf %(date)s}}
\\fancyhead[RO,LE]{{\\large \\bf %(short)s}}

%% delete this manually if page is too long
\\begin{center} \\textbf{\\large %(name)s} \\end{center}

\\noindent
\\begin{tabular}{p{0.7cm}lp{\\sessionwidth}r}
""" % dict #(n, dict["date"], n, n)

    out += "\\\\[\\sessionsep]\n".join( map(sessionRender, dict["sessions"]) )

    out += "\\end{tabular}\n"
    return out


if '__main__' == __name__:

    # info

    # config

    if (len(sys.argv) != 2):
        print >> sys.stderr, "Usage: mkLatex.py [filename]"
        sys.exit()

    filename = sys.argv[1]

    # call the function...
    event = toJSON(filename)

    if not event:
        print >> sys.stderr, "No result, must have been an error..."
        sys.exit()

    page = eventRender(event)

    print "%% %s%s\\newpage\n" % (filename, page)

    print >> sys.stderr, "Done rendering Latex"

