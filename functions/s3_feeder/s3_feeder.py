import boto3
from botocore.exceptions import ClientError
import json

def s3_upload(bucket, key, body):
    s3 = boto3.client('s3')
    body = json.dumps(body)
    response = s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=body
    )

    return(response)

def lambda_handler(event, context):
    print("Got event: \n" + json.dumps(event, indent=2))

    records = event['Records']
    response = []
    for r in records:
        body = json.loads(r['body'])
        bucket = "test-amilookup-lake"
        key = r['messageAttributes']['region']['stringValue'] + "/" + body['ImageId']
        s3upload = s3_upload(bucket, key, body)
        response = response.append(s3upload)
    
    return(response)