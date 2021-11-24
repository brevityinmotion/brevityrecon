# Code adapted from https://github.com/wellcomecollection/platform-infrastructure/blob/4b16beef44efbe8faa9a62f5459ab6f706e07032/builds/copy_docker_images_to_ecr.py
# https://docs.aws.amazon.com/lambda/latest/dg/runtimes-images.html

import base64
import subprocess
import boto3
import docker
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    
    def _getParameters(paramName):
        client = boto3.client('ssm')
        response = client.get_parameter(
            Name=paramName
        )
        return response['Parameter']['Value']
    
    refinedBucketPath = _getParameters('refinedBucketPath')
    inputBucketPath = _getParameters('inputBucketPath')
    programInputBucketPath = _getParameters('programInputBucketPath')
    ATHENA_BUCKET = _getParameters('ATHENA_BUCKET')
    ATHENA_DB = _getParameters('ATHENA_DB')
    ATHENA_TABLE = _getParameters('ATHENA_TABLE')
    
#    if event['program'] is None:
#        return {"isBase64Encoded":False,"statusCode":400,"body":json.dumps({"error":"Missing program name."})}
#    if event['operation'] is None:
#        return {"isBase64Encoded":False,"statusCode":400,"body":json.dumps({"error":"Missing operation name."})}
#    programName = str(event['program'])
#    operationName = str(event['operation'])
    
   # Code adapted from https://github.com/wellcomecollection/platform-infrastructure/blob/4b16beef44efbe8faa9a62f5459ab6f706e07032/builds/copy_docker_images_to_ecr.py

    account_id = boto3.client("sts").get_caller_identity()["Account"]

    image_tags = [
        "cloudcustodian/c7n-org:latest",
        "returntocorp/semgrep",
    ]

    ecr_client=boto3.client("ecr") #, account_id=ACCOUNT_ID, image_tags=IMAGE_TAGS

    print("Retrieving list of existing ECR repositories...")

    def get_ecr_repo_names_in_account(ecr_client, account_id):
        """
        Returns a set of all the ECR repository names in an AWS account.
        """
        repo_names = set()

        paginator = ecr_client.get_paginator("describe_repositories")
        for page in paginator.paginate(registryId=account_id):
            for repo in page["repositories"]:
                repo_names.add(repo["repositoryName"])
                # print(repo["repositoryName"])
        return repo_names
    existing_repos = get_ecr_repo_names_in_account(ecr_client, account_id)
    #print(existing_repos)

    print("Creating all ECR repositories...")

    mirrored_repos = set(tag.split(":")[0] for tag in image_tags)
    missing_repos = mirrored_repos - existing_repos
    print(missing_repos)
    for repo_name in missing_repos:
        ecr_client.create_repository(repositoryName=repo_name, imageScanningConfiguration={'scanOnPush':True})

    print("Authenticating Docker with ECR...")

    def docker_login_to_ecr(ecr_client, account_id):

        response = ecr_client.get_authorization_token(registryIds=[account_id])

    
        ecr_credentials = (ecr_client.get_authorization_token()['authorizationData'][0])
        ecr_username = 'AWS'
        ecr_password = (base64.b64decode(ecr_credentials['authorizationToken']).replace(b'AWS:', b'').decode('utf-8'))
        ecr_url = ecr_credentials['proxyEndpoint']
    
        docker_client = docker.from_env()
        docker_client.login(username=ecr_username, password=ecr_password, registry=ecr_url)
    
        return docker_client    

    docker_client = docker_login_to_ecr(ecr_client, account_id)
    docker_api = docker.APIClient()

    for hub_tag in image_tags:
        ecr_tag = f"{account_id}.dkr.ecr.us-east-1.amazonaws.com/{hub_tag}"
        print(f"Mirroring {hub_tag} to {ecr_tag}")
    
        image = docker_client.images.pull(hub_tag)
    
        print("Tagging image")
        if docker_api.tag(hub_tag, ecr_tag) is False:
            raise RuntimeError("ECR tag appeared to fail.")
        
        print("Pushing image to ECR")
        push_log = docker_client.images.push(ecr_tag, tag='latest')
        
    return 'successfully cloned docker image to ecr repo'