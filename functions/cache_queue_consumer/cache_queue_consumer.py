import json
import boto3
import datetime
from ami_lookup import ami_lookup

ts = datetime.datetime.now()
ts = str(ts)

region = 'us-east-1'

sqs = boto3.client('sqs', region_name=region)
dynamodb = boto3.resource('dynamodb')

# Get the db
table = dynamodb.Table('dev-amilookup-infra-cacheTable-1B4X4QTUCYRI0')

def lambda_handler(event, context):
    results = {}
    for msg in event['Records']:

        print(msg)
        payload = {
            'Id': msg['messageId'],
            'ReceiptHandle': msg['receiptHandle'],
            'ImageId': msg['body'],
            'Region': msg['messageAttributes']['region']['stringValue']
        }

        print(payload)

        ami_results = ami_lookup(payload['Region'],payload['ImageId'])
        ami_results = json.loads(ami_results)

        print(ami_results)

        table.put_item(
            Item={
                "VirtualizationType": ami_results['VirtualizationType'],
                "Description": str(ami_results['Description']),
                "Hypervisor": ami_results['Hypervisor'],
                "ImageOwnerAlias": ami_results['ImageOwnerAlias'],
                "EnaSupport": ami_results['EnaSupport'],
                "SriovNetSupport": ami_results['SriovNetSupport'],
                "ImageId": ami_results['ImageId'],
                "State": ami_results['State'],
                "BlockDeviceMappings": ami_results['BlockDeviceMappings'],
                "Architecture": ami_results['Architecture'],
                "ImageLocation": ami_results['ImageLocation'],
                "RootDeviceType": ami_results['RootDeviceType'],
                "OwnerId": ami_results['OwnerId'],
                "RootDeviceName": ami_results['RootDeviceName'],
                "CreationDate": ami_results['CreationDate'],
                "Public": ami_results['Public'],
                "ImageType": ami_results['ImageType'],
                "Name": ami_results['Name'],
                "CreateTimestamp": ts
            }
        )

    return {"message": "Batch processed."}
