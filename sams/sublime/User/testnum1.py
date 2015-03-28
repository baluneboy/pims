import threading
import time
import sublime
import sublime_plugin

"""
The command just creates and runs a thread.
The thread will do all the work in the background.

Note that in your Thread constructor, you will need to pass in an 
instance of your Command class to work with in your thread.
"""
class ExampleCommand(sublime_plugin.TextCommand):

    def run(self, edit):

        exampleThread = ExampleThread(self, edit)
        exampleThread.start()

"""
Extend the Thread class and add your functionality in 
the run method below.

One thing to remember when moving your code over is 
you need to use self.cmd instead of self.
"""
class ExampleThread(threading.Thread):

    """
    Remember to pass in the parameters you need
    in this thread constructor.
    """
    def __init__(self, cmd, edit):
        threading.Thread.__init__(self)
        self.cmd = cmd
        self.edit = edit

    """
    Add your functionality here.

    If you need to access the main thread, you need to
    use sublime.set_timeout(self.callback, 1).

    In my example here, you can't call insert text into the editor
    unless you are in the main thread.

    Luckily that is fast operation.

    Basically, time.sleep(3) is a slow operation and will block, hence it
    is run in this separate thread.
    """
    def run(self):
        time.sleep(3)
        sublime.set_timeout(self.callback, 1)

    """
    This is the callback function that will be called to 
    insert HelloWorld. 

    You will probably need to use this to set your status message at 
    the end. I'm pretty sure that requires that you be on main thread 
    to work.
    """
    def callback(self):
        self.cmd.view.insert(self.edit, 0, "\n# Hello, World!")