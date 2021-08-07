import boto3
import io
import botocore
import json
#from botocore.exceptions import ClientError
import logging
import brevitycore.core
import brevityprogram.dynamodb
import brevityscope.scope
import brevityscope.parser

def generate_program(programPlatform, inviteType, listscopein, listscopeout, programName, scopeInURLs, scopeInGithub, scopeInWild, scopeInGeneral, scopeInIP, scopeOutURLs, scopeOutGithub, scopeOutWild, scopeOutGeneral, scopeOutIP):
    try:
        # DynamoDB data load
        createStatus = brevityprogram.dynamodb.create_program(programName)
        scopeinStatus = brevityprogram.dynamodb.update_program_scopein(programName,listscopein)
        scopeoutStatus = brevityprogram.dynamodb.update_program_scopeout(programName,listscopeout)
        platformStatus = brevityprogram.dynamodb.update_program_platform(programName, programPlatform)
        inviteStatus = brevityprogram.dynamodb.update_invite_type(programName, inviteType)
        
        scopeStatus = brevityprogram.dynamodb.update_program_scopeinurls(programName,scopeInURLs)
        scopeStatus = brevityprogram.dynamodb.update_program_scopeingithub(programName,scopeInGithub)
        scopeStatus = brevityprogram.dynamodb.update_program_scopeinwild(programName,scopeInWild)
        scopeStatus = brevityprogram.dynamodb.update_program_scopeingeneral(programName,scopeInGeneral)
        scopeStatus = brevityprogram.dynamodb.update_program_scopeinIP(programName,scopeInIP)
        scopeStatus = brevityprogram.dynamodb.update_program_scopeouturls(programName,scopeOutURLs)
        scopeStatus = brevityprogram.dynamodb.update_program_scopeoutgithub(programName,scopeOutGithub)
        scopeStatus = brevityprogram.dynamodb.update_program_scopeoutwild(programName,scopeOutWild)
        scopeStatus = brevityprogram.dynamodb.update_program_scopeoutgeneral(programName,scopeOutGeneral)
        scopeStatus = brevityprogram.dynamodb.update_program_scopeoutIP(programName,scopeOutIP)
        
    except:
        return 'Program creation failed.'
    return 'Program successfully created.'

def generateProgramSyncScript(programName):
    secretName = 'brevity-aws-recon'
    regionName = 'us-east-1'
    secretRetrieved = brevitycore.core.get_secret(secretName,regionName)
    secretjson = json.loads(secretRetrieved)
    awsAccessKeyId = secretjson['AWS_ACCESS_KEY_ID']
    awsSecretKey = secretjson['AWS_SECRET_ACCESS_KEY']
    
    fileBuffer = io.StringIO()
    #fileBuffer.write("""#!/bin/bash
    fileContents = f"""#!/bin/bash

# AWS synchronization of data
    
# This information will be cleared every session as it is not persistent
export AWS_ACCESS_KEY_ID={awsAccessKeyId}
export AWS_SECRET_ACCESS_KEY={awsSecretKey}
export AWS_DEFAULT_REGION=us-east-1

export HOME=/root
mkdir $HOME/security/raw/{programName}
mkdir $HOME/security/refined/{programName}
mkdir $HOME/security/run/{programName}
mkdir $HOME/security/raw/{programName}/responses
mkdir $HOME/security/raw/{programName}/httpx
mkdir $HOME/security/raw/{programName}/crawl
mkdir $HOME/security/presentation
mkdir $HOME/security/presentation/{programName}
mkdir $HOME/security/presentation/{programName}/httpx
mkdir $HOME/security/presentation/{programName}/httpx-json

# Retrieve any configuration updates
aws s3 sync s3://brevity-inputs/config/ $HOME/security/config/

# Retrieve any new scopes specific for amass
aws s3 sync s3://brevity-inputs/scope/{programName}/ $HOME/security/tools/amass/

# Retrieve custom input scopes for programs
aws s3 sync s3://brevity-inputs/programs/{programName}/ $HOME/security/inputs/{programName}/

# Retrieve run files specific for program
aws s3 sync s3://brevity-inputs/run/{programName}/ $HOME/security/run/{programName}/
    
# Submit any new data
# aws s3 sync $HOME/security/raw/{programName}/ s3://brevity-data/raw/{programName}/
aws s3 sync $HOME/security/refined/{programName}/ s3://brevity-data/refined/{programName}/

# Load configs
aws s3 sync s3://brevity-inputs/tools/ $HOME/security/tools/

# Copy files from server post operations to S3 raw bucket
aws s3 cp --recursive $HOME/security/raw/{programName}/responses/ s3://brevity-raw/responses/{programName}/
aws s3 cp --recursive $HOME/security/raw/{programName}/httpx/ s3://brevity-raw/httpx/{programName}/
aws s3 cp --recursive $HOME/security/raw/{programName}/crawl/ s3://brevity-raw/crawl/{programName}/
aws s3 cp --recursive $HOME/security/presentation/{programName}/httpx-json/ s3://brevity-data/presentation/httpx-json/
aws s3 cp --recursive $HOME/security/presentation/{programName}/httpx/ s3://brevity-data/presentation/httpx/"""
    fileBuffer.write(fileContents)
    #objectBuffer = io.BytesIO(fileBuffer.getvalue().encode())
    return fileBuffer

