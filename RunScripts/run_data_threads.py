#!/usr/bin/python3


import os
import sys
import subprocess
import re
import csv
import pathlib
import time
import argparse
import queue
import logging
from typing import Pattern
import multiprocessing
import subprocess


MOTHER_FOLDER = '/runs'
INPUT_FILE_NAME = 'input.txt'
OUTPUT_FILE_NAME = 'test.txt'
GEANT_EXE_LOCATION = 'Sim.sh' #need to change back to build_prod
RUN_BEAM_ON = 2000

COUNT_TIME = True


def init_logging(mode):
    logging.basicConfig(filename=mode + "_data_threads.log", level=logging.INFO, format='%(asctime)s, %(message)s',datefmt='%Y-%m-%d, %H:%M:%S')

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
    #03/12/22 Aviv's edit to support split to 3 columns
    #enter_ordered = ['']* const_slabs
    enter_ordered = ['']* const_slabs * 3
    exit_ordered = ['']* const_slabs * 3
    total_energy = ['']* const_slabs
    for j in range(const_slabs):
        scint_zdim[j]= [scint_1_center-scintilator_size/2 + detector_size*j, scint_1_center+scintilator_size/2 + detector_size*j]
    #old_len = len(res)
    while i < len(content):
        i += 1
        # if NUMBER_OF_SLABS == 0:
        #     if "Total energy deposited" in content[i]:
        #         total_energy = re.search("[0-9'.']+")
        #         break
        #     continue
        if "Enter Location" in content[i]: # or "Exit Location" in content[i]:
            if NUMBER_OF_SLABS == 0:
                continue
            # searching for the z-axis element, and then reversing the string so we find only the z-dim between the ',' and the ')', as there is another ',' before the first one
            zdim_enter = re.search('\)(.*?)\,', content[i][16:][::-1]).group(1)[::-1]
            for j in range(const_slabs):
                if float(zdim_enter)/10 <= (float(scint_zdim[j][1])+0.2) and float(zdim_enter)/10 >= (float(scint_zdim[j][0])-0.2):
                    enter_ordered[j] = content[i][16:]
            #res.append(content[i][16:])
            #21/01/23 Aviv changed for the exit_location
            # NUMBER_OF_SLABS -= 1
        elif "Exit Location" in content[i]:
            if NUMBER_OF_SLABS == 0:
                continue
            # searching for the z-axis element, and then reversing the string so we find only the z-dim between the ',' and the ')', as there is another ',' before the first one
            zdim_exit = re.search('\)(.*?)\,', content[i][15:][::-1]).group(1)[::-1]
            for j in range(const_slabs):
                if float(zdim_exit)/10 <= (float(scint_zdim[j][1])+0.2) and float(zdim_exit)/10 >= (float(scint_zdim[j][0])-0.2):
                    exit_ordered[j] = content[i][15:]
                    #21/01/23 Aviv included total energy deposition
                    if "Total energy deposited" in content[i+1]:
                        x = re.search("[0-9'.']+", content[i+1])
                        total_energy[j] = x.group(0) if x is not None else ''
            #21/01/23 Aviv changed for the exit_location
            NUMBER_OF_SLABS -= 1
            #21/01/23 Aviv included total energy deposition
        # elif "Total energy deposited" in content[i]:
        #     total_energy = re.search("[0-9'.']+")
        elif "Number of" in content[i]:
            break
            #for j in range(const_slabs):
            #    if  not enter_ordered[j]:
            #        enter_ordered[j] = 'None'

    for j in range(const_slabs):
        #03/12/22 Aviv changed to split the  3D enter location to a 3 column for each axis
        #print (enter_ordered[j])
        if enter_ordered[j] == '':
            res.append('')
            res.append('')
            res.append('')
        else:
            xdim_enter = float(re.search('[(](.*?)[,]' , enter_ordered[j]).group(1))
            res.append(xdim_enter)

            ydim_enter = float(re.search('[,](.*?)[,]' , enter_ordered[j]).group(1))
            res.append(ydim_enter)

            zdim_enter = float(re.search('[)](.*?)[,]' , enter_ordered[j][::-1]).group(1)[::-1])
            res.append(zdim_enter)
    #21/01/23 Aviv included exit_location
    for j in range(const_slabs):
        if exit_ordered[j] == '':
            res.append('')
            res.append('')
            res.append('')
        else:
            xdim_enter = float(re.search('[(](.*?)[,]' , exit_ordered[j]).group(1))
            res.append(xdim_enter)

            ydim_enter = float(re.search('[,](.*?)[,]' , exit_ordered[j]).group(1))
            res.append(ydim_enter)

            zdim_enter = float(re.search('[)](.*?)[,]' , exit_ordered[j][::-1]).group(1)[::-1])
            res.append(zdim_enter)
    #21/01/23 Aviv included total energy deposition
    for j in range(const_slabs):
        if total_energy[j] == '':
            res.append('')
        else:
            res.append(total_energy[j])

        #print (enter_ordered[j])
        #res.append(enter_ordered[j]) #03/12/22 Aviv changed to split the  3D enter location to a 3 column for each axis

    # if len(res) < old_len + 2:  # in case the particle stopped in this slab
    #     res.append('None')
    return i

