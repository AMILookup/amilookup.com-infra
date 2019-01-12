import boto3
from botocore.exceptions import ClientError
import json
import os
import sys

from iopipe import IOpipe, IOpipeCore
from iopipe.contrib.eventinfo import EventInfoPlugin
from iopipe.contrib.logger import LoggerPlugin
from iopipe.contrib.profiler import ProfilerPlugin
from iopipe.contrib.trace import TracePlugin

iopipe = IOpipe(plugins=[LoggerPlugin(enabled=True),EventInfoPlugin()])

@iopipe
def event_return(statusCode, body):
    response = {
        'isBase64Encoded': "false",
        'statusCode': statusCode,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': body
    }
    return response

@iopipe
def ami_lookup(region, ami):
    ami.iopipe.log.info('Starting Function')
    ec2 = boto3.resource('ec2', region_name=region)
    ami.iopipe.log.info('Looking for Image')
    ami.iopipe.log.info(ami)
    image = ec2.Image(ami)
    image.load()
    ami.iopipe.log.info('Image loaded')
    ami.iopipe.log.info(image.name)

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
        print("{} = {}".format(key, value))
        if value is None:
            print("{} is Null".format(key))
            ami_json[key] = "None"
        if value is "":
            ami_json[key] = "None"
    ami = json.dumps(ami_json)

    return ami

@iopipe
def lambda_handler(event, context):
    context.iopipe.log.info("Got event\n" + json.dumps(event, indent=2))
    response = {}
    ami = event['ami']
    region = event['region']
    try:
        if ami == "":
            return event_return(500, {"ErrorMessage": "AMIId missing"})
        else:
            response = ami_lookup(region, ami)
    except ClientError as e: 
        if e.response['Error']['Code'] == 'InvalidAMIID.Malformed':
            return event_return(500, {"ErrorMessage": "AMIId is Malformed"})
        else:
            return event_return(500, {"ErrorMessage": "Unexpected Error"})
    return event_return(200, json.loads(response))