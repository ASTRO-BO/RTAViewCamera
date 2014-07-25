#**************************************************************************#
#   begin                : Jul 24 2014                                     #
#   copyright            : (C) 2014 Andrea Zoli                            #
#   email                : zoli@iasfbo.inaf.it                             #
#**************************************************************************#

#**************************************************************************#
#                                                                          #
# This program is free software; you can redistribute it and/or modify     #
# it under the terms of the GNU General Public License as published by     #
# the Free Software Foundation; either version 2 of the License, or        #
# (at your option) any later version.                                      #
#                                                                          #
#**************************************************************************#

# Prefix for each installed program. Only ABSOLUTE PATH
prefix=/usr/local
exec_prefix=$(prefix)
# The directory to install the binary files in.
bindir=$(exec_prefix)/bin
# The directory to install the libraries in.
libdir=$(exec_prefix)/lib
# The directory to install the include files in.
includedir=$(exec_prefix)/include
# The directory to install the local configuration file.
datadir=$(exec_prefix)/share

all:

clean:

install:
	test -d $(bindir) || mkdir -p $(bindir)
	cp -pf RTAViewCamera.py $(bindir)
	test -d $(datadir)/viewcamera || mkdir -p $(datadir)/viewcamera
	cp -pf config.server* $(datadir)/viewcamera
	cp -pf RTAViewCamera.ice $(datadir)/viewcamera
	cp -pf PROD2_telconfig.fits.gz $(datadir)/viewcamera
