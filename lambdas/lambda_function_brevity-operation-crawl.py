import json, boto3, os, re
import urllib.parse
import brevityprogram.gospider
import brevityprogram.programs
import brevitycore.core
import brevityoperations.droplet
import brevityscope.process

def lambda_handler(event, context):
    
    if event['program'] is None:
        return {"isBase64Encoded":False,"statusCode":400,"body":json.dumps({"error":"Missing program name."})}
    if event['operation'] is None:
        return {"isBase64Encoded":False,"statusCode":400,"body":json.dumps({"error":"Missing operation name."})}
    else:
        operationName = 'crawl'
    
    programName = str(event['program'])
    taskToken = str(event['token'])
    
    def _getParameters(paramName):
        client = boto3.client('ssm')
        response = client.get_parameter(
            Name=paramName
        )
        return response['Parameter']['Value']
    
    inputBucketName = _getParameters('inputBucketName')
    rawBucketPath = _getParameters('rawBucketPath')
    refinedBucketPath = _getParameters('refinedBucketPath')
    inputBucketPath = _getParameters('inputBucketPath')
    programInputBucketPath = _getParameters('programInputBucketPath')
    inputBucketName = _getParameters('inputBucketName')

    goSpiderStatus = brevityprogram.gospider.generateScriptGoSpider(programName,inputBucketName)
    # Create installation file (bounty-startup-crawl.sh) to run on ephemeral server at startup
    installScriptStatus = brevityprogram.gospider.generateInstallScriptGoSpider(inputBucketName)
    stepFunctionsStatus = brevityprogram.programs.generateScriptStepFunctions(programName, inputBucketName, taskToken, operationName)
    
    runOperation = 'crawl'
    dropletName = 'brevity-' + runOperation + '-' + programName
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
    
    droplet = brevityoperations.droplet.loadDropletInfo(accessToken,dropletName)
    if droplet == 'NotFound':
        droplet = brevityoperations.droplet.createDroplet(accessToken,dropletName,runOperation,programName,awsAccessKeyId,awsSecretKey)
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
        'operation': operationName,
        'body': json.dumps(responseData)
    }