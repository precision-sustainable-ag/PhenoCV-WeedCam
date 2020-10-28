import numpy  as np
import pandas as pd
import os
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import seaborn as sns
from scipy import stats 
# from sklearn import mean_squared_error
sns.set(color_codes=True)

for _,_,files in os.walk('/home/sardesaim/depthai-tutorials-practice/4-spatialnoise/Frames/', topdown=True):
    f = files

frames = []
for frame in f: 
    frames.append(np.load('/home/sardesaim/depthai-tutorials-practice/4-spatialnoise/Frames/'+frame))

xyz=[]

for i in range(frames[0].shape[0]):
    for j in range(frames[0].shape[1]):
        xyz.append((i,j,frames[0][i][j]))

print(np.array(xyz)[:,:2].shape)
xyz=np.array(xyz)
df=pd.DataFrame(xyz, columns=['x','y','z'])
print(df.tail())
dropz=df.index[df['z']==0].tolist()
dropi=df.index[df['z']==65535].tolist()
c=dropz+dropi
df=df.drop(df.index[c])
print(df.shape)
df_o = df[df['z'] < df['z'].quantile(.90)]
print(df_o.shape)

xyz=df_o.to_numpy()
plt.figure()
ax = plt.subplot(111, projection='3d')
ax.scatter(xyz[:,0], xyz[:,1], xyz[:,2], color='b')

A = np.matrix(np.c_[xyz[:,0], xyz[:,1], np.ones(xyz.shape[0])])
b = np.matrix(xyz[:,2]).T
fit = (A.T * A).I * A.T * b
errors = b - A * fit
residual = np.linalg.norm(errors)

print("solution:")
print("%f x + %f y + %f = z" % (fit[0], fit[1], fit[2]))
print("errors:")
print(errors)
print("residual:")
print(residual)
print("rmse")
print(np.sqrt((np.multiply(np.array(errors), np.array(errors))).mean()))

# plot plane
xlim = ax.get_xlim()
ylim = ax.get_ylim()
X,Y = np.meshgrid(np.arange(xlim[0], xlim[1]),
                  np.arange(ylim[0], ylim[1]))
Z = np.zeros(X.shape)
for r in range(X.shape[0]):
    for c in range(X.shape[1]):
        Z[r,c] = fit[0] * X[r,c] + fit[1] * Y[r,c] + fit[2]
ax.plot_wireframe(X,Y,Z, color='k')
ax.set_xlabel('x')
ax.set_ylabel('y')
ax.set_zlabel('z')
plt.show()