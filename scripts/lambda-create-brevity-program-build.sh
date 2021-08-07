#!/bin/bash
LAMBDANAME="brevity-program-build"
mkdir /home/ec2-user/environment/brevity-infra/lambdas/build/$LAMBDANAME
cp -r /home/ec2-user/environment/brevity-infra/lib/* /home/ec2-user/environment/brevity-infra/lambdas/build/$LAMBDANAME
cp /home/ec2-user/environment/brevity-infra/lambdas/lambda_function_$LAMBDANAME.py /home/ec2-user/environment/brevity-infra/lambdas/build/$LAMBDANAME/lambda_function.py
cd /home/ec2-user/environment/brevity-infra/lambdas/build/$LAMBDANAME
zip -r ../$LAMBDANAME.zip *
aws s3 cp /home/ec2-user/environment/brevity-infra/lambdas/build/$LAMBDANAME.zip s3://brevity-deploy/infra/
aws lambda create-function --function-name $LAMBDANAME --runtime python3.7 --handler lambda_function.lambda_handler --role arn:aws:iam::000017942944:role/brevity-lambda --code S3Bucket=brevity-deploy,S3Key=infra/$LAMBDANAME.zip --description 'Generates program specific scripts.' --timeout 60 --memory-size 128 --package-type Zip