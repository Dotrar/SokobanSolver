import search
import sokoban
import time
import os
import sys
from functools import partial
from threading import Thread

class SokobanPuzzle(search.Problem):

	#warehouse walls, goals, and taboos stay the same
	#boxes and player move so that is the "state"

	def __init__(self, warehouse, cgt_goal = None):
		self.initial = warehouse
		self.taboos = gen_taboos(warehouse)
		
		if cgt_goal is not None:
			self.cgt_goal = (cgt_goal[1]-1,cgt_goal[0]-1) #cgt is given in (row,col) format
		else:
			self.cgt_goal = None

	def actions(self, state):
		"""
		Return the list of actions that can be executed in the given state 
		if these actions do not push a box in a taboo cell.
		The actions must belong to the list ['Left', 'Down', 'Right', 'Up']        
		"""
		px,py = state.worker
		actions = []
		
		#for each action, check if we're 1.pushing a box into a taboo or 2. moving into empty space
		
		ac = ['Up','Down','Left','Right']
		position = [(px,py-1),(px,py+1),(px-1,py),(px+1,py)]
		check = [(px,py-2),(px,py+2),(px-2,py),(px+2,py)]
		
		for i in range(0,4):

			if position[i] in state.boxes:
				if self.cgt_goal is not None:
					continue
				
				#we're not moving a box into a taboo, walls, or into other boxes.
				if check[i] in self.taboos or check[i] in state.walls or check[i] in state.boxes:
					#skip this
					continue
				
			if position[i] in state.walls:
				#skip this
				continue
			
			actions.append(ac[i])
			
		return actions

	def result(self, s, action):
		#return the state resolved from executing action
		
		state = s.copy(boxes=list(s.boxes)) #we return a copy of the state
		
		nx,ny = state.worker
		cx,cy = state.worker
	
		if(action is 'Up'):
			ny -= 1
			cy -= 2
		elif(action is 'Down'):
			ny += 1
			cy += 2
		elif(action is 'Right'):
			nx += 1
			cx += 2
		elif(action is 'Left'):
			nx -= 1
			cx -= 2

		if (nx,ny) in state.walls: #can't move into a wall
			return state
		
		if (self.cgt_goal is not None): #if we're cgt, then can't move into a box
			if (nx,ny) in state.boxes:
				return state

		for thebox,box in enumerate(state.boxes):
			if (nx,ny) == box: #if we're moving into a box

				if (cx,cy) in state.boxes or (cx,cy) in state.walls: #if we're moving the box into another box or wall

					#can't do anything. return state
					return state
				else: #move box
					state.boxes[thebox] = (cx,cy) # move it to where we forcasted
				break

		state.worker = (nx,ny)
		
		return state
	
	def print_solution(self,goal_node):
		path = goal_node.path()
		
		print("solution takes {0} moves".format(len(path)-1))
		print(path[0].state)
		print("to solution:")
		print(path[-1].state)
		print("moves:")
		
		for node in path:
			print(node.action)
			print(node.state)

	def goal_path(self,goal_node):
		path = goal_node.path()
		return path[1:]
	
	def goal_test(self, state):
				
		if self.cgt_goal is not None: #can go there goal test
			
			#print(state.worker, self.cgt_goal, state.worker == self.cgt_goal)
			return state.worker == self.cgt_goal
		
		else:	#sokoban goal test - every box on a goal
			return str(state).count('$') == 0
	
	
def gen_taboos(warehouse):

	#the start of anything great starts with an empty list
	taboo = []
	
	#go along the walls and find corners
	for (x,y) in warehouse.walls:
		#if we have a gap on the right, ( left wall ) and a wall above or below that:
		if (x+1,y) not in warehouse.walls and (
		(x+1,y+1) in warehouse.walls or (x+1,y-1) in warehouse.walls):
			taboo.append((x+1,y))
			
		#and for the gap on the left ( right wall ) yadda yadda
		if(x-1,y) not in warehouse.walls and (
		(x-1,y+1) in warehouse.walls or (x-1,y-1) in warehouse.walls):
			taboo.append((x-1,y))


	#remove any taboos that are targets
	taboo = [t for t in taboo if t not in warehouse.targets]
	
	#check if outside play area ( should not be inline with the topmost, bottommost, etc)
	#ex = get x component, etc. shortcut
	ex = lambda x:x[0]
	ey = lambda x:x[1]
	
	topmost = min(warehouse.walls, key=ey)
	botmost = max(warehouse.walls, key=ey)
	rigmost = max(warehouse.walls, key=ex)
	lefmost = min(warehouse.walls, key=ex)

	#trim any that are inline with topmost, etc.
	taboo = [ t for t in taboo if ey(t) is not ey(topmost) and ey(t) is not ey(botmost) and ex(t) is not ex(rigmost) and ex(t) is not ex(lefmost)]

	
	#get a list of taboos that are inline with each other ( a pair)
	#0^2 time here, probably really bad
	taboo_pairs = []
	for t in taboo:
		for T in taboo:
			if (T[0] == t[0] or t[1] == T[1]) and T is not t:
				if [T,t] not in taboo_pairs or [t,T] not in taboo_pairs:   
					#print(T,t])
					taboo_pairs.append([t,T])

	#have a list of pairs that we calculate between them.
	for pair in taboo_pairs:
		wall_check = 0		#wall runner
		gap = False		#a gap was found ( not taboo ) 
		a,b = pair[0],pair[1] #each taboo
		
		if(a[0] == b[0]): #x components are the same, so check along y
			# (2,2) -> (2,6)
			
			if(a[0]+1,a[1]) in warehouse.walls: #check which side wall is on
				wall_check=a[0]+1
			else: #it was on the other side
				wall_check=a[0]-1
		
			#run along wall, see if there's a gap
			for i in range(a[1],b[1]): # each cell between a and b
				if (wall_check,i) not in warehouse.walls or (a[0],i) in warehouse.walls or (a[0],i) in warehouse.targets:
					#there's a gap in the wall or we ran into a wall.
					gap = True
					
			#if we didn't have a gap, paint the entire wall
			if not gap:
				for i in range(a[1],b[1]):
					taboo.append((a[0],i)) #append a whole lotta taboos

			
		else: #check along x direction
			
			if(a[0],a[1]+1) in warehouse.walls: #check which side wall is on
				wall_check=a[1]+1
			else: #it was on the other side
				wall_check=a[1]-1
		
			#run along wall, see if there's a gap
			for i in range(a[0],b[0]): #between a and b
				if (i,wall_check) not in warehouse.walls or (i,a[1]) in warehouse.walls or (i,a[1]) in warehouse.targets:
					#there's a gap in the wall or we ran into one
					gap = True
		
			if not gap:
				for i in range(a[0],b[0]):
					taboo.append((i,a[1])) #append a whole lotta taboos
	return taboo
	