def prepareProgram(programName,inputBucketName):
    fileBuffer = generateProgramSyncScript(programName)
    objectBuffer = io.BytesIO(fileBuffer.getvalue().encode())

    # Upload file to S3
    object_name = 'sync-' + programName + '.sh'
    object_path = 'run/' + programName + '/' + object_name
    status = brevitycore.core.upload_object(objectBuffer,inputBucketName,object_path)
    fileBuffer.close()
    objectBuffer.close()
    return status

def cleanupScopeFiles(dfIn):
    dfIn.columns=['ScopeIn']
    dfIn = dfIn[~dfIn.ScopeIn.str.contains('[ ]')]
    dfIn.ScopeIn = dfIn.ScopeIn.str.replace('https://','')
    dfIn.ScopeIn = dfIn.ScopeIn.str.replace('http://','')
    dfIn.ScopeIn = dfIn.ScopeIn.str.replace('\*.','')
    return dfIn

def generateScriptStepFunctions(programName, inputBucketName, taskToken, operationName):
    secretName = 'brevity-aws-recon'
    regionName = 'us-east-1'
    secretRetrieved = brevitycore.core.get_secret(secretName,regionName)
    secretjson = json.loads(secretRetrieved)
    awsAccessKeyId = secretjson['AWS_ACCESS_KEY_ID']
    awsSecretKey = secretjson['AWS_SECRET_ACCESS_KEY']

    stateInput = '{"program":"' + programName + '","operation":"' + operationName + '","statusCode":200}'
    fileBuffer = io.StringIO()
    fileContents = f"""#!/bin/bash

export AWS_ACCESS_KEY_ID={awsAccessKeyId}
export AWS_SECRET_ACCESS_KEY={awsSecretKey}
export AWS_DEFAULT_REGION=us-east-1

aws stepfunctions send-task-success --task-token {taskToken} --task-output '{stateInput}'"""

    fileBuffer.write(fileContents)
    objectBuffer = io.BytesIO(fileBuffer.getvalue().encode())
    # Upload file to S3
    object_name = 'stepfunctions-' + programName + '.sh'
    object_path = 'run/' + programName + '/' + object_name
    status = brevitycore.core.upload_object(objectBuffer,inputBucketName,object_path)
    fileBuffer.close()
    objectBuffer.close()
    return status

# This approach is no longer in-use. Moving functionality from DO Droplet to persistent EC2 instance that is always syncing S3 bucket of responses to attached EBS volume. Will eventually delete this function once the EC2 code is complete.
def generateScriptSift(programName, inputBucketName):
    
    secretName = 'brevity-aws-recon'
    regionName = 'us-east-1'
    secretRetrieved = brevitycore.core.get_secret(secretName,regionName)
    secretjson = json.loads(secretRetrieved)
    awsAccessKeyId = secretjson['AWS_ACCESS_KEY_ID']
    awsSecretKey = secretjson['AWS_SECRET_ACCESS_KEY']
    fileBuffer = io.StringIO()
    fileContents = f"""#!/bin/bash

export AWS_ACCESS_KEY_ID={awsAccessKeyId}
export AWS_SECRET_ACCESS_KEY={awsSecretKey}
export AWS_DEFAULT_REGION=us-east-1

# Run custom sift script
export HOME=/root
export PATH=/root/go/bin:$PATH

# Retrieve zipped and compressed responses file
aws s3 cp s3://brevity-data/refined/{programName}/{programName}-responses.tar.gz $HOME/security/raw/{programName}/

wait
cd $HOME/security/raw/{programName}/
tar -xvzf {programName}-responses.tar.gz
wait
sift -f $HOME/security/config/search-keywords.csv $HOME/security/raw/{programName}/responses -o matches-{programName}-keywords.txt --only-matching
wait
sift -f $HOME/security/config/search-extensions.csv $HOME/security/raw/{programName}/responses -o matches-{programName}-extensions.txt --only-matching
wait
sift -f $HOME/security/config/search-filenames.csv $HOME/security/raw/{programName}/responses -o matches-{programName}-filenames.txt --only-matching
wait
sift -f $HOME/security/config/search-phrases.csv $HOME/security/raw/{programName}/responses -o matches-{programName}-phrases.txt --only-matching
wait
sleep 10
mv $HOME/security/raw/{programName}/matches-* $HOME/security/refined/{programName}/
sleep 10
# rm -r responses
# sleep 10
sh $HOME/security/config/sync-{programName}.sh"""

    fileBuffer.write(fileContents)
    objectBuffer = io.BytesIO(fileBuffer.getvalue().encode())
    # Upload file to S3
    object_name = 'sift-' + programName + '.sh'
    object_path = 'run/' + programName + '/' + object_name
    status = brevitycore.core.upload_object(objectBuffer,inputBucketName,object_path)
    fileBuffer.close()
    objectBuffer.close()
    return status

