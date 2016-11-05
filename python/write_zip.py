class Point(object):
    def __init__(self, x,y):
        self.x = x
        self.y = y
    def to_xml(self):
        return '<point x="{}" y = "{}"/>'.format(self.x, self.y)
class Box(object):
    def __init__(self):
        self.minx = 9999999.999
        self.miny = 9999999.999
        self.maxx = -9999999.999
        self.maxy = -9999999.999
def print_hex(x, n=32, header=True):
    if header:
        print 'Length: {}'.format(len(x))
        print '     ', ' '.join(map(lambda i: '{:02d}'.format(i), range(n)))
        print '     ', '-'.join(map(lambda i: '--', range(n)))

    for i in range(0,len(x), n):
        print '{:03d}:  {}'.format(i, ' '.join('{:02X}'.format(ord(c)) for c in x[i:i+n]))

from gzip import GzipFile
from zipfile import ZipFile, ZIP_DEFLATED
import zlib
from cStringIO import StringIO
import struct

header = '''<?xml version="1.0" encoding="UTF-8"?>
<xmldata>
<bbox>1234567.123 1234567.123 1234567.123 1234567.123</bbox>
'''

pts_data1 = '''<point id="asdf" x="1" y="2"/>
<point id="bsdf" x="2" y="2"/>
<point id="csdf" x="3" y="2"/>
<point id="dsdf" x="4" y="2"/>
<point id='''
pts_data2 = '''"esdf" x="5" y="2"/>
<point id="fsdf" x="6" y="2"/>
<point id="gsdf" x="7" y="2"/>
<point id="hsdf" x="8" y="2"/>
<point id="isdf" x="9" y="2"/>
<point id="jsdf" x="10" y="2"/>
'''

footer = '''</xmldata>
'''

print 'Payload:\n', header
print_hex(header)

x = zlib.compress(header)
y = zlib.compress(pts_data1)
z = zlib.compress(pts_data2)

print '\nzlib.compress x:'
print_hex(x)

print bin(ord(x[0])), bin(ord(x[1])), bin(ord(x[2]))

print '\nzlib.compress y:'
print_hex(y)

print bin(ord(y[0]))

print '\nzlib.compress z:'
print_hex(z)

print bin(ord(z[0]))
'''
28. Can I access data randomly in a compressed stream?

No, not without some preparation.
If when compressing you periodically use Z_FULL_FLUSH, carefully write all the
pending data at those points, and keep an index of those locations, then you can
start decompression at those points. You have to be careful to not use
Z_FULL_FLUSH too often, since it can significantly degrade compression.
Alternatively, you can scan a deflate stream once to generate an index, and then
use that index for random access. See examples/zran.c.
'''
compressor = zlib.compressobj(6, ZIP_DEFLATED, -9)
print '\n:'
print_hex(compressor.compress(header))
print '\n:'
print_hex(compressor.compress(pts_data1))
print '\n:'
print_hex(compressor.compress(pts_data2))
print '\n:'
print_hex(compressor.flush(zlib.Z_FULL_FLUSH))
print '\n:'
print_hex(compressor.compress(footer))
print '\n:'
print_hex(compressor.flush(zlib.Z_FULL_FLUSH))

compressor = zlib.compressobj(6, ZIP_DEFLATED, -9)

parts = map(lambda data: compressor.compress(data) + compressor.flush(zlib.Z_FULL_FLUSH), (header, pts_data1, pts_data2, footer))
print '\nparts:'
map(print_hex, parts)

decompressor = zlib.decompressobj(-9)

print ''.join(map(decompressor.decompress, parts))

print ''.join(map(decompressor.decompress, reversed(parts)))

print decompressor.decompress(''.join(parts))
exit(0)

gzip_out = StringIO()

gzip_file = GzipFile(mode='wb', fileobj=gzip_out)
gzip_file.write(header)
gzip_file.close()

print '\nGzipFile:'
print_hex(gzip_out.getvalue())


zip_out = StringIO()

zip_file = ZipFile(zip_out, 'w', ZIP_DEFLATED)

