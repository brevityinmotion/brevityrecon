import json, boto3
import brevityoperations.droplet
import brevitycore.core

def lambda_handler(event, context):

    if event['queryStringParameters']['program'] is None:
        return {"isBase64Encoded":False,"statusCode":400,"body":json.dumps({"error":"Missing program name."})}
    if event['queryStringParameters']['operation'] is None:
        return {"isBase64Encoded":False,"statusCode":400,"body":json.dumps({"error":"Missing operation command."})}
    programName = str(event['queryStringParameters']['program'])
    runOperation = str(event['queryStringParameters']['operation'])
    
    dropletName = 'brevity-recon-' + programName
    
    secretName = 'digitalocean'
    regionName = 'us-east-1'
    accessToken = brevitycore.core.get_secret(secretName,regionName)
    
    secretName = 'brevity-aws-recon'
    secretRetrieved = brevitycore.core.get_secret(secretName,regionName)
    secretjson = json.loads(secretRetrieved)
    awsAccessKeyId = secretjson['AWS_ACCESS_KEY_ID']
    awsSecretKey = secretjson['AWS_SECRET_ACCESS_KEY']
    
    droplet = brevityoperations.droplet.loadDropletInfo(accessToken,dropletName)
    if droplet == 'NotFound':
        droplet = brevityoperations.droplet.createDroplet(accessToken,dropletName,runOperation,programName,awsAccessKeyId,awsSecretKey)
        dropletStatus = brevityoperations.droplet.getDropletStatus(droplet)
    droplet = brevityoperations.droplet.loadDropletInfo(accessToken,dropletName)
    # Take the droplet information and retrieve the IP address for the connection string
    dropletConnection = brevityoperations.droplet.retrieveDropletConnection(accessToken,dropletName)
    
    responseData = {
        'Droplet Connection': str(dropletConnection),
    }
    
    return {
        'statusCode': 200,
        'body': json.dumps(responseData)
    }