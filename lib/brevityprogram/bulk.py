import boto3
import io
import botocore
import json
from pandas.io.json import json_normalize
#import logging

# Thank you Arkadiy Tetelman (https://github.com/arkadiyt) for the great work that you do! Also be sure to checkout his Data Driven Bug Bounty talk as it is excellent (https://www.youtube.com/watch?v=2TWY74MgTrc&t=1139s)!
def getBugcrowdPrograms():
    import ast
    import urllib.request, json
    import pandas as pd

    def _parseScopeIn(scopeIn):
        targetData = []
        if not scopeIn:
            return targetData
        smallAll = str(scopeIn)[1:-1]
        scopeLength = len(scopeIn)
        smallData = ast.literal_eval(smallAll)

        if (scopeLength > 1):
            for item in smallData:
                targetData.append(item.get('target'))
            return targetData
        else:
            targetData.append(smallData.get('target'))
            return targetData
    def _parseScopeOut(scopeOut):
        targetData = []
        if not scopeOut:
            targetData.append('icicles.io')
            return targetData
        smallAll = str(scopeOut)[1:-1]
        scopeLength = len(scopeOut)
        smallData = ast.literal_eval(smallAll)

        if (scopeLength > 1):
            for item in smallData:
                targetData.append(item.get('target'))
            return targetData
        else:
            targetData.append(smallData.get('target'))
            return targetData
    def _parseProgramUrl(programUrl):
        programName = programUrl.rsplit('/', 1)[-1]
        return programName
    # File is updated hourly
    filePath = 'https://raw.githubusercontent.com/arkadiyt/bounty-targets-data/master/data/bugcrowd_data.json'
    with urllib.request.urlopen(filePath) as url:
        data = json.loads(url.read().decode())

    dfPublicPrograms = pd.json_normalize(data)
    dfPublicPrograms['programPlatform'] = 'Bugcrowd'
    dfPublicPrograms['inviteType'] = 'Public'
    dfPublicPrograms['ScopeIn'] = dfPublicPrograms['targets.in_scope'].apply(_parseScopeIn)
    dfPublicPrograms['ScopeOut'] = dfPublicPrograms['targets.out_of_scope'].apply(_parseScopeOut)
    dfPublicPrograms['ProgramName'] = dfPublicPrograms['url'].apply(_parseProgramUrl)
    dfPublicPrograms = dfPublicPrograms.rename(columns={'name':'description'})
    
    return dfPublicPrograms

# Arkadiy Tetelman (https://twitter.com/arkadiyt) again for the win!!
def getHackerOnePrograms():
    import ast
    import urllib.request, json
    import pandas as pd

    def _parseScopeIn(scopeIn):
        targetData = []
        if not scopeIn:
            return targetData
        smallAll = str(scopeIn)[1:-1]
        scopeLength = len(scopeIn)
        smallData = ast.literal_eval(smallAll)

        if (scopeLength > 1):
            for item in smallData:
                targetData.append(item.get('target'))
            return targetData
        else:
            targetData.append(smallData.get('target'))
            return targetData
    def _parseScopeOut(scopeOut):
        targetData = []
        if not scopeOut:
            # Some things break when there is no out-of-scope domain so this is my own domain. For example, amass does not like it if you send it the out of scope syntax and file path but have zero entries in the file.
            targetData.append('icicles.io')
            return targetData
        # This is removing quotes from the first and last characters of the input. This seemed like the best way to clean this without removing quotes within the content.
        smallAll = str(scopeOut)[1:-1]
        scopeLength = len(scopeOut)
        smallData = ast.literal_eval(smallAll)

        if (scopeLength > 1):
            for item in smallData:
                targetData.append(item.get('target'))
            return targetData
        else:
            targetData.append(smallData.get('target'))
            return targetData
    def _parseProgramUrl(programUrl):
        programName = programUrl.rsplit('/', 1)[-1]
        return programName
    # File is updated hourly
    filePath = 'https://raw.githubusercontent.com/arkadiyt/bounty-targets-data/master/data/hackerone_data.json'
    with urllib.request.urlopen(filePath) as url:
        data = json.loads(url.read().decode())

    dfPublicPrograms = pd.json_normalize(data)
    dfPublicPrograms['programPlatform'] = 'HackerOne'
    dfPublicPrograms['inviteType'] = 'Public'
    dfPublicPrograms['ScopeIn'] = dfPublicPrograms['targets.in_scope'].apply(_parseScopeIn)
    dfPublicPrograms['ScopeOut'] = dfPublicPrograms['targets.out_of_scope'].apply(_parseScopeOut)
    dfPublicPrograms['ProgramName'] = dfPublicPrograms['handle'].apply(_parseProgramUrl)
    dfPublicPrograms = dfPublicPrograms.rename(columns={'name':'description'})
    
    return dfPublicPrograms