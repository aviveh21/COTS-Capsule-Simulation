#!/usr/bin/python3
# First stage is to create the data for the Sim

# We need to make random occurance of the particles,
#  but we need to make sure the random particle would make contact with the detector

# For the sake of calling other scripts
from math import acos, asin, cos, pi, sin, sqrt
from locale import normalize
from random import randint, random, randrange, choices, uniform,choice
import subprocess
# for writing json files
import json
# for math calcutaions
import numpy as np
import logging
import os
import sys
import getopt
from make_data import particle_name
from datetime import datetime
import configparser
import psutil


# import Full_Detector/Sim/src/SimDetectorConstruction.cc
# import Full_Detector/Sim/src/SimDetectorConstruction.hh

WORKING_DIR = "."   # Not needed unless we want it hardcoded.

# importent paths
results_folder = "run_data"
# data_to_be_run_path = "example_one_song_hero.json"
make_data_script = WORKING_DIR + "/make_data.py"
run_simulator_script = WORKING_DIR + "/run_data_threads.py"
# s3_uri =  "geant4-sim"
LOG_PATH = WORKING_DIR + "/run_script_Cosmic_Ray_Sim.log"
LOCAL_CONFIG_FILE = WORKING_DIR + "/sim_config.ini"
# AWS_CREDS_LOCATION = '/etc/opt/geant4/aws_creds'
# s3_arn = "aws:s3:::geant4-sim"
# Functions

def init_logging():
    logging.basicConfig(filename=LOG_PATH, level=logging.INFO, format='%(asctime)s, %(message)s',datefmt='%Y-%m-%d, %H:%M:%S')


def pick_point_on_sphere(r, center):
    theta = 2 * pi * random()
    phi = acos(2 * random() - 1)

    x_pos = float(r * cos(theta) * sin(phi))
    y_pos = float(r * sin(theta) * sin(phi))
    z_pos = float(r * cos(phi))

    # put the sphere in the center of the telescope
    x_pos += center[0]
    y_pos += center[1]
    z_pos += center[2]

    position = np.array([x_pos, y_pos, z_pos])
    return position


def pick_point_cuboid(corner_far_z, corner_close_z, Alcover_x, Alcover_y):
    x = Alcover_x * random() - Alcover_x / 2  # -3.5 <-> 3.5cm
    y = Alcover_y * random() - Alcover_y / 2  # -3.5 <-> 3.5cm
    z = (corner_far_z - corner_close_z) * random() - (-corner_close_z)  # -0.687 <-> 5.543cm
    position = np.array([x, y, z])
    return position

def pick_point_in_chip(center_z_scint_3, chip_size_x, chip_size_y,chip_size_z):
    x = chip_size_x * random() - chip_size_x / 2  # -size_x/2 <-> size_x/2 (chip is in the middle)
    y = chip_size_y * random() - chip_size_y / 2  # -size_y/2 <-> size_y/2 (chip is in the middle)
    z = chip_size_z * random() - chip_size_z / 2 +center_z_scint_3 # center_scint_z + size_z/2 <->  center_scint_z + size_z/2  (chip is in the middle)
    position = np.array([x, y, z])
    return position


def create_run(json_number, energy, position, vector, particle, ion, beam_on = 1):


    ### creating python dict to before making it a json
    new_particle = {
        "energies": [energy],
        "positions": [list(position)],
        "directions": [list(vector)],
        "particles": [particle],
        "ions": [list(ion)] if len(ion)>1 else [],
        "beamOn": beam_on
    }

    # convert into JSON:
    file_path = f"{results_folder}/{str(int(json_number))}.json"
    with open(file_path, 'w') as outfile:
        json.dump(new_particle, outfile, indent=4)

    logging.info("Running %s", make_data_script)
        # prepare the data with python script, for every json file
    ret = subprocess.run([make_data_script, results_folder, file_path, str(json_number)], capture_output=True)
    if ret.returncode != 0:
        logging.error("Make data script failed to start")
        logging.error(ret.stdout + ret.stderr)
        logging.error("Exiting")
        sys.exit(2)
    else:
        logging.info("Data created successfully")



# data randomizer

## data from the cpp code