# Thank you Arkadiy Tetelman (https://github.com/arkadiyt) for the great work that you do! Also be sure to checkout his Data Driven Bug Bounty talk as it is excellent (https://www.youtube.com/watch?v=2TWY74MgTrc&t=1139s)!
def getBugcrowdPrograms():
    import ast
    import urllib.request, json
    import pandas as pd

    def _parseScopeIn(scopeIn):
        targetData = []
        if not scopeIn:
            return targetData
        smallAll = str(scopeIn)[1:-1]
        scopeLength = len(scopeIn)
        smallData = ast.literal_eval(smallAll)

        if (scopeLength > 1):
            for item in smallData:
                targetData.append(item.get('target'))
            return targetData
        else:
            targetData.append(smallData.get('target'))
            return targetData
    def _parseScopeOut(scopeOut):
        targetData = []
        if not scopeOut:
            targetData.append('icicles.io')
            return targetData
        smallAll = str(scopeOut)[1:-1]
        scopeLength = len(scopeOut)
        smallData = ast.literal_eval(smallAll)

        if (scopeLength > 1):
            for item in smallData:
                targetData.append(item.get('target'))
            return targetData
        else:
            targetData.append(smallData.get('target'))
            return targetData
    def _parseProgramUrl(programUrl):
        programName = programUrl.rsplit('/', 1)[-1]
        return programName
    # File is updated hourly
    filePath = 'https://raw.githubusercontent.com/arkadiyt/bounty-targets-data/master/data/bugcrowd_data.json'
    with urllib.request.urlopen(filePath) as url:
        data = json.loads(url.read().decode())

    dfPublicPrograms = pd.json_normalize(data)
    dfPublicPrograms['programPlatform'] = 'Bugcrowd'
    dfPublicPrograms['inviteType'] = 'Public'
    dfPublicPrograms['ScopeIn'] = dfPublicPrograms['targets.in_scope'].apply(_parseScopeIn)
    dfPublicPrograms['ScopeOut'] = dfPublicPrograms['targets.out_of_scope'].apply(_parseScopeOut)
    dfPublicPrograms['ProgramName'] = dfPublicPrograms['url'].apply(_parseProgramUrl)
    dfPublicPrograms = dfPublicPrograms.rename(columns={'name':'description'})
    
    return dfPublicPrograms

# Arkadiy Tetelman (https://twitter.com/arkadiyt) again for the win!!
def getHackerOnePrograms():
    import ast
    import urllib.request, json
    import pandas as pd

    def _parseScopeIn(scopeIn):
        targetData = []
        if not scopeIn:
            return targetData
        smallAll = str(scopeIn)[1:-1]
        scopeLength = len(scopeIn)
        smallData = ast.literal_eval(smallAll)

        if (scopeLength > 1):
            for item in smallData:
                targetData.append(item.get('target'))
            return targetData
        else:
            targetData.append(smallData.get('target'))
            return targetData
    def _parseScopeOut(scopeOut):
        targetData = []
        if not scopeOut:
            # Some things break when there is no out-of-scope domain so this is my own domain. For example, amass does not like it if you send it the out of scope syntax and file path but have zero entries in the file.
            targetData.append('icicles.io')
            return targetData
        # This is removing quotes from the first and last characters of the input. This seemed like the best way to clean this without removing quotes within the content.
        smallAll = str(scopeOut)[1:-1]
        scopeLength = len(scopeOut)
        smallData = ast.literal_eval(smallAll)

        if (scopeLength > 1):
            for item in smallData:
                targetData.append(item.get('target'))
            return targetData
        else:
            targetData.append(smallData.get('target'))
            return targetData
    def _parseProgramUrl(programUrl):
        programName = programUrl.rsplit('/', 1)[-1]
        return programName
    # File is updated hourly
    filePath = 'https://raw.githubusercontent.com/arkadiyt/bounty-targets-data/master/data/hackerone_data.json'
    with urllib.request.urlopen(filePath) as url:
        data = json.loads(url.read().decode())

    dfPublicPrograms = pd.json_normalize(data)
    dfPublicPrograms['programPlatform'] = 'HackerOne'
    dfPublicPrograms['inviteType'] = 'Public'
    dfPublicPrograms['ScopeIn'] = dfPublicPrograms['targets.in_scope'].apply(_parseScopeIn)
    dfPublicPrograms['ScopeOut'] = dfPublicPrograms['targets.out_of_scope'].apply(_parseScopeOut)
    dfPublicPrograms['ProgramName'] = dfPublicPrograms['handle'].apply(_parseProgramUrl)
    dfPublicPrograms = dfPublicPrograms.rename(columns={'name':'description'})
    
    return dfPublicPrograms