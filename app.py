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

def download_secret_files():
    def download_secret_file(s3, key, path):
        s3.download_file(env['AWS_BUCKET'], '{}{}'.format(env.get('AWS_SECRETS_PREFIX', ''), key), path)

    s3 = boto_client('s3')
    download_secret_file(s3, 'private.key', './secrets/private.key')
    download_secret_file(s3, 'certificate.pem', './secrets/certificate.pem')
    download_secret_file(s3, 'apple-wwdrca.pem', './secrets/apple-wwdrca.pem')
    download_secret_file(s3, 'api_keys.yaml', './secrets/api_keys.yaml')

if not env.get('SKIP_DOWNLOAD_SECRETS'):
    print('Downloading secrets from AWS S3...')
    download_secret_files()
    print('Done')

with open('./secrets/api_keys.yaml', 'r') as f:
    api_keys = yaml_load(f)

passgen = Passgen(
    private_key='./secrets/private.key',
    private_key_password=env['APPLE_PRIVATE_KEY_PASSWORD'],
    certificate='./secrets/certificate.pem',
    wwdrca='./secrets/apple-wwdrca.pem',
    pass_type_identifier=env['APPLE_PASS_TYPE_IDENTIFIER'],
    team_identifier=env['APPLE_TEAM_IDENTIFIER'])

@app.route('/')
def root_html():
    return render_template('form.html')

@app.route('/generate', methods=['GET'])
def generate():
    def format_time(date, time, time_zone):
        time_str = '{}T{}:00{}'.format(date, time, time_zone)
        return datetime.fromisoformat(time_str)

    # handle api key
    api_key = request.args.get('apiKey')
    organization_name = get_organization_name(api_key)
    icon = get_icon(api_key)
    venue = request.args.get('venue')
    date = request.args.get('date')
    time_zone = request.args.get('timeZone')
    start_time = format_time(date, request.args.get('start_time'), time_zone)
    end_time = format_time(date, request.args.get('end_time'), time_zone)
    allowed_message = get_message(api_key, request.args.get('qrCode'))
    if allowed_message == None:
        allowed_message = 'Demo barcode, please contact me to get an API key. Venue is {} at {} anyway'.format(venue, start_time)
    latitude, longitude = request.args.get('location').split(',')

    output = passgen.generate(
        name=request.args.get('attendeeName'),
        venue=request.args.get('venue'),
        organization_name=organization_name,
        message=allowed_message,
        latitude=float(latitude),
        longitude=float(longitude),
        start_time=start_time,
        end_time=end_time,
        icon=icon)

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

def get_icon(api_key):
    data = api_keys.get(api_key)
    if data:
        return data.get('image')
    else:
        return None


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3000)
