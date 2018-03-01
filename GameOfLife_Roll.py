#Same as the Generator but with std function at its core

import numpy as np

#This is a generator / closure to evolve N steps
def evolve(X):

	def roll_it(x, y):
		# x=1, y=0 on the left;  x=-1, y=0 right;
		# x=0, y=1 top; x=0, y=-1 down; x=1, y=1 top left; ...
		return np.roll(np.roll(X, y, axis=0), x, axis=1)

	Y = roll_it(1, 0) + roll_it(0, 1) + roll_it(-1, 0) \
			+ roll_it(0, -1) + roll_it(1, 1) + roll_it(-1, -1) \
			+ roll_it(1, -1) + roll_it(-1, 1)
	# game of life rules
	X=np.logical_or(np.logical_and(X, Y ==2), Y==3)
	X=X.astype(int)
	return X

def animateGame(world,Nframes,interv):
	#This is the "artist object which we update"
	fig=plt.figure()
	im=plt.imshow(world,cmap=plt.cm.binary,interpolation='nearest',animated=True)   
         
	def animate(*args):
		global world
		NewWorld=evolve(world)
		im.set_data(NewWorld)
		world=NewWorld
		return (im,)

	ani = animation.FuncAnimation(fig, animate, frames=200,interval=100,blit=True)
	plt.show()  
       


if __name__ =='__main__':
	world = np.loadtxt('GliderLarge.txt')
	#for i in xrange (1000):
	#	worldNext=evolve(world)
	
	import matplotlib
	matplotlib.use('TKAgg')
	import matplotlib.pyplot as plt
	import matplotlib.animation as animation

	animateGame(world,200,100)

