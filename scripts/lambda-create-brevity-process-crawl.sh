#!/bin/bash
LAMBDANAME="brevity-process-crawl"
mkdir /home/ec2-user/environment/brevity-infra/lambdas/build/$LAMBDANAME
cp -r /home/ec2-user/environment/brevity-infra/lib/* /home/ec2-user/environment/brevity-infra/lambdas/build/$LAMBDANAME
cp /home/ec2-user/environment/brevity-infra/lambdas/lambda_function_$LAMBDANAME.py /home/ec2-user/environment/brevity-infra/lambdas/build/$LAMBDANAME/lambda_function.py
cd /home/ec2-user/environment/brevity-infra/lambdas/build/$LAMBDANAME
zip -r ../$LAMBDANAME.zip *
aws s3 cp /home/ec2-user/environment/brevity-infra/lambdas/build/$LAMBDANAME.zip s3://brevity-deploy/infra/
aws lambda create-function --function-name $LAMBDANAME --runtime python3.7 --handler lambda_function.lambda_handler --role arn:aws:iam::000017942944:role/brevity-lambda --layers arn:aws:lambda:us-east-1:000017942944:layer:brevity-sonar:2 arn:aws:lambda:us-east-1:000017942944:layer:brevity-pandas:3 --code S3Bucket=brevity-deploy,S3Key=infra/$LAMBDANAME.zip --description 'Processes output from GoSpider crawl.' --timeout 300 --memory-size 10240 --package-type Zip