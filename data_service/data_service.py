#!/usr/bin/python3


import time
import logging
import sys
import subprocess
import os, os.path
import configparser
import requests
from datetime import datetime
import boto3
from botocore.exceptions import ClientError




# This service checks if a config file name exists. If it does, the simulation is started. Otherwise, sleep for 1 minute

RUN_SCRIPTS_DIR="RunScripts"
CONFIG_PATH = "data_service/config.ini"
LOG_PATH = "data_service/data_service.log"
SIMULATION_PATH = RUN_SCRIPTS_DIR + "/run_script_Cosmic_Ray_Sim.py"
RESULTS_FOLDER =  "run_data"
AWS_CREDS_LOCATION = '/etc/opt/geant4/aws_creds'
RUN_SIMULATOR_SCRIPT = "./run_data_threads.py"
NUM_OF_THREADS = 4
NUMBER_OF_SLABS = 5

DAEMON = True


def init_logging():
    if DAEMON is True:
        logging.basicConfig(filename=LOG_PATH, level=logging.INFO, format='%(asctime)s, %(message)s',datefmt='%Y-%m-%d, %H:%M:%S')
    else:
        logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(asctime)s %(message)s')

def get_instance_id():

    metadata_url = "http://169.254.169.254/latest/meta-data/instance-id"
    response = requests.get(metadata_url)

    return response.text


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
        logging.info("S3 upload_file response: %s", str(response))
    except ClientError as e:
        logging.error(e)
        return False
    return True


def delete_file(object_name, bucket, access_key, secret_key):
    
    s3_client = boto3.client("s3", 
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key)

    try:
        response = s3_client.delete_object(Bucket=bucket, Key=object_name)
        logging.info("S3 delete response: %s", str(response))
    except ClientError as e:
        logging.error(e)
        return False
    return True


def collect_results():

    detector_size_z = 1.214  # cm # Size in Z axis of the whole detector, which some of them create the telescope/Kasefet
    scint_z = 0.67  # cm # Size in Z axis of ONLY the scintilator part of one detector
    center_z_first_scint = 0  # cm # The position in Z axis of the center of the #1 scintilator
  
    logging.info("Making CSV file")

    # make CSV file

    ret = subprocess.Popen([RUN_SIMULATOR_SCRIPT, "-j", str(NUM_OF_THREADS), "-dir", RESULTS_FOLDER, "-numofscints", str(NUMBER_OF_SLABS), "-detsize", str(detector_size_z), "-scintz", str(scint_z), 
        "-centerscint",  str(center_z_first_scint),  "-parse"], cwd=RUN_SCRIPTS_DIR, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    stdout, stderr = ret.communicate()

    if ret.returncode != 0:
        logging.error("Making CSV file failed, %d", ret.returncode)
        logging.error(stdout + stderr)
        logging.error("Exiting")
        sys.exit(2)
    else:
        logging.info("%s finished successfully", RUN_SIMULATOR_SCRIPT)

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
    start_simulation_and_log_loop(aws_bucket_name, sim_type, total_runs)

def start_simulation_and_log_loop(aws_bucket_name, sim_type, total_runs):

    config = configparser.ConfigParser()
    config.read(AWS_CREDS_LOCATION)
    access_key = config['DEFAULT']['ACCESS_KEY']
    secret_key = config['DEFAULT']['SECRET_KEY']

    args = [SIMULATION_PATH, "--aws-bucket", aws_bucket_name, "--sim-type" ,sim_type]

    instance_id = get_instance_id()
    logging.info("Instance ID is %s", instance_id)

    partial_results_file_name = False

    if total_runs is not False:
        args += ["--total-runs", total_runs]

    logging.info("Starting simulation with arguments: " + str(args))
    start_simulation_time = datetime.now().strftime("%m%d%Y%H_%M_%S")
    process = subprocess.Popen(args)
    # Allow a few seconds to fail if something went wrong

    time.sleep(5) 

    while process.poll() is None:
        logging.info("Simulation is up and running. Saving partial results.")
        # Run python script to collect existing results
        collect_results()

        partial_results_file_name = "partial_results_" + instance_id + "_" + sim_type + "_" + start_simulation_time + ".csv"
        logging.info("Uploading file to S3 bucket %s", aws_bucket_name)
        upload_file(RUN_SCRIPTS_DIR + "/" + RESULTS_FOLDER + "/final_results.csv", aws_bucket_name, access_key, secret_key, partial_results_file_name)
        logging.info("Done uploading to S3")
        time.sleep(600)

    if process.returncode != 0:
        logging.error("Simulation failed, error code: %s", process.returncode)
    else:
        logging.info("Simulation finished successfully, Collecting results to CSV file")
        collect_results()
        logging.info("Done. Uploading results.")
        final_results_filename = "final_results_" + instance_id + "_" + sim_type + "_" + start_simulation_time + ".csv"
        upload_file(RUN_SCRIPTS_DIR + "/" + RESULTS_FOLDER + "/final_results.csv", aws_bucket_name, access_key, secret_key, final_results_filename)

        if partial_results_file_name is not False:
            logging.info("Deleting partial results file " + partial_results_file_name)
            delete_file(partial_results_file_name, aws_bucket_name, access_key, secret_key)

        logging.info("Shutting down system")
        os.system("sudo shutdown -h now")


def main():
    init_logging()
    read_config_and_start_service_loop(CONFIG_PATH)


if __name__ == "__main__":
    # Set the working directory to be the directory of the script

    main()


