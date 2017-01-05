#!/usr/bin/python

def cmp2lists(list1, list2):
    return list1 == list2

if __name__ == '__main__':
    list1 = ['one', 'two']
    list2 = ['two', 'one']
    list3 = ['one', 'two']
    print cmp2lists(list1, list2)
    print cmp2lists(list1, list3)
