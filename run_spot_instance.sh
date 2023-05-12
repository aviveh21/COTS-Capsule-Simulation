#!/bin/bash 

# This script runs a geant4 instance and sends a config file as user data. Then, the instance should start the simulation automatically

today=$(date +%Y-%m-%d.%H:%M:%S)
INSTANCE_NAME="geant-sim $today"
AMI_ID=ami-09a17df6c6cb84971
# INSTANCE_TYPE=c6i.xlarge
COUNT=10
# For high mem simulations
INSTANCE_TYPE=c6i.4xlarge
KEY_NAME=alex_key

USER_DATA=`base64 -i "init_geant_config_script.txt"` # Replace with the path to your user-data script



aws ec2 request-spot-instances \
    --instance-count "$COUNT" \
    --launch-specification "{
        \"ImageId\": \"$AMI_ID\",
        \"InstanceType\": \"$INSTANCE_TYPE\",
        \"KeyName\": \"$KEY_NAME\",
        \"SecurityGroupIds\": [\"sg-0b3decb39d029facf\"],
        \"UserData\": \"$USER_DATA\"
    }" \


#     --instance-interruption-behavior stop 
