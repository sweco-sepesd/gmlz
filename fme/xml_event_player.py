import sys
sys.path.append('bidict-0.13.1-py2.7.egg')
from bidict import bidict

import fmeobjects
import xml.parsers.expat
import json

HANDLER_LUT = {'start_doctype_decl': 'StartDoctypeDeclHandler'
, 'start_cdata_section': 'StartCdataSectionHandler'
, 'unparsed_entity_decl': 'UnparsedEntityDeclHandler'
, 'element_decl': 'ElementDeclHandler'
, 'not_standalone': 'NotStandaloneHandler'
, 'character_data': 'CharacterDataHandler'
, 'end_namespace_decl': 'EndNamespaceDeclHandler'
, 'default': 'DefaultHandler'
, 'end_element': 'EndElementHandler'
, 'attlist_decl': 'AttlistDeclHandler'
, 'comment': 'CommentHandler'
, 'end_doctype_decl': 'EndDoctypeDeclHandler'
, 'external_entity_ref': 'ExternalEntityRefHandler'
, 'end_cdata_section': 'EndCdataSectionHandler'
, 'processing_instruction': 'ProcessingInstructionHandler'
, 'start_element': 'StartElementHandler'
, 'xml_decl': 'XmlDeclHandler'
, 'start_namespace_decl': 'StartNamespaceDeclHandler'
, 'skipped_entity': 'SkippedEntityHandler'
, 'entity_decl': 'EntityDeclHandler'
, 'notation_decl': 'NotationDeclHandler'
}

NS_DELIM = ' '

