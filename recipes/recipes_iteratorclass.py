import datetime
from time import sleep

class CountIterator(object):
    """simple demo for iterator class"""
    def __init__(self, low, high):
        self.current = low
        self.high = high

    def __iter__(self):
        return self

    def next(self):
        if self.current > self.high:
            raise StopIteration
        else:
            self.current += 1
            return self.current - 1

def simpleCountDemo():
    for c in CountIterator(3, 8):
        print c

class DatabaseTimeIterator(object):
    """simple example for db iterator class"""    
    def __init__(self, displayHours=2.0, updateMinutes=2.0):
        self.dispTime = datetime.timedelta(hours=displayHours)
        self.updateTime = datetime.timedelta(minutes=updateMinutes)
        now =  datetime.datetime.now()
        print '%s <<< init time' % now
        self.startTime = datetime.datetime.now() - self.dispTime - self.updateTime
        self.endTime = self.startTime + self.updateTime

    def __iter__(self):
        return self

    def next(self):
        self.startTime = self.endTime
        self.endTime = self.startTime + self.updateTime
        while ( self.endTime > datetime.datetime.now() ):
            sleep(1)
        return self.startTime, self.endTime

def main():
    displayHours = 0.1
    updateMinutes = 2.0
    dbti = DatabaseTimeIterator(displayHours=displayHours, updateMinutes=updateMinutes)
    for startTime, endTime in dbti:
        print startTime
        print endTime
        print '================='
    print 'done'

if __name__ == '__main__':
    main()