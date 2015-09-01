"""
"""

# inkslide.py $Id$
# Author: Terry Brown
# Created: Thu Oct 11 2007

import lxml.etree as ET

import copy
import subprocess
import os.path
from docutils.core import publish_string

import sys  # for debug
class inkSlide(object):
    def __init__(self):

        self.NS = { 'i': 'http://www.inkscape.org/namespaces/inkscape',
           's': 'http://www.w3.org/2000/svg',
           'xlink' : 'http://www.w3.org/1999/xlink'}

        # number of defined tablevels, FIXME, could derive from template?
        self.tabLevels = 4  

        self._nextId = 0

        self.gap = {
            'bIMAGE': 15,   # gap before image
            'aIMAGE': 15,   # gap after image
            'aTAB0': 10,    # gap after top level text
            'aTAB1': 10,    # gap after level 1 bullet
            'aTAB2': 10,    # gap after level 2 bullet
            'aTAB3': 10,    # gap after level 3 bullet
            'fVCENTER': 1,  # flag - center vertically
            'dHEIGHT': 728, # dimension, bottom of page
            'fHCENTER': 1,  # flag - center vertically
            'dWIDTH': 1024, # dimension, bottom of page
        }

        self.dimCache = {}
        self.is_reads, self.is_cache = 0, 0
    def __del__(self):
        print '%d reads, %d cache hits' % (self.is_reads, self.is_cache)
    def nextId(self):
        """return an unsed Id"""
        # FIXME, should inspect template doc.
        self._nextId += 1
        return 'is'+str(self._nextId)

    def clearId(self, x, what='id', NS={}):
        """recursively clear @id on element x and descendants"""
        if not NS: NS = self.NS
        if what in x.keys():
            del x.attrib[what]
        for i in x.xpath('.//*[@%s]'%what, NS):
            del i.attrib[what]
        return x
    def getDim(self, fn, Id, what):
        """return dimension of element in fn with @id Id, what is
        x, y, width, height
        """

        hsh = fn+Id+what
        if hsh in self.dimCache:
            self.is_cache += 1
            return self.dimCache[hsh]

        cmd = ('inkscape', '--without-gui', '--query-id', Id, '--query-'+what, fn)

        proc = subprocess.Popen(cmd, stdout = subprocess.PIPE,
                                stderr = subprocess.PIPE)
        # make new pipe for stderr to supress chatter from inkscape
        proc.wait()
        self.dimCache[hsh] = proc.stdout.read()
        if self.dimCache[hsh].strip() == '':
            print "Warning: '%s' not found" % Id
        self.is_reads += 1
        return self.dimCache[hsh]
    def textReader(self, text):
        """NOT USED iterate parts in input text"""
        if not text: return
        for line in text.split('\n'):
            if line.startswith('%slide '):
                yield {'type':'TITLE', 's':line[7:].strip()}
                continue
            if line.startswith('%pause'):
                yield {'type':'PAUSE'}
                continue
            if line.startswith('%id '):
                yield {'type':'ID', 's':line[4:].strip()}
                continue
            if not line.strip():
                yield {'type':'BLANK'}
                continue
            tabs = len(line) - len(line.lstrip('\t'))
            yield {'type':'TAB', 'tabs':tabs, 's':line.strip()}

    def textReaderRst(self, text):

        xml = publish_string(text.replace('\t','    '), writer_name = 'xml')
        doc = ET.fromstring(xml)
        # yield {'type':'TITLE', 's':doc.xpath('/document/@title')[0]}
        nodes = 'paragraph', 'comment', 'title', 'image'
        for i in doc.xpath('//%s' % '|//'.join(nodes)):

            if i.tag == 'title':
                yield {'type':'TITLE', 's':i.text}
            if i.tag == 'paragraph':
                tabs = len(i.xpath('ancestor::list_item'))
                yield {'type':'TAB', 'tabs':tabs, 's':i.text, 'e':i}
            if i.tag == 'image':
                tabs = len(i.xpath('ancestor::list_item'))
                yield {'type':'IMAGE', 'uri':i.get('uri')}
            if i.tag == 'comment':

                comparts = i.text.split(None, 1)

                if len(comparts) > 1:
                    ctag, cval = comparts
                elif len(comparts) == 1:
                    ctag = comparts[0]
                else:
                    continue  # empty comment had no meaning to InkView

                if ctag == 'is:id':
                    try:
                        yield {'type':'ID', 's':cval}
                    except:
                        raise Exception('"id" comment requires a value')
                elif ctag == 'is:notitle':
                    yield {'type':'DROP', 'what':('gr_title',)}
                elif ctag == 'is:notext':
                    yield {'type':'DROP', 'what':('gr_text',)}
                elif ctag == 'is:nobackground':
                    yield {'type':'DROP', 'what':('gr_bg',)}
                elif ctag == 'is:noforeground':
                    yield {'type':'DROP', 'what':('gr_fg',)}
                elif ctag == 'is:blank':
                    yield {'type':'DROP', 'what':('gr_title','gr_text')}
                elif ctag == 'is:empty':
                    yield {'type':'DROP', 'what':('gr_bg','gr_title','gr_text','gr_fg')}
                elif ctag == 'is:no':
                    try:
                        yield {'type':'DROP', 'what':(cval,)}
                    except:
                        raise Exception('"no" comment requires a value')

                if ctag == 'is:dim':
                    dim, val = cval.strip().split()
                    yield {'type':'DIM', 'dim':dim, 'val':val}
    def groupOrLayer(self, g):
        dst = self.doc.xpath('//s:g[@id="%s"]'%g, self.NS)
        if not dst: dst = self.doc.xpath('//s:g[@i:label="%s"]'%g, self.NS)
        if not dst: return dst  # let the caller test, don't raise exception here
        dst = dst[0]
        return dst
    def instanceFromTemplate(self, template, instance, text, pauseOk = True):

        slide = 0

        hlist = []
        self.doc = ET.parse(template)
        slideId = None

        for t in self.textReaderRst(text):

            if t['type'] == 'ID':
                slideId = t['s']
                continue

            if t['type'] == 'TITLE':
                if hlist:
                    self.process(instance, hlist, slideId, slide)
                    slide = slide + 1
                    hlist = [t]
                    self.doc = ET.parse(template)
                    slideId = None
                else:
                    hlist.append(t)

                print t['s']

                dst = self.groupOrLayer('gr_title')
                src = self.doc.xpath('//s:flowRoot[@id="fr_title"]', self.NS)[0]
                cpy = self.clearId(copy.deepcopy(src))
                Id = self.nextId()
                cpy.set('id', Id)
                hlist[-1]['id']=Id
                cpy.xpath('s:flowPara',self.NS)[0].text = t['s']
                dst.append(cpy)
                continue

            if t['type'] == 'PAUSE':
                if pauseOk:
                    self.process(instance, hlist, slideId, slide)
                    slide = slide + 1
                continue

            if t['type'] == 'BLANK':
                hlist.append(t)
                continue

            if t['type'] == 'TAB':
                hlist.append(t)
                dst = self.groupOrLayer('gr_text')
                src = self.doc.xpath('//s:flowRoot[@id="fr_tab%d"]' % t['tabs'], self.NS)[0]
                cpy = self.clearId(copy.deepcopy(src))
                Id = self.nextId()
                cpy.set('id', Id)
                hlist[-1]['id']=Id
                # cpy.xpath('s:flowPara',self.NS)[0].text = t['s']
                self.flowParaFromElement(
                    cpy.xpath('s:flowPara',self.NS)[0], t['e'])
                dst.append(cpy)
                continue

            if t['type'] == 'IMAGE':
                hlist.append(t)
                dst = self.groupOrLayer('gr_image')
                if not dst:
                    dst = self.groupOrLayer('gr_text')
                img = ET.Element('image')
                img.set('{%s}href'%self.NS['xlink'], t['uri'])
                Id = self.nextId()
                img.set('id', Id)
                hlist[-1]['id']=Id
                dst.append(img)
                continue

            hlist.append(t)  # whatever it was

        self.process(instance, hlist, slideId, slide)
    def flowParaFromElement(self, fp, e):
        fp.text = e.xpath('string(.)')
    def process(self, instance, hlist, slideId, slide):

        instanceName = instance.replace('%s', '%04d'%slide)

        instance = 'tmp.svg'  # reusing allows caching in getDim, but relies on nextId ensuring
                              # that the changing parts have new ids

        self.doc.write(file(instance, 'w'))

        drop = []

        bullDim = {}
        tabDim = {}
        for n in range(0,self.tabLevels):
            b = {}
            x = self.doc.xpath('//*[@id="bu_%d"]'%n, self.NS)
            if x:
                # self.clearId(x[0], what='transform')
                for i in 'x', 'y', 'width', 'height':
                    b[i] = float(self.getDim(instance, 'bu_%d'%n, i))
                bullDim[n] = b
            b = {}
            x = self.doc.xpath('//*[@id="fr_tab%d"]'%n, self.NS)
            if x:
                # clearId(x[0], what='transform')
                for i in 'x', 'y', 'width', 'height':
                    b[i] = float(self.getDim(instance, 'fr_tab%d'%n, i))
                x = x[0].xpath('.//s:rect',self.NS)[0]
                b['max-width'] = float(x.get('width'))
                b['max-height'] = float(x.get('height'))
                tabDim[n] = b

        delta = 0.
        firstVert = True
        placed_xy = []
        placed_transform = []

        for n, i in enumerate(hlist):

            this = hlist[n]
            prev = hlist[n-1]

            if this['type'] == 'DROP': drop += this['what']

            if this['type'] == 'DIM':
                if this['dim'] not in self.gap or this['val'][0] not in '+-':
                    self.gap[this['dim']] = float(this['val'])
                else:
                    self.gap[this['dim']] += float(this['val'])

            zeroHeight = ['TITLE', 'DROP', 'DIM']

            # don't do this - need to add height from prev to delta
            #if this['type'] in zeroHeight:
            #    continue  # already in right place, not a vertical element

            hgt = 0
            if prev['type'] == 'BLANK':
                hgt = 30
            elif prev['type'] not in zeroHeight:
                hgt = float(self.getDim(instance, prev['id'], 'height'))

                # risky gambit to space bullets properly when some lines
                # have no ascenders etc.
                if prev['type'] == 'TAB' and prev['tabs'] > 0:
                    lnh = tabDim[prev['tabs']]['height']
                    hgt = lnh * int(hgt/lnh+0.5)

            # TAB0, TAB1, TITLE, IMAGE, etc.
            # gap after previous
            hsh = 'a' + prev['type'] + str(prev.get('tabs',''))
            hgt += self.gap.get(hsh, 0)
            # gap before current
            hsh = 'b' + this['type'] + str(this.get('tabs',''))
            hgt += self.gap.get(hsh, 0)

            if firstVert:
                hgt = 0
                firstVert = False

            delta += hgt

            if this['type'] == 'BLANK': continue

            if this['type'] == 'TAB':
                tabs = this['tabs']

                r = self.doc.xpath('//s:flowRoot[@id="%s"]' % this['id'], self.NS)[0]
                self.clearId(r, what='transform')
                r = r.xpath('.//s:rect', self.NS)[0]
                r.set('x', str(tabDim[tabs]['x']))
                y = tabDim[tabs]['y'] + delta
                #print '%s -> %s' % (r.get('y'), y)
                #print tabDim[tabs]['y']
                r.set('y', str(y))
                placed_xy.append([r, this['id']])

            if (this['type'] == 'TAB' and this['tabs'] in bullDim
                and 'isDone' not in this):
                this['isDone'] = True
                dx = (tabDim[tabs]['x'] 
                      - bullDim[tabs]['x']
                      - 1.5*bullDim[tabs]['width']
                      )
                dy = (y 
                      + tabDim[tabs]['height'] / 2.
                      - bullDim[tabs]['y'] 
                      - bullDim[tabs]['height'] / 2.
                      )
                # dst = doc0.xpath('//s:g[@i:label="Texts"]', NS)[0]
                dst = self.groupOrLayer('gr_text')
                #print y, tabDim[tabs]['height'], bullDim[tabs]['y'], bullDim[tabs]['height'], dy
                clone = ET.Element('use')
                clone.set('transform', 'translate(%f,%f)' % (dx,dy))
                clone.set('{%s}href'%self.NS['xlink'], '#bu_%d'%tabs)
                placed_transform.append([clone, dx, dy])
                dst.append(clone)

            if this['type'] == 'IMAGE':

                xpath = '//s:image[@id="%s"]' % this['id']  # doesn't work?
                xpath = '//*[@id="%s"]' % this['id']
                i = self.doc.xpath(xpath, self.NS)[0]
                w = float(self.getDim(instance, this['id'], 'width'))
                x = tabDim[0]['x']+tabDim[0]['max-width']/2-w/2
                i.set('x', str(x))
                y = tabDim[0]['y'] + delta
                i.set('y', str(y))
                placed_xy.append([i,this['id']])

        if self.gap['fVCENTER']:

            if 'id' in this:
                delta += float(self.getDim(instance, this['id'], 'height'))

            recenter = (self.gap['dHEIGHT'] - delta - tabDim[0]['y']) * 0.45

            for i in placed_transform:
                i[0].set('transform', 'translate(%f,%f)'%(i[1],i[2]+recenter))
                i[2] += recenter  # so it's not lost below
            for i in placed_xy:
                i[0].set('y', str(float(i[0].get('y'))+recenter))

        if self.gap['fHCENTER']:

            maxX = 0
            for i in placed_xy:
                x = float(self.getDim(instance, i[1], 'x'))
                x += float(self.getDim(instance, i[1], 'width'))
                if x > maxX: maxX = x

            recenter = (self.gap['dWIDTH'] - maxX - tabDim[0]['x']) * 0.5

            for i in placed_transform:
                i[0].set('transform', 'translate(%f,%f)'%(i[1]+recenter,i[2]))
                i[1] += recenter  # in case it's used again
            for i in placed_xy:
                if i[0].tag != 'image':  # images already centered
                    # print i[0].tag
                    i[0].set('x', str(float(i[0].get('x'))+recenter))

        # look for instance specific parts
        if slideId:
            f = self.instancePath(slideId)
            if os.path.isfile(f):
                comp = ET.parse(f)
                svg = self.doc.xpath('//s:svg', self.NS)[0]
                g = "{%s}g"%self.NS['s']
                k = "{%s}label"%self.NS['i']
                for n, i in enumerate(svg.getchildren()):
                    if i.tag == g and i.get(k, '').startswith('Instance'):
                        x = comp.xpath('//s:svg//s:g[@i:label="%s"]'%i.get(k), self.NS)
                        if x:
                            x = x[0]
                            cpy = self.clearId(copy.deepcopy(x))
                            # cpy = self.textCopy(x)
                            svg[n] = cpy
                defs = comp.xpath('//s:svg/s:defs/*', self.NS)
                dst = self.doc.xpath('//s:svg/s:defs', self.NS)[0]
                for d in defs:
                    Id = d.get('id')
                    current = self.doc.xpath('//s:svg/s:defs/*[@id="%s"]'%Id, self.NS)
                    if not current:
                        cpy = copy.deepcopy(d)
                        dst.append(cpy)

        for i in drop:
            e = self.groupOrLayer(i)
            if e:
                e.xpath('..')[0].remove(e)

        # problem losing xlink ns?
        for i in self.doc.xpath('//*[@href]'):
            i.set('{%s}href'%self.NS['xlink'], i.get('href'))

        self.doc.write(file(instanceName, 'w'))

        return slideId
    def textCopy(self, ele):
        """copy the element ele via xml->text->xml, as deepcopy seems to lose text"""
        txt = ET.tostring(ele)
        # print txt
        return ET.fromstring(txt)
    def instancePath(self, slideId):
        """return path to component for slide"""
        # return os.path.join(slideId, component)
        return slideId+'.svg'
    def writeComponents(self, inkscapeFile, slideId):
        """write components from file for slide"""
        if not slideId: return
        doc0 = ET.parse(inkscapeFile)
        hasComponents = False
        for i in doc0.xpath('//s:svg//s:g', self.NS):
            k = "{%s}label"%self.NS['i']
            # print i.keys(),k
            if (k in i.keys() and i.get(k).startswith('Instance')):
                if len(i) > 0:
                    hasComponents = True
                    break
                    # ET.ElementTree(i).write(f)

        f = self.instancePath(slideId)

        if hasComponents:
            if (os.path.abspath(os.path.realpath(inkscapeFile)) != 
                os.path.abspath(os.path.realpath(f))):
                file(f, 'w').write(file(inkscapeFile).read())
        else:
            if os.path.isfile(f):
                os.remove(f)

if __name__ == '__main__':
    import sys
    x = inkSlide()
    x.instanceFromTemplate(sys.argv[1], 'slide%s.svg', file(sys.argv[2]).read())
