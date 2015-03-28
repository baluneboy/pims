#!/usr/bin/env python

import os
import pygtk; pygtk.require('2.0')
import gtk
import re
from pims.patterns.dirnames import _HANDBOOKDIR_PATTERN
from pims.files.handbook import HandbookEntry

def alert(msg, title='ALERT'):
    label = gtk.Label(msg)
    dialog = gtk.Dialog(title,
                        None,
                        gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                        buttons=(gtk.STOCK_OK, 1, "Show Log", 2))
    dialog.vbox.pack_start(label)
    label.show()
    response = dialog.run()
    dialog.destroy()
    return response # 1 for "OK", 2 for "Show Log", otherwise -4 (for X)

def OLDalert(msg):
    """Show a dialog with a simple message."""
    dialog = gtk.MessageDialog()
    dialog.set_markup(msg)
    dialog.run()

def do_build(pth):
    """Create interim hb entry build products."""
    hbe = HandbookEntry( source_dir=pth )
    if not hbe.will_clobber():
        err_msg = hbe.process_pages()
        return err_msg or 'pre-processed %d hb pdf files' % len(hbe.pdf_files), hbe
    else:
        return 'ABORT PAGE PROCESSING: hb pdf filename conflict on yoda', hbe

def finalize(pth):
    """Finalize handbook page."""
    hbe = HandbookEntry(source_dir=pth)
    if not hbe.will_clobber():
        err_msg = hbe.process_build()
        return err_msg or 'did pdftk post-processing', hbe
    else:
        return 'ABORT BUILD: hb pdf filename conflict on yoda', hbe

def show_log(log_file):
    os.system('subl %s' % log_file)

def main(curdir):

    # Strip off uri prefix
    if curdir.startswith('file:///'):
        curdir = curdir[7:]

    # Verify curdir matches pattern (this works even in build subdir, which is a good thing)
    match = re.search( re.compile(_HANDBOOKDIR_PATTERN), curdir )

    # THIS IS WHERE WE DO BRANCHING BASED ON...
    # whether we are in the "build" subdir or the source_dir
    if match:
        #alert( match.string )
        if match.string.endswith('build'):
            #alert( 'we are in build directory, so finalize')
            msg, hbe = finalize( os.path.dirname(curdir) )
        else:
            #alert( 'we are in source_dir, so create build')
            msg, hbe = do_build(curdir)
    else:
        msg = 'ABORT: ignore non-hb dir'
        hbe = None

    response = alert( '%s' % msg ) # 1 for "OK", 2 for "Show Log", otherwise -4 (for eXited out)
    if match and response == 2 and hbe:
        hbe.log.process.info('  *** CLOSE SUBLIME TO FINALIZE GTK DIALOG ***')
        show_log(hbe.log.file)

if __name__ == "__main__":
    # Get nautilus current uri
    curdir = os.environ.get('NAUTILUS_SCRIPT_CURRENT_URI', os.curdir)
    main(curdir)
