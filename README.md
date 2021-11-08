# Brevity In Motion - Automated Cloud Recon Ecosystem

## Introduction
This is the initial release of the code powering a cloud-based automated recon ecosystem.

There is detailed information surrounding this repository at: https://www.brevityinmotion.com/automated-cloud-based-recon/

Not all of the codified infrastructure is complete and will be added to this repository in the future as a usable deployment package. There are some dependencies missing like IAM roles and S3 buckets that would need to be implemented for the code to run without error. However, there is a vast number of examples and templates that can be leveraged for building your own environments.

Additional documentation will be developed in the near future.

Reach out to me on Twitter with any questions: 
https://twitter.com/ryanelkins

## Walkthrough of workflow
New program is sent to brevity-program-build

### Lambda: brevity-program-build
Calls the following functions:
* brevityprogram.programs.generate_program
* brevityprogram.programs.prepareProgram
* brevityscope.parser.generateInitialDomains
* brevityprogram.dynamodb.update_program_latestRecon

### brevityprogram.programs

#### brevityprogram.programs.generate_program
This function parses the initial program input data and loads it into a DynamoDB table for long-term storage.

Calls the following functions:
* brevityprogram.dynamodb.create_program
* brevityprogram.dynamodb.update_program_scopein
* brevityprogram.dynamodb.update_program_scopeout
* brevityprogram.dynamodb.update_program_platform
* brevityprogram.dynamodb.update_invite_type
* brevityprogram.dynamodb.update_program_scopeinurls
* brevityprogram.dynamodb.update_program_scopeingithub
* brevityprogram.dynamodb.update_program_scopeinwild
* brevityprogram.dynamodb.update_program_scopeingeneral
* brevityprogram.dynamodb.update_program_scopeinIP
* brevityprogram.dynamodb.update_program_scopeouturls
* brevityprogram.dynamodb.update_program_scopeoutgithub
* brevityprogram.dynamodb.update_program_scopeoutwild
* brevityprogram.dynamodb.update_program_scopeoutgeneral
* brevityprogram.dynamodb.update_program_scopeoutIP
 
#### brevityprogram.programs.prepareProgram

Calls the following functions:
* brevityprogram.programs.prepareProgram.generateProgramSyncScript
* 
 

### brevityprogram.dynamodb
None of the dynamodb functions create or utilize files.



        
