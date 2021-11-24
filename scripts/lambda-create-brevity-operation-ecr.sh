#!/bin/bash
LAMBDANAME="brevity-operation-ecr"
#RESOURCENAME="brevity-container-docker"
#ECRREGISTRY="000017942944.dkr.ecr.us-east-1.amazonaws.com/"
ECRPATH="000017942944.dkr.ecr.us-east-1.amazonaws.com/brevity-container-docker:latest"

#mkdir /home/ec2-user/environment/brevityrecon/lambdas/build/$LAMBDANAME
#cp -r /home/ec2-user/environment/brevityrecon/lib/* /home/ec2-user/environment/brevityrecon/lambdas/build/$LAMBDANAME
#cp /home/ec2-user/environment/brevityrecon/lambdas/lambda_function_$LAMBDANAME.py /home/ec2-user/environment/brevityrecon/lambdas/build/$LAMBDANAME/lambda_function.py
#cd /home/ec2-user/environment/brevityrecon/lambdas/build/$LAMBDANAME
#zip -r ../$LAMBDANAME.zip *
#aws s3 cp /home/ec2-user/environment/brevityrecon/lambdas/build/$LAMBDANAME.zip s3://brevity-deploy/infra/
#aws lambda create-function --function-name $LAMBDANAME --runtime python3.8 --handler lambda_function.lambda_handler --role arn:aws:iam::000017942944:role/brevity-lambda --layers arn:aws:lambda:us-east-1:000017942944:layer:brevity-docker:1 --code S3Bucket=brevity-deploy,S3Key=infra/$LAMBDANAME.zip --description 'Copies DockerHub images into private ECR repos' --timeout 300 --memory-size 512 --package-type Zip
aws lambda create-function --function-name $LAMBDANAME --region us-east-1 --package-type Image --code ImageUri=$ECRPATH   --role arn:aws:iam::000017942944:role/brevity-lambda --description 'Copies DockerHub images into private ECR repos' --timeout 300 --memory-size 512