import json, boto3
import brevityinfra.infra

def lambda_handler(event, context):
    # TODO implement
    def _getParameters(paramName):
        client = boto3.client('ssm')
        response = client.get_parameter(
            Name=paramName
        )
        return response['Parameter']['Value']
    
    inputBucketName = _getParameters('inputBucketName')

    ATHENA_BUCKET = _getParameters('ATHENA_BUCKET')
    ATHENA_DB = _getParameters('ATHENA_DB')
    
    # Generate the standard amass config file
    status = brevityinfra.infra.generateAmassConfig(inputBucketName)
    
    # Create installation file (bounty-startup.sh) to run on ephemeral server at startup
    # May no longer need since these are generated on-demand.
    #installScriptStatus = brevityinfra.infra.generateBountyInstallScript(inputBucketName)

    # Update Rapid7 Sonar partitions to make latest indexes searchable
    brevityinfra.infra.updateSonarPartitions(ATHENA_DB, ATHENA_BUCKET)
    
    return {
        'statusCode': 200,
        'body': json.dumps('Infrastructure readiness complete.')
    }