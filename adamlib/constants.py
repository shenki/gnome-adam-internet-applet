#
# constants.py - Constants file for the
#                GNOME ADSL Adam Usage Meter Panel Applet
#
# Copyright (C) 2005  Sam Pohlenz <retrix@adam.on.net>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#

ADAM_NAME = 'Adam Usage Meter'

ADAM_URL = 'http://jms.id.au/wiki/AdamUsageMeter'

ADAM_VERSION = '0.1'

ADAM_COPYRIGHT = '(C) 2009 Joel Stanley'

ADAM_DESCRIPTION = 'Applet for monitoring your Adam ADSL usage.'

ADAM_AUTHORS = [
    'Joel Stanley <joel@jms.id.au>',
	]

WEB_DATA = 'https://members.adam.com.au/um1.6/usage.xml'
WEB_URI = 'https://members.adam.com.au'
WEB_REALM = 'Adam Members Area External Access'

# XML tags
XML_QUOTA = 'megabytequota'
XML_TOTAL = 'megabytesdownloadedtotal'
XML_EXTERNAL = 'megabytesdownloadedexternal'
XML_UPLOAD = 'megabytesuploadedtotal'
XML_START_DATE = 'quotastartdate'
XML_LAST_UPDATE = 'lastupdate'
XML_NEXT_UPDATE = 'nextupdateestimate'

ADAM_PREFIX = '/home/shenki/src/adam-applet.git/build'


ADAM_GNOMEAPPLET = 'gnomeapplet'