zip_file.writestr('header.xml', header)

zip_file.close()

print '\nZipFile:'
print_hex(zip_out.getvalue())

crc32 = zlib.crc32(header) #& 0xffffffff
print '\nCRC-32:', crc32
csc32str = struct.pack('<q', crc32)[:4]
print_hex(csc32str)

'''
Payload:
<?xml version="1.0" encoding="UTF-8"?>
<xmldata>
<bbox>1234567.123 1234567.123 1234567.123 1234567.123</bbox>

Length: 110
00:   3C 3F 78 6D 6C 20 76 65 72 73 69 6F 6E 3D 22 31 2E 30 22 20 65 6E 63 6F 64 69 6E 67 3D 22 55 54
32:   46 2D 38 22 3F 3E 0A 3C 78 6D 6C 64 61 74 61 3E 0A 3C 62 62 6F 78 3E 31 32 33 34 35 36 37 2E 31
64:   32 33 20 31 32 33 34 35 36 37 2E 31 32 33 20 31 32 33 34 35 36 37 2E 31 32 33 20 31 32 33 34 35
96:   36 37 2E 31 32 33 3C 2F 62 62 6F 78 3E 0A

zlib.compress:
Length: 78
00:   78 9C     B3 B1 AF C8 CD 51 28 4B 2D 2A CE CC CF B3 55 32 D4 33 50 52 48 CD 4B CE 4F C9 CC 4B B7 55
32:   0A 0D 71 D3 B5 50 B2 B7 E3 B2 01 AA 4A 49 2C 49 04 B2 92 92 F2 2B EC 0C 8D 8C 4D 4C CD CC F5 80
64:   B4 02 11 6C 1B 7D B0 2E 2E 00     D5 AD 1C D8

GzipFile:
Length: 90
00:   1F 8B 08 00 F5 F9 16 58 02 FF     B3 B1 AF C8 CD 51 28 4B 2D 2A CE CC CF B3 55 32 D4 33 50 52 48 CD
32:   4B CE 4F C9 CC 4B B7 55 0A 0D 71 D3 B5 50 B2 B7 E3 B2 01 AA 4A 49 2C 49 04 B2 92 92 F2 2B EC 0C
64:   8D 8C 4D 4C CD CC F5 80 B4 02 11 6C 1B 7D B0 2E 2E 00     59 1C E4 87 6E 00 00 00


ZipFile:
Length: 228                                                 + pos 18 compressed size 72 bytes -
                                                            |                       + pos 26: file name length (header.xml - 10 (0A 00 byte order big endian?) characters)
                                                + CRC-32    |                       |           + start of data stream
                                                |.......... |..........             |.......... |
      00 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31
      -----------------------------------------------------------------------------------------------
00:   50 4B 03 04 14 00 00 00 08 00 CA 55 5F 49 59 1C E4 87 48 00 00 00 6E 00 00 00 0A 00 00 00 68 65
32:   61 64 65 72 2E 78 6D 6C     B3 B1 AF C8 CD 51 28 4B 2D 2A CE CC CF B3 55 32 D4 33 50 52 48 CD 4B CE
64:   4F C9 CC 4B B7 55 0A 0D 71 D3 B5 50 B2 B7 E3 B2 01 AA 4A 49 2C 49 04 B2 92 92 F2 2B EC 0C 8D 8C
96:   4D 4C CD CC F5 80 B4 02 11 6C 1B 7D B0 2E 2E 00     50 4B 01 02 14 03 14 00 00 00 08 00 CA 55 5F 49
128:  59 1C E4 87 48 00 00 00 6E 00 00 00 0A 00 00 00 00 00 00 00 00 00 00 00 80 01 00 00 00 00 68 65
160:  61 64 65 72 2E 78 6D 6C 50 4B 05 06 00 00 00 00 01 00 01 00 38 00 00 00 70 00 00 00 00 00

CRC-32: -2015093671
Length: 4
      00 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31
      -----------------------------------------------------------------------------------------------
000:  59 1C E4 87
'''
