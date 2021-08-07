# Author: Ryan Elkins
# Objective: Core functions that apply to multiple components of the environment

import boto3
import logging
#import ClientError
import time
import json
from botocore.exceptions import ClientError
import base64

# upload memory buffers to AWS S3 bucket
def upload_object(file_name, bucket, object_name=None):
    
    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.put_object(Body=file_name, Bucket=bucket, Key=object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True

# update a secret value within AWS Secrets Manager
def put_secret(secretName,secretValue,regionName):
    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=regionName
    )

    response = client.put_secret_value(
        SecretId=secretName,
        SecretString=secretValue
    )
    return response

# Create a secret to store within AWS Secrets Manager
def create_secret(secretName,secretValue,regionName,secretDesc):
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=regionName
    )
    response = client.create_secret(
        Name=secretName,
        Description=secretDesc,
        SecretString=secretValue
    )
    return response

# Retrieve an AWS Secrets Manager secret
def get_secret(secret_name, region_name):

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    # In this sample we only handle the specific exceptions for the 'GetSecretValue' API.
    # See https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
    # We rethrow the exception by default.

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'DecryptionFailureException':
            # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InternalServiceErrorException':
            # An error occurred on the server side.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            # You provided an invalid value for a parameter.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            # You provided a parameter value that is not valid for the current state of the resource.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'ResourceNotFoundException':
            # We can't find the resource that you asked for.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
    else:
        # Decrypts secret using the associated KMS CMK.
        # Depending on whether the secret is a string or binary, one of these fields will be populated.
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
            return secret
 
        else:
            decoded_binary_secret = base64.b64decode(get_secret_value_response['SecretBinary'])
            return json.loads(secret)

# Submit a query to AWS Athena
def queryathena(athenadb, athenabucket, query):
    athena = boto3.client('athena')
    qexec = athena.start_query_execution(
        QueryString=query,
        QueryExecutionContext={
            'Database':athenadb
        },
        ResultConfiguration={
            'OutputLocation':athenabucket
        }
    )
    execid = qexec['QueryExecutionId']
    return execid

# After submitting an athena query, the response will be an execution id. This function will check the loop until it completes. Upon completion, the location will be parsed from the response and a S3 presigned URL will be created for download. AWS pre-signed URLs include time-based authorization for access to the specific object.
def retrieveresults(execid):
    athena = boto3.client('athena')
    s3 = boto3.client('s3')
    queryres = athena.get_query_execution(
        QueryExecutionId = execid
    )
    
    # Athena query checking code is from https://medium.com/dataseries/automating-athena-queries-from-s3-with-python-and-save-it-as-csv-8917258b1045
    # Loop until results are ready or fail after 5 minutes
    status = 'RUNNING'
    iterations = 60
    
    while (iterations>0):
        iterations = iterations - 1
        response_get_query_details = athena.get_query_execution(
        QueryExecutionId = execid
        )
        status = response_get_query_details['QueryExecution']['Status']['State']
        print(status)
        if (status == 'FAILED') or (status == 'CANCELLED'):
            return 'Query failed.'
        elif status == 'SUCCEEDED':
            try:
                outputloc = queryres['QueryExecution']['ResultConfiguration']['OutputLocation']
                full = outputloc[5:] # trim s3:// prefix
                bucketloc = full.split('/')[0] # get bucket from full path
                keyloc = full.replace(bucketloc,'')[1:] # get key and remove starting /
    
                url = s3.generate_presigned_url(
                    'get_object',
                    Params={
                    'Bucket':bucketloc,
                    'Key':keyloc
                    }
                )
                return url
            except:
                url = "No results."
                return url
        else:
            time.sleep(5)
            
# Configure SNS topic and text messaging
def notify_user(phonenumber,message):
    client = boto3.client('sns')
    client.publish(PhoneNumber=phonenumber, Message=message)

# Example function call syntax
# notify_user('+1XXXXXXXXXX', 'Results are done')