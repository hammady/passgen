#!/usr/bin/env python

from uuid import uuid4
from datetime import datetime
from passbook.models import Pass, Barcode, EventTicket, BarcodeFormat, Location

class Passgen():
    def __init__(self, private_key, private_key_password, certificate, wwdrca, pass_type_identifier, team_identifier):
        self._private_key = private_key
        self._private_key_password = private_key_password
        self._certificate = certificate
        self._wwdrca = wwdrca
        self._pass_type_identifier = pass_type_identifier
        self._team_identifier = team_identifier

    # returns BytesIO
    def generate(self, name, venue, organization_name, message, latitude, longitude, start_time, end_time, icon=None):
        print('Generating: name:%s, venue:%s, organization_name:%s, message:%s, latitude:%f, longitude:%f, start_time:%s, end_time:%s, icon:%s' % \
            (name, venue, organization_name, message, latitude, longitude, start_time, end_time, icon))
        start_time_str = start_time.strftime('%c %Z')
        cardInfo = EventTicket()
        cardInfo.addPrimaryField('name', name, 'Name')
        cardInfo.addSecondaryField('venue', venue, 'Venue')
        cardInfo.addAuxiliaryField('start_time', start_time_str, 'Start Time')
        cardInfo.addBackField('org', organization_name, 'Organizer')

        passfile = Pass(cardInfo, \
            passTypeIdentifier=self._pass_type_identifier, \
            organizationName=organization_name, \
            teamIdentifier=self._team_identifier)
        passfile.serialNumber = str(uuid4())
        passfile.barcode = Barcode(message = message, format=BarcodeFormat.QR)
        location = Location(latitude=latitude, longitude=longitude)
        location.relevantText = "Swipe to show barcode"
        passfile.locations = [location]
        passfile.relevantDate = datetime.isoformat(start_time)
        passfile.expirationDate = datetime.isoformat(end_time)

        # Including the icon and logo is necessary for the passbook to be valid.
        icon_file = 'images/passgen.png'
        if icon:
            icon_file = 'images/{}'.format(icon)
        passfile.addFile('icon.png', open(icon_file, 'rb'))
        passfile.addFile('logo.png', open(icon_file, 'rb'))

        # Create and output the Passbook file (.pkpass)
        output = passfile.create(self._certificate, self._private_key, self._wwdrca, self._private_key_password)
        output.seek(0)
        return output
