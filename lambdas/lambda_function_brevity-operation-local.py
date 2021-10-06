import json, boto3, os, re
import brevitycore.core
import urllib.parse
import brevityprogram.local
import brevityoperations.ec2

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
    if event['operation'] is None:
        operationName = 'axiom'
    else:
        operationName = str(event['operation']) 
    
    programName = str(event['program'])

    # Generate Axiom installation script
    
    localStatus = brevityprogram.local.prepareLocal(programName, inputBucketName)
    # Create installation file (bounty-startup-local.sh) to run on server at startup
    installScriptStatus = brevityprogram.local.generateInstallScriptLocal(inputBucketName)
    # Create EC2 instance and run local installation startup script
    ec2Instance = brevityoperations.ec2.createEC2(operationName,programName)
    
    responseData = {
        'EC2 Connection': str(ec2Instance),
    }
    
    return {
        'statusCode': 200,
        'program': programName,
        'body': json.dumps(responseData)
    }