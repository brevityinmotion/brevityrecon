import json, boto3, os
import brevityprogram.programs
import brevityscope.scope

def lambda_handler(event, context):

    def _getParameters(paramName):
        client = boto3.client('ssm')
        response = client.get_parameter(
            Name=paramName
        )
        return response['Parameter']['Value']
    
    dataBucketName = _getParameters('dataBucketName')
    graphBucketName = _getParameters('graphBucketName')
    inputBucketName = _getParameters('inputBucketName')
    graphBucketPath = _getParameters('graphBucketPath')
    rawBucketPath = _getParameters('rawBucketPath')
    refinedBucketPath = _getParameters('refinedBucketPath')
    inputBucketPath = _getParameters('inputBucketPath')
    programInputBucketPath = _getParameters('programInputBucketPath')
    presentationBucketPath = _getParameters('presentationBucketPath')
    
    eventinput = json.loads(event['body'])
    
    if eventinput['program'] is None:
        return {"isBase64Encoded":False,"statusCode":400,"body":json.dumps({"error":"Missing program name."})}
    programName = str(eventinput['program'])
    listscopein = list(eventinput['scopein'])
    listscopeout = list(eventinput['scopeout'])
    programPlatform = str(eventinput['platform'])
    inviteType = str(eventinput['invite'])
    
    # Extrapolate scope based on general in and out items
    ScopeInURLs, ScopeInGithub, ScopeInWild, ScopeInGeneral, ScopeInIP, ScopeOutURLs, ScopeOutGithub, ScopeOutWild, ScopeOutGeneral, ScopeOutIP = brevityscope.scope.extrapolateScope(programName, listscopein, listscopeout)
    
    programStatus = brevityprogram.programs.generate_program(programPlatform, inviteType, listscopein, listscopeout, programName, ScopeInURLs, ScopeInGithub, ScopeInWild, ScopeInGeneral, ScopeInIP, ScopeOutURLs, ScopeOutGithub, ScopeOutWild, ScopeOutGeneral, ScopeOutIP)
    
    operationName = 'initial'

    stateInput = f'''
    {{
      "program": "{programName}",
      "operation": "{operationName}"
    }}
    '''

    my_state_machine_arn = 'arn:aws:states:us-east-1:000017942944:stateMachine:brevity-recon'
    client = boto3.client('stepfunctions')
    response = client.start_execution(
        stateMachineArn=my_state_machine_arn,
            input=stateInput
        )
    
    responseData = {
        'Program Status': str(programStatus),
    }
    
    return {
        'statusCode': 200,
        'body': json.dumps(responseData)
    }