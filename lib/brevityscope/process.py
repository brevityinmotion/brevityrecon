import pandas as pd
import numpy as np
import re
import json
from pandas.io.json import json_normalize
from urllib.parse import urlparse
import brevityscope.parser
import brevityprogram.dynamodb

def processAmass(programName, refinedBucketPath, programInputBucketPath):
    filePath = refinedBucketPath + programName + '/' + programName + '-amass-subs.json'
    df = pd.read_json(filePath, lines=True)
    # Expand out the list columns - sources and addresses
    flat_df = df.set_index([c for c in df.columns if c != 'addresses' and c !='sources']).explode('addresses').explode('sources').reset_index()
    flat_df = pd.concat([flat_df, flat_df['addresses'].apply(pd.Series)], axis=1).drop(columns=['addresses'])
    flat_df.rename({'name': 'subdomain'}, axis=1, inplace=True)
    storePath = refinedBucketPath + programName + '/' + programName + '-subs-detail.csv'
    flat_df.to_csv(storePath, index=False)
    
    # Generate a list of all of the unique domains while parsing potentially missing child domains
    allDomains = brevityscope.parser.processBulkDomains(flat_df)
    # Store the unique list of domains into S3 - Creates file - programName-domains.csv
    dfDomains = brevityscope.parser.storeAllDomains(programName, refinedBucketPath, allDomains, programInputBucketPath)
    
    return dfDomains

def parseUrlRoot(urlvalue):
        try:
            cleanurl = urlparse(urlvalue)#.netloc
            cleanurl = cleanurl.hostname
            return str(cleanurl)
        except:
            # If urlparse due to weird characters like "[", utilize generic url to avoid downstream issues.
            # TODO: I'm sure there is probably a better way to handle this.
            urlvalue = "https://icicles.io"
            cleanurl = urlparse(urlvalue)#.netloc
            cleanurl = cleanurl.hostname
            return str(cleanurl)

def parseUrlBase(urlvalue):
    # Normalize URLs to avoid duplicate urls if it is http or https and has standard ports. Was discovering duplicate urls with and without port.
    try:
        baseurl = urlparse(urlvalue)
        if (baseurl.port == 443 or baseurl.port == 80):
            baseurl = baseurl.scheme + '://' + baseurl.hostname + baseurl.path
        else:
            baseurl = baseurl.scheme + '://' + baseurl.netloc + baseurl.path
        return str(baseurl)
    except:
        # If urlparse due to weird characters like "[", utilize generic url to avoid downstream issues.
        # TODO: I'm sure there is probably a better way to handle this.
        urlvalue = "https://icicles.io"
        baseurl = urlparse(urlvalue)
        baseurl = baseurl.scheme + '://' + baseurl.hostname + baseurl.path
        return str(baseurl)
    
def processHttpx(programName, refinedBucketPath, inputBucketPath, presentationBucketPath, operationName, programInputBucketPath):
    # This is the file that gets created from the output of HTTPX - either initial or crawl as the operation
    fileName = programName + '-httpx-' + operationName + '.json'
    presentationFilePath = presentationBucketPath + 'httpx-json/' + fileName
    
    df = pd.read_json(presentationFilePath, lines=True)
    df['program'] = programName
    
    if (operationName == 'initial'):
        storePathUrl = programInputBucketPath + programName + '/' + programName + '-httpx.csv'
        df.to_csv(storePathUrl, header=False, index=False, sep='\n')
    
        storePathUrl = programInputBucketPath + programName + '/' + programName + '-urls-base.txt'
        dfUrls = df.drop_duplicates(subset=['url'])
        dfUrls['url'].to_csv(storePathUrl, header=False, index=False, sep='\n')

    df['domain'] = df['url'].apply(parseUrlRoot)
    df['baseurl'] = df['url'].apply(parseUrlBase)
    fileOutputName = programName + '-httpx.json'
    fileOutputNameUrls = programName + '-urls-mod.txt'
    outputPath = presentationBucketPath + 'httpx/' + fileOutputName
    
    # Check if there is already output so that it is not overwritten
    try:
        dfInitialHttpx = pd.read_json(outputPath, lines=True)
        df = dfInitialHttpx.append(df)
        df = df.drop_duplicates(subset=['url'], keep='last')
    except:
        print('No initial httpx output')
      
    df.to_json(outputPath, orient='records', lines=True)

    if (operationName == 'initial'):
        #fileOutputCrawl = programName + '-httpx-crawl.csv'
        storePathUrl = inputBucketPath + 'programs/' + programName + '/' + fileOutputNameUrls
        df['url'].to_csv(storePathUrl, header=False, index=False, sep='\n')
    return 'Success'

# Duplicate of processCrawl
def publishUrls(programName, refinedBucketPath, presentationBucketPath):
    from urllib.parse import urlparse

    csvPath = refinedBucketPath + programName + '/' + programName + '-urls-max.txt'
    dfAllDomains = pd.read_csv(csvPath, header=None, names=['url'], sep='\n')

    dfAllDomains['domain'] = dfAllDomains['url'].apply(parseUrlRoot)
    dfAllDomains['baseurl'] = dfAllDomains['url'].apply(parseUrlBase)
    dfAllDomains['program'] = programName
    storePath = refinedBucketPath + programName + '/' + programName + '-spider-urls.csv'
    dfAllDomains.to_csv(storePath, columns=['url', 'domain', 'baseurl'], index=False)

    # Need to add a variable for this
    presentationPath = 's3://brevity-data/presentation/urls/' + programName + '-urls-info.csv'
    dfAllDomains.to_csv(presentationPath, columns=['url','domain','baseurl','program'], index=False)
    return 'URLs successfully published'

