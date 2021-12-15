# Test event
#{
#  "program": "manual",
#  "operation": "interact",
#  "token": "fake",
#  "type": "client"
#}

import json, boto3, os, re
import brevitycore.core
import urllib.parse
import brevityprogram.programs
import brevityprogram.interact
import brevityoperations.droplet

def lambda_handler(event, context):
    
    def _getParameters(paramName):
        client = boto3.client('ssm')
        response = client.get_parameter(
            Name=paramName
        )
        return response['Parameter']['Value']
    
    inputBucketName = _getParameters('inputBucketName')
    
    if event['program'] is None:
        return {"isBase64Encoded":False,"statusCode":400,"body":json.dumps({"error":"Missing program name."})}
    if event['type'] is None:
        return {"isBase64Encoded":False,"statusCode":400,"body":json.dumps({"error":"Missing interact type."})}
    if event['operation'] is None:
        operationName = 'initial'
    else:
        operationName = str(event['operation']) 
    
    programName = str(event['program'])
    interactType = str(event['type'])
    taskToken = str(event['token'])
    
    operationStatus = brevityprogram.interact.prepareInteract(programName, inputBucketName, interactType)
    # Create installation file (bounty-startup-httpx.sh) to run on ephemeral server at startup
    installScriptStatus = brevityprogram.interact.generateInstallScriptInteract(inputBucketName)
    stepFunctionsStatus = brevityprogram.programs.generateScriptStepFunctions(programName, inputBucketName, taskToken, operationName)
    
    runOperation = 'interact'
    dropletName = 'keep-' + runOperation + '-' + interactType
    #print(dropletName)
    
    #runOperation = 'httpx'
    secretName = 'digitalocean'
    regionName = 'us-east-1'
    #secretDesc = 'API access token for Digital Ocean'

    accessToken = brevitycore.core.get_secret(secretName,regionName)
    
    secretName = 'brevity-aws-recon'
    secretRetrieved = brevitycore.core.get_secret(secretName,regionName)
    secretjson = json.loads(secretRetrieved)
    awsAccessKeyId = secretjson['AWS_ACCESS_KEY_ID']
    awsSecretKey = secretjson['AWS_SECRET_ACCESS_KEY']
    
    try:
        droplet = brevityoperations.droplet.loadDropletInfo(accessToken,dropletName)
    except:
        droplet = 'NotFound'
    if droplet == 'NotFound':
        droplet = brevityoperations.droplet.createDropletManual(accessToken,dropletName,runOperation,programName,awsAccessKeyId,awsSecretKey)
        dropletStatus = brevityoperations.droplet.getDropletStatus(droplet)
    droplet = brevityoperations.droplet.loadDropletInfo(accessToken,dropletName)
    # Take the droplet information and retrieve the IP address for the connection string
    dropletConnection = brevityoperations.droplet.retrieveDropletConnection(accessToken,dropletName)
    
    responseData = {
        'Droplet Connection': str(dropletConnection),
    }
    
    return {
        'statusCode': 200,
        'program': programName,
        'body': json.dumps(responseData)
    }