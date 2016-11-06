'''
Created on 5 nov. 2016

@author: Peter Segerstedt
'''
import binascii, os, shutil, struct, time
from zipfile import LargeZipFile, ZipFile, ZipInfo, ZIP_DEFLATED, ZIP64_LIMIT

try:
    import zlib # We may need its compression method
    crc32 = zlib.crc32
except ImportError:
    zlib = None
    crc32 = binascii.crc32

class GmlZFile(ZipFile):
    def writecompressed(self, zinfo_or_arcname, compressed_input, crc, uncompressed_size, compressed_size, compress_type=ZIP_DEFLATED):
        """Write pre compressed data into the archive.
        
        zinfo_or_arcname: Either a ZipInfo instance or the name of the file in the archive.
        compressed_input: The pre compressed content. This can be either a string, a file object or an iterator.
        If input is an iterator, each item will be checked if it's a string or file object.
        crc: The CRC32 checksum of the (combined) input.
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
        
        # Check if we were passed a file-like object
        # TODO: Add more possibilities and checks here. 
        # Most important probably is iterator of file like objects so 
        # that we can have separate streams for different parts of the input.
        # Head of file would probably come from a StringIO object, bulk from temp file and tail from StringIO object 
        
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