def add_missing_slabs(res):
    global NUMBER_OF_SLABS
    while NUMBER_OF_SLABS > 0:
        #03/12/22 Aviv's edit to support split to 3 columns
        for i in range(3):
            res.append('') # enter
        #res.append('None') # enter
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
        logging.info("Running %s %s", GEANT_EXE_LOCATION, run_dir + "/" + INPUT_FILE_NAME)
        geant_exe_full_path = os.path.abspath(GEANT_EXE_LOCATION)  
        # Must use absolute path of geant, since we change the working directory
        subprocess.run([geant_exe_full_path, run_dir + "/" + INPUT_FILE_NAME], stdout=out_fd, cwd=run_dir)
        logging.info("Finished simulation %s", run_dir)   
 

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-run", action='store_true')
    parser.add_argument("-parse", action='store_true')
    parser.add_argument("-dir", default='.')
    parser.add_argument("-j", default=1, type=int)
    # 09/07/22 Aviv changed to support changes in number of slabs. ATTENTION - the default number is 5
    parser.add_argument("-numofscints", default= 5 , type=int)
    parser.add_argument("-detsize", default=1.214 , type=float)
    parser.add_argument("-scintz", default= 0.67 , type=float)
    parser.add_argument("-centerscint", default= 0 , type=float)
    args = parser.parse_args()
    if args.run:
        init_logging("run")
    if args.parse:
        init_logging("parse")


    save_path = args.dir
    if os.path.exists(save_path):
   #     os.chdir(save_path)
        save_path = str(pathlib.Path().absolute()) 
        MOTHER_FOLDER = save_path + "/" + args.dir + MOTHER_FOLDER
    else:
        print(f"Directory {save_path} does not exists!")
        exit(1)

    if (args.run and args.parse) or (not args.run and not args.parse):
        print("Choose one of -run/-parse arguments!")
        exit(1)

    if args.run:
        dir_q = queue.Queue() 
    start_time = time.time() # timestamp before run
    simulation_data = dict()
    for run_dir, _, filename in os.walk(os.getcwd()):
        if INPUT_FILE_NAME in filename:
 #           os.chdir(run_dir)
            if args.run:
                dir_q.put(run_dir)
                # with open("run_stdout.txt", 'w') as out_fd:
                #     subprocess.run([GEANT_EXE_LOCATION, INPUT_FILE_NAME], stdout=out_fd)
            elif args.parse:
                run_number = get_run_number(run_dir)
                # 09/07/22 Aviv changed to support changes in number of slabs
                # and to fix the bug of the order of the positions of hitting the scints
                #simulation_data[run_number] = get_run_data(run_dir)
                simulation_data[run_number] = get_run_data(run_dir,args.numofscints, args.detsize , args.scintz, args.centerscint)
            # print('Debug: extracted the following data: \n {}'.format(simulation_data[run_number]))
    print(" Got Here horray!")
    if args.run:
        pool = multiprocessing.Pool(processes=args.j)
        while not dir_q.empty():
            name = dir_q.get()
            pool.apply_async(worker_func, args=(name,))

        pool.close()
        pool.join()
        end_time = time.time() # timestamp after run
        print(end_time - start_time, " seconds")
        exit(0)
    #print(" Got Here horray!")
 #   os.chdir(save_path)  # return to script folder
    with open("{}/mapping.csv".format(save_path),'r') as csvinput:
        with open("{}/final_results.csv".format(save_path + "/" + args.dir), 'w') as csvoutput:
            writer = csv.writer(csvoutput, lineterminator='\n')
            reader = csv.reader(csvinput)

            output_lines = []
            row = next(reader)
            row.extend(['Run number'])
            #row.extend(['Silicon_2 enter location', 'Silicon_1 enter location'])
            row.extend(['Scint_1 enter location[X]', 'Scint_1 enter location[Y]', 'Scint_1 enter location[Z]', 'Scint_2 enter location[X]', 'Scint_2 enter location[Y]', 'Scint_2 enter location[Z]', 'Scint_3 enter location[X]', 'Scint_3 enter location[Y]', 'Scint_3 enter location[Z]', 'Scint_4 enter location[X]', 'Scint_4 enter location[Y]', 'Scint_4 enter location[Z]', 'Scint_5 enter location[X]', 'Scint_5 enter location[Y]', 'Scint_5 enter location[Z]'])
            row.extend(['Scint_1 exit location[X]', 'Scint_1 exit location[Y]', 'Scint_1 exit location[Z]', 'Scint_2 exit location[X]', 'Scint_2 exit location[Y]', 'Scint_2 exit location[Z]', 'Scint_3 exit location[X]', 'Scint_3 exit location[Y]', 'Scint_3 exit location[Z]', 'Scint_4 exit location[X]', 'Scint_4 exit location[Y]', 'Scint_4 exit location[Z]', 'Scint_5 exit location[X]', 'Scint_5 exit location[Y]', 'Scint_5 exit location[Z]'])
            row.extend(['Total energy in this scint_1', 'Total energy in this scint_2','Total energy in this scint_3', 'Total energy in this scint_4','Total energy in this scint_5'])
            row.extend(['Number of photons created'])
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
            output_lines.append(["Total time for simulation: ", str(end_time - start_time), " (seconds)"])
            output_lines.append(["Total runs: ", str(number_of_runs)])
            #end = time.time()
            #total_time= end -start
            #output_lines.append(["Current run took: ", total_time])
            writer.writerows(output_lines)

logging.info("Time: %s seconds", str(end_time - start_time))

