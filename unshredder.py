import sys
from PIL import Image
from fractions import gcd
from os.path import exists,isfile,normpath,basename,join
from math import sqrt

SHRED_WIDTH = 32

def normalize(x):
    max_ = max(x)
    min_ = min(x)
    range_ = max_ - min_
    #return (arr-amin)*255/rng
    return [ ((v - min_) * 255 / range_) for v in x ]

def dist(x, y):
    """euclidean distance between x and y"""
    #x = normalize(x)
    #y = normalize(y)
    return sqrt(sum([ (x[i]-y[i])**2 for i in range(len(x)) ]))

def sequence(successors, start):
    seq = [start]
    while successors[seq[0]] not in seq:
        seq.insert(0, successors[seq[0]])
    return len(seq), seq

def argmin(x):
    return min([ (v,i) for i,v in enumerate(x) ])[1]
    
def unshred(path):
    image = Image.open(path).convert('L')
    im_width,im_height = image.size
    pixels = list(image.getdata())
    rows = [ pixels[row_start:row_start+im_width] for row_start in range(0,len(pixels),im_width) ]
    cols = zip(*rows)
    
    """
    diff = numpy.diff([numpy.mean(column) for column in image.transpose()])
    threshold, width = 1, 0
    while width < 5 and threshold < 255:
        boundaries = [index+1 for index, d in enumerate(diff) if d > threshold]
        width = reduce(lambda x, y: gcd(x, y), boundaries) if boundaries else 0
        threshold += 1
    """

    shreds = range(im_width/SHRED_WIDTH)
    bounds = [ (i*SHRED_WIDTH,(i+1)*SHRED_WIDTH-1) for i in shreds ]

    D = [ [ dist(cols[bounds[s2][1]],cols[bounds[s1][0]]) if s1 != s2 else float(sys.maxint) for s2 in shreds ] for s1 in shreds ]
    successors = [ argmin(D[i]) for i in shreds ]
    walks = [ sequence(successors,start) for start in shreds ]
    new_order = max(walks)[1]

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
