#! /usr/env python

# The MIT License (MIT)

# Copyright (c) 2013 Erik Hemberg

# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:

# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import random
import math
import copy
import sys
import argparse
import csv
"""
PonyGP

Implementation of GP to describe how the algorithm works.

Creates a population by initializing two types of trees;
A "full" tree in which the tree is automatically expanded to its maximum depth
and a "grow" tree that randomly chooses symbols until it reaches a terminal or
maximum depth. After a tree is created, its fitness is evaluated and the best
performing tree or "solution" is kept and a new population is created.  After
this, the trees can undergo 2 types of changes.  The first is "subtree mutation"
 in which part or all of the tree is mutated or "regrown". The second is
"subtree crossover" in which all or part of two trees in the population swap
nodes with the same symbol. As long as this swap doesn't exceed the maximum
tree depth.  This process is then repeated 'x' number of times. The best
solution is then returned at the end of the search.

As of today:

Optimizing to minimize MSE
Defaults:
popsize = 4
explan vars: 2 x[1], x[0], 1 response var
training set: 2 points (random)
test set: 2 points (random)
trying to fit  arbitrary x1, x2  to random y's

Population is an instance of the class List 
the population contains individuals

Individual has fields
- genome
- fitness

Genome is object of class Tree

Tree has a root which is an object of class TreeNode

TreeNode has instance variables
- parent
- children (a list of TreeNodes)
- symbol

Author Erik Hemberg

"""


### Below are class definitions for the core objects used in ponyGP

class Tree(object):
    """A Tree has a root which is an object of class TreeNode"""

    def __init__(self, root):
        self.root = root
        self.node_cnt = 1
        self.depth = 1

    #TODO create add child?
    
    def grow(self, node, depth, max_depth, full=False):        
        """Recursively grow a node to max depth"""
        
        # Symbols are mathematical operators
        for _ in range(symbols.arities[node.symbol]):
            symbol = symbols.get_rnd_symbol(depth, max_depth, full)
            self.node_cnt += 1
            child = TreeNode(node, symbol, self.node_cnt)
            node.children.append(child)
            self.grow(child, depth + 1, max_depth)
        
    def calculate_depth(self):
        """Calculate the maximum depth of the tree."""
        node_depths = []
        all_nodes = self.depth_first(self.root)
        for node in all_nodes:
            node_depths.append(self.get_depth(node))
        self.depth = max(node_depths)
        return self.depth

    def depth_first(self, root):
        """Return a list of nodes collected by depth-first pre-order
        left-to-right traversal."""

        #TODO this should be a generator using "yield root". 
        nodes = [root]
        for child in root.children:
            nodes += (self.depth_first(child))
        return nodes

    def get_depth(self, node):
        """Calculate the depth of a node."""

        depth = 0
        while node.parent:
            node = node.parent
            depth += 1
        return depth

    def __str__(self):
        s = 'node_cnt:%d depth:%d root:%s' % \
            (self.node_cnt, self.depth, str(self.root))
        return s

    
class TreeNode(object):
    """A node in a tree."""

    def __init__(self, parent=None, symbol=None, children=[]):
        self.parent = parent
        self.symbol = symbol
        self.children = []

    def __str__(self):
        """Return an s-expression for the node and its descendents."""

        if len(self.children):
            retval = "(" + self.symbol[:]
            for child in self.children:
                retval += " " + str(child)
            retval += ")"
            return retval
        else:
            return self.symbol

class Symbols(object):
    """Symbols are functions (internal nodes) or terminals (leaves)"""
    
    def __init__(self, arities, variable_prefix):
        """Arities: A dictionary mapping symbol name to arity (integer >=0)."""
        self.arities = arities
        self.terminals = []
        for key in self.arities.keys():
            if self.arities[key] == 0:
                self.terminals.append(key)
                
        self.functions = []
        for key in self.arities.keys():
            if self.arities[key] > 0:
                self.functions.append(key)
                
        self.variable_prefix = variable_prefix
        #TODO move to Symbolic Regression problem, not really a symbol issue?
        self.variable_map = {}
        cnt = 0
        for terminal in self.terminals:
            if terminal.startswith(variable_prefix):
                self.variable_map[terminal] = cnt
                cnt += 1
    ##Depth is current depth of tree, max depth is constant
    def get_rnd_symbol(self, depth, max_depth, full_tree=False):
        """Get a random symbol. The depth is the current depth of the tree
        detrimines if a terminal must be chosen. If full is specifed a function
        will be chosen until depth == max_depth(constant)."""
        if depth >= max_depth:
            symbol = random.choice(self.terminals)
        else:
            if not full_tree and get_random_boolean():
                # Faster to index and use random.random
                    symbol = random.choice(self.terminals)
            else:
                symbol = random.choice(self.functions)
                #Randomly choose terminal or function for node in a grow tree 

        return symbol