def taboo_cells(warehouse):
	'''  
    Identify the taboo cells of a warehouse. A cell is called 'taboo' 
    if whenever a box get pushed on such a cell then the puzzle becomes unsolvable.  
    When determining the taboo cells, you must ignore all the existing boxes, 
    simply consider the walls and the target  cells.  
    Use only the following two rules to determine the taboo cells;
     Rule 1: if a cell is a corner and not a target, then it is a taboo cell.
     Rule 2: all the cells between two corners along a wall are taboo if none of 
             these cells is a target.

    @param warehouse: a Warehouse object

    @return
       A string representing the puzzle with only the wall cells marked with 
       an '#' and the taboo cells marked with an 'X'.  
       The returned string should NOT have marks for the worker, the targets,
       and the boxes.  
    '''
	taboo = gen_taboos(warehouse)
					
	#zip it up
	#shamelessly copied from example code
	X,Y = zip(*warehouse.walls)
	x_size, y_size = 1+max(X), 1+max(Y)
	vis = [[" "] * x_size for y in range(y_size)]
	for (x,y) in warehouse.walls:
		vis[y][x] = "#"
	for (x,y) in taboo:
		vis[y][x] = "X"
	
	return "\n".join(["".join(line) for line in vis])

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def check_action_seq(warehouse, action_seq):
	'''
	Determine if the sequence of actions listed in 'action_seq' is legal or not.

	Important notes:
	  - a legal sequence of actions does not necessarily solve the puzzle.
	  - an action is legal even if it pushes a box onto a taboo cell.

	@param warehouse: a valid Warehouse object

	@param action_seq: a sequence of legal actions.
	       For example, ['Left', 'Down', Down','Right', 'Up', 'Down']

	@return
	    The string 'Failure', if one of the action was not successul.
	       For example, if the agent tries to push two boxes at the same time,
	                    or push one box into a wall.
	    Otherwise, if all actions were successful, return                 
	           A string representing the state of the puzzle after applying
	           the sequence of actions.  This must be the same string as the
	           string returned by the method  Warehouse.__str__()
	'''
	puzzle = SokobanPuzzle(warehouse)
	old_result = puzzle.initial
	
	for action in action_seq:
		result = puzzle.result(old_result,action)
		
		if old_result == result: #action didn't do anything, so it is illegal
			return 'Failure'
		old_result = result
		
	return old_result

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def solve_sokoban_elem(warehouse):
	'''    
	This function should solve using elementary actions 
	the puzzle defined in a file.

	@param warehouse: a valid Warehouse object

	@return
	    A list of strings.
	    If puzzle cannot be solved return ['Impossible']
	    If a solution was found, return a list of elementary actions that solves
	        the given puzzle coded with 'Left', 'Right', 'Up', 'Down'
	        For example, ['Left', 'Down', Down','Right', 'Up', 'Down']
	        If the puzzle is already in a goal state, simply return []
	'''
	problem = SokobanPuzzle(warehouse)
	
	solution = search.breadth_first_graph_search(problem)
		
	if solution is not None:
		return [node.action for node in problem.goal_path(solution) if node.action is not 'None']
	else:
		return ['Impossible']

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def can_go_there(warehouse, dst):
	'''    
	Determine whether the worker can walk to the cell dst=(row,col) 
	without pushing any box.

	@param warehouse: a valid Warehouse object

	@return
	  True if the worker can walk to cell dst=(row,col) without pushing any box
	  False otherwise
	'''
	#do a simple search to find a path to the place.
	problem = SokobanPuzzle(warehouse,dst)
	solution = search.breadth_first_graph_search(problem)
	
	return solution is not None

