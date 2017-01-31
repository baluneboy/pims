#!/usr/bin/env python

# Try to import PIL in either of the two ways it can end up installed.
try:
    from PIL import Image, ImageChops, ImageFilter
except ImportError:
    import Image, ImageChops, ImageFilter

def trim(im):
    bg = Image.new(im.mode, im.size, im.getpixel((0,0)))
    diff = ImageChops.difference(im, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    if bbox:
        return im.crop(bbox)

def crop_border_color():
    im = Image.open("/tmp/bord4.jpg")
    im = trim(im)
    im.show()
 
def analyze(image):
    ###Open the image with PIL
    img = Image.open(image)
 
    ###Grab the width, height, and build a list of each pixel in the image.
    width, height = img.size
    pixels = img.load()
    data = []
    for x in range(width):
        for y in range(height):
            cpixel = pixels[x, y]
            data.append(cpixel)
 
    ###Setup our R, G, and B variables for some math!
    r = 0
    g = 0
    b = 0
    avgCount = 0
 
    ###Run through every single pixel in the image, grab the r, g, and b value.
    ###Then test if the image has an alpha. If so, only average pixels with an
    ###alpha value of 200 or greater (out of 255).
    for x in range(len(data)):
        try:
            if data[x][3] > 200:
                r+=data[x][0]
                g+=data[x][1]
                b+=data[x][2]
        except:
            r+=data[x][0]
            g+=data[x][1]
            b+=data[x][2]
 
        avgCount+=1
 
    ###Get the averages, and return!
    rAvg = r/avgCount
    gAvg = g/avgCount
    bAvg = b/avgCount
 
    return (rAvg, gAvg, bAvg)

def print_stats(image):
    r, g, b = analyze(image)
    print r, g, b

def flavor_stack(data):

    #Python program to create 25 image flavour 
    x=0
    def images(data):
        #data=raw_input('Enter your Image name,Specify path:')
        global x
        x=0
        try:
            mg=Image.open(data)
        except:
            x=1
            return 0
        mg.save('a.bmp')
        r,g,b = mg.split()
        mg2=Image.merge('RGB',(r,b,g))
        mg2.save('/tmp/B.jpg')
        mg2=Image.merge('RGB',(g,r,b))
        mg2.save('/tmp/C.jpg')
        mg2=Image.merge('RGB',(g,b,r))
        mg2.save('/tmp/D.jpg')
        mg2=Image.merge('RGB',(b,r,g))
        mg2.save('/tmp/E.jpg')
        mg2=Image.merge('RGB',(b,g,r))
        mg2.save('/tmp/F.jpg')
        mg2=Image.merge('RGB',(r,g,r))
        mg2.save('/tmp/G.jpg')
        mg2=Image.merge('RGB',(r,r,g))
        mg2.save('/tmp/H.jpg')
        mg2=Image.merge('RGB',(r,g,g))
        mg2.save('/tmp/I.jpg')
        mg2=Image.merge('RGB',(g,r,g))
        mg2.save('/tmp/J.jpg')
        mg2=Image.merge('RGB',(g,g,r))
        mg2.save('/tmp/K.jpg')
        mg2=Image.merge('RGB',(g,r,r))
        mg2.save('/tmp/L.jpg')
        mg2=Image.merge('RGB',(r,b,r))
        mg2.save('/tmp/M.jpg')
        mg2=Image.merge('RGB',(r,r,b))
        mg2.save('/tmp/N.jpg')
        mg2=Image.merge('RGB',(r,b,b))
        mg2.save('/tmp/O.jpg')
        mg2=Image.merge('RGB',(g,b,g))
        mg2.save('/tmp/P.jpg')
        mg2=Image.merge('RGB',(g,g,b))
        mg2.save('/tmp/Q.jpg')
        mg2=Image.merge('RGB',(g,b,b))
        mg2.save('/tmp/R.jpg')
        mg2=Image.merge('RGB',(b,r,r))
        mg2.save('/tmp/S.jpg')
        mg2=Image.merge('RGB',(b,r,b))
        mg2.save('/tmp/T.jpg')
        mg2=Image.merge('RGB',(b,b,r))
        mg2.save('/tmp/U.jpg')
        mg2=Image.merge('RGB',(b,g,g))
        mg2.save('/tmp/V.jpg')
        mg2=Image.merge('RGB',(b,g,b))
        mg2.save('/tmp/W.jpg')
        mg2=Image.merge('RGB',(b,b,g))
        mg2.save('/tmp/X.jpg')
        mg2=Image.merge('RGB',(b,b,b))
        mg2.save('/tmp/Y.jpg')
        print "Process complete, Thanks....."
    images(data)

def dropShadow( image, offset=(5,5), background=0xffffff, shadow=0x444444, 
                border=8, iterations=3):
  """
  Add a gaussian blur drop shadow to an image.  
  
  image       - The image to overlay on top of the shadow.
  offset      - Offset of the shadow from the image as an (x,y) tuple.  Can be
                positive or negative.
  background  - Background colour behind the image.
  shadow      - Shadow colour (darkness).
  border      - Width of the border around the image.  This must be wide
                enough to account for the blurring of the shadow.
  iterations  - Number of times to apply the filter.  More iterations 
                produce a more blurred shadow, but increase processing time.
  """
  
  # Create the backdrop image -- a box in the background colour with a 
  # shadow on it.
  totalWidth = image.size[0] + abs(offset[0]) + 2*border
  totalHeight = image.size[1] + abs(offset[1]) + 2*border
  back = Image.new(image.mode, (totalWidth, totalHeight), background)
  
  # Place the shadow, taking into account the offset from the image
  shadowLeft = border + max(offset[0], 0)
  shadowTop = border + max(offset[1], 0)
  back.paste(shadow, [shadowLeft, shadowTop, shadowLeft + image.size[0], 
    shadowTop + image.size[1]] )
  
  # Apply the filter to blur the edges of the shadow.  Since a small kernel
  # is used, the filter must be applied repeatedly to get a decent blur.
  n = 0
  while n < iterations:
    back = back.filter(ImageFilter.BLUR)
    n += 1
    
  # Paste the input image onto the shadow backdrop  
  imageLeft = border - min(offset[0], 0)
  imageTop = border - min(offset[1], 0)
  back.paste(image, (imageLeft, imageTop))
  
  return back
  
def drop_shadow_twice(image):
  image = Image.open(image)
  image.thumbnail( (200,200), Image.ANTIALIAS)
  dropShadow(image).show()
  dropShadow(image, background=0xeeeeee, shadow=0x444444, offset=(0,5)).show()
   

if __name__ == '__main__':
    #crop_border_color()
    #print_stats('/tmp/bord4.jpg')
    flavor_stack('/tmp/bord4.jpg')
    #drop_shadow_twice('/tmp/bord4.jpg')