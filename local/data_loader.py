import boto3
import configparser
AWS_CREDS_LOCATION = '/home/aviv/.aws/credentials'  # change according to your aws credentials
AWS_CONFIG_LOCATION = '/home/aviv/.aws/config'  # change according to your aws config for the region
local_directory = '/home/aviv/geant4/' # change according to the directory you want to save

def get_files_from_s3(bucket_name, prefix):
    # Create an S3 client
    s3 = boto3.client('s3')

    # List objects in the specified bucket and prefix
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)

    for obj in response['Contents']:
        if obj['Key'] != prefix: # handling bug which gives key of the prefix once for every file without the file
            file_name = obj['Key']
            local_file_path = local_directory + file_name
            s3.download_file(bucket_name, file_name,local_file_path)
            print(f'Downloaded file: {file_name}')

# Specify your AWS credentials and region
config_cred = configparser.ConfigParser()
config_cred.read(AWS_CREDS_LOCATION)
aws_access_key_id = config_cred['default']['aws_access_key_id']
aws_secret_access_key  = config_cred['default']['aws_secret_access_key']
config_reg = configparser.ConfigParser()
config_reg.read(AWS_CONFIG_LOCATION)
aws_region = config_reg['default']['region']

# Specify the S3 bucket name and prefix
bucket_name = 'geant4-sim' # change according to the your bucket
prefix ='Initial_DataSet/'  # change acording to the directory in which the files are "in" the specific bucket

# Create a session using your AWS credentials and region
session = boto3.Session(
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=aws_region
)

# Set the session as the default session for Boto3
#boto3.setup_default_session(session)
s3 = boto3.resource('s3')

# Get the files from S3
get_files_from_s3(bucket_name, prefix)
