import numpy as np
X = np.int8(np.zeros((100, 180)))

X[49,90:92]=1
X[50,89:91]=1
X[51,90]=1
np.savetxt("R-Pantomino.txt",X,fmt='%d')
