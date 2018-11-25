import boto3
import json

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

    return json.dumps({ 'id': ami,
                        'ami': image.name,
                        'description': image.description,
                        'owner': image.image_owner_alias,
                        'owner2': image.owner_id,
                        'state': image.state,
                        'image_type': image.image_type,
                        'platform': image.platform
                      })
def lambda_handler(event, context):
    print('Starting handler')
    ami = event['query']['ami']
    region = event['query']['region']
    ami_lookup = ami_lookup(region, ami)
    return ami_lookup
