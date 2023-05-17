import boto3
import configparser

AWS_CREDS_LOCATION = '/home/aviv/.aws/credentials'
AWS_CONFIG_LOCATION = '/home/aviv/.aws/config'
local_directory = 'home/aviv/geant4/initial_dataset'

def get_files_from_s3(bucket_name, prefix):
    # Create an S3 client
    s3 = boto3.client('s3')

    # List objects in the specified bucket and prefix
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)

    for obj in response['Contents']:
        file_name = obj['Key']
        local_file_path = local_directory + file_name

        s3.download_file(bucket_name, file_name, local_file_path)
        print(f'Downloaded file: {file_name}')


# Specify your AWS credentials and region
config = configparser.ConfigParser()
config.read(AWS_CREDS_LOCATION)
aws_access_key_id = config['DEFAULT']['aws_access_key_id']
aws_secret_access_key  = config['DEFAULT']['aws_secret_access_key']
config = configparser.ConfigParser()
config.read(AWS_CREDS_LOCATION)
aws_region = config['DEFAULT']['region']

# Specify the S3 bucket name and prefix
bucket_name = 'geant4-sim'
prefix = 'Initial_DataSet/'

# Create a session using your AWS credentials and region
session = boto3.Session(
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=aws_region
)

# Set the session as the default session for Boto3
boto3.setup_default_session(session)

# Get the files from S3
get_files_from_s3(bucket_name, prefix)