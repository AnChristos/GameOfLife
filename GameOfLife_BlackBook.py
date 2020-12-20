import numpy as np
# There are more Pythonic solutions

# Here I tried to replicate the logic from
# https://www.phatcode.net/res/224/files/html/ch17/17-06.html#Heading8
# Quite  a bit is still lost to the numpy translation.

# Each cell keeps track of his status and of the status of his 8 neighbours.
# It encodes the following :
# Bit(s)
# 0  : Live or dead . So 0 or 1
# 1-4: +=2 for each alive neighbour (so values can be 0-16)
# 5-7: Not used
# Examples:
# Alive cell with 0 alive neighbours is (int)(1).
# Alive cell with 2 live neighbours is (int)(5).
# Dead cell with 3 alive neighbours is (int)(6).
# Alive cell with 3 alive neighbours is (int)(7).

# This way we can check a cell without touching its neighbours.
# - So first see which cells need to change status and change them
# - Then notify the 8 neighbours of the cells that changed status

# Currently, parts of the scanning happen twice,
# ideally one would like to do them in the same
# pass (could do it in C/C++ or without numpy)

# The original had only wrapping for the edges. Here we create a zone
# of 3 cells at each side to avoid some of the artifacts in the boundaries.
# More or less we do not want to touch things that have visible neighbours
# so we need a bit of buffer space .


# Rule functions
def GameOfLife(world):
    ''' Game of Life rules.Inputs : world.
        Returns a tuple with the indices of the cells that change status,
        in the form (idx_alive_to_die,idx_dead_to_live)'''
    # if it is alive and does not have 2 or 3 neighbours it must die.
    # if it is dead and has 3 neighbours it becomes alive
    return (np.nonzero(np.logical_and(np.bitwise_and(world, 1),
                                      np.logical_and(world != 5, world != 7))),
            np.nonzero(world == 6))


def HighLife(world):
    ''' HighLife rules: Input world.
        Returns a tuple with the indices of the cells that change status,
        in the form (idx_alive_to_die,idx_dead_to_live)'''
    # if it is alive and does not have 2 or 3 neighbours it must die
    # if it is dead and has 3 or 6 neighbours it becomes alive
    return (np.nonzero(np.logical_and(np.bitwise_and(world, 1),
                                      np.logical_and(world != 5, world != 7))),
            np.nonzero(np.logical_or(world == 6, world == 12)))


class ConwayGame:
    '''Class representing a world evolving with certain
    rules using a specific geometry'''

    def __init__(self, world, ruleFun=GameOfLife, doWrap=False):
        ''' Constructor, input world, function for the rules ,
        wrap or not wrap the world'''
        # [i-1,j-1], [i-1,j], [i-1,j+1]
        # [i,j-1 ] ,  ----  , [i,j+1]
        # [i+1,j-1]  [i+1,j]   [i+1,j+1]
        self.relative_i = np.array(
            [-1, -1, -1, 0, 0, 1, 1, 1], dtype=np.int8)[np.newaxis].T
        self.relative_j = np.array(
            [-1, 0, 1, -1, 1, -1, 0, 1], dtype=np.int8)[np.newaxis].T
        # The rules
        self.ruleFun = ruleFun
        self.doWrap = doWrap

        # To wrap or not to wrap
        rows, cols = world.shape
        self.visBeginR = 3
        self.visEndR = rows+3
        self.sizeR = rows+6
        self.visBeginC = 3
        self.visEndC = cols+3
        self.sizeC = cols+6
        if doWrap:
            self.visBeginR = 0
            self.visEndR = rows
            self.sizeR = rows
            self.visBeginC = 0
            self.visEndC = cols
            self.sizeC = cols

        self.bottomedge = self.sizeR-1
        self.rightedge = self.sizeC-1

        # internal world
        # we can can use the internal convention
        # and also avoid the wrapping
        self.worldInternal = np.zeros((self.sizeR, self.sizeC))
        self.worldInternal[self.visBeginR:self.visEndR,
                           self.visBeginC:self.visEndC] = world
        self.worldInternal = np.array(self.worldInternal, dtype=np.int8)

        self.neighbours(self.worldInternal.nonzero(), 2)

    def neighbours(self, updateIdx, toadd):
        """Returns the indices of the 8 Neighbours of cell(i,j)
        Wraps around the right/bottom edge of the world.
        The left/up is covered by the numpy conventions"""
        # update_i/j are (8 rows, 1 column)
        # updateIdx[0/1] are (1 row, N columns
        # where N depends on the indices to update)
        # At the end we have 2 matrices with the indexes
        # of the neighbours to update
        update_i = self.relative_i+updateIdx[0]
        update_j = self.relative_j+updateIdx[1]
        # Here numpy array does the negative wrapping
        # We need to add the positive.
        update_i[update_i > self.bottomedge] = 0
        update_j[update_j > self.rightedge] = 0

        # add the proper info to the world
        np.add.at(self.worldInternal, (update_i, update_j), toadd)
        pass

    def evolveCells(self):
        '''The method that does the actual evolution.
        Only the non-zero cells i.e alive or alive neighbours
        Need to be checked. Update the cell plus its neighbours'''
        # Live or dead is the 0th bit
        # Since the neighbour info is encoded
        idx_alive_to_die, idx_dead_to_live = self.ruleFun(self.worldInternal)
        # Now in the world update the cells to change and the 8 neighbour words
        # All the operations are fixed/encoded at this stage i.e
        # we move all things to the next step
        # we need to add or subtract 2 to each of the 8 neighbours
        if idx_dead_to_live[0].size != 0:
            self.worldInternal[idx_dead_to_live] += 1
            self.neighbours(idx_dead_to_live, 2)
        if idx_alive_to_die[0].size != 0:
            self.worldInternal[idx_alive_to_die] -= 1
            self.neighbours(idx_alive_to_die, -2)

        if not self.doWrap:
            self.worldInternal[0, 0:] = 0
            self.worldInternal[0:, 0] = 0
            self.worldInternal[0:, self.rightedge] = 0
            self.worldInternal[self.bottomedge, 0:] = 0
        pass

    def getCurrent(self):
        """Returns the current world"""
        return self.worldInternal[self.visBeginR:self.visEndR,
                                  self.visBeginC:self.visEndC] & 0x01


def animateGame(inFrames, inInterval, ConwayGame):
    '''Produce an animation of size inFrames,
    with interval between frames inInterval
    given a ConwayGame class instance'''
    fig, ax = plt.subplots()
    im = plt.imshow(ConwayGame.getCurrent(), cmap=plt.cm.binary,
                    interpolation='nearest', animated=True)
    ax.set_yticklabels([])
    ax.set_xticklabels([])
    # animate function

    def animate(frame):
        ConwayGame.evolveCells()
        newWorld = ConwayGame.getCurrent()
        im.set_data(newWorld)
        return (im,)

    animation.FuncAnimation(fig, animate, frames=inFrames,
                            interval=inInterval, blit=True)
    plt.show()


if __name__ == '__main__':
    world = np.loadtxt('R-Pantomino.txt', dtype=np.int8)
    game = ConwayGame(world, GameOfLife, False)
    # Test the animation
    import matplotlib
    matplotlib.use('MacOSX')
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation

    animateGame(2000, 30, game)
