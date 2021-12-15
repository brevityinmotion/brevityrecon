import json, boto3, os, re
import gzip
import base64
from io import BytesIO

def lambda_handler(event, context):
    


    cw_data = str(event['awslogs']['data'])
    cw_logs = gzip.GzipFile(fileobj=BytesIO(base64.b64decode(cw_data, validate=True))).read()
    log_events = json.loads(cw_logs)
    for log_event in log_events['logEvents']:
        print(log_event)
# subscription filter pattern: [logversion,timestamp,zoneid,queryname,querytype,responsecode,protocol,edgelocation,resolverip,clientsubnet]
# URL with schema https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/query-logs.html

#    if event['program'] is None:
#        return {"isBase64Encoded":False,"statusCode":400,"body":json.dumps({"error":"Missing program name."})}
#    if event['operation'] is None:
#        return {"isBase64Encoded":False,"statusCode":400,"body":json.dumps({"error":"Missing operation name."})}
#    else:
#        operationName = 'crawl'
    
#    programName = str(event['program'])
#    taskToken = str(event['token'])
    
    return {
        'statusCode': 200,
#        'event': event,
#        'operation': operationName,
        'body': json.dumps(log_event)
    }