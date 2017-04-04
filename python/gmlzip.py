import zlib
import xml.parsers.expat

NS_SEP = ' '
ns_map = {}
xpath = []
qnames = {}
xpaths = {}


import ctypes
from ctypes import util
#_zlib = ctypes.cdll.LoadLibrary(util.find_library('z'))
lib = util.find_library('zlib1')
_zlib = ctypes.CDLL(lib)
assert _zlib._name, "Can't find zlib"

_zlib.crc32_combine.argtypes = [
    ctypes.c_ulong, ctypes.c_ulong, ctypes.c_ulong]
_zlib.crc32_combine.restype = ctypes.c_ulong



def start_ns_decl(prefix, uri):
    if not uri in ns_map:
        uri_bytes = bytes(uri, 'utf8')
        crc = zlib.crc32(uri_bytes, 0) & 0xffffffff
        ns_map[uri] = (crc,prefix, len(uri_bytes))
        print(prefix, uri, crc)

def start_element(qname, attributes):
    ns_uri, localname = qname.split(NS_SEP)
    if not ns_uri in ns_map:
        raise Exception('namespace not declared')
    ns_crc, ns_prefix, ns_len_bytes = ns_map[ns_uri]
    localname_bytes = bytes(localname, 'utf8')
    qname_crc = zlib.crc32(localname_bytes, ns_crc) & 0xffffffff
    if not qname_crc in qnames:
        qnames[qname_crc] = (ns_uri, localname)
    if not len(xpath):
        if not qname_crc in xpaths:
            xpaths[qname_crc] = qname
        xpath.append(qname_crc)
    else:
        prev_xpath_crc = xpath[-1]
        updated_xpath_crc = zlib.crc32(bytes(ns_uri, 'utf8'), prev_xpath_crc) & 0xffffffff
        updated_xpath_crc = zlib.crc32(bytes(localname, 'utf8'), updated_xpath_crc) & 0xffffffff
        xpath.append(updated_xpath_crc)
        if updated_xpath_crc not in xpaths:
            prev_xpath = xpaths[prev_xpath_crc]
            xpaths[updated_xpath_crc] = '{}/{}'.format(prev_xpath, qname)
def end_element(qname):
    if len(xpath):
        xpath.pop()

src_gml = "C:\\Users\\sepesd\\Downloads\\167_CadastralParcel.gml"

parser = xml.parsers.expat.ParserCreate(namespace_separator=NS_SEP)

parser.StartNamespaceDeclHandler = start_ns_decl
parser.StartElementHandler = start_element
parser.EndElementHandler = end_element

with open(src_gml, 'rb') as fin:
    parser.ParseFile(fin)

for qname_crc, (ns_uri, localname) in qnames.items():
    print(qname_crc, ns_uri, localname)

for xpath_crc, full_xpath in xpaths.items():
    print(xpath_crc, full_xpath)

    