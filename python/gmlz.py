'''
Created on 5 nov. 2016

@author: Peter Segerstedt
'''
import shutil, struct, time
from zipfile import LargeZipFile, ZipFile, ZipInfo, ZIP_DEFLATED, ZIP64_LIMIT
from StringIO import StringIO
import zlib
import io
from tempfile import TemporaryFile
crc32 = zlib.crc32

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

_GMLZBUFFER_MAX_SIZE = 4096

class GmlZBuffer(io.IOBase):
    '''
    
    '''
    def __init__(self):
        self.buffer = StringIO()
        self.compressor = zlib.compressobj(6, ZIP_DEFLATED, -9)
        self.overflow = False
        self.crc = 0
        self.uncompressed_size = 0
        self.compressed_size = 0
        self.compressed_chunk_mark = 0
    def write(self, data):
        self.crc = zlib.crc32(data, self.crc) & 0xffffffff
        self.uncompressed_size += len(data)
        compressed_data = self.compressor.compress(data)
        if not (compressed_data and len(compressed_data)):
            return 0
        compressed_size = len(compressed_data)
        self._prepare_write(compressed_size)
        self.buffer.write(compressed_data)
        self.compressed_size += compressed_size
        return compressed_size
    def _prepare_write(self, length):
        if self.overflow: return
        if self.buffer.tell() + length > _GMLZBUFFER_MAX_SIZE:
            data = self.buffer.getvalue()
            self.buffer.close()
            self.buffer = TemporaryFile()
            self.buffer.write(data)
            self.overflow = True
    def flush(self):
        prev_mark = self.mark
        compressed_data = self.compressor.flush(zlib.Z_FULL_FLUSH)
        compressed_size = len(compressed_data)
        self._prepare_write(compressed_size)
        self.buffer.write(compressed_data)
        self.compressed_size += compressed_size
        self.mark = self.buffer.tell()
        return prev_mark, self.mark
        # TODO: verify working, useful...
 
class GmlZFile(ZipFile):
    def writecompressed(self, zinfo_or_arcname, compressed_input, crc, uncompressed_size, compressed_size, compress_type=ZIP_DEFLATED):
        """Write pre compressed data into the archive.

        This method could be useful in a case when data needs to be stored in
        a different order from what it is being produced. For example when
        writing a GML-file, the bbox element needs to be written at the top of
        the document. Naturally this can not be produced until all members of
        the final document has been visited. The 'compressed_input' can be an
        itarator of file like objects or strings. In the GML case the head of
        the file would probably come from a StringIO object, bulk from temp file
        and tail from StringIO object. Care has to be taken to properly compose
        the different pre-compressed parts so that the concatenated value
        becomes a valid deflate-stream. Also note that the combined crc32 has to
        be calculated in correct order. This can be achieved using method
        crc32_combine from zlib.

        zinfo_or_arcname:  Either a ZipInfo instance or the name of the file in
                           the archive.
        compressed_input:  The pre compressed content. This can be either a
                           string, a file object or an iterator. If input is an
                           iterator, each item will be checked if it's a string
                           or file object.
        crc:               The CRC32 checksum of the (combined) input.
        uncompressed_size:
        compressed_size:
        compress_type:
         """
        if not compress_type == self.compression: raise RuntimeError(
            "Pre compressed data has to be of same kind as this archive uses, got {}, expected {}".format(compress_type, self.compression))
        if not isinstance(zinfo_or_arcname, ZipInfo):
            zinfo = ZipInfo(filename=zinfo_or_arcname,
                            date_time=time.localtime(time.time())[:6])

            zinfo.compress_type = self.compression
            if zinfo.filename[-1] == '/':
                zinfo.external_attr = 0o40775 << 16   # drwxrwxr-x
                zinfo.external_attr |= 0x10           # MS-DOS directory flag
            else:
                zinfo.external_attr = 0o600 << 16     # ?rw-------
        else:
            zinfo = zinfo_or_arcname

        if not self.fp:
            raise RuntimeError(
                  "Attempt to write to ZIP archive that was already closed")

        if compress_type is not None:
            zinfo.compress_type = compress_type

        zinfo.file_size = uncompressed_size     # Uncompressed size
        zinfo.header_offset = self.fp.tell()    # Start of header bytes
        self._writecheck(zinfo)
        self._didModify = True
        zinfo.CRC = crc & 0xffffffff            # CRC-32 checksum

        zinfo.compress_size = compressed_size

        zip64 = zinfo.file_size > ZIP64_LIMIT or \
                zinfo.compress_size > ZIP64_LIMIT
        if zip64 and not self._allowZip64:
            raise LargeZipFile("Filesize would require ZIP64 extensions")
        self.fp.write(zinfo.FileHeader(zip64))

        if isinstance(compressed_input, basestring):
            self.fp.write(compressed_input)
        elif hasattr(compressed_input, '__iter__'):
            for o in compressed_input:
                if isinstance(o, basestring):
                    self.fp.write(o)
                else:
                    shutil.copyfileobj(o, self.fp)
        else:
            shutil.copyfileobj(compressed_input, self.fp)

        if zinfo.flag_bits & 0x08:
            # Write CRC and file sizes after the file data
            fmt = '<LQQ' if zip64 else '<LLL'
            self.fp.write(struct.pack(fmt, zinfo.CRC, zinfo.compress_size,
                  zinfo.file_size))
        self.fp.flush()
        self.filelist.append(zinfo)
        self.NameToInfo[zinfo.filename] = zinfo
        return
