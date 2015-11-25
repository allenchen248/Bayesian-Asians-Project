import numpy as np

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