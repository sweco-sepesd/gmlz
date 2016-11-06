from gmlz import GmlZFile, ZIP_DEFLATED
import zlib
from crc32_combine import crc32_combine

def iterfiles(filepaths, mode = 'rb'):
    for filepath in filepaths:
        yield open(filepath, mode)

class Main(object):
    def __init__(self, argv):
        if len(argv):
            self.run = self.__getattribute__(argv[0])
            self.argv = argv[1:]
        else: 
            self.run = self.help
    def help(self):
        print self.argv
        return 0
    def gmlz_write(self):
        print 'helo', self.argv
        gmlz_file = GmlZFile('gmlz_write.zip', mode="w", compression=ZIP_DEFLATED)
        gmlz_file.writestr('test1.xml','<xml></xml>', compress_type=ZIP_DEFLATED)
        
        
        compressor = zlib.compressobj(6, ZIP_DEFLATED, -9)
        
        data = '<xml></xml>'
        compressed_data = compressor.compress(data) + compressor.flush()
        crc = zlib.crc32(data)
        
        gmlz_file.writecompressed('test_prcompressed.xml', compressed_data, crc, len(data), len(compressed_data))
        
        filelist = ['crc32_combine.py', 'asdf']
        gen = iterfiles(filelist)
        print type(filelist), type(gen), isinstance(filelist, list) , hasattr(gen, '__iter__')
        
        gmlz_file.close()

if __name__ == '__main__':
    import sys
    print help(GmlZFile)
    exit(Main(sys.argv[1:]).run())