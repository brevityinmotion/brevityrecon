# This Lambda is still under development.

import json, boto3, os

def lambda_handler(event, context):
    
    import boto3

    client = boto3.client('glue')
    response = client.create_crawler(
        Name='brevity-httpx-recon',
        Role='AWSGlueServiceRole-brevity',
        DatabaseName='brevity-analysis',
        Description='HTTPX json recon crawler',
        TablePrefix='brevity_',
        Targets={
            'S3Targets': [
                {
                    'Path': 's3://brevity-data/presentation/httpx-json/',
                    'Exclusions': [
                    ]
                },
            ]
        },
        SchemaChangePolicy={
            'UpdateBehavior': 'UPDATE_IN_DATABASE',
            'DeleteBehavior': 'DELETE_FROM_DATABASE'
        }
    )

    response = client.start_crawler(
        Name='httpx-json'
    )

    response = client.update_table(
        DatabaseName='brevity-analysis',
        TableInput={
            'Name': 'json',
            'Description': 'HTTPX raw json',
            'StorageDescriptor': {
                'SerdeInfo': {
                    'Name': '',
                    'SerializationLibrary': 'org.openx.data.jsonserde.JsonSerDe'
                }
            }
        }
    )
    
    client = boto3.client('glue')
    response = client.start_crawler(
        Name='brevity-httpx'
    )
    
    responseData = {
        'Program Status': 'Success',
        'Operation Status': response
    }
    
    return {
        'statusCode': 200,
        'body': json.dumps(responseData)
    }