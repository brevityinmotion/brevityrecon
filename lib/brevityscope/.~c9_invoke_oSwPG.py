import ast
import re
import urllib.request, json
from urllib.parse import urlparse

def parseScopeIn(scopeIn):
    targetData = []
    if not scopeIn:
        return targetData
    smallAll = str(scopeIn)[1:-1]
    scopeLength = len(scopeIn)
    smallData = ast.literal_eval(smallAll)

    if (scopeLength > 1):
        for item in smallData:
            if item.get('target') is not None:
                targetData.append(item.get('target'))
            if item.get('asset_identifier') is not None:
                targetData.append(item.get('asset_identifier'))
        return targetData
    else:
        if smallData.get('target') is not None:
            targetData.append(smallData.get('target'))
        if smallData.get('asset_identifier') is not None:
            targetData.append(smallData.get('asset_identifier'))
        return targetData
def parseScopeOut(scopeOut):
    targetData = []
    if not scopeOut:
        targetData.append('icicles.io')
        return targetData
    smallAll = str(scopeOut)[1:-1]
    scopeLength = len(scopeOut)
    smallData = ast.literal_eval(smallAll)

    if (scopeLength > 1):
        for item in smallData:
            if item.get('target') is not None:
                targetData.append(item.get('target'))
            if item.get('asset_identifier') is not None:
                targetData.append(item.get('asset_identifier'))
        return targetData
    else:
        if smallData.get('target') is not None:
            targetData.append(smallData.get('target'))
        if smallData.get('asset_identifier') is not None:
            targetData.append(smallData.get('asset_identifier'))
        return targetData
def parseProgramUrl(programUrl):
    programName = programUrl.rsplit('/', 1)[-1]
    programName = ''.join(e for e in programName if e.isalnum())
    return programName

def parseProgramName(programName):
    programName = ''.join(e for e in programName if e.isalnum())
    return programName

def cleanScope(sub, test_str):
    for ele in sub:
        if ele in test_str:
            return 1
    return 0
    
def cleanupScopeGithub(dfIn):
    matchString = 'github.com'
    matches = []
    for match in dfIn:
        match = re.search("(?P<url>https?://[^\s]+)", match)
        if match is None:
            continue
        else:
            match = match.group('url')
            if matchString in match:
                matches.append(match)
            else:
                continue
    return matches
def cleanupScopeStrict(dfIn):
    matchString = 'github.com'
    matches = []
    for match in dfIn:
        #if matchString in match:
        match = re.search("(?P<url>https?://[^\s]+)", match)
        if match is None:
            continue
        else:
            match = match.group('url')
            if matchString in match:
                continue
            else:
                matches.append(match)
    return matches

def cleanupScopeWild(dfIn):
    matchString = '\*.'
    matches = []
    for match in dfIn:
        match = re.search("(?P<url>[*][^\s|\,]+)", match)
   
        if match is None:
            continue
        else:
            match = match.group('url')
            matches.append(match)
    return matches

def cleanupScopeIP(dfIn):
    matchString = '\*.'
    matches = []
    for match in dfIn:
        
        match = re.search("(?P<url>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(?:/\d{1,2}|))", match)
        
        if match is None:
            continue
        else:
            match = match.group('url')
            matches.append(match)
    return matches

def cleanupScopeGeneral(dfIn):
    matchStringSpace = ' '
    matchStringGit = 'github.com'
    matchStringUrl = 'http'
    matchStringWild = '\*.'
    matchStringDot = '.'
    matches = []
    for match in dfIn:
        matchWild = re.search("(?P<url>[*][^\s|\,]+)", match)
        matchDot = re.search("(?P<url>[.][^\s]+)", match)
        matchIP = re.search("(?P<url>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(?:/\d{1,2}|))", match)
        if matchStringGit in match:
            continue
        elif matchStringSpace in match:
            continue
        elif matchStringUrl in match:
            url = urlparse(match)
            match = url.netloc
            matches.append(match)
            continue
        elif matchIP is not None:
            continue
        elif matchWild is not None:
            match = match.replace('*.','')
            matches.append(match)
            continue
        elif matchDot is None:
            continue
        else:
            matches.append(match)
    return matches

def extrapolateScope(programName, listscopein, listscopeout):
    ScopeInURLs = cleanupScopeStrict(listscopein)
    ScopeInGithub = cleanupScopeGithub(listscopein)
    ScopeInWild = cleanupScopeWild(listscopein)
    ScopeInGeneral = cleanupScopeGeneral(listscopein)
    ScopeInIP = cleanupScopeIP(listscopein)
    ScopeOutURLs = cleanupScopeStrict(listscopeout)
    ScopeOutGithub = cleanupScopeGithub(listscopeout)
    ScopeOutWild = cleanupScopeWild(listscopeout)
    ScopeOutGeneral = cleanupScopeGeneral(listscopeout)
    ScopeOutIP = cleanupScopeIP(listscopeout)
    return ScopeInURLs, ScopeInGithub, ScopeInWild, ScopeInGeneral, ScopeInIP, ScopeOutURLs, ScopeOutGithub, ScopeOutWild, ScopeOutGeneral, ScopeOutIP



























