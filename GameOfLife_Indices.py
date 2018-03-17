#!/usr/bin/env python
import numpy as np
# The ideas are taken from the C version at chapter 17
# https://www.phatcode.net/res/224/files/html/ch17/17-01.html

#Simple function to encode the rules,this depends on how the evolve expects them
def GameOfLife(world):
	#Live or dead is the 0th bit
	 #Since the neighbour info is encoded 
	#if it is alive and does not have 2 or 3 neighbours it must die
	idx_alive_to_die=np.nonzero( (world&0x01) &((world>>1)!=2) & ((world>>1)!=3))
	#if it is dead and has 3 neighbours it becomes alive 
	idx_dead_to_live= np.nonzero(((world&0x01)==0) & ((world>>1)==3))	
	return idx_alive_to_die,idx_dead_to_live

def HighLife(world):
	#if it is alive and does not have 2 or 3 neighbours it must die
	idx_alive_to_die=np.nonzero((world!=0) & (world&0x01) &((world>>1)!=2) & ((world>>1)!=3))
	#if it is dead and has 3 or 6 neighbours it becomes alive 
	idx_dead_to_live= np.nonzero((world!=0) & ((world&0x01)==0) & ( ((world>>1)==3) | ((world>>1)==6) ) )
	return idx_alive_to_die,idx_dead_to_live

#This is a generator  to evolve N steps
def evolve(world,steps,ruleFun=GameOfLife,Infinite=False):
	""" Each cell encodes at bit :
	0 : Live or dead
	1-4 : +=2 for each alive neighbour (so values can be 0-16)
	5-7 :not used  """
	#Get an idea of the world shape
	rows, cols=world.shape
	bottomedge=rows-1
	rightedge=cols-1
	center_i=rows>>1
	center_j=cols>>1

	mesh=np.meshgrid(np.linspace(-1,1,3),np.linspace(-1,1,3),indexing='ij')
	mesh_i=np.array(np.delete(mesh[0].flatten(),4),dtype=np.int8)[np.newaxis].T
	mesh_j=np.array(np.delete(mesh[1].flatten(),4),dtype=np.int8)[np.newaxis].T
	def neighbours(world,updateIdx,toadd):
		"""Returns the indices of the 8 Neighbours of cell(i,j)
		   Wraps around the right/bottom edge of the world.
		   The left/up is covered by the numpy conventions
		   [i-1,j-1], [i-1,j], [i-1,j+1]
		   [i,j-1 ] ,  ----  , [i,j+1]
		   [i+1,j-1]  [i+1,j]   [i+1,j+1]"""
		#mesh_i/j are (8 row, 1 column) , updateIdx[0/1] are (1 row, N column
		# this creates an 8xN which we ravel so we have the i,j inices
		update_i=mesh_i+updateIdx[0]
		update_j=mesh_j+updateIdx[1]
		#handle edges
		update_i[update_i>bottomedge]=0
		update_j[update_j>rightedge]=0
		#add the proper world
		np.add.at(world, (update_i,update_j),toadd)
		return world


	def evolveCells(world):
		"""The method that does the actual evolution.
		Only the non-zero cells i.e alive or alive neighbours
		Need to be checked. Update the cell plus its neighbours"""
		#Live or dead is the 0th bit
		#Since the neighbour info is encoded 
		idx_alive_to_die,idx_dead_to_live=ruleFun(world)
		#Now in the world update the cells to change and the 8 neighbour words
		#All the operations are fixed/encoded at this stage i.e
		#we move all things to the next step	
		world[idx_dead_to_live] |= 0x01
		world[idx_alive_to_die] &= (~0x01) 
		#we need to add or subtract 2 for each of the 8 neighbours
		world=neighbours(world,idx_dead_to_live,2)
		world=neighbours(world,idx_alive_to_die,-2)
		return world

	def handle_inf():
		#The simplest is to keep the cells at the middle of the board
		#At least for shapes than do not grow too fast keeping the "centre
		# of mass" of the live cells should be good enough
		#Find the max and minimum of the live cells
		alive_tuple=(world&0x01).nonzero()
		if alive_tuple[0].size==0:
            		return world,world.shape
		
		min_i=np.amin(alive_tuple[0])
		max_i=np.amax(alive_tuple[0])
		min_j=np.amin(alive_tuple[1])
		max_j=np.amax(alive_tuple[1])
		#Do we need to resize i.e are we going out of the edges? 	
		newrows=rows
		newcols=cols
		addrows=0
		addcols=0
		if (max_i==bottomedge or  min_i==0):
			addrows=int(0.1*rows)
			newrows=rows+2*addrows

		if(max_j==rightedge or  max_j==0) :
			addcols=int(0.1*cols)
			newcols=cols+2*addcols
		
		newshape=(newrows,newcols)
		#offset to keep the live barycenter at the center
		offset_i = center_i - min_i- (int(max_i-min_i)>>1)
		offset_j = center_j - min_j -(int(max_j-min_j)>>1)
		#Create the new world
		if(newshape==world.shape):
			nextworld=np.roll(world,(offset_i,offset_j),axis=(0,1))
		else:
			nextworld=np.zeros(newshape,dtype=np.int8)
			nextworld[addrows:rows+addrows,addcols:cols+addcols]=np.roll(world,(offset_i,offset_j),axis=(0,1))

		return nextworld,newshape
	
	#convert as to use the internal conventions
	world=np.array(world,dtype=np.int8)
	nonZero=world.nonzero()
	world=neighbours(world,nonZero,2)

	#step using the function set up above
	for _ in xrange(steps):	        
		nextworld=evolveCells(world)
		world=nextworld
		if Infinite:
			world,shape=handle_inf()
			rows,cols=world.shape
			bottomedge=rows-1
			rightedge=cols-1
			center_i=rows>>1
			center_j=cols>>1	
		out=world&0x01	
		yield out

if __name__ =='__main__':

	animation=True
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
			fig,ax=plt.subplots()
			im=plt.imshow(world,cmap=plt.cm.binary,interpolation='nearest',animated=True)
			ax.set_yticklabels([])
			ax.set_xticklabels([])
			#This will genetate as many frames as requested 	
			def animationFrames():
				yield world
				for i in evolve(world,inFrames,GameOfLife,True):
					yield i

			#Here we set the 'artist', needs one input argument
			# which is what animationFrames yields
			def animate(board):
				im.set_data(board)
				return (im,)

			ani = animation.FuncAnimation(fig, animate, frames=animationFrames,interval=inInterval,blit=True)
			plt.show()

		world = np.loadtxt('GliderGun.txt')
		animateGame(world,1000,50)




