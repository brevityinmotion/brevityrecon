import json, io
import boto3

def createEC2(runOperation,programName):
    def _generateUserDataScript(runOperation,programName):
        import io
        fileBuffer = io.StringIO()
        fileContents = f"""#cloud-config
    packages:
     - awscli

    runcmd:
     - mkdir /home/ec2-user/security
     - mkdir /home/ec2-user/security/config
     - mkdir /home/ec2-user/security/run
     - mkdir /home/ec2-user/security/run/{programName}
     - sudo mkfs -t xfs /dev/nvme1n1
     - sudo mkdir /data
     - sudo mount /dev/nvme1n1 /data
     - export AWS_DEFAULT_REGION=us-east-1
     - aws s3 sync s3://brevity-inputs/config/ /home/ec2-user/security/config/
     - wait
     - bash /home/ec2-user/security/config/bounty-startup-{runOperation}.sh"""
     
        userData = fileContents
        return userData
    
    userData = _generateUserDataScript(runOperation,programName)
    
    def _getParameters(paramName):
        client = boto3.client('ssm')
        response = client.get_parameter(
            Name=paramName
        )
        return response['Parameter']['Value']
    
    brevityEBSKeyId = _getParameters('brevityEBSKeyId')
    
    ec2_client = boto3.client('ec2', region_name='us-east-1')
    
    instances = ec2_client.run_instances(
        BlockDeviceMappings=[
            {
                'DeviceName': '/dev/sdf',
                'VirtualName': 'brevity-recon',
                'Ebs': {
                    'DeleteOnTermination': False,
                    'VolumeSize': 200,
                    'VolumeType': 'gp2',
                    'KmsKeyId': brevityEBSKeyId,
                    'Encrypted': True
                },
            },
        ],
        ImageId='ami-0c2b8ca1dad447f8a',
        MinCount=1,
        MaxCount=1,
        InstanceType="t3.medium",
        IamInstanceProfile={
            'Name': 'brevity-ec2'
        },
        KeyName="brevity-recon",
        SecurityGroups=["brevity-ec2"],
        UserData=userData,
    )
    
    return instances