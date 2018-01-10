# things available on lambda
import os, sys, boto3, json

# make the endpoint for interacting with Route 53 
route53 = boto3.client('route53')

# ----- function to actually interact with Route 53 -----
# call to change_resource_record_sets is also made within this function
def alter_resource_record(zone_id, host_name, hosted_zone_name, rectype, ttl, action, value):
        dns_changes = {
            'Comment': 'Vishal update fuin test --lalala ---- this can be a parameter also',
            'Changes': [
                {
                    'Action': action,
                    'ResourceRecordSet': {
                        'Name': host_name + '.' + hosted_zone_name,
                        'Type': rectype,
                        'TTL': ttl,
                        'ResourceRecords': [
                            { "Value": value
                            }
                        ]
                    }
                }
            ]
        }
        if action == "CREATE":
          action_keyword = 'created'  
        elif action == "UPSERT":
          action_keyword = 'updated'
        elif action == "DELETE":
          action_keyword = 'deleted'
        else:
          sys.exit('ERROR: Incorrect action specified')


        try:  #  API request to interact with Route 53!
            route53.change_resource_record_sets(HostedZoneId=zone_id, ChangeBatch=dns_changes)
            #time.sleep(2) # - is this needed? - timeouts if hit from  from DFT / PD perhaps? 
            # if ^ is needed, please import the time package also 
        except BaseException as e:
            #print e
            #sys.exit('ERROR: Incorrect input specified for the update of the domain  %s' % hosted_zone_name)
            # maybe we want to send the exception as part of the response body also ?
            body_text = 'ERROR: Record %s.%s could not be %s to %s for domain %s' % (host_name,hosted_zone_name,action_keyword,value,hosted_zone_name)
            return return_response(400,body_text)
        else:
            body_text = 'Record %s.%s %s with value %s for %s' % (host_name,hosted_zone_name,action_keyword,value,hosted_zone_name)
            return return_response(200,body_text)
   

# -----end of the meat function -----



# ----- function for good responses back from the lambda ----- 

def return_response(statuscode,body):    
    
    return {
        'statusCode': statuscode,
        'headers': { 'Content-Type': 'application/json' },
        #'body': json.dumps(local_event)
        'body': body
    }

# ----- end of funct ----- 

# ----- main funct ----- 

def lambda_handler(event, context):
# 1. convert the input - REQUEST parameters into a locally accessible dictionary (json)

    try:
        local_event = json.loads(event['body'])
    except BaseException as e:
        #print 'Error in loading the REQUEST parameters as (%s) ' % e
        #sys.exit('ERROR: Ensure that the JSON parameters are sent correctly:', event)
        # again perhaps we want the error to be a part of the response? 
        body_text = 'ERROR: JSON Inpput provided is incomplete or has errors. You provided the an %s record %s.%s with the value %s and TTL of %s for %s ' % (RecordType,RecordName,DomainName,RecordValue,RecordTtl,DomainName)
        return return_response(400,body_text)

 # 2. Convert the local dictionary into usable objects that we need       
        
    try:

        DomainName = local_event['DomainName']
        ZoneId = local_event['ZoneId']
        RecordName = local_event['RecordName']
        RecordType = local_event['RecordType']
        RecordTtl = local_event['RecordTtl']
        RecordAction = local_event['RecordAction']
        RecordValue = local_event['RecordValue']
          

    except BaseException as e:
        #print 'Error in setting up the environment, exiting now (%s) ' % e
        #sys.exit('ERROR: check JSON file is complete:', event)
        # again maybe we need the error in response 
        body_text = 'ERROR: JSON Inpput provided is incomplete or has errors. You provided the an %s record %s.%s with the value %s and TTL of %s for %s ' % (RecordType,RecordName,DomainName,RecordValue,RecordTtl,DomainName)
        return return_response(400,body_text)
 
 # 3. Call the function to do the work and return an appropriate response 
    return alter_resource_record(ZoneId, RecordName, DomainName, RecordType, RecordTtl, RecordAction, RecordValue)

