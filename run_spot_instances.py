#!/opt/homebrew/bin/python3


import argparse
import base64
import boto3
import time

# Parse command-line arguments
parser = argparse.ArgumentParser()
parser.add_argument('--key-name', required=True, help='Name of the EC2 key pair to use')
parser.add_argument('--instance-count', type=int, required=True, help='Number of instances to launch')
parser.add_argument('--sim-type', required=True, help='Choose a simulation type (default/high_mem)')
parser.add_argument('--mode', required=False, help='mode = REGULAR/RANDOM/GRID/RANDOM_GRID', default='REGULAR')
parser.add_argument('--runs', required=True, type=int, help='Number of simulation runs. Not used with grid modes')
parser.add_argument('--debug', action='store_true', help='Enable debug mode')
parser.add_argument('--on-chip', action='store_true', help='Enable on_chip mode')



args = parser.parse_args()

# Define the parameters for the spot instances
# spot_price = '0.1'
instance_type = 'c6i.8xlarge'
image_id = 'ami-04c407babca800370' #'ami-0f722e57b64c61129'
key_name = args.key_name
instance_count = args.instance_count
sim_type = args.sim_type
runs = args.runs
mode = args.mode
security_group_ids = [ 'sg-0b3decb39d029facf' ]


x_start=-3.5
x_end=3.55
y_start=-3.5
y_end=3.55
particle='ion'
energy=18000 # MeV
beam_on=1
grid_step=0.1 # cmd
ion=[8, 16, 8] # oxygen
l_runs=5000 # only for random grid mode

debug = False
on_chip = False

if args.debug:
    debug = args.debug

if args.on_chip:
    on_chip = args.on_chip

user_data = f'''#!/bin/bash

tee -a /home/ubuntu/COTS-Capsule-Simulation/data_service/config.ini <<EOF
[DEFAULT]
AWS_BUCKET=alex-geant-test
SIMULATION_TYPE={sim_type}
TOTAL_RUNS={runs}
DEBUG={debug}
ON_CHIP={on_chip}
EOF

tee -a /home/ubuntu/COTS-Capsule-Simulation/RunScripts/sim_config.ini <<EOF2
[DEFAULT]
MODE={mode}
# REGULAR (default)/ GRID /RANDOM / RANDOM_GRID. In those cases BEAM_ON will be used as the parameter for beamOn and TOTAL_RUNS ignored
X_START={x_start}
# (cm)
Y_START={y_start}
X_END={x_end}
Y_END={y_end}
STEP={grid_step}
PARTICLE={particle}           
# Only in case of grid 
ENERGY={energy}
# Energy (MeV)
ION={ion}
BEAM_ON={beam_on}
RUNS={l_runs}
EOF2
'''

user_data_b64 = base64.b64encode(user_data.encode('utf-8')).decode('utf-8')
# Define the tags to apply to the instances
tags = [
    {'Key': 'Name', 'Value': sim_type},
]

ec2 = boto3.client('ec2')


if args.debug:
    print("Running regular instance")
    response = ec2.run_instances(
            ImageId=image_id,  # Replace with your desired AMI ID
            InstanceType=instance_type,  # Replace with your desired instance type
            MinCount=instance_count,
            MaxCount=instance_count,
            KeyName=key_name,  # Replace with your key pair name
            UserData=user_data,
            SecurityGroupIds=security_group_ids,
            TagSpecifications=[
                {
                    'ResourceType': 'instance',
                    'Tags': tags
                },
            ]
        )
    exit(0)


# Launch the spot instances
response = ec2.request_spot_instances(
  #  SpotPrice=spot_price,
    InstanceCount=instance_count,
    LaunchSpecification={
        'ImageId': image_id,
        'InstanceType': instance_type,
        'KeyName': key_name,
        'UserData': user_data_b64,
        'SecurityGroupIds': security_group_ids
    }
)

time.sleep(1)

# Get the spot request IDs
spot_request_ids = [r['SpotInstanceRequestId'] for r in response['SpotInstanceRequests']]

# Wait for the instances to start running
running_instance_ids = []
while len(running_instance_ids) < len(spot_request_ids):
    time.sleep(1)
    instances = ec2.describe_instances(Filters=[{'Name': 'spot-instance-request-id', 'Values': spot_request_ids}])
    for reservation in instances['Reservations']:
        for instance in reservation['Instances']:
            if instance['State']['Name'] == 'running':
                if instance['InstanceId'] not in running_instance_ids:
                    running_instance_ids.append(instance['InstanceId'])

# Tag the running instances
ec2.create_tags(Resources=running_instance_ids, Tags=tags)
