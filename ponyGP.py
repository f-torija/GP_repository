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

"""
PonyGP

Implementation of GP to describe how the algorithm works. 

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

class Tree(object):
    """A Tree has a root which is an object of class TreeNode"""

    def __init__(self, root):
        self.root = root
        self.node_cnt = 1
        self.depth = 1

    #TODO create add child?
    
    def grow(self, node, depth, max_depth, full=False):        
        """Recursively grow a node to max depth"""
        
        for _ in range(symbols.arities[node.symbol]):
            symbol = symbols.get_rnd_symbol(depth, max_depth, full)
            self.node_cnt += 1
            child = TreeNode(node, symbol, self.node_cnt)
            node.children.append(child)
            self.grow(child, depth + 1, max_depth)
        
    def calculate_depth(self):
        """Calculate the maximum depth of the tree."""
        
        all_nodes = self.depth_first(self.root)
        node_depths = [self.get_depth(node) for node in all_nodes]
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
            (self.node_cnt, self.depth, self.root.str_as_tree())
        return s

    
class TreeNode(object):
    """A node in a tree."""

    def __init__(self, parent=None, symbol=None, children=[]):
        self.parent = parent
        self.symbol = symbol
        self.children = []

    def str_as_tree(self):
        """Return an s-expression for the node and its descendents."""

        if len(self.children):
            retval = "(" + self.symbol[:]
            for child in self.children:
                retval += " " + child.str_as_tree()
            retval += ")"
            return retval
        else:
            return self.symbol

    def __repr__(self):
        """Return a detailed string representation of the node
        itself."""

        if self.parent is None:
            parent = "None"
        else:
            parent = self.parent.symbol
        return "p:%s symbol:%s" % (parent, self.symbol)
                

class Symbols(object):
    """Symbols are functions (internal nodes) or terminals (leaves)"""
    
    def __init__(self, arities, variable_prefix):
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
    
    def get_rnd_symbol(self, depth, max_depth, full=False):
        """Get a random symbol. The depth detrimines if a terminal
        must be chosen. If full is specifed a function will be chosen
        until max_depth."""
        
        if depth >= max_depth:
            symbol = random.choice(self.terminals)
        else:
            if not full and bool(random.getrandbits(1)):
                symbol = random.choice(self.terminals)
            else:
                symbol = random.choice(self.functions)

        return symbol


class Individual(object):
    """A GP Individual"""

    def __init__(self, genome):
        self.genome = genome
        self.fitness = DEFAULT_FITNESS

    def __lt__(self, other):
        return self.fitness < other.fitness

    def __str__(self):
        s = 'Individual: %f %s' % \
            (float(self.fitness), self.genome.root.str_as_tree())
        return s


class Symbolic_Regression(object):
    """Evaluate fitnesses"""

    def __init__(self, fitness_cases, targets, variable_map):
        #Matrix with each row a case and each column a variable
        self.fitness_cases = fitness_cases
        #Each row is the response to the corresponding fitness cases
        self.targets = targets
        self.variable_map = variable_map
        assert len(self.fitness_cases) == len(self.targets)

    def __call__(self, individual):
        """Evaluates and sets the fitness in an individual. Fitness is
        mean square error(MSE)."""
        
        fitness = 0.0
        for case, target in zip(self.fitness_cases, self.targets):
            self.variables = case
            error = self.evaluate(individual.genome.root)
            fitness += math.sqrt(abs(error - target))

        individual.fitness = fitness/float(len(self.targets))

    def evaluate(self, node):        
        """Evaluate a node recursively"""
        
        #Identify the node symbol
        if node.symbol == "+":
            return self.evaluate(node.children[0]) + self.evaluate(node.children[1])
        elif node.symbol == "-":
            return self.evaluate(node.children[0]) - self.evaluate(node.children[1])
        elif node.symbol == "*":
            return self.evaluate(node.children[0]) * self.evaluate(node.children[1])
        elif node.symbol == "/":
            numerator = self.evaluate(node.children[0])
            denominator = self.evaluate(node.children[1])
            if abs(denominator) < 0.00001:
                return numerator
            else:
                return numerator / denominator
        elif node.symbol.startswith(symbols.variable_prefix):
            return self.variables[self.variable_map[node.symbol]]
        else:
            #The symbol is a terminal
            return float(node.symbol)


def initialize_population():
    """Ramped half-half initialization. The individuals in the
    population are initialized using the grow or the full method for
    each depth value (ramped) up to max_depth."""
    
    individuals = []
    for i in range(POPULATION_SIZE):
        #Pick full or grow method
        full = bool(random.getrandbits(1))
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
        print('Initial tree %d: %s' %(i, tree.root.str_as_tree()))

    return individuals

def search_loop(new_individuals):
    """The evolutionary search loop."""

    #Initalise first generation
    individuals = []
    best_ever = None
    #Generation loop
    generation = 0
    #TODO break out when best fitness equals max fitness
    while generation < GENERATIONS:
        #Evaluate fitness
        evaluate_fitness(new_individuals, fitness_function)
        #Find best solution
        new_individuals.sort()
        best_ever = new_individuals[0]
        #Replace population
        individuals = generational_replacement(new_individuals,
                                               individuals)
        #Stats when the population has been replaced
        print_stats(generation, individuals)
        #Increase the generation counter
        generation += 1        
        #Selection
        parents = tournament_selection(individuals)
        #Create new population
        new_individuals = []
        while len(new_individuals) < POPULATION_SIZE:
            #Crossover
            new_individuals.extend(
                subtree_crossover(*random.sample(parents, 2)))
        #Handle uneven populations size. Always 2 offspring 
        new_individuals = new_individuals[:POPULATION_SIZE]
        #Mutation
        new_individuals = list(map(subtree_mutation, new_individuals))

    return best_ever

def print_stats(generation, individuals):
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
            
    individuals.sort()
    fitness_vals = [i.fitness for i in individuals]
    size_vals = [i.genome.node_cnt for i in individuals]
    depth_vals = [i.genome.calculate_depth() for i in individuals]
    ave_fit, std_fit = get_ave_and_std(fitness_vals)
    ave_size, std_size = get_ave_and_std(size_vals)
    ave_depth, std_depth = get_ave_and_std(depth_vals)
    print("Gen:%d evals:%d fit_ave:%.2f+-%.3f size_ave:%.2f+-%.3f depth_ave:%.2f+-%.3f %s" %
          (generation, (POPULATION_SIZE * generation),
           ave_fit, std_fit,
           ave_size, std_size,
           ave_depth, std_depth,
           individuals[0]))

def tournament_selection(population, tournament_size=2):
    """Given a population, draw <tournament_size> competitors
    randomly and return the best."""

    winners = []
    while len(winners) < POPULATION_SIZE:
        competitors = random.sample(population, tournament_size)
        competitors.sort()
        winners.append(competitors[0])
        
    return winners

def generational_replacement(new_pop, individuals):
    """Return new a population. The ELITE_SIZE best individuals are
    appended to the new population if they are better than the worst
    individuals in new population"""

    individuals.sort()
    for ind in individuals[:ELITE_SIZE]:
        new_pop.append(copy.deepcopy(ind))
    new_pop.sort()

    return new_pop[:POPULATION_SIZE]

def evaluate_fitness(individuals, fitness_function):
    """Perform the mapping for each individual """
    for ind in individuals:
        fitness_function(ind)

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
    
    #Create population
    individuals = initialize_population()
    #Evolutionary search
    best_ever = search_loop(individuals)
    print("Best train:" + str(best_ever))
    #Test on out-of-sample data
    out_of_sample_test(best_ever)

def out_of_sample_test(individual):
    """Out-of-sample test on an individual solution"""
    
    fitness_cases = [
        [0, 1],
        [1, 1]
        ]
    targets = [1, 1]
    fitness_function = Symbolic_Regression(fitness_cases, targets, symbols.variable_map)
    fitness_function(individual)
    print("Best test:" + str(individual))

if __name__ == '__main__':
    #TODO too many global variables
    ARITIES = {"x0": 0, "x1": 0, "0.1": 0, "1.0": 0, "5.0": 0,
               "*": 2, "+": 2, "-": 2}
    VARIABLE_PREFIX = 'x'
    POPULATION_SIZE = 10
    MAX_DEPTH = 3
    DEFAULT_FITNESS = 10000
    GENERATIONS = 10
    ELITE_SIZE = 1
    #WARNING SEED is hardcoded. Change the SEED for different search
    SEED = 4
    CROSSOVER_PROBABILITY = 0.9
    MUTATION_PROBABILITY = 0.5
    #TODO command line arguments
    
    random.seed(SEED)
    
    #TODO function showing how to compile the code and then run
    #instead of interpreter
    
    #TODO have a function generating the fitness cases
    
    #TODO currently this function has very few fitness cases and
    #serves most for illustrative purposes
    symbols = Symbols(ARITIES, VARIABLE_PREFIX)
    fitness_cases = [
        [0, 1],
        [1, 0]
        ]
    targets = [0, 2]
    fitness_function = Symbolic_Regression(fitness_cases,
                                           targets,
                                           symbols.variable_map)
    main()