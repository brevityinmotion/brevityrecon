import digitalocean
import json, io

def createDroplet(accessToken,dropletName,runOperation,programName,awsAccessKeyId,awsSecretKey):
    
    def _generateUserDataScript(runOperation,programName,awsAccessKeyId,awsSecretKey):
        import io
        fileBuffer = io.StringIO()
        fileContents = """#cloud-config
    packages:
     - awscli

    runcmd:
     - mkdir /root/security
     - mkdir /root/security/config
     - mkdir /root/security/run/{1}
     - export AWS_ACCESS_KEY_ID={2}
     - export AWS_SECRET_ACCESS_KEY={3}
     - export AWS_DEFAULT_REGION=us-east-1
     - aws s3 sync s3://brevity-inputs/config/ /root/security/config/
     - wait
     - aws s3 sync s3://brevity-inputs/run/{1}/ /root/security/run/{1}/
     - wait
     - sh /root/security/config/bounty-startup-{0}.sh
     - wait
     - sh /root/security/run/{1}/sync-{1}.sh
     - wait
     - sh /root/security/run/{1}/{0}-{1}.sh
     - wait
     - shutdown now"""
        fileContents = fileContents.format(runOperation,programName,awsAccessKeyId,awsSecretKey)
        fileBuffer.write(fileContents)
        userData = fileBuffer.getvalue()
        return userData
    
    userData = _generateUserDataScript(runOperation,programName,awsAccessKeyId,awsSecretKey)
    
    # Extract all keys within the account to load into the droplet
    manager = digitalocean.Manager(token=accessToken)
    keys = manager.get_all_sshkeys()
    #  source ~/.bashrc
    # Prepare droplet specifications
    droplet = digitalocean.Droplet(token=accessToken,
                                   name=dropletName,
                                   region='nyc3', # New York 2
                                   image='ubuntu-20-04-x64', # Ubuntu 20.04 x64
                                   size_slug='s-8vcpu-16gb',  # 1GB RAM, 1 vCPU
                                   ssh_keys=keys,
                                   backups=False,
                                   user_data=userData)
    # Create new droplet
    droplet.create()
    return droplet

def loadDropletInfo(accessToken,dropletName):
    manager = digitalocean.Manager(token=accessToken)
    my_droplets = manager.get_all_droplets()
    for dropletvalue in my_droplets:
        if dropletvalue.name == dropletName:
            #dropletId = dropletvalue.id
            droplet = dropletvalue
            return droplet
        else: droplet = 'NotFound'
    return droplet
    
def getDropletStatus(droplet):
    import time
    dropletStatus = ''
    while dropletStatus != 'completed':
        actions = droplet.get_actions()
        for action in actions:
            action.load()
            dropletStatus = action.status
            print(dropletStatus)
        time.sleep(5)
    return dropletStatus
    
def retrieveDropletConnection(accessToken,dropletName):
    manager = digitalocean.Manager(token=accessToken)
    my_droplets = manager.get_all_droplets()
    for dropletvalue in my_droplets:
        if dropletvalue.name == dropletName:
            dropletIP = dropletvalue.ip_address
            # TO-DO - add the brevityocean ssh key name as a variable
            dropletConnection = 'ssh -i brevityocean root@' + dropletIP
            return dropletConnection
        else: dropletConnection = 'NotFound'
    return dropletConnection
    
def retrieveDropletOff(accessToken,dropletName):
    import time
    dropletState = ''
    while dropletState != 'off':
        manager = digitalocean.Manager(token=accessToken)
        my_droplets = manager.get_all_droplets()
        for dropletvalue in my_droplets:
            if dropletvalue.name == dropletName:
                dropletState = dropletvalue.status
                print(dropletState)
                time.sleep(60)
    return dropletState

def deleteDroplet(brevityDroplet,dropletName):
    try:
        if brevityDroplet.name == dropletName:
            brevityDroplet.destroy()
            status = 'Droplet has been destroyed.'
            return status
    except:
        status = 'Droplet not found.'
        return status
