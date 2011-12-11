from PIL import Image
import ImageOps
image = Image.open("TokyoPanoramaShredded.png")
data = list(image.getdata())

width, height = image.size
NUMBER_OF_COLUMNS = 20

def get_pixel_value(x, y):
    pixel = data[y * width + x]
    return pixel

def compare_strips(column1,column2):
    dif = rdif = gdif = bdif = 0
    x1 = ((width/NUMBER_OF_COLUMNS)*column1)-1
    x2 = (width/NUMBER_OF_COLUMNS)*(column2-1)
    for y in range(0,height):
        data1 = get_pixel_value(x1,y)
        data2 = get_pixel_value(x2,y)
        rdif += abs(data1[0]-data2[0])
        gdif += abs(data1[1]-data2[1])
        bdif += abs(data1[2]-data2[2])
    return (rdif+gdif+bdif)/3

def compare_striptops(column1,column2):
    x1 = ((width/NUMBER_OF_COLUMNS)*column1)-1
    x2 = (width/NUMBER_OF_COLUMNS)*(column2-1)
    data1 = get_pixel_value(x1,0)
    data2 = get_pixel_value(x2,0)
    rdif = abs(data1[0]-data2[0])
    gdif = abs(data1[1]-data2[1])
    bdif = abs(data1[2]-data2[2])
    return (rdif+gdif+bdif)/3

# find adjacent strips
strips = []
for strip1 in range(1,NUMBER_OF_COLUMNS+1):
    strips.append((0,0,100000))
    for strip2 in range(1,NUMBER_OF_COLUMNS+1):
        if (strip1 != strip2):
            temp = strip1,strip2,compare_strips(strip1,strip2)
            if (temp[2] < strips[strip1-1][2]): 
                strips[strip1-1] = (temp[0],temp[1],temp[2])

# sort the strips
sortedstrips = []
for i in range(len(strips)):
    if (i==0):
        sortedstrips.append(strips[i])
        nextstrip = strips[i][1]
    else:
        sortedstrips.append(strips[nextstrip-1])
        nextstrip = strips[nextstrip-1][1]

# find first and last strips
seam = (1,0)
for i in range(len(sortedstrips)):
    temp = i+1,compare_striptops(sortedstrips[i][0],sortedstrips[i][1])
    print temp
    if (temp[1] > seam[1]):
        seam = temp
print seam
for i in range(0,seam[0]):
    temp = sortedstrips.pop(0)
    sortedstrips.append(temp)
print sortedstrips
       
# Create a new image of the same size as the original
# and copy a region into the new image
unshredded = Image.new("RGBA", image.size)
shred_width = unshredded.size[0]/NUMBER_OF_COLUMNS
for i in range(0,NUMBER_OF_COLUMNS):
    shred_number = sortedstrips[i][0]
    x1, y1 = (shred_width * shred_number)-shred_width, 0
    x2, y2 = x1 + shred_width, height
    source_region = image.crop((x1, y1, x2, y2))
    destination_point = (i * shred_width, 0)
    unshredded.paste(source_region, destination_point)
# Output the new image
unshredded.save("unshredded.jpg", "JPEG")

