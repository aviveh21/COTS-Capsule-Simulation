#!/usr/bin/python3

import os
import sys
import csv
import json
import re

MOTHER_FOLDER = "/runs/"
INPUT_FILE_NAME = "input.txt"
OUTPUT_FILE_NAME = "/output" # should match what geant4 expects

def load_json(path):
    def_data = {"energies": [0.50, 0.64, 0.82, 1.06, 1.35, 1.74, 2.23, 2.86, 3.67, 4.71, 6.04, 7.74, 9.94, 12.75, 16.35, 20.98, 26.91, 34.52, 44.29, 56.82, 72.89, 93.51, 119.96, 153.89, 197.42, 253.27, 324.91, 416.82, 534.72, 685.98, 880.03, 1128.97, 1448.33, 1858.02, 2383.61, 3057.88, 3922.87, 5032.56, 6456.14, 8282.42, 10625.31, 13630.94, 17486.79, 22433.36, 28779.19, 36920.10, 47363.87, 60761.91, 77949.93, 100000.00]  # in MeV
                , "positions": [(0, 0, -4)], "directions": [(0, 0, 1)], "beamOn": 10}
    expected_data = ["energies", "positions", "directions", "particles", "ions", "beamOn"]
    with open(path, 'r') as f:
        json_data = json.load(f)

    for d in expected_data:
        if d not in json_data.keys():
            if d in def_data.keys():
                print(f"{d} field is missing, using default:\n \t{def_data[d]}")
                json_data[d] = def_data[d]
            else:
                print(f"{d} field is missing, this is a requied field, aborting...")
                return []
    
    def assert_number(num, types):
        return any([type(num) == t for t in types])

    for data in ["positions", "directions", "ions"]:
        fixed = []
        types = [int] if data == "ions" else [int, float]
        for pos in json_data[data]:
            assert len(pos) == 3, f"'{data}': type must be of length 3"
            assert assert_number(pos[0], types) and assert_number(pos[1], types) and assert_number(pos[2], types), f"'{data}': type must be of: {types}"
            fixed.append(tuple(pos))
        json_data[data] = fixed
        del fixed

    assert type(json_data["beamOn"]) == int, f"'beamOn': type must be of {[int]}"
    assert all([assert_number(d, [int, float]) for d in json_data["energies"]]), f"'energies': type must be of {[int, float]}"
    
    return json_data


def make_dir(path):
    try:
        os.mkdir(path)
    except FileExistsError:
        pass

def vec_to_str(in_str):
    return "{} {} {}".format(*in_str)

def particle_name(particle, ion):
    if particle != "ion":
        return particle
    return "{} - {}".format(particle, ion)


def create_input_file(filepath, particle: str, ion: str, energy: str,
                      direction: str, position: str, beamOn: int, position_unit: str = "cm", energy_unit: str = "MeV"):
    with open(filepath + "/" + INPUT_FILE_NAME, 'w') as f:
        f.write("/run/initialize\n")
        f.write("/gun/particle {}\n".format(particle))
        if particle == "ion":
            f.write("/gun/ion {}\n".format(ion))
        f.write("/gun/energy {} {}\n".format(energy, energy_unit))
        f.write("/gun/position {} {}\n".format(position, position_unit))  # 0 0 0 m (x,y,z, unit)
        f.write("/gun/direction {}\n".format(direction)) # 0 0 0
        for _ in range(beamOn):
            f.write("/run/beamOn 1\n")
        make_dir(filepath + OUTPUT_FILE_NAME)

