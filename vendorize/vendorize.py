#!/usr/bin/env python

# vendorize.py
# Copyright (c) 2017 All About Jake
# Quick and dirty debian package and python package downloader
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Send thanks to: 
#   Bitcoin: 1PqvzEtDcboQYF2yhMvcdzK3J6uj7SMtQQ
#  Etherium: 0x568eBDFB7685230021942C33620263771014573B

import os
import hashlib
import sys
import wget
import requests
import argparse
from tqdm import tqdm
import json
from packaging import version
import tempfile
import shutil
import urlparse
import tarfile

temp_dir = tempfile.mkdtemp()
print "Creating temporary directory: " + temp_dir

# Parse the command line parameter(s)
parser = argparse.ArgumentParser(description='Download a list of debian pacakges from a hard-coded list of repositories.')
parser.add_argument('-s', '--save-local', action='store_true', help='keep a local copy of files downloaded in the local directory')
parser.add_argument('-l', '--list', type=str, help='the file containing the list of dependences')
parser.add_argument('-i', '--install-script', action='store_true', help='Write a shell script install commands')
parser.add_argument('-o', '--out', type=str, help='name of the pacakge file (.tar.gz) to create.')
args = parser.parse_args()
save_local = args.save_local

# Prepare the directory to dump all our stuff
working_dir = args.out
if working_dir.endswith(".tar.gz"): working_dir = working_dir[:-7]
working_dir = os.path.join(temp_dir, working_dir)
if not working_dir.endswith("/"): working_dir += "/"
os.makedirs(working_dir)

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

# https://stackoverflow.com/questions/2032403/how-to-create-full-compressed-tar-file-using-python
def make_tarfile(output_filename, source_dir):
	if source_dir.endswith("/"): 
		source_dir = source_dir[:-1]
	with tarfile.open(output_filename, "w:gz") as tar:
		tar.add(source_dir, arcname=os.path.basename(source_dir))

# https://stackoverflow.com/questions/37573483/progress-bar-while-download-file-over-http-with-requests
def download(url, dir="./"):
	filename = os.path.basename(urlparse.urlsplit(url).path)
	outfile = os.path.join(dir,filename)
	# print "Downloading " + url + " to " + outfile 
	r = requests.get(url, stream=True)
	total_size = int(r.headers.get('content-length', 0)); 
	with open(outfile, 'wb') as f:
		for data in tqdm(r.iter_content(32*1024), total=total_size, unit='B', unit_scale=True, leave=False):
			f.write(data)

def md5_checksum_string(the_string):
	m = hashlib.md5()
	m.update(the_string)
	return m.hexdigest()

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
	hash_of_url = md5_checksum_string(url)
	temp_file_path = os.path.join(tempfile.gettempdir(), hash_of_url)
	temp_file_name = os.path.join(temp_file_path, "Packages")

	if not os.path.isdir(temp_file_path):
		os.makedirs(temp_file_path)
			
	if not os.path.isfile(temp_file_name):
		print "Loading repository. This could take a minute..."
		download(url, temp_file_path)
	else:
		print "Found cache of packages file for this repository..."
	
	with open(temp_file_name, "r") as f:
		for line in f: 
			line=line.rstrip()
			if line.startswith("Package: "):
				current_pkg = {}
				current_pkg['name'] = line.split(": ")[1]
				current_pkg['source'] = the_repo[0]
			if line == "":
				if current_pkg['filename']:				
					name = os.path.basename(current_pkg['filename'])
					packages[current_pkg['name']]= current_pkg
				else:
					print("Error: No filename for given pacakge in the repository? " + line)
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

for repo in repositories:
	print "Loading " + repo[0]
	loadpackages(repo)

# Process each item in the provided list
install_script = "#!/bin/sh\n"
errors = 0

