import urllib2
import os
import ast
import time
import re
import numpy as np

from urllib2 import HTTPError

from project.lyrics import pull_lyrics, grab_lyrics

# API Key: CBCEMBUU5RKMZCANM
# Consumer Key: de5a80a9b8bce49952c3da59306b0c87
# Shared Secret: nrvPzmksQkmeK1kAXiK9vw

API_KEYS = ['CBCEMBUU5RKMZCANM','EJCLKDYO0IG8BPAMD','N1BKLELC5KB7IBR6K', 'KESZKE2QUN4SVPNHC',
		'FJRU9KPN5HVDJK8EZ', 'NLFXA1IBUGVSWCIFQ', 'F0ABVNJI3MVUYSSQJ', 'B1KXAHKSVAXRNQSEW',
		'GE8QKD8K9LTZJOUSW', 'OO0TYEIFXLCSTVEZ7', 'U2W0OZHN52FM4HW9K', 'AAVGZKDPBNKWOBMRM', 
		'1M1F5GLMPOQ1PAIVI', 'UJ8CU9AISIVDZPYDX', 'MLQHLZWLSRXZ3VKWM', 'GP1TQLH0UMYBWSWY1', 
		'9QX6MXTEZXIFRQHR9', 'CCLZCYBZW5RRNFJIV', 'GNPX5JOKHDWGK201K', 'GW0FZNNQZZFISWDPU', 
		'ERKK9SPSKBJZWULNK', 'IXSAQDFFLJFL98CWW', 'ZD2RT50EO6V7IZ9BC', 'ELC9POZKIDYTHURAX',
		'IJMKESRYUTLWQP9VN', 'VMAIHRDPYE8ZWGBRK', 'H4CSPTRC996SCDAWX', 'RJTL5RUUMY7Y94JZY',
		'GD1LZYWFFAH8NX5WT', '3HEGCDTFC3XAYELGJ', 'EQIGA9KKDFX0OBAM7', 'JEJODYWILNWSAHDKR',
		'2OBYASF4JYKO3N8G6']

class SongBase:
	"""
	An extension of a string class. This substitutes the API Keys into the song titles,
	one at a time, and swaps them out as used. This allows us to make continuous calls to
	an API, without looking like we are doing so.
	"""
	def __init__(self, keys, postfix, prefix='http://developer.echonest.com/api/v4/artist/search?api_key='):
		self.keys = keys
		self.prefix = prefix
		self.postfix = postfix
		self.cur = 0

	def __add__(self, other):
		val = self.prefix+self.keys[self.cur]+self.postfix+other

		self.cur += 1
		if self.cur == len(self.keys):
			self.cur = 0

		return val

	def __radd__(self, other):
		val = other+self.prefix+self.keys[self.cur]+self.postfix

		self.cur += 1
		if self.cur == len(self.keys):
			self.cur = 0

		return val

	def __iadd__(self, other):
		self.postfix += other
		return self

# Minimum amount of sleep time between calls
SLEEP_MIN = 0.5

# Time to sleep between errors
SLEEP_ERROR=10

# How to search the database for an artist
ARTIST_SEARCH_BASE = SongBase(API_KEYS, '&format=json&sort=song_hotttnesss-desc&results=99', 'http://developer.echonest.com/api/v4/song/search?api_key=')

# How to search the database for a song
SONG_SEARCH_BASE = SongBase(API_KEYS, '&format=json&sort=song_hotttnesss-desc&results=99', 'http://developer.echonest.com/api/v4/song/search?api_key=')

# The attributes that matter when searching the database for a specific song profile
attrs = ['audio_summary', 'artist_discovery', 'artist_discovery_rank', 'artist_familiarity', 'artist_familiarity_rank', \
			'artist_hotttnesss', 'artist_hotttnesss_rank', 'artist_location', 'song_currency', 'song_currency_rank', \
			'song_hotttnesss', 'song_hotttnesss_rank', 'song_type', 'tracks', 'id:musixmatch-WW']

