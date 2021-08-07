import json, boto3, os, re
import urllib.parse
import brevityprogram.dynamodb
import brevityscope.parser
import brevityprogram.programs
import datetime

def lambda_handler(event, context):
    
    def _getParameters(paramName):
        client = boto3.client('ssm')
        response = client.get_parameter(
            Name=paramName
        )
        return response['Parameter']['Value']
    
    inputBucketName = _getParameters('inputBucketName')
    refinedBucketPath = _getParameters('refinedBucketPath')
    inputBucketPath = _getParameters('inputBucketPath')
    programInputBucketPath = _getParameters('programInputBucketPath')
    ATHENA_BUCKET = _getParameters('ATHENA_BUCKET')
    ATHENA_DB = _getParameters('ATHENA_DB')
    ATHENA_TABLE = _getParameters('ATHENA_TABLE')
    
    if event['program'] is None:
        return {"isBase64Encoded":False,"statusCode":400,"body":json.dumps({"error":"Missing program name."})}
    if event['operation'] is None:
        return {"isBase64Encoded":False,"statusCode":400,"body":json.dumps({"error":"Missing operation name."})}
    programName = str(event['program'])
    operationName = str(event['operation']) 

    programPlatform, inviteType, listscopein, listscopeout, ScopeInURLs, ScopeInGithub, ScopeInWild, ScopeInGeneral, ScopeInIP, ScopeOutURLs, ScopeOutGithub, ScopeOutWild, ScopeOutGeneral, ScopeOutIP = brevityprogram.dynamodb.getProgramInfo(programName)
    ScopeInURLs, ScopeInGithub, ScopeInWild, ScopeInGeneral, ScopeInIP, ScopeOutURLs, ScopeOutGithub, ScopeOutWild, ScopeOutGeneral, ScopeOutIP = brevityscope.scope.extrapolateScope(programName, listscopein, listscopeout)
    programStatus = brevityprogram.programs.generate_program(programPlatform, inviteType, listscopein, listscopeout, programName, ScopeInURLs, ScopeInGithub, ScopeInWild, ScopeInGeneral, ScopeInIP, ScopeOutURLs, ScopeOutGithub, ScopeOutWild, ScopeOutGeneral, ScopeOutIP)
    programConfiguration = brevityprogram.programs.prepareProgram(programName,inputBucketName)

    # Separate generation
    generationStatus = brevityscope.parser.generateInitialDomains(programName, refinedBucketPath, ScopeInGeneral, programInputBucketPath)

    # Insert recon timestamp into DynamoDB to track reconnaisance
    reconDate = str(datetime.datetime.now().date().isoformat())
    timeStatus = brevityprogram.dynamodb.update_program_latestRecon(programName,reconDate)

    
    responseData = {
        'Program Status': str(generationStatus)
    }
    
    return {
        'statusCode': 200,
        'program': programName,
        'operation': operationName,
        'body': json.dumps(responseData)
    }