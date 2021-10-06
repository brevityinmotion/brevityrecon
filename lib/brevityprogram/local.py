import io, json
import brevitycore.core

def prepareLocal(programName,inputBucketName):
    
    scriptStatus = generateScriptLocal(programName,inputBucketName)
    return scriptStatus

def generateScriptLocal(programName, inputBucketName):
    fileBuffer = io.StringIO()
    fileContents = f"""#!/bin/bash

# Run custom httpx script
export HOME=/home/ec2-user
export PATH=/home/ec2-user/go/bin:$PATH

mkdir $HOME/security/raw/{programName}/responses
mkdir $HOME/security/raw/{programName}/httpx
mkdir $HOME/security/presentation
mkdir $HOME/security/presentation/httpx-json

sh $HOME/security/run/{programName}/sync-{programName}.sh
wait
sh $HOME/security/run/{programName}/stepfunctions-{programName}.sh"""

    fileBuffer.write(fileContents)
    objectBuffer = io.BytesIO(fileBuffer.getvalue().encode())
    # Upload file to S3
    object_name = 'local-' + programName + '.sh'
    object_path = 'run/' + programName + '/' + object_name
    status = brevitycore.core.upload_object(objectBuffer,inputBucketName,object_path)
    fileBuffer.close()
    objectBuffer.close()
    return status

def generateInstallScriptLocal(inputBucketName):
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
export HOME=/home/ec2-user
mkdir $HOME/security
mkdir $HOME/security/tools
mkdir $HOME/security/tools/amass
mkdir $HOME/security/tools/amass/db
mkdir $HOME/security/tools/hakrawler
mkdir $HOME/security/tools/httpx
mkdir $HOME/security/tools/ffuf
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
yum update -y

# Ensure OS and packages are fully upgraded
#apt-get -y upgrade

# Install Git
yum install -y git # May already be installed

# Install Python and Pip
yum install -y python3 # Likely is already installed
yum install -y python3-pip

# Install Golang via cli
yum install -y golang

echo 'export GOROOT=/usr/lib/go' >> ~/.bashrc
echo 'export GOPATH=$HOME/go' >> ~/.bashrc
echo 'export PATH=$GOPATH/bin:$GOROOT/bin:$PATH' >> ~/.bashrc
#source ~/.bashrc

# Install docker
#curl -fsSL get.docker.com -o get-docker.sh
#sh get-docker.sh
    
# Install aws cli
#apt-get install -y awscli
yum install -y unzip
#cd /$HOME/security/tools/
#curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
#unzip awscliv2.zip
# Need to figure out how to make this install silent in order to leverage
#./aws/install

pip3 install --upgrade pip
pip3 install --upgrade awscli

#Install amass
#snap install amass

# Install go tools
GO111MODULE=on go get -v github.com/projectdiscovery/nuclei/v2/cmd/nuclei
GO111MODULE=on go get -v github.com/projectdiscovery/httpx/cmd/httpx
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

# Upgrade botocore to support pacu
#pip install botocore --upgrade

# Install Pacu
python3 -m pip install -U pacu

export AWS_ACCESS_KEY_ID={awsAccessKeyId}
export AWS_SECRET_ACCESS_KEY={awsSecretKey}
export AWS_DEFAULT_REGION=us-east-1"""

   # Load AWS access keys for s3 synchronization
    secretName = 'brevity-aws-recon'
    regionName = 'us-east-1'
    secretRetrieved = brevitycore.core.get_secret(secretName,regionName)
    secretjson = json.loads(secretRetrieved)
    awsAccessKeyId = secretjson['AWS_ACCESS_KEY_ID']
    awsSecretKey = secretjson['AWS_SECRET_ACCESS_KEY']
    
    fileBuffer.write(fileContents)
    objectBuffer = io.BytesIO(fileBuffer.getvalue().encode())

    # Upload file to S3
    object_name = 'bounty-startup-local.sh'
    object_path = 'config/' + object_name
    bucket = inputBucketName
    installScriptStatus = brevitycore.core.upload_object(objectBuffer,bucket,object_path)
    fileBuffer.close()
    objectBuffer.close()
    return installScriptStatus