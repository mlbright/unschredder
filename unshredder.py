import sys
from PIL import Image
from fractions import gcd
from os.path import exists,isfile,normpath,basename,join
from math import sqrt

SHRED_WIDTH = 32

def norm(x):
    range_ = max(x) - min(x)
    min_ = min(x)
    return [ x[i] - min_ for i in range(len(x)) ]
        

def dist(x, y):
    """euclidean distance between x and y"""
    if len(x) != len(y):
        raise ValueError, "vectors must be same length"
    x_n = norm(x)
    y_n = norm(y)
    sum_ = 0
    for i in range(len(x)):
        sum_ += (x_n[i]-y_n[i])**2
    return sqrt(sum_)

def unshred(path):
    image = Image.open(path).convert('L')
    im_width,im_height = image.size
    #print "w: %d, h: %d" % (im_width,im_height)
    pixels = list(image.getdata())
    rows = [ pixels[row_start:row_start+im_width] for row_start in range(0,len(pixels),im_width) ]
    cols = zip(*rows)
    print "# of rows: %d, # of columns: %d" % (len(rows),len(cols))
    
    """diff = numpy.diff([numpy.mean(column) for column in image.transpose()])"""

    """
    threshold, width = 1, 0
    while width < 5 and threshold < 255:
        boundaries = [index+1 for index, d in enumerate(diff) if d > threshold]
        width = reduce(lambda x, y: gcd(x, y), boundaries) if boundaries else 0
        threshold += 1
    """

    shreds = [ (cols[i*SHRED_WIDTH],cols[((i+1)*SHRED_WIDTH)-1],i) for i in range(im_width/SHRED_WIDTH) ]
    ordered = [shreds.pop(0)]
    while shreds:
        ordered.append(shreds.pop(min([ (dist(ordered[-1][1],s[0]),i) for i,s in enumerate(shreds) ])[1]))
        
    seam = max([ (dist(ordered[i][1],ordered[i+1][0]),i+1) for i in range(0,len(ordered)-1) ])[1]
    ordered = ordered[seam:] + ordered[:seam]

    source_im = Image.open(path)
    unshredded = Image.new("RGBA", source_im.size)
    for target, shred in enumerate([shred[2] for shred in ordered]):
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
