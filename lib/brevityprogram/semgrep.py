## THIS IS STILL A WORK IN PROGRESS

import io, json
import brevitycore.core

def prepareSemgrep(programName,inputBucketName):

    fileName = programName + '-templates.txt'
    # If operation is initial, it will be domains-new as filename
    diffPath = programName + '-domains-new.csv'
    
    templatePath = '$HOME/security/inputs/' + programName + '/' + programName + '-templates.txt'
    inputPath = '$HOME/security/inputs/' + programName + '/' + programName + '-domains-all.csv'
    outputPath = '$HOME/security/refined/' + programName + '/' + programName + '-nuclei.json'
    
    scriptStatus = generateScriptSemgrep(programName,inputBucketName, inputPath, outputPath)
    return scriptStatus

def generateScriptSemgrep(programName, inputBucketName, inputPath, outputPath):
    fileBuffer = io.StringIO()
    #fileBuffer.write("""#!/bin/bash
    fileContents = f"""#!/bin/bash

# Run custom nuclei script
export HOME=/root
export PATH=/root/go/bin:$PATH

mkdir $HOME/security/raw/{programName}/nuclei
# inputPath should resemble: $HOME/security/input/nuclei
export NUCLEIINPUTPATH={inputPath}

# nuclei -passive -target /data/responses/ -json -output nucleilocal.txt

if [ -f "$NUCLEIINPUTPATH" ]; then
    nuclei -passive -target {inputPath} -json -output $HOME/security/presentation/{programName}/nuclei-json/{programName}-nuclei-{outputPath}.json
fi

sh $HOME/security/run/{programName}/sync-{programName}.sh
wait
sh $HOME/security/run/{programName}/stepfunctions-{programName}.sh"""

    #fileContents = fileContents.format(programName)
    fileBuffer.write(fileContents)
    objectBuffer = io.BytesIO(fileBuffer.getvalue().encode())
    # Upload file to S3
    object_name = 'httpx-' + programName + '.sh'
    object_path = 'run/' + programName + '/' + object_name
    status = brevitycore.core.upload_object(objectBuffer,inputBucketName,object_path)
    fileBuffer.close()
    objectBuffer.close()
    return status

def generateInstallScriptSemgrep(inputBucketName):
    # Load AWS access keys for s3 synchronization
    secretName = 'brevity-aws-recon'
    regionName = 'us-east-1'
    secretRetrieved = brevitycore.core.get_secret(secretName,regionName)
    secretjson = json.loads(secretRetrieved)
    awsAccessKeyId = secretjson['AWS_ACCESS_KEY_ID']
    awsSecretKey = secretjson['AWS_SECRET_ACCESS_KEY']
    
    fileBuffer = io.StringIO()
    #fileBuffer.write("""#!/bin/bash
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

# Install semgrep
python3 -m pip install semgrep

# Install go tools
GO111MODULE=on go get -v github.com/projectdiscovery/nuclei/v2/cmd/nuclei"""
    fileBuffer.write(fileContents)
    objectBuffer = io.BytesIO(fileBuffer.getvalue().encode())

    # Upload file to S3
    object_name = 'bounty-startup-nuclei.sh'
    object_path = 'config/' + object_name
    bucket = inputBucketName
    installScriptStatus = brevitycore.core.upload_object(objectBuffer,bucket,object_path)
    fileBuffer.close()
    objectBuffer.close()
    return installScriptStatus