#!/usr/bin/env python
#!/usr/bin/env python

# example text.py

import gtk

class TextExample:
    def text_toggle_editable(self, checkbutton,text):
        text.set_editable(checkbutton.active)

    def text_toggle_word_wrap(self, checkbutton, text):
        text.set_word_wrap(checkbutton.active)

    def close_application(self, widget):
        gtk.mainquit()

    def __init__(self):
        window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        window.set_usize(600, 500)
        window.set_policy(gtk.TRUE, gtk.TRUE, gtk.FALSE)
        window.connect("destroy", self.close_application)
        window.set_title("Text Widget Example")
        window.set_border_width(0)

        box1 = gtk.GtkVBox(gtk.FALSE, 0)
        window.add(box1)
        box1.show()

        box2 = gtk.GtkVBox(gtk.FALSE, 10)
        box2.set_border_width(10)
        box1.pack_start(box2, gtk.TRUE, gtk.TRUE, 0)
        box2.show()

        table = gtk.GtkTable(2, 2, gtk.FALSE)
        table.set_row_spacing(0, 2)
        table.set_col_spacing(0, 2)
        box2.pack_start(table, gtk.TRUE, gtk.TRUE, 0)
        table.show()

        # Create the GtkText widget
        text = gtk.GtkText()
        text.set_editable(gtk.TRUE)
        table.attach(text, 0, 1, 0, 1,
                    gtk.EXPAND | gtk.SHRINK | gtk.FILL,
                    gtk.EXPAND | gtk.SHRINK | gtk.FILL, 0, 0)
        text.show()

        # Add a vertical scrollbar to the GtkText widget
        vscrollbar = gtk.GtkVScrollbar(text.get_vadjustment())
        table.attach(vscrollbar, 1, 2, 0, 1,
                    gtk.FILL, gtk.EXPAND | gtk.SHRINK | gtk.FILL, 0, 0)
        vscrollbar.show()

        # Get the window's color map and allocate the color red
        cmap = window.get_colormap()
        color = cmap.alloc('red')

        # Load a fixed font
        fixed_font = gtk.load_font(
            "-misc-fixed-medium-r-*-*-*-140-*-*-*-*-iso8859-1")

        # Realizing a widget creates a window for it,
        # ready for us to insert some text
        text.realize()

        # Freeze the text widget, ready for multiple updates
        text.freeze()

        # Insert some colored text
        text.insert(None, text.get_style().black, None, "Supports ")
        text.insert(None, color, None, "colored ")
        text.insert(None, text.get_style().black, None, "text and different ")
        text.insert(fixed_font, text.get_style().black, None, "fonts\n\n")

        # Load the file text.py into the text window
        infile = open("/home/pims/log/handbook.log", "r")

        if infile:
            string = infile.read()
            infile.close()
            text.insert(fixed_font, None, None, string)

        # Thaw the text widget, allowing the updates to become visible
        text.thaw()

        hbox = gtk.GtkHButtonBox()
        box2.pack_start(hbox, gtk.FALSE, gtk.FALSE, 0)
        hbox.show()

        check = gtk.GtkCheckButton("Editable")
        hbox.pack_start(check, gtk.FALSE, gtk.FALSE, 0)
        check.connect("toggled", self.text_toggle_editable, text)
        check.set_active(gtk.TRUE)
        check.show()
        check = gtk.GtkCheckButton("Wrap Words")
        hbox.pack_start(check, gtk.FALSE, gtk.TRUE, 0)
        check.connect("toggled", self.text_toggle_word_wrap, text)
        check.set_active(gtk.FALSE)
        check.show()

        separator = gtk.GtkHSeparator()
        box1.pack_start(separator, gtk.FALSE, gtk.TRUE, 0)
        separator.show()

        box2 = gtk.GtkVBox(gtk.FALSE, 10)
        box2.set_border_width(10)
        box1.pack_start(box2, gtk.FALSE, gtk.TRUE, 0)
        box2.show()

        button = gtk.GtkButton("close")
        button.connect("clicked", self.close_application)
        box2.pack_start(button, gtk.TRUE, gtk.TRUE, 0)
        button.set_flags(gtk.CAN_DEFAULT)
        button.grab_default()
        button.show()
        window.show()

def main():
    gtk.mainloop()
    return 0

if __name__ == "__main__":
    TextExample()
    main()
