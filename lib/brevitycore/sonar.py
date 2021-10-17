import boto3, io, botocore, json, requests
import pandas as pd
from botocore.exceptions import ClientError
import logging
import tldextract
import brevitycore.core
import brevityprogram.dynamodb
import brevityscope.parser
from dynamodb_json import json_util as dynjson

# TO-DO: This function may no longer be used. Delete if not being utilized.
def sonarGenerateSubdomains(programName, refinedBucketPath, ATHENA_DB, ATHENA_BUCKET, ATHENA_TABLE):
    # Retrieve the input data to process from the list of domains
    storePath = refinedBucketPath + programName + '/' + programName + '-domains-roots.txt'   
    dfDomainRoots = pd.read_csv(storePath)
    # Prepare the domain roots for the query
    dfDomainRoots['athenaquery'] = "'%." + dfDomainRoots['domain'] + "'"
    searchDomains = dfDomainRoots['athenaquery'].tolist()
    searchDomainString = ' OR name LIKE '.join(searchDomains)
    query = "SELECT * FROM %s WHERE name LIKE %s AND date = (SELECT MAX(date) from %s);" % (ATHENA_TABLE,searchDomainString,ATHENA_TABLE)
    execid = brevitycore.core.queryathena(ATHENA_DB, ATHENA_BUCKET, query)
    # Utilize executionID to retrieve results
    return execid

# This function will concatenate the wildcard scope domains to incorporate into one larger Athena query.    
def sonarRun(programName, refinedBucketPath, ATHENA_DB, ATHENA_BUCKET, ATHENA_TABLE):
    
    resp = brevityprogram.dynamodb.query_program(programName)
    searchDomains = dynjson.loads(resp['ScopeInWild'])
    if not searchDomains:
        execid = 'No Wildcards'
        return execid
    else:
        searchDomains = [s.replace("*", "'%") for s in searchDomains]
        searchDomains = [s + "'" for s in searchDomains]
        searchDomainString = ' OR name LIKE '.join(searchDomains)
        query = "SELECT * FROM %s WHERE name LIKE %s AND date = (SELECT MAX(date) from %s);" % (ATHENA_TABLE,searchDomainString,ATHENA_TABLE)
        execid = brevitycore.core.queryathena(ATHENA_DB, ATHENA_BUCKET, query)
        # Utilize executionID to retrieve results
        return execid

# Retrieve the Sonar Athena query results and write them to the refined S3 bucket.
def sonarRetrieveResults(programName, execid, refinedBucketPath):
    downloadURL = brevitycore.core.retrieveresults(execid)
    if (downloadURL == 'No results.') or (downloadURL == 'Query failed.'):
        return 'No subdomains discovered.'
    # Load output into dataframe
    s=requests.get(downloadURL).content
    dfhosts=pd.read_csv(io.StringIO(s.decode('utf-8')))
    storePath = refinedBucketPath + programName + '/' + programName + '-sonar-output.csv'
    dfhosts.to_csv(storePath, index=False)
    return 'Subdomains successfully generated'

# Add the newly discovered subdomains from the Sonar output results file.
def sonarLoadSubdomains(programName, refinedBucketPath, programInputBucketPath):
    storePath = refinedBucketPath + programName + '/' + programName + '-sonar-output.csv'   
    dfhosts = pd.read_csv(storePath)
    dfhosts = dfhosts.rename(columns={'name': 'subdomain'})
    # Generate a list of all of the unique domains while parsing potentially missing child domains
    allDomains = brevityscope.parser.processBulkDomains(dfhosts)
    # Store the unique list of domains into S3 - Creates file - programName-domains.csv
    sonarStoreStatus = brevityscope.parser.storeAllDomains(programName, refinedBucketPath, allDomains, programInputBucketPath)
    sonarScopeStatus = brevityscope.parser.storeScopeDomains(programName, refinedBucketPath, allDomains, programInputBucketPath)
    return sonarStoreStatus