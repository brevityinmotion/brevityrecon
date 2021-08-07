import json, boto3, os

def lambda_handler(event, context):
    # This section validates whether the expected query parameters exist.
    if event['queryStringParameters']['program'] is None:
        return {"isBase64Encoded":False,"statusCode":400,"body":json.dumps({"error":"Missing program name."})}
    if event['queryStringParameters']['operation'] is None:
        return {"isBase64Encoded":False,"statusCode":400,"body":json.dumps({"error":"Missing operation name."})}
    programName = str(event['queryStringParameters']['program'])
    operationName = str(event['queryStringParameters']['operation'])
    
    # Prepare the initial input parameters for the AWS Step Functions state machine
    stateInput = f'''
    {{
      "program": "{programName}",
      "operation": "{operationName}"
    }}
    '''
    
    # Small function to retrieve SSM config parameter to avoid hard-coding
    def _getParameters(paramName):
        client = boto3.client('ssm')
        response = client.get_parameter(
            Name=paramName
        )
        return response['Parameter']['Value']
    
    # Retrieve step functions arn from AWS SSM parameter store service
    # stepfunctionsArn = 'arn:aws:states:us-east-1:000000000000:stateMachine:stateMachineName'
    stepfunctionsArn = _getParameters('stepfunctionsArn')
    
    # Begin execution of the AWS Step Function state machine
    client = boto3.client('stepfunctions')
    response = client.start_execution(
        stateMachineArn=stepfunctionsArn,
            input=stateInput
        )
    
    responseData = {
        'Program Status': 'Success',
    }
    
    # Provide a response back to the API call
    return {
        'statusCode': 200,
        'body': json.dumps(responseData)
    }