class Individual(object):
    """A GP Individual"""

    def __init__(self, genome):
        self.genome = genome
        self.fitness = DEFAULT_FITNESS
    ## Explain lt purpose in sort
    def __lt__(self, other):
        """__lt__ defines the default condition for sort() command."""
        return self.fitness < other.fitness

    def __str__(self):
        s = 'Individual: %f %s' % \
            (float(self.fitness), str(self.genome.root))
        return s


class Symbolic_Regression(object):
    """Evaluate fitnesses"""

    def __init__(self, fitness_cases, targets, variable_map):
        # Matrix with each row a case and each column a variable
        self.fitness_cases = fitness_cases
        # Each row is the response to the corresponding fitness cases
        self.targets = targets
        ## self.variables never referenced
        self.variables = None
        ## Maps terminals to their values
        self.variable_map = variable_map
        assert len(self.fitness_cases) == len(self.targets)

    ## Individual is a solution in the form of a tree
    def __call__(self, individual):
        """Evaluates and sets the fitness in an individual. An individual is a
        solution in the form of a tree Fitness is root mean square error(MSE).
        """
        fitness = 0.0
        for fitness_case, target in zip(self.fitness_cases, self.targets):
            predicted = self.evaluate(individual.genome.root, fitness_case)
            fitness += (predicted - target)**2
        ##Check root mean squared error
        individual.fitness = math.sqrt(fitness)/float(len(self.targets))

    ## fitness_case: the explanatory variables for one data point
    def evaluate(self, node, fitness_case):        
        """Evaluate a node recursively. Fitness_case are all of the
        explanatory varibles for one data point."""
        
        if node.symbol == "+":
            return self.evaluate(node.children[0], fitness_case) + self.evaluate(node.children[1],fitness_case)
        elif node.symbol == "-":
            return self.evaluate(node.children[0], fitness_case) - self.evaluate(node.children[1], fitness_case)
        elif node.symbol == "*":
            return self.evaluate(node.children[0], fitness_case) * self.evaluate(node.children[1], fitness_case)
        elif node.symbol == "/":
            numerator = self.evaluate(node.children[0])
            denominator = self.evaluate(node.children[1])
            if abs(denominator) < 0.00001:
                return numerator
            else:
                return numerator / denominator
        
        ## handle the terminal variables
        elif node.symbol.startswith(symbols.variable_prefix):
                return fitness_case[self.variable_map[node.symbol]]

        # the symbol is a terminal constant
        else:
            return float(node.symbol)


### Below are functions which are used for evolution
        
def get_random_boolean():
    """Returns a random boolean optimized for speed"""
    return bool(random.getrandbits(1))

def initialize_population():
    """Ramped half-half initialization. The individuals in the
    population are initialized using the grow or the full method for
    each depth value (ramped) up to max_depth."""
    
    individuals = []
    for i in range(POPULATION_SIZE):
        #Pick full or grow method
        full = get_random_boolean()
        #Ramp the depth
        max_depth = (i % MAX_DEPTH) + 1
        #Create root node
        symbol = symbols.get_rnd_symbol(1, max_depth)
        root = TreeNode(None, symbol, 0)
        tree = Tree(root)
        #Grow the tree
        if tree.depth < max_depth and symbol in symbols.functions:
            tree.grow(tree.root, 1, max_depth, full)
        individuals.append(Individual(tree))
        print('Initial tree %d: %s' %(i, str(tree.root)))
    population = individuals
    
    #Use population to find best of first generation
    for ind in population:
        fitness_function(ind)

    population.sort()
    best_ever = population[0]
    return population, best_ever
    

