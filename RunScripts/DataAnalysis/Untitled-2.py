# %%
import csv
import numpy as np
import matplotlib.pyplot as plt
import pandas
import os

DATA_PATH = "E:/University/VM - Images/Shared Folder/Results/SiliconScintillator/ions_all"
SAVE_PATH = DATA_PATH + "/outputs/"

SILICON_COLUMN_NAME = ["Number of electron-hole pairs created in Silicon_1", "Number of electron-hole pairs created in Silicon_2"]
SCINT_1_COLUMN_NAME = ["Photons absorbed in Scint_1 Top-Left","Photons absorbed in Scint_1 Bottom-Right","Photons absorbed in Scint_1 Top-Right","Photons absorbed in Scint_1 Bottom-Left"]
SCINT_2_COLUMN_NAME = ["Photons absorbed in Scint_2 Top-Left","Photons absorbed in Scint_2 Bottom-Right","Photons absorbed in Scint_2 Top-Right","Photons absorbed in Scint_2 Bottom-Left"]
SCINT_LST = [SCINT_1_COLUMN_NAME, SCINT_2_COLUMN_NAME]
PARTICLE = ["mu-", "mu+"]

df = pandas.read_csv(DATA_PATH + '/final_results.csv')

PARTICLE = df.Particle.unique()

# %%
particle = "mu+"
df_energy = df.loc[df["Particle"] == particle]
df_energy = df_energy.set_index("Energy")
plot_data = df_energy[SILICON_COLUMN_NAME[1:]].groupby(['Energy']).mean()
plot_data.index = plot_data.index.astype(float)
plot_data = plot_data.sort_index()

# %%
"""
    Silicon-Scintillator grapher - all same folder
"""
for particle in PARTICLE:
    df_energy = df.loc[df["Particle"] == particle]
    df_energy = df_energy.set_index("Energy")

    column_to_choose = SILICON_COLUMN_NAME
    # silicon graphs:
    plt.clf()
    plot_data = df_energy[column_to_choose].groupby(['Energy']).mean()
    plot_data.index = plot_data.index.astype(float)
    plot_data = plot_data.sort_index()
    plt.plot(plot_data)
    plt.xscale("log")
    plt.yscale("log")
    plt.legend(["Silicon_1", "Silicon_2"])
    # plt.legend([column_to_choose[0].split(" ")[-1]])
    plt.xlabel("Energy [MeV]")
    plt.ylabel("Electron-Hole")
    plt.title(f"Silicon e-h generation: \n({particle})")
    plt.savefig(f"{SAVE_PATH}/silicon_{particle}.png")


    for i, scint in enumerate(SCINT_LST, start=1):
        plt.clf()
        plot_data = df_energy[scint].groupby(['Energy']).mean()
        plot_data.index = plot_data.index.astype(float)
        plot_data = plot_data.sort_index()
        plt.plot(plot_data)
        plt.legend(["Top-Left", "Bottom-Right", "Top-Right", "Bottom-Left"])
        plt.xlabel("Energy [MeV]")
        plt.ylabel("Photons absorbed")
        plt.xscale("log")
        plt.title(f"Scintillator {i} photon absorption: \n({particle})")
        plt.savefig(f"{SAVE_PATH}/scint_{i}_{particle}.png")
        plt.plot()

# %%
"""
    Silicon grapher
"""
for particle in PARTICLE:
    path_to_save = SAVE_PATH + f"/{particle}"
    if not os.path.isdir(path_to_save):
        os.mkdir(path_to_save)

    df_energy = df.loc[df["Particle"] == particle]
    df_energy = df_energy.set_index("Energy")

    column_to_choose = SILICON_COLUMN_NAME
    # silicon graphs:
    plt.clf()
    plot_data = df_energy[column_to_choose].groupby(['Energy']).mean()
    plot_data.index = plot_data.index.astype(float)
    plot_data = plot_data.sort_index()
    plt.plot(plot_data)
    plt.xscale("log")
    # plt.yscale("log")
    plt.legend(["Silicon_1", "Silicon_2"])
    # plt.legend([column_to_choose[0].split(" ")[-1]])
    plt.xlabel("Energy [MeV]")
    plt.ylabel("Electron-Hole")
    plt.title(f"Silicon e-h generation: \n({particle})")
    plt.savefig(f"{path_to_save}/silicon_{particle}.png")
# %%
"""
    Scintillator grapher
"""
for particle in PARTICLE:
    path_to_save = SAVE_PATH + f"/{particle}"
    if not os.path.isdir(path_to_save):
        os.mkdir(path_to_save)

    df_energy = df.loc[df["Particle"] == particle]
    df_energy = df_energy.set_index("Energy")
    for i, scint in enumerate(SCINT_LST, start=1):
            plt.clf()
            plot_data = df_energy[scint].groupby(['Energy']).mean()
            plot_data.index = plot_data.index.astype(float)
            plot_data = plot_data.sort_index()
            plt.plot(plot_data)
            plt.legend(["Top-Left", "Bottom-Right", "Top-Right", "Bottom-Left"])
            plt.xlabel("Energy [MeV]")
            plt.ylabel("Photons absorbed")
            plt.xscale("log")
            plt.title(f"Scintillator {i} photon absorption: \n({particle})")
            plt.savefig(f"{path_to_save}/scint_{i}_{particle}.png")
            plt.plot()
# %%
"""
    Silicon Stopping Power!
"""
energy_power = []
for particle in PARTICLE:
    path_to_save = SAVE_PATH + f"/{particle}"
    if not os.path.isdir(path_to_save):
        os.mkdir(path_to_save)

    df_energy = df.loc[df["Particle"] == particle]
    df_energy = df_energy.set_index("Energy")

    column_to_choose = SILICON_COLUMN_NAME[:1]
    # silicon graphs:
    plt.clf()
    plot_data = df_energy[column_to_choose].groupby(['Energy']).mean()
    plot_data.index = plot_data.index.astype(float)
    plot_data = plot_data.sort_index()
    energy_power.append([particle, plot_data.ne(0).idxmax()[0]])
with open(f"{DATA_PATH}/stopping_energy.csv", 'w') as f:
    f.write(pandas.DataFrame(energy_power, columns=['Particle', 'Energy (MeV)']).to_csv(index=False))
# %%
"""
    Silicon Stopping Power!
"""
energy_power_2 = []
for particle in PARTICLE:
    path_to_save = SAVE_PATH + f"/{particle}"
    if not os.path.isdir(path_to_save):
        os.mkdir(path_to_save)

    df_energy = df.loc[df["Particle"] == particle]
    df_energy = df_energy.set_index("Energy")

    for i, scint in enumerate(SCINT_LST[:1], start=1):
        plt.clf()
        plot_data = df_energy[scint].groupby(['Energy']).mean()
        plot_data.index = plot_data.index.astype(float)
        plot_data = plot_data.sort_index()
        # break
        energy_power_2.append([particle, plot_data.mean(axis=1).ne(0).idxmax()])
    # break
with open(f"{DATA_PATH}/stopping_energy_2.csv", 'w') as f:
    f.write(pandas.DataFrame(energy_power_2, columns=['Particle', 'Energy (MeV)']).to_csv(index=False))
# %%
