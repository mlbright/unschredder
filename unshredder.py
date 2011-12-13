import sys
from PIL import Image
from fractions import gcd
from os.path import exists,isfile,normpath,basename,join
import numpy

def sequence(conn, start):
    seq = [start]
    while conn[seq[0]] not in seq:
        seq.insert(0, conn[seq[0]])
    return len(seq), seq

def unshred(path):
    image = numpy.asarray(Image.open(path).convert('L'))
    diff = numpy.diff([numpy.mean(column) for column in image.transpose()])

    threshold, width = 1, 0
    while width < 5 and threshold < 255:
        boundaries = [index+1 for index, d in enumerate(diff) if d > threshold]
        width = reduce(lambda x, y: gcd(x, y), boundaries) if boundaries else 0
        threshold += 1

    shreds = range(image.shape[1] / width)
    bounds = [(image[:,width*shred], image[:,width*(shred+1)-1]) for shred in shreds]
    D = [[numpy.linalg.norm(bounds[s2][1] - bounds[s1][0]) if s1 != s2 else numpy.Infinity for s2 in shreds] for s1 in shreds]
    neighbours = [numpy.argmin(D[shred]) for shred in shreds]
    walks = [sequence(neighbours, start) for start in shreds]
    new_order = max(walks)[1]

    source_im = Image.open(path)
    unshredded = Image.new("RGBA", source_im.size)
    for target, shred in enumerate(new_order):
        source = source_im.crop((shred*width, 0, (shred+1)*width, image.shape[1]))
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
