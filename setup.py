import os
import sys

from distutils.core import setup

# Get the install prefix and write to the constants file
prefix = sys.prefix
for arg in sys.argv:
		if arg.startswith('--prefix='):
				prefix = arg[9:]
				prefix = os.path.expandvars(prefix)

infile = open(os.path.join('adam', 'constants.py.in'))
data = infile.read()
infile.close()

outfile = open(os.path.join('adam', 'constants.py'), 'w')
outfile.write(data)
outfile.write("\nADAM_PREFIX = '%s'\n\n" % prefix)

# Test whether we want to import the deprecated gnome.applet or
# the newer gnomeapplet
try:
	import gnomeapplet
	# Use gnomeapplet
	outfile.write("\nADAM_GNOMEAPPLET = 'gnomeapplet'\n\n")
except ImportError:
	# Use (deprecated) gnome.applet
	outfile.write("\nADAM_GNOMEAPPLET = 'gnome.applet'\n\n")

outfile.close()


# Write the install prefix to the AdamUsageMeterApplet.server file (bonobo)
infile = open('AdamUsageMeterApplet.server.in')
data = infile.read().replace('@PREFIX@', prefix)
infile.close()

outfile = open('AdamUsageMeterApplet.server', 'w')
outfile.write(data)
outfile.close()

from adam.constants import *

# Do the setup routine
setup(name = ADAM_NAME,
	  version = ADAM_VERSION,
	  description = ADAM_DESCRIPTION,
	  url = ADAM_URL,
	  author = ADAM_AUTHORS[0].split('<')[0],
	  author_email = ADAM_AUTHORS[0],
	  license = 'GPL',
	  packages = ['adam'],
	  scripts = ['adam-applet.py'],
	  data_files = [('lib/bonobo/servers', ['AdamUsageMeterApplet.server']),
	  				('share/adam', ['adam-applet.glade', 'menu.xml']),
					('share/adam/pixmaps', ['pixmaps/adam-0.png',
												 'pixmaps/adam-25.png',
												 'pixmaps/adam-50.png',
												 'pixmaps/adam-75.png',
												 'pixmaps/adam-100.png',
												 'pixmaps/adam-u0.png',
												 'pixmaps/adam-u25.png',
												 'pixmaps/adam-u75.png',
												 'pixmaps/adam-u100.png',
												 'pixmaps/adam-x.png',
												 'pixmaps/adam-applet.png',
												 'pixmaps/logo.png']), ]
	  )
