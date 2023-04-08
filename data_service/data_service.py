#!/usr/bin/python3


import time
import logging
import sys
import subprocess
import os.path
import configparser




# This service checks if a config file name exists. If it does, the simulation is started. Otherwise, sleep for 1 minute

CONFIG_PATH = "data_serivce/config.ini"
LOG_PATH = "data_service/data_service.log"
SIMULATION_PATH = "RunScripts/run_scriptCosmic_Ray_Sim.py"
DAEMON = True


def init_logging():
    if (DAEMON is True):
        logging.basicConfig(filename=LOG_PATH, level=logging.INFO, format='%(asctime)s, %(message)s',datefmt='%Y-%m-%d, %H:%M:%S')
    else:
        logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(asctime)s %(message)s')


def check_config_file_exists(filename):
    return os.path.isfile(filename)

def read_config_and_start_service_loop(filename):

    while not check_config_file_exists(filename):
        logging.info("No configuration file found, sleeping 60 seconds")
        time.sleep(60)

    config = configparser.ConfigParser()
    config.read(filename)
    
    aws_bucket_name = config['DEFAULT']['AWS_BUCKET']
    sim_type = config['DEFAULT']['SIMULATION_TYPE']

    start_simulation_and_exit(aws_bucket_name, sim_type)

def start_simulation_and_exit(aws_bucket_name, sim_type):

    args = [SIMULATION_PATH, "--aws-bucket ", aws_bucket_name, "--sim-type" sim_type]

    ret = subprocess.run(args, capture_output=True)

    if ret.returncode != 0:
        logging.error("Simulation failed to start")
        logging.error(ret.stdout + ret.stderr)
    else:
        logging.info("Simulated started successfully")

def main():
    init_logging()
    read_config_and_start_service_loop(CONFIG_PATH)


if __name__ == "__main__":
    # Set the working directory to be the directory of the script

    main()


