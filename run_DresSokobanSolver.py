#!/usr/bin/python3

import search
import sokoban
import time
import os
import sys
from functools import partial
from threading import Thread

from puzzler import *

_orig_print = print
def print(*args, **kwargs):
    _orig_print(*args, flush=True, **kwargs)

def cls():os.system('clear')

def print_goal():
	print('''
_____/\\\\\\\\\\\\\\\\\\\\\\\\_______/\\\\\\\\\\__________/\\\\\\\\\\\\\\\\\\_____/\\\\\\_____________        
 ___/\\\\\\//////////______/\\\\\\///\\\\\\______/\\\\\\\\\\\\\\\\\\\\\\\\\\__\\/\\\\\\_____________       
  __/\\\\\\_______________/\\\\\\/__\\///\\\\\\___/\\\\\\/////////\\\\\\_\\/\\\\\\_____________      
   _\\/\\\\\\____/\\\\\\\\\\\\\\__/\\\\\\______\\//\\\\\\_\\/\\\\\\_______\\/\\\\\\_\\/\\\\\\_____________     
    _\\/\\\\\\___\\/////\\\\\\_\\/\\\\\\_______\\/\\\\\\_\\/\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\_\\/\\\\\\_____________    
     _\\/\\\\\\_______\\/\\\\\\_\\//\\\\\\______/\\\\\\__\\/\\\\\\/////////\\\\\\_\\/\\\\\\_____________   
      _\\/\\\\\\_______\\/\\\\\\__\\///\\\\\\__/\\\\\\____\\/\\\\\\_______\\/\\\\\\_\\/\\\\\\_____________  
       _\\//\\\\\\\\\\\\\\\\\\\\\\\\/_____\\///\\\\\\\\\\/_____\\/\\\\\\_______\\/\\\\\\_\\/\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\_ 
        __\\////////////_________\\/////_______\\///________\\///__\\///////////////__
''')

class Solver(Thread):
	def __init__(self,wh_file):
		super().__init__()
		self.warehouse = sokoban.Warehouse()
		self.warehouse.read_warehouse_file(
			'./warehouses/'+str(wh_file))
		self.puzzle = SokobanPuzzle(self.warehouse)
		self.solution = None
		self.path = []
		self.started = False

	def run(self):
		self.solution = search.breadth_first_graph_search(self.puzzle)
		self.path = [x for x in self.puzzle.goal_path(self.solution)]

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
warehouses = sorted(os.listdir('./warehouses/'))
solutions = {}

for wh_file in warehouses:
	try:
		solutions[wh_file] = Solver(wh_file)
	except AssertionError:
		print(wh_file)
		continue

for wh_file in warehouses[:12]:
	solutions[wh_file].start()

print('started a billion threads')

for w in warehouses[:10]:
	cls()

	print("AI Sokuban Solver!     ~", w)
	print("warehouse:",solutions[w].warehouse)
	print()

	print("Ready?, ",end='')

	for i in range(4):
		time.sleep(0.3)
		print('{}.. '.format(3-i),end='')

	animated_solution = solutions[w].path

	if not animated_solution:
		#wait for solution to finish up
		print('....err, sorry, taking a bit longer than I thought..')
		solutions[w].join(3)
		animated_solution = solutions[w].path
		if not animated_solution:
			print('.. ok well I had a hard time with this one, but continuing..')
			time.sleep(1)
			continue

	#we should have an animated solution

	for node in animated_solution:
		cls()
		print(str(node.state))
		time.sleep(0.1)

	cls()
	print_goal()
	time.sleep(1)

