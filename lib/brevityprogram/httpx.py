import io, json
import brevitycore.core

def prepareHttpx(programName,inputBucketName, fileName):
    
    # This url-mods.txt file is the output after processing the crawl URLs and only adding the in-scope urls and it only keeps the first url with parameters because sometimes the crawl loops through tens of thousands of blog or product type sites where the variation is a parameter vs page. Another option is to pass in the -urls-max.txt or -urls-min.txt file, but it will include out-of-scope URLs.
    gospiderPath = programName + '-urls-mod.txt'
    # If operation is initial, it will be domains-new as filename
    diffPath = programName + '-domains-new.txt'
    
    # The first iteration of recon is only going to have a -domains-all.csv file. The second recursive iteration after the crawl will have a -urls-mod.txt file.
    if (fileName == gospiderPath):
        inputPath = '$HOME/security/inputs/' + programName + '/' + programName + '-urls-mod.txt'
        outputPath = 'crawl'
    if (fileName == diffPath):
        inputPath = '$HOME/security/inputs/' + programName + '/' + programName + '-domains-all.txt'
        outputPath = 'initial'
    
    scriptStatus = generateScriptHttpx(programName,inputBucketName, inputPath, outputPath)
    return scriptStatus

def generateScriptHttpx(programName, inputBucketName, inputPath, outputPath):
    fileBuffer = io.StringIO()
    fileContents = f"""#!/bin/bash

# Run custom httpx script
export HOME=/root
export PATH=/root/go/bin:$PATH

mkdir $HOME/security/raw/{programName}/responses
mkdir $HOME/security/raw/{programName}/httpx
mkdir $HOME/security/presentation
mkdir $HOME/security/presentation/httpx-json

export HTTPXINPUTPATH={inputPath}

if [ -f "$HTTPXINPUTPATH" ]; then
    httpx -json -o $HOME/security/presentation/httpx-json/{programName}-httpx-{outputPath}.json -l {inputPath} -status-code -title -location -content-type -web-server -no-color -tls-probe -x GET -ip -cname -cdn -content-length -sr -srd $HOME/security/raw/{programName}/responses -timeout 1
fi
sleep 10
# Remove .txt from all of the files
echo 'Completed crawl'
cd $HOME/security/raw/{programName}/responses/
for f in *.txt; do mv -- "$f" "${{f%.txt}}"; done
sleep 10
cd /root/security/raw/{programName}/
sleep 10
sh $HOME/security/run/{programName}/sync-{programName}.sh
wait
sh $HOME/security/run/{programName}/stepfunctions-{programName}.sh"""

    fileBuffer.write(fileContents)
    objectBuffer = io.BytesIO(fileBuffer.getvalue().encode())
    # Upload file to S3
    object_name = 'httpx-' + programName + '.sh'
    object_path = 'run/' + programName + '/' + object_name
    status = brevitycore.core.upload_object(objectBuffer,inputBucketName,object_path)
    fileBuffer.close()
    objectBuffer.close()
    return status

def generateInstallScriptHttpx(inputBucketName):
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
mkdir $HOME/security/presentation
mkdir $HOME/security/presentation/httpx
mkdir $HOME/security/presentation/httpx-json
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
GO111MODULE=on go get -v github.com/projectdiscovery/httpx/cmd/httpx"""
    fileBuffer.write(fileContents)
    objectBuffer = io.BytesIO(fileBuffer.getvalue().encode())

    # Upload file to S3
    object_name = 'bounty-startup-httpx.sh'
    object_path = 'config/' + object_name
    bucket = inputBucketName
    installScriptStatus = brevitycore.core.upload_object(objectBuffer,bucket,object_path)
    fileBuffer.close()
    objectBuffer.close()
    return installScriptStatus