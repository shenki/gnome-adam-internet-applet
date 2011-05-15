#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# GNOME Adam Internet Applet
# Copyright 2009 Joel Stanley <joel@jms.id.au>
# Copyright 2005 Sam Pohlenz <retrix@internode.on.net>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import urllib2
import logging
from xml.etree.ElementTree import ElementTree
from dateutil.parser import parse as dateparse
from dateutil.relativedelta import relativedelta
from datetime import datetime, date, timedelta
from adamlib.constants import XML_QUOTA, XML_PEAK, XML_OFFPEAK, \
        XML_UPLOAD, XML_START_DATE, XML_LAST_UPDATE, XML_NEXT_UPDATE, \
        WEB_REALM, WEB_URI, WEB_DATA

class AdamUtil:
    """
    Updates usage information, caching the data to avoid excessive requests
    to the Adam servers. New data will only be fetched once per hour.
    """

    def __init__(self):
        logging.basicConfig(level=logging.DEBUG)
        log = logging.getLogger("adamutil")
        log.info("Initalising")

        self.username = ""
        self.password = ""
        self.show_used = False
        self.time = datetime.now()

        self.error = True

        self.percent_used = 0
        self.percent_remaining = 0
        self.used = 0
        self.remaining = 0

        self.daysleft = 0

        self.start_date = 0
        self.last_update = datetime.min
        self.next_update = datetime.min

        self.quota = 0
        self.used = 0
        self.ip_addr = ""

    def do_update(self):
        """
        Updates data, regardless of currently held data
        """
        log = logging.getLogger("adamutil.do_update")
        log.info("Starting update at %s", datetime.now())

        self.error = True

        try:
            log.info("Fetching data")
            auth = urllib2.HTTPBasicAuthHandler()
            auth.add_password(realm=WEB_REALM,
                    uri=WEB_URI,
                    user='',
                    passwd=self.password)
            opener = urllib2.build_opener(auth)
            data = opener.open(WEB_DATA)

        except IOError:
            log.exception("Failed to fetch usage data.")
            raise Exception("Failed to fetch usage data.")

        except:
            log.exception("Unknown error when fetching usage data")
            raise Exception("Unknown error when fetching usage data")

        try:
            log.info("Parsing data")

            t = ElementTree()
            t.parse(data)
            usage = t.find('Customer/Account/Usage/Bucket/Usage').text
            quota = t.find('Customer/Account/Usage/Bucket/Quota').text

            start_date = t.find('Customer/Account/Usage/Bucket/Quota').items()[1][1]

            last_update = t.find('Customer/Account/Usage/LastUsageUpdate').text
            ip_addr = t.find('Customer/Account/IPAddresses/IPv4Address').text

            log.debug("quota: %s", quota)
            log.debug("usage: %s", usage)
            log.debug("date: %s", date)
            log.debug("last_update: %s", last_update)

            log.info("Converting dates")

            self.start_date = dateparse(start_date)
            self.last_update = dateparse(last_update)
            self.next_update = self.last_update + timedelta(minutes=30)

            log.info("Converting data")

            self.quota = int(quota) / 1000 / 1000
            self.usage = int(usage) / 1000 / 1000

            self.ip_addr = ip_addr

            log.debug("quota: %d", self.quota)
            log.debug("usage: %d", self.usage)

            used = float(self.usage)
            remaining = float(self.quota - used)

            self.percent_remaining = int(round(remaining / self.quota * 100))
            self.percent_used = int(round(used / self.quota * 100))
            self.used = int(used)
            self.remaining = int(remaining)

            log.debug("percent_remaining: %d", self.percent_remaining)
            log.debug("percent_used: %d", self.percent_used)

            end_date = self.start_date.date() + relativedelta(months=+1)
            self.daysleft = (end_date - date.today()).days - 1

            log.debug("daysleft: %d", self.daysleft)

            log.info("Update completed at %s", datetime.now())

            self.error = False
        except:
            log.exception("Failed to extract usage data from XML.")
            raise Exception("Failed to extract usage data from XML.")

    def update(self):
        """
        Updates data, first checking that there is no recent data
        """
        log = logging.getLogger("adamutil.update")

#         log.info("Checking weather to fetch data")
#         now = datetime.utcnow()
# 
#         print "now: ", now, type(now)
#         print "next_update: ", self.next_update, type(self.next_update)
# 
#         log.info("Is %s > %s? %s", now, self.next_update,
#                 now > self.next_update)
# 
#         if now > self.next_update:

        log.info("Fetching data")
        self.do_update()
