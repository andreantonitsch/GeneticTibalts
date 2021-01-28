import sys
import argparse
import random
import copy
import os
from multiprocessing.dummy import Pool as ThreadPool


def simulate(deck):
    active_tibalts = 4 #hand or deck
    random.shuffle(deck)
    # Sets hand and initial deck
    def mulligan(deck):
        hand_size = 7
        undecided = True
        hand = []
        while undecided:
            deck += hand
            hand = [deck.pop() for i in range(hand_size)]
            
            if hand_size >4 and ('T' in hand and (('0' in hand) or('1' in hand) )):
                undecided = False
            elif 'T' in hand:
                undecided = False
            elif hand_size <= 1:
                undecided = False
            
            hand_size -= 1
        
        return hand
    

    # Returns true if tibalt casts hits a payoff
    def tibalt(hand, deck):
        nonlocal active_tibalts

        mill = random.randint(1,3)

        if len(deck) - mill <= 0:
            return False
        
        for i in range(mill):
            milled = deck.pop()
            if milled == 'T':
                active_tibalts -= 1
        
        exiled = []

        while len(deck) > 0:
            current = deck.pop()
            if current == 'L':
                exiled += [current]
                continue
            if current == 'P':
                deck += exiled
                return True
            if current == '0' or current == '1' or current == 'T':
                if current == 'T':
                    active_tibalts -= 1
                deck += exiled
                return False
                
        return False

    def go_off(hand, deck, lands):
        nonlocal active_tibalts
        if ('T' in hand) and ('0' in hand and lands >= 2):
            active_tibalts -= 1
            hand.remove('T')
            hand.remove('0')
            return tibalt(hand, deck)
        elif ('T' in hand) and ('1' in hand and lands >= 3):
            hand.remove('T')
            hand.remove('1')
            active_tibalts -= 1
            return tibalt(hand, deck)
        else:
            return False

    hand = mulligan(deck)
    lands = 0
    turn = 0

    success = False

    while len(deck) > 0 and active_tibalts > 0:

        #turn draw
        turn += 1
        if turn == 1:
            # goes second
            if random.randint(0,1) == 1:
                hand += [deck.pop()]
        else:    
            hand += [deck.pop()]

        if 'L' in hand:
            hand.remove('L')
            lands+=1

        if go_off(hand, deck, lands):
            success = True
            break

    return turn if success else 60




class Deck():
    def __init__(self):
        self.zero_enablers = 0
        self.one_enablers = 0
        self.tibalts = 0
        self.payoffs = 0
        self.lands = 0
        self.fitness = None
        self.success_fitness = None
        self.successes = None
        self.fast_success_fitness = None
        self.fast_successes = None

        self.iterations = 5000

    def __str__(self):
        if self.fitness is None:
            return f'0 {self.zero_enablers}, 1 {self.one_enablers}, T {self.tibalts}, P {self.payoffs}, L {self.lands}, Fit = None'
        elif self.successes != 0:
            return f'0 {self.zero_enablers}, 1 {self.one_enablers}, T {self.tibalts}, P {self.payoffs}, L {self.lands}, Fit = {self.fitness}, WFit = {self.success_fitness}, Win % {self.successes / self.iterations}, FWFit = {self.fast_success_fitness},Fast Win % {self.fast_successes / self.iterations}'
        else:
            return f'0 {self.zero_enablers}, 1 {self.one_enablers}, T {self.tibalts}, P {self.payoffs}, L {self.lands}, Fit = {self.fitness}, WFit = {0}, Win % {0}, FWFit = {0},Fast Win % {0}'
        
    def __repr__(self):
        if self.fitness is None:
            return f'0 {self.zero_enablers}, 1 {self.one_enablers}, T {self.tibalts}, P {self.payoffs}, L {self.lands}, Fit = None'
        elif self.successes != 0:
            return f'0 {self.zero_enablers}, 1 {self.one_enablers}, T {self.tibalts}, P {self.payoffs}, L {self.lands}, Fit = {self.fitness}, WFit = {self.success_fitness}, Win % {self.successes / self.iterations }, FWFit = {self.fast_success_fitness},Fast Win % {self.fast_successes / self.iterations}, '
        else:
            return f'0 {self.zero_enablers}, 1 {self.one_enablers}, T {self.tibalts}, P {self.payoffs}, L {self.lands}, Fit = {self.fitness}, WFit = {0}, Win % {0}, FWFit = {0},Fast Win % {0}'    

    def randomize(self):
        self.zero_enablers = random.randint(0, 8)
        self.one_enablers = random.randint(0, 10)
        self.tibalts = random.randint(0, 4)
        self.payoffs = random.randint(0, 30)
        self.lands = 60 - self.payoffs - self.tibalts - self.one_enablers - self.zero_enablers

    def cross_over(self, deck1, deck2):
        parents = [deck1, deck2]

        self.zero_enablers = parents[random.randint(0, 1)].zero_enablers
        self.one_enablers = parents[random.randint(0, 1)].one_enablers
        self.tibalts = parents[random.randint(0, 1)].tibalts
        self.payoffs = parents[random.randint(0, 1)].payoffs
        
        self.lands = 60 - self.payoffs - self.tibalts - self.one_enablers - self.zero_enablers


    def mutate(self):
        att = random.randint(0, 3)
        if att == 0:
            self.zero_enablers = random.randint(0, 8)
        if att == 1:
            self.one_enablers = random.randint(0, 15)
        if att == 2:
            self.tibalts = random.randint(0, 4)
        if att == 3:
            self.payoffs = random.randint(0, 30)
        self.lands = 60 - self.payoffs - self.tibalts - self.one_enablers - self.zero_enablers
        self.fitness = None

    def get_decklist(self):
        d = []
        d += ['0' for i in range(self.zero_enablers)]
        d += ['1' for i in range(self.one_enablers)]
        d += ['T' for i in range(self.tibalts)]
        d += ['P' for i in range(self.payoffs)]
        d += ['L' for i in range(self.lands)]
        return d


    def calculate_fitness(self, iterations, specie_count = 0):
        turns = 0
        successes = 0
        success_turns = 0
        fast_successes = 0
        fast_success_turns = 0
        decklist = self.get_decklist()
        self.iterations = iterations

        for i in range(iterations):
            sim_end = simulate(copy.copy(decklist))
            turns += sim_end

            if sim_end != 60:
                success_turns += sim_end
                successes += 1
                if sim_end < 5:
                    fast_success_turns += sim_end
                    fast_successes += 1

            # if i % 10  == 0:
            #     print(f'Specimen {specie_count} Fitness Iteration {i}', end = '\r')

        self.successes = successes
        self.success_fitness = success_turns / successes if successes != 0 else 0
        self.fitness = turns / iterations
        self.fast_success_fitness = fast_success_turns / fast_successes if fast_successes != 0 else 0
        self.fast_successes = fast_successes


