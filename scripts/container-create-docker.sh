#!/bin/bash
RESOURCENAME="brevity-container-docker"
ECRREGISTRY="000017942944.dkr.ecr.us-east-1.amazonaws.com/"
ECRPATH="000017942944.dkr.ecr.us-east-1.amazonaws.com/brevity-container-docker"
#ECRPATH=$ECRREGISTRY + $LAMBDANAME
mkdir /home/ec2-user/environment/brevityrecon/containers/build/$RESOURCENAME
#cp /home/ec2-user/environment/brevityrecon/lambdas/lambda_function_$LAMBDANAME.py /home/ec2-user/environment/brevityrecon/containers/build/$LAMBDANAME/lambda_function.py
cp /home/ec2-user/environment/brevityrecon/containers/container_function_$RESOURCENAME.py /home/ec2-user/environment/brevityrecon/containers/build/$RESOURCENAME/lambda_function.py
cp /home/ec2-user/environment/brevityrecon/containers/dockerfile_$RESOURCENAME /home/ec2-user/environment/brevityrecon/containers/build/$RESOURCENAME/dockerfile
cp /home/ec2-user/environment/brevityrecon/containers/requirements_$RESOURCENAME.txt /home/ec2-user/environment/brevityrecon/containers/build/$RESOURCENAME/requirements.txt
cp /home/ec2-user/environment/brevityrecon/containers/run_$RESOURCENAME.sh /home/ec2-user/environment/brevityrecon/containers/build/$RESOURCENAME/run.sh
cd /home/ec2-user/environment/brevityrecon/containers/build/$RESOURCENAME
docker build -t $RESOURCENAME .
docker tag $RESOURCENAME $ECRPATH
aws ecr get-login-password --region 'us-east-1' | docker login --username AWS --password-stdin $ECRREGISTRY
aws ecr create-repository --repository-name $RESOURCENAME --image-scanning-configuration scanOnPush=true --region 'us-east-1'
docker push $ECRPATH
#zip -r ../$LAMBDANAME.zip *
#aws s3 cp /home/ec2-user/environment/brevityrecon/containers/build/$LAMBDANAME.zip s3://brevity-deploy/infra/
#aws lambda create-function --function-name $LAMBDANAME --runtime python3.8 --handler lambda_function.lambda_handler --role arn:aws:iam::000017942944:role/brevity-lambda --layers arn:aws:lambda:us-east-1:000017942944:layer:brevity-docker:1 --code S3Bucket=brevity-deploy,S3Key=infra/$LAMBDANAME.zip --description 'Copies DockerHub images into private ECR repos' --timeout 300 --memory-size 512 --package-type Zip





#FROM public.ecr.aws/lambda/python:3.8

# Copy function code
#COPY app.py ${LAMBDA_TASK_ROOT}

# Install the function's dependencies using file requirements.txt
# from your project folder.

#COPY requirements.txt  .
#RUN  pip3 install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
#CMD [ "app.handler" ] 

#public.ecr.aws/eks-distro-build-tooling/eks-distro-minimal-base-docker-client:latest