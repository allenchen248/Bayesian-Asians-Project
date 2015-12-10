import numpy as np
import urllib2
import ast
import re
import requests
import time

from httplib import BadStatusLine

# Song.resp['foreign_ids'] is an array of dicts that are key:'foreign_id', value: 'musixmatch-WW:song:3957'
# if 3957 is the ID of the song in musixmatch.

# API Key: 3476eaa823bbdd8fc9b8fe89ee98c387

SLEEP_BASE = 1

LYRICS_BASE = 'http://api.musixmatch.com/ws/1.1/track.lyrics.get?apikey=3476eaa823bbdd8fc9b8fe89ee98c387'
NLY_BASE = "http://www.lyrics.com"

def pull_lyrics(fids):
	if len(fids) == 0:
		return []

	responses = []
	for f in fids:
		code = int(f['foreign_id'].split(":")[-1])
		responses.append(urllib2.urlopen(LYRICS_BASE+"&track_id="+str(code)).read())

	return responses

r = urllib2.urlopen('http://lyrics.wikia.com/api.php?action=lyrics&artist=Cake&song=Dime&fmt=json').read()
d = ast.literal_eval(r.split("= ")[1])
u = d['url']

test = requests.get(u).text

def gen_database(dbfile):
	output = {}
	with open(dbfile, 'r') as f:
		for x in xrange(17):
			f.next()
		words = f.next().strip().split(",")[1:]
		for line in f:
			song = line.strip().split(",")
			odict = {}
			for s in song[2:]:
				vals = s.split(":")
				if len(vals) != 2:
					raise ValueError("Not Formatted as Expected")
				odict[int(vals[0])-1] = int(vals[1])

			output[song[1]] = odict
	return words, output

def grab_lyrics_NOT_ON_ALLEN_COMPUTER_BECAUSE_BLOCKED(params=['hello', 'adele'], urlbase='http://search.azlyrics.com/search.php?q=', throw_except=False):
	# Set up URL
	url = urlbase
	for p in params:
		url += p+"+"
	url = url[:-1]
	print url

	# Read and split into correct pieces
	try:
		r = urllib2.urlopen(url).read()
	except BadStatusLine:
		if throw_except:
			raise ValueError("Bad URL!")
		return []

	tl = r.split("text-left visitedlyr")[1:]

	# Grab hyperlinks
	hrefs = [t.split('href')[1].split('target')[0][2:-2] for t in tl]

	# Process into lyrics
	output = []
	for ur in hrefs:
		try:
			resp = urllib2.urlopen(ur).read()
			output.append(re.sub(r'\<.*?\>', '', resp.split('cf_text_top')[1][2:]).split('Android')[0][-8].strip())
		except BadStatusLine:
			if throw_except:
				raise ValueError("Bad URL!")
		time.sleep(SLEEP_BASE)

	return output

def grab_lyrics(params=['hello', 'adele'], urlbase="http://www.lyrics.com/search.php?keyword=", urlpost="&what=all&search_btn=Search"):
	# Set up URL
	url = urlbase
	for p in params:
		url += p+"+"
	url = url[:-1]+urlpost
	
	# Read and split into correct pieces
	try:
		r = urllib2.urlopen(url).read()
		time.sleep(SLEEP_BASE)
	except BadStatusLine:
		if throw_except:
			raise ValueError("Server stopped connecting!")
		return []

	try:
		tl = r.split("rightcontent")[1].split("bottom_wrapper")[0].split("href")[1:-1]

		# Grab hyperlinks
		hrefs = []
		for t in tl:
			vals = t.split("class=")
			if (len(vals) > 1) and (vals[1][1:15] == 'lyrics_preview'):
				hrefs.append(NLY_BASE+vals[0][2:-2])

		# Process into lyrics
		output = []
		for ur in hrefs:
			try:
				resp = urllib2.urlopen(ur).read()
				try:
					output.append(re.sub(r'\<.*?\>', '', resp.split("lyric_space")[1].split("itemprop=")[1][14:].split("class=\"PRINTONLY\"")[0][:-42]).strip())
				except IndexError:
					pass
			except BadStatusLine:
				if throw_except:
					raise ValueError("Server Stopped Responding!")
			time.sleep(SLEEP_BASE)
	except IndexError:
		# Implies that no lyrics exist
		return []

	return output

def testme():
	urllib2.urlopen("http://www.lyrics.com/the-hills-lyrics-the-weeknd.html")

	r = urllib2.urlopen("http://www.lyrics.com/earned-it-fifty-shades-of-grey-lyrics-the-weeknd.html")

	t = r.read()

	t.split("lyric_space")[1].split("itemprop=")[1][14:].split("class=\"PRINTONLY\"")[0][:-42]

	r = urllib2.urlopen("http://www.lyrics.com/search.php?keyword=the+weekend+the+hills&what=all&search_btn=Search")

	t = r.read()

	t.split("rightcontent")[1].split("bottom_wrapper")[0].split("href")[1:-1]

	urls = []
	for re in t:
		vals = re.split("class=")
		if (len(vals) > 1) and (vals[1][1:15] == 'lyrics_preview'):
			urls.append(NLY_BASE+vals[0][2:-2])