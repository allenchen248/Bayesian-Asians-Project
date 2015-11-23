import ast
import time

import urllib
import urllib2

from urllib2 import HTTPError


# Server limits requests to 1 / sec.
SLEEP_MIN = 1.
SLEEP_ERROR = 20.

HOOK_END = "https://api.hooktheory.com/v1/"

authentication = urllib.urlencode({'username':'dchang137', 'password':'ambalima'})
page = urllib2.urlopen(urllib2.Request(HOOK_END+"users/auth", authentication)).read()

HTTP_TOKEN = ast.literal_eval(page)['activkey']

def read_with_auth(url, auto_sleep=True, perform_eval=True):
	req = urllib2.Request(url, None, {"Authorization": "Bearer %s" % HTTP_TOKEN})
	resp = urllib2.urlopen(req)

	# Technically this is bad, but we are doing this to save computation time
	# Actually searching through for the "X-Rate-Limit" category and parsing
	# takes up too much time.
	if auto_sleep:
		min_sleep_time = int(resp.info().headers[7].split(":")[1].split("\r")[0][1:])
		time.sleep(min_sleep_time)

	if perform_eval:
		try:
			return ast.literal_eval(resp.read())
		except SyntaxError:
			return []
	else:
		return resp.read()

def read_to_end(url, startval=1, verbose=True, return_failed=True):
	output = []
	failed = []
	
	i = startval
	while True:
		try:
			newval = read_with_auth(url+"&page="+str(i))

			if verbose:
				print "\rFinished Reading Page %d" % i

			if len(newval) > 0:
				output.extend(newval)
			else:
				if return_failed:
					return output, failed
				else:
					return output
		except HTTPError as e:
			print "ERROR OCCURED ON PAGE %d" % i
			print e
			time.sleep(SLEEP_ERROR)
			failed.append(i)

		i += 1

def read_by_chord(base_url=HOOK_END, verbose=True):
	output = {}
	for i in xrange(1,8):
		for j in xrange(1,8):
			if verbose:
				print "--------------------------------------"
				print "Now Reading Chord Progression (%d, %d)" % (i, j)
				print "--------------------------------------"
			output[(i,j)] = read_to_end(base_url+"trends/songs?cp="+str(i)+","+str(j), verbose=verbose)

	return output