def search_loop():
    """The evolutionary search loop."""
    #Create an initial population
    population, best_ever = initialize_population()

    #Generation loop
    generation = 0
    #TODO break out when best fitness equals max fitness
    while generation < GENERATIONS:
        #1) Create new population
        new_individuals = []
        #Select parents for creating children
        parents = tournament_selection(population)
        while len(new_individuals) < POPULATION_SIZE:
            #Crossover
            new_individuals.extend(
                subtree_crossover(*random.sample(parents, 2)))
        #Handle uneven populations size. Always 2 offspring 
        new_individuals = new_individuals[:POPULATION_SIZE]
        #Mutation
        new_individuals = list(map(subtree_mutation, new_individuals))

        #2) Evaluate fitness
        for ind in new_individuals:
            fitness_function(ind)

        #3) Select best individuals to keep in population
        population = generational_replacement(new_individuals, population)

        #4) Find best solution
        population.sort()
        best_ever = population[0]

        #Stats when the population has been replaced
        print_stats(generation, population)

        #Finally, increase the generation counter
        generation += 1        

    return best_ever

def print_stats(generation, population):
    """Print the statistics for the generation and individuals"""
    def ave(values):
        """Return the average of the values """
        return float(sum(values))/len(values)
    def std(values, ave):
        """Return the standard deviation of the values and average """
        return math.sqrt(float(
            sum((value-ave)**2 for value in values))/len(values))
    def get_ave_and_std(values):
        _ave = ave(values)
        _std = std(values, _ave)
        return _ave, _std
    fitness_vals = [i.fitness for i in population]
    size_vals = [i.genome.node_cnt for i in population]
    depth_vals = [i.genome.calculate_depth() for i in population]
    ave_fit, std_fit = get_ave_and_std(fitness_vals)
    ave_size, std_size = get_ave_and_std(size_vals)
    ave_depth, std_depth = get_ave_and_std(depth_vals)
    print("Gen:%d evals:%d fit_ave:%.2f+-%.3f size_ave:%.2f+-%.3f depth_ave:%.2f+-%.3f %s" %
          (generation, (POPULATION_SIZE * generation),
           ave_fit, std_fit,
           ave_size, std_size,
           ave_depth, std_depth,
           population[0]))

def tournament_selection(population, tournament_size=2):
    """Given a population, draw <tournament_size> competitors
    randomly and return the best."""

    winners = []
    while len(winners) < POPULATION_SIZE:
        competitors = random.sample(population, tournament_size)
        competitors.sort()
        winners.append(competitors[0])
        
    return winners

def generational_replacement(new_pop, population):
    """Return new a population. The ELITE_SIZE best individuals are
    appended to the new population if they are better than the worst
    individuals in new population"""

    new_pop += copy.deepcopy(population)
    new_pop.sort()
    return new_pop[:POPULATION_SIZE]

def subtree_mutation(individual):
    """Subtree mutation. Pick a node and grow it"""
    
    if random.random() < MUTATION_PROBABILITY:
        #Pick node
        node = random.choice(individual.genome.depth_first(individual.genome.root))
        #Clear children
        node.children[:] = []
        node_depth = individual.genome.get_depth(node)
        node.symbol = symbols.get_rnd_symbol(node_depth, MAX_DEPTH)
        #Grow tree
        if node.symbol in symbols.functions:
            individual.genome.grow(node, node_depth, MAX_DEPTH)

        node_cnt = len(individual.genome.depth_first(individual.genome.root))
        individual.genome.node_cnt = node_cnt
        individual.genome.calculate_depth()

    return individual

def subtree_crossover(parent1, parent2):
    """Subtree crossover. Two parents generate two offspring"""
    ##TODO Change to crossover at any inernal node
    #TODO have X tries for finding valid crossover points
    offsprings = (Individual(copy.deepcopy(parent1.genome)),
                Individual(copy.deepcopy(parent2.genome)))

    if random.random() < CROSSOVER_PROBABILITY:
        #Pick a crossover point
        offspring_0_node = random.choice(offsprings[0].genome.depth_first(offsprings[0].genome.root))
        #Only crossover internal nodes, not only leaves
        if offspring_0_node.symbol in symbols.functions:
            nodes = offsprings[1].genome.depth_first(offsprings[1].genome.root)            
            possible_nodes = []
            #Find possible crossover points
            for node in nodes:
                if node.symbol == offspring_0_node.symbol:
                    possible_nodes.append(node)
            #An equivalent symbol must exist in the other parent
            if possible_nodes:
                #Pick the second crossover point
                offspring_1_node = random.choice(possible_nodes)
                #Swap the children of the nodes
                node_children = (offspring_0_node.children, offspring_1_node.children)
                offspring_1_node.children = copy.deepcopy(node_children[0])
                offspring_0_node.children = copy.deepcopy(node_children[1])

    return offsprings
            
    
