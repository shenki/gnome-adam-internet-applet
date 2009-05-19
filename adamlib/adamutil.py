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
from BeautifulSoup import BeautifulSoup as soup
from dateutil.parser import parse as dateparse
from dateutil.relativedelta import relativedelta
from datetime import datetime, date
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
        self.next_update = datetime.now()

        self.offpeak = 0
        self.external = 0
        self.uploads = 0
        self.quota = 0

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
                    user=self.username,
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

            xml = soup(data.read())
            quota_str = xml.find(XML_QUOTA).string
            peak_str = xml.find(XML_PEAK).string
            offpeak_str = xml.find(XML_OFFPEAK).string
            upload_str = xml.find(XML_UPLOAD).string
            date_str = xml.find(XML_START_DATE).string
            last_update_str = xml.find(XML_LAST_UPDATE).string
            next_update_str = xml.find(XML_NEXT_UPDATE).string

            log.debug("quota_str: %s", quota_str)
            log.debug("peak_str: %s", peak_str)
            log.debug("offpeak_str: %s", offpeak_str)
            log.debug("upload_str: %s", upload_str)
            log.debug("date_str: %s", date_str)
            log.debug("last_update_str: %s", last_update_str)
            log.debug("next_update_str: %s", next_update_str)

            log.info("Converting strings to dates, ints, etc")

            self.start_date = dateparse(date_str)
            self.last_update = dateparse(last_update_str)
            self.next_update = dateparse(next_update_str)

            log.info("Converting dates")

            self.peak = int(peak_str)
            self.offpeak = int(offpeak_str)
            self.uploads = int(upload_str)
            self.quota = int(quota_str)

            log.info("Converting data")

            log.debug("peak: %d", self.peak)
            log.debug("offpeak: %d", self.offpeak)
            log.debug("uploads: %d", self.uploads)
            log.debug("quota: %d", self.quota)

            self.percent_remaining = int(round(
                float(self.quota-self.peak) / self.quota * 100))
            self.percent_used = int(round(
                float(self.peak) / self.quota * 100))
            self.used = self.peak
            self.remaining = self.quota-self.peak

            log.debug("percent_remaining: %d", self.percent_remaining)
            log.debug("percent_used: %d", self.percent_used)

            end_date = self.start_date.date() + relativedelta(months=1)
            self.daysleft = (end_date - date.today()).days

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
        log.info("Checking weather to fetch data")
        log.info("Is %s > %s? %s", self.next_update, self.last_update,
                self.next_update > self.last_update)

        if self.next_update > self.last_update:
            log.info("Fetching data")
            self.do_update()
