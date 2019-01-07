from __future__ import print_function
from __future__ import division


import operator
import functools
'''

This module defines utility functions and classes for sokoban

The main class is the Wareshouse class.
An instance of this class can read a text file coding a Sokoban puzzle,
and  store information about the positions of the walls, boxes and targets 
list. See the header comment of the Warehouse class for details


Last modified 2017-03-18
by f.maire@qut.edu.au

'''


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#                           UTILS
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def find_1D_iterator(line, char):
    '''
    Return a generator that yield the positions (offset indices)
       where the character 'char' appears in the  'line' string.
    line : a string where we might find occurences of the 'char' character.
    char : a character that we are looking for.
    '''
    pos = 0
    # To see the doc of the string method 'find',  type  help(''.find)
    pos = line.find(char, pos)
    while pos != -1:
        yield pos
        pos = line.find(char, pos+1)


def find_2D_iterator(lines, char):
    '''
    Return a generator that  yields the (x,y) positions of
       the occurences of the character 'char' in the list of string 'lines'.
       A tuple (x,y) is returned, where
          x is the horizontal coord (column offset),
          and  y is the vertical coord (row offset)
    lines : a list of strings.
    char : the character we are looking for.
    '''
    for y, line in enumerate(lines):
        for x in find_1D_iterator(line, char):
            yield (x,y)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class Warehouse:
    '''
    A Warehouse object represents the configuration of a warehouse, including
    the position of the walls, targets, boxes and the worker.
    Self.boxes, self.targets and self.walls  are lists of (x,y) coordinates
    self.worker is a tuple (x,y)
    '''
    def copy(self, worker = None, boxes = None):
        '''
        Make a copy of this warehouse. Possibly with new positions
        for the worker and the boxes.  Targets and Walls are copied (shallow copy)
        worker : a (x,y) tuple, position of the agent
        boxes : list of (x,y) pairs, positions of the boxes
        '''
        result = Warehouse()
        result.worker = worker or self.worker
        result.boxes = boxes or self.boxes
        result.targets = self.targets
        result.walls = self.walls
        return result

    def read_warehouse_file(self, filePath):
        '''
        Load the description of a warehouse stored in a text file
        '''
        with open(filePath, 'r') as f:
            # 'lines' is a list of strings (rows of the puzzle) 
            lines = f.readlines() 
        self.extract_locations(lines)
    
    def write_warehouse_file(self, filePath):
        with open(filePath, 'w') as f:
            f.write(self.visualize())

    def extract_locations(self, lines):
        '''
        Extract positional information from the the list of string 'lines'.
        The list of string 'lines' represents the puzzle.
        This function sets the fields
          self.worker, self.boxes, self.targets and self.walls
        '''
        workers =  list(find_2D_iterator(lines, "@"))  # workers on a free cell
        workers_on_a_target = list(find_2D_iterator(lines, "!"))
        # Check that we have exactly one agent
        assert len(workers)+len(workers_on_a_target) == 1 
        if len(workers) == 1:
            self.worker = workers[0]
        self.boxes = list(find_2D_iterator(lines, "$")) # crate/box
        self.targets = list(find_2D_iterator(lines, ".")) # empty target
        targets_with_boxes = list(find_2D_iterator(lines, "*")) # box on target
        self.boxes += targets_with_boxes
        self.targets += targets_with_boxes
        if len(workers_on_a_target) == 1:
            self.worker = workers_on_a_target[0]
            self.targets.append(self.worker) 
        self.walls = list(find_2D_iterator(lines, "#")) # set(find_2D_iterator(lines, "#"))
        assert len(self.boxes) == len(self.targets)

#    def visualize(self):
    def __str__(self):
        '''
        Return a string representation of the warehouse
        '''
        ##        x_size = 1+max(x for x,y in self.walls)
        ##        y_size = 1+max(y for x,y in self.walls)
        X,Y = zip(*self.walls) # pythonic version of the above
        x_size, y_size = 1+max(X), 1+max(Y)
        
        vis = [[" "] * x_size for y in range(y_size)]
        for (x,y) in self.walls:
            vis[y][x] = "#"
        for (x,y) in self.targets:
            vis[y][x] = "."
        # if worker is on a target display a "!", otherwise a "@"
        # exploit the fact that Targets has been already processed
        if vis[self.worker[1]][self.worker[0]] == ".": # Note y is worker[1], x is worker[0]
            vis[self.worker[1]][self.worker[0]] = "!"
        else:
            vis[self.worker[1]][self.worker[0]] = "@"
        # if a box is on a target display a "*"
        # exploit the fact that Targets has been already processed
        for (x,y) in self.boxes:
            if vis[y][x] == ".": # if on target
                vis[y][x] = "*"
            else:
                vis[y][x] = "$"
        return "\n".join(["".join(line) for line in vis])

    def __eq__(self, other):
        return self.worker == other.worker and \
               self.boxes == other.boxes

    def __hash__(self):
        return hash(self.worker) ^ functools.reduce(operator.xor, [hash(box) for box in self.boxes])
    
if __name__ == "__main__":
    wh = Warehouse()
    wh.read_warehouse_file("./warehouses/warehouse_03.txt")
#    field.write_warehouse_file("./F_01.txt")
    print(wh)   # this calls    wh.__str__()