if __name__ == "__main__":

   # Set working dir to script's location
    os.chdir(os.path.dirname(sys.argv[0]))
    init_logging()

    sim_type = 'default'
    aws_bucket = False
    total_runs = False
    on_chip = None
    running_mode = False


    try:
        opts, args = getopt.getopt(sys.argv[1:],"",['aws-bucket=', 'sim-type=', 'total-runs=','on-chip='])
    except getopt.GetoptError as err:
        logging.info("%s bad parameters %s", sys.argv[0], err)
        sys.exit(2)

    for opt, arg in opts:
        if opt == '--aws-bucket':
            aws_bucket = arg
            logging.info("using aws bucket %s", aws_bucket)
        elif opt == '--sim-type':
            sim_type = arg
            logging.info("simulation type %s", sim_type)
        elif opt == '--total-runs':
            total_runs = int(arg)
            logging.info("total runs %d", total_runs)
        elif opt == '--on-chip':
            if arg == 'True':
                on_chip = True
                logging.info("Shooting particles into chip at random")
            else:
                on_chip = False
                logging.info("Shooting particles at random")
        else:
            logging.error("%s bad parameter %s", sys.argv[0], opt)
            sys.exit(2)

    if not os.path.exists(results_folder):
        os.makedirs(results_folder)

    number_of_threads = psutil.cpu_count(logical=True)
    logging.info("Using %d logical cpus", number_of_threads)

    NUMBER_OF_SLABS = 5
    detector_size_z = 1.214  # cm # Size in Z axis of the whole detector, which some of them create the telescope/Kasefet
    scint_z = 0.67  # cm # Size in Z axis of ONLY the scintilator part of one detector
    center_z_first_scint = 0  # cm # The position in Z axis of the center of the #1 scintilator

    # detector_parameters = [NUMBER_OF_SLABS, float(detector_size_z) , float(scint_z) , float(center_z_first_scint)]

    Alcover1_location = -0.647  # cm
    Alcover2_location = 5.503  # cm
    Alcover_z = 0.08  # cm
    Alcover_x = 7  # cm
    Alcover_y = 7  # cm

    center_z = (Alcover2_location + Alcover_z / 2 - (Alcover1_location - Alcover_z / 2)) / 2  # 3.115cm
    corner_far_z = Alcover2_location + Alcover_z / 2  # 5.543cm
    corner_close_z = Alcover1_location - Alcover_z / 2  # -0.687cm
    
    # paramters of chip to defend and extra
    chip_size_x = 1.5 # cm
    chip_size_y = 1.5 # cm
    chip_size_z = 0.03 # cm or 300 um
    center_z_scint_3 = center_z_first_scint + detector_size_z*2  # 2.428cm

    ##locations for calculating 
    center = np.array([0, 0, center_z])  # cm
    corner_far = np.array([Alcover_x / 2, Alcover_y / 2, corner_far_z])  # cm
    corner_close = np.array([-Alcover_x / 2, -Alcover_y / 2, corner_close_z])  # cm

    radius = np.linalg.norm(corner_far - center) + 0.1  # the 0.1 is for  a margin from the telescope

    ## making data


