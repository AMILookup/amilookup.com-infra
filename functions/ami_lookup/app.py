import boto3
import json
from chalice import Chalice
from chalice import CORSConfig
cors_config = CORSConfig(
    allow_origin='https://amilookup.com',
)
app = Chalice(app_name='amilookup')
app.debug = True

@app.route('/')
def index():
    print('Starting Hello World')
    return {'Hello': 'World'}
@app.route('/ami/{region}/{ami}', cors=cors_config, methods=['GET'])
def ami(region, ami):
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
