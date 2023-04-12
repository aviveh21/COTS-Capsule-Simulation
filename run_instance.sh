#!/bin/bash

# This script runs a geant4 instance and sends a config file as user data. Then, the instance should start the simulation automatically

today=$(date +%Y-%m-%d.%H:%M:%S)
instance_name="geant-sim $today"

aws ec2 run-instances --image-id ami-0f225704f866d6cd6 --count 1 --instance-type t2.micro --key-name alex_key \
--security-group-ids sg-0b3decb39d029facf --user-data file://init_geant_config_script.txt \
--tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=$instance_name}]"

