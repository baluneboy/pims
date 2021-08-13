from curses.ascii import isdigit
from nltk.corpus import cmudict
import inflect


d = cmudict.dict()
p = inflect.engine()


def num2words(x):
    """return string with words for numbers after replacing superfluous characters or words"""
    return p.number_to_words(x).replace(' and ', ' ').replace(', ', ' ').replace('-', ' ')


def nsyl(word):
    """return number of syllables in word"""
    return min([len(list(y for y in x if isdigit(y[-1]))) for x in d[word.lower()]])


# brute force find number with max syllables for counting numbers up to a million
themax = [-1, 0]
for x in range(999999 + 2):
    num_syl = sum([nsyl(w) for w in num2words(x).split(' ')])
    if num_syl > themax[1]:
        themax[0], themax[1] = x, num_syl
        print(themax)
