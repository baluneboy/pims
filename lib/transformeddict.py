import collections


class TransformedDict(collections.MutableMapping):
    """A dictionary that applies an arbitrary key-altering
       function before accessing the keys"""

    def __init__(self, *args, **kwargs):
        self.store = dict()
        self.update(dict(*args, **kwargs))  # use the free update to set keys

    def __getitem__(self, key):
        return self.store[self.__keytransform__(key)]

    def __setitem__(self, key, value):
        self.store[self.__keytransform__(key)] = value

    def __delitem__(self, key):
        del self.store[self.__keytransform__(key)]

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)

    def __keytransform__(self, key):
        return key

class MyTransformedDict(TransformedDict):

    def __keytransform__(self, key):
        return key.lower()

if __name__ == "__main__":
    import pickle
    s = MyTransformedDict([('Test', 'test')])
    assert s.get('TEST') is s['test']   # free get
    assert 'TeSt' in s                  # free __contains__
                                        # free setdefault, __eq__, and so on
    assert pickle.loads(pickle.dumps(s)) == s
                                        # works too since we just use a normal dict
    print 'got here apparently without any errors'