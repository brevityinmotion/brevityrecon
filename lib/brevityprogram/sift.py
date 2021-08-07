import io
import brevitycore.core

def prepareSift(programName,inputBucketName):
    #scriptStatus = generateScriptSift(programName, inputBucketName)
    scriptStatus = generateScriptSiftAWS(programName, inputBucketName)
    return scriptStatus

# This does not yet work. Need to write the EC2 deploy and install script as a dependency.
def generateScriptSiftAWS(programName, inputBucketName):
    
    fileBuffer = io.StringIO()
    fileContents = f"""#!/bin/bash

# Run custom sift script
export HOME=/home/ec2-user

cd $HOME/security/raw/{programName}/

wait
sift -f $HOME/security/config/sift/search-keywords.csv /data/responses/{programName} -o matches-{programName}-keywords.txt --literal --only-matching
wait
sift -f $HOME/security/config/sift/search-regex.csv /data/responses/{programName} -o matches-{programName}-extensions.txt --only-matching
wait
sift -f $HOME/security/config/sift/search-extensions.csv /data/responses/{programName} -o matches-{programName}-extensions.txt --only-matching
wait
sift -f $HOME/security/config/search-filenames.csv /data/responses/{programName} -o matches-{programName}-filenames.txt --only-matching
wait
sift -f $HOME/security/config/search-phrases.csv /data/responses/{programName} -o matches-{programName}-phrases.txt --only-matching
wait
sleep 10
mv $HOME/security/raw/{programName}/matches-* $HOME/security/refined/{programName}/
sleep 10
# rm -r responses
# sleep 10
sh $HOME/security/config/sync-{programName}.sh"""

    fileBuffer.write(fileContents)
    objectBuffer = io.BytesIO(fileBuffer.getvalue().encode())
    # Upload file to S3
    object_name = 'sift-' + programName + '.sh'
    object_path = 'run/' + programName + '/' + object_name
    status = brevitycore.core.upload_object(objectBuffer,inputBucketName,object_path)
    fileBuffer.close()
    objectBuffer.close()
    return status
