import json, boto3, os
#import brevityprogram.programs
#import brevityscope.scope

def lambda_handler(event, context):

    #def _getParameters(paramName):
    #    client = boto3.client('ssm')
    #    response = client.get_parameter(
    #        Name=paramName
    #    )
    #    return response['Parameter']['Value']
    
    #dataBucketName = _getParameters('dataBucketName')
    #graphBucketName = _getParameters('graphBucketName')
    #inputBucketName = _getParameters('inputBucketName')
    #graphBucketPath = _getParameters('graphBucketPath')
    #rawBucketPath = _getParameters('rawBucketPath')
    #refinedBucketPath = _getParameters('refinedBucketPath')
    #inputBucketPath = _getParameters('inputBucketPath')
    #programInputBucketPath = _getParameters('programInputBucketPath')
    #presentationBucketPath = _getParameters('presentationBucketPath')
    #stepfunctionsArn = _getParameters('stepfunctionsArn')
    
    eventinput = json.loads(event['body'])
    print(eventinput)
    
    responseData = {
        'Error',
    }
    
    return {
        'statusCode': 200,
        'body': json.dumps(responseData)
    }