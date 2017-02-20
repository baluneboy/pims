"""
A slightly-modified candlestick plotting function adapted
from mpl_finance.py code.  Intended for finance there, but
for EE HS plotting here.
"""

from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
#                        alpha=alpha, ochl=False)

def candlestick_yhltv(ax, quotes, width=0.4, colordown='blue', colorup='red', minvol=43200.0):

    """
    Plot the time, open, high, low, close as a vertical line ranging
    from low to high.  Use a rectangular bar to represent the
    open-close span.  If close >= open, use colorup to color the bar,
    otherwise use colordown

    Parameters
    ----------
    ax : `Axes`
        an Axes instance to plot to
    quotes : sequence of quote sequences
        data to plot.  time must be in float date format - see date2num
        (time, open, high, low, close, volume)
    width : float
        fraction of a day for the rectangle width
    colorup : color
        the color of the rectangle where close >= open
    colordown : color
         the color of the rectangle where close <  open      
    minvol : float
        minimum volume (typically half a day when quotes are once a second)
        if vol < minvol, then color changes to lightgray

    Returns
    -------
    ret : tuple
        returns (lines, patches) where lines is a list of lines
        added and patches is a list of the rectangle patches added

    """

    OFFSET = width / 2.0
    alpha = 1.0
    
    lines = []
    patches = []
    for q in quotes:
        t, open, high, low, close, vol = q[:6]

        if close >= open:
            color = colorup
            lower = open
            height = close - open
        else:
            color = colordown
            lower = close
            height = open - close
        
        if vol < minvol:
            color = 'lightgray'
            
        vline = Line2D(
            xdata=(t, t), ydata=(low, high),
            color=color,
            linewidth=0.5,
            antialiased=True,
        )

        rect = Rectangle(
            xy=(t - OFFSET, lower),
            width=width,
            height=height,
            facecolor=color,
            edgecolor=color,
        )
        rect.set_alpha(alpha)

        lines.append(vline)
        patches.append(rect)
        ax.add_line(vline)
        ax.add_patch(rect)
    ax.autoscale_view()

    return lines, patches

