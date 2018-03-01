import numpy as np

# The ideas are taken from the C version at chapter 17
# https://www.phatcode.net/res/224/files/html/ch17/17-01.html

#This is a generator / "closure" to evolve N steps
def evolve(world,steps):
	""" Each cell encodes at bit :
	0 : Live or dead
	1-4 : +=2 for each alive neighbour (so values can be 0-16)
	5-7 :not used  """
	#Get an idea of the world shape
	rows,cols=world.shape
	rightedge=cols-1
	bottomedge=rows-1

	def neighbours(i,j):
		"""Returns the indices of the 8 Neighbours of cell(i,j)
		   Wraps around the right/bottom edge of the world.
		   The left/up is covered by the numpy conventions
		   [i-1,j-1], [i-1,j], [i-1,j+1]
		   [i,j-1 ] ,  ----  , [i,j+1]
		   [i+1,j-1]  [i+1,j]   [i+1,j+1]"""
		#Perhaps small Opt are possible here 
		neighIdx= (np.array([i-1,i-1,i-1,i,i,i+1,i+1,i+1]),
				np.array([j-1,j,j+1,j-1,j+1,j-1,j,j+1]))
		if i<bottomedge and j<rightedge:
			return neighIdx
		else :
			if i==bottomedge :
				neighIdx[0][5:8]=0
			if j==rightedge:
				neighIdx[1][np.array([2,4,7])]=0
			return neighIdx	

	def prepareInitialWorld(world):
		"""Simple helper for the initialisation,
		   Change the input to the conventions used"""
		nonZero=world.nonzero()
		for i in xrange(nonZero[0].size):
			neighindices=neighbours(nonZero[0][i],nonZero[1][i])
			world[neighindices]+=2
		pass

	def evolveCells(world):
		"""The method that does the actual evolution.
		Only the non-zero cells i.e alive or alive neighbours
		Need to be checked. Update the cell plus its neighbours"""
		#Live or dead is the 0th bit
		#Since the neighbour info is encoded 
		#if it is alive and does not have 2 or 3 neighbours it must die
		idx_alive_to_die=((world!=0) & (world&0x01) &((world>>1)!=2) & ((world>>1)!=3)).nonzero()
		#if it is dead and has 3 neighbours it becomes alive 
		idx_dead_to_live= ((world!=0) & ((world&0x01)==0) & ((world>>1)==3)).nonzero()
	
		
		#Now in the world update the cell and the 8 neighbour words
		#All the operations are fixed/encoded at this stage i.e
		#we move all things to the next step
		world[idx_dead_to_live] |= 0x01
		world[idx_alive_to_die] &= (~0x01) 
		#This is the part where a more numpy way is perhaps needed
		#we need to add or subtract 2 for each of the 8 neighbours

		#This is still a python loop so can be further optimised
		for i in xrange(idx_dead_to_live[0].size):
			world[neighbours(idx_dead_to_live[0][i],idx_dead_to_live[1][i])]+=2
		for i in xrange(idx_alive_to_die[0].size):
			world[neighbours(idx_alive_to_die[0][i],idx_alive_to_die[1][i])]-=2		
		pass

	#convert to the internal representation 
	world=np.array(world,dtype=np.int8)
	prepareInitialWorld(world)
	#srep using the function set up above
	for _ in xrange(steps):
		evolveCells(world)
	        #swap the "pointers"
		out=world&0x01	
		yield out

if __name__ =='__main__':
	world = np.loadtxt('GliderSmall.txt')
	for nextworld in evolve(world,1000):
		print nextworld
		
	


