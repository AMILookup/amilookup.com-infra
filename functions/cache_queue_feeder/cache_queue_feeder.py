import json
import boto3

queue = "https://sqs.us-east-1.amazonaws.com/124775650587/seed_queue"
session = boto3.session.Session(profile_name='aws-dev-amilookup')
region = 'us-east-1'

ec2 = session.resource('ec2', region_name=region)
sqs = session.client('sqs', region_name=region)
#image_iterator = ec2.images.all()
image_iterator = ec2.images.all()

for i in image_iterator:
    print(i.id)
    response = sqs.send_message(
        QueueUrl=queue,
        MessageBody=i.id,
        MessageAttributes={
            'region': {
                'StringValue': region,
                'DataType': 'String'
            }
        }
    )
