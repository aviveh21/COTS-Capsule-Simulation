#!/usr/bin/python3


import time
import logging
import sys
import subprocess
import os.path
import configparser




# This service checks if a config file name exists. If it does, the simulation is started. Otherwise, sleep for 1 minute

CONFIG_PATH = "data_service/config.ini"
LOG_PATH = "data_service/data_service.log"
SIMULATION_PATH = "RunScripts/run_script_Cosmic_Ray_Sim.py"
DAEMON = True


def init_logging():
    if (DAEMON is True):
        logging.basicConfig(filename=LOG_PATH, level=logging.INFO, format='%(asctime)s, %(message)s',datefmt='%Y-%m-%d, %H:%M:%S')
    else:
        logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(asctime)s %(message)s')


def check_config_file_exists_and_valid(filename):
    if os.path.isfile(filename) is False:
        logging.info("No configuration file %s found.", filename)
        return False

    config = configparser.ConfigParser()
    config.read(filename)

    if not config.has_option('DEFAULT', 'AWS_BUCKET') or not config.has_option('DEFAULT', 'SIMULATION_TYPE'):
        logging.info("Missing parameters in secion DEFAULT.")
        return False

    else:
        return config


def read_config_and_start_service_loop(filename):

    config = False
    total_runs = False

    while config is False:
        config = check_config_file_exists_and_valid(filename)
        if config is False:
            logging.info("sleeping 60 seconds")
            time.sleep(60)

    aws_bucket_name = config['DEFAULT']['AWS_BUCKET']
    sim_type = config['DEFAULT']['SIMULATION_TYPE']

    if config.has_option('DEFAULT', 'TOTAL_RUNS'):
        total_runs = config['DEFAULT']['TOTAL_RUNS']

    logging.info("Starting simulation.")
    start_simulation_and_exit(aws_bucket_name, sim_type, total_runs)

def start_simulation_and_exit(aws_bucket_name, sim_type, total_runs):

    args = [SIMULATION_PATH, "--aws-bucket", aws_bucket_name, "--sim-type" ,sim_type]

    if total_runs is not False:
        args += ["--total-runs", total_runs]

    logging.info("Starting simulation with arguments: " + str(args))

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


