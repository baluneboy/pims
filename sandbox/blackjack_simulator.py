import random
import multiprocessing
import math
import time

# configuration options
simulations = 1_000_000
num_decks = 4
shuffle_percent = 75


def simulate(queue, batch_size):
    deck = []

    def new_deck():
        std_deck = [
            # 2  3  4  5  6  7  8  9  10  J   Q   K   A
            2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11,
            2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11,
            2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11,
            2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11,
        ]

        # add more decks
        std_deck = std_deck * num_decks

        random.shuffle(std_deck)

        return std_deck[:]

    def play_hand():
        dealer_cards = []
        player_cards = []

        # deal initial cards, 2 cards each to the dealer and just one player
        for _ in range(2):
            dealer_cards.append(deck.pop(0))
            player_cards.append(deck.pop(0))

        # deal player until sum is 12 or higher
        while sum(player_cards) < 12:
            player_cards.append(deck.pop(0))

        # deal to dealer (special case on soft 17)
        while sum(dealer_cards) < 18:
            done = False
            # check for soft 17
            if sum(dealer_cards) == 17:
                done = True
                # check for an ace and convert to 1 if found
                for i, card in enumerate(dealer_cards):
                    if card == 11:
                        done = False
                        dealer_cards[i] = 1
            if done:
                break

            dealer_cards.append(deck.pop(0))

        p_sum = sum(player_cards)
        d_sum = sum(dealer_cards)

        # dealer bust
        if d_sum > 21:
            return 1
        # dealer tie
        if d_sum == p_sum:
            return 0
        # dealer win
        if d_sum > p_sum:
            return -1
        # dealer lose
        if d_sum < p_sum:
            return 1

    # starting deck
    deck = new_deck()

    # play hands
    win = 0
    draw = 0
    lose = 0
    for _ in range(0, batch_size):
        # reshuffle cards at shuffle percentage
        if (float(len(deck)) / (52 * num_decks)) * 100 < shuffle_percent:
            deck = new_deck()

        # play hand
        result = play_hand()

        # tally results
        if result == 1:
            win += 1
        if result == 0:
            draw += 1
        if result == -1:
            lose += 1

    # add everything to the final results
    queue.put([win, draw, lose])


def main():
    """run very many simulations via multiprocessing on what like 2 cpu cores"""
    start_time = time.time()

    # simulate
    cpus = multiprocessing.cpu_count()
    batch_size = int(math.ceil(simulations / float(cpus)))

    queue = multiprocessing.Queue()

    # create n processes
    processes = []
    for _ in range(0, cpus):
        process = multiprocessing.Process(target=simulate, args=(queue, batch_size))
        processes.append(process)
        process.start()

    # wait for everything to finish
    for proc in processes:
        proc.join()

    finish_time = time.time() - start_time

    # get totals
    win = 0
    draw = 0
    lose = 0

    for _ in range(0, cpus):
        results = queue.get()
        win += results[0]
        draw += results[1]
        lose += results[2]

    print()
    print('  cores used: %d' % cpus)
    print('  total simulations: {:,.0f}'.format(simulations))
    print('  simulations/s: {:,.0f}'.format(float(simulations) / finish_time))
    print('  execution time: %.2fs' % finish_time)
    print('  win  pct: {:>7.3%}'.format(win / float(simulations)))
    print('  draw pct: {:>7.3%}'.format(draw / float(simulations)))
    print('  lose pct: {:>7.3%}'.format(lose / float(simulations)))
    print()


if __name__ == '__main__':
    main()

    # Configuration
    # simulations = 1_000_000_000
    # num_decks = 4
    # shuffle_percent = 75
    #
    # EXAMPLE OUTPUT:
    # cores used: 2
    # total simulations: 1,000,000,000
    # simulations/s: 82,994
    # execution time: 12049.13s
    # win  pct: 45.596%
    # draw pct:  6.316%
    # lose pct: 48.088%
