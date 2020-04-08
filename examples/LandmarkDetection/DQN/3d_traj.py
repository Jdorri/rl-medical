import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

from medical import MedicalPlayer

fig = plt.figure(figsize=(8.0,8.0))
ax = fig.add_subplot(111, projection='3d')

example_traj_x = [210,210,210,210,210,192,192,174,156,174]
example_traj_y = [258,240,240,222,222,202,204,204,204,204]
example_traj_z = [102,102,120,120,138,138,138,138,138,138]

example_target = [182, 204, 138]

ax.plot(example_traj_x,example_traj_y,example_traj_z)
plt.show()

x_traj, y_traj, z_traj = [], [], []
def extract(agent_loc):
    x_traj.append(agent_loc[0])
    y_traj.append(agent_loc[1])
    z_traj.append(agent_loc[2])
    return (x_traj,y_traj,z_traj)

for x,y,z in zip(example_traj_x,example_traj_y,example_traj_z):
    hist = extract((x,y,z))

print(hist)
