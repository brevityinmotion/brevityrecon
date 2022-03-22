import pandas as pd
import boto3
import requests
import io
from requests.structures import CaseInsensitiveDict
from boto3.dynamodb.conditions import Key

def lambda_handler(event, context):
    
    def _getParameters(paramName):
        client = boto3.client('ssm')
        response = client.get_parameter(
            Name=paramName
        )
        return response['Parameter']['Value']
    
    dashboardBucketName = _getParameters('dataBucketName')
    
    def query_dns(dynamodb=None):
        if not dynamodb:
            dynamodb = boto3.resource('dynamodb')

        table = dynamodb.Table('brevity_ipinfo')
        response = table.scan(
            Limit=100
        )
        return response['Items']

    # Retrieve DNS entries from DynamoDB
    dnsResults = query_dns()
    # Load results into Pandas DataFrame
    dfDNS = pd.DataFrame(dnsResults)
    # Convert IP addresses column into a list
    ipList = dfDNS["ipinfo_ip"].tolist()

    # Retrieves the IPInfo Map URL
    def query_ipinfo(ipList):    
        headers = CaseInsensitiveDict()    
        url = "https://ipinfo.io/tools/map?cli=1"
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        data = "@-" + str(ipList)
        resp = requests.post(url, headers=headers, data=data)
        response = resp.json()
        mapUrl = response['reportUrl']
        return mapUrl

    mapUrl = query_ipinfo(ipList)

    def generate_dns_html(dfDNS, mapUrl):
        resphtml = f"""<html>
        <title>Brevity In Motion - DNS Tracker</title>
        <body>
        <a href="{mapUrl}">IPInfo Map</a>
        """
        resphtml += dfDNS.to_html()
        resphtml += f"""
        </body>
        </html>
        """
        return resphtml

    resphtml = generate_dns_html(dfDNS, mapUrl)

    def upload_html(resphtml):
        filebuffer = io.BytesIO(resphtml.encode())
        bucket = 'dashboard.icicles.io'
        key = 'index.html'

        client = boto3.client('s3')
        response = client.upload_fileobj(filebuffer, bucket, key, ExtraArgs={'ContentType':'text/html'})
        return response

    response = upload_html(resphtml)
   
    return {
        'statusCode': 200
    }