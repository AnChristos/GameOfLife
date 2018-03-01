# The ideas are taken from the C version at chapter 17
# https://www.phatcode.net/res/224/files/html/ch17/17-01.html

#Here a more class oriented approach
import numpy as np
class GameOfLife:
	def __init__(self,world):
		rows,cols=world.shape
		self.rightedge=cols-1
		self.bottomedge=rows-1
		self.world=np.array(world,dtype=np.int8)
		self.prepareInitialWorld()
		
	def neighbours(self,i,j):
		"""Returns the indices of the 8 Neighbours of cell(i,j)
		   Wraps around the right/bottom edge of the world.
		   The left/up is covered by the numpy conventions
		   [i-1,j-1], [i-1,j], [i-1,j+1]
		   [i,j-1 ] ,  ----  , [i,j+1]
		   [i+1,j-1]  [i+1,j]   [i+1,j+1]"""
		#Perhaps small Opt are possible here 
		neighIdx= (np.array([i-1,i-1,i-1,i,i,i+1,i+1,i+1]),
				np.array([j-1,j,j+1,j-1,j+1,j-1,j,j+1]))
		if i<self.bottomedge and j<self.rightedge:
			return neighIdx
		else :
			if i==self.bottomedge :
				neighIdx[0][5:8]=0
			if j==self.rightedge:
				neighIdx[1][np.array([2,4,7])]=0
			return neighIdx	

	def prepareInitialWorld(self):
		"""Simple helper for the initialisation,
		   Change the input to the conventions used"""
		nonZero=self.world.nonzero()
		for i in xrange(nonZero[0].size):
			neighindices=self.neighbours(nonZero[0][i],nonZero[1][i])
			self.world[neighindices]+=2
		pass


	def evolve(self):
		"""The method that does the actual evolution.
		Only the non-zero cells i.e alive or alive neighbours
		Need to be checked. Update the cell plus its neighbours"""
		#Live or dead is the 0th bit
		#Since the neighbour info is encoded 
		#if it is alive and does not have 2 or 3 neighbours it must die
		idx_alive_to_die=((self.world!=0) & (self.world&0x01) &((self.world>>1)!=2) & ((self.world>>1)!=3)).nonzero()
		#if it is dead and has 3 neighbours it becomes alive 
		idx_dead_to_live= ((self.world!=0) & ((self.world&0x01)==0) & ((self.world>>1)==3)).nonzero()
	
		
		#Now in the self.world update the cell and the 8 neighbour words
		#All the operations are fixed/encoded at this stage i.e
		#we move all things to the next step
		self.world[idx_dead_to_live] |= 0x01
		self.world[idx_alive_to_die] &= (~0x01) 
		#This is the part where a more numpy way is perhaps needed
		#we need to add or subtract 2 for each of the 8 neighbours

		#This is still a python loop so can be further optimised
		for i in xrange(idx_dead_to_live[0].size):
			self.world[self.neighbours(idx_dead_to_live[0][i],idx_dead_to_live[1][i])]+=2
		for i in xrange(idx_alive_to_die[0].size):
			self.world[self.neighbours(idx_alive_to_die[0][i],idx_alive_to_die[1][i])]-=2		
		
		out=self.world&0x01	
		return out



if __name__ =='__main__':
	
	world = np.loadtxt('GliderLarge.txt')
	mygame=GameOfLife(world)
	
	animation=True
	
	if not animation:
		for i in xrange (1000):
			mygame.evolve()
	else:
		#Test the animation 
		import matplotlib
		matplotlib.use('TKAgg')
		import matplotlib.pyplot as plt
		import matplotlib.animation as animation

		fig=plt.figure()
		im=plt.imshow(world,cmap=plt.cm.binary,interpolation='nearest',animated=True)

		def animate(*args): 
			data= mygame.evolve()
			im.set_data(data)
			return im,

		ani = animation.FuncAnimation(fig, animate, frames=200, interval=100,blit=True)
		plt.show()



