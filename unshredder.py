import sys
from PIL import Image
from fractions import gcd
from os.path import exists,isfile,normpath,basename,join
import math

SHRED_WIDTH = 32

def dist(x, y):
    """euclidean distance between x and y"""
    if len(x) != len(y):
        raise ValueError, "vectors must be same length"
    sum_ = 0
    for i in range(len(x)):
        sum_ += (x[i]-y[i])**2
    return math.sqrt(sum_)

def unshred(path):
    image = Image.open(path).convert('L')
    im_width,im_height = image.size
    #print "w: %d, h: %d" % (im_width,im_height)
    pixels = list(image.getdata())
    rows = [ pixels[start:start+im_width] for start in range(0,len(pixels),im_width) ]
    cols = zip(*rows)
    
    """diff = numpy.diff([numpy.mean(column) for column in image.transpose()])"""

    """
    threshold, width = 1, 0
    while width < 5 and threshold < 255:
        boundaries = [index+1 for index, d in enumerate(diff) if d > threshold]
        width = reduce(lambda x, y: gcd(x, y), boundaries) if boundaries else 0
        threshold += 1
    """

    shreds = [ (cols[i*SHRED_WIDTH],cols[((i+1)*SHRED_WIDTH)-1],i) for i in range(im_width/SHRED_WIDTH) ]
    new_order = [shreds.pop()]
    while shreds:
        new_order.append(shreds.pop(min([ (dist(new_order[-1][1],s[0]),i) for i,s in enumerate(shreds) ])[1]))
        
    new_order = [shred[2] for shred in new_order]

    source_im = Image.open(path)
    unshredded = Image.new("RGBA", source_im.size)
    for target, shred in enumerate(new_order):
        source = source_im.crop((shred*SHRED_WIDTH,0,(shred+1)*SHRED_WIDTH, im_height))
        destination = (target*SHRED_WIDTH, 0)
        unshredded.paste(source, destination)
    unshredded.save(''.join(['reconstituted-',basename(path)]))

def run():
    try:
        filepath = sys.argv[1]
    except:
        print "Could not determine image to operate on"
        print "usage: %s <image path>" % (sys.argv[0])
        raise
    filepath.replace('/$','')
    if not exists(filepath):
        print "Path does not exist: %s" % (filepath)
        raise SystemExit
    if not isfile(filepath):
        print "Path is not a file: %s" % (filepath)
        raise SystemExit

    unshred(filepath)

if __name__ == "__main__":
    run()