class FeatureProcessor(object):
    def __init__(self):
        self.parser = None
        self.path = None
        self.nsmap = bidict()
        self.max_events = 0
        self.event_nbr = 0
    def create_feature(self, xml_event):
        feature = fmeobjects.FMEFeature()
        feature.setAttribute('xml_event', xml_event)
        feature.setAttribute('xml_event_nbr', self.event_nbr)
        feature.setAttribute('xml_byte_index', self.parser.CurrentByteIndex)
        feature.setAttribute('xml_line_nbr', self.parser.CurrentLineNumber)
        feature.setAttribute('xml_col_nbr', self.parser.CurrentColumnNumber)
        if self.path:
            feature.setAttribute('xml_path', '/'.join(self.path))
        return feature
    def input(self,feature):
        source = feature.getAttribute('__xml_source')
        events = feature.getAttribute('__events').split(' ')
        max_events = feature.getAttribute('__max_events')
        if max_events != '':
            self.max_events = int(max_events)
        if feature.getAttribute('__produce_path') == 'Yes':
            self.path = ['']
        self.parser = xml.parsers.expat.ParserCreate(namespace_separator=NS_DELIM)
        for event in events:
            if hasattr(self, event):
                setattr(self.parser, HANDLER_LUT[event], getattr(self, event))
        with open(source, 'rb') as fin:
            for chunk in iter((lambda:fin.read(1024*64)),''):
                if self.max_events and self.event_nbr >= self.max_events:
                    break
                self.parser.Parse(chunk, False)
        if self.max_events and self.event_nbr >= self.max_events:
            return
        self.parser.Parse('', True)
    def close(self):
        pass
    def attlist_decl(self):
        self.event_nbr += 1
        feature = self.create_feature('attlist_decl')
        self.pyoutput(feature)
    def character_data(self, data):
        self.event_nbr += 1
        feature = self.create_feature('character_data')
        feature.setAttribute('data', data)
        self.pyoutput(feature)
    def comment(self, data):
        self.event_nbr += 1
        feature = self.create_feature('comment')
        feature.setAttribute('data', data)
        self.pyoutput(feature)
    def default(self,data):
        self.event_nbr += 1
        feature = self.create_feature('default')
        feature.setAttribute('data',data)
        self.pyoutput(feature)
    def element_decl(self, name, model):
        self.event_nbr += 1
        feature = self.create_feature('element_decl')
        feature.setAttribute('name',name)
        feature.setAttribute('model',model)
        self.pyoutput(feature)
    def end_cdata_section(self):
        self.event_nbr += 1
        feature = self.create_feature('end_cdata_section')
        self.pyoutput(feature)
    def end_doctype_decl(self):
        self.event_nbr += 1
        feature = self.create_feature('end_doctype_decl')
        self.pyoutput(feature)
    def end_element(self, name):
        self.event_nbr += 1
        feature = self.create_feature('end_element')
        feature.setAttribute('name', name)
        self.pyoutput(feature)
        if self.path: self.path.pop()
    def end_namespace_decl(self, prefix):
        self.event_nbr += 1
        feature = self.create_feature('end_namespace_decl')
        feature.setAttribute('prefix', prefix)
        self.pyoutput(feature)
        del self.nsmap[prefix]
    def entity_decl(self, entityName, is_parameter_entity, value, base, systemId, publicId, notationName):
        self.event_nbr += 1
        feature = self.create_feature('entity_decl')
        feature.setAttribute('entityName',entityName)
        feature.setAttribute('is_parameter_entity',is_parameter_entity)
        feature.setAttribute('value',value)
        feature.setAttribute('base',base)
        feature.setAttribute('systemId',systemId)
        feature.setAttribute('publicId',publicId)
        feature.setAttribute('notationName',notationName)
        self.pyoutput(feature)
    def external_entity_ref(self, context, base, systemId, publicId):
        self.event_nbr += 1
        feature = self.create_feature('external_entity_ref')
        feature.setAttribute('context',context)
        feature.setAttribute('base',base)
        feature.setAttribute('systemId',systemId)
        feature.setAttribute('publicId',publicId)
        self.pyoutput(feature)
    def not_standalone(self):
        self.event_nbr += 1
        feature = self.create_feature('not_standalone')
        self.pyoutput(feature)
    def notation_decl(self, notationName, base, systemId, publicId):
        self.event_nbr += 1
        feature = self.create_feature('notation_decl')
        feature.setAttribute('notationName',notationName)
        feature.setAttribute('base',base)
        feature.setAttribute('systemId',systemId)
        feature.setAttribute('publicId',publicId)
        self.pyoutput(feature)
    def processing_instruction(self, target, data):
        self.event_nbr += 1
        feature = self.create_feature('processing_instruction')
        feature.setAttribute('target', target)
        feature.setAttribute('data', data)
        self.pyoutput(feature)
    def skipped_entity(self, entityName, is_parameter_entity):
        self.event_nbr += 1
        # This method was not documented on the expat website...
        feature = self.create_feature('skipped_entity')
        feature.setAttribute('entityName',entityName)
        feature.setAttribute('is_parameter_entity',is_parameter_entity)
        self.pyoutput(feature)
    def start_cdata_section(self):
        self.event_nbr += 1
        feature = self.create_feature('start_cdata_section')
        self.pyoutput(feature)
    def start_doctype_decl(self, doctypeName, systemId, publicId, has_internal_subset):
        self.event_nbr += 1
        feature = self.create_feature('start_doctype_decl')
        feature.setAttribute('doctypeName',doctypeName)
        feature.setAttribute('systemId',systemId)
        feature.setAttribute('publicId',publicId)
        feature.setAttribute('has_internal_subset',has_internal_subset)
        self.pyoutput(feature)
    def start_element(self, name, attrs):
        self.event_nbr += 1
        tokens = name.split(NS_DELIM)
        if len(tokens) == 2:
            uri, name = tokens
            prefix = self.nsmap.inv.get(uri, uri)
            name = '{}:{}'.format(prefix, name)
        if self.path: self.path.append(name)
        feature = self.create_feature('start_element')
        feature.setAttribute('name', name)
        feature.setAttribute('attrs', json.dumps(attrs))
        self.pyoutput(feature)
    def start_namespace_decl(self, prefix, uri):
        self.event_nbr += 1
        self.nsmap[prefix] = uri
        feature = self.create_feature('start_namespace_decl')
        feature.setAttribute('prefix', prefix)
        feature.setAttribute('uri', uri)
        self.pyoutput(feature)
    def unparsed_entity_decl(self):
        self.event_nbr += 1
        feature = self.create_feature('unparsed_entity_decl')
        self.pyoutput(feature)
    def xml_decl(self, version, encoding, standalone):
        self.event_nbr += 1
        feature = self.create_feature('xml_decl')
        if version != None: feature.setAttribute('version', version)
        if encoding != None: feature.setAttribute('encoding', encoding)
        if standalone != None: feature.setAttribute('standalone', standalone)
        self.pyoutput(feature)
