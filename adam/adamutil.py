#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
#                                                                             #
# adamutil.py - Support file for the                                          #
#               GNOME ADSL Adam Usage Meter Panel Applet                 #
#                                                                             #
# Copyright (C) 2005  Sam Pohlenz <retrix@adam.on.net>                   #
#                                                                             #
# This program is free software; you can redistribute it and/or               #
# modify it under the terms of the GNU General Public License                 #
# as published by the Free Software Foundation; either version 2              #
# of the License, or (at your option) any later version.                      #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program; if not, write to the Free Software                 #
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA. #
#                                                                             #
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

import urllib2
from BeautifulSoup import BeautifulSoup as soup
from dateutil.parser import parse as dateparse
from dateutil.relativedelta import relativedelta
from datetime import datetime, date

import logging

class AdamUtil:
	"""
	Updates usage information, caching the data to avoid excessive requests
	to the Adam servers. New data will only be fetched once per hour.
	"""

	def __init__(self):
		"""
		Initalize the Adam utility class
		"""
		logging.basicConfig(level=logging.DEBUG)
		log = logging.getLogger("adamutil")

		self.username = ""
		self.password = ""
		self.show_used = False
		self.time = datetime.now()

		self.error = ""

		self.percent_used = 0
		self.percent_remaining = 0
		self.used = 0
		self.remaining = 0

		self.daysleft = 0

		self.start_date = 0
		self.last_update = datetime.min
		self.next_update = datetime.now()

		self.local = 0
		self.external = 0
		self.uploads = 0
		self.quota = 0

	def do_update(self):
		"""
		Updates data, regardless of currently held data
		"""
		log = logging.getLogger("adamutil.do_update")
		log.info("Starting update at %s", datetime.now())

		try:
			log.info("Fetching data")
			auth = urllib2.HTTPBasicAuthHandler()
			auth.add_password(realm='Adam Members Area External Access',
					uri='https://members.adam.com.au',
					user=self.username,
					passwd=self.password)
			opener = urllib2.build_opener(auth)
			data = opener.open('https://members.adam.com.au/um1.6/usage.xml')

		except IOError:
			log.error("Failed to fetch usage data.")
			log.exception()

		try:
			log.info("Parsing data")

			s = soup(data.read())
			quota_str = s.find("megabytequota").string
			total_str = s.find("megabytesdownloadedtotal").string
			external_str = s.find("megabytesdownloadedexternal").string
			upload_str = s.find("megabytesuploadedtotal").string
			date_str = s.find("quotastartdate").string
			last_update_str = s.find("lastupdate").string
			next_update_str = s.find("nextupdateestimate").string

			log.debug("quota_str: %s", quota_str)
			log.debug("total_str: %s", total_str)
			log.debug("quota_str: %s", external_str)
			log.debug("upload_str: %s", upload_str)
			log.debug("date_str: %s", date_str)
			log.debug("last_update_str: %s", last_update_str)
			log.debug("next_update_str: %s",next_update_str)


			log.info("Converting strings to dates, ints, etc")

			self.start_date = dateparse(date_str)
			self.last_update = dateparse(last_update_str)
			self.next_update = dateparse(next_update_str)

			log.info("Converting dates")

			total = int(total_str)
			self.external = int(external_str)
			self.local = total - self.external
			self.uploads = int(upload_str)
			self.quota = int(quota_str)

			log.info("Converting data")

			log.debug("external: %d", self.external)
			log.debug("local: %d", self.local)
			log.debug("uploads: %d", self.uploads)
			log.debug("quota: %d", self.quota)

			self.percent_remaining = int(round(
				float(self.quota-self.external) / self.quota * 100))
			self.percent_used = int(round(
				float(self.external) / self.quota * 100))
			self.used = self.external
			self.remaining = self.quota-self.external

			log.debug("percent_remaining: %d", self.percent_remaining)
			log.debug("percent_used: %d", self.percent_used)

			end_date = self.start_date.date() + relativedelta(months=1)
			self.daysleft = (end_date - date.today()).days

			log.debug("daysleft: %d", self.daysleft)

			log.info("Update completed at %s", datetime.now())

		except:
			log.error("Failed to extract usage data")
			raise

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

class UpdateError(Exception):
	"""
	Exception class to handle update errors
	"""

	pass
