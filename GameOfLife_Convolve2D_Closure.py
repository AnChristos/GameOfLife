#Solution using a more functional approach , with a generator
#function at its core
# inspiration from http://jakevdp.github.io/blog/2013/08/07/conways-game-of-life/
import numpy as np
from scipy.signal import convolve2d

#This is a generator / closure to evolve N steps
def evolve(world):
	#[i-1,j-1], [i-1,j], [i-1,j+1]
	# [i,j-1 ] ,  ----  , [i,j+1]
	# [i+1,j-1]  [i+1,j]   [i+1,j+1]      
        # count the number of neighbours 
        neigh = convolve2d(world, np.ones((3, 3)), mode='same', boundary='wrap') - world
        # game of life rules
        localworld = np.logical_or(np.logical_and(world, neigh ==2), neigh==3)
        localworld = localworld.astype(int)
        return  localworld

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
   			fig=plt.figure()
   			ims=[] 
    			for i in range(inFrames):
        			print(i)
        			world=evolve(world)
				im=plt.imshow(world,cmap=plt.cm.binary,interpolation='nearest',animated=True)
        			ims.append([im])
        
    			ani=animation.ArtistAnimation(fig, ims,interval=inInterval,blit=True)
    			plt.show()
    			pass
		
		world = np.loadtxt('GliderGun.txt')
		animateGame(world,200,50)
	


