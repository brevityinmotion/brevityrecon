import json, boto3, os, re
import gzip
import base64
import ipinfo
from io import BytesIO
import brevitycore.core

def lambda_handler(event, context):
    
    dynamodbclient = boto3.client('dynamodb')
    cw_data = str(event['awslogs']['data'])
    cw_logs = gzip.GzipFile(fileobj=BytesIO(base64.b64decode(cw_data, validate=True))).read()
    log_events = json.loads(cw_logs)
    
    def retrieveIPInfo(ip_address):
        # Retrieve API key for IPInfo
        secretName = "brevity-recon-apis"
        regionName = "us-east-1"
        secretRetrieved = brevitycore.core.get_secret(secretName,regionName)
        secretjson = json.loads(secretRetrieved)
        access_token = secretjson['ipinfo']
        handler = ipinfo.getHandler(access_token)
        details = handler.getDetails(ip_address)
        return details
    
    for log_event in log_events['logEvents']:
        queryid = log_event['id']
        log_event = log_event['extractedFields']
        dns_timestamp = log_event['timestamp']
        dns_zoneid = log_event['zoneid']
        dns_queryname = log_event['queryname']
        dns_querytype = log_event['querytype']
        dns_responsecode = log_event['responsecode']
        dns_protocol = log_event['protocol']
        dns_edgelocation = log_event['edgelocation']
        dns_resolverip = log_event['resolverip']
        dns_clientsubnet = log_event['clientsubnet']
        # Since the DNS query only provides a CIDR range, it converts it to the starting IP address of the range
        dns_clientipaddress = dns_clientsubnet.split('/', 1)[0]
        response = retrieveIPInfo(dns_clientipaddress)
        ipinfo_ip = response.ip
        ipinfo_city = response.city
        ipinfo_region = response.region
        ipinfo_country = response.country
        ipinfo_loc = response.loc
        ipinfo_org = response.org
        ipinfo_postal = response.postal
        ipinfo_timezone = response.timezone
        ipinfo_country_name = response.country_name
        ipinfo_latitude = response.latitude
        ipinfo_longitude = response.longitude
    
        dynamoItem = {'queryid':{'S':queryid},'timestamp':{'S':dns_timestamp},'dns_zoneid':{'S':dns_zoneid},'dns_queryname':{'S':dns_queryname},'dns_querytype':{'S':dns_querytype},'dns_responsecode':{'S':dns_responsecode},'dns_protocol':{'S':dns_protocol},'dns_edgelocation':{'S':dns_edgelocation},'dns_resolverip':{'S':dns_resolverip},'dns_clientsubnet':{'S':dns_clientsubnet},'dns_clientipaddress':{'S':dns_clientipaddress},'ipinfo_ip':{'S':ipinfo_ip},'ipinfo_city':{'S':ipinfo_city},'ipinfo_region':{'S':ipinfo_region},'ipinfo_country':{'S':ipinfo_country},'ipinfo_loc':{'S':ipinfo_loc},'ipinfo_org':{'S':ipinfo_org},'ipinfo_postal':{'S':ipinfo_postal},'ipinfo_timezone':{'S':ipinfo_timezone},'ipinfo_country_name':{'S':ipinfo_country_name},'ipinfo_latitude':{'S':ipinfo_latitude},'ipinfo_longitude':{'S':ipinfo_longitude}}
        dynamoresponse = dynamodbclient.put_item(TableName='brevity_ipinfo',Item=dynamoItem)
    
    return {
        'statusCode': 200,
        'body': json.dumps(log_event),
        'dbstatus': dynamoresponse
    }