def main():
    """Create population. Search. Evaluate best solution on out-of-sample data"""
    
    #Evolutionary search
    best_ever = search_loop()
    print("Best train:" + str(best_ever))
    #Test on out-of-sample data
    out_of_sample_test(best_ever)

def out_of_sample_test(individual):
    """Out-of-sample test on an individual solution"""
    
    targets, fitness_cases = csv_fitness_and_target_reader('list_file_test.csv')
    fitness_function = Symbolic_Regression(fitness_cases, targets, symbols.variable_map)
    fitness_function(individual)
    print("Best test:" + str(individual))

def csv_fitness_and_target_reader(file_name):
    file_1 = open(file_name, 'r')
    fitness_case_list = []
    fitness_cases = []
    target_list = []
    initial_fitness_list = []
    reader = csv.reader(file_1)
    for line in reader:
        csv_list = []
        if not 'y' in line:             
            for part in line:
                csv_list.append(part)
            target = csv_list.pop(-1)
            target_list.append(target)
            fitness_case_list.append(csv_list)
            
    targets = map(float, target_list)
    for elem in fitness_case_list:
        fitness_cases.append(map(float, elem))
    return targets, fitness_cases
       

if __name__ == '__main__':
    ARITIES = {"x0": 0, "x1": 0, "0.1": 0, "1.0": 0, "5.0": 0,
               "*": 2, "+": 2, "-": 2}
    VARIABLE_PREFIX = 'x'
    DEFAULT_FITNESS = 10000
    
    #Adds optional arguments to command line
    parser = argparse.ArgumentParser()
    
    parser.add_argument("-cp", "--crossover_prob" , help="Define the probability\
                        the tree will choose to perform a crossover of nodes"\
                        , type=float)
    parser.add_argument("-mp", "--mutation_prob", help="Define the probability the \
                        tree will choose to perform a mutation of a node", \
                        type=float)
    parser.add_argument("-e", "--elite_size", help="Defines the number of 'best'\
                        individuals kept from previous generations", type=\
                        float)
    parser.add_argument("-g", "--generations", help="Determines the number of \
                        generations for which the search is run", type=float)
    parser.add_argument("-d", "--max_depth", help="Maximum depth a tree can \
                        grow to" , type=float)
    parser.add_argument("-p", "--pop_size", help="Determines the total population\
                        per generation", type=float)
    parser.add_argument("-s", "--seed", help="Determines the seed for random.seed",\
                        type=float)

    args = parser.parse_args()
    
    #Make arguments optional with a default
    if args.crossover_prob:
        CROSSOVER_PROBABILITY = args.crossover_prob
    else:
        CROSSOVER_PROBABILITY =  .9
        
    if args.mutation_prob:
        MUTATION_PROBABILITY = args.crossover_prob
    else:
        MUTATION_PROBABILITY = .5
        
    if args.elite_size:
        ELITE_SIZE =  args.elite_size
    else:
        ELITE_SIZE =  1
        
    if args.generations:
        GENERATIONS = args.generations
    else:
        GENERATIONS = 10
        
    if args.max_depth:
        MAX_DEPTH = args.max_depth
    else:
        MAX_DEPTH = 3
        
    if args.pop_size:
        POPULATION_SIZE = args.pop_size
    else:
        POPULATION_SIZE = 10
    if args.seed:
         SEED = args.seed
    else:
         SEED = None
        
    random.seed(SEED)

    check = []
    
    targets, fitness_cases = csv_fitness_and_target_reader('list_file_train.csv')
    
    #Checks for variable number mismatch and stops program if this is the case
    for sym in ARITIES.keys():
        if 'x' in sym:
            check.append(sym)
            
    if len(check)!=len(fitness_cases[0]):
        print "Variable number mismatch: Change arity dictionary or fitness_cases to match"
        raise SystemExit
    
    #TODO function showing how to compile the code and then run
    #instead of interpreter
    symbols = Symbols(ARITIES, VARIABLE_PREFIX)
    fitness_function = Symbolic_Regression(fitness_cases, targets, symbols.variable_map)
    main()
