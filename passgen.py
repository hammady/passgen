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
    def generate(self, name, venue, organization_name, message, latitude, longitude, time):
        print('Generating: name:%s, venue:%s, organization_name:%s, message:%s, latitude:%f, longitude:%f, time:%s' % \
            (name, venue, organization_name, message, latitude, longitude, time))
        time_str = time.strftime('%c %Z')
        cardInfo = EventTicket()
        cardInfo.addPrimaryField('name', name, 'Name')
        cardInfo.addSecondaryField('venue', venue, 'Venue')
        cardInfo.addAuxiliaryField('time', time_str, 'Time')
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
        passfile.relevantDate = datetime.isoformat(time)

        # Including the icon and logo is necessary for the passbook to be valid.
        passfile.addFile('icon.png', open('images/mnn.png', 'rb'))
        passfile.addFile('logo.png', open('images/mnn.png', 'rb'))

        # Create and output the Passbook file (.pkpass)
        output = passfile.create(self._certificate, self._private_key, self._wwdrca, self._private_key_password)
        output.seek(0)
        return output
