import json, boto3
import ast
import urllib.request
import pandas as pd
import numpy as np
import brevityscope.scope
import brevityprogram.programs

def lambda_handler(event, context):
    
    if event['program'] is None:
        return {"isBase64Encoded":False,"statusCode":400,"body":json.dumps({"error":"Missing program name."})}
    if event['operation'] is None:
        return {"isBase64Encoded":False,"statusCode":400,"body":json.dumps({"error":"Missing operation name."})}
    programName = str(event['program'])
    operationName = str(event['operation']) 
    
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
    
    def bulkLoadPrograms(programPlatform, inviteType, ScopeIn, ScopeOut, programName, ScopeInURLs, ScopeInGithub, ScopeInWild, ScopeInGeneral, ScopeInIP, ScopeOutURLs, ScopeOutGithub, ScopeOutWild, ScopeOutGeneral, ScopeOutIP):
        programStatus = brevityprogram.programs.generate_program(programPlatform, inviteType, ScopeIn, ScopeOut, programName, ScopeInURLs, ScopeInGithub, ScopeInWild, ScopeInGeneral, ScopeInIP, ScopeOutURLs, ScopeOutGithub, ScopeOutWild, ScopeOutGeneral, ScopeOutIP)
        return 'Success'
    
    def bulkLoadBugcrowd():
        # Retrieve Bugcrowd
        filePath = 'https://raw.githubusercontent.com/arkadiyt/bounty-targets-data/master/data/bugcrowd_data.json'
        with urllib.request.urlopen(filePath) as url:
            data = json.loads(url.read().decode())
    
        dfPublicPrograms = pd.json_normalize(data)
        dfPublicPrograms['programPlatform'] = 'Bugcrowd'
        dfPublicPrograms['inviteType'] = 'Public'
        dfPublicPrograms['ScopeIn'] = dfPublicPrograms['targets.in_scope'].apply(brevityscope.scope.parseScopeIn)
        dfPublicPrograms['ScopeOut'] = dfPublicPrograms['targets.out_of_scope'].apply(brevityscope.scope.parseScopeOut)
        dfPublicPrograms['ProgramName'] = dfPublicPrograms['url'].apply(brevityscope.scope.parseProgramUrl)
        dfPublicPrograms = dfPublicPrograms.rename(columns={'name':'description'})

        dfPublicPrograms['ScopeInURLs'] = dfPublicPrograms['ScopeIn'].apply(brevityscope.scope.cleanupScopeStrict)
        dfPublicPrograms['ScopeInGithub'] = dfPublicPrograms['ScopeIn'].apply(brevityscope.scope.cleanupScopeGithub)
        dfPublicPrograms['ScopeInWild'] = dfPublicPrograms['ScopeIn'].apply(brevityscope.scope.cleanupScopeWild)
        dfPublicPrograms['ScopeInGeneral'] = dfPublicPrograms['ScopeIn'].apply(brevityscope.scope.cleanupScopeGeneral)
        dfPublicPrograms['ScopeInIP'] = dfPublicPrograms['ScopeIn'].apply(brevityscope.scope.cleanupScopeIP)
        dfPublicPrograms['ScopeOutURLs'] = dfPublicPrograms['ScopeOut'].apply(brevityscope.scope.cleanupScopeStrict)
        dfPublicPrograms['ScopeOutGithub'] = dfPublicPrograms['ScopeOut'].apply(brevityscope.scope.cleanupScopeGithub)
        dfPublicPrograms['ScopeOutWild'] = dfPublicPrograms['ScopeOut'].apply(brevityscope.scope.cleanupScopeWild)
        dfPublicPrograms['ScopeOutGeneral'] = dfPublicPrograms['ScopeOut'].apply(brevityscope.scope.cleanupScopeGeneral)
        dfPublicPrograms['ScopeOutIP'] = dfPublicPrograms['ScopeOut'].apply(brevityscope.scope.cleanupScopeIP)

        programStatus = np.vectorize(bulkLoadPrograms)(dfPublicPrograms['programPlatform'], dfPublicPrograms['inviteType'], dfPublicPrograms['ScopeIn'], dfPublicPrograms['ScopeOut'], dfPublicPrograms['ProgramName'], dfPublicPrograms['ScopeInURLs'], dfPublicPrograms['ScopeInGithub'], dfPublicPrograms['ScopeInWild'], dfPublicPrograms['ScopeInGeneral'], dfPublicPrograms['ScopeInIP'], dfPublicPrograms['ScopeOutURLs'], dfPublicPrograms['ScopeOutGithub'], dfPublicPrograms['ScopeOutWild'], dfPublicPrograms['ScopeOutGeneral'], dfPublicPrograms['ScopeOutIP'])
    
        responseData = {
            'Program Status': str(programStatus),
        }
    
        return {
            'statusCode': 200,
            'body': json.dumps(responseData)
        }
    
    def bulkLoadHackerOne():
        # Retrieve Bugcrowd
        filePath = 'https://raw.githubusercontent.com/arkadiyt/bounty-targets-data/master/data/hackerone_data.json'
        with urllib.request.urlopen(filePath) as url:
            data = json.loads(url.read().decode())
    
        dfPublicPrograms = pd.json_normalize(data)
        dfPublicPrograms['programPlatform'] = 'HackerOne'
        dfPublicPrograms['inviteType'] = 'Public'
        dfPublicPrograms['ScopeIn'] = dfPublicPrograms['targets.in_scope'].apply(brevityscope.scope.parseScopeIn)
        dfPublicPrograms['ScopeOut'] = dfPublicPrograms['targets.out_of_scope'].apply(brevityscope.scope.parseScopeOut)
        dfPublicPrograms['ProgramName'] = dfPublicPrograms['handle'].apply(brevityscope.scope.parseProgramUrl)
        dfPublicPrograms = dfPublicPrograms.rename(columns={'name':'description'})

        dfPublicPrograms['ScopeInURLs'] = dfPublicPrograms['ScopeIn'].apply(brevityscope.scope.cleanupScopeStrict)
        dfPublicPrograms['ScopeInGithub'] = dfPublicPrograms['ScopeIn'].apply(brevityscope.scope.cleanupScopeGithub)
        dfPublicPrograms['ScopeInWild'] = dfPublicPrograms['ScopeIn'].apply(brevityscope.scope.cleanupScopeWild)
        dfPublicPrograms['ScopeInGeneral'] = dfPublicPrograms['ScopeIn'].apply(brevityscope.scope.cleanupScopeGeneral)
        dfPublicPrograms['ScopeInIP'] = dfPublicPrograms['ScopeIn'].apply(brevityscope.scope.cleanupScopeIP)
        dfPublicPrograms['ScopeOutURLs'] = dfPublicPrograms['ScopeOut'].apply(brevityscope.scope.cleanupScopeStrict)
        dfPublicPrograms['ScopeOutGithub'] = dfPublicPrograms['ScopeOut'].apply(brevityscope.scope.cleanupScopeGithub)
        dfPublicPrograms['ScopeOutWild'] = dfPublicPrograms['ScopeOut'].apply(brevityscope.scope.cleanupScopeWild)
        dfPublicPrograms['ScopeOutGeneral'] = dfPublicPrograms['ScopeOut'].apply(brevityscope.scope.cleanupScopeGeneral)
        dfPublicPrograms['ScopeOutIP'] = dfPublicPrograms['ScopeOut'].apply(brevityscope.scope.cleanupScopeIP)

        programStatus = np.vectorize(bulkLoadPrograms)(dfPublicPrograms['programPlatform'], dfPublicPrograms['inviteType'], dfPublicPrograms['ScopeIn'], dfPublicPrograms['ScopeOut'], dfPublicPrograms['ProgramName'], dfPublicPrograms['ScopeInURLs'], dfPublicPrograms['ScopeInGithub'], dfPublicPrograms['ScopeInWild'], dfPublicPrograms['ScopeInGeneral'], dfPublicPrograms['ScopeInIP'], dfPublicPrograms['ScopeOutURLs'], dfPublicPrograms['ScopeOutGithub'], dfPublicPrograms['ScopeOutWild'], dfPublicPrograms['ScopeOutGeneral'], dfPublicPrograms['ScopeOutIP'])
    
        responseData = {
            'Program Status': str(programStatus),
        }
        
        return responseData
    if (programName == 'bugcrowd'):
        responseData = bulkLoadBugcrowd()
    if (programName == 'hackerone'):
        responseData = bulkLoadHackerOne()
    else:
        responseData = 'Program not yet ready'
        
    return {
        'statusCode': 200,
        'program': programName,
        'operation': operationName,
        'body': json.dumps(responseData)
    }