# How to search for a song profile
SONG_PROFILE = SongBase(API_KEYS, '&format=json', 'http://developer.echonest.com/api/v4/song/profile?api_key=')

# Adding to this! All the attributes must be added on
SONG_PROFILE_BASE = SongBase(API_KEYS, '&format=json', 'http://developer.echonest.com/api/v4/song/profile?api_key=')
for a in attrs:
	SONG_PROFILE_BASE += "&bucket="+a

def database_search(basestr=ARTIST_SEARCH_BASE, maxval=10, sleep=SLEEP_MIN, verbose=False): 
	"""
	This function searches through the echonest database. We need it because the 
	echonest database can only return 99 results on a single page - as a result, to
	get anything meaningful, we have to search through multiple pages
	"""
	try:
		# Attempt the initial search
		artists = [urllib2.urlopen(basestr).read()]
		time.sleep(sleep)
	except HTTPError as e:
		# If we have already failed
		if verbose:
			print e
			print "SLEEPING FOR %d SECONDS" % SLEEP_ERROR
		time.sleep(SLEEP_ERROR)
		
		# Python will handle the infinite loop issue
		return database_search(basestr, maxval, sleep, verbose)

	for i in xrange(1,maxval):
		# Search through the rest of the pages
		try:
			artists.append(urllib2.urlopen(basestr+"&start="+str(i*99)).read())
			time.sleep(sleep)
			if verbose:
				print "FINISHED WEBPAGE %d" % i
		except HTTPError:
			if verbose:
				print "SLEEPING FOR %d SECONDS; TOO MANY REQUESTS" % SLEEP_ERROR
			time.sleep(SLEEP_ERROR)

			# Force it to try to get the page again if an error occured
			i -= 1

	return artists

def full_artists(n=100, minval=0, maxval=1, **kwargs):
	"""
	Grabs all of the information for our artists - gets them sorted by hotttnesss
	so that the 10k maximum length is okay.
	"""
	hotness = np.linspace(minval, maxval, n)
	artists = database_search(ARTIST_SEARCH_BASE+"&max_hotttnesss="+str(hotness[1]), **kwargs)
	artists.extend(database_search(ARTIST_SEARCH_BASE+"&min_hotttnesss="+str(hotness[-2]), **kwargs))
	for i in xrange(2,len(hotness)-2):
		curstr = ARTIST_SEARCH_BASE+"&max_hotttnesss="+str(hotness[i])+"&min_hotttnesss="+str(hotness[i-1])
		artists.extend(database_search(curstr, **kwargs))
		print "FINISHED %.4f Percent" % (float(i+1)/len(hotness))
	return artists

def get_field(data, field="name", value=None):
	"""
	Takes a JSON response object and grabs a relevant field from it
	"""
	# We only deal in arrays, so a single response becomes an array
	if data.__class__ == str:
		data = [data]

	# Likewise, if garbage input is passed in, we want to get rid of it
	if not np.iterable(data):
		raise ValueError("Yo bro data isn't iterable! Check it?")

	# Nope, no more garbage input
	if (value.__class__ != str) and (value is not None):
		raise ValueError("Yo dude you passed in a bad value for value.")

	# This is where we will save our data
	output = {}
	for resp in data:
		# Look for the first instance where the response starts
		artists = resp.split("[")[1].split("{\"")[1:]
		for a in artists:
			try:
				# Grab the name that split the response
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
				# Response doesn't exist
				pass

	return output

