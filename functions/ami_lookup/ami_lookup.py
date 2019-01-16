import boto3
from botocore.exceptions import ClientError
import json
import logging
import os

from iopipe import IOpipe, IOpipeCore
from iopipe.contrib.eventinfo import EventInfoPlugin
from iopipe.contrib.logger import LoggerPlugin
from iopipe.contrib.profiler import ProfilerPlugin
from iopipe.contrib.trace import TracePlugin

iopipe = IOpipe(plugins=[LoggerPlugin(enabled=True),TracePlugin()])
logger = logging.getLogger()

def event_return(statusCode, body):
    response = {
        'isBase64Encoded': "false",
        'statusCode': statusCode,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': body
    }
    if statusCode != 200:
        logger.error(f"StatusCode: {statusCode} with {body}")
    return response

def ami_lookup(region, ami):
    logger.info('Starting Function')
    
    ec2 = boto3.resource('ec2', region_name=region)
    logger.info('Looking for Image')
    logger.info(ami)
    image = ec2.Image(ami)
    image.load()
    logger.info('Image loaded')
    logger.info(image.name)

    ami = {}
    ami = json.dumps({
        "VirtualizationType": image.virtualization_type,
        "Description": image.description,
        "Hypervisor": image.hypervisor,
        "ImageOwnerAlias": image.image_owner_alias,
        "EnaSupport": image.ena_support,
        "SriovNetSupport": image.sriov_net_support,
        "ImageId": image.image_id,
        "State": image.state,
        "BlockDeviceMappings": image.block_device_mappings,
        "Architecture": image.architecture,
        "ImageLocation": image.image_location,
        "RootDeviceType": image.root_device_type,
        "OwnerId": image.owner_id,
        "RootDeviceName": image.root_device_name,
        "CreationDate": image.creation_date,
        "Public": image.public,
        "ImageType": image.image_type,
        "Name": image.name
    })

    # Handle Null values in JSON.
    ami_json = json.loads(ami)
    for key, value in ami_json.items():
        if value is None:
            ami_json[key] = "None"
        if value is "":
            ami_json[key] = "None"
    ami = json.dumps(ami_json)

    return ami

@iopipe
def lambda_handler(event, context):
    logger.info("Got event\n" + json.dumps(event, indent=2))
    response = {}
    ami = event['ami']
    region = event['region']
    try:
        if ami == "":
            return event_return(500, {"ErrorMessage": "AMIId is missing"})
        else:
            context.iopipe.mark.start('AMILookup')
            response = ami_lookup(region, ami)
            context.iopipe.mark.end('AMILookup')
    except ClientError as e: 
        if e.response['Error']['Code'] == 'InvalidAMIID.Malformed':
            return event_return(500, {"ErrorMessage": "AMIId is Malformed"})
        else:
            return event_return(500, {"ErrorMessage": "Unexpected Error"})
    return event_return(200, json.loads(response))