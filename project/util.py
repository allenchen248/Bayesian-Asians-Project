import numpy as np
import numpy.random as random

from project.store import fread

def split_dict(d, num):
	output = [{} for i in xrange(num)]
	assign = random.random_integers(0,num-1,(len(d)))
	for i,(k,v) in enumerate(d.iteritems()):
		output[assign[i]][k] = v
	return output

def gen_keys(alist):
	output = {}
	failed = []
	ars = fread("./data/AllenArtist.pkl")
	ad = {}
	for k in ars.iterkeys():
		ad[k] = k
		ad[k.lower()] = k
		ad[k.split(",")[0]] = k

	for a in alist:
		if a in ad:
			output[a] = ars[ad[a]]
		elif a.lower() in ad:
			output[a] = ars[ad[a.lower()]]
		else: 
			failed.append(a)

	return output, failed
