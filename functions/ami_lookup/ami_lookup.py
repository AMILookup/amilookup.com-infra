import boto3
import json

#This is a test change.
def ami_lookup(region, ami):
    print('Starting Function')
    ec2 = boto3.resource('ec2', region_name=region)
    print('Looking for Image')
    print(ami)
    image = ec2.Image(ami)
    print('Image found')
    image.load()
    print('Image loaded')
    print(image.name)

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

def lambda_handler(event, context):
    print("Got event\n" + json.dumps(event, indent=2))
    response = {}
    ami = event['ami']
    region = event['region']
    response = ami_lookup(region, ami)

    return {
        'isBase64Encoded': "false",
        'statusCode': 200,
        'headers': { 'Content-Type': 'application/json' },
        'body': json.loads(response)
    }
