import json, requests, csv, boto3
import brevitycore.core
import brevityscope.parser

def retrieveSecurityTrailsDomains(rootDomain):
    
    # Retrieve API key for SecurityTrails
    secretName = "brevity-recon-apis"
    regionName = "us-east-1"
    secretRetrieved = brevitycore.core.get_secret(secretName,regionName)
    secretjson = json.loads(secretRetrieved)
    APIKEY = secretjson['securitytrails']
    
    #rootDomainStr = rootDomain[0]
    url = "https://api.securitytrails.com/v1/domain/" + rootDomain + "/subdomains"
    querystring = {"children_only":"false","include_inactive":"true"}
    headers = {"Accept": "application/json","APIKEY": APIKEY}
    # Initiate request and retrieve results
    response = requests.request("GET", url, headers=headers, params=querystring)
    # Normalizing data
    jsonInfo = response.json()
  
    try:
        jsonSubs = jsonInfo['subdomains']
        domainList = ['{0}.{1}'.format(sub, rootDomain) for sub in jsonSubs]
        print(domainList)
        return domainList
    except:
        return 'no subdomains'