class CachedData:
	"""
	This class stores all of our data. What it does is it holds dictionaries that
	are updated as a process is running. That way, if a process fails or errors out,
	our data will still exist and we can still retrieve it
	"""
	def __init__(self, input_dict):
		self.internal_dict = [(k,v) for k,v in input_dict.iteritems()]
		self.cur_index = 0
		self.data_dict = {}
		self.failed_dict = {}
		self.frozen = False

	def intersect(self, input_dict, output={}):
		"""
		Determine which part of the input dict is in this cacheddata instance;
		the rest is thrown out as failed.

		Can iteratively add to it using the output kwarg
		"""
		failed = {}
		for v in self.data_dict.itervalues():
			if v.name in input_dict:
				output[v.name] = v
		
		for k,v in input_dict.iteritems():
			if k not in output:
				failed[k] = v

		return output, failed

	def remaining(self):
		"""
		Tells you how many values are remaining to process
		"""
		return len(self.internal_dict)-self.cur_index

	def permute(self):
		"""
		Permutes the values, for random ordering later for multiple people processing.
		"""
		neworder = np.random.permutation(xrange(len(self.internal_dict[self.cur_index:])))
		newarr = [None]*len(self.internal_dict)
		for i in xrange(self.cur_index):
			newarr[i] = self.internal_dict[i]

		for i, v in enumerate(neworder):
			newarr[i+self.cur_index] = self.internal_dict[v]

		self.internal_dict = newarr

	def get(self):
		"""
		Gets the next value to be processed, except if we haven't called success()
		or failed() - in that case, it repeatedly returns the old object until
		you decide that the process was a success or failure
		"""
		if self.frozen == True:
			return self.internal_dict[self.cur_index-1]

		if self.cur_index == len(self.internal_dict):
			raise IndexError("No more values!")

		self.cur_index += 1
		self.frozen = True
		return self.internal_dict[self.cur_index-1]

	def success(self, data):
		"""
		Log the last data point as a success
		"""
		self.data_dict[self.cur_index-1] = data
		self.frozen = False

	def failed(self):
		"""
		Log the last data point as a failure
		"""
		k,v = self.internal_dict[self.cur_index-1]
		self.failed_dict[k] = v
		self.frozen = False

class Song:
	"""
	A class that holds all of our data for song information. As we are pulling
	the data from the online database, this object will handle processing+getting
	its own lyrics, etc. 

	Just so that the structures are more organized.
	"""
	def __init__(self, name, idvals, resp, verbose=True):
		self.name = name
		self.id = idvals
		self.lyrics = None

		# Process each of the responses that are associated with this song.
		self.resp = []
		for r in resp:
			try:
				try:
					self.resp.append(ast.literal_eval(r[0])['response']['songs'][0])
				except ValueError:
					try:
						self.resp.append(ast.literal_eval(r[0].replace("null", "None"))['response']['songs'][0])
					except ValueError:
						if verbose:
							print "Error on Song %s, ID Number %d" % (self.name, len(self.resp))
						self.resp.append(r[0])
			except IndexError:
				self.resp.append({})

		# Cleaning to prevent duplicates
		for r in self.resp:
			try:
				r['title'] = re.sub(r'\(.*?\)', '', r['title']).strip()
			except KeyError:
				raise ValueError("Title Doesn't Exist!")

	def get_ids(self, which='foreign_id'):
		"""
		Get the MusiXMatch ID values so that we can grab lyrics from their database
		"""
		output = []
		[output.extend([td[which].split(":")[-1] for td in r['tracks']]) for r in self.resp]
		return output

	def from_database(self, db, **kwargs):
		"""
		Takes a dictionary "database" and picks out its own song lyrics. The database
		must be keyed by a musixmatch key of some sort (one that exists in this response)
		"""
		if self.lyrics is not None:
			raise ValueError("Lyrics already Exist!")

		flag = False
		self.lyrics = []
		id_list = self.get_ids(**kwargs)
		for i in id_list:
			if i in db:
				self.lyrics.extend([db[i]])
				flag = True

		if flag:
			return True
		else:
			return False

	def get_lyrics(self, get_full=True):
		"""
		Gets the lyrics from an external database - grabs them from online.
		Which online other site is chosen by changing what grab_lyrics() does,
		since this doesn't have to be done often
		"""
		self.lyrics = []
		if get_full:
			for r in self.resp:
				params = r['artist_name'].split(" ")
				params.extend(r['title'].split(" "))
				self.lyrics.extend(grab_lyrics(params))
		else:
			for r in self.resp:
				self.lyrics.extend(pull_lyrics(r['foreign_ids']))

		return self.lyrics

	def __str__(self):
		"""
		Make it print prettily
		"""
		return "Song %s with %d attributes" % (self.id, np.sum([len(r) for r in self.resp]))

	def __repr__(self):
		"""
		Make it print prettily
		"""
		return self.__str__()