#Aviv changed 01/07/22, to handle bunch of jsons
#def create_runs(input_data):
def create_runs(input_data,json_number):
    energies = input_data["energies"]
    positions = input_data["positions"]
    directions = input_data["directions"]
    particles = input_data["particles"]
    ions = input_data["ions"]
    beamOn = input_data["beamOn"]
    file = open("mapping.csv", 'a', newline='')
    if os.stat("mapping.csv").st_size == 0:
        file.close()
        with open("mapping.csv", 'w', newline='') as map_file:
            run_writer = csv.writer(map_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            run_writer.writerow(['Folder Number', 'Particle', 'Energy', 'Position[X]','Position[Y]','Position[Z]', 'Direction[X]','Direction[Y]','Direction[Z]'])

            i = 0

            for particle in particles:
                #subfolder_subname = MOTHER_FOLDER + particle + str(int(json_number)) + "/"
                subfolder_subname = MOTHER_FOLDER + particle + "/"
                make_dir(subfolder_subname)
                ions_lst = [(0, 0, 0)]
                if particle == "ion":
                    ions_lst = ions
                for ion in ions_lst:
                    for energy in energies:
                        for pos in positions:
                            # 03/12/22 Aviv's edit, to split "pos" and "direct" to 3 columns each, one for each dimension
                            #xdim_pos = float(re.search('[(](.*?)[,]' , pos).group(1))
                            #ydim_pos = float(re.search('[,](.*?)[,]' , pos).group(1))
                            #zdim_pos = float(re.search('[)](.*?)[,]' , pos[::-1]).group(1)[::-1])
                            xdim_pos = float(pos[0])
                            ydim_pos = float(pos[1])
                            zdim_pos = float(pos[2])
                            for direct in directions:
                                #xdim_direct = float(re.search('[(](.*?)[,]' , direct).group(1))
                                #ydim_direct = float(re.search('[,](.*?)[,]' , direct).group(1))
                                #zdim_direct = float(re.search('[)](.*?)[,]' , direct[::-1]).group(1)[::-1])
                                xdim_direct = float(direct[0])
                                ydim_direct = float(direct[1])
                                zdim_direct = float(direct[2])
                                i+=1
                                if json_number != 0:
                                    # 03/12/22 Aviv's edit, to split "pos" and "direct" to 3 columns each, one for each dimension
                                    #run_writer.writerow([str(int(json_number)), particle_name(particle, ion), energy, pos, direct])
                                    run_writer.writerow([str(int(json_number)), particle_name(particle, ion), energy, xdim_pos, ydim_pos,zdim_pos, xdim_direct, ydim_direct, zdim_direct])
                                    #Aviv changed 01/07/22, to handle bunch of jsons
                                    #subfolder_name = subfolder_subname + str(i)
                                    subfolder_name = subfolder_subname + str(int(json_number))
                                else:
                                    # 03/12/22 Aviv's edit, to split "pos" and "direct" to 3 columns each, one for each dimension
                                    #run_writer.writerow([i, particle_name(particle, ion), energy, pos, direct])
                                    run_writer.writerow([i, particle_name(particle, ion), energy, xdim_pos, ydim_pos,zdim_pos, xdim_direct, ydim_direct, zdim_direct])
                                    subfolder_name = subfolder_subname + str(i)

                                make_dir(subfolder_name)
                                create_input_file(subfolder_name, particle, vec_to_str(ion), str(energy), vec_to_str(direct), vec_to_str(pos), beamOn)
    else:
        file.close()
        with open("mapping.csv", 'a+', newline='') as map_file:
            run_writer = csv.writer(map_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            #run_writer.writerow(['Folder Number', 'Particle', 'Energy', 'Position', 'Direction'])

            i = 0

            for particle in particles:
                #subfolder_subname = MOTHER_FOLDER + particle + str(int(json_number)) + "/"
                subfolder_subname = MOTHER_FOLDER + particle + "/"
                make_dir(subfolder_subname)
                ions_lst = [(0, 0, 0)]
                if particle == "ion":
                    ions_lst = ions
                for ion in ions_lst:
                    for energy in energies:
                        # 03/12/22 Aviv's edit, to split "pos" and "direct" to 3 columns each, one for each dimension
                        for pos in positions:
                            #xdim_pos = float(re.search('[(](.*?)[,]' , pos).group(1))
                            #ydim_pos = float(re.search('[,](.*?)[,]' , pos).group(1))
                            #zdim_pos = float(re.search('[)](.*?)[,]' , pos[::-1]).group(1)[::-1])
                            xdim_pos = float(pos[0])
                            ydim_pos = float(pos[1])
                            zdim_pos = float(pos[2])
                            for direct in directions:
                                #xdim_direct = float(re.search('[(](.*?)[,]' , direct).group(1))
                                #ydim_direct = float(re.search('[,](.*?)[,]' , direct).group(1))
                                #zdim_direct = float(re.search('[)](.*?)[,]' , direct[::-1]).group(1)[::-1])
                                xdim_direct = float(direct[0])
                                ydim_direct = float(direct[1])
                                zdim_direct = float(direct[2])
                                i+=1
                                if json_number != 0:
                                    # 03/12/22 Aviv's edit, to split "pos" and "direct" to 3 columns each, one for each dimension
                                    #run_writer.writerow([str(int(json_number)), particle_name(particle, ion), energy, pos, direct])
                                    run_writer.writerow([str(int(json_number)), particle_name(particle, ion), energy, xdim_pos, ydim_pos,zdim_pos, xdim_direct, ydim_direct, zdim_direct])
                                    #Aviv changed 01/07/22, to handle bunch of jsons
                                    #subfolder_name = subfolder_subname + str(i)
                                    subfolder_name = subfolder_subname + str(int(json_number))
                                else:
                                    # 03/12/22 Aviv's edit, to split "pos" and "direct" to 3 columns each, one for each dimension
                                    #run_writer.writerow([i, particle_name(particle, ion), energy, pos, direct])
                                    run_writer.writerow([i, particle_name(particle, ion), energy, xdim_pos, ydim_pos,zdim_pos, xdim_direct, ydim_direct, zdim_direct])
                                    subfolder_name = subfolder_subname + str(i)
                                make_dir(subfolder_name)
                                create_input_file(subfolder_name, particle, vec_to_str(ion), str(energy), vec_to_str(direct), vec_to_str(pos), beamOn)

if __name__=="__main__":
    try:
        save_path = sys.argv[1]
        json_path = sys.argv[2]
        #Aviv added new argument 01/07/22, to handle bunch of jsons
        json_number = sys.argv[3]
    except IndexError:
        print("Error parsing args: make_data.py [save_path] [input_json_path] [json_number]")
        exit(1)
    
    if os.path.exists(json_path):
        json_data = load_json(json_path)
    else:
        print(f"Missing json data, tried path: {json_path}")
        exit(1)
    
    if os.path.exists(save_path):
        # Save_pass is relative to working_dir. Do not play with this shit!
#        os.chdir(save_path)
        MOTHER_FOLDER = save_path + MOTHER_FOLDER
    else:
        exit(1)

    make_dir(MOTHER_FOLDER)
    #Aviv changed 01/07/22, to handle bunch of jsons
    #create_runs(json_data)
    create_runs(json_data,json_number)
