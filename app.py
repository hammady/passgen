#!/usr/bin/env python

from passgen import Passgen
from os import environ as env
from datetime import datetime
from flask import Flask, render_template, send_file, request
from boto3 import client as boto_client
from yaml import safe_load as yaml_load

app = Flask(__name__)
passgen = None
api_keys = {}

@app.route('/')
def root_html():
    return render_template('form.html')

@app.route('/generate', methods=['GET'])
def generate():
    # handle api key
    api_key = request.args.get('apiKey')
    organization_name = get_organization_name(api_key)
    venue = request.args.get('venue')
    time = '{}T{}:00{}'.format(request.args.get('date'), request.args.get('time'), request.args.get('timeZone'))
    time = datetime.fromisoformat(time)
    allowed_message = get_message(api_key, request.args.get('qrCode'))
    if allowed_message == None:
        allowed_message = 'Demo barcode, please contact me to get an API key. Venue is {} at {} anyway'.format(venue, time)
    latitude, longitude = request.args.get('location').split(',')

    output = passgen.generate(
        name=request.args.get('attendeeName'),
        venue=request.args.get('venue'),
        organization_name=organization_name,
        message=allowed_message,
        latitude=float(latitude),
        longitude=float(longitude),
        time=time)

    return send_file(
        output,
        as_attachment=True,
        attachment_filename='event.pkpass',
        mimetype='application/vnd.apple.pkpass')
    
def get_organization_name(api_key):
    data = api_keys.get(api_key)
    if data:
        return data['org']
    else:
        return 'Generic Event Organizer'

def get_message(api_key, message):
    if api_keys.get(api_key):
        return message
    else:
        return None

def download_secret_files():
    def download_secret_file(s3, key, path):
        s3.download_file(env['AWS_BUCKET'], '{}{}'.format(env.get('AWS_SECRETS_PREFIX', ''), key), path)

    s3 = boto_client('s3')
    download_secret_file(s3, 'private.key', './certs/private.key')
    download_secret_file(s3, 'certificate.pem', './certs/certificate.pem')
    download_secret_file(s3, 'apple-wwdrca.pem', './certs/apple-wwdrca.pem')
    download_secret_file(s3, 'api_keys.yaml', './api_keys.yaml')

if __name__ == '__main__':
    if not env.get('SKIP_DOWNLOAD_SECRETS'):
        print('Downloading secrets from AWS S3...')
        download_secret_files()

    with open('./api_keys.yaml', 'r') as f:
        api_keys = yaml_load(f)

    passgen = Passgen(
        private_key='./certs/private.key',
        private_key_password=env['APPLE_PRIVATE_KEY_PASSWORD'],
        certificate='./certs/certificate.pem',
        wwdrca='./certs/apple-wwdrca.pem',
        pass_type_identifier=env['APPLE_PASS_TYPE_IDENTIFIER'],
        team_identifier=env['APPLE_TEAM_IDENTIFIER'])

    app.run(debug=True, host='0.0.0.0', port=3000)