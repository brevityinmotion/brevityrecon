import json, boto3, os, re
import urllib.parse
import brevityscope.process

def lambda_handler(event, context):
    
    def _getParameters(paramName):
        client = boto3.client('ssm')
        response = client.get_parameter(
            Name=paramName
        )
        return response['Parameter']['Value']
    
    refinedBucketPath = _getParameters('refinedBucketPath')
    presentationBucketPath = _getParameters('presentationBucketPath')

    # Get the object from the event and show its content type
    #bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    fileName = os.path.basename(key)
    programName = re.search("^[^-]*[^-]", fileName)
    programName = programName.group(0)
    
    publishStatus = brevityscope.process.publishUrls(programName, refinedBucketPath, presentationBucketPath)
    
    responseData = {
        'Status': str(publishStatus)
    }
    
    return {
        'statusCode': 200,
        'body': json.dumps(responseData)
    }