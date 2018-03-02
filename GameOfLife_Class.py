# The ideas are taken from the C version at chapter 17
# https://www.phatcode.net/res/224/files/html/ch17/17-01.html

#Here a more class oriented approach
import numpy as np
class GameOfLife(object):
	def __init__(self,world):
		_rows,_cols=world.shape
		self.rightedge=_cols-1
		self.bottomedge=_rows-1
		_mesh=np.meshgrid(np.linspace(-1,1,3),np.linspace(-1,1,3),indexing='ij')
		self.mesh_i=np.array(np.delete(_mesh[0].flatten(),4),dtype=np.int8)[np.newaxis].T
		self.mesh_j=np.array(np.delete(_mesh[1].flatten(),4),dtype=np.int8)[np.newaxis].T
		self.world=np.array(world,dtype=np.int8)
		self.prepareInitialWorld()

	def neighbours(self,updateIdx,toadd):
		"""Returns the indices of the 8 Neighbours of cell(i,j)
		   Wraps around the right/bottom edge of the world.
		   The left/up is covered by the numpy conventions
		   [i-1,j-1], [i-1,j], [i-1,j+1]
		   [i,j-1 ] ,  ----  , [i,j+1]
		   [i+1,j-1]  [i+1,j]   [i+1,j+1]"""
		#mesh_i/j are (8 row, 1 column) , updateIdx[0/1] are (1 row, N column
		# this creates an 8xN which we transpose to Nx8
		# So each row of the matrices is the i / j indices to update 
		# per cell 
		update_i=(self.mesh_i+updateIdx[0]).T
		update_j=(self.mesh_j+updateIdx[1]).T
		#handle edges
		update_i[update_i>self.bottomedge]=0
		update_j[update_j>self.rightedge]=0
		#add the proper world
		np.add.at(self.world, (update_i,update_j),toadd)
		pass

	def prepareInitialWorld(self):
		"""Simple helper for the initialisation,
		   Change the input to the conventions used"""
		nonZero=self.world.nonzero()
		self.neighbours(nonZero,2)
		pass


	def evolve(self,steps):
		"""The method that does the actual evolution.
		Only the non-zero cells i.e alive or alive neighbours
		Need to be checked. Update the cell plus its neighbours"""	
		for _ in xrange(steps):
			#Live or dead is the 0th bit
			#Since the neighbour info is encoded 
			#if it is alive and does not have 2 or 3 neighbours it must die
			idx_alive_to_die=((self.world!=0) & (self.world&0x01) &((self.world>>1)!=2) & ((self.world>>1)!=3)).nonzero()
			#if it is dead and has 3 neighbours it becomes alive 
			idx_dead_to_live= ((self.world!=0) & ((self.world&0x01)==0) & ((self.world>>1)==3)).nonzero()
			#Now in the self.world update the cell and the 8 neighbour words
			#All the operations are fixed/encoded at this stage i.e
			#we move all things to the next step
			#This is the part where a more numpy way is perhaps needed
			#we need to add or subtract 2 for each of the 8 neighbours
			self.world[idx_dead_to_live] |= 0x01	
			self.world[idx_alive_to_die] &= (~0x01) 
			self.neighbours(idx_alive_to_die,-2)		
			self.neighbours(idx_dead_to_live,2)

			out=self.world&0x01
			yield out



if __name__ =='__main__':

	animation=True
	if not animation:
		world = np.loadtxt('GliderGun.txt')
		game=GameOfLife(world)
		for i in game.evolve(10000):
			pass
	else:
		#Test the animation 
		import matplotlib
		matplotlib.use('TKAgg')
		import matplotlib.pyplot as plt
		import matplotlib.animation as animation
		# A closure seems nicer for this 
		def animateGame(world,inFrames,inInterval):
			#get the artist we will need
   			fig=plt.figure()
			im=plt.imshow(world,cmap=plt.cm.binary,interpolation='nearest',animated=True)
			#create an instance of the class 
			#This will genetate as many frames as requested 	
    			def animationFrames():    
				game=GameOfLife(world)
        			for i in game.evolve(inFrames):
            				yield i

            		#Here we set the 'artist', needs one input argument
			# which is what animationFrames yields
    			def animate(board):
        			im.set_data(board)
        			return (im,)
    
    			ani = animation.FuncAnimation(fig, animate, frames=animationFrames,interval=inInterval,blit=True)
    			plt.show()

		world = np.loadtxt('GliderGun.txt')
		animateGame(world,200,50)
	


