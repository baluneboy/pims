# TODO
# - decide where source code for Windows TReK will reside (on yoda)
#   '/misc/yoda/www/plots/user/sams/trekscripts'
# - keep Windows TReK source code in svn on jimmy via incrontab entry
# ------
# - capture multiple, relevant windows
# - embed link to these screenshots in the eetemp.html code
# - crop messages part of Accelerometer View to avoid showing sensitive info
# - get this as scheduled task on TReK (every minute)


from PIL import ImageGrab
import win32gui
from time import sleep
from sams_ctads_screenshots import crop_acc_view_msgbox, create_crappy_thumbnail

def grab_image(titlestart):
    toplist, winlist = [], []
    def enum_cb(hwnd, results):
        winlist.append((hwnd, win32gui.GetWindowText(hwnd)))
    win32gui.EnumWindows(enum_cb, toplist)

    # Just grab the hwnd for first window matching window title pattern
    my_win = [(hwnd, title) for hwnd, title in winlist if title.startswith(titlestart)]
    my_win = my_win[0]
    hwnd = my_win[0]

    # Get coords for original win loc
    x,y,w,h = win32gui.GetWindowRect(hwnd)

    # Move win to its original location
    # NOTE: this is kludge to bring win to front (SetFocus does not work)
    win32gui.MoveWindow(hwnd, x, y, w, h, True)    
    
    # FIXME: Robust try/except here with STALE annotation on previous screenshot via PIL

    # Grab image of win
    win32gui.SetForegroundWindow(hwnd)
    win32gui.BringWindowToTop(hwnd)
    bbox = win32gui.GetWindowRect(hwnd)
    img = ImageGrab.grab(bbox)
    
    # Save to yoda
    jpgfile = r'//yoda/pims/www/plots/user/sams/screenshots/' + titlestart.replace(' ','_') + '.jpg'
    img.save(jpgfile)
    print 'wrote %s' % jpgfile
    
    return jpgfile

if __name__ == "__main__":

    windows = ['Accelerometer View', 'GSE Packet Data', 'EE Housekeeping']
    for w in windows:
        jpgfile = grab_image(w)
        if w.startswith('Accelerometer View'):
            jpgfile = crop_acc_view_msgbox(jpgfile)
            print 'wrote %s' % jpgfile
        #imfile_thumb = create_crappy_thumbnail(jpgfile)
        #print 'wrote %s' % imfile_thumb    
        sleep(1)
