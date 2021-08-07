import boto3
import botocore
from botocore.exceptions import ClientError
from dynamodb_json import json_util as dynjson

def create_program(programName):
    try:
        program = {
            'ProgramName': programName
        }
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('bugbounty')
        table.put_item(
            Item=program,
            ConditionExpression='attribute_not_exists(ProgramName)'
        )
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            return 'Program already exists.'
        else:
            return 'An error occurred adding the program.'
    return 'Program successfully added.'

def get_program(programName):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('bugbounty')
    resp = table.get_item(
        Key={
            'ProgramName' : programName,
        }
    )
    if 'Item' in resp:
        print(resp['Item'])

def update_program_scopein(programName,scopeIn):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('bugbounty')
    table.update_item(
        Key={
                'ProgramName' : programName,
            },
        UpdateExpression="set ScopeIn = :g",
        ExpressionAttributeValues={
                ':g': scopeIn
            },
        ReturnValues="UPDATED_NEW"
        )
    return 'Scope in successfully added.'
    
def update_program_scopeout(programName,scopeOut):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('bugbounty')
    table.update_item(
        Key={
                'ProgramName' : programName,
            },
        UpdateExpression="set ScopeOut = :g",
        ExpressionAttributeValues={
                ':g': scopeOut
            },
        ReturnValues="UPDATED_NEW"
        )
    return 'Scope out successfully added.'
    
def update_program_platform(programName,programPlatform):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('bugbounty')
    table.update_item(
        Key={
                'ProgramName' : programName,
            },
        UpdateExpression="set Platform = :g",
        ExpressionAttributeValues={
                ':g': programPlatform
            },
        ReturnValues="UPDATED_NEW"
        )
    return 'Program platform successfully added.'

def update_invite_type(programName,inviteType):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('bugbounty')
    table.update_item(
        Key={
                'ProgramName' : programName,
            },
        UpdateExpression="set InviteType = :g",
        ExpressionAttributeValues={
                ':g': inviteType
            },
        ReturnValues="UPDATED_NEW"
        )
    return 'Program invite successfully added.'
    

def update_program_scopeinurls(programName,scopeInURLs):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('bugbounty')
    table.update_item(
        Key={
                'ProgramName' : programName,
            },
        UpdateExpression="set ScopeInURLs = :g",
        ExpressionAttributeValues={
                ':g': scopeInURLs
            },
        ReturnValues="UPDATED_NEW"
        )
    return 'Scope in successfully added.'

def update_program_scopeingithub(programName,scopeInGithub):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('bugbounty')
    table.update_item(
        Key={
                'ProgramName' : programName,
            },
        UpdateExpression="set ScopeInGithub = :g",
        ExpressionAttributeValues={
                ':g': scopeInGithub
            },
        ReturnValues="UPDATED_NEW"
        )
    return 'Scope in successfully added.'

def update_program_scopeinwild(programName,scopeInWild):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('bugbounty')
    table.update_item(
        Key={
                'ProgramName' : programName,
            },
        UpdateExpression="set ScopeInWild = :g",
        ExpressionAttributeValues={
                ':g': scopeInWild
            },
        ReturnValues="UPDATED_NEW"
        )
    return 'Scope in successfully added.'

def update_program_scopeingeneral(programName,scopeInGeneral):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('bugbounty')
    table.update_item(
        Key={
                'ProgramName' : programName,
            },
        UpdateExpression="set ScopeInGeneral = :g",
        ExpressionAttributeValues={
                ':g': scopeInGeneral
            },
        ReturnValues="UPDATED_NEW"
        )
    return 'Scope in successfully added.'

def update_program_scopeinIP(programName,scopeInIP):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('bugbounty')
    table.update_item(
        Key={
                'ProgramName' : programName,
            },
        UpdateExpression="set ScopeInIP = :g",
        ExpressionAttributeValues={
                ':g': scopeInIP
            },
        ReturnValues="UPDATED_NEW"
        )
    return 'Scope in successfully added.'

