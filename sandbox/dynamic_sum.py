#!/usr/bin/env python

def subset_sum(results, numbers, target, partial=[]):
    """careful with this recursive in-place results populating routine"""
    s = sum(partial)

    # check if the partial sum is equal to target
    if s == target:
        #print "sum(%s)=%s" % (partial, target)
        results.append(partial)
    if s >= target:
        return  # if we reach the number why bother to continue

    for i in range(len(numbers)):
        n = numbers[i]
        remaining = numbers[i+1:]
        subset_sum(results, remaining, target, partial + [n])

class SubsetSum(object):
    
    def __init__(self, candidates, target_sum):
        self.candidates = candidates
        self.target_sum = target_sum
        self.results = []
        self.populate_results()
        
    def populate_results(self):
        subset_sum(self.results, self.candidates, self.target_sum)

class RoundSubsetSum(SubsetSum):
    pass
    
if __name__ == "__main__":
    candidates, target_sum = [3, 9, 8, 4, 5, 7, 8], 15
    ss = SubsetSum(candidates, target_sum)
    print ss.results
