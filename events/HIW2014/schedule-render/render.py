#!/usr/bin/python

import sys

from convert import toJSON

def exit_usage():
    print >> sys.stderr, 'Usage: render.py mode [filename]'
    print >> sys.stderr, '  where mode is "html" or "latex"'
    sys.exit()

if '__main__' == __name__:

    # info

    # config

    if (len(sys.argv) != 3):
        exit_usage()
    if (sys.argv[1] == "html"):
        from mkHtml import eventRender
    elif (sys.argv[1] == "latex"):
        from mkLatex import eventRender
    else:
        exit_usage()

    filename = sys.argv[2]

    # call the function...
    event = toJSON(filename)

    if not event:
        print >> sys.stderr, "No result, must have been an error..."
        sys.exit()

    page = eventRender(event)

    print page

    print >> sys.stderr, "Done rendering " + sys.argv[1]

