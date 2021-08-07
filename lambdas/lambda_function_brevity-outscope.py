import json, boto3, os, re
import urllib.parse
import brevityscope.process

def lambda_handler(event, context):
    
    # TODO implement
    def _getParameters(paramName):
        client = boto3.client('ssm')
        response = client.get_parameter(
            Name=paramName
        )
        return response['Parameter']['Value']
    
    refinedBucketPath = _getParameters('refinedBucketPath')
    inputBucketPath = _getParameters('inputBucketPath')

    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    fileName = os.path.basename(key)
    programName = re.search("^[^-]*[^-]", fileName)
    programName = programName.group(0)
    
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('bugbounty')
    resp = table.get_item(
        Key={
            'ProgramName' : programName,
        }
    )
    
    listscopeout = resp['Item']['ScopeOut']
    scopeStatus = brevityscope.process.removeOutScope(programName, refinedBucketPath, inputBucketPath, listscopeout)

    responseData = {
        'Scope Status': str(scopeStatus)
    }
    
    return {
        'statusCode': 200,
        'body': json.dumps(responseData)
    }