#!/usr/bin/python

from PIL import Image
import urllib, cStringIO

def demo_read_url(URL):
    imfile = cStringIO.StringIO(urllib.urlopen(URL).read())
    img = Image.open(imfile)
    imfile_out = '/tmp/out.png'
    w, h = img.size
    img.crop((0, 0, w, h-160)).save( imfile_out, "PNG" )
    print 'wrote %s' % imfile_out
    
demo_read_url('http://pims.grc.nasa.gov/plots/sams/121f08/121f08.jpg')
raise SystemExit

def resize_and_crop(img_path, modified_path, size, crop_type='top'):
    """
    Resize and crop an image to fit the specified size.

    args:
        img_path: path for the image to resize.
        modified_path: path to store the modified image.
        size: `(width, height)` tuple.
        crop_type: can be 'top', 'middle' or 'bottom', depending on this
            value, the image will cropped getting the 'top/left', 'middle' or
            'bottom/right' of the image to fit the size.
    raises:
        Exception: if can not open the file in img_path of there is problems
            to save the image.
        ValueError: if an invalid `crop_type` is provided.
    """
    # If height is higher we resize vertically, if not we resize horizontally
    img = Image.open(img_path)
    # Get current and desired ratio for the images
    img_ratio = img.size[0] / float(img.size[1])
    ratio = size[0] / float(size[1])
    #The image is scaled/cropped vertically or horizontally depending on the ratio
    if ratio > img_ratio:
        img = img.resize((size[0], round(size[0] * img.size[1] / img.size[0])),
                Image.ANTIALIAS)
        # Crop in the top, middle or bottom
        if crop_type == 'top':
            box = (0, 0, img.size[0], size[1])
        elif crop_type == 'middle':
            box = (0, round((img.size[1] - size[1]) / 2), img.size[0],
                   round((img.size[1] + size[1]) / 2))
        elif crop_type == 'bottom':
            box = (0, img.size[1] - size[1], img.size[0], img.size[1])
        else :
            raise ValueError('ERROR: invalid value for crop_type')
        cropbox = tuple(int(i) for i in box)
        img = img.crop(cropbox)
    elif ratio < img_ratio:
        img = img.resize((round(size[1] * img.size[0] / img.size[1]), size[1]),
                Image.ANTIALIAS)
        # Crop in the top, middle or bottom
        if crop_type == 'top':
            box = (0, 0, size[0], img.size[1])
        elif crop_type == 'middle':
            box = (round((img.size[0] - size[0]) / 2), 0,
                   round((img.size[0] + size[0]) / 2), img.size[1])
        elif crop_type == 'bottom':
            box = (img.size[0] - size[0], 0, img.size[0], img.size[1])
        else :
            raise ValueError('ERROR: invalid value for crop_type')
        cropbox = tuple(int(i) for i in box)
        img = img.crop(cropbox)
    else :
        img = img.resize((size[0], size[1]),
                Image.ANTIALIAS)
        # If the scale is the same, we do not need to crop
    img.save(modified_path)

# use PIL to crop off Messages (in case of IP addresses or such)
def crop_acc_view_msgbox(imfile):
    """use PIL to crop off Messages (in case of IP addresses or such)"""
    im = Image.open(imfile)
    imfile_cropped = imfile.replace('.bmp', "_cropped.jpg")
    w, h = im.size
    im.crop((0, 0, w, h-160)).save( imfile_cropped, "JPEG" )
    return imfile_cropped

# create artistic thumbnail (upper left portion 256x256)
def create_crappy_thumbnail(imfile):
    """create artistic thumbnail (upper left portion 256x256)"""
    im = Image.open(imfile)
    imfile_thumb = imfile.replace('.jpg', "_thumb.jpg")
    w, h = im.size
    im.crop((0, 0, 256, 256)).save( imfile_thumb, "JPEG" )
    return imfile_thumb

if __name__ == "__main__":
    
    imfile = '/misc/yoda/www/plots/user/sams/screenshots/acc_view.bmp'
    
    imfile_cropped = crop_acc_view_msgbox(imfile)
    print 'wrote %s' % imfile_cropped
    
    imfile_thumb = create_crappy_thumbnail(imfile_cropped)
    print 'wrote %s' % imfile_thumb