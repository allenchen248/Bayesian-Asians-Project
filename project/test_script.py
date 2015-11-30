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