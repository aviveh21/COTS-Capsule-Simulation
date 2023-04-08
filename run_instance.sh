#!/bin/bash

# This script runs a geant4 instance and sends a config file as user data. Then, the instance should start the simulation automatically

aws ec2 run-instances --image-id ami-0aff0f38121111507 --count 1 --instance-type t2.micro --key-name alex_key --security-group-ids sg-0b3decb39d029facf --user-data file://init_geant_config_script.txt

