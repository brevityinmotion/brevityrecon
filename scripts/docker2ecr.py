# Code adapted from https://github.com/wellcomecollection/platform-infrastructure/blob/4b16beef44efbe8faa9a62f5459ab6f706e07032/builds/copy_docker_images_to_ecr.py

import base64
import subprocess
import boto3
import docker
from botocore.exceptions import ClientError

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

    try:
        auth = response["authorizationData"][0]
    except (IndexError, KeyError):
        raise RuntimeError("Unable to get authorization token from ECR!")

    auth_token = base64.b64decode(auth["authorizationToken"]).decode()
    username, password = auth_token.split(":")

    cmd = [
        "docker",
        "login",
        "--username",
        username,
        "--password",
        password,
        auth["proxyEndpoint"],
    ]

    subprocess.check_call(cmd)

docker_login_to_ecr(ecr_client, account_id)

for hub_tag in image_tags:
    ecr_tag = f"{account_id}.dkr.ecr.us-east-1.amazonaws.com/{hub_tag}"
    print(f"Mirroring {hub_tag} to {ecr_tag}")
    subprocess.run(["docker", "pull", hub_tag])
    subprocess.run(["docker", "tag", hub_tag, ecr_tag])
    subprocess.run(["docker", "push", ecr_tag])