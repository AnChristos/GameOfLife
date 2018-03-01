#Solution using a more functional approach , with a generator
#function at its core
# inspiration from http://jakevdp.github.io/blog/2013/08/07/conways-game-of-life/
import numpy as np


#This is a generator / closure to evolve N steps
def evolve(world,steps):
    def roll_it(x, y):
        # x=1, y=0 on the left;  x=-1, y=0 right;
        # x=0, y=1 top; x=0, y=-1 down; x=1, y=1 top left; ...
        return np.roll(np.roll(world, y, axis=0), x, axis=1)

    for _ in xrange(steps):
        # count the number of neighbours 
        neigh = roll_it(1, 0) + roll_it(0, 1) + roll_it(-1, 0) \
            + roll_it(0, -1) + roll_it(1, 1) + roll_it(-1, -1) \
            + roll_it(1, -1) + roll_it(-1, 1)
        # game of life rules
        world = np.logical_or(np.logical_and(world, neigh ==2), neigh==3)
        world = world.astype(int)
        yield world

if __name__ =='__main__':

 	animation=True
	if not animation:
		world = np.loadtxt('GliderLarge.txt')
		for nextWorld in evolve(world,1000):
			pass
	else:
		#Test the animation 
		import matplotlib
		matplotlib.use('TKAgg')
		import matplotlib.pyplot as plt
		import matplotlib.animation as animation
		# A closure seems nicer for this 
		def animateGame(world,frames,inInterval):
			#get the artist we will need
   			fig=plt.figure()
			im=plt.imshow(world,cmap=plt.cm.binary,interpolation='nearest',animated=True)
			#This will genetate as many frames as requested 	
    			def animationFrames():    
        			for i in evolve(world,frames):
            				yield i

            		#Here we set the 'artist', needs one input argument
			# which is what animationFrames yields
    			def animate(board):
        			im.set_data(board)
        			return (im,)
    
    			ani = animation.FuncAnimation(fig, animate, frames=animationFrames,interval=inInterval,blit=True)
    			plt.show()

		world = np.loadtxt('GliderLarge.txt')
		animateGame(world,200,100)
	

