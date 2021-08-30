import boto3, io, json, requests
import botocore
from botocore.exceptions import ClientError
import logging
import brevitycore

# This function will update the Athena table to point to the latest Sonar FDNS datasets
def updateSonarPartitions(ATHENA_DB, ATHENA_BUCKET):
    query = 'msck repair table rapid7_fdns_any;'
    execid = brevitycore.core.queryathena(ATHENA_DB, ATHENA_BUCKET, query)
    downloadURL = brevitycore.core.retrieveresults(execid)
    s=requests.get(downloadURL).content