import numpy as np

# The ideas are taken from the C version at chapter 17
# https://www.phatcode.net/res/224/files/html/ch17/17-01.html

#This is a generator  to evolve N steps
def evolve(world,steps):
	""" Each cell encodes at bit :
	0 : Live or dead
	1-4 : +=2 for each alive neighbour (so values can be 0-16)
	5-7 :not used  """
	#Get an idea of the world shape
	rows,cols=world.shape
	rightedge=cols-1
	bottomedge=rows-1
	#convert to the internal representation 
	world=np.array(world,dtype=np.int8)
	
	mesh=np.meshgrid(np.linspace(-1,1,3),np.linspace(-1,1,3),indexing='ij')
	mesh_i=np.array(np.delete(mesh[0].flatten(),4),dtype=np.int8)[np.newaxis].T
	mesh_j=np.array(np.delete(mesh[1].flatten(),4),dtype=np.int8)[np.newaxis].T
	def neighbours(updateIdx,toadd):
		"""Returns the indices of the 8 Neighbours of cell(i,j)
		   Wraps around the right/bottom edge of the world.
		   The left/up is covered by the numpy conventions
		   [i-1,j-1], [i-1,j], [i-1,j+1]
		   [i,j-1 ] ,  ----  , [i,j+1]
		   [i+1,j-1]  [i+1,j]   [i+1,j+1]"""
		update_i=(mesh_i+updateIdx[0]).T
		update_j=(mesh_j+updateIdx[1]).T
		allcomb=map(lambda x,y :( x, y ) ,update_i,update_j)
		print allcomb
		#This can be slow in python but possibly can be mapped
		for neighIdx in allcomb: 
			try :	
				world[neighIdx]+=toadd
			except IndexError:
				if np.any(neighIdx[0]==bottomedge) :
					neighIdx[0][5:8]=0
				if np.any(neighIdx[1]==rightedge):
					neighIdx[1][np.array([2,4,7])]=0			
				world[neighIdx]+=toadd
		pass

	def prepareInitialWorld():
		"""Simple helper for the initialisation,
		   Change the input to the conventions used"""
		nonZero=world.nonzero()
		neighbours(nonZero,int(2))
		pass

	def evolveCells():
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
		neighbours(idx_dead_to_live,int(2))
		neighbours(idx_alive_to_die,int(-2))
		pass
        #convert as to use the internal conventions
	prepareInitialWorld()
	#step using the function set up above
	for _ in xrange(steps):
		evolveCells()
	        #swap the "pointers"
		out=world&0x01	
		yield out

if __name__ =='__main__':

 	animation=False
	if not animation:
		world = np.loadtxt('GliderGun.txt')
		for nextWorld in evolve(world,10000):
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
			#This will genetate as many frames as requested 	
    			def animationFrames():    
				for i in evolve(world,inFrames):
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
	
	


