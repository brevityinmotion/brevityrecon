#!/bin/bash
LAMBDANAME="brevity-ec2"
aws ec2 run-instances --image-id ami-0c2b8ca1dad447f8a --count 1 --instance-type m3.medium \
--key-name my-key-pair --subnet-id subnet-eb16fd8d --security-group-ids sg-06b7ab6f94c9699cb \
--user-data echo user data

mkdir /home/ec2-user/environment/brevity-infra/lambdas/build/$LAMBDANAME
cp -r /home/ec2-user/environment/brevity-infra/lib/* /home/ec2-user/environment/brevity-infra/lambdas/build/$LAMBDANAME
cp /home/ec2-user/environment/brevity-infra/lambdas/lambda_function_$LAMBDANAME.py /home/ec2-user/environment/brevity-infra/lambdas/build/$LAMBDANAME/lambda_function.py
cd /home/ec2-user/environment/brevity-infra/lambdas/build/$LAMBDANAME
zip -r ../$LAMBDANAME.zip *
aws s3 cp /home/ec2-user/environment/brevity-infra/lambdas/build/$LAMBDANAME.zip s3://brevity-deploy/infra/
aws lambda create-function --function-name $LAMBDANAME --runtime python3.8 --handler lambda_function.lambda_handler --role arn:aws:iam::000017942944:role/brevity-lambda --layers arn:aws:lambda:us-east-1:000017942944:layer:brevity-digitalocean:2 --code S3Bucket=brevity-deploy,S3Key=infra/$LAMBDANAME.zip --description 'Creates droplets and runs the provided operation.' --timeout 300 --package-type Zip