def print_pool(pool, generation):
    os.system('cls')
    print(f'GENERATION {generation}\n')
    print(f'{pool[0]}\n{pool[1]}\n{pool[2]}\n{pool[3]}\n{pool[4]}\n')



arg_parser = argparse.ArgumentParser(description="Tibalt's Trickery Genetic Optimzer.")
arg_parser.add_argument('-fitness_iterations', '--si', metavar='SI', type=int, default = 10000, help='Monte Carlo iterations to define fitness.')
arg_parser.add_argument('-species_quantity', '--sq', metavar='SQ', type=int, default = 100, help='How many species in Pool.')
arg_parser.add_argument('-cull_ratio', '--cr', metavar='CR', type=int, default = 50, help='How many species to cull.')
arg_parser.add_argument('-species_kept', '--sk', metavar='SK', type=int, default = 5, help='How many species to keep.')
arg_parser.add_argument('-generations', '--e', metavar='E', type=int, default = 5, help='How many epochs to run.')
arg_parser.add_argument('-crossover_ratio', '--xr', metavar='X', type=int, default = 45, help='How many species to breed. The rest of the pool is filled with new specimens')


args = vars(arg_parser.parse_args())

FITNESS_ITERATIONS = args['si']
SPECIES_QUANTITY = args['sq']
CULL_RATIO = args['cr']
SPECIEST_KEPT = args['sk']
GENERATIONS = args['e']
XOVER_RATIO = args['xr']



def fit (deck):
    deck.calculate_fitness(FITNESS_ITERATIONS)
    return deck

if __name__ == '__main__':

    pool = []
    # initialize pool
    for i in range(SPECIES_QUANTITY-1):
        deck = Deck()
        deck.randomize()
        pool += [deck]
    
    obvious = Deck()
    obvious.tibalts = 1
    obvious.payoffs = 1
    obvious.zero_enablers = 1
    obvious.one_enablers = 0
    obvious.lands = 57

    pool += [obvious]

    #generations
    for generation in range(GENERATIONS):
        # calculate fitness
        count = 0

        threading_pool = ThreadPool(4)
        result = threading_pool.map(fit , pool)
        threading_pool.close()
        threading_pool.join()
        pool = result

        # for deck in pool:
        #     if deck.fitness is None:
        #         deck.calculate_fitness(FITNESS_ITERATIONS, count)
        #         count +=1
        
        pool = sorted(pool, key = lambda d : d.fast_successes, reverse=True)    
        print_pool(pool, generation)

        # cull worst specimens
        del pool[-CULL_RATIO:]

        # XOver new specimens
        for i in range(XOVER_RATIO):
            deck = Deck()
            deck.cross_over(*random.choices(pool, k=2))
            pool += [deck]

        # mutate old species
        for deck in pool[SPECIEST_KEPT:SPECIEST_KEPT+XOVER_RATIO]:
            deck.mutate()

        # complete with new random elements
        while len(pool) < SPECIES_QUANTITY:
            deck = Deck()
            deck.randomize()
            pool += [deck]



        