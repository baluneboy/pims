#!/usr/bin/env python

import math
import struct
import ctypes
from binascii import hexlify
from accelPacket import UnixToHumanTime, HumanToUnixTime

# prefix dictionary for struct packing
ENDIANNESS = {
    'native, native'  : '@',
    'native, standard': '=',
    'little-endian'   : '<',
    'big-endian'      : '>',
    'network'         : '!',
    'unspecified'     : '',
    }

class StringBufferPackage(object):
    
    def __init__(self, fmt, values, en='network'):
        self.byteorder = en
        self.format = ENDIANNESS[en] + ' ' + fmt
        self.values = values
        self.struct = struct.Struct(self.format)
        self.strbuf = ctypes.create_string_buffer(self.struct.size)
        self.ispacked = False
        
    def packinto(self):
        self.struct.pack_into(self.strbuf, 0, *self.values)
        self.ispacked = True
    
    def __str__(self):
        s = '-'*33 + '\n'
        s += 'Format    : "%s" (endianness prefix is "%s" for "%s" byte ordering)\n' % (self.format, ENDIANNESS[self.byteorder], self.byteorder)
        if self.ispacked:
            s += 'AfterPack : %s (hex fmt packed-into buffer with "%s" byte ordering)\n' % (hexlify(self.strbuf.raw), self.byteorder)
            s += 'Original  : %s\n' % str(self.values)
            s += 'Unpacked  : %s' % str(self.struct.unpack_from(self.strbuf, 0))
        else:
            s += 'BeforePack: %s (hex fmt pre-allocated, empty buffer)' % hexlify(self.strbuf.raw)
        s += '\n' + '-'*66
        return s
    
def show_pack(fmt, values, en='network'):
    fmt = ENDIANNESS[en] + ' ' + fmt
    s = struct.Struct(fmt)
    print 'Format    : "%s" (endianness prefix is "%s" for "%s" byte ordering)' % (fmt, ENDIANNESS[en], en)
    b = ctypes.create_string_buffer(s.size)
    print 'BeforePack:', hexlify(b.raw), '(hex fmt pre-allocated, empty buffer)'
    s.pack_into(b, 0, *values)
    print 'AfterPack :', hexlify(b.raw), '(hex fmt packed-into buffer with "%s" byte ordering)' % en
    print 'Original  :', values
    print 'Unpacked  :', s.unpack_from(b, 0)
    return b

def demo_pack_unpack(ut, endianness='network'):

    print 'human time: %s (ORIGINAL)' % UnixToHumanTime(ut), '=',
    fracsec, sec = math.modf(ut)
    usec = fracsec*1000000.0
    print 'unix time of %.3f' % ut
    print 'unix time1: %s' % format(int(sec), '#034b'),  # 32 bits  + 2 placeholders for "0b" prefix
    print '(hex: %s for sec part)' % format(int(sec), '#x')           #  8 bytes + 2 placeholders for "0x" prefix
    print 'unix time2: %s' % format(int(usec), '#034b'), # 32 bits  + 2 placeholders for "0b" prefix
    print '(hex: %s for usec part)' % format(int(usec), '#010x')       #  8 bytes + 2 placeholders for "0x" prefix   

    # old demo way to do this
    #b = show_pack('II', (int(sec), int(usec)), en=endianness) # 2nd arg for values is always a tuple
    
    # now do same thing with class way    
    sb = StringBufferPackage('II', (int(sec), int(usec)), en=endianness) # 2nd arg for values is always a tuple
    print sb
    sb.packinto()
    print sb
    
    # verify that b works like what is expected in Ted's code
    en_prefix = ENDIANNESS[endianness]
    sec1, usec1 = struct.unpack(en_prefix + 'II', sb.strbuf) # endianness refix to specify byte ordering of unpack
    print 'human time: %s (ORIGINAL)' % UnixToHumanTime(ut)
    print 'human time: %s (AFTER PACK-UNPACK)' % UnixToHumanTime( sec1 + usec1/1000000.0 )

if __name__ == "__main__":
    ut = HumanToUnixTime(2014, 10, 04, 12, 34, 56, 0.789)
    demo_pack_unpack(ut)
    
    #for fine_bin in range(0, 256):
    #    print '%03d %0.3f' %(fine_bin, fine_bin/2.0**8)
