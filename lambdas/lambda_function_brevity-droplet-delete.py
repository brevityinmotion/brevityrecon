import json, boto3
import brevitycore.core
import digitalocean

def lambda_handler(event, context):
    
    # Retrieve Digital Ocean API key from AWS Secrets Manager
    secretName = 'digitalocean'
    regionName = 'us-east-1'
    accessToken = brevitycore.core.get_secret(secretName,regionName)
    
    manager = digitalocean.Manager(token=accessToken)
    my_droplets = manager.get_all_droplets()
    for dropletvalue in my_droplets:
        dropletState = dropletvalue.status
        dropletName = dropletvalue.name
        # It would be smart to add a filter in this for the future to validate droplet naming convention as well in case there is a droplet that should not be deleted when shutdown.
        if dropletState == 'off':
            if dropletName.startswith('brevity-'):
                dropletvalue.destroy()
    return {
        'statusCode': 200
    }