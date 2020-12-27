import urwid

palette = [('header', 'white', 'black'),
    ('reveal focus', 'black', 'dark cyan', 'standout')]

menu = {"121f02, 200Hz": 'do 121f02, 200Hz',
        "121f03, 200Hz": 'do 121f03, 200Hz',
        "121f04, 200Hz": 'do 121f04, 200Hz'}

items = [urwid.Text(k) for k in menu.keys()]

content = urwid.SimpleListWalker([urwid.AttrMap(w, None, 'reveal focus') for w in items])

listbox = urwid.ListBox(content)

show_key = urwid.Text("Press any key", wrap='clip')
head = urwid.AttrMap(show_key, 'header')
top = urwid.Frame(listbox, head)


def show_all_input(input, raw):

    show_key.set_text("Pressed: " + " ".join([
        str(i) for i in input]))
    return input


def exit_on_cr(input):
    if input in ('q', 'Q'):
        raise SystemExit
    elif input == 'up':
        focus_widget, idx = listbox.get_focus()
        if idx > 0:
            idx = idx-1
            listbox.set_focus(idx)
    elif input == 'down':
        focus_widget, idx = listbox.get_focus()
        idx = idx+1
        if idx > len(items)-1:
            idx = 0
        listbox.set_focus(idx)
    elif input == 'enter':
        raise urwid.ExitMainLoop()


def out(s):
    show_key.set_text(str(s))


loop = urwid.MainLoop(top, palette, input_filter=show_all_input, unhandled_input=exit_on_cr)
loop.run()

print(menu[items[listbox.get_focus()[1]].get_text()[0]])
