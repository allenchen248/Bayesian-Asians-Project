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

def full_artists(n=100, minval=0, maxval=1, **kwargs):
	hotness = np.linspace(minval, maxval, n)
	artists = database_search(ARTIST_SEARCH_BASE+"&max_hotttnesss="+str(hotness[1]), **kwargs)
	artists.extend(database_search(ARTIST_SEARCH_BASE+"&min_hotttnesss="+str(hotness[-2]), **kwargs))
	for i in xrange(2,len(hotness)-2):
		curstr = ARTIST_SEARCH_BASE+"&max_hotttnesss="+str(hotness[i])+"&min_hotttnesss="+str(hotness[i-1])
		artists.extend(database_search(curstr, **kwargs))
		print "FINISHED %.4f Percent" % (float(i+1)/len(hotness))
	return artists

def get_artists(data, splitstr="name"):
	if data.__class__ == str:
		data = [data]

	if not np.iterable(data):
		raise ValueError("Yo bro data isn't iterable! Check it?")

	output = {}
	for resp in data:
		artists = resp.split("[")[1].split(splitstr)[1:]
		for a in artists:
			output[a[4:].split("\"")[0]] = True

	return output

class Artist:
	def __init__(self, name, resp):
		if (name.__class__ != str) and (name.__class__ is not None):
			raise ValueError("Artist Name must be either a string or none")

		self.name = name
		self.songs = {}

		if resp is None:
			return

		if resp.__class__ != str:
			raise ValueError("Artist Class is generated from String!")

		titles = resp.split("[")[1].split("title")[1:]
		for t in titles:
			self.songs[t[4:].split("\"")[0]] = None

	def __str__(self):
		if len(self.songs) == 0:
			return "Empty Artist with name %s" % self.name

		return "Artist %s, with %d songs." % (self.name, len(self.songs))

	def __repr__(self):
		return self.__str__()