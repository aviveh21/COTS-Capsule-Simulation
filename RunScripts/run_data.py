import os
import sys
import subprocess
import re
import csv
import pathlib
import time
import argparse
from typing import Pattern

MOTHER_FOLDER = '/runs/'
INPUT_FILE_NAME = 'input.txt'
OUTPUT_FILE_NAME = 'test.txt'
GEANT_EXE_LOCATION = '/home/aviveh/Code/new_detector/build/Sim'
RUN_BEAM_ON = 100

COUNT_TIME = True

NUMBER_OF_SLABS = 4


def make_dir(path):
    try:
        os.mkdir(path)
    except FileExistsError:
        pass


def get_locations(content, i, res):
    global NUMBER_OF_SLABS
    old_len = len(res)
    while i < len(content):
        i += 1
        if "Enter Location" in content[i]: # or "Exit Location" in content[i]:
            if NUMBER_OF_SLABS == 0:
                continue
            res.append(content[i][16:])
            NUMBER_OF_SLABS -= 1
        elif "Number of" in content[i]:
            break
    # if len(res) < old_len + 2:  # in case the particle stopped in this slab
    #     res.append('None')
    return i


def add_missing_slabs(res):
    global NUMBER_OF_SLABS
    while NUMBER_OF_SLABS > 0:
        res.append('None') # enter
        # res.append('None') # exit
        NUMBER_OF_SLABS -= 1


def get_particle_count(line, loc):
    lst_nums = re.findall(r"[-+]?\d*\.\d+|\d+", line)
    return lst_nums[loc]


def get_scientific_number(line):
    match_number = re.compile(r"-?[0-9]+\.?[0-9]*(?:[Ee][-+]?[0-9]+)?")
    final_list = [float(x) for x in re.findall(match_number, line)]
    return final_list[0]


def init_number_of_slabs():
    global NUMBER_OF_SLABS
    NUMBER_OF_SLABS = 4


def get_run_data(run_dir):
    output_res = list()
    for beam_idx in range(RUN_BEAM_ON):
        res = list()
        try:
            with open("{}/output/{}.txt".format(run_dir, beam_idx), 'r') as output_file:
                file_lines = output_file.readlines()
                content = [line.rstrip('\n') for line in file_lines]
        except FileNotFoundError:
            continue
        i = 0
        while i < len(content):
            # Getting locations
            if "Particle Volume" in content[i]:
                i = get_locations(content, i, res)
                continue
            # Check if there are untouchable slabs
            add_missing_slabs(res)
            if "Number of scintillation photons per event :" in content[i]:
                # print("Number of hits per event:")
                res.append(get_scientific_number(content[i]))
            elif "Silicon slab no." in content[i]:
                # print("Silicon slab no.")
                res.append(get_particle_count(content[i], 1))
            elif "Scintillator" in content[i]:
                # print("Scintillator")
                res.append(get_particle_count(content[i], 2))
            i += 1
        init_number_of_slabs()
        output_res.append(res)
    return output_res


def get_run_number(run_dir):
    path = pathlib.PurePath(run_dir)
    # print(path.name)
    return int(path.name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-run", action='store_true')
    parser.add_argument("-parse", action='store_true')
    parser.add_argument("-dir", default='.')
    args = parser.parse_args()

    save_path = args.dir
    if os.path.exists(save_path):
        os.chdir(save_path)
        save_path = str(pathlib.Path().absolute())
        MOTHER_FOLDER = save_path + MOTHER_FOLDER
    else:
        print(f"Directory {save_path} does not exists!")
        exit(1)

    if (args.run and args.parse) or (not args.run and not args.parse):
        print("Choose one of -run/-parse arguments!")
        exit(1)


    # start_time = time.time() # timestamp before run
    simulation_data = dict()
    for run_dir, _, filename in os.walk(os.getcwd()):
        if INPUT_FILE_NAME in filename:
            os.chdir(run_dir)
            if args.run:
                with open("run_stdout.txt", 'w') as out_fd:
                    subprocess.run([GEANT_EXE_LOCATION, INPUT_FILE_NAME], stdout=out_fd)
            elif args.parse:
                run_number = get_run_number(run_dir)
                simulation_data[run_number] = get_run_data(run_dir)
            # print('Debug: extracted the following data: \n {}'.format(simulation_data[run_number]))

    if args.run:
        exit(0)
    # end_time = time.time() # timestamp after run

    os.chdir(save_path)  # return to script folder

    with open("{}/mapping.csv".format(save_path),'r') as csvinput:
        with open("{}/final_results.csv".format(save_path), 'w') as csvoutput:
            writer = csv.writer(csvoutput, lineterminator='\n')
            reader = csv.reader(csvinput)

            output_lines = []
            row = next(reader)
            row.extend(['Run number'])
            row.extend(['Silicon_2 enter location', 'Silicon_1 enter location'])
            row.extend(['Scint_1 enter location', 'Scint_2 enter location', 'Number of photons created'])
            row.extend(['Number of electron-hole pairs created in Silicon_1', 'Number of electron-hole pairs created in Silicon_2'])
            row.extend(['Photons absorbed in Scint_1 Top-Left', 'Photons absorbed in Scint_1 Bottom-Right', 'Photons absorbed in Scint_1 Top-Right', 'Photons absorbed in Scint_1 Bottom-Left'])
            row.extend(['Photons absorbed in Scint_2 Top-Left', 'Photons absorbed in Scint_2 Bottom-Right', 'Photons absorbed in Scint_2 Top-Right', 'Photons absorbed in Scint_2 Bottom-Left'])

            output_lines.append(row)
            for run_number, row in enumerate(reader):
                actual_run_number = run_number + 1
                if actual_run_number in simulation_data:
                    for beam_counter, run in enumerate(simulation_data[actual_run_number]):
                        row_to_append = row + [beam_counter + 1] + run
                        output_lines.append(row_to_append)
                else:
                    print('Can\'t find output data for run number: {}'.format(actual_run_number))
                    output_lines.append(row)

            number_of_runs = len(output_lines) - 1

            # output_lines.append(["Total time for simulation: ", end_time - start_time, " (seconds)"])
            output_lines.append(["Total runs: ", number_of_runs])
            writer.writerows(output_lines)

    # print("Current run took")

