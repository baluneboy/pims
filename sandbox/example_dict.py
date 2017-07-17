#!/usr/bin/env python

########################################
# a dictionary:
# - is a mapping of a key to a value
# - is a lookup table (LUT)

########################################
# a dictionary key:
# - does not have to be a simple string
# - can be [any?] object

# create a mapping of full state name to (abbreviation, my_rank, quip)
states = {
#    KEY:            VALUE
    'Oregon':       ('OR', 3, 'bORing'),
    'Florida':      ('FL', 4, 'humid'),9
    'California':   ('CA', 2, 'fun'),
    'New York':     ('NY', 6, 'stinky'),
    'Michigan':     ('MI', 5, 'pseudo-Canadian'),
    'Ohio':         ('OH', 1, 'well-rounded')
}

# TODO discuss refactoring (do not get hung up on terms)
# TODO refactor the following line along with next 2 "print dividing lines"
# TODO mention that refactoring allows for easy code maintenance


print '-' * 80 # eighty


# iterate (loop) over items
for state, state_tuple in states.items():
    state_abbrev, my_rank, quip = state_tuple
    print "%s is the abbreviation for the state of %s, a %s state." % (state_abbrev, state, quip)


print '-' * 10 # ten


# TODO refactor to make guess a command line argument

# safely get a abbreviation by state that might not be there
guess = 'Ohio'
state = states.get(guess)
if not state:
    print "Sorry, no item for state of '%s'." % guess
else:
    print "NOT sorry, we do have an item for the %s state of %s." % (state[2], guess)
