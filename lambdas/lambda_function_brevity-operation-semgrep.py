import json, boto3, os, re
import brevitycore.core
import subprocess

def lambda_handler(event, context):
    
    def _getParameters(paramName):
        client = boto3.client('ssm')
        response = client.get_parameter(
            Name=paramName
        )
        return response['Parameter']['Value']
    
    inputBucketName = _getParameters('inputBucketName')
    
    if event['program'] is None:
        return {"isBase64Encoded":False,"statusCode":400,"body":json.dumps({"error":"Missing program name."})}
    if event['operation'] is None:
        operationName = 'axiom'
    else:
        operationName = str(event['operation']) 
    
    programName = str(event['program'])
    args0 = 'mkdir /tmp/repos'
    args1 = 'mkdir /tmp/output'
    args2 = "git clone https://github.com/aws/chalice.git"
    args3 = "semgrep --config=p/ci /tmp/repos/aws/chalice/ -o semgrep-chalice.json --json"
    
    popen = subprocess.Popen(args0, stdout=subprocess.PIPE)
    popen.wait()
    output = popen.stdout.read()
    print(output)
    
    #responseData = {
    #    'EC2 Connection': str(ec2Instance),
    #}
    
    #return {
    #    'statusCode': 200,
    #    'program': programName,
    #    'body': json.dumps(responseData)
    #}
    return output