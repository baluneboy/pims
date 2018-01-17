#!/usr/bin/python


def constrain(n, low, high):
    """return value of n that has been constrained between low and high values"""
    return max(min(n, high), low)    


def p5remap(value, start1, stop1, start2, stop2, within_bounds=False):
    """return re-mapped float value from one range to another"""
    try:
        value = float(value)
        start1 = float(start1)
        stop1 = float(stop1)
        start2 = float(start2)
        stop2 = float(stop2)
    except ValueError:
        return None
    
    new_value = (value - start1) / (stop1 - start1) * (stop2 - start2) + start2
    
    if not within_bounds:
        return new_value
    else:
        if start2 < stop2:
            return constrain(new_value, start2, stop2)
        else:
            return constrain(new_value, stop2, start2)
    

def demo_p5map():
    value, start1, stop1, start2, stop2 = 12, 0, 36, 0, 100
    print p5remap(value, start1, stop1, start2, stop2)

    value, start1, stop1, start2, stop2 = 12, 0, 3, 0, 100
    print p5remap(value, start1, stop1, start2, stop2)
    print p5remap(value, start1, stop1, start2, stop2, within_bounds=True)


if __name__ == '__main__':
    demo_p5map()