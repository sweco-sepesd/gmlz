import zlib
from zipfile import ZIP_DEFLATED

'''
crc32_combine(crc1, crc2, len2)
'''

from data_generator import BBox, random_points

#from gfy_pycrc32_combine import crc32_combine
from crc32_combine import crc32_combine
'''
def crc32_combine(crc1, crc2, len2):
    import ctypes
    from ctypes import util
    _zlib = ctypes.cdll.LoadLibrary(util.find_library('z'))
    #lib = util.find_library('zlib1')
    #_zlib = ctypes.CDLL(lib)
    assert _zlib._name, "Can't find zlib"

    _zlib.crc32_combine.argtypes = [
        ctypes.c_ulong, ctypes.c_ulong, ctypes.c_ulong]
    _zlib.crc32_combine.restype = ctypes.c_ulong

    return _zlib.crc32_combine(crc1, crc2, len2)
'''
def print_hex(x, n=32, header=True):
    if header:
        print 'Length: {}'.format(len(x))
        print '     ', ' '.join(map(lambda i: '{:02d}'.format(i), range(n)))
        print '     ', '-'.join(map(lambda i: '--', range(n)))

    for i in range(0,len(x), n):
        print '{:03d}:  {}'.format(i, ' '.join('{:02X}'.format(ord(c)) for c in x[i:i+n]))

# set small for test purpuse - would perhaps make more sense if we consider compressed size instead here
FLUSH_WHEN = 100
def testrun(n=10):
	'''
	n: number of points to generate

	Simulates writing of gml:ish data where bbox of all input needs to be at top of xml-file.
	Writing is done in compressed chunks to a temporary buffer (fout_tail) as points are input.
	BBox of seen input is expanded along the way
	When no more input, we write the start of doc to final output as a compressed chunk.
	Then we can copy our temporary buffer of already compressd data to final_output and write end of document (closing tag)
	The CRC32 for the final documents uncompressed data is calculated using zlib crc32_combine.
	Indices to chunks in the compressed stream is kept and could be saved separately for random access into the compressed stream.

	to further improve writing maybe pigz could be used: http://zlib.net/pigz/
	'''
	from cStringIO import StringIO
	fout_tail = StringIO()
	compressor = zlib.compressobj(6, ZIP_DEFLATED, -9)
	bbox = BBox()
	crc_tail = None
	len_tail = 0 # total length of tail uncompressed data
	unflushed = 0 # length of uncompressed data not yet flushed
	#compressed_len = 0 # length of compressed data not yet flushed
	indices = [0]
	fragments = [] # used for verification
	for p in random_points(n):
		bbox.expand(p)
		data = str(p) + '\n'
		fout_tail.write(compressor.compress(data))
		# TODO: Find out when exactly (and possibly why) we need to do & 0xffffffff
		crc_tail = zlib.crc32(data, crc_tail) & 0xffffffff if crc_tail else zlib.crc32(data) & 0xffffffff
		len_tail += len(data)
		unflushed += len(data)
		if unflushed >= FLUSH_WHEN:
			fout_tail.write(compressor.flush(zlib.Z_FULL_FLUSH)) # what's the difference between Z_FULL_FLUSH and Z_SYNC_FLUSH ?
			#fout_tail.write(compressor.flush(zlib.Z_SYNC_FLUSH))
			indices.append(fout_tail.tell()) # we keep track of position *after* our chunk
			unflushed = 0
		fragments.append(data)

	footer = '\n</xmldata>\n'
	crc_tail = zlib.crc32(footer, crc_tail) & 0xffffffff
	len_tail += len(footer)
	fragments.append(footer)

	fout_tail.write(compressor.compress(footer))
	fout_tail.write(compressor.flush(zlib.Z_FINISH))
	fout_tail.flush()
	del compressor

	fout_final = StringIO()
	compressor = zlib.compressobj(6, ZIP_DEFLATED, -9)

	header = '''<?xml version="1.0" encoding="UTF-8"?>
	<xmldata>
	{}
	'''.format(bbox)

	crc1 = zlib.crc32(header) & 0xffffffff
	fragments.insert(0, header)

	fout_final.write(compressor.compress(header))
	fout_final.write(compressor.flush(zlib.Z_FULL_FLUSH))
	#fout_final.write(compressor.flush(zlib.Z_SYNC_FLUSH))

	header_compressed_chunk_size = fout_final.tell()

	fout_final.write(fout_tail.getvalue())
	fout_tail.close()
	del fout_tail

	indices = map(lambda x: x + header_compressed_chunk_size, indices)

	crc12 = crc32_combine(crc1, crc_tail, len_tail) & 0xFFFFFFFF
	#crc21 = crc32_combine(crc2, crc1, len(header))
	doc = ''.join(fragments)
	return crc12, len_tail, doc, zlib.crc32(doc) & 0xFFFFFFFF, fout_final.getvalue(), indices

for i in range(1):
	crc12, len2, doc, crcdoc, compressed_data, indices = testrun(100)
	print '\t'.join(map(str,[crc12, len2, crcdoc, crc12 == crcdoc, len(compressed_data) * 100.0 / len(doc)]))
	decompressor = zlib.decompressobj(-9)
	print zlib.crc32(decompressor.decompress(compressed_data)) & 0xFFFFFFFF
	print len(indices)
	#decompressor = zlib.decompressobj(-9)
	last_pos = 0
	continue
	for pos in indices:
		decompressor = zlib.decompressobj(-9)
		print(decompressor.decompress(compressed_data[last_pos:pos]))
		print_hex(compressed_data[last_pos:pos])
		#print compressed_data
		data = bytearray(compressed_data[last_pos:pos])
		print "format(ord(compressed_data[last_pos]), '#010b'): ", format(ord(compressed_data[last_pos]), '#010b')
		print "format(0x80, '#010b')", format(0x80, '#010b')
		print "format(data[0], '#010b')", format(data[0], '#010b')
		data[0] = data[0] | 0x80
		data = data[0:len(data)-4]
		print 'last byte:', format(data[len(data)-1], '#010b')
		#print_hex(str(data))
		print "format(data[0], '#010b')", format(data[0], '#010b')
 		# works for last block only - zlib.error: Error -3 while decompressing data: invalid bit length repeat
		# for intermediate chunks we can use a new decompressobj.decompress which is said to ignore some things - seems to work, not fully understood.
		# Some details on the stream format here: http://www.bolet.org/~pornin/deflate-flush.html
		#print zlib.decompress(str(data), -9)
		last_pos = pos
	print(decompressor.decompress(compressed_data[last_pos:]))
	print format(ord(compressed_data[last_pos]), '#010b')
	print_hex(compressed_data[last_pos:])
	data = compressed_data[last_pos:]
	print zlib.decompress(data, -9) # works for last block
