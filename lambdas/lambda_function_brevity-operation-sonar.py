import json, boto3, os, re
import urllib.parse
import brevityprogram.sonar

def lambda_handler(event, context):
    
    def _getParameters(paramName):
        client = boto3.client('ssm')
        response = client.get_parameter(
            Name=paramName
        )
        return response['Parameter']['Value']
    
    refinedBucketPath = _getParameters('refinedBucketPath')
    inputBucketPath = _getParameters('inputBucketPath')
    programInputBucketPath = _getParameters('programInputBucketPath')
    ATHENA_BUCKET = _getParameters('ATHENA_BUCKET')
    ATHENA_DB = _getParameters('ATHENA_DB')
    ATHENA_TABLE = _getParameters('ATHENA_TABLE')
    
    if event['program'] is None:
        return {"isBase64Encoded":False,"statusCode":400,"body":json.dumps({"error":"Missing program name."})}
    if event['operation'] is None:
        return {"isBase64Encoded":False,"statusCode":400,"body":json.dumps({"error":"Missing operation name."})}
    programName = str(event['program'])
    operationName = str(event['operation'])
    
    execid = brevityprogram.sonar.sonarRun(programName,refinedBucketPath,ATHENA_DB,ATHENA_BUCKET,ATHENA_TABLE)
    
    if (execid == 'No Wildcards'):
        return {
            'statusCode': 200,
            'program': programName,
            'operation': operationName,
            'body': json.dumps(execid)
        }
        
    else:
        sonarRetrieveStatus = brevityprogram.sonar.sonarRetrieveResults(programName, execid, refinedBucketPath)
    
        if (sonarRetrieveStatus == 'Subdomains successfully generated'):
            sonarLoadStatus = brevityprogram.sonar.sonarLoadSubdomains(programName, refinedBucketPath, programInputBucketPath)
        else: sonarLoadStatus = 'No subdomains loaded'
  
        responseData = {
            'Status': 'Success'
        }
        
        return {
            'statusCode': 200,
            'program': programName,
            'operation': operationName,
            'body': json.dumps(responseData)
        }