import urllib2
import os
import time
import numpy as np

from urllib2 import HTTPError

# API Key: CBCEMBUU5RKMZCANM
# Consumer Key: de5a80a9b8bce49952c3da59306b0c87
# Shared Secret: nrvPzmksQkmeK1kAXiK9vw

SLEEP_MIN = 1
SLEEP_ERROR=30
ARTIST_SEARCH_BASE = 'http://developer.echonest.com/api/v4/artist/search?api_key=CBCEMBUU5RKMZCANM&format=json&sort=hotttnesss-desc&results=99'
SONG_SEARCH_BASE = 'http://developer.echonest.com/api/v4/song/search?api_key=CBCEMBUU5RKMZCANM&format=json&sort=song_hotttnesss-desc&results=99'

def database_search(basestr=ARTIST_SEARCH_BASE, sleep=SLEEP_MIN, verbose=False): 
	try:
		artists = [urllib2.urlopen(basestr).read()]
	except HTTPError:
		if verbose:
			print "SLEEPING FOR %d SECONDS; TOO MANY REQUESTS" % SLEEP_ERROR
		time.sleep(SLEEP_ERROR)
		return artist_search(basestr, sleep, verbose)
	for i in xrange(1,10):
		try:
			artists.append(urllib2.urlopen(basestr+"&start="+str(i*99)).read())
			time.sleep(sleep)
			if verbose:
				print "FINISHED WEBPAGE %d" % i
		except HTTPError:
			if verbose:
				print "SLEEPING FOR %d SECONDS; TOO MANY REQUESTS" % SLEEP_ERROR
			time.sleep(SLEEP_ERROR)
			i -= 1

	return artists

def full_artists(n=1000, minval=0, maxval=.1, **kwargs):
	hotness = np.linspace(minval, maxval, n)
	artists = database_search(ARTIST_SEARCH_BASE+"&max_hotttnesss="+str(hotness[1]), **kwargs)
	artists.extend(database_search(ARTIST_SEARCH_BASE+"&min_hotttnesss="+str(hotness[-2]), **kwargs))
	for i in xrange(2,len(hotness)-2):
		curstr = ARTIST_SEARCH_BASE+"&max_hotttnesss="+str(hotness[i])+"&min_hotttnesss="+str(hotness[i-1])
		artists.extend(database_search(curstr, **kwargs))
		print "FINISHED %.4f Percent" % (float(i+1)/len(hotness))
	return artists