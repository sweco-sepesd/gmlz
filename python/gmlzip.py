import os
import os.path
import zlib
import xml.parsers.expat
import sqlite3
import struct

DEFAULT_NS_ID = 0
NS_SEP = ' '
ns_map = {}
xpath = []
qnames = {}
xpaths = {}

class Indexer(object):
    def __init__(self):
        self.conn = None
        self.parser = None
        self.ns_map = {}
        self.qname_map = {}
        self.xpath_map = {}
        self.xpath = []
    def import_gml(self, gml_file, sqlite_file=':memory:', overwrite=True):
        self._open_db(sqlite_file, overwrite)
        self.parser = xml.parsers.expat.ParserCreate(namespace_separator=NS_SEP)
        self.parser.StartNamespaceDeclHandler = self._start_ns_decl
        self.parser.StartElementHandler = self._start_element
        self.parser.EndElementHandler = self._end_element
        self._clear_state()
        with open(gml_file, 'rb') as fin:
            self.parser.ParseFile(fin)
            self.conn.commit()
        self._post_import()
        return 0
    def _post_import(self):
        cur = self.conn.cursor()
        cur.execute('create table if not exists xpath_elements(crc integer, level integer, qname integer, primary key (crc, level)) without rowid')
        # [item for sublist in l for item in sublist]
        cur.executemany('insert into xpath_elements(crc, level, qname) values(?, ?, ?)'
                    ,  [(crc, level, qname) for crc, qnames in self.xpath_map.items() for level, qname in enumerate(qnames)])
        self.conn.commit()
        #cur.executemany

    def _clear_state(self):
        self.ns_map = {}     # {uri: id [, ...]}
        self.qname_map = {}  # {qname: id [, ...]}
        self.xpath_map = {}  # {crc: id [, ...]}
        self.xpath = []      # [crc, crc, crc ...]
    def _open_db(self, fp, overwrite):
        self._close_db()
        if overwrite and os.path.exists(fp) and os.path.isfile(fp):
            os.remove(fp)
        self.conn = sqlite3.connect(fp)
        cur = self.conn.cursor()
        cur.execute('create table if not exists namespace(id integer primary key, uri text, prefix text)')
        cur.execute('create table if not exists qname(id integer primary key, ns_id integer, local_name text)')
        cur.execute('create table if not exists xpath(crc integer primary key, parent_crc integer, qname integer)')
    def _close_db(self):
        if self.conn != None:
            self.conn.close()
    def _start_ns_decl(self, prefix, uri):
        if not uri in self.ns_map:
            cur = self.conn.cursor()
            ns_id = len(self.ns_map)
            cur.execute('insert into namespace(id, uri, prefix) values (?, ?, ?)'
                        , (ns_id, uri, prefix))
            self.ns_map[uri] = ns_id
            print('NS ', ns_id, '\t', prefix, '\t', uri)
    def _start_element(self, qname, attributes):
        ns_uri, local_name = qname.split(NS_SEP)
        if not ns_uri in self.ns_map:
            raise Exception('namespace not declared')
        ns_id = self.ns_map[ns_uri]
        if not qname in self.qname_map:
            cur = self.conn.cursor()
            qname_id = len(self.qname_map)
            cur.execute('insert into qname(id, ns_id, local_name) values (?, ?, ?)'
                        , (qname_id, ns_id, local_name))
            self.qname_map[qname] = qname_id
            print('QN ', qname_id, '\t', ns_id, '\t', local_name)
        qname_id = self.qname_map[qname]
        qname_id_bytes = struct.pack('<I', qname_id)
        parent_xpath_crc = self.xpath[-1] if len(self.xpath) else 0
        xpath_crc = zlib.crc32(qname_id_bytes, parent_xpath_crc) & 0xffffffff
        self.xpath.append(xpath_crc)
        if not xpath_crc in self.xpath_map:
            cur = self.conn.cursor()
            cur.execute('insert into xpath(crc, parent_crc, qname) values (?, ?, ?)'
                        , (xpath_crc, parent_xpath_crc, qname_id))
            xpath_elements = self.xpath_map.get(parent_xpath_crc, []) + [qname_id]
            xpath_text = '/'.join(map(str, xpath_elements))
            self.xpath_map[xpath_crc] = xpath_elements
            print('XP ', xpath_text)

    def _end_element(self, qname):
        if len(self.xpath):
           self.xpath.pop()
            
    def __del__(self):
        self._close_db()

if __name__ == '__main__':
    import sys
    src_gml = r"C:\Users\sepesd\Downloads\FormOfWay_GML_UTM32-EUREF89\DK_FormOfWay.gml"
    dst_db = r"C:\Users\sepesd\Downloads\FormOfWay_GML_UTM32-EUREF89\DK_FormOfWay.sqlite"
    indexer = Indexer()
    exit(indexer.import_gml(src_gml,sqlite_file=dst_db))


'''
-- can not be used from within fme
create view xpath_resolved as 
with recursive x(crc, parent_crc, qname) as (
    select 
        xpath.crc
        , xpath.parent_crc
        , namespace.uri || ' ' || qname.local_name qname
    from xpath, qname, namespace 
    where xpath.qname = qname.id 
        and qname.ns_id = namespace.id
), xp(crc, path) as (
    select crc, qname path from x where parent_crc = 0
    union all select x.crc, xp.path || '/' || qname from xp, x where xp.crc = x.parent_crc
)
select * from xp;



with recursive t(crc, parent_crc, level, qname) as (
    select crc, parent_crc, 0 level, qname
    from xpath
    where parent_crc = 0
    union all
    select xp.crc, xp.parent_crc, t.level + 1, xp.qname
    from xpath xp, t
    where xp.parent_crc = t.crc
)
select count(*) 
from t
order by crc;




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

'''