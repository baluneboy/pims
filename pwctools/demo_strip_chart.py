# (c) MIT License Copyright 2014 Ronald H Longo
# Please reuse, modify or distribute freely.

import tkinter as tk
from collections import OrderedDict

CHART_HEIGHT_PX = 300
CHART_WIDTH_PX = 800


def translate(value, left_min, left_max, right_min, right_max):
    """return interpolated value, translating input value from "left" range to "right" range"""
    # calculate out how wide each range is
    left_span = left_max - left_min
    right_span = right_max - right_min

    # normalize the left range value into a 0-1 range (float)
    value_scaled = float(value - left_min) / float(left_span)

    # convert the normalized left value into a value in the right range
    return right_min + (value_scaled * right_span)


class StripChart(tk.Frame):

    def __init__(self, parent, scale, history_size, track_colors, *args, **opts):

        super().__init__(parent, *args, **opts)
        self._track_hist = OrderedDict()  # Map: TrackName -> list of canvas objID
        self._track_color = track_colors  # Map: Track Name -> color

        self._chart_height = scale + 1
        self._chart_width = history_size * 2  # Stretch for readability

        self._canvas = tk.Canvas(self, height=self._chart_height + 17, width=self._chart_width, background='black')
        self._canvas.grid(sticky=tk.N + tk.S + tk.E + tk.W)

        # Draw horizontal to divide plot from tick labels
        x, y = 0, self._chart_height + 2
        x2, y2 = self._chart_width, y
        self._baseLine = self._canvas.create_line(x, y, x2, y2, fill='white')

        # Init track def and histories lists
        self._track_color.update({'tick': 'white', 'tickline': 'white', 'ticklabel': 'white'})
        for trackName in self._track_color.keys():
            self._track_hist[trackName] = [None for _ in range(history_size)]

    def plot_values(self, **vals):
        for track_name, track_history in self._track_hist.items():
            # Scroll left-wards
            self._canvas.delete(track_history.pop(0))  # Remove left-most canvas objs
            self._canvas.move(track_name, -2, 0)  # Scroll canvas objs 2 pixels left

            # Plot the new values
            try:
                val = vals[track_name]
                x = self._chart_width
                y = self._chart_height - val
                color = self._track_color[track_name]
                obj_id = self._canvas.create_line(x, y, x + 1, y, fill=color, width=3, tags=track_name)
                track_history.append(obj_id)
            except (ValueError, Exception):
                track_history.append(None)

    def draw_tick(self, text=None, **line_opts):
        # draw vertical tick line
        x = self._chart_width
        y = 1
        x2 = x
        y2 = self._chart_height
        color = self._track_color['tickline']
        obj_id = self._canvas.create_line(x, y, x2, y2, fill=color, tags='tick', **line_opts)
        self._track_hist['tickline'].append(obj_id)

        # draw tick label
        if text is not None:
            x = self._chart_width
            y = self._chart_height + 10
            color = self._track_color['ticklabel']
            obj_id = self._canvas.create_text(x, y, text=text, fill=color, tags='tick')
            self._track_hist['ticklabel'].append(obj_id)

    def config_track_colors(self, **track_colors):
        # Change plotted data color
        for trackName, colorName in track_colors.items():
            self._canvas.itemconfigure(trackName, fill=colorName)

        # Change settings so future data has the new color
        self._track_color.update(track_colors)


class OssFuncSimStripChart(StripChart):

    def __init__(self, parent, scale, history_size, track_colors, *args, **opts):
        super().__init__(parent, scale, history_size, track_colors, *args, **opts)
        self._tick_count = 0

    def set_title(self, s):
        self.winfo_toplevel().title(s)

    @property
    def tick_count(self):
        """integer tick count value"""
        self.winfo_toplevel().title('tick_count=%d' % self._tick_count)
        return self._tick_count

    @staticmethod
    def fivevolt_translate(v):
        """return interpolated value translated for graphing 0-5V analog housekeeping range onto strip chart range"""
        return translate(v, 0, 5, 0+10, CHART_HEIGHT_PX-10)

    @staticmethod
    def tenvolt_translate(v):
        """return interpolated value translated for graphing -10V to +10V analog xyz value range to strip chart range"""
        return translate(v, -10, 10, 0+10, CHART_HEIGHT_PX-10)

    # def draw_text(self, text=None, **text_opts):
    #     color = 'white'
    #     if text is not None:
    #         x = self._chart_width
    #         y = self._chart_height + 100
    #         obj_id = self._canvas.create_text(x, y, text=text, fill=color, tags='text')
    #         self._track_hist['ticklabel'].append(obj_id)

    def plot_values(self, **vals):
        """translate values from analog voltage to chart range in pixels & call super's method with translated values"""
        new_vals = vals.copy()
        # FIXME this assumes keys are strictly h, x, y, z (no explicit checking of dict)
        for k in 'xyz':
            new_vals[k] = self.tenvolt_translate(vals[k])
        new_vals['h'] = self.fivevolt_translate(vals['h'])
        super().plot_values(**new_vals)
        self._tick_count += 1


class MyBetterClass(object):

    def __init__(self, h, x, y, z):
        self.h = h
        self.x = x
        self.y = y
        self.z = z
        self.top = None
        self.graph = None

    def get_next_value(self, current, lower_bound=-10.0, upper_bound=10.0):
        from random import choice
        deltas = list(range(-5, 6))  # randomly vary the values to be one of these
        delta = choice(deltas) / 10.0
        current += delta
        if current < lower_bound:
            return lower_bound
        elif current > upper_bound:
            return upper_bound
        else:
            return current

    def plot_next_values(self):

        if self.graph.tick_count % 50 == 0:
            self.graph.draw_tick(text=str(self.graph.tick_count), dash=(1, 4))
            # self.graph.draw_text(text='hello')

        self.h, self.x, self.y, self.z = 2.5, self.get_next_value(self.x), self.get_next_value(self.y), self.get_next_value(self.z)
        self.graph.plot_values(h=self.h, x=self.x, y=self.y, z=self.z)

        # change_color = {50: 'black',
        # 100: 'yellow',
        # 150: 'orange',
        # 200: 'white',
        # 250: 'brown',
        # 300: 'blue'}
        # if self.graph.tick_count in change_color:
        #     self.graph.config_track_colors(x=change_color[self.graph.tick_count])

        self.top.after(100, self.plot_next_values)

    def run_strip_chart(self):
        self.top = tk.Tk()
        self.graph = OssFuncSimStripChart(self.top, CHART_HEIGHT_PX, CHART_WIDTH_PX,
                                     {'h': 'gray', 'x': 'red', 'y': 'green', 'z': 'yellow'})
        self.graph.grid()
        self.top.after(100, self.plot_next_values)
        self.top.mainloop()


if __name__ == '__main__':
    mbc = MyBetterClass(2.5, 0.0, 0.0, 0.0)
    mbc.run_strip_chart()
