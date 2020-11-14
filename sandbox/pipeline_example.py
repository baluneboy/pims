#!/usr/bin/env python3

import sys


if __name__ == "__main__":

    # Initialize a names dictionary as empty to start with.
    names = {}

    # Each key in this dictionary will be a name and the value will be the number of times that name appears.
    # Also, sys.stdin is a file object, so you can apply all the same functions that can be applied to a file object.
    for name in sys.stdin.readlines():
            name = name.strip()  # each line will have a newline on the end that should be removed
            if name in names:
                    names[name] += 1
            else:
                    names[name] = 1

    # Iterating over the dictionary, print name followed by a space followed by the number of times it appeared.
    for name, count in names.items():
            sys.stdout.write("%d\t%s\n" % (count, name))
