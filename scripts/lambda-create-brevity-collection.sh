#!/bin/bash
LAMBDANAME="brevity-collection"
mkdir /home/ec2-user/environment/brevityrecon/lambdas/build/$LAMBDANAME
cp -r /home/ec2-user/environment/brevityrecon/lib/* /home/ec2-user/environment/brevityrecon/lambdas/build/$LAMBDANAME
cp /home/ec2-user/environment/brevityrecon/lambdas/lambda_function_$LAMBDANAME.py /home/ec2-user/environment/brevityrecon/lambdas/build/$LAMBDANAME/lambda_function.py
cd /home/ec2-user/environment/brevityrecon/lambdas/build/$LAMBDANAME
zip -r ../$LAMBDANAME.zip *
aws s3 cp /home/ec2-user/environment/brevityrecon/lambdas/build/$LAMBDANAME.zip s3://brevity-deploy/infra/
aws lambda create-function --function-name $LAMBDANAME --runtime python3.8 --handler lambda_function.lambda_handler --role arn:aws:iam::000017942944:role/brevity-lambda --code S3Bucket=brevity-deploy,S3Key=infra/$LAMBDANAME.zip --description 'Performs request collection.' --timeout 300 --package-type Zip