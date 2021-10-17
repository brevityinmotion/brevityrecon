import json, io
import brevitycore.core

def generateScriptPhoton(programName, inputBucketName):
    fileBuffer = io.StringIO()
    fileContents = f"""#!/bin/bash

# Run custom goSpider script
export HOME=/root
export PATH=/root/go/bin:$PATH
mkdir $HOME/security/refined/{programName}
mkdir $HOME/security/refined/{programName}/crawl
gospider -S $HOME/security/inputs/{programName}/{programName}-urls-base.txt -o $HOME/security/raw/{programName}/crawl -u web -t 1 -c 5 -d 1 --js --sitemap --robots --other-source --include-subs --include-other-source
cd $HOME/security/raw/{programName}/
# Pipes everything within the crawl directory, anew will unique them, and then they are written to a consolidated file.
# -urls-min.txt - The regex attempts to only retrieve the base urls, stopping at any parameters.
# -urls-max.txt - The regex includes all of the full urls but uniques any duplicates.
cat crawl/* | grep -Eo '(http|https)://[^/?:&"]+' | anew > $HOME/security/refined/{programName}/{programName}-urls-min.txt
sleep 20
cat crawl/* | grep -Eo '(http|https):\/\/[^]*]+' | anew > $HOME/security/refined/{programName}/{programName}-urls-max.txt
sleep 20

# This section will create an individual url listing for each domain passed in to crawl. I have no idea what that last bracket of symbols is doing, but it somehow writes in the filename.
FILES=$HOME/security/raw/{programName}/crawl/*
for f in $FILES
do
    cat $f | grep -Eo '(http|https)://[^/?:&"]+' | anew > $HOME/security/refined/{programName}/crawl/urls-simple-${{f##*/}}.txt
done
sleep 10                                                                      
sh $HOME/security/run/{programName}/sync-{programName}.sh
wait
sh $HOME/security/run/{programName}/stepfunctions-{programName}.sh"""

    fileBuffer.write(fileContents)
    objectBuffer = io.BytesIO(fileBuffer.getvalue().encode())
    # Upload file to S3
    object_name = 'crawl-' + programName + '.sh'
    object_path = 'run/' + programName + '/' + object_name
    status = brevitycore.core.upload_object(objectBuffer,inputBucketName,object_path)
    fileBuffer.close()
    objectBuffer.close()
    return status

def generateInstallScriptPhoton(inputBucketName):
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

# Install go tools
go get -u github.com/tomnomnom/anew
go get -u github.com/jaeles-project/gospider"""
    fileBuffer.write(fileContents)
    objectBuffer = io.BytesIO(fileBuffer.getvalue().encode())

    # Upload file to S3
    object_name = 'bounty-startup-crawl.sh'
    object_path = 'config/' + object_name
    bucket = inputBucketName
    installScriptStatus = brevitycore.core.upload_object(objectBuffer,bucket,object_path)
    fileBuffer.close()
    objectBuffer.close()
    return installScriptStatus