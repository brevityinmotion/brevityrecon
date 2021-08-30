import json, boto3, requests, csv
import brevitycore.core
import brevityscope.process
import brevityprogram.securitytrails

def lambda_handler(event, context):
    
    def _getParameters(paramName):
        client = boto3.client('ssm')
        response = client.get_parameter(
            Name=paramName
        )
        return response['Parameter']['Value']
    
    refinedBucketName = _getParameters('dataBucketName')
    refinedBucketPath = _getParameters('refinedBucketPath')
    inputBucketPath = _getParameters('inputBucketPath')
    programInputBucketPath = _getParameters('programInputBucketPath')
    
    if event['program'] is None:
        return {"isBase64Encoded":False,"statusCode":400,"body":json.dumps({"error":"Missing program name."})}
    if event['operation'] is None:
        return {"isBase64Encoded":False,"statusCode":400,"body":json.dumps({"error":"Missing operation name."})}
    programName = str(event['program'])
    operationName = str(event['operation'])
    
    #s3://brevity-data/refined/programName/programName-domains-roots.csv
    objectKeyPath = 'refined/' + programName + '/' + programName + '-domains-roots.csv'

    def retrieve_object(bucketName, objectKeyPath):
        s3Client = boto3.client('s3')
        s3Object = s3Client.get_object(Bucket=bucketName, Key=objectKeyPath)
        objectData = s3Object['Body'].read()
        return objectData
    
    def parseCSV(objectData):
        objectData = objectData.decode("utf-8")
        reader = csv.reader(objectData.split('\n'))
        data = []
        header = next(reader)
        for row in reader:
            if not ''.join(row).strip():
                continue
            else:
                data.append(row)
        return data
    
    # Retrieve domain roots file
    objectData = retrieve_object(refinedBucketName,objectKeyPath)

    # Parse line items from domain roots csv and process each root domain through SecurityTrails
    # Add any newly discovered domains to the domains file.
    objectCSV = parseCSV(objectData)
    for rootDomain in objectCSV:
        lstDomains = brevityprogram.securitytrails.retrieveSecurityTrailsDomains(rootDomain)
        storeStatus = brevityscope.parser.storeAllDomains(programName, refinedBucketPath, lstDomains, programInputBucketPath)
    
    responseData = {
        'status': str(storeStatus),
    }
    
    return {
        'statusCode': 200,
        'program': programName,
        'operation': operationName,
        'body': json.dumps(responseData)
    }