import numpy as np
import numpy.random as random

def split_dict(d, num):
	output = [{} for i in xrange(num)]
	assign = random.random_integers(0,num-1,(len(d)))
	for i,(k,v) in enumerate(d.iteritems()):
		output[assign[i]][k] = v
	return output
