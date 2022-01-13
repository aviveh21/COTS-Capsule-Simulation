
"""
Calc pmt's locations
"""
# %%
# imports
from matplotlib.colors import Colormap
import numpy as np
import pandas
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import math
import csv

# %%
# def's
SCINT_SIDE = 7  # (mm)
PMT_DIST_FROM_CORNER = 0.64/2  # (mm)

PMT_SIDE = PMT_DIST_FROM_CORNER * 2  # (mm)
PMT_HALF_DIAG = PMT_DIST_FROM_CORNER * math.sqrt(2)

LOCS = np.array([[i, j] for i in range(-30, 31, 2) for j in range(-30, 31, 2)])

DIFF = SCINT_SIDE - PMT_HALF_DIAG*2
PMT_LOCS = np.array([[[i*SCINT_SIDE, j*DIFF], [i*DIFF, j*SCINT_SIDE]]
                     for i in [-1, 1] for j in [-1, 1]])/2.

DEG_SNELL = 30 # (deg)
# %%

loc_with_sum_angles = np.zeros((LOCS.shape[0], LOCS.shape[1] + 1))
loc_with_sum_angles[:, :-1] = LOCS * 0.1


def calc_sum_angles(loc):
    theta_sum = 0
    for pmt in PMT_LOCS:
        loc = loc[:2]  # first 2 elements, point x-y, in mm
        a = np.sqrt(np.sum((loc-pmt[0])**2))
        b = np.sqrt(np.sum((loc-pmt[1])**2))
        c = PMT_SIDE
        theta_sum += math.acos(-(c**2 - a**2 - b**2) /
                               (2*a*b)) * 360/(2*math.pi)  # in deg
    return theta_sum


for line in loc_with_sum_angles:
    line[2] = calc_sum_angles(line)
loc_with_sum_angles
# %%
# plot shooting points with pmt locations
shoot_points = [loc_with_sum_angles[:, 0], loc_with_sum_angles[:, 1]]
pmt_points = [PMT_LOCS.reshape((8, 2))[:, 0], PMT_LOCS.reshape((8, 2))[:, 1]]
plt.scatter(*shoot_points, c=loc_with_sum_angles[:, 2], vmax=40)
for pmt in PMT_LOCS:
    plt.plot(pmt[:, 0], pmt[:, 1], c="Orange")
plt.plot([SCINT_SIDE/2, SCINT_SIDE/2], [SCINT_SIDE/2, -SCINT_SIDE/2], c="Black")
plt.plot([SCINT_SIDE/2, -SCINT_SIDE/2], [SCINT_SIDE/2, SCINT_SIDE/2], c="Black")
plt.plot([SCINT_SIDE/2, -SCINT_SIDE/2], [-SCINT_SIDE/2, -SCINT_SIDE/2], c="Black")
plt.plot([-SCINT_SIDE/2, -SCINT_SIDE/2], [SCINT_SIDE/2, -SCINT_SIDE/2], c="Black")
plt.xlabel("x (cm)")
plt.ylabel("y (cm)")
plt.gca().set_aspect('equal', adjustable='box')
plt.colorbar()
plt.show(block=False)
# %%
fig = plt.figure()
ax = Axes3D(fig)

ax.scatter(loc_with_sum_angles[:, 0],
           loc_with_sum_angles[:, 1], loc_with_sum_angles[:, 2])
plt.show(block=False)
# %%
df = pandas.read_csv(
    "E:/University/VM - Images/Shared Folder/Results/SiliconScintillator/ions_all/ions_scint_first/final_results_scint.csv")
pos = df["Position"].to_numpy()
for i in range(len(pos)):
    temp = eval(pos[i])
    pos[i] = temp

df["Position"] = pos
df_position = df.set_index("Position")
df_position = df_position[["Photons absorbed in Scint_1 Top-Left", "Photons absorbed in Scint_1 Bottom-Right",
                           "Photons absorbed in Scint_1 Top-Right", "Photons absorbed in Scint_1 Bottom-Left"]].groupby(['Position']).mean()
sum_of_stuff = np.expand_dims(df_position.sum(axis=1).to_numpy(), 1)

df_position = df.set_index("Position")
df_position = df_position[["Number of photons created"]].groupby(['Position']).mean()
all_data = np.concatenate([loc_with_sum_angles, sum_of_stuff, df_position.to_numpy()], axis=1)
del df, df_position, pos, sum_of_stuff

# all_data:
# x, y, degrees, total_pmt, total_created 

# %%
photons_avg = all_data[:, 3]/all_data[:, 2]
print(f"Photons per 1-deg: {np.mean(photons_avg)} +- {np.std(photons_avg)}") 
photons_total = photons_avg * 360
print(f"Photons total(by relative deg): {np.mean(photons_total)} +- {np.std(photons_total)}") 
del photons_avg, photons_total
# %%
beta = 2*(-math.cos(DEG_SNELL*math.pi/360) + 1)
total_created_measured = np.expand_dims((all_data[:, 3] / all_data[:, 2]) * (360 / (1 - beta)), 1)
all_data = np.concatenate([all_data, total_created_measured], axis=1)
# all_data:
# x, y, degrees, total_pmt, total_created, total_created_measured
# %%
# save to csv
# with open("./results_2.csv", "w", newline='') as f:
#     field_names = ["x", "y", "degrees", "total_pmt", "total_created", "total_created_measured"]
#     writer = csv.writer(f, delimiter=',', quotechar='"',
#                             quoting=csv.QUOTE_MINIMAL)
#     writer.writerow(field_names)
#     writer.writerows(all_data)

# %%
fig = plt.figure()
ax = Axes3D(fig)
diff = np.abs(all_data[:, -2] - all_data[:, -1])
# ax.plot(all_data[:, 0],
#            all_data[:, 1], diff, c=np.max(diff)-diff, cmap='inferno', s=200)
ax.plot_trisurf(all_data[:, 0],
           all_data[:, 1], diff, cmap='inferno', vmax=300)
ax.set_zlabel("Error (|Estimated - Expected|)")
ax.set_xlabel("x (cm)")
ax.set_ylabel("y (cm)")

plt.show()
# %%
print(f"Measurement error: {np.mean(diff)} +- {np.std(diff)}") 
print(f"Measurement error percentage: {(np.mean(diff) / np.mean(all_data[:, -2]))*100}%")
# %%
