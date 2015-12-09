import project

from project.store import *
from project.echonest import *

ad = fread("ArtistDict.pkl")
name = "The Weekend"
A = Artist.from_name(name, ad[name])
A.process(True)
print "FINISHED THE WEEKEND"

name = "Miley Cyrus"
B = Artist.from_name(name, ad[name])
B.process(True)
print "FINISHED MILEY"

name = "Justin Bieber"
C = Artist.from_name(name, ad[name])
C.process(True)

from project.store import fread
from project.echonest import CachedData, Artist

# Read in file
a_dict = fread("./data/AllenArtist.pkl")

# Generate a cached data object
cd = CachedData(a_dict)

# Find out all artist info from these.
Artist.from_cached(cd)

for k,song in s.iteritems():
	for v in song.resp:
		if v.__class__ == str:
			bad = v
			print "FOUND."





# AFTER THANKSGIVING
from project.store import fread, fwrite
from project.echonest import CachedData, Artist

for i in xrange(0,5):
	# Read in file
	a_dict = fread("data"+str(i)+".pkl")

	# Generate cached data object
	cd = CachedData(a_dict)

	# Find out artist info
	Artist.from_cached(cd)

	# Write to file
	fwrite(cd, "processed"+str(i)+".pkl")

	# Null for garbage collect
	cd = None

from util.progress import Progress
prg = Progress(len(cd.data_dict))
for v in cd.data_dict.itervalues():
	totallen = len(v.songs)
	for k,v in v.songs.iteritems():
		v.get_lyrics()
		prg.increment(1./totallen)

for v in cd.data_dict.itervalues():
	for k,v in v.songs.iteritems():
		v.get_lyrics()
