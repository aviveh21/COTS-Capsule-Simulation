#!/usr/bin/python3
# First stage is to create the data for the Sim

# We need to make random occurance of the particles,
#  but we need to make sure the random particle would make contact with the detector

# For the sake of calling other scripts
from cmath import acos, asin, cos, pi, sin, sqrt
from locale import normalize
from random import randint, random, randrange, choices, uniform
import subprocess
# for writing json files
import json
# for math calcutaions
import numpy as np
import logging
import boto3
from botocore.exceptions import ClientError
import os
from make_data import particle_name

# import Full_Detector/Sim/src/SimDetectorConstruction.cc
# import Full_Detector/Sim/src/SimDetectorConstruction.hh

WORKING_DIR = "."   # Not needed unless we want it hardcoded.

# importent paths
results_folder = WORKING_DIR + "/new_run"
# data_to_be_run_path = "example_one_song_hero.json"
make_data_script = WORKING_DIR + "/make_data.py"
run_simulator_script = WORKING_DIR + "/run_data_threads.py"
# s3_uri =  "geant4-sim"
LOG_PATH = WORKING_DIR + "/run_script_Cosmic_Ray_Sim.log"
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

def upload_file(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_name)

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True

# data randomizer

## data from the cpp code

if __name__ == "__main__":

    init_logging()
    # Set working dir to script's location
    os.chdir(os.path.dirname(sys.argv[0]))

    sim_type = 'default'
    aws_bucket = False

    try:
        opts, args = getopt.getopt(sys.argv[1:],"",['aws-bucket=', 'sim-type='])
    except getopt.GetoptError as err:
        logging.info("%s bad parameters", sys.argv[0])
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
    # particle = "mu-"
    population_particles = ["proton", "alpha", "e-", "ion_carbon", "ion_oxygen", "ion_iron"]
    weights_particles = [1, 0, 0, 0, 0, 0]

    # energy = uniform(500,2000) # The randomness is in the loop

    total_runs = 1
    ### for loop to randomize 100 particles 

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
        if particle == "ion_carbon":
            particle = "ion"
            ion = [6, 12, 6]
            energy = uniform(700, 2500)
        elif particle == "ion_oxygen":
            particle = "ion"
            ion = [8, 16, 8]
            energy = uniform(700, 2500)
        elif particle == "ion_iron":
            particle = "ion"
            ion = [26, 52, 26]
            energy = uniform(7000, 15000)
        elif particle == "proton":
            ion = []
            energy = uniform(500, 2000)
        elif particle == "alpha":
            ion = []
            energy = uniform(150, 1000)

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

        # prepare the data with python script, for every json file
        subprocess.run(f"python3 {make_data_script} {results_folder} {file_path} {json_number}", shell=True)

        # closing for loop

    # run data
    subprocess.run(
        f"python3 {run_simulator_script} -j {number_of_threads} -dir {results_folder} -numofscints {NUMBER_OF_SLABS} -detsize {detector_size_z}  -scintz {scint_z} -centerscint {center_z_first_scint} -run",
        shell=True)

    # make CSV file
    subprocess.run(
        f"python3 {run_simulator_script} -j {number_of_threads} -dir {results_folder} -numofscints {NUMBER_OF_SLABS} -detsize {detector_size_z}  -scintz {scint_z} -centerscint {center_z_first_scint} -parse",
        shell=True)
    # upload csv to S3
    #s3 = boto3.client('s3')
    #with open("new_run/final_results.csv","rb") as f:
        #s3.upload_fileobj(f,s3_uri)
    if aws_bucket is not False:
        logging.info("Uploading file to S3 bucket %s", aws_bucket)
        upload_file("new_run/final_results.csv", aws_bucket, "final_results_" + sim_type + "_" + now.strftime("%m%d%Y%H_%M_%S"))



