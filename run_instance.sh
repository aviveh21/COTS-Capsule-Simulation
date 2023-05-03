#!/bin/bash

# This script runs a geant4 instance and sends a config file as user data. Then, the instance should start the simulation automatically

today=$(date +%Y-%m-%d.%H:%M:%S)
instance_name="geant-sim $today"
AMI=ami-029e947f3a58a9208
INSTANCE=c6i.xlarge

aws ec2 run-instances --image-id "$AMI" --count 4 --instance-type "$INSTANCE" --key-name alex_key \
--security-group-ids sg-0b3decb39d029facf --user-data file://init_geant_config_script.txt \
--tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=$instance_name}]"

