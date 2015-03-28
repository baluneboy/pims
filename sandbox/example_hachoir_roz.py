"""
A silly example for binary file parser.

Author: Kenneth Hrovat
Creation date: 2014-10-18
"""

from hachoir_parser import Parser
from hachoir_core.field import FieldSet, UInt8, Character, String
from hachoir_core.stream import StringInputStream, LITTLE_ENDIAN

def displayTree(parent):
    for field in parent:
        #print field.path, 'is', field.value
        #if field.is_field_set: displayTree(field)
        print field.path,
        if field.is_field_set:
            print
            displayTree(field)
        else:
            print 'is', field.value

class Entry(FieldSet):
    def createFields(self):
        yield Character(self, "letter")
        yield UInt8(self, "code")

class BinaryRozFile(Parser):
    endian = LITTLE_ENDIAN
    PARSER_TAGS = {
        "id": "roz",
        "category": "misc",
        "file_ext": ("roz",),
        "min_size": 1*8, # FIXME
        "description": "A roz file.",
    }

    def validate(self):
        if self["signature"].value != "ROZ":
            return "Invalid signature (%s)" % self["signature"].value
        return True

    def createFields(self):
        yield String(self, "signature", 3, charset="ASCII")
        yield UInt8(self, "count")
        for index in range(self["count"].value):
            yield  Entry(self, "point[]")

#print 'BinaryRozFile here'
#data = b"ROZ\3s\0e\2X\0"
#stream = StringInputStream(data)
#root = BinaryRozFile(stream)
#displayTree(root)

#if __name__ == "__main__":
#    from hachoir_parser import HachoirParser
#    print issubclass(BinaryRozFile, HachoirParser)