def update_program_scopeouturls(programName,scopeOutURLs):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('bugbounty')
    table.update_item(
        Key={
                'ProgramName' : programName,
            },
        UpdateExpression="set ScopeOutURLs = :g",
        ExpressionAttributeValues={
                ':g': scopeOutURLs
            },
        ReturnValues="UPDATED_NEW"
        )
    return 'Scope out successfully added.'

def update_program_scopeoutgithub(programName,scopeOutGithub):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('bugbounty')
    table.update_item(
        Key={
                'ProgramName' : programName,
            },
        UpdateExpression="set ScopeOutGithub = :g",
        ExpressionAttributeValues={
                ':g': scopeOutGithub
            },
        ReturnValues="UPDATED_NEW"
        )
    return 'Scope out successfully added.'

def update_program_scopeoutwild(programName,scopeOutWild):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('bugbounty')
    table.update_item(
        Key={
                'ProgramName' : programName,
            },
        UpdateExpression="set ScopeOutWild = :g",
        ExpressionAttributeValues={
                ':g': scopeOutWild
            },
        ReturnValues="UPDATED_NEW"
        )
    return 'Scope out successfully added.'

def update_program_scopeoutgeneral(programName,scopeOutGeneral):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('bugbounty')
    table.update_item(
        Key={
                'ProgramName' : programName,
            },
        UpdateExpression="set ScopeOutGeneral = :g",
        ExpressionAttributeValues={
                ':g': scopeOutGeneral
            },
        ReturnValues="UPDATED_NEW"
        )
    return 'Scope out successfully added.'

def update_program_scopeoutIP(programName,scopeOutIP):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('bugbounty')
    table.update_item(
        Key={
                'ProgramName' : programName,
            },
        UpdateExpression="set ScopeOutIP = :g",
        ExpressionAttributeValues={
                ':g': scopeOutIP
            },
        ReturnValues="UPDATED_NEW"
        )
    return 'Scope in successfully added.'

def update_program_latestRecon(programName,reconDate):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('bugbounty')
    table.update_item(
        Key={
                'ProgramName' : programName,
            },
        UpdateExpression="set latestRecon = :g",
        ExpressionAttributeValues={
                ':g': reconDate
            },
        ReturnValues="UPDATED_NEW"
        )
    return 'Program platform successfully added.'
    
def query_program(programName, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.client('dynamodb')
    table_name = 'bugbounty'
    #table = dynamodb.Table(table_name)
    response = dynamodb.get_item(
        TableName=table_name,
        Key={
            'ProgramName': {'S': programName}
        }
    )
    return response['Item']

# Function to retrieve all program information from DynamoDB and return all fields as an independent variable value.
def getProgramInfo(programName):
    resp = query_program(programName)
    programPlatform = dynjson.loads(resp['Platform'])
    inviteType = dynjson.loads(resp['InviteType'])
    listscopein = dynjson.loads(resp['ScopeIn'])
    listscopeout = dynjson.loads(resp['ScopeOut'])
    ScopeInURLs = dynjson.loads(resp['ScopeInURLs'])
    ScopeInGithub = dynjson.loads(resp['ScopeInGithub'])
    ScopeInWild = dynjson.loads(resp['ScopeInWild'])
    ScopeInGeneral = dynjson.loads(resp['ScopeInGeneral'])
    ScopeInIP = dynjson.loads(resp['ScopeInIP'])
    ScopeOutURLs = dynjson.loads(resp['ScopeOutURLs'])
    ScopeOutGithub = dynjson.loads(resp['ScopeOutGithub'])
    ScopeOutWild = dynjson.loads(resp['ScopeOutWild'])
    ScopeOutGeneral = dynjson.loads(resp['ScopeOutGeneral'])
    ScopeOutIP = dynjson.loads(resp['ScopeOutIP'])
    return programPlatform, inviteType, listscopein, listscopeout, ScopeInURLs, ScopeInGithub, ScopeInWild, ScopeInGeneral, ScopeInIP, ScopeOutURLs, ScopeOutGithub, ScopeOutWild, ScopeOutGeneral, ScopeOutIP