#!/usr/bin/env python

import sys

import pygtk
pygtk.require('2.0')

import gtk

import adam

if adam.constants.ADAM_GNOMEAPPLET == 'gnomeapplet':
	import gnomeapplet
else:
	import gnome.applet
	gnomeapplet = gnome.applet

def adam_factory(applet, iid):
	"""
	Creates an Adam Usage Meter Applet
	"""

	adam.AdamMeter(applet, iid)
	return True



if len(sys.argv) == 2 and sys.argv[1] == "--window":
	# Launch the applet in its own window
	main_window = gtk.Window(gtk.WINDOW_TOPLEVEL)
	main_window.set_title("Adam")
	main_window.connect("destroy", gtk.main_quit)

	app = gnomeapplet.Applet()
	adam_factory(app, None)
	app.reparent(main_window)
	main_window.show_all()

	gtk.main()
	sys.exit()
else:
	# Launch the applet through the bonobo interfaces (as a panel applet)
	gnomeapplet.bonobo_factory("OAFIID:AdamUsageMeterApplet_Factory",
		gnomeapplet.Applet.__gtype__, "adam", "0", adam_factory)

