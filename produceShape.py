import numpy as np
X = np.int8(np.zeros((70, 70)))

#X[49,90:92]=1
#X[50,89:91]=1
#X[51,90]=1
#np.savetxt("R-Pantomino.txt",X,fmt='%d')

r_pantomino=np.array([
    [0,1,1],
    [1,1,0],
    [0,1,0]])

#X[37:40,58:61]=r_pantomino
#np.savetxt("R-Pantomino.txt",X,fmt='%d')

#die_hard = np.array([
#    [0,0,0,0,0,0,1,0],
#    [1,1,0,0,0,0,0,0],
#    [0,1,0,0,0,1,1,1]])
#X[17:20,20:28]=die_hard
#np.savetxt("Die-Hard.txt",X,fmt='%d')

pi_heptomino=np.array([[1,1,1],
    [1,0,1],
    [1,0,1]])

X[32:35,32:35]=pi_heptomino
np.savetxt("Pi-Heptomino.txt",X,fmt='%d')
