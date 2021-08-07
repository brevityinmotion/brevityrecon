import boto3, io, json, requests
import botocore
from botocore.exceptions import ClientError
import logging
import brevitycore

# This function is no longer used as there is a tool install script specific to each operation. It is still a good reference for upcoming tools which do not yet have their own operation.
def generateBountyInstallScript(inputBucketName):
    # Load AWS access keys for s3 synchronization
    secretName = 'brevity-aws-recon'
    regionName = 'us-east-1'
    secretRetrieved = brevitycore.core.get_secret(secretName,regionName)
    secretjson = json.loads(secretRetrieved)
    awsAccessKeyId = secretjson['AWS_ACCESS_KEY_ID']
    awsSecretKey = secretjson['AWS_SECRET_ACCESS_KEY']
    
    fileBuffer = io.StringIO()
    fileContents = f"""#!/bin/bash

# Create directory structure
export HOME=/root
mkdir $HOME/security
mkdir $HOME/security/tools
mkdir $HOME/security/tools/amass
mkdir $HOME/security/tools/amass/db
mkdir $HOME/security/tools/hakrawler
mkdir $HOME/security/tools/httpx
mkdir $HOME/security/raw
mkdir $HOME/security/refined
mkdir $HOME/security/curated
mkdir $HOME/security/scope
#mkdir $HOME/security/cron
#mkdir $HOME/security/cron/cron.hourly
#mkdir $HOME/security/cron/cron.daily
mkdir $HOME/security/install
mkdir $HOME/security/config
mkdir $HOME/security/run
mkdir $HOME/security/inputs

# Update apt repositories to avoid software installation issues
apt-get update

# Ensure OS and packages are fully upgraded
#apt-get -y upgrade

# Install Git
apt-get install -y git # May already be installed

# Install Python and Pip
apt-get install -y python3 # Likely is already installed
apt-get install -y python3-pip

# Install Golang via cli
apt-get install -y golang

echo 'export GOROOT=/usr/lib/go' >> ~/.bashrc
echo 'export GOPATH=$HOME/go' >> ~/.bashrc
echo 'export PATH=$GOPATH/bin:$GOROOT/bin:$PATH' >> ~/.bashrc
#source ~/.bashrc
    
# Install aws cli
apt-get install -y awscli

# Install docker
curl -fsSL get.docker.com -o get-docker.sh
sh get-docker.sh

# Tool installations

# Install amass for recon
snap install amass

# Install go tools
# GO111MODULE=on go get -v github.com/projectdiscovery/httpx/cmd/httpx@07bff31c45cc0c1f558c2c4f7718b06c328481bc
GO111MODULE=on go get -v github.com/projectdiscovery/httpx/cmd/httpx
#go get -u github.com/projectdiscovery/httpx/cmd/httpx
go get -u github.com/tomnomnom/unfurl
go get -u github.com/ffuf/ffuf
go get -u github.com/hakluke/hakrawler
go get -u github.com/tomnomnom/anew
go get -u github.com/jaeles-project/gospider
go get -u github.com/svent/sift

# Install LinkFinder
cd /$HOME/security/tools/
git clone https://github.com/GerbenJavado/LinkFinder.git
cd LinkFinder
python3 setup.py install
pip3 install -r requirements.txt

# Install SemGrep
python3 -m pip install semgrep

# AWS synchronization of data

# This information will be cleared every session as it is not persistent
export AWS_ACCESS_KEY_ID={awsAccessKeyId}
export AWS_SECRET_ACCESS_KEY={awsSecretKey}
export AWS_DEFAULT_REGION=us-east-1"""
    fileBuffer.write(fileContents)
    objectBuffer = io.BytesIO(fileBuffer.getvalue().encode())

    # Upload file to S3
    object_name = 'bounty-startup-all.sh'
    object_path = 'config/' + object_name
    bucket = inputBucketName
    installScriptStatus = brevitycore.core.upload_object(objectBuffer,bucket,object_path)
    fileBuffer.close()
    objectBuffer.close()
    return installScriptStatus

# This function will update the Athena table to point to the latest Sonar FDNS datasets
def updateSonarPartitions(ATHENA_DB, ATHENA_BUCKET):
    query = 'msck repair table rapid7_fdns_any;'
    execid = brevitycore.core.queryathena(ATHENA_DB, ATHENA_BUCKET, query)
    downloadURL = brevitycore.core.retrieveresults(execid)
    s=requests.get(downloadURL).content