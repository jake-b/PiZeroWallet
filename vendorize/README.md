# Vendorize

According to [Going Go Programming](https://www.goinggo.net/2013/10/manage-dependencies-with-godep.html):

> "Vendoring is the act of making your own copy of the 3rd party packages 
> your project is using.  Those copies are traditionally placed inside 
> each project and then saved in the project repository."

This is a quick and dirty python script 'vendor' a list of debian or python packages on an internet-connected machine and tar/gz them into a single file for installing on another machine taht has no internet connection.

# Disclamer
I wrote this script as part of exploring the world of cryptocurrency.  It was intended to build an offline "cold wallet".  My holdings in cryptocurrency are meger, and I currently hold TENS of US dollars in cryptocurrency. This is secure enough for my purpose. I am not an expert, so evaluate the risks before you put any significant investment in cryptocurrency at risk on some random person’s solution to the wallet problem. I am not responsible if your coins are lost or stolen.

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

# About this python script

It accepts a text file with a list of pacakges with the `-l` parameter.  This list should be of the format:

	[dpkg|pypi]: <name of package>

For example, a listing file like:

	dpkg: python-pkg-resources
	pypi: setuptools

Will download the "python-pkg-resource" debian package and the "setuptools" python package.

The script will verify SHA-256 or MD5 checksums of the downloaded files against their repositories.

The following Rasberry Pi Debian repositories are hard coded into the script for looking up debian packages:

	http://mirrordirector.raspbian.org/raspbian/
	http://archive.raspberrypi.org/debian/

The pypi repository is also hardcoded into the script for looking up python packages.

The `-i` parameter will generate an "install.sh" file with a list of commands necessary to install the packages that were downloaded

The `-o` parameter will generate a tarball with the downloaded files, and install script.

The script does no dependency checking of its own.  The intended use is to look up the dependencies by installing (or doing a "apt-get install --dry-run") on an internet connected development machine to determine the packages and installation order, and then using this script to 'vendor' the dependencies for installing on a machine without an internet connection.

Example usage:

	python vendorize.py -i -l cups_and_electrum_deps_jessie_full.txt  -o dependencies.tar.tz

This script has not been tested on Windows or Linux.  There is not much in the way of error checking.

Use at your own risk, your mileage may vary.
