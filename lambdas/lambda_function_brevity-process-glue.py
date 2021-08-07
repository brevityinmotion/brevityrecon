import json, boto3, os

def lambda_handler(event, context):
    
    if event['program'] is None:
        return {"isBase64Encoded":False,"statusCode":400,"body":json.dumps({"error":"Missing program name."})}
    if event['operation'] is None:
        return {"isBase64Encoded":False,"statusCode":400,"body":json.dumps({"error":"Missing operation name."})}
    else:
        operationName = str(event['operation']) 
    
    programName = str(event['program'])
    
    client = boto3.client('glue')
    response = client.start_crawler(
        Name='brevity-httpx-recon'
    )
    
    responseData = {
        'Program Status': 'Success',
        'Operation Status': response
    }
    
    return {
        'statusCode': 200,
        'body': json.dumps(responseData)
    }