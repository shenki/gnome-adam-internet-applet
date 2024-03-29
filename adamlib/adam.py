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

import os
import logging
import gtk
import gtk.glade
import gnome.ui
import gconf
import gobject
import gnomeapplet

from adamutil import AdamUtil
from constants import ADAM_NAME, ADAM_VERSION, ADAM_COPYRIGHT, \
        ADAM_DESCRIPTION, ADAM_AUTHORS, ADAM_PREFIX
 

class AdamMeter:
    """
    Controls drawing of applet contents, as well as dialogs.  Contains
    a timer to periodicly query for updated usage data
    """

    ui_dir = os.path.join(ADAM_PREFIX, 'share', 'adam')
    pixmap_dir = os.path.join(ui_dir, 'pixmaps')

    def __init__(self, applet, iid):
        # Initialize GConf
        self.gconf_client = gconf.client_get_default()

        # Initialize images
        self.init_images()

        # Initialize GTK widgets
        self.image = gtk.Image()
        self.image.set_from_pixbuf(self.icons["x"])
        self.label = gtk.Label("??%")
        self.eventbox = gtk.EventBox()
        self.hbox = gtk.HBox()
        self.tooltips = gtk.Tooltips()

        # Add widgets to applet
        self.hbox.add(self.image)
        self.hbox.add(self.label)
        self.eventbox.add(self.hbox)

        applet.add(self.eventbox)

        # Load the right-click menu
        f = open(self.ui_dir + "/menu.xml", 'r')
        menu = f.read()
        applet.setup_menu(menu,
                         [("Preferences", self.show_prefs),
                          ("About", self.show_about),
                          ("Update", self.update)],
                          None)

        applet.show_all()

        # Initialize Adam Usage Checker
        self.adamutil = AdamUtil()
        self.load_prefs()

        # Connect background callback
        applet.connect("change_background", self.change_background)


    def init_images(self):
        """
        Initialises the icons and images used by the usage meter
        """

        self.icons = {}

        # Show Percentage Remaining icons
        self.icons["0"] = gtk.gdk.pixbuf_new_from_file(self.pixmap_dir +
                "/adam-0.png")
        self.icons["25"] = gtk.gdk.pixbuf_new_from_file(self.pixmap_dir +
                "/adam-25.png")
        self.icons["50"] = gtk.gdk.pixbuf_new_from_file(self.pixmap_dir +
                "/adam-50.png")
        self.icons["75"] = gtk.gdk.pixbuf_new_from_file(self.pixmap_dir +
                "/adam-75.png")
        self.icons["100"] = gtk.gdk.pixbuf_new_from_file(self.pixmap_dir +
                "/adam-100.png")
        self.icons["x"] = gtk.gdk.pixbuf_new_from_file(self.pixmap_dir +
                "/adam-x.png")

        # Show Percentage Used icons
        self.icons["u0"] = gtk.gdk.pixbuf_new_from_file(self.pixmap_dir +
                "/adam-u0.png")
        self.icons["u25"] = gtk.gdk.pixbuf_new_from_file(self.pixmap_dir +
                "/adam-u25.png")
        self.icons["u50"] = self.icons["50"]
        self.icons["u75"] = gtk.gdk.pixbuf_new_from_file(self.pixmap_dir +
                "/adam-u75.png")
        self.icons["u100"] = gtk.gdk.pixbuf_new_from_file(self.pixmap_dir +
                "/adam-u100.png")

        # About logo
        self.logo = gtk.gdk.pixbuf_new_from_file(self.pixmap_dir + "/logo.png")


    def update_image(self):
        log = logging.getLogger("adam.update_image")
        """
        Sets the icon to the appropriate image.
        """

        if self.adamutil.error:
            # Show error image
            self.image.set_from_pixbuf(self.icons["x"])

        else:
            if self.adamutil.show_used:
                percent = self.adamutil.percent_used
                prefix = "u"
            else:
                percent = self.adamutil.percent_remaining
                prefix = ""
            log.debug("percent: %d", percent)

            # No error
            if percent > 87:
                self.image.set_from_pixbuf(self.icons[prefix + "100"])
            elif percent > 62:
                self.image.set_from_pixbuf(self.icons[prefix + "75"])
            elif percent > 37:
                self.image.set_from_pixbuf(self.icons[prefix + "50"])
            elif percent > 12:
                self.image.set_from_pixbuf(self.icons[prefix + "25"])
            else:
                self.image.set_from_pixbuf(self.icons[prefix + "0"])

    def set_timeout(self, enable = True, interval = 3600000):
        """
        Sets or unsets the timeout to automatically update the usage meter
        """
        self.timeout = gobject.timeout_add(interval, self.update, self)


    def update(self, widget=False, data=False):
        """
        Fetches the latest usage information and updates the display
        """

        try:
            self.adamutil.update()
            self.update_image()

            if self.adamutil.show_used:
                percent = self.adamutil.percent_used
                usage = self.adamutil.used
                status = "used"
            else:
                percent = self.adamutil.percent_remaining
                usage = self.adamutil.quota - self.adamutil.used
                status = "remaining"

            self.label.set_text("%i%%" % percent)

            if self.adamutil.daysleft == 1:
                daystring = 'day'
            else:
                daystring = 'days'

            tiptext =  "%i MB used.\n" % self.adamutil.used
            tiptext += "%i MB quota.\n" % self.adamutil.quota
            tiptext += "IP: %s\n" % self.adamutil.ip_addr
            tiptext += "%i %s remaining." % (self.adamutil.daysleft, daystring)

        except Exception, err:
            # An error occurred
            self.label.set_text("??%")
            tiptext = str(err)
            self.update_image()

        self.tooltips.set_tip(self.eventbox, tiptext)

        # Return true so the GTK timeout will continue
        return True


    def show_about(self, widget, data):
        """
        Displays the About dialog
        """

        about = gnome.ui.About(ADAM_NAME, ADAM_VERSION, ADAM_COPYRIGHT,
            ADAM_DESCRIPTION, ADAM_AUTHORS, None,
            None, self.logo)

        about.run()

    def show_prefs(self, widget, data):
        """
        Displays the Preferences dialog
        """

        # Load and show the preferences dialog box
        glade = gtk.glade.XML(self.ui_dir + "/adam-applet.glade", "preferences")
        preferences = glade.get_widget("preferences")

        # Set the input text to the current username/password values
        passtext = glade.get_widget("password")
        passtext.set_text(self.adamutil.password)

        # Set the used/remaining radio buttons
        used = glade.get_widget("show_used")
        used.set_active(self.adamutil.show_used)

        result = preferences.run()

        if result == gtk.RESPONSE_OK:
            # Update username and password
            self.adamutil.username = usertext.get_text()
            self.adamutil.password = passtext.get_text()
            self.adamutil.show_used = used.get_active()
            self.write_prefs()

            # updating here causes a delay after pressing OK  
            #self.update()

        preferences.destroy()


    def write_prefs(self):
        """
        Writes the username and password to the GConf registry
        """

        self.gconf_client.set_string("/apps/adam-applet/username",
                self.adamutil.username)
        self.gconf_client.set_string("/apps/adam-applet/password",
                self.adamutil.password)
        self.gconf_client.set_bool("/apps/adam-applet/show_used",
                self.adamutil.show_used)


    def load_prefs(self):
        """
        Reads the username and password from the GConf registry
        """

        username = self.gconf_client.get_string("/apps/adam-applet/username")
        password = self.gconf_client.get_string("/apps/adam-applet/password")
        show_used = self.gconf_client.get_bool("/apps/adam-applet/show_used")

        if username == None or password == None:
            if username == None:
                username = ""
            if password == None:
                password = ""

            self.show_prefs()
        else:
            self.adamutil.username = username
            self.adamutil.password = password
            self.adamutil.show_used = show_used
            self.update()
            self.set_timeout()


    def change_background(self, applet, bg_type, color, pixmap):
        """
        Changes the background of the applet when the panel's background
        changes.
        """

        applet.set_style(None)
        self.eventbox.set_style(None)

        applet.modify_style(gtk.RcStyle())
        self.eventbox.modify_style(gtk.RcStyle())

        if bg_type == gnomeapplet.PIXMAP_BACKGROUND:
            style = applet.get_style()
            style.bg_pixmap[gtk.STATE_NORMAL] = pixmap
            applet.set_style(style)
            self.eventbox.set_style(style)
        elif bg_type == gnomeapplet.COLOR_BACKGROUND:
            applet.modify_bg(gtk.STATE_NORMAL, color)
            self.eventbox.modify_bg(gtk.STATE_NORMAL, color)
