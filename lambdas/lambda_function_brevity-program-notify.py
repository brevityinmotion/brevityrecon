import json, boto3
import brevitycore.core

def lambda_handler(event, context):
    
    if event['program'] is None:
        return {"isBase64Encoded":False,"statusCode":400,"body":json.dumps({"error":"Missing program name."})}
    if event['operation'] is None:
        return {"isBase64Encoded":False,"statusCode":400,"body":json.dumps({"error":"Missing operation name."})}
    else:
        operationName = str(event['operation']) 
        
    programName = str(event['program'])
    
    def _getParameters(paramName):
        client = boto3.client('ssm')
        response = client.get_parameter(
            Name=paramName
        )
        return response['Parameter']['Value']
    
    phoneNumber = _getParameters('phoneNumber')
    message = programName + ' recon complete.'
    
    notifyStatus = brevitycore.core.notify_user(phoneNumber,message)
    
    return {
        "isBase64Encoded":False,
        "statusCode":200,
        "body":json.dumps("Notification sent.")
    }