import json, requests, csv, boto3
import brevitycore.core
import brevityscope.parser

def retrieveSecurityTrailsDomains(rootDomain):
    
    # Retrieve API key for SecurityTrails
    secretName = "brevity-recon-apis"
    regionName = "us-east-1"
    secretRetrieved = brevitycore.core.get_secret(secretName,regionName)
    APIKEY = secretRetrieved['securitytrails']
    
    rootDomainStr = rootDomain[0]
    url = "https://api.securitytrails.com/v1/domain/" + rootDomainStr + "/subdomains"
    print(url)
    querystring = {"children_only":"false","include_inactive":"true"}
    headers = {"Accept": "application/json","APIKEY": APIKEY}
    # Initiate request and retrieve results
    response = requests.request("GET", url, headers=headers, params=querystring)
    # Normalizing data
    jsonInfo = response.json()
    try:
        jsonSubs = jsonInfo['subdomains']
        domainList = ['{0}.{1}'.format(sub, rootDomainStr) for sub in jsonSubs]
        return domainList
    except:
        return 'no subdomains'