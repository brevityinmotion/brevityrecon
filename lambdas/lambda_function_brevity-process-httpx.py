import json, boto3, os, re
import brevitycore.core
import urllib.parse
import brevityscope.process

def lambda_handler(event, context):
    
    def _getParameters(paramName):
        client = boto3.client('ssm')
        response = client.get_parameter(
            Name=paramName
        )
        return response['Parameter']['Value']
    
    rawBucketPath = _getParameters('rawBucketPath')
    refinedBucketPath = _getParameters('refinedBucketPath')
    inputBucketPath = _getParameters('inputBucketPath')
    programInputBucketPath = _getParameters('programInputBucketPath')
    presentationBucketPath = _getParameters('presentationBucketPath')
    
    if event['program'] is None:
        return {"isBase64Encoded":False,"statusCode":400,"body":json.dumps({"error":"Missing program name."})}
    if event['operation'] is None:
        return {"isBase64Encoded":False,"statusCode":400,"body":json.dumps({"error":"Missing operation name."})}
    else:
        operationName = str(event['operation']) 
    
    programName = str(event['program'])
    
    processHTTPXStatus = brevityscope.process.processHttpx(programName, refinedBucketPath, inputBucketPath, presentationBucketPath, operationName, programInputBucketPath)
    
    responseData = {
        'status': str(processHTTPXStatus),
    }
    
    return {
        'statusCode': 200,
        'program': programName,
        'operation': operationName,
        'body': json.dumps(responseData)
    }