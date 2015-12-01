import numpy as np
import urllib2
import ast
import requests

# Song.resp['foreign_ids'] is an array of dicts that are key:'foreign_id', value: 'musixmatch-WW:song:3957'
# if 3957 is the ID of the song in musixmatch.

# API Key: 3476eaa823bbdd8fc9b8fe89ee98c387

LYRICS_BASE = 'http://api.musixmatch.com/ws/1.1/track.lyrics.get?apikey=3476eaa823bbdd8fc9b8fe89ee98c387'

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

def grab_lyrics(params=['hello', 'adele'], urlbase='http://search.azlyrics.com/search.php?q='):
	# Set up URL
	url = urlbase
	for p in params:
		url += p+"+"
	url = url[:-1]

	# Read and split into correct pieces
	r = urllib2.urlopen(url).read()
	tl = r.split("text-left visitedlyr")[1:]

	# Grab hyperlinks
	hrefs = [t.split('href')[1].split('target')[0][2:-2] for t in tl]

	# Process into lyrics
	output = []
	for ur in hrefs:
		resp = urllib2.urlopen(ur).read()
		output.append(re.sub(r'\<.*?\>', '', resp.split('cf_text_top')[1][2:]).split('Android')[0][-8].strip())
	
	
	return output