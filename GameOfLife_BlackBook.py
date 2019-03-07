#!/usr/bin/env python
import numpy as np
# The ideas are taken from the C version at chapter 17
# https://www.phatcode.net/res/224/files/html/ch17/17-01.html
#Simple function to encode the rules,this depends on how the evolve expects them
def GameOfLife(world):
    #Live or dead is the 0th bit
    #Since the neighbour info is encoded 
    #if it is alive and does not have 2 or 3 neighbours it must die
    idx_alive_to_die= np.logical_and ( (world&0x01) , np.logical_and( (world>>1)!=2,(world>>1)!=3 ) ).nonzero()
    #if it is dead and has 3 neighbours it becomes alive 
    idx_dead_to_live= np.logical_and( (world>>1)==3, (world&0x01)==0 ).nonzero()
    return idx_alive_to_die,idx_dead_to_live

def HighLife(world):
    #if it is alive and does not have 2 or 3 neighbours it must die
    idx_alive_to_die= np.logical_and ( (world&0x01) , np.logical_and( (world>>1)!=2 , (world>>1)!=3)).nonzero()
    #if it is dead and has 3 or 6 neighbours it becomes alive 
    idx_dead_to_live= np.logical_and(np.logical_or( (world>>1)==3, (world>>1)==6), (world&0x01)==0).nonzero()	
    return idx_alive_to_die,idx_dead_to_live

#This is a generator  to evolve N steps

def evolve(world,steps,ruleFun=GameOfLife,doWrap=False):
    """ Each cell encodes at bit :
    0 : Live or dead
    1-4 : +=2 for each alive neighbour (so values can be 0-16)
    5-7 :not used  """
   
    rows,cols=world.shape
   
    visBeginR=3
    visEndR=rows+3
    sizeR=rows+6
    
    visBeginC=3
    visEndC=cols+3
    sizeC=cols+6
    
    if doWrap:
        visBeginR=0
        visEndR=rows
        sizeR=rows
        visBeginC=0
        visEndC=cols
        sizeC=cols
      
    #internal world
    #we can can use the internal convention
    #and also avoid the wrapping
    worldInternal=np.zeros((sizeR,sizeC))
    worldInternal[visBeginR:visEndR,visBeginC:visEndC]=world
    worldInternal=np.array(worldInternal,dtype=np.int8)
    nonZero=worldInternal.nonzero() 

    bottomedge=sizeR-1
    rightedge=sizeC-1
    
    #[i-1,j-1], [i-1,j], [i-1,j+1]
    #[i,j-1 ] ,  ----  , [i,j+1]
    #[i+1,j-1]  [i+1,j]   [i+1,j+1]
    relative_i= np.array([-1,-1,-1,0,0,1,1,1])[np.newaxis].T
    relative_j= np.array([-1,0,1,-1,1,-1,0,1])[np.newaxis].T

    def neighbours(inputworld,updateIdx,toadd):
        """Returns the indices of the 8 Neighbours of cell(i,j)
        Wraps around the right/bottom edge of the world.
        The left/up is covered by the numpy conventions"""
        #mesh_i/j are (8 rows, 1 column)  
        #updateIdx[0/1] are (1 row, N columns where N depends on the indices to update)
        #At the end we have 2 matrices with the indexes
        #of the neighbours to update
        update_i=relative_i+updateIdx[0]
        update_j=relative_j+updateIdx[1]
      
        #Here numpy array does the negative wrapping
        #We need to add the positive.
        update_i[update_i>bottomedge]=0
        update_j[update_j>rightedge]=0
       
        
        #add the proper info to the world
        np.add.at(inputworld, (update_i,update_j),toadd)
        return inputworld

    def evolveCells(inputworld):
        """The method that does the actual evolution.
        Only the non-zero cells i.e alive or alive neighbours
        Need to be checked. Update the cell plus its neighbours"""
        #Live or dead is the 0th bit
        #Since the neighbour info is encoded 
        idx_alive_to_die,idx_dead_to_live=ruleFun(inputworld)
        #Now in the world update the cells to change and the 8 neighbour words
        #All the operations are fixed/encoded at this stage i.e
        #we move all things to the next step
        #we need to add or subtract 2 for each of the 8 neighbours	
        if idx_dead_to_live[0].size !=0 :
            inputworld[idx_dead_to_live] |= 0x01
            inputworld=neighbours(inputworld,idx_dead_to_live,2)
        if idx_alive_to_die[0].size!=0 :
            inputworld[idx_alive_to_die] &= (~0x01) 
            inputworld=neighbours(inputworld,idx_alive_to_die,-2)
        return inputworld

    worldInternal=neighbours(worldInternal,nonZero,2)

    #step using the function set up above
    for _ in xrange(steps):	        
        nextworld=evolveCells(worldInternal)
        #  print "===================================================================="
        # print worldInternal

        worldInternal=nextworld
        if not doWrap:
            worldInternal[0,0:]=0
            worldInternal[0:,0]=0
            worldInternal[0:,rightedge]=0;
            worldInternal[bottomedge,0:]=0;
        out=worldInternal[visBeginR:visEndR,visBeginC:visEndC]&0x01	
        yield out


if __name__ =='__main__':
    animation=True
    world = np.loadtxt('GliderGun.txt')
    if not animation:
        for nextWorld in evolve(world,10000,GameOfLife,False):
            pass
    else:
        #Test the animation 
        import matplotlib
        matplotlib.use('TKAgg')
        import matplotlib.pyplot as plt
        import matplotlib.animation as animation

        def animateGame(world,inFrames,inInterval):
            #get the artist we will need
            fig,ax=plt.subplots()
            im=plt.imshow(world,cmap=plt.cm.binary,interpolation='nearest',animated=True)
            ax.set_yticklabels([])
            ax.set_xticklabels([])
            #Frame Generation 	
            def animationFrames():
                yield world
                for i in evolve(world,inFrames,GameOfLife,False):
                    yield i

            #animate function
            def animate(board):
                im.set_data(board)
                return (im,)

            ani = animation.FuncAnimation(fig, animate, frames=animationFrames,interval=inInterval,blit=True)
            plt.show()

        animateGame(world,2000,30)