def processCrawl(programName, refinedBucketPath, inputBucketPath, presentationBucketPath, operationName, programInputBucketPath):

    # Retrieve the program information from database
    programPlatform, inviteType, listscopein, listscopeout, ScopeInURLs, ScopeInGithub, ScopeInWild, ScopeInGeneral, ScopeInIP, ScopeOutURLs, ScopeOutGithub, ScopeOutWild, ScopeOutGeneral, ScopeOutIP = brevityprogram.dynamodb.getProgramInfo(programName)
 
    # Open the output file from the crawl. It is a raw list of URLs.
    csvPath = refinedBucketPath + programName + '/' + programName + '-urls-max.txt'
    dfAllURLs = pd.read_csv(csvPath, header=None, names=['url'], sep='\n')

    # Enrich the URL fields within the dataframe
    dfAllURLs['domain'] = dfAllURLs['url'].apply(parseUrlRoot)
    dfAllURLs['baseurl'] = dfAllURLs['url'].apply(parseUrlBase)
    dfAllURLs['program'] = programName
    
     # Scope mapper
    mapperIn = {True: 'in', False: 'other'}  # in = within the defined scope
    mapperOut = {True: 'out', False: 'in'} # out = explicitly out of scope
    mapperWild = {True: 'wild', False: 'out'} # wild - within the wildcard scope
     # other = not in scope but not explicitly excluded
    
    # This checks to determine whether a url is explicitly defined as out-of-scope
    dfAllURLs['scopeOut'] = dfAllURLs.domain.str.lower().isin([x.lower() for x in ScopeOutGeneral]).map(mapperOut)
    # This checks to determine whether a url is explicitly defined as in-scope
    dfAllURLs['scopeIn'] = dfAllURLs.domain.str.lower().isin([x.lower() for x in ScopeInGeneral]).map(mapperIn)
    
    # This section checks for wildcard scopes and determines whether a url is included within the wildcard scope
    lstWild = []
    for wild in ScopeInWild:
        wild = re.sub(r'^.*?\*\.', '', wild)
        lstWild.append(wild.lower())
        print(wild)
    
    dfAllURLs['scopeWild'] = dfAllURLs.domain.str.lower().str.endswith(tuple(lstWild)).map(mapperWild)
    
    # This section creates a normalized scope field to track in, out, wild, or other
    conditions = [
        (dfAllURLs['scopeOut'] == 'out'),
        (dfAllURLs['scopeIn'] == 'in') & (dfAllURLs['scopeOut'] != 'out'),
        (dfAllURLs['scopeWild'] == 'wild') & (dfAllURLs['scopeIn'] != 'in') & (dfAllURLs['scopeOut'] != 'out'),
        (dfAllURLs['scopeIn'] == 'other') & (dfAllURLs['scopeWild'] != 'wild') & (dfAllURLs['scopeIn'] != 'in') & (dfAllURLs['scopeOut'] != 'out')
    ]
    
    # Each of these values maps to the equivalent condition listed
    values = ['out', 'in', 'wild', 'other']                                                                           
    
    # Create a new column and assign the values specific to the conditions.
    # TODO - This could potentially miss items since it is a select. Need to perform some searches on whether or not scope column is populated after using this for a while.
    dfAllURLs['scope'] = np.select(conditions, values)

    # File path that does not contain explicitly out-of-scope items
    storeModPathUrl = inputBucketPath + 'programs/' + programName + '/' + programName + '-urls-mod.txt'
    # File path that only contains explicitly in-scope urls
    storeInPathUrl = inputBucketPath + 'programs/' + programName + '/' + programName + '-urls-in.txt'
    # File path that only contains explicitly in-scope urls
    storeBasePathUrl = inputBucketPath + 'programs/' + programName + '/' + programName + '-urls-base.txt'

    # Output URLs that are in-scope
    dfURLsIn = dfAllURLs[(dfAllURLs['scope'] == 'in') | (dfAllURLs['scope'] == 'wild')]
    dfURLsIn['url'].drop_duplicates().to_csv(storeInPathUrl, header=None, index=False, sep='\n')
    # This only outputs the base URL so that it can be used for fuzzing
    dfURLsIn['baseurl'].drop_duplicates().to_csv(storeBasePathUrl, header=None, index=False, sep='\n')
    
    # Output URLs that are not explicitly out-of-scope
    dfURLsMod = dfAllURLs[dfAllURLs['scope'] != 'out']
    dfURLsMod['url'].drop_duplicates().to_csv(storeModPathUrl, header=None, index=False, sep='\n')
    
    # Output metrics within log
    print('Length of all urls: ' + str(len(dfAllURLs)))
    print('Length of mod urls: ' + str(len(dfURLsMod)))
    print('Length of in-scope urls: ' + str(len(dfURLsIn)))

    # Need to add a variable for this
    presentationPath = 's3://brevity-data/presentation/urls/' + programName + '-urls-info.csv'
    dfAllURLs.to_csv(presentationPath, columns=['url','domain','baseurl','program', 'scope'], index=False)
    
    return 'URLs successfully published'