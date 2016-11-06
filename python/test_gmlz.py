from gmlz import GmlZFile, ZIP_DEFLATED, crc32_combine
import zlib

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
        
        gmlz_file.writecompressed('test2.xml', compressed_data, crc, len(data), len(compressed_data))
        
        """Test 3"""
        filelist = ['crc32_combine.py', 'crc_experiment.py']
        compressor = zlib.compressobj(6, ZIP_DEFLATED, -9)
        compressed_input = []
        uncompressed_size = 0
        compressed_size = 0
        crc = 0
        header = ['== Here follows two concatenated files ==']
        for filename in filelist:
            with open(filename, 'rb') as fin:
                data = fin.read()                
                compressed_data = compressor.compress(data)
                crc = zlib.crc32(data, crc) & 0xffffffff
                uncompressed_size += len(data)
                compressed_size += len(compressed_data)
                compressed_input.append(compressed_data)
                header.append('{} ({} bytes):'.format(filename, len(data)))
        compressed_data = compressor.flush()
        compressed_size += len(compressed_data)
        compressed_input.append(compressed_data)
        
        compressor = zlib.compressobj(6, ZIP_DEFLATED, -9)
        header = '\n'.join(header)
        crc = crc32_combine(zlib.crc32(header) & 0xffffffff, crc, uncompressed_size)  & 0xffffffff
        uncompressed_size += len(header)
        compressed_data = compressor.compress(header)
        compressed_size += len(compressed_data)
        compressed_input.insert(0, compressed_data)
        compressed_data = compressor.flush(zlib.Z_FULL_FLUSH) # Note - not a finish flush here since we want to put this before
        compressed_size += len(compressed_data)
        compressed_input.insert(0, compressed_data)
        
        gmlz_file.writecompressed('test3.txt', compressed_input, crc, uncompressed_size, compressed_size)

        gmlz_file.close()

if __name__ == '__main__':
    import sys
    print help(GmlZFile)
    exit(Main(sys.argv[1:]).run())