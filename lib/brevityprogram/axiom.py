## THIS IS STILL A WORK IN PROGRESS. WILL BE MIGRATING TO DOCKER VERSION

import io, json
import brevitycore.core

def generateInstallScriptAxiom(inputBucketName):
    # Load AWS access keys for s3 synchronization
    secretName = 'brevity-aws-recon'
    regionName = 'us-east-1'
    secretRetrieved = brevitycore.core.get_secret(secretName,regionName)
    secretjson = json.loads(secretRetrieved)
    awsAccessKeyId = secretjson['AWS_ACCESS_KEY_ID']
    awsSecretKey = secretjson['AWS_SECRET_ACCESS_KEY']
    
    # Load DigitalOcean API key for Axiom
    secretNameDO = 'digitalocean'
    regionName = 'us-east-1'
    accessToken = brevitycore.core.get_secret(secretNameDO,regionName)
    
    axiomInputCommands = '\\n1\\nn\\ndo\\ny\\n' + accessToken + '\\nnyc1\\ns-1vcpu-1gb\\n\\nn\\nbrevityrecon\\nreconftw\\n'
    
    fileBuffer = io.StringIO()
    fileContents = f"""#!/bin/bash

# Create directory structure
export HOME=/home/ec2-user
mkdir $HOME/security
mkdir $HOME/security/tools
mkdir $HOME/security/raw
mkdir $HOME/security/refined
mkdir $HOME/security/presentation
mkdir $HOME/security/scope
mkdir $HOME/security/install
mkdir $HOME/security/config
mkdir $HOME/security/run
mkdir $HOME/security/inputs

# Update apt repositories to avoid software installation issues
sudo yum -y update

# Ensure OS and packages are fully upgraded
#apt-get -y upgrade

# Install Git
sudo yum install -y git # May already be installed

# Install Python and Pip
sudo yum install -y python3 # Likely is already installed
sudo yum install -y python3-pip

# Install Golang via cli
sudo yum install -y golang

echo 'export GOROOT=/usr/lib/go' >> ~/.bashrc
echo 'export GOPATH=$HOME/go' >> ~/.bashrc
echo 'export PATH=$GOPATH/bin:$GOROOT/bin:$PATH' >> ~/.bashrc
#source ~/.bashrc
    
# Install aws cli
sudo yum install -y awscli

# Install dependencies for Axiom
sudo yum install -y ruby
sudo yum install -y jq
# Utilized for install packer
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://rpm.releases.hashicorp.com/AmazonLinux/hashicorp.repo
sudo yum -y install packer
# Install doctl
wget https://github.com/digitalocean/doctl/releases/download/v1.62.0/doctl-1.62.0-linux-amd64.tar.gz
tar xf doctl-1.62.0-linux-amd64.tar.gz
sudo mv doctl /usr/local/bin
rm doctl*
# Install interlace
git clone https://github.com/codingo/Interlace.git
cd Interlace
sudo python3 setup.py install
cd ..
sudo rm -r Interlace
# Install rsync - likely already installed
sudo yum -y install rsync
# Install lsb_release
sudo yum -y install redhat-lsb-core
# Install fzf
git clone --depth 1 https://github.com/junegunn/fzf.git
sudo fzf/install --all
sudo rm -r fzf

# Install axiom while passing in commands
echo -ne '{axiomInputCommands}' | bash <(curl -s https://raw.githubusercontent.com/pry0cc/axiom/master/interact/axiom-configure)"""
    fileBuffer.write(fileContents)
    objectBuffer = io.BytesIO(fileBuffer.getvalue().encode())

    # Upload file to S3
    object_name = 'bounty-startup-axiom.sh'
    object_path = 'config/' + object_name
    bucket = inputBucketName
    installScriptStatus = brevitycore.core.upload_object(objectBuffer,bucket,object_path)
    fileBuffer.close()
    objectBuffer.close()
    return installScriptStatus