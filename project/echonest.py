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


def database_search(basestr=ARTIST_SEARCH_BASE, maxval=10, sleep=SLEEP_MIN, verbose=False): 
	try:
		artists = [urllib2.urlopen(basestr).read()]
	except HTTPError:
		if verbose:
			print "SLEEPING FOR %d SECONDS; TOO MANY REQUESTS" % SLEEP_ERROR
		time.sleep(SLEEP_ERROR)
		return artist_search(basestr, sleep, verbose)
	for i in xrange(1,maxval):
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

def get_field(data, field="name", value=None):
	if data.__class__ == str:
		data = [data]

	if not np.iterable(data):
		raise ValueError("Yo bro data isn't iterable! Check it?")

	if (value.__class__ != str) and (value is not None):
		raise ValueError("Yo dude you passed in a bad value for value.")

	output = {}
	for resp in data:
		artists = resp.split("[")[1].split("{\"")[1:]
		for a in artists:
			try:
				name = a.split(field)[1][4:].split("\"")[0]
				if value is None:
					output[name] = None
				else:
					val = a.split(value)[1][4:].split("\"")[0]
					if name in output:
						output[name].append(val)
					else:
						output[name] = [val]
			except IndexError:
				pass

	return output

class CachedData:
	def __init__(self, input_dict):
		self.internal_dict = [(k,v) for k,v in input_dict.iteritems()]
		self.cur_index = 0
		self.data_dict = {}
		self.failed_dict = {}
		self.frozen = False

	def remaining(self):
		return len(self.internal_dict)-self.cur_index

	def get(self):
		if self.frozen == True:
			return self.internal_dict[self.cur_index-1]

		if self.cur_index == len(self.internal_dict):
			raise IndexError("No more values!")

		self.cur_index += 1
		self.frozen = True
		return self.internal_dict[self.cur_index-1]

	def success(self, data):
		self.data_dict[self.cur_index-1] = data
		self.frozen = False

	def failed(self):
		k,v = self.internal_dict[self.cur_index-1]
		self.failed_dict[k] = v
		self.frozen = False

class Artist:
	def __init__(self, name, resp):
		if (name.__class__ != str) and (name.__class__ is not None):
			raise ValueError("Artist Name must be either a string or none")

		self.name = name
		self.songs = {}

		if resp is None:
			return

		elif resp.__class__ == dict:
			self.songs = resp
			return self

		elif resp.__class__ == str:
			titles = resp.split("[")[1].split("title")[1:]
			for t in titles:
				self.songs[t[4:].split("\"")[0]] = None
			return

		elif resp.__class__ == list:
			self.songs = get_field(resp, "title")
			return

		raise ValueError("Plz give me a string!")

	@classmethod
	def add(cls, first, second):
		if first.name != second.name:
			raise ValueError("Can only add together artists of the same name!")

		song = np.copy(first.songs)
		for k,v in second.songs.iteritems():
			song[k] = v

		return cls(first.name, song)

	@classmethod
	def from_name(cls, name, ids, basestr=SONG_SEARCH_BASE):
		output = []
		for i in ids:
			query = basestr+"&artist_id="+i
			try:
				output.append(cls(name, database_search(query, maxval=3)))
			except HTTPError as e:
				print e
				raise ValueError("You failed.")

		cur = output[0]
		for i in xrange(1,len(output)):
			cur = cls.add(cur, output[i])

		return cur

	@classmethod
	def from_cached(cls, cacheddata):
		for i in xrange(cacheddata.remaining()):
			k,v = cacheddata.get()
			try:
				cacheddata.success(cls.from_name(k, v))
			except:
				cacheddata.failed()

			time.sleep(SLEEP_MIN)
			print "\r Finished with %.2f Percent!" % (100*float(i)/len(artists))

		return cacheddata

	@classmethod
	def from_dict(cls, artists):
		output = []
		failed = {}
		for i,(k,v) in enumerate(artists.iteritems()):
			try:
				output.append(cls.from_name(k, v))
			except:
				failed[k] = v

			time.sleep(SLEEP_MIN)
			print "\r Finished with %.2f Percent!" % (100*float(i)/len(artists))
		return output, failed

	def __str__(self):
		if len(self.songs) == 0:
			return "Empty Artist with name %s" % self.name

		return "Artist %s, with %d songs." % (self.name, len(self.songs))

	def __repr__(self):
		return self.__str__()