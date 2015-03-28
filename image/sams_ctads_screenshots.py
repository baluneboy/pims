#!/usr/bin/python

from PIL import Image

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