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