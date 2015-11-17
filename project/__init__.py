import os

DOCLOC="/".join(os.path.realpath(__file__).split("/")[:-1])+"/pkl_files/"

if not os.path.exists(DOCLOC):
	os.makedirs(DOCLOC)

from project.store import *

class File:
	def __init__(self):
		self.files = []

	def del_all(self):
		for f in self.files:
			frm(f)

	def __contains__(self, item):
		if item in self.files:
			return True
		return False

	def __iter__(self):
		return (fget(item) for item in self.files)

	def __str__(self):
		flook()
		return ""

	def __repr__(self):
		flook()
		return ""

	def __getitem__(self, item):
		return fget(str(item))

	def __delitem__(self, item):
		return frm(str(item))

	def __setitem__(self, ind, val):
		if (ind.__class__ == tuple) or (ind.__class__ == list):
			if len(ind) == 2:
				msg = str(ind[1])
				ind = str(ind[0])
			else:
				raise ValueError("Indices must Be [Index,Message]")
		else:
			ind = str(ind)
			self.files.append(ind)
			msg = "Stored File Number "+str(len(self.files))
		
		fput(val, ind, msg)

		return