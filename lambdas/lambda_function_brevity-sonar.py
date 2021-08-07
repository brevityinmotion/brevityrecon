import json, boto3, os, re
import urllib.parse
import brevitycore.sonar

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
    
    # Get the object from the event and show its content type
    #bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    fileName = os.path.basename(key)
    programName = re.search("^[^-]*[^-]", fileName)
    programName = programName.group(0)
    
    execid = brevitycore.sonar.sonarGenerateSubdomains(programName, refinedBucketPath, ATHENA_DB, ATHENA_BUCKET, ATHENA_TABLE)
    sonarRetrieveStatus = brevitycore.sonar.sonarRetrieveResults(programName, execid, refinedBucketPath)
    
    if (sonarRetrieveStatus == 'Subdomains successfully generated'):
        sonarLoadStatus = brevitycore.sonar.sonarLoadSubdomains(programName, refinedBucketPath, programInputBucketPath)
    else: sonarLoadStatus = 'No subdomains loaded'
    
    responseData = {
        'Sonar Execution Id': str(execid),
        'Sonar Retrieve Status': str(sonarRetrieveStatus),
        'Sonar Load Status': str(sonarLoadStatus)
    }
    
    return {
        'statusCode': 200,
        'body': json.dumps(responseData)
    }