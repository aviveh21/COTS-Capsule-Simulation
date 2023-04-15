#!/usr/bin/python3
# First stage is to create the data for the Sim

# We need to make random occurance of the particles,
#  but we need to make sure the random particle would make contact with the detector

# For the sake of calling other scripts
from cmath import acos, asin, cos, pi, sin, sqrt
from locale import normalize
from random import randint, random, randrange, choices, uniform,choice
import subprocess
# for writing json files
import json
# for math calcutaions
import numpy as np
import logging
import boto3
from botocore.exceptions import ClientError
import os
import sys
import getopt
from make_data import particle_name
from datetime import datetime
import configparser


# import Full_Detector/Sim/src/SimDetectorConstruction.cc
# import Full_Detector/Sim/src/SimDetectorConstruction.hh

WORKING_DIR = "."   # Not needed unless we want it hardcoded.

# importent paths
results_folder = "new_run"
# data_to_be_run_path = "example_one_song_hero.json"
make_data_script = WORKING_DIR + "/make_data.py"
run_simulator_script = WORKING_DIR + "/run_data_threads.py"
# s3_uri =  "geant4-sim"
LOG_PATH = WORKING_DIR + "/run_script_Cosmic_Ray_Sim.log"
AWS_CREDS_LOCATION = '/etc/opt/geant4/aws_creds'
# s3_arn = "aws:s3:::geant4-sim"
# Functions

def init_logging():
    logging.basicConfig(filename=LOG_PATH, level=logging.INFO, format='%(asctime)s, %(message)s',datefmt='%Y-%m-%d, %H:%M:%S')


def pick_point_on_sphere(r, center):
    # while True:
    #     x1 = 2*random() -1
    #     x2 = 2*random() -1
    #     if (x1**2 +x2**2) < 1:
    #         break
    # x_pos = float(r * 2 * x1 * sqrt(1-x1**2-x2**2))
    # y_pos = float(r * 2 * x2 * sqrt(1-x1**2-x2**2))
    # z_pos = float(r * (1-2*(x1**2 +x2**2)))

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
    x = Alcover_x * random() - Alcover_x / 2  # -3.5 <-> 3.5
    y = Alcover_y * random() - Alcover_y / 2  # -3.5 <-> 3.5
    z = (corner_far_z - corner_close_z) * random() - (-corner_close_z)  # -0.687 <-> 5.543
    position = np.array([x, y, z])
    return position

def upload_file(file_name, bucket, access_key, secret_key, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """
    
    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_name)

    s3_client = boto3.client("s3", 
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key)

    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True

# data randomizer

## data from the cpp code

if __name__ == "__main__":

   # Set working dir to script's location
    os.chdir(os.path.dirname(sys.argv[0]))
    init_logging()

    sim_type = 'default'
    aws_bucket = False

    try:
        opts, args = getopt.getopt(sys.argv[1:],"",['aws-bucket=', 'sim-type='])
    except getopt.GetoptError as err:
        logging.info("%s bad parameters %s", sys.argv[0], err)
        sys.exit(2)

    for opt, arg in opts:
        if opt == '--aws-bucket':
            aws_bucket = arg
        elif opt == '--sim-type':
            sim_type = arg
        else:
            logging.error("%s bad parameter %s", sys.argv[0], opt)
            sys.exit(2)

    number_of_threads = 4

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

    ##locations for calculating 
    center = np.array([0, 0, center_z])  # cm
    corner_far = np.array([Alcover_x / 2, Alcover_y / 2, corner_far_z])  # cm
    corner_close = np.array([-Alcover_x / 2, -Alcover_y / 2, corner_close_z])  # cm

    radius = np.linalg.norm(corner_far - center) + 0.1  # the 0.1 is for  a margin from the telescope

    ## making data

    ### random particle and energy from the cosmic ray radiation
    if sim_type == 'high_mem':
        population_particles = ["ion_neon","ion_magnesium","ion_silicon","ion_iron"]
        weights_particles = [0.2, 0.2,0.2, 0.4]
        total_runs = 1000
        
    else:
        population_particles = ["proton", "alpha","lituium","carbon","oxygen", "e-", "e+", "mu-", "mu+","gamma"]
        weights_particles = [0.3, 0.3, 0.1, 0.1, 0.1, 0.02,0.02,0.02,0.02,0.02]
        total_runs = 100000
    ### for loop to randomize all the particles 

    for x in range(total_runs):
        json_number = x + 1
        ### random starting position
        position = pick_point_on_sphere(radius, center)

        # position = [0 , 0 , -5 ] # For a beam from the start of the 1st scent, at the center

        ### random point inside the telescope
        destination = pick_point_cuboid(corner_far_z, corner_close_z, Alcover_x, Alcover_y)

        ### calculate the direction
        vector = (destination - position)
        vector_norm = np.linalg.norm(destination - position)
        vector = vector / vector_norm

        # vector = [0 , 0 , 1 ] # For a beam from the start of the 1st scent, at the center
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
            energy_range = choices([[700,7000],[7000,2000],[700,150000]],[0.1,0.8,0.1])[0]
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

        ### creating python dict to before making it a json
        new_particle = {
            "energies": [energy],
            "positions": [list(position)],
            "directions": [list(vector)],
            "particles": [particle],
            "ions": [list(ion)] if len(ion)>1 else [],
            "beamOn": 1
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

        # closing for loop

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

    logging.info("Making CSV file")

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
        upload_file("new_run/final_results.csv", aws_bucket, access_key, secret_key, "final_results_" + sim_type + "_" + datetime.now().strftime("%m%d%Y%H_%M_%S"))
        logging.info("Done uploading to S3")



