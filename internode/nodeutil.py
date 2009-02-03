#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
#                                                                             #
# nodeutil.py - Support file for the                                          #
#               GNOME ADSL Internode Usage Meter Panel Applet                 #
#                                                                             #
# Copyright (C) 2005  Sam Pohlenz <retrix@internode.on.net>                   #
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

###########
# Imports #
###########

import time
import datetime
import urllib


#####################
# Class Definitions #
#####################

class AppURLopener(urllib.FancyURLopener):
  version = "UsageMeterForGNOME/1.6"

urllib._urlopener = AppURLopener()

class NodeUtil:
	""" 
	Updates usage information, caching the data to avoid excessive requests
	to the Internode servers. New data will only be fetched once per hour.
	"""

	def __init__(self):
		"""
		Initalize the Internode utility class
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

		params_dic = {}
		params_dic["username"] = self.username
		params_dic["password"] = self.password
		params = urllib.urlencode(params_dic)

		try:
			f = urllib.urlopen("https://customer-webtools-api.internode.on.net/cgi-bin/padsl-usage", params)
			data = f.read().split()
		except IOError:
			self.error = "Failed to fetch usage data."
			raise UpdateError

		try:
			params_dic["history"] = 1
			params = urllib.urlencode(params_dic)
			f = urllib.urlopen("https://customer-webtools-api.internode.on.net/cgi-bin/padsl-usage", params)
			history = f.read().split()
			self.history = [(history[x],history[x+1]) for x in range(0,len(history),2)]
		except IOError:
			self.error = "Failed to fetch history data."
			raise UpdateError

		try:
			self.quota = int(data[1])
			self.used = float(data[0])
			self.remaining = self.quota - self.used

			self.percent_remaining = int(round(self.remaining / self.quota * 100))
			self.percent_used = int(round(self.used / self.quota * 100))

			# Convert date from array to date and find difference with current date
			# to get number of days remaining in billing period
			# *Possibly a better way to do this*
			datetuple = time.strptime(data[2], '%d/%m/%Y')
			date = datetime.date(datetuple[0], datetuple[1], datetuple[2])
			diff = date - datetime.date.today()
		
			self.daysleft = diff.days

			self.time = time.time()
			print "Data updated for username %s." % self.username

			self.error = ""
		except:
			# An error occurred
			self.error = " ".join(data)

			print self.error

			raise UpdateError


	def update(self):
		"""
		Updates data, first checking that there is no recent data
		"""

		if time.time() - 3600 > self.time:
			self.do_update()


class UpdateError(Exception):
	"""
	Exception class to handle update errors
	"""
	
	pass
