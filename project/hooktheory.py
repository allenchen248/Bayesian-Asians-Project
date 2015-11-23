import ast
import time

import urllib
import urllib2

# Server limits requests to 1 / sec.
SLEEP_MIN = 1.

HOOK_END = "https://api.hooktheory.com/v1/"

authentication = urllib.urlencode({'username':'dchang137', 'password':'ambalima'})
page = urllib2.urlopen(urllib2.Request(HOOK_END+"users/auth", authentication)).read()

HTTP_TOKEN = ast.literal_eval(page)['activkey']

def read_with_auth(url):
	req = urllib2.Request(url, None, {"Authorization": "Bearer %s" % HTTP_TOKEN})
	resp = urllib2.urlopen(req)

	# Technically this is bad, but we are doing this to save computation time
	# Actually searching through for the "X-Rate-Limit" category and parsing
	# takes up too much time.
	min_sleep_time = int(resp.info().headers[7].split(":")[1].split("\r")[0][1:])
	time.sleep(min_sleep_time)
	return ast.literal_eval(resp.read())