class Artist:
	"""
	Because of how the Echonest database is set up, the Artist class is set up
	to hold all of the information about the artist. From here, we can process
	songs and generate all of the songs that correspond to a given artist.
	"""
	def __init__(self, name, resp):
		"""
		Most of the time you won't use this - use a class method instead.
		"""
		if (name.__class__ != str) and (name.__class__ is not None):
			raise ValueError("Artist Name must be either a string or none")

		self.name = name
		self.songs = {}
		self.processed = False

		if resp is None:
			return

		elif resp.__class__ == dict:
			self.songs = resp
			return self

		elif resp.__class__ == str:
			titles = resp.split("[")[1].split("title")[1:]
			ids = resp.split("[")[1].split("\"id")[1:]
			for i in xrange(len(titles)):
				self.songs[titles[i][4:].split("\"")[0]] = [ids[i][4:].split("\"")[0]]
			return

		elif resp.__class__ == list:
			self.songs = get_field(resp, "title", value='\"id')
			return

		raise ValueError("Plz give me a string!")

	def process(self, verbose=False):
		"""
		Processes all the songs that are internal to this artist.
		"""
		if self.processed == True:
			return

		for k,v in self.songs.iteritems():
			try:
				self.songs[k] = Song(k, v, [database_search(SONG_PROFILE_BASE+"&id="+val, 1, verbose=verbose) for val in v])
			except:
				time.sleep(SLEEP_ERROR)
				self.songs[k] = Song(k, v, [database_search(SONG_PROFILE_BASE+"&id="+val, 1, verbose=verbose) for val in v])

		self.processed = True

	@classmethod
	def add(cls, first, second):
		"""
		Takes two artists and adds them together into a third
		"""
		if first.name != second.name:
			raise ValueError("Can only add together artists of the same name!")

		song = np.copy(first.songs)
		for k,v in second.songs.iteritems():
			song[k] = v

		return cls(first.name, song)

	@classmethod
	def from_name(cls, name, ids, basestr=SONG_SEARCH_BASE):
		"""
		Takes an artist name and echonest ID and then constructs a fully
		processed artist object from it.
		"""
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
		"""
		Takes an instance of CachedData and generates artist objects inside of it,
		just in case a long computation fails and we still want all of the results
		that we already have.
		"""
		total = len(cacheddata.internal_dict)
		left = cacheddata.cur_index
		for i in xrange(total-left):
			k,v = cacheddata.get()
			try:
				artist = cls.from_name(k, v)
				artist.process()
				cacheddata.success(artist)
			except:
				cacheddata.failed()

			time.sleep(SLEEP_MIN)
			print "\r Finished with %.4f Percent!" % (100*float(i)/total)

		return cacheddata

	@classmethod
	def from_dict(cls, artists, verbose=False):
		"""
		Takes a dictionary and generates artist objects in a list from it.

		Note that if you're going to do this, you might as well use Artist.from_cached()
		because you can generate a cacheddata instance from a dictionary.
		"""
		output = []
		failed = {}
		for i,(k,v) in enumerate(artists.iteritems()):
			try:
				art = cls.from_name(k, v)
				art.process(verbose=verbose)
				output.append(art)
			except HTTPError as e:
				print e
				failed[k] = v

			time.sleep(SLEEP_MIN)
			print "\r Finished with %.2f Percent!" % (100*float(i)/len(artists))
		return output, failed

	def __str__(self):
		"""
		Make sure that the artist is pretty and makes sense
		"""
		if len(self.songs) == 0:
			return "Empty Artist with name %s" % self.name

		return "Artist %s, with %d songs." % (self.name, len(self.songs))

	def __repr__(self):
		"""
		Ditto
		"""
		return self.__str__()