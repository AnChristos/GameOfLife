#!/usr/bin/env python
import numpy as np

#Naive / text book Game of Life Implementation

#This is a generator  to evolve N steps
def evolve(world,steps,Born=(3,),Survive=(2,3),Infinite=False):
	#Get an idea of the world shape
	rows, cols=world.shape
	bottomedge=rows-1
	rightedge=cols-1
	center_i=rows>>1
	center_j=cols>>1
	world=np.array(world,dtype=np.int8)
	def evolveCells(world):
		"""The method that does the actual evolution.
		Only the non-zero cells i.e alive or alive neighbours
		Need to be checked. Update the cell plus its neighbours"""
		#[i-1,j-1], [i-1,j], [i-1,j+1]
		#   [i,j-1 ] ,  ----  , [i,j+1]
		#   [i+1,j-1]  [i+1,j]   [i+1,j+1]
		step=world.copy()	
		for i in xrange(rows):
			for j in xrange (cols):
				alive=world[i,j]
				try:
					neighsum=world[i-1,j-1]+\
				        	world[i-1,j]+\
					 	world[i-1,j+1]+\
					 	world[i,j-1]+\
					 	world[i,j+1]+\
					 	world[i+1,j-1]+\
					 	world[i+1,j]+\
					 	world[i+1,j+1]
						
				except IndexError:
					if i>bottomedge and j>righedge:
						neighsum=world[i-1,j-1]+\
				        		world[i-1,j]+\
					 		world[i-1,0]+\
					 		world[i,j-1]+\
					 		world[i,0]+\
					 		world[0,j-1]+\
					 		world[0,j]+\
					 		world[0,0]
					elif i>bottomedge:
						neighsum=world[i-1,j-1]+\
				        		world[i-1,j]+\
					 		world[i-1,j+1]+\
					 		world[i,j-1]+\
					 		world[i,j+1]+\
					 		world[0,j-1]+\
					 		world[0,j]+\
					 		world[0,j+1]
					elif j>rightedge:
						neighsum=world[i-1,j-1]+\
				        		world[i-1,j]+\
					 		world[i-1,0]+\
					 		world[i,j-1]+\
					 		world[i,0]+\
					 		world[i+1,j-1]+\
					 		world[i+1,j]+\
					 		world[i+1,0]



				if alive==0 and neighsum in Born:
					step[i,j]=1
				elif alive==1 and neighsum in Survive :
					step[i,j]=1
				else:
					step[i,j]=0
		return step

	def handle_inf(world):
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
	#step using the function set up above
	for _ in xrange(steps):	        
		world=evolveCells(world)
		if Infinite:
			world,shape=handle_inf(world)
			rows,cols=world.shape
			bottomedge=rows-1
			rightedge=cols-1
			center_i=rows>>1
			center_j=cols>>1	
		yield world

if __name__ =='__main__':
	animation=True
	if not animation:
		world = np.loadtxt('GliderGun.txt')
		for nextWorld in evolve(world,100):
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
		animateGame(world,1000,50)




