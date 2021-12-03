#!/bin/bash
TOOLNAME="nuclei"
TOOLSBUCKET="brevity-inputs"

aws s3 cp --recursive /home/ec2-user/environment/brevityrecon/tools/$TOOLNAME/ s3://$TOOLSBUCKET/tools/$TOOLNAME/


# To be run on the EC2 instance.
# Need the environment variables configured first for creds
aws s3 cp --recursive s3://brevity-inputs/tools/nuclei/ /home/kali/security/tools/nuclei/

aws s3 cp --recursive s3://brevity-raw/responses/dhsvdp/ /home/kali/security/data/responses/dhsvdp/

mkdir /home/kali/security/presentation
nuclei -passive -target /home/kali/security/data/responses/dhsvdp/ -json -output /home/kali/security/presentation/dhsvdp/nuclei-json/dhsvdp-nuclei-findings.json