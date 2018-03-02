#Solution using a more functional approach , with a generator
#function at its core
# inspiration from http://jakevdp.github.io/blog/2013/08/07/conways-game-of-life/
import numpy as np
from scipy.signal import convolve2d

#This is a generator / closure to evolve N steps
def evolve(world,steps):
	#[i-1,j-1], [i-1,j], [i-1,j+1]
	# [i,j-1 ] ,  ----  , [i,j+1]
	# [i+1,j-1]  [i+1,j]   [i+1,j+1]      
	for _ in xrange(steps):
        	# count the number of neighbours 
        	neigh = convolve2d(world, np.ones((3, 3)), mode='same', boundary='wrap') - world
        	# game of life rules
        	world = np.logical_or(np.logical_and(world, neigh ==2), neigh==3)
        	world = world.astype(int)
        	yield world

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
	

