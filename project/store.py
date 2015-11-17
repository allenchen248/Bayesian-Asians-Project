import cPickle
import numpy as np

import os
from os import listdir

from project import DOCLOC

BASEDIR = DOCLOC+"vars/"
MSGDIR = BASEDIR+"messages/"

if not os.path.exists(BASEDIR):
	os.makedirs(BASEDIR)

if not os.path.exists(MSGDIR):
	os.makedirs(MSGDIR)

def fwrite(val, fname):
	with open(fname, 'wb') as test_file:
		cPickle.Pickler(test_file, -1).dump(val)

def fread(fname):
	with open(fname, 'rb') as test_file:
		return cPickle.Unpickler(test_file).load()

def fput(val, varname, message):
	fwrite(val, BASEDIR+varname)
	fwrite(message, MSGDIR+varname)

def _get_all_files(BASEDIR=BASEDIR):
	fs = [f for f in listdir(BASEDIR) if os.path.isfile(os.path.join(BASEDIR, f))]
	for i,f in enumerate(fs):
		if f == '.DS_Store':
			del fs[i]
	return fs

def flook(which=None):
	allfiles = _get_all_files(BASEDIR)
	if which is None:
		print "All Files:"
		for i in xrange(len(allfiles)):
			print "   (%d) %s" % (i, allfiles[i])
	else:
		if (which >= 0) and (which < len(allfiles)):
			print "File %d: %s" % (which, allfiles[which])
			try:
				print fread(MSGDIR+allfiles[which])
			except IOError:
				# Compatibility - for old varload format
				fread(allfiles[which])

def frm(varname, verbose=True):
	try:
		allfiles = _get_all_files(BASEDIR)
		os.remove(MSGDIR+allfiles[int(varname)])
		os.remove(BASEDIR+allfiles[int(varname)])
		if verbose:
			print "Sucess"
	except (ValueError, IOError, IndexError):
		try:
			os.remove(MSGDIR+varname)
			os.remove(BASEDIR+varname)
			if verbose:
				print "Sucess"
		except IOError:
			raise IOError("Doesn't Exist!")

def fget(varname, verbose=True):
	try:
		allfiles = _get_all_files(BASEDIR)
		message = fread(MSGDIR+allfiles[int(varname)])
		if verbose:
			print message
		return fread(BASEDIR+allfiles[int(varname)])
	except (ValueError, IOError, IndexError):
		try:
			message = fread(MSGDIR+varname)
			if verbose:
				print message
			return fread(BASEDIR+varname)
		except IOError:
			raise IOError("Doesn't Exist!")