### Check if local config exists

    if os.path.isfile(LOCAL_CONFIG_FILE) is True:
        logging.info("Configuration file %s found.", LOCAL_CONFIG_FILE)

        config = configparser.ConfigParser()
        config.read(LOCAL_CONFIG_FILE)

        running_mode = config['DEFAULT']['MODE']

        logging.info("Running local configuration mode %s", running_mode)

        particle = config['DEFAULT']['PARTICLE']
        energy = float(config['DEFAULT']['ENERGY'])
        beam_on = int(config['DEFAULT']['BEAM_ON'])
        ion = eval(config['DEFAULT']['ION'])

        x_start = float(config['DEFAULT']['X_START'])
        y_start = float(config['DEFAULT']['Y_START'])
        x_end = float(config['DEFAULT']['X_END'])
        y_end = float(config['DEFAULT']['Y_END'])
        runs = int(config['DEFAULT']['RUNS'])



        if running_mode == 'GRID' or running_mode == 'RANDOM_GRID':

            if running_mode == 'GRID':
                grid_step = float(config['DEFAULT']['STEP'])

                json_number = 0

                for x in np.arange(x_start, x_end, grid_step):
                    for y in np.arange(y_start, y_end, grid_step):
                        logging.info("Simulating %s at X: %f, Y: %f with %f (MeV), beamOn %d", particle, x, y, energy, beam_on)
                        logging.info(ion)
                        position = [x, y, -5]
                        vector = [0, 0, 1]
                        json_number += 1
                        create_run(json_number, energy, position, vector, particle, ion, beam_on)
            else:            
                for json_number in range(runs):
                    x = np.random.uniform(x_start, x_end)
                    y = np.random.uniform(x_start, x_end)            
                    position = [x, y, -5]
                    vector = [0, 0, 1]
                    logging.info("Simulating %s at X: %f, Y: %f with %f (MeV), beamOn %d", particle, x, y, energy, beam_on)
                    create_run(json_number + 1, energy, position, vector, particle, ion, beam_on)

        elif running_mode == 'RANDOM':
 
            for json_number in range(runs):
                
                position = pick_point_on_sphere(5.0, np.array([0, 0, corner_close_z]))

                if position[2] > 0:
                    position = -position

                x_target = np.random.uniform(x_start, x_end)
                y_target = np.random.uniform(x_start, x_end)
                z_target = -0.335  ## 1st scintillator bottom

                destination = np.array([x_target, y_target, z_target])

                vector = np.array(destination - position)
                vector = vector/np.linalg.norm(vector)

                logging.info("Simulating %s at position [%f, %f, %f] and destination [%f, %f, %f]", particle, position[0], position[1], position[2], x_target, y_target, z_target)
                create_run(json_number + 1, energy, position, vector, particle, ion, beam_on)
            




    if running_mode == 'REGULAR' or running_mode is False:
        logging.info("Running regular configuration (ignoring local config).")


       ### random particle and energy from the cosmic ray radiation
        if sim_type == 'high_mem':
            population_particles = ["ion_neon","ion_magnesium","ion_silicon","ion_iron"]
            weights_particles = [0.2, 0.2,0.2, 0.4]
            if total_runs is False:
                total_runs = 1000
                logging.info("total_runs not found, using default value %d",total_runs)
            else:
                logging.info("Total runs %d", total_runs)
            
        else:
            population_particles = ["proton", "alpha", "ion_lithium", "ion_carbon", "ion_oxygen", "e-", "e+", "mu-", "mu+","gamma"]
            weights_particles = [0.3, 0.3, 0.1, 0.1, 0.1, 0.02, 0.02, 0.02, 0.02, 0.02]
            if total_runs is False:
                total_runs = 100000
                logging.info("total_runs not found, using default value %d",total_runs)
            else:
                logging.info("Total runs %d", total_runs)


        ### for loop to randomize all the particles 
        for x in range(total_runs):
            logging.info("Starting run number %d", x + 1)
            json_number = x + 1
            ### random starting position
            position = pick_point_on_sphere(radius, center)

            # position = [0 , 0 , -5 ] # For a beam from the start of the 1st scent, at the center

            ### random point inside the telescope OR inside chip to defend
            if on_chip:
                destination = pick_point_in_chip(center_z_scint_3, chip_size_x, chip_size_y,chip_size_z)
            else:
                destination = pick_point_cuboid(corner_far_z, corner_close_z, Alcover_x, Alcover_y)

            ### calculate the direction
            vector = (destination - position)
            vector_norm = np.linalg.norm(destination - position)
            vector = vector / vector_norm

            ### randomizing the particle and the energy

            particle = choices(population_particles, weights_particles)[0]
            if particle == "ion_lithium":
                particle = "ion"
                ion = [3, 6, 3]
                energy_range = choices([[30,300],[300,700],[700,4000]],[0.1,0.8,0.1])[0]
                energy = uniform(energy_range[0],energy_range[1])
            elif particle == "ion_carbon":
                particle = "ion"
                ion = [6, 12, 6]
                energy_range = choices([[70,700],[700,2000],[2000,11000]],[0.1,0.8,0.1])[0]
                energy = uniform(energy_range[0],energy_range[1])
            elif particle == "ion_oxygen":
                particle = "ion"
                ion = [8, 16, 8]
                energy_range = choices([[100,1000],[1000,3000],[3000,18000]],[0.1,0.8,0.1])[0]
                energy = uniform(energy_range[0],energy_range[1])
            elif particle == "ion_neon":
                particle = "ion"
                ion = [10, 20, 10]
                energy_range = choices([[150,1500],[1500,4500],[4500,25000]],[0.1,0.8,0.1])[0]
                energy = uniform(energy_range[0],energy_range[1])
            elif particle == "ion_magnesium":
                particle = "ion"
                ion = [12, 24, 12]
                energy_range = choices([[200,2000],[2000,6000],[6000,35000]],[0.1,0.8,0.1])[0]
                energy = uniform(energy_range[0],energy_range[1])
            elif particle == "ion_silicon":
                particle = "ion"
                ion = [14, 28, 14]
                energy_range = choices([[250,2500],[2500,8000],[8000,50000]],[0.1,0.8,0.1])[0]
                energy = uniform(energy_range[0],energy_range[1])
            elif particle == "ion_iron":
                particle = "ion"
                ion = [26, 52, 26]
                energy_range = choices([[700,7000],[7000,20000],[20000,150000]],[0.1,0.8,0.1])[0]
                energy = uniform(energy_range[0],energy_range[1])
            elif particle == "proton":
                ion = []
                energy_range = choices([[4,40],[40,400],[400,2000]],[0.1,0.8,0.1])[0]
                energy = uniform(energy_range[0],energy_range[1])
            elif particle == "alpha":
                ion = []
                energy_range = choices([[15,150],[150,800],[800,3000]],[0.1,0.8,0.1])[0]
                energy = uniform(energy_range[0],energy_range[1])
            elif particle == "e-":
                ion = []
                energy = uniform(0.1, 1000)
            elif particle == "e+":
                ion = []
                energy = uniform(0.1, 1000)
            elif particle == "mu-":
                ion = []
                energy = uniform(5000, 7000)
            elif particle == "mu+":
                ion = []
                energy = uniform(5000, 7000)
            elif particle == "gamma":
                ion = []
                energy = uniform(1, 10000)
            else:
                logging.error("ERROR: Particle type %s not found, check particles list", particle)

            logging.info("Starting run number %d, particle %s, energy %d", x + 1, particle, energy)

            create_run(json_number, energy, position, vector, particle, ion)

             # closing for else

    logging.info("Running %s", run_simulator_script)

    # run data
    ret = subprocess.run([run_simulator_script, "-j", str(number_of_threads),  "-dir", results_folder, "-numofscints", str(NUMBER_OF_SLABS), 
     "-detsize",  str(detector_size_z),  "-scintz", str(scint_z), "-centerscint", str(center_z_first_scint), "-run"], capture_output=True)

    if ret.returncode != 0:
        logging.error("Running %s failed", run_simulator_script)
        logging.error(ret.stdout + ret.stderr)
        logging.error("Exiting")
        sys.exit(2)
    else:
        logging.info("%s finished successfully", run_simulator_script)

