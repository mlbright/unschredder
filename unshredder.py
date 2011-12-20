import sys
from PIL import Image
from fractions import gcd
from os.path import exists,isfile,normpath,basename,join
import numpy

def unshred(path):
    image = numpy.asarray(Image.open(path).convert('L'))
    
    diff = numpy.diff([numpy.mean(column) for column in image.transpose()])
    threshold, width = 1, 0
    while width < 5 and threshold < 255:
        boundaries = [index+1 for index, d in enumerate(diff) if d > threshold]
        width = reduce(lambda x, y: gcd(x, y), boundaries) if boundaries else 0
        threshold += 1

    num_shreds = image.shape[1]/width
    shred_index = range(num_shreds)
    shreds = [ (image[:,i*width],image[:,(i+1)*width-1]) for i in shred_index ]
    orderings = []
    for first in shred_index:
        shred_ordering = [None] * num_shreds
        shred_ordering[0] = first
        for i in range(1,num_shreds):
            left = i - 1
            min_dist = numpy.Infinity
            index = 10
            for right in shred_index:
                if left == right:
                    continue
                if right in shred_ordering:
                    continue
                d = numpy.linalg.norm( shreds[right][0] - shreds[shred_ordering[left]][1] )
                if d < min_dist:
                    min_dist = d
                    index = right
            shred_ordering[i] = index
        orderings.append(shred_ordering)
        
    for o in orderings:
        print len(o), o

    source_im = Image.open(path)
    unshredded = Image.new("RGBA", source_im.size)
    for target, shred in enumerate(shred_ordering):
        source = source_im.crop((shred*width,0,(shred+1)*width, image.shape[1]))
        destination = (target*width, 0)
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
