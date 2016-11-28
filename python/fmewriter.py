import xml.parsers.expat

data = """<?xml version="1.0" encoding="UTF-8"?>
<gml:FeatureCollection xmlns:fme="http://www.safe.com/gml/fme" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:gml="http://www.opengis.net/gml" xsi:schemaLocation="http://www.safe.com/gml/fme FireHallsWithZones.xsd">
  <gml:boundedBy>
    <gml:Envelope srsName="EPSG:26910" srsDimension="2">
      <gml:lowerCorner>486459.325918726 5455944.71823123</gml:lowerCorner>
      <gml:upperCorner>494398.960786842 5462384.07179924</gml:upperCorner>
    </gml:Envelope>
  </gml:boundedBy>
  <gml:featureMember>
    <fme:FireHalls gml:id="idfb1ae4ef-cabd-4202-bc64-0150e655cb1a">
      <fme:HallNumber>1</fme:HallNumber>
      <fme:Name>Vancouver Fire Hall No 1</fme:Name>
      <fme:Address>900 Heatley Av</fme:Address>
      <fme:PhoneNumber>604-665-6001</fme:PhoneNumber>
      <fme:Engine>Y</fme:Engine>
      <fme:Ladder>Y</fme:Ladder>
      <fme:Quint/>
      <fme:Rescue/>
      <fme:Medic>Y</fme:Medic>
      <gml:pointProperty>
        <gml:Point srsName="EPSG:26910" srsDimension="2">
          <gml:pos>493480.244355323 5458114.84423187</gml:pos>
        </gml:Point>
      </gml:pointProperty>
    </fme:FireHalls>
  </gml:featureMember>
  <gml:featureMember>
    <fme:FireHalls gml:id="id954ead7f-99b2-4682-97a2-499a64c69ba1">
      <fme:HallNumber>2</fme:HallNumber>
      <fme:Name>Vancouver Fire Hall No 2</fme:Name>
      <fme:Address>199 Main St</fme:Address>
      <fme:PhoneNumber>604-665-6002</fme:PhoneNumber>
      <fme:Engine>Y</fme:Engine>
      <fme:Ladder/>
      <fme:Quint>Y</fme:Quint>
      <fme:Rescue/>
      <fme:Medic>Y</fme:Medic>
      <gml:pointProperty>
        <gml:Point srsName="EPSG:26910" srsDimension="2">
          <gml:pos>492725.237734015 5458965.48615312</gml:pos>
        </gml:Point>
      </gml:pointProperty>
    </fme:FireHalls>
  </gml:featureMember>
</gml:FeatureCollection>
"""
class XmlIndexer(object):
    ns_sep = ' '
    def __init__(self, fin, fout, lookfor, callback):
        self.fin = fin
        self.fout = fout
        self.lookfor = {}
        for ns, name, id_tuple in lookfor:
            key = XmlIndexer.ns_sep.join((ns,name))
            self.lookfor[key] = XmlIndexer.ns_sep.join(id_tuple)
        self.callback = callback
        self.parser = xml.parsers.expat.ParserCreate(namespace_separator=XmlIndexer.ns_sep)
        self.parser.StartElementHandler = self.start_element
        self.parser.EndElementHandler = self.end_element
        self.tic = None
    def start_element(self, name, attrs):
        if self.tic and self.tic[2]:
            #print 'End element:', name
            #print data[self.tic[0]:self.parser.CurrentByteIndex]
            self.tic = None
        if name in self.lookfor.keys():
            print 'Start element:', name, attrs[self.lookfor[name]] if self.lookfor[name] in attrs.keys() else ''
            self.tic = [self.parser.CurrentByteIndex, name, None]
    def end_element(self, name):
        if self.tic and name == self.tic[1]:
            print self.parser.GetInputContext()
            self.tic[2] = self.parser.CurrentByteIndex
    def go(self):
        self.parser.Parse(self.fin, 1)


indexer = XmlIndexer(fin=data, fout=None, lookfor=[('http://www.safe.com/gml/fme','FireHalls',('http://www.opengis.net/gml', 'id') )], callback=None)
indexer.go()

print 'helo'
