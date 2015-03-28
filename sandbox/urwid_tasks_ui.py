#!/usr/bin/env python

################################################################################
## User Interface module                                                      ##
################################################################################

################################################################################
## Import necessary modules                                                   ##
################################################################################
import urwid
import subprocess
import os

################################################################################
## Class JobInterface                                                         ##
##                                                                            ##
## Implements a UI that takes a list of commands to execute in the shell and  ##
## wraps a pretty urwid based UI around it                                    ##
################################################################################
class JobInterface(object):
    ## different colours used. Most text will be 'informational', labels and
    ## headers are likely to be 'header', 'focus' is used for currently selected
    ## items in the listbox, while 'pb *' are used to colour the progress bar
    palette = [
               ('header',        'yellow,bold',     'dark blue' ),
               ('informational', 'white',           'dark blue' ),
               ('focus',         'white,bold',      'light cyan'),
               ('pb normal',     'yellow,bold',     'light blue' ),
               ('pb complete',   'black,bold',      'light cyan'),
              ]

    ##############################################################################
    ## __init__(title_text, tasklist_title, info_list, task_details, progress_bar)
    ##
    ## Class constructor, initialises the user interface. Variables are:
    ##   title_text:     Text to display in the title bar of the UI
    ##   tasklist_title: Text to display as the label for the list of tasks to
    ##                   perform
    ##   info_list:      A list of tuples (label, value) to display in the
    ##                   informational area of the UI
    ##   task_details:   A list of dictionaries. Each dictionary has two entries,
    ##                   'description' is a string containing descriptive text
    ##                   for a sub-task, and 'commands' which is a list of strings
    ##                   consisting of external commands to execute to complete
    ##                   the sub-task
    ##   progress_bar:   True if you want to include a progress bar in the
    ##                   informational area
    ##
    ## The code constructs the UI and sets some internal variables to allow us
    ## to directly refer to some widgets
    ##############################################################################
    def __init__(self, title_text, tasklist_title, info_list, task_details, progress_bar=False):

        ## Save list of tasks to be executed by the run_jobs() method
        self.task_details = task_details

        ## header: The title bar for the application
        self.header = urwid.AttrWrap(urwid.Text(title_text, 'center'), 'focus')

        ## progress: Progress bar, always present but conditionally displayed
        self.progress = urwid.ProgressBar('pb normal', 'pb complete')

        ## process job information prior to adding to UI
        ## how long should the label field be, at least 11 to cater to "Progress:"
        max_header_len = max(max(len(x[0]) for x in info_list) + 4, 11)

        ## split list of tuples into two columns
        tmp = [urwid.Columns(
                 [('fixed', max_header_len, urwid.Text(('header', '  ' + '\n  '.join(x[0] for x in info_list[::2])))),
                  urwid.Text('\n'.join(x[1] for x in info_list[::2])),
                  ('fixed', max_header_len, urwid.Text(('header', '  ' + '\n  '.join(x[0] for x in info_list[1::2])))),
                  urwid.Text('\n'.join(x[1] for x in info_list[1::2]))
                 ]
               )
              ]

        ## conditionally append progress bar information
        if progress_bar:
            tmp.append(urwid.Divider())
            tmp.append(urwid.Columns([('fixed', max_header_len, urwid.Text(('header', '  Progress:'))), self.progress]))

        ## information: Boxed area with information about jobs being executed
        self.information = urwid.AttrWrap(urwid.LineBox(urwid.Pile(tmp)),'informational')

        ## build_window: The terminal widget in which we will run the necessary commands
        self.build_window = urwid.Terminal(self.run_jobs)

        ## build_frame: The build environment, essentially build_window surrounded by a box
        ##              Separate variable so we can update the title
        self.build_frame = urwid.AttrWrap(urwid.LineBox(self.build_window, title = u'Work Window'),
                                          'informational'
                                         )

        ## task_listbox: The list of tasks to be completed, compiled from the provided task_details
        ##               Separate variable so we can update the selected item
        self.task_listbox = urwid.ListBox(
                              urwid.SimpleListWalker(
                                [urwid.AttrMap(urwid.Text(task['description']), 'informational') for task in task_details]
                              )
                            )

        ## body: Combine it all together to create the main body of the UI
        self.body = urwid.Pile(
                      [('flow', self.information),
                       urwid.Columns(
                         [('fixed',
                           30,
                           urwid.AttrWrap(
                             urwid.LineBox(urwid.WidgetDisable(self.task_listbox), title=tasklist_title),
                             'informational'
                           )
                          ),
                          self.build_frame
                         ]
                       )
                      ]
                    )

        ## mainframe: Everything including the title bar
        self.mainframe = urwid.Frame(self.body, self.header)

    ##############################################################################
    ## run_jobs()
    ##
    ## Callable function that is called in the terminal window of the UI. Executes
    ## all the jobs in the task_details parameter provided during class
    ## construction. For each task, send the task ID to the primary thread to
    ## update the UI, then execute each shell command in the individual task in
    ## turn
    ##############################################################################
    def run_jobs(self):
        f = os.fdopen(self.write_fd, "w", 0)

        for task in self.task_details:
            f.write(str(self.task_details.index(task)))
            for job in task['commands']:
                print "\033[1m" + job + "\033[0m"
                subprocess.call(job, shell=True)

        f.close()

    ##############################################################################
    ## set_title(widget, title)
    ##
    ## Callback for when the 'title' signal is sent from 'build_window'. Sets the
    ## primary title for the console
    ##############################################################################
    def set_title(self, widget, title):
        self.build_frame.set_title(title)

    ##############################################################################
    ## quit(*args, **kwargs)
    ##
    ## Callback for when the terminal window (build_window) has completed its
    ## tasks and has terminated. This terminates the urwid loop and thus the script
    ##############################################################################
    def quit(self, *args, **kwargs):
        raise urwid.ExitMainLoop()

    ##############################################################################
    ## handle_key(key)
    ##
    ## Callback for any unhandled key presses. If the Q key happens to make it
    ## through the mess of concurrent apps, then call the quit() callback which
    ## subsequently terminates the program. THIS IS NOT TRUSTWORTHY.
    ##############################################################################
    def handle_key(self, key):
        if key in ('q', 'Q'):
            quit()

    ##############################################################################
    ## update(data)
    ##
    ## Callback for any messages sent from the concurrent function running the jobs
    ## in the terminal window. The message is an integer (string format) that
    ## indexes the current task in task_details. We use the information to update
    ## the current item in the listbox, the title of the terminal sub-window, and
    ## (if present) the progress bar
    ##############################################################################
    def update(self, data):
        task_number = int(data)

        if task_number > 0: self.task_listbox.body[task_number - 1].set_attr_map({None:'informational'})
        self.task_listbox.body[task_number].set_attr_map({None:'focus'})
        self.build_frame.set_title(self.task_details[task_number]['description'])
        self.progress.set_completion(100.0 * task_number / len(self.task_details))

    ##############################################################################
    ## main()
    ##
    ## The main program loop, we connect the signal callback handlers, create the
    ## urwid loop, attach the watch pipe (to receive updates from the work process)
    ## attach the loop to the terminal build window and then execute until the
    ## jobs in the task list are complete
    ##############################################################################
    def main(self):
        urwid.connect_signal(self.build_window, 'title', self.set_title)
        urwid.connect_signal(self.build_window, 'closed', self.quit)

        self.loop = urwid.MainLoop(self.mainframe, self.palette, handle_mouse=False, unhandled_input=self.handle_key)

        self.write_fd = self.loop.watch_pipe(self.update)

        self.build_window.main_loop = self.loop
        self.loop.run()
