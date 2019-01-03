import json
import boto3
import time
from itertools import zip_longest

def grouper(n, iterable, fillvalue=None):
    '''
    Usage: grouper(10, 'ABCDEFG', 'x') --> ABC DEF Gxx
    This function will split a (iterable) into (n) groupings with (fillvalue) defaulting to None
    '''
    args = [iter(iterable)] * n
    return zip_longest(fillvalue=fillvalue, *args)

def checkKey(dict, key):
    '''
    Check if key exists and return True/False
    '''
    if key in dict:
        return True
    else:
        return False

def check_response(response, key):
    '''
    Check the response for errors and report True/False.
    '''
    if checkKey(response, key):
        return True
    else:
        return False


queue_url = "https://sqs.us-east-1.amazonaws.com/124775650587/seed_queue"
region = 'us-east-1'

ec2 = boto3.client('ec2', region_name=region)
sqs = boto3.client('sqs', region_name="us-east-1")

print("Iterating through all Images")

images = ec2.describe_images()
print(len(images['Images']))
for group in grouper(10, images['Images']):
    entries=[]
    for i in group:
        data = {
            'Id': i['ImageId'],
            'MessageBody': json.dumps(i),
            'MessageAttributes': {
                'region': {
                    'StringValue': region,
                    'DataType': 'String'
                },
                'timestamp': {
                    'StringValue': str(time.time()),
                    'DataType': 'Number'
                }
            }
        }
        entries.append(data)

    response = sqs.send_message_batch(
        QueueUrl=queue_url,
        Entries=entries
    )
    if check_response(response, 'Failed'):
        print("Failures have occurred:")
        for i in response['Failed']:
            print(i)
        raise RuntimeError('The function failed for due to a response "Failed" from SQS.')
    else:
        print("Success!")


# def lambda_handler(event, context):
#     print("Got event\n" + json.dumps(event, indent=2))

#     bucket = event['bucket']
#     body = event['body']
#     key = event['key']

#     return(s3_upload(bucket, key, body))