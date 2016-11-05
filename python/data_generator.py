class Point(object):
    def __init__(self, x,y):
        self.x = x
        self.y = y
    def __str__(self):
        return '<point x="{}" y="{}"/>'.format(self.x, self.y)
class BBox(object):
    def __init__(self):
        self.minx = 9999999.999
        self.miny = 9999999.999
        self.maxx = -9999999.999
        self.maxy = -9999999.999
    def expand(self, p):
        if p.x < self.minx: self.minx = p.x
        if p.y < self.miny: self.miny = p.y
        if p.x > self.maxx: self.maxx = p.x
        if p.y > self.maxy: self.maxy = p.y
    def __str__(self):
        return '<bbox>{} {} {} {}</bbox>'.format(self.minx, self.miny, self.maxx, self.maxy)
def random_points(n=10,x0=-1,y0=-1,w=2,h=2):
    import random
    for i in xrange(n):
        x = random.uniform(x0, x0 + w)
        y = random.uniform(y0, y0 + h)
        yield Point(x,y)
if __name__ == '__main__':
    bbox = BBox()
    for p in random_points():
        bbox.expand(p)
        print p
    print bbox
