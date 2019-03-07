import numpy as np
X = np.int8(np.zeros((200, 200)))

X[99,100:102]=1
X[100,99:101]=1
X[101,100]=1
np.savetxt("R-Pantomino.txt",X,fmt='%d')
