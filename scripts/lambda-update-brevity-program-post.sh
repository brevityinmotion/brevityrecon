#!/bin/bash
LAMBDANAME="brevity-program-post"
DEPLOYBUCKET="brevity-deploy"
mkdir /home/ec2-user/environment/brevityrecon/lambdas/build/$LAMBDANAME
cp -r /home/ec2-user/environment/brevityrecon/lib/* /home/ec2-user/environment/brevityrecon/lambdas/build/$LAMBDANAME
cp /home/ec2-user/environment/brevityrecon/lambdas/lambda_function_$LAMBDANAME.py /home/ec2-user/environment/brevityrecon/lambdas/build/$LAMBDANAME/lambda_function.py
cd /home/ec2-user/environment/brevityrecon/lambdas/build/$LAMBDANAME
zip -r ../$LAMBDANAME.zip *
aws s3 cp /home/ec2-user/environment/brevityrecon/lambdas/build/$LAMBDANAME.zip s3://$DEPLOYBUCKET/infra/
aws lambda update-function-code --function-name $LAMBDANAME --s3-bucket $DEPLOYBUCKET --s3-key infra/$LAMBDANAME.zip