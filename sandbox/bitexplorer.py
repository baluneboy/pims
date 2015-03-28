#!/usr/bin/python

# STEPS FOR NEW FORMAT DEFINITION:
# 1. make definition like /home/pims/dev/programs/python/pims/sandbox/example_hachoir_roz.py
# 2. cd /usr/lib/pymodules/python2.7/hachoir_parser/misc
# 3. sudo ln -s /home/pims/dev/programs/python/pims/sandbox/example_hachoir_roz.py example_roz.py
# 4. add import for new class def as line in: sudo vi /usr/share/pyshared/hachoir_parser/misc/__init__.py

import sys
from optparse import OptionGroup, OptionParser
from hachoir_core.cmd_line import (getHachoirOptions, configureHachoir, unicodeFilename)
from hachoir_core.stream import InputStreamError, FileInputStream, StringInputStream
from hachoir_core.i18n import _
from hachoir_parser import guessParser, HachoirParserList
from hachoir_urwid import exploreFieldSet
from hachoir_urwid.version import VERSION, WEBSITE
import hachoir_core

def displayVersion(*args):
    print _("Hachoir urwid version %s") % VERSION
    print _("Hachoir library version %s") % hachoir_core.__version__
    print _("Website: %s") % WEBSITE
    sys.exit(0)

def displayParserList(*args):
    HachoirParserList().print_()
    sys.exit(0)

def parseOptions():
    parser = OptionParser(usage="%prog [options]")

    common = OptionGroup(parser, "Urwid", _("Option of urwid explorer"))
    common.add_option("--preload", help=_("Number of fields to preload at each read"),
        type="int", action="store", default=15)
    common.add_option("--path", help=_("Initial path to focus on"),
        type="str", action="store", default=None)
    common.add_option("--parser", help=_("Use the specified parser (use its identifier)"),
        type="str", action="store", default=None)
    common.add_option("--offset", help=_("Skip first bytes of input file"),
        type="long", action="store", default=0)
    common.add_option("--parser-list",help=_("List all parsers then exit"),
        action="callback", callback=displayParserList)
    common.add_option("--profiler", help=_("Run profiler"),
        action="store_true", default=False)
    common.add_option("--profile-display", help=_("Force update of the screen beetween each event"),
        action="store_true", default=False)
    common.add_option("--size", help=_("Maximum size of bytes of input file"),
        type="long", action="store", default=None)
    common.add_option("--hide-value", dest="display_value", help=_("Don't display value"),
        action="store_false", default=True)
    common.add_option("--hide-size", dest="display_size", help=_("Don't display size"),
        action="store_false", default=True)
    common.add_option("--version", help=_("Display version and exit"),
        action="callback", callback=displayVersion)
    parser.add_option_group(common)

    hachoir = getHachoirOptions(parser)
    parser.add_option_group(hachoir)

    values, arguments = parser.parse_args()
    if len(arguments) != 0:
        parser.print_help()
        sys.exit(1)
    return values

def profile(func, *args):
    from hachoir_core.profiler import runProfiler
    runProfiler(func, args)

def openParser(parser_id, filename, offset, size):
    tags = []
    if parser_id:
        tags += [ ("id", parser_id), None ]
    try:
        #stream = FileInputStream(unicodeFilename(filename), filename, offset=offset, size=size, tags=tags)
        # TODO go get data from db (jam together time, type, header, and packet)
        data = b"ROZ" + b"\2" + b"s\0e\2"
        stream = StringInputStream(data)
    except InputStreamError, err:
        return None, _("Unable to open stream [not file]: %s") % err
    parser = guessParser(stream)
    if not parser:
        return None, _("Unable to parse stream [not file]: %s") % filename
    return parser, None

def main():
    # Parser options and initialize Hachoir
    values = parseOptions()
    configureHachoir(values)

    # Open file and create parser
    filename = 'placeholder4dbQueryStuff'
    parser, err = openParser(values.parser, filename, values.offset, values.size)
    if err:
        print err
        sys.exit(1)

    # Explore file
    if values.profiler:
        ok = profile(exploreFieldSet, parser, values)
    else:
        exploreFieldSet(parser, values, {
            "display_size": values.display_size,
            "display_value": values.display_value,
        })

if __name__ == "__main__":
    main()
