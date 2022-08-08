import os
import sys
import subprocess
import re
import csv
import pathlib
import time
import argparse
import queue
from typing import Pattern
from thread_worker import Workers

MOTHER_FOLDER = '/runs/'
INPUT_FILE_NAME = 'input.txt'
OUTPUT_FILE_NAME = 'test.txt'
GEANT_EXE_LOCATION = '/home/aviveh/Code/new_detector/build/Sim'
RUN_BEAM_ON = 2000

COUNT_TIME = True

NUMBER_OF_SLABS = 5
start = time.time()

total_time=0

def make_dir(path):
    try:
        os.mkdir(path)
    except FileExistsError:
        pass

# Aviv edit 15/07/22 - to solve bug of unordered hits in the scints 
def get_locations(content, i, res, detector_size, scintilator_size , scint_1_center):
    global NUMBER_OF_SLABS
    const_slabs = NUMBER_OF_SLABS
    scint_zdim = [[] for j in range(const_slabs)]
    enter_ordered = ['None']* const_slabs
    for j in range(const_slabs):
        scint_zdim[j]= [scint_1_center-scintilator_size/2 + detector_size*j, scint_1_center+scintilator_size/2 + detector_size*j]
    #old_len = len(res)
    while i < len(content):
        i += 1
        if "Enter Location" in content[i]: # or "Exit Location" in content[i]:
            if NUMBER_OF_SLABS == 0:
                continue
            # searching for the z-axis element, and than reversing the string so we find only the z-dim between the ',' and the ')', as there is another ',' before the first one
            zdim_enter = re.search('\)(.*?)\,', content[i][16:][::-1]).group(1)[::-1]
            for j in range(const_slabs):
                if float(zdim_enter)/10 <= (float(scint_zdim[j][1])+0.2) and float(zdim_enter)/10 >= (float(scint_zdim[j][0])-0.2):
                    enter_ordered[j] = content[i][16:]
            #res.append(content[i][16:])
            NUMBER_OF_SLABS -= 1
        elif "Number of" in content[i]:
            #for j in range(const_slabs):
            #    if  not enter_ordered[j]:
            #        enter_ordered[j] = 'None'
            break
    for j in range(const_slabs):
        res.append(enter_ordered[j]) # MAYBE I need to loop on all the 5 options in enter_ordered
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

# 09/07/22 Aviv changed to support changes in number of slabs
#def init_number_of_slabs():
def init_number_of_slabs(number_of_slabs):
    global NUMBER_OF_SLABS
    #NUMBER_OF_SLABS = 5
    NUMBER_OF_SLABS = number_of_slabs


def get_run_data(run_dir,numofscints, detector_size, scintilator_size , scint_1_center):
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
                i = get_locations(content, i, res, detector_size, scintilator_size , scint_1_center)
                continue
            elif "Number of hits per event:	 0" in content[i]:
                # Check if there are untouchable slabs
                add_missing_slabs(res)

            if "Number of scintillation photons per event :" in content[i]:
                # print("Number of hits per event:")
                res.append(get_scientific_number(content[i]))
            #elif "Silicon slab no." in content[i]:
                # print("Silicon slab no.")
            #    res.append(get_particle_count(content[i], 1))
            elif "Scintillator" in content[i]:
                # print("Scintillator")
                res.append(get_particle_count(content[i], 2))
            i += 1
        # 09/07/22 Aviv changed to support changes in number of slabs
        #init_number_of_slabs()
        init_number_of_slabs(numofscints)
        output_res.append(res)
    return output_res


def get_run_number(run_dir):
    path = pathlib.PurePath(run_dir)
    # print(path.name)
    return int(path.name)