###### Moved to data service
'''    logging.info("Making CSV file")

    # make CSV file
    ret = subprocess.run([run_simulator_script, "-j", str(number_of_threads), "-dir", results_folder, "-numofscints", str(NUMBER_OF_SLABS), "-detsize", str(detector_size_z), "-scintz", str(scint_z), 
        "-centerscint",  str(center_z_first_scint),  "-parse"],  capture_output=True)
    if ret.returncode != 0:
        logging.error("Making CSV file failed")
        logging.error(ret.stdout + ret.stderr)
        logging.error("Exiting")
        sys.exit(2)
    else:
        logging.info("%s finished successfully", run_simulator_script)
    # upload csv to S3
    #s3 = boto3.client('s3')
    #with open("new_run/final_results.csv","rb") as f:
        #s3.upload_fileobj(f,s3_uri)
    if aws_bucket is not False:
        config = configparser.ConfigParser()
        config.read(AWS_CREDS_LOCATION)
        access_key = config['DEFAULT']['ACCESS_KEY']
        secret_key = config['DEFAULT']['SECRET_KEY']

        logging.info("Uploading file to S3 bucket %s", aws_bucket)
        upload_file(results_folder + "/final_results.csv", aws_bucket, access_key, secret_key, "final_results_" + sim_type + "_" + datetime.now().strftime("%m%d%Y%H_%M_%S") + ".csv")
        logging.info("Done uploading to S3")
'''

