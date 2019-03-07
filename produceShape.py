import numpy as np
X = np.int8(np.zeros((256, 256)))

X[127,128:130]=1
X[128,127:129]=1
X[129,128]=1
np.savetxt("R-Pantomino.txt",X,fmt='%d')
