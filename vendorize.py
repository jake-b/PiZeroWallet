#!/usr/bin/env python
import os
import urllib
import hashlib
import sys
import wget
import urllib
import argparse
from tqdm import tqdm
import json
from packaging import version

# Parse the command line parameter(s)
parser = argparse.ArgumentParser(description='Download a list of debian pacakges from a hard-coded list of repositories.')
parser.add_argument('-l', '--list', type=str, help='the file containing the list of dependences')
parser.add_argument('-s', '--script', type=str, help='write a shell script to this file with the install commands')
args = parser.parse_args()

# The list of package repositories to search, as a tuple
# A tuple: The first is the base path of the repo, the second is the path to the package list
repositories = [ ('http://mirrordirector.raspbian.org/raspbian/', 'dists/jessie/main/binary-armhf/Packages'),
				 ('http://archive.raspberrypi.org/debian/', 'dists/jessie/main/binary-armhf/Packages')]

# A dictionary to contain all the info from the package repository files.
packages = {}

# https://stackoverflow.com/questions/287871/print-in-terminal-with-colors-using-python
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# From https://pypi.python.org/pypi/tqdm
class TqdmUpTo(tqdm):
    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)

def download(url):
	with TqdmUpTo(unit='B', unit_scale=True, miniters=1, 
				  desc=url.split('/')[-1]) as t:  # all optional kwargs
		urllib.urlretrieve(url, filename=line, reporthook=t.update_to, data=None)


# https://gist.github.com/rji/b38c7238128edf53a181
def md5_checksum(filename, block_size=65536):
    md5 = hashlib.md5()
    with open(filename, 'rb') as f:
        for block in iter(lambda: f.read(block_size), b''):
            md5.update(block)
    return md5.hexdigest()

def sha256_checksum(filename, block_size=65536):
    sha256 = hashlib.sha256()
    with open(filename, 'rb') as f:
        for block in iter(lambda: f.read(block_size), b''):
            sha256.update(block)
    return sha256.hexdigest()

# quick and dirty function to parse the Packages file and store the result int he packages dict
def loadpackages(the_repo):
	# download the Packages file
	url = the_repo[0] + the_repo[1]
	response = urllib.urlopen(url)
	expected_size = int(response.info().getheaders("Content-Length")[0])

	current_pkg = None
	with tqdm(unit='B', unit_scale=True, total=expected_size) as pbar:
		for line in response: 
			pbar.update(len(line))
			line=line.rstrip()
			if line.startswith("Package: "):
				current_pkg = {}
				current_pkg['source'] = the_repo[0]
			if line == "":
				if current_pkg['filename']:				
					name = os.path.basename(current_pkg['filename'])
					packages[name]= current_pkg
				else:
					print("Errror")
	 			current_pkg = None
			if line.startswith("Filename: "):
				current_pkg['filename'] = line.split(": ")[1]
				current_pkg['url'] = the_repo[0] + current_pkg['filename']
			if line.startswith("SHA256"):
				current_pkg['SHA256'] = line.split(": ")[1]

def python_package_install_script(f):
	scrpt = ""
	if f.endswith(".tar.gz"):
		scrpt += "tar xvfz " + f + "\n"
		scrpt += "cd " + f[:-7] + "\n"
	elif f.endswith(".zip"):
		scrpt += "unzip " + f + "\n"
		scrpt += "cd " + f[:-4] + "\n"
	scrpt += "python setup.py install\n"
	scrpt += "cd ..\n"
	return scrpt

print "Loading repositories. This could take a few minutes: "
for repo in repositories:
	print "- " + repo[0]
	loadpackages(repo)

# Process each item in the provided list
install_script = "#!/bin/sh\n"
errors = 0

# If we have a list file, open it and process each line
if args.list:
	with open(args.list, 'r') as f:
		for line in f:
			line = line.rstrip() # trim off new line

			# We handle Debian Pacakges (.deb) and what we assume to be python packages (.tar.gz / zip)
			if line.endswith(".deb"):
				# Assume file is a debian package
				# Check to see if the file is in the current directory
				if os.path.isfile(line):
					if sha256_checksum(line) == packages[line]['SHA256']:
						print("EXISTS: " + line + bcolors.OKGREEN + "OK" + bcolors.ENDC )
						install_script += "dpkg -i " + line + "\n"	
						continue;

				# Download it
				url = packages[line]['url']
				download(url)

				# Verify checksum
				if sha256_checksum(line) == packages[line]['SHA256']:
					print line + " " + bcolors.OKGREEN + " OK " + bcolors.ENDC
					install_script += "dpkg -i " + line + "\n"
				else:
					errors += 1
					print line + " " + bcolors.FAIL + " BAD " + bcolors.ENDC
					print full_url

			elif line.endswith(".zip") or line.endswith(".tar.gz"):
				# Assume file is a python distribution
				# First figure out the package name and version from the filename:
				splits = line.split("-",1)
				package = splits[0]
				ver = splits[1]
				if ver.endswith(".tar.gz"): ver = ver[:-7]
				if ver.endswith(".zip"): ver = ver[:-4]

				# Download information from pypi
				pypi_url = "https://pypi.python.org/pypi/" + package + "/json"
				f = urllib.urlopen(pypi_url)
				entry = json.loads(f.read())

				# Make sure the ver we asked for is the most recent version
				# If not, just print a warning so we know.
				if version.parse(ver) < version.parse(entry['info']['version']):
					print bcolors.WARNING + "WARN" + bcolors.ENDC + " " + package + " may not be most recent ver. Requested: " + ver + " available: " + entry['info']['version']

				# Each release may come in diferent formats (whl vs. tar.gz) - iterate to find the one we want
				if ver in entry['releases']:
					for item in  entry['releases'][ver]:
						if line == item['filename']:
							# We've found the file
							# See if we have it already
							if os.path.isfile(line):
								if md5_checksum(line) == item['md5_digest']:
									print("EXISTS: " + line + bcolors.OKGREEN + " OK" + bcolors.ENDC )
									install_script += python_package_install_script(line)
									continue;

							# If not, download it 
							download(item['url'])

							# Check it's digest
							if md5_checksum(line) == item['md5_digest']:
								print line + " " + bcolors.OKGREEN + " OK " + bcolors.ENDC
								install_script += python_package_install_script(line)
							else:
								errors += 1
								print line + " " + bcolors.FAIL + " BAD " + bcolors.ENDC															
				else:
					print bcolors.WARNING + "WARN" + bcolors.ENDC + " couldn't find info on " +  package + "-" + ver + " skipping."




	# Write out the install script if there were no errors
	if args.script:
		if errors == 0:
			with open(args.script, "w") as text_file:
				text_file.write(install_script)
				text_file.close()
		else:
			print bcolors.FAIL + "FAIL" + bcolors.ENDC + ": errors occured and install script not generated"
else:
	print "A list of files is required"