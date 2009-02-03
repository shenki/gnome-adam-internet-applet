#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
#                                                                             #
# nodeutil.py - Support file for the                                          #
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

import time
import datetime
import urllib2
from BeautifulSoup import BeautifulSoup as soup
from getpass import getpass

class NodeUtil:
	"""
	Updates usage information, caching the data to avoid excessive requests
	to the Adam servers. New data will only be fetched once per hour.
	"""

	def __init__(self):
		"""
		Initalize the Adam utility class
		"""

		self.username = ""
		self.password = ""
		self.show_used = False
		self.time = 0

		self.error = ""

		self.percent_used = 0
		self.percent_remaining = 0
		self.quota = 0
		self.used = 0
		self.remaining = 0

		self.daysleft = 0

		self.history = []


	def do_update(self):
		"""
		Updates data, regardless of currently held data
		"""

		try:
			auth = urllib2.HTTPBasicAuthHandler()
			auth.add_password(realm='Adam Members Area External Access',
					uri='https://members.adam.com.au',
					user=self.username,
					passwd=self.password)
			opener = urllib2.build_opener(auth)

		except IOError:
			self.error = "Failed to fetch usage data."
			raise UpdateError

		try:
			s = soup(data.read())
			quota_str = s.find("megabytequota").string
			total_str = s.find("megabytesdownloadedtotal").string
			external_str = s.find("megabytesdownloadedexternal").string
			upload_str = s.find("megabytesuploadedtotal").string
			date_str = s.find("quotastartdate").string

			last_update_str = s.find("lastupdate")
			next_update_str = s.find("nextupdateestimate")

			total = int(total_str)
			external = int(external_str)

			self.start_date = dateparse(date_str)
			self.last_update = dateparse(last_update_str)
			self.next_update = dateparse(next_update_str)

			self.local = total - external
			self.downloads = external
			self.uploads = int(upload_str)
			self.quota = int(quota_str)

			print "Data updated for username %s." % self.username

		except:
			self.error = "Failed to extract usage data"

	def update(self):
		"""
		Updates data, first checking that there is no recent data
		"""

		if self.next_update < self.time:
			self.do_update()


class UpdateError(Exception):
	"""
	Exception class to handle update errors
	"""

	pass