# If we have a list file, open it and process each line
if args.list:
	# Open the list file with the packages we want to vendor
	with open(args.list, 'r') as f:
		for line in f:

			# Skip comments
			if line.startswith("#") or line.strip() == "":
				continue;

			package_desc = line.split(":")
			package_type = package_desc[0].strip().rstrip()
			package_name = package_desc[1].lstrip().rstrip()

			# We handle Debian Pacakges (.deb) and what we assume to be python packages (.tar.gz / zip)
			if package_type=="dpkg":
				if package_name not in packages:
					print "Unable to find requested pacakge in the repostiory: " + package_name
					continue

				filename = os.path.basename(packages[package_name]['filename'])

				# Assume file is a debian package
				# Check to see if the file is in the current directory
				if os.path.isfile(filename):
					if sha256_checksum(filename) == packages[package_name]['SHA256']:
						print(bcolors.OKBLUE + "EXISTS: " + bcolors.ENDC + package_name + bcolors.OKGREEN + " SHA256-OK" + bcolors.ENDC )
						shutil.copyfile(package_name, os.path.join(working_dir, package_name))
						install_script += "dpkg -i " + filename + "\n"	
						continue;

				# Download it
				url = packages[package_name]['url']
				if save_local:
					download(url)
					shutil.copyfile(filename, os.path.join(working_dir, filename))
				else:
					download(url, working_dir)

				# Verify checksum
				if sha256_checksum(os.path.join(working_dir, filename)) == packages[package_name]['SHA256']:
					print filename + " " + bcolors.OKGREEN + " SHA256-OK " + bcolors.ENDC
					install_script += "dpkg -i " + filename + "\n"
				else:
					errors += 1
					print filename + " " + bcolors.FAIL + " SHA256-BAD " + bcolors.ENDC
					print full_url

			elif package_type=="pypi":
				# Assume file is a python distribution
				# Download information from pypi
				pypi_url = "https://pypi.python.org/pypi/" + package_name + "/json"
				json_text = requests.get(pypi_url).text				
				entry = json.loads(json_text)

				# Look up the most recent version of this package
				# can't trust this info->version tag for some reason in some cases?
				# ver = entry['info']['version']
				newest_release = "0.0.0"
				for release_ver, release_info in entry['releases'].iteritems():
					if (version.parse(release_ver) > version.parse(newest_release)):
						for release_file in release_info:
							if 'filename' in release_file:
					   			newest_release = release_ver
					   			continue;

				ver = newest_release

				# Each release may come in diferent formats (whl vs. tar.gz) - iterate to find the one we want
				handled_flag = None
				if ver in entry['releases']:
					for item in  entry['releases'][ver]:
						filename = item['filename']
						if filename.endswith(".tar.gz") or filename.endswith(".zip"):
							# We've found the file
							# See if we have it already in the current directory
							if os.path.isfile(filename):
								# If it exists, make sure the MD5 checksum matches
								if md5_checksum(filename) == item['md5_digest']:
									print(bcolors.OKBLUE + "EXISTS: " + bcolors.ENDC + filename + bcolors.OKGREEN + " MD5-OK" + bcolors.ENDC )
									# Copy the file to our working directory and append the install script									
									shutil.copyfile(filename, os.path.join(working_dir, filename))
									install_script += python_package_install_script(filename)
									handled_flag = True
									continue;

							# If we don't have the file download it directly to the working directory							
							if save_local:
								download(item['url'])
								shutil.copyfile(filename, os.path.join(working_dir, filename))
							else:
								download(item['url'], working_dir)

							# Check it's digest
							if md5_checksum(os.path.join(working_dir, filename)) == item['md5_digest']:
								print filename + bcolors.OKGREEN + " MD5-OK " + bcolors.ENDC
								install_script += python_package_install_script(filename)
								handled_flag = True
							else:
								errors += 1
								print package_name + " " + bcolors.FAIL + " MD5-BAD " + bcolors.ENDC	

					# If all these loops haven't found what we're looking for then skip					
					if not handled_flag:
						print bcolors.WARNING + "WARN" + bcolors.ENDC + " couldn't find info on " +  package_name + "-" + ver + " skipping."
				else:
					print bcolors.WARNING + "WARN" + bcolors.ENDC + " couldn't find info on " +  package_name + "-" + ver + " skipping."
			else:
				print "Unknown package type: " + pacakge_type

	# Write out the install script if there were no errors
	if args.install_script:
		if errors == 0:
			with open(os.path.join(working_dir, "install.sh"), "w") as text_file:
				text_file.write(install_script)
				text_file.close()
		else:
			print bcolors.FAIL + "FAIL" + bcolors.ENDC + ": errors occured and install script not generated"

	if args.out:
		# Package up all the files (and instll script if generated) into a tar.gz file
		filename = args.out
		if not (filename.endswith(".tar.gz") or filename.endswith(".tgz")):
			filename += ".tar.gz"
		make_tarfile(filename, working_dir)
else:
	print "A list of files is required"

print "Cleaning up temporary directory: " + temp_dir
shutil.rmtree(temp_dir)