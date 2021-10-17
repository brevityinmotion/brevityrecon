import pandas as pd
import json
from pandas.io.json import json_normalize
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
    
def processHTTPXOld(programName, rawBucketPath, refinedBucketPath, programInputBucketPath):
    filePath = refinedBucketPath + programName + '/' + programName + '-httpx-initial.json'
    df = pd.read_json(filePath, lines=True)
    
    storePathUrl = programInputBucketPath + programName + '/' + programName + '-httpx.csv'
    df.to_csv(storePathUrl, header=False, index=False, sep='\n')
    
    storePathUrl = programInputBucketPath + programName + '/' + programName + '-urls-base.csv'
    df['url'].to_csv(storePathUrl, header=False, index=False, sep='\n')
    return df
    
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
    
    from urllib.parse import urlparse

    def _parseUrlRoot(urlvalue):
        cleanurl = urlparse(urlvalue).netloc
        return cleanurl

    def _parseUrlBase(urlvalue):
        baseurl = urlparse(urlvalue)
        baseurl = baseurl.scheme + '://' + baseurl.netloc + baseurl.path
        return baseurl

    df['domain'] = df['url'].apply(_parseUrlRoot)
    df['baseurl'] = df['url'].apply(_parseUrlBase)
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
    
def processCrawl(programName, refinedBucketPath, inputBucketPath, presentationBucketPath, operationName, programInputBucketPath):
    from urllib.parse import urlparse

    def parseUrlRoot(urlvalue):
        try:
            cleanurl = urlparse(urlvalue).netloc
            return cleanurl
        except:
            # If urlparse due to weird characters like "[", utilize generic url to avoid downstream issues.
            # TODO: I'm sure there is probably a better way to handle this.
            urlvalue = "https://icicles.io"
            cleanurl = urlparse(urlvalue).netloc
            return cleanurl

    def parseUrlBase(urlvalue):
        try:
            baseurl = urlparse(urlvalue)
            baseurl = baseurl.scheme + '://' + baseurl.netloc + baseurl.path
            return baseurl
        except:
            # If urlparse due to weird characters like "[", utilize generic url to avoid downstream issues.
            # TODO: I'm sure there is probably a better way to handle this.
            urlvalue = "https://icicles.io"
            baseurl = urlparse(urlvalue)
            baseurl = baseurl.scheme + '://' + baseurl.netloc + baseurl.path
            return baseurl

    csvPath = refinedBucketPath + programName + '/' + programName + '-urls-max.txt'
    #print(csvPath)
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

# Duplicate of processCrawl
def publishUrls(programName, refinedBucketPath, presentationBucketPath):
    from urllib.parse import urlparse

    def parseUrlRoot(urlvalue):
        cleanurl = urlparse(urlvalue).netloc
        return cleanurl

    def parseUrlBase(urlvalue):
        baseurl = urlparse(urlvalue)#.netloc
        baseurl = baseurl.scheme + '://' + baseurl.netloc + baseurl.path
        return baseurl

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
    
def removeOutScope(programName, refinedBucketPath, inputBucketPath, presentationBucketPath):
    
    programPlatform, inviteType, listscopein, listscopeout, ScopeInURLs, ScopeInGithub, ScopeInWild, ScopeInGeneral, ScopeInIP, ScopeOutURLs, ScopeOutGithub, ScopeOutWild, ScopeOutGeneral, ScopeOutIP = brevityprogram.dynamodb.getProgramInfo(programName)
    domainScopePath = refinedBucketPath + programName + '/' + programName + '-domains-scope.txt'
    
    urlPath = presentationBucketPath + 'httpx/' + programName + '-httpx.json'
    dfScopeDomains = pd.read_csv(domainScopePath, header=None)
    dfScopeDomains.rename({0: 'domain'}, axis=1, inplace=True)
    lstScopeDomains = dfScopeDomains.domain.tolist()
    dfAllURLs = pd.read_json(urlPath, lines=True)

    storePathUrl = inputBucketPath + 'programs/' + programName + '/' + programName + '-urls-scope.txt'
    dfScopeURLs = dfAllURLs[dfAllURLs.domain.isin(lstScopeDomains)]
    print('dfScopeURLs length: ' + str(len(dfScopeURLs)))
    dfCleanedURLs = dfScopeURLs[~dfScopeURLs.domain.isin(ScopeOutGeneral)]

    dfCleanedURLs = dfCleanedURLs.append(dfScopeURLs)
    dfCleanedURLs = dfCleanedURLs.drop_duplicates(subset='baseurl')
    dfCleanedURLs['url'].to_csv(storePathUrl, header=None, index=False, sep='\n')
    urlScope = str(len(dfCleanedURLs))
    return urlScope    
