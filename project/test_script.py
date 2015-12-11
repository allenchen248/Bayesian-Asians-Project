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

totallen = len(alk)
i=0
for v in alk.itervalues():
	singlelen = len(v.songs)
	for k,v in v.songs.iteritems():
		v.get_lyrics()
		i += 1./singlelen
		print "\rFinished with %.2f Percent!" % (100.*i)


from project.store import fread
fread(FILE)
totallen = len(arts)
i = 0
for k,v in arts.iteritems():
	singlelen = len(v.songs)*totallen
	for k,v in v.songs.iteritems():
		v.get_lyrics()
		i += 1./singlelen
		print "\rFinished with %.2f Percent!" % (100.*i)

##### LYRICS EXTRACTION

from project.store import *
from project.lyrics import *
adict = fread("known_data.pkl")
words, output = gen_database("mxm_dataset_train.txt")
output.update(gen_database("mxm_dataset_test.txt")[1])

lyrics_songs = []
for a_name,artist in adict.iteritems():
	for s_name,song in artist.songs.iteritems():
		if song.from_database(output):
			lyrics_songs.append(song)

del output

full_response = np.array(fread('full_response.pkl'))
song_ids_list = fread('song_ids_list.pkl')

song_ids_dict = {song_ids_list[i]:i for i in xrange(len(song_ids_list))}
lyrics = []
for l in lyrics_songs:
	for i in l.id:
		if i in song_ids_dict:
			lyrics.append([i, full_response[song_ids_dict[i]], l.lyrics])

ids, resp, lyrs_raw = zip(*lyrics)
lyrs = []
for l in lyrs_raw:
	if l.__class__ == list:
		lyrs.append(l[0])
	else:
		lyrs.append(l)

from sklearn.feature_extraction import DictVectorizer
v = DictVectorizer()
v_lyrics = v.fit_transform(lyrs)

from sklearn.cross_validation import train_test_split
Xtrain, Xtest, ytrain, ytest = train_test_split(v_lyrics, resp, test_size=0.33)

from sklearn.linear_model import Lasso
clf = Lasso(alpha=0.004)
clf.fit(Xtrain, ytrain)
y_resp = clf.predict(Xtest)

vocab = v.vocabulary_
to_word = {}
for i,w in enumerate(words):
	if i in vocab:
		to_word[vocab[i]] = w

weights = clf.coef_
word_weight = []
for i,w in enumerate(weights):
	word_weight.append((to_word[i], w))

word_weight = sorted(word_weight, key=lambda x: x[1])

# Get back into score form by ID
scores = {}
for i in xrange(len(ids)):
	ly = lyrs[i]
	score = 0
	for k,v in ly.iteritems():
		score += float(v)*weights[vocab[k]]
	scores[ids[i]] = score

fwrite(scores, "lyric_scores.pkl")

in_100 = 0
not_in_100 = 0
for i in xrange(len(resp)):
	if resp[i]:
		in_100 += scores[ids[i]]
	else:
		not_in_100 += scores[ids[i]]


print "Total Coefficients:"
print np.sum(np.abs(clf.coef_))
print "Total Error:"
print np.sum(np.abs(y_resp-ytest))

#### USELESS
success = []
for i in all_ids:
	try:
		success.append(output[i])
	except KeyError:
		try:
			success.append(output2[i])
		except KeyError:
			try:
				success.append(output3[i])
			except KeyError:
				try:
					success.append(output4[i])
				except KeyError:
					pass