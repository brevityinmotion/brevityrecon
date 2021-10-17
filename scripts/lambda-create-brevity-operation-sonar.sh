#!/bin/bash
LAMBDANAME="brevity-operation-sonar"
mkdir /home/ec2-user/environment/brevityrecon/lambdas/build/$LAMBDANAME
cp -r /home/ec2-user/environment/brevityrecon/lib/* /home/ec2-user/environment/brevityrecon/lambdas/build/$LAMBDANAME
cp /home/ec2-user/environment/brevityrecon/lambdas/lambda_function_$LAMBDANAME.py /home/ec2-user/environment/brevityrecon/lambdas/build/$LAMBDANAME/lambda_function.py
cd /home/ec2-user/environment/brevityrecon/lambdas/build/$LAMBDANAME
zip -r ../$LAMBDANAME.zip *
aws s3 cp /home/ec2-user/environment/brevityrecon/lambdas/build/$LAMBDANAME.zip s3://brevity-deploy/infra/
aws lambda create-function --function-name $LAMBDANAME --runtime python3.7 --handler lambda_function.lambda_handler --role arn:aws:iam::000017942944:role/brevity-lambda --layers arn:aws:lambda:us-east-1:000017942944:layer:brevity-sonar:2 --code S3Bucket=brevity-deploy,S3Key=infra/$LAMBDANAME.zip --description 'Runs a sonar search for domains.' --timeout 600 --memory-size 256 --package-type Zip