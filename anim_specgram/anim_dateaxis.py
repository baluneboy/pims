import random
import time
from matplotlib import pyplot as plt
import matplotlib.dates as mdates
from matplotlib import animation
import datetime

# Plot parameters
fig, ax = plt.subplots()
line, = ax.plot([], [], 'k-', label='ABNA: Price')
legend = ax.legend(loc='upper right',frameon=False)
plt.setp(legend.get_texts(), color='grey')
ax.margins(0.05)
ax.grid(True, which='both', color='grey')

# Creating data variables
x = [datetime.datetime.now()]
y = [1]


def init():
    line.set_data(x[:1],y[:1])
    line.axes.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
    return line,


def animate(args):
    # Args are the incoming value that are animated
    animate.counter += 1
    i = animate.counter
    win = 60
    imin = max(0, i - win)
    x.append(args[0])
    y.append(args[1])

    xdata = x[imin:i]
    ydata = y[imin:i]

    line.set_data(xdata, ydata)
    line.set_color("red")

    plt.title('ABNA CALCULATIONS', color = 'grey')
    plt.ylabel("Price", color ='grey')
    plt.xlabel("Time", color = 'grey')

    ax.set_facecolor('black')
    ax.xaxis.label.set_color('grey')
    ax.tick_params(axis='x', colors='grey')
    ax.yaxis.label.set_color('grey')
    ax.tick_params(axis='y', colors='grey')

    ax.relim()
    ax.autoscale()

    return line,

animate.counter = 0

def frames1():
    # Generating time variable
    target_time = datetime.datetime.now()
    while True:
        # Add new time + 60 seconds
        target_time = target_time + datetime.timedelta(seconds=60)
        x = target_time
        y = random.randint(250,450)/10
        yield (x,y)
        time.sleep(random.randint(2, 4) / 10.0)

anim = animation.FuncAnimation(fig, animate,init_func=init,frames=frames1)

plt.show()