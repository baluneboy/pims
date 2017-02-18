#!/usr/bin/env python

###############################################################################
# NOTE: we assume a value of 1 is always included in list of available values #
###############################################################################

def coin_change(cents_needed, coin_values):
    min_coins = [[0 for j in range(cents_needed + 1)]
                for i in range(len(coin_values))]
    min_coins[0] = range(cents_needed + 1)

    for i in range(1,len(coin_values)):
        for j in range(0, cents_needed + 1):
            if j < coin_values[i]:
                min_coins[i][j] = min_coins[i-1][j]
            else:
                min_coins[i][j] = min(min_coins[i-1][j], 1 + min_coins[i][j-coin_values[i]])
    return min_coins[-1][-1]


def dp_make_change(coin_values, change, min_coins, coins_used):
    for cents in range(change+1):
        coin_count = cents
        new_coin = 1
        for j in [c for c in coin_values if c <= cents]:
            if min_coins[cents-j] + 1 < coin_count:
                coin_count = min_coins[cents-j]+1
                new_coin = j
        min_coins[cents] = coin_count
        coins_used[cents] = new_coin
    return min_coins[change]


def get_coins(coins_used, change):
    values = []
    coin = change
    while coin > 0:
        this_coin = coins_used[coin]
        values.append(this_coin)
        coin = coin - this_coin
    return values


def main(amt, clist):
    coins_used = [0]*(amt+1)
    coin_count = [0]*(amt+1)

    print "Making change for", amt, "requires these",
    print dp_make_change(clist, amt, coin_count, coins_used), "coins:",
    #print coin_change(amt, clist)
    values = get_coins(coins_used, amt)
    print values
    #print("The used list is as follows:")
    #print(coins_used)

clist = [1, 2, 2, 4]
for amt in range(22):
    main(amt, clist)


#print coin_change(12, [1, 2, 3, 8, 9, 10])
#print coin_change(12, [1, 2, 3, 10])
#print coin_change(12, [1, 2, 3, 9])
#print coin_change(12, [1, 2, 3, 4, 5])