def worker_func(run_dir):
    # os.chdir(run_dir)
    with open(f"{run_dir}/run_stdout.txt", 'w') as out_fd:
        subprocess.run(f"cd {run_dir} && {GEANT_EXE_LOCATION} {INPUT_FILE_NAME}", stdout=out_fd, shell=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-run", action='store_true')
    parser.add_argument("-parse", action='store_true')
    parser.add_argument("-dir", default='.')
    parser.add_argument("-j", default=1, type=int)
    # 09/07/22 Aviv changed to support changes in number of slabs. ATTANTION - the default number is 5
    parser.add_argument("-numofscints", default= 5 , type=int)
    parser.add_argument("-detsize", default=1.214 , type=float)
    parser.add_argument("-scintz", default= 0.67 , type=float)
    parser.add_argument("-centerscint", default= 0 , type=float)
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

    if args.run:
        queue = queue.Queue()
    start_time = time.time() # timestamp before run
    simulation_data = dict()
    for run_dir, _, filename in os.walk(os.getcwd()):
        if INPUT_FILE_NAME in filename:
            os.chdir(run_dir)
            if args.run:
                queue.put(run_dir)
                # with open("run_stdout.txt", 'w') as out_fd:
                #     subprocess.run([GEANT_EXE_LOCATION, INPUT_FILE_NAME], stdout=out_fd)
            elif args.parse:
                run_number = get_run_number(run_dir)
                # 09/07/22 Aviv changed to support changes in number of slabs
                # and to fix the bug of the order of the positions of hitting the scints
                #simulation_data[run_number] = get_run_data(run_dir)
                simulation_data[run_number] = get_run_data(run_dir,args.numofscints, args.detsize , args.scintz,args.centerscint )
            # print('Debug: extracted the following data: \n {}'.format(simulation_data[run_number]))
    print(" Got Here horray!")
    if args.run:
        workers = Workers(queue, worker_func, args.j)
        workers.start_workers()
        workers.wait_for_all_workers()
        end_time = time.time() # timestamp after run
        print(end_time - start_time, " seconds")
        exit(0)
    #print(" Got Here horray!")
    os.chdir(save_path)  # return to script folder

    with open("{}/mapping.csv".format(save_path),'r') as csvinput:
        with open("{}/final_results.csv".format(save_path), 'w') as csvoutput:
            writer = csv.writer(csvoutput, lineterminator='\n')
            reader = csv.reader(csvinput)

            output_lines = []
            row = next(reader)
            row.extend(['Run number'])
            #row.extend(['Silicon_2 enter location', 'Silicon_1 enter location'])
            row.extend(['Scint_1 enter location', 'Scint_2 enter location', 'Scint_3 enter location' , 'Scint_4 enter location', 'Scint_5 enter location', 'Number of photons created'])
            #row.extend(['Number of electron-hole pairs created in Silicon_1', 'Number of electron-hole pairs created in Silicon_2'])
            row.extend(['Photons absorbed in Scint_1 Top-Right', 'Photons absorbed in Scint_1 Bottom-Left', 'Photons absorbed in Scint_1 Bottom-Right', 'Photons absorbed in Scint_1 Top-Left'])
            row.extend(['Photons absorbed in Scint_2 Top-Right', 'Photons absorbed in Scint_2 Bottom-Left', 'Photons absorbed in Scint_2 Bottom-Right', 'Photons absorbed in Scint_2 Top-Left'])
            row.extend(['Photons absorbed in Scint_3 Top-Right', 'Photons absorbed in Scint_3 Bottom-Left', 'Photons absorbed in Scint_3 Bottom-Right', 'Photons absorbed in Scint_3 Top-Left'])
            row.extend(['Photons absorbed in Scint_4 Top-Right', 'Photons absorbed in Scint_4 Bottom-Left', 'Photons absorbed in Scint_4 Bottom-Right', 'Photons absorbed in Scint_4 Top-Left'])
            row.extend(['Photons absorbed in Scint_5 Top-Right', 'Photons absorbed in Scint_5 Bottom-Left', 'Photons absorbed in Scint_5 Bottom-Right', 'Photons absorbed in Scint_5 Top-Left'])
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
            end_time = time.time() # timestamp after run
            output_lines.append(["Total time for simulation: ", end_time - start_time, " (seconds)"])
            output_lines.append(["Total runs: ", number_of_runs])
            #end = time.time()
            #total_time= end -start
            #output_lines.append(["Current run took: ", total_time])
            writer.writerows(output_lines)

print(end_time - start_time, " seconds")

