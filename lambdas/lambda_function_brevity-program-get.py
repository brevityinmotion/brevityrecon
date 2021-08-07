import json, boto3

def lambda_handler(event, context):
    if event['queryStringParameters']['program'] is None:
        return {"isBase64Encoded":False,"statusCode":400,"body":json.dumps({"error":"Missing program name."})}
    programName = str(event['queryStringParameters']['program'])
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('bugbounty')
    resp = table.get_item(
        Key={
            'ProgramName' : programName,
        }
    )
    def set_default(obj):
        if isinstance(obj, set):
            return list(obj)
    #raise TypeError
    if 'Item' in resp:
        responseOutput = str(resp['Item'])
        return {"isBase64Encoded":False,"statusCode":200,"body":json.dumps({responseOutput}, default=set_default)}
    return {
        "isBase64Encoded":False,
        "statusCode":200,
        "body":json.dumps("Program